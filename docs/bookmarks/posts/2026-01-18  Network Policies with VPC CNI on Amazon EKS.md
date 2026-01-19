---
title: "Network Policies with VPC CNI on Amazon EKS"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://eminalemdar.medium.com/network-policies-with-vpc-cni-on-amazon-eks-c6993d6ae596"
author:
  - "[[Emin ALEMDAR]]"
---
<!-- more -->

[Sitemap](https://eminalemdar.medium.com/sitemap/sitemap.xml)

**By default, all Pod communications in Kubernetes are allowed without any restriction.** But if you want to control the network traffic between Pods on IP address and port level you can use **Kubernetes Network Policies**. With Network Policies, you can enforce rule sets to have control over the flow. Network Policies first introduced to the upstream Kubernetes in 2016 as an alpha feature but of course now it’s stable and widely used across the industry. Network Policies act like a firewall and it allows you to create rules for both ingress and egress network traffic.

But of course there is one prerequisite for using Network Policies within Kubernetes. Network Policies are implemented by network plugins aka CNI plugins. You must have a CNI plugin that supports Network Policies installed on your Kubernetes cluster. You can choose plugins like [Cilium](https://cilium.io/), [Calico](https://www.tigera.io/project-calico/), [Weave](https://www.weave.works/). When Network Policies first introduced the most used implementation option was using ***iptables***. But iptables implementation has some limitations especially when using big scale Kubernetes clusters. Some of these CNI Plugins use [**eBPF**](https://ebpf.io/). eBPF offers a more efficient way for packet filtering and it really improves the performance dramatically compared to iptables.

When using Amazon EKS, the users have the option to choose which CNI Plugin they want to use. AWS also has its own open source CNI Plugin called [VPC CNI](https://github.com/aws/amazon-vpc-cni-k8s) and it’s a really good option because of the integration between AWS services and the networking configuration options. But there was one problem with VPC CNI. It didn’t support Network Policies natively. Users would need to install additional tools to be able to control the network traffic in their clusters. This situation of course brings additional operational burdens.

In August, AWS announced the native support for Network Policies to VPC CNI. That means users now don’t have to install third party applications to use native Network Policies. VPC CNI also uses eBPF. Amazon EKS now introduce three new components to the clusters to be able to support Network Policies:

- Network Policy Controller
- Node Agents
- eBPF SDK

## How it Works

In order to use Network Policies with VPC CNI on Amazon EKS, you need to have a cluster using **Kubernetes v1.25** version or later and also you need to have **VPC CNI version 1.14.0** or later and also you need to use an EKS optimised AMI with the **Kernel version 5.10** or later. If you are using a Kernel version below 5.10 you can check out the EKS documentation to follow the instructions to mount the eBPF file system. This feature is also disabled by default and you need to enable it by changing the VPC CNI configuration parameters.

Network Policies also can be used with both IPv4 and IPv6 EKS cluster configurations.

## Demo Time!

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*b4VYIo-M5TFjgnqG)

For this demo, I’ve created an example [GitHub repository](https://github.com/eminalemdar/vpc-cni-network-policies) with example Terraform code to create an EKS cluster and I’ve also created a bash script to enable Network Policies on VPC CNI.

There are also sample Kubernetes manifests in this repository to deploy a sample application. You can see the application layout in the diagram above but to put it in words, I can say these manifests creates these resources in the cluster:

- A Kubernetes namespace with the name “another-ns”
- A Demo application in the default namespace
- Two clients in the default namespace
- Two clients in the another-ns namespace

I’ve also added some example Network Policy definition manifests in the repository to test the functionality.

After creating the EKS cluster, I will run this command to be able to authenticate with the cluster. `aws eks --region eu-west-1 update-kubeconfig --name eks-cluster-vpc-cni`. Don’t forget to update the region name and cluster name according to your environment.

The configuration I have, install the VPC CNI version 1.14.1.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*9BMWCoKKcnvVVOeE)

I will run the `vpc_cni.sh` script to enable Network Policies and configure the required IAM Roles for Service Account for the VPC CNI Plugin.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*f1AG5lInKuAqrFph)

You can see the Network Policy is now enabled on VPC CNI from the AWS Management Console.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*w0J64xCGVsn_xOkt)

You can also run this command to confirm if the Node Agent is running in VPC CNI:

`kubectl get ds -n kube-system aws-node -o jsonpath='{.spec.template.spec.containers[*].name}{"\n"}'`

Let’s install the application resources with `kubectl apply -f example-manifests/`

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*iYSxdJz5SpR55TQz)

You can check out the connectivity between these components with these commands and you should see the expected output in the screenshot below:

`kubectl exec -it client-one -- curl --max-time 3 demo-app`

`kubectl exec -it another-client-one -n another-ns -- curl --max-time 3 demo-app.default`

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*rAAyc3jOZNLuExUP)

Let’s apply some policies to this application stack. First let me create the deny all policy.

```c
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: demo-app-deny-all
spec:
  podSelector:
    matchLabels:
      app: demo-app
  policyTypes:
  - Ingress
```

`kubectl apply -f example-manifests/policies/deny-all-ingress.yaml`. After creating the policy, let’s check if I can still access the application with the commands above.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*p1q27a1vwuphcs2n)

As you can see from the screenshot above, Network Policy actually works and denies access from both namespaces.

You can of course try other example policies I have in the repository to simulate different scenarios for multi namespace application deployments.

With native support for network policy in Amazon VPC CNI, when using EKS, you can now create policies that isolate sensitive workloads and protect them from unauthorised access. This opportunity to have granular control enables you to implement the principle of least privilege access. This feature was awaited for a long time and it really reduced the operational overhead.

CNCF Ambassador | AWS Community Builder | HashiCorp Ambassador | Calico Big Cats Ambassador | CKA — CKS — 6x AWS Certified

## More from Emin ALEMDAR

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--c6993d6ae596---------------------------------------)