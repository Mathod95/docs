---
title: "Cilium CNI on EKS using secondary CIDR and prefix delegation"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@benoit.mouquet/cilium-cni-on-eks-using-secondary-cidr-and-prefix-delegation-55e57ffd2537"
author:
  - "[[Benoit MOUQUET]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

We are currently working on a Kubernetes shared cluster to host various applications on my current company. Deploy multiple applications on the same cluster required enforce networking security to control traffic flow between pods.

AWS VPC CNI (installed by default on all EKS clusters) is not supporting network policies, but AWS offers to [install Calico](https://docs.aws.amazon.com/eks/latest/userguide/calico.html) on top of the CNI to apply network restriction inside the cluster with ***iptables*** rules. But we made the choice to use Cilium in our case.

### Why Cilium?

Cilium is based on eBPF, a feature that allows dynamically inject small code inside linux kernel in order to monitor and filter network communications. eBPF improves performances and reduces resource consumption in large infrastructure with intensive network usage (compare to classic ***iptables*** rules).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*eugg7hpfQEXLo4UP.png)

Cilium Components

Calico is also able to work using eBPF, however we decide to use Cilium due to 2 missing features in the free version of calico (but included in the enterprise license):

- DNS policy: permits to allow or deny dns queries names or pattern names. This allows, for example to authorize traffic to \*.mycompany.com and block the rest.
- Hubble: a network monitoring and security observability platform. Build on top of Cilium and eBPF to enable deep visibility into the communication and behavior of services as well as the networking infrastructure in a completely transparent manner.

At this moment we will only use eBPF for network rules, but it’s also possible to optimize the full network stack by using eBPF host routing (for totally bypassing iptables and the upper host stack). This will also remove the usage of kube-proxy. But this required a kernel version ≥ 5.10 (Amazon EKS optimized Amazon Linux AMI uses version 5.4 of linux kernel at the moment).

### Deployment specifications

After a quick study and with the objective of properly integrate the cluster in our AWS organization and development standards, we made the following technical choices:

- Cilium networking plugin with Cilium CNI
- VPC Secondary CIDR for pods: permit to reduce IP consumption for enterprise network
- ENI Prefix delegation: allow increase pods limits on small nodes
- Usage of Terraform for infrastructure deployment: full infrastructure as code deployment

We need to use at least the version 1.12.x of cilium which added prefix delegation.

### Delete AWS VPC CNI

The first difficulty of this infrastructure is to remove default AWS VPC CNI installed. EKS does not provide an option to avoid CNI installation so we have to find a trick to do this automatically. Using Terraform it is a little bit tricky because the tool is not designed to remove a resource that is not managed by it.

Two solutions can be considered. The first one is used a Kubernetes Job that runs the following command to delete the ***aws-node*** daemonset:

```c
kubectl delete daemonset aws-node -n kube-system
```

This solution works, but it required at least one functional node to run it. So several pods will probably start on that node using AWS VPC CNI and must be restarted after Cilium installation.

The selected solution is the usage of a Terraform ***null\_resource*** in order to run a ***curl*** command to delete the daemonset (can also be done using kubectl tool but simple http request removes the dependency to kubectl binary).

```c
data "aws_eks_cluster" "cluster" {
  name = var.eks_name
}

data "aws_eks_cluster_auth" "cluster" {
  name = var.eks_name
}resource "null_resource" "delete_aws_cni" {
  provisioner "local-exec" {
    command = "curl -s -k -XDELETE -H 'Authorization: Bearer ${data.aws_eks_cluster_auth.cluster.token}' -H 'Accept: application/json' -H 'Content-Type: application/json' '${data.aws_eks_cluster.cluster.endpoint}/apis/apps/v1/namespaces/kube-system/daemonsets/aws-node'"
  }
}
```

On EKS, auth token can be easily retrieved using ***aws\_eks\_cluster\_auth*** data source.

### Prepare necessary AWS Role

With the purpose of managing network interface, Cilium required a set of permissions on the AWS API. To avoid usage of IAM user with static secret, we will use ***IAM roles for service accounts*** feature of EKS.

```c
data "aws_iam_policy_document" "cilium" {
  statement {
    effect = "Allow"
    actions = [
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "ec2:DescribeSecurityGroups",
      "ec2:CreateNetworkInterface",
      "ec2:AttachNetworkInterface",
      "ec2:ModifyNetworkInterfaceAttribute",
      "ec2:AssignPrivateIpAddresses",
      "ec2:CreateTags",
      "ec2:UnassignPrivateIpAddresses",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeInstanceTypes"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "cilium" {
  name   = "${var.eks_name}-cilium"
  policy = data.aws_iam_policy_document.cilium.json

  tags = merge(
    var.tags,
    tomap({
      Name = "${var.eks_name}-cilium"
    })
  )
}

module "irsa_ca" {
  source       = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"
  version      = "4.1.0"
  create_role  = true
  role_name    = "${var.eks_name}-cilium"
  provider_url = replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "/https?:///", "")
  role_policy_arns = [
    aws_iam_policy.cilium.arn
  ]
  oidc_fully_qualified_subjects = ["system:serviceaccount:kube-system:cilium-operator"]
  tags = merge(
    var.tags,
    tomap({
      Name = "${var.eks_name}-cilium"
    })
  )
}
```

To get information about required API actions, please see the following documentation: [IPAM ENI Required privileges](https://docs.cilium.io/en/stable/concepts/networking/ipam/eni/#required-privileges)

### Install Cilium network plugin

Before deploying Cilium Helm Chart, we will create a custom configuration for Cilium CNI.

```c
resource "kubernetes_config_map" "cni_config" {
  metadata {
    name      = "cni-configuration"
    namespace = "kube-system"
  }
  data = {
    "cni-config" = <<EOF
{
  "cniVersion":"0.3.1",
  "name":"cilium",
  "plugins": [
    {
      "cniVersion":"0.3.1",
      "type":"cilium-cni",
      "eni": {
        "subnet-ids": ${jsonencode(var.pod_subnet_ids)},
        "first-interface-index": 1
      }
    }
  ]
}
EOF
  }
}
```

Two important options in this file. The first one is the list of ***subnet-ids****.* By default, nodes subnets will be used to assign pods IP. This is not what we want, so we specify subnets to use.

***Note:*** *You can use* ***subnet-tags*** *instead of* ***subnet-ids*** *to select pods subnets. In my case, I used the Terraform VPC module and I cannot easily set tags only on pod private subnets. Also cilium documentation recommends to specify this configuration directly on the CNI and not at the chart level (see:* [https://github.com/cilium/cilium/pull/19276](https://github.com/cilium/cilium/pull/19276)).

The second most important option is ***first-interface-index***. The default value is 0, so node primary network interface will be used to assign a pod IP address. This is not expected (we only want to use secondary CIDR), so will tell to cilium-cni to ignore the first ENI.

Now we can deploy the Cilium Helm chart:

```c
resource "helm_release" "cilium" {
  name         = "cilium"
  namespace    = "kube-system"
  repository   = "https://helm.cilium.io/"
  chart        = "cilium"
  version      = "1.12.1"
  timeout      = 600
  force_update = false
  replace      = true
  values = [
    <<EOF
cni:
  configMap: cni-configuration
  customConf: true
eni:
  enabled: true
  iamRole: "${module.irsa_ca.iam_role_arn}"
  updateEC2AdapterLimitViaAPI: true
  awsEnablePrefixDelegation: true
  awsReleaseExcessIPs: true
egressMasqueradeInterfaces: eth0
ipam:
  mode: eni
hubble:
  relay:
    enabled: true
  ui:
    enabled: true
tunnel: disabled
nodeinit:
  enabled: true
EOF
  ]
}
```

A quick explanation of the different options:

***CNI:  
***We set the name of previously created ***configmap*** to cilium-cni.

***ENI:  
***We enable Cilium AWS ENI management. The following options are activated:

- iamRole: role previously created for API management
- updateEC2AdapterLimitViaAPI: update EC2 limits (number of ENI and number of IP limits for instance types) using AWS API (normally this is configured using static values in Cilium source code: [https://github.com/cilium/cilium/blob/master/pkg/aws/eni/limits/limits.go](https://github.com/cilium/cilium/blob/master/pkg/aws/eni/limits/limits.go))
- awsEnablePrefixDelegation: enable prefix delegation for IP assignment
- awsReleaseExcessIPs: allow release not used IPs

***Egress Masquerade Interfaces:  
***We specify which network interfaces Cilium will use on nodes when the destination of a packet is outside the cluster. In this case, we will use the primary interface of the node (the one with an IP in the main VPC CIDR).

***IPAM:  
***Use ENI mode for IPAM: special Cilium IPAM mode for AWS environment.

***Hubble:***  
Enable Hubble web UI and relay.

***Tunnel:  
***Disable overlay routing functionality of Cilium because we use AWS ENI (direct VPC routing) in our case.

***NodeInit:***  
Enable node init script (iptables clean, kubelet configuration for cilium-cni …).

### Test configuration

Cilium CLI can be used to quickly run tests on a recent installation. First, follow this documentation to install the CLI:

[https://docs.cilium.io/en/v1.12/gettingstarted/k8s-install-default/#install-the-cilium-cli](https://docs.cilium.io/en/v1.12/gettingstarted/k8s-install-default/#install-the-cilium-cli)

You can display the status of your Cilium configuration:

```c
cilium status
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*p7NA6y5wUyTD_ijbWx5rfA.png)

Cilium status

After that just run the following command:

```c
cilium connectivy test
```

A set of deployments and network policies will be successively deployed to the cluster to ensure that Cilium is working properly.

### Hubble UI

Hubble is a great tool to visualize network flow inside your cluster. This will help you to easily debug any trouble with network policies. Just use port-forwarding to secure access to the dashboard:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*sTZM-2nIwolfM2qKpZrHwA.png)

Hubble UI Interface

### Writing network policies

After install and configure Cilium on your cluster, the next major part is to write your network policies in order to control flow between application. At this point two choices are offered to you:

- Write NetworkPolicy that follows Kubernetes API standard. The main advantage of that kind of policy is the compatibility with any CNI plugin that permits control of traffic flow.
- Write CiliumNetworkPolicy (or CiliumClusterwideNetworkPolicy) to take advantage of more powerful capabilities provided by Cilium like: DNS or HTTP (host, method, path …) rules for example.

Cilium provides a web tool to easily write your policies here: [https://editor.cilium.io/](https://editor.cilium.io/)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*pvhOje2gZgdRw3eaUoIaGg.png)

Restricted policy for Gitlab Runner agent

The editor will directly provide you the full yaml for the configured policy.

```c
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-gitlab
  namespace: gitlab-runner
spec:
  endpointSelector: {}
  ingress:
    - {}
  egress:
    - toEndpoints:
        - matchLabels:
            io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: UDP
          rules:
            dns:
              - matchPattern: "*"
    - toServices:
        - k8sService:
            serviceName: kubernetes
            namespace: default
      toPorts:
        - ports:
            - port: "443"
    - toFQDNs:
        - matchPattern: "*.factory.mycompany.com"
      toPorts:
        - ports:
            - port: "443"
    - toFQDNs:
        - matchPattern: "*.gitlab.com"
      toPorts:
        - ports:
            - port: "443"
```

The editor can also directly convert Kubernetes NetworkPolicy to CiliumNetworkPolicy if you do not use any Cilium specific feature.

### Conclusion

We have now a working networking stack on our cluster and we can filter and monitor all network communications. After the creation of an application namespace, don’t forget to deploy network policies to enforce restriction on ingress, egress and pods to pods communications.

Of course further optimisation can be done in order to use some advanced features of Cilium like eBPF based host routing or transparent encryption for pod to pod communications ([https://docs.cilium.io/en/stable/gettingstarted/encryption/](https://docs.cilium.io/en/stable/gettingstarted/encryption/)). Please have a look to necessary requirements if you are interested: [https://docs.cilium.io/en/stable/operations/system\_requirements/#required-kernel-versions-for-advanced-features](https://docs.cilium.io/en/stable/operations/system_requirements/#required-kernel-versions-for-advanced-features)

DevOps Engineer and Kubernetes Lover

## More from Benoit MOUQUET

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--55e57ffd2537---------------------------------------)