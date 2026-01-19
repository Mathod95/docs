---
title: "Cilium: Support for EFA drivers in EKS"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://awstip.com/cilium-support-for-efa-drivers-in-eks-249987d043eb"
author:
  - "[[Amit Gupta]]"
---
<!-- more -->

[Sitemap](https://awstip.com/sitemap/sitemap.xml)## [AWS Tip](https://awstip.com/?source=post_page---publication_nav-b4c1e34ed5e-249987d043eb---------------------------------------)

[![AWS Tip](https://miro.medium.com/v2/resize:fill:76:76/1*LXqMmX8rKuWEc3D_apZ1rQ.jpeg)](https://awstip.com/?source=post_page---post_publication_sidebar-b4c1e34ed5e-249987d043eb---------------------------------------)

Best AWS, DevOps, Serverless, and more from top Medium writers.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*cp3AtUs8109FN1KULoyfEQ.png)

Source-AWS

## ☸ ️Introduction

Elasticity is defined as “The ability to acquire resources as you need them and release resources when you no longer need them” — this is one of the biggest selling points of the cloud. In Amazon EC2 instances, Elastic Fabric Adapters (EFAs) are network devices that accelerate high-performance computing (HPC) and machine learning. EFAs are Elastic Network Adapters (ENAs) with additional OS-bypass capabilities. AWS Elastic Fabric Adapter (EFA) is a specialized network interface for Amazon EC2 instances that allows customers to run high levels of inter-instance communication, such as HPC applications on AWS at scale.

Some use cases for EFA are in weather modelling, semiconductor design, streaming a live sporting event, oil and gas simulations, genomics, finance, and engineering, amongst others.

## 🎯Goals & Objectives

In this article you will learn how to install Cilium on an EKS cluster with the EFA adapter. The test below was done with `g5.12xlarge`, and Cilium was installed to ensure it can claim support for it. [NCCL Tests](https://github.com/NVIDIA/nccl-tests) were run to evaluate the performance of the network using the Nvidia Collective Communication Library.

## What’s the difference between ENI, EFA, and ENA in AWS?

- **Elastic Network Interface (ENI)**: A virtual network interface for basic networking needs, including secondary IP addresses and security group attachment.
- **Elastic Fabric Adapter (EFA)**: Designed for high-performance computing (HPC) and machine learning applications, reducing latency for inter-instance communication.
- **Elastic Network Adapter (ENA)**: AWS’s standard for high-bandwidth networking, supporting enhanced networking features for optimized throughput.

## Why EFA adapter?

- Due to EFA’s support for libfabric APIs, applications using a supported MPI library can be easily migrated to AWS without having to make any changes to their existing code.
- For this reason, AWS EFA is often used in conjunction with Cluster placement groups — which allow physical hosts to be placed much closer together within an AZ to decrease latency even more.
- Elastic Fabric Adapter (EFA) is a network interface for Amazon EC2 instances that enables customers to run applications requiring high levels of inter-node communications at scale on AWS.
- Its custom-built operating system (OS) bypass hardware interface enhances the performance of inter-instance communications, which is critical to scaling these applications.
- With EFA, high-performance computing (HPC) applications using the message-passing interface (MPI) and machine learning (ML) applications using NVIDIA Collective Communications Library (NCCL) can scale to thousands of CPUs or GPUs.
- As a result, you get the application performance of on-premises HPC clusters with the on-demand elasticity and flexibility of the AWS cloud.
- EFA is an optional EC2 networking feature that can be enabled at no additional cost on any supported EC2 instance.

## Supported interfaces and libraries

EFAs support the following interfaces and libraries:

- Open MPI 4.1 and later
- Intel MPI 2019 Update 5 and later
- NVIDIA Collective Communications Library (NCCL) 2.4.2 and later
- AWS Neuron SDK version 2.3 and later

## EFA Limitations

EFAs have the following limitations:

- All P4d and P5 instance types support NVIDIA GPUDirect Remote Direct Memory Access (RDMA).
- EFA traffic between P4d/P4de/DL1 instances and other instance types is currently not supported.
- [Instance types that support multiple network cards](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html#network-cards) can be configured with one EFA per network card. All other supported instance types support only one EFA per instance.
- For `c7g.16xlarge`, `m7g.16xlarge` and `r7g.16xlarge` Dedicated Instances and Dedicated Hosts are not supported when an EFA is attached.
- EFA OS-bypass traffic can’t cross Availability Zones, VPCs, or AWS accounts. In other words, EFA OS-bypass traffic can’t flow from one Availability Zone, VPC (with or without a VPC peering connection), or AWS account to another. This does not apply to normal IP traffic from the EFA.
- EFA requires all nodes be in a single subnet
```c
2024-09-12 22:35:07 [ℹ]  EFA requires all nodes be in a single subnet, arbitrarily choosing one: [subnet-0f4785c61fbdec025]
```
- EFA OS-bypass traffic can’t be sent across subnets in a Local Zone.
- EFA OS-bypass traffic is not routable. Normal IP traffic from the EFA remains routable.
- The EFA must be a member of a security group that allows all inbound and outbound traffic to and from the security group itself.
- EFA is not supported on Windows instances.
- EFA is not supported on AWS [Outposts](https://docs.aws.amazon.com/outposts/index.html).
- The tests below were done keeping in mind multi-GPU VM’s.

## Let’s get going

- Ensure that the requisite instances are available in your region. In this case, `g5.12xlarge` was chosen.
```c
aws ec2 describe-instance-types  --region us-east-1  --filters Name=network-info.efa-supported,Values=true  --query "InstanceTypes[*].[InstanceType]"  --output text | sort
```
- Sample clusterconfig.yaml file
```c
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: efa-cluster
  region: us-west-2
  version: "1.29"
iam:
  withOIDC: true
availabilityZones: ["us-west-2a", "us-west-2b", "us-west-2c"]
managedNodeGroups:
  - name: my-efa-ng
    iam:
        attachPolicyARNs:
          - arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy
          - arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
          - arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
          - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
    instanceType: g5.12xlarge
    minSize: 1
    desiredCapacity: 2
    maxSize: 2
    availabilityZones: ["us-west-2b"]
    volumeSize: 300
    privateNetworking: true
    efaEnabled: true
    # taint nodes so that application pods are
     # not scheduled/executed until Cilium is deployed.
     # Alternatively, see the note below.
    taints:
      - key: "node.cilium.io/agent-not-ready"
        value: "true"
        effect: "NoExecute"
```
- Create an EKS cluster using the sample cluster\_config.yaml
```c
eksctl create cluster -f ./eks-config_efa.yaml
```
- Notice that the EFA device plugin is now being automatically installed.
```c
2024-09-09 15:46:43 [ℹ]  created "kube-system:DaemonSet.apps/aws-efa-k8s-device-plugin-daemonset"
2024-09-09 15:46:44 [ℹ]  as you have enabled EFA, the EFA device plugin was automatically installed.
2024-09-09 15:46:44 [▶]  completed task: install EFA device plugin
```
- Patch the AWS daemonset- In case of ENI mode, Cilium will manage ENIs instead of VPC CNI, so the `aws-node` DaemonSet has to be patched to prevent conflict behavior.
```c
kubectl -n kube-system patch daemonset aws-node --type='strategic' -p='{"spec":{"template":{"spec":{"nodeSelector":{"io.cilium/aws-node-enabled":"true"}}}}}'
```
- Install Cilium in ENI mode
```c
helm install cilium cilium/cilium --version 1.15.8   --namespace kube-system   --set eni.enabled=true   --set ipam.mode=eni   --set egressMasqueradeInterfaces=eth0   --set routingMode=native
```
- Check that the nodes and pods are Ready and in a healthy state.
```c
kubectl get nodes -o wide
NAME                                          STATUS   ROLES    AGE   VERSION               INTERNAL-IP     EXTERNAL-IP   OS-IMAGE         KERNEL-VERSION                  CONTAINER-RUNTIME
ip-192-168-66-72.us-west-2.compute.internal   Ready    <none>   19m   v1.29.6-eks-1552ad0   192.168.66.72   <none>        Amazon Linux 2   5.10.223-212.873.amzn2.x86_64   containerd://1.7.11
ip-192-168-67-38.us-west-2.compute.internal   Ready    <none>   19m   v1.29.6-eks-1552ad0   192.168.67.38   <none>        Amazon Linux 2   5.10.223-212.873.amzn2.x86_64   containerd://1.7.11

kubectl get pods -o wide -A
NAMESPACE     NAME                                        READY   STATUS    RESTARTS   AGE   IP               NODE                                          NOMINATED NODE   READINESS GATES
kube-system   aws-efa-k8s-device-plugin-daemonset-jjlwb   1/1     Running   0          17m   192.168.67.38    ip-192-168-67-38.us-west-2.compute.internal   <none>           <none>
kube-system   aws-efa-k8s-device-plugin-daemonset-vr76k   1/1     Running   0          17m   192.168.66.72    ip-192-168-66-72.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-9kbgf                                1/1     Running   0          15m   192.168.67.38    ip-192-168-67-38.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-kbcxt                                1/1     Running   0          15m   192.168.66.72    ip-192-168-66-72.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-operator-c55d96f4c-6cr97             1/1     Running   0          15m   192.168.66.72    ip-192-168-66-72.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-operator-c55d96f4c-n5hb4             1/1     Running   0          15m   192.168.67.38    ip-192-168-67-38.us-west-2.compute.internal   <none>           <none>
kube-system   coredns-5b8cc885bc-4vmt2                    1/1     Running   0          15m   192.168.89.100   ip-192-168-67-38.us-west-2.compute.internal   <none>           <none>
kube-system   coredns-5b8cc885bc-kf7tx                    1/1     Running   0          15m   192.168.88.68    ip-192-168-66-72.us-west-2.compute.internal   <none>           <none>
kube-system   kube-proxy-lrxp2                            1/1     Running   0          17m   192.168.66.72    ip-192-168-66-72.us-west-2.compute.internal   <none>           <none>
kube-system   kube-proxy-qts58                            1/1     Running   0          18m   192.168.67.38    ip-192-168-67-38.us-west-2.compute.internal   <none>           <none>
```
- The nodegroup template contains bootstrap to install EFA drivers in node. Confirm that the EFA drivers components were successfully installed,
```c
[root@ip-192-168-144-49 /]# fi_info -p efa
provider: efa
    fabric: efa
    domain: rdmap0s26-rdm
    version: 122.0
    type: FI_EP_RDM
    protocol: FI_PROTO_EFA
provider: efa
    fabric: efa
    domain: rdmap0s26-dgrm
    version: 122.0
    type: FI_EP_DGRAM
    protocol: FI_PROTO_EFA
```
- `aws-efa-k8s-device-plugin-daemonset` pod logs should be similar to:
```c
kubectl-stern efa ds/aws-efa-k8s-device-plugin-daemonset -n kube-system

+ efa-aws-efa-k8s-device-plugin-4kc9h › aws-efa-k8s-device-plugin
+ efa-aws-efa-k8s-device-plugin-vp978 › aws-efa-k8s-device-plugin
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Fetching EFA devices.
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 device: rdmap0s26,uverbs0,/sys/class/infiniband_verbs/uverbs0,/sys/class/infiniband/rdmap0s26
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 EFA Device list: [{rdmap0s26 uverbs0 /sys/class/infiniband_verbs/uverbs0 /sys/class/infiniband/rdmap0s26}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Starting FS watcher.
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Starting OS watcher.
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 device: rdmap0s26,uverbs0,/sys/class/infiniband_verbs/uverbs0,/sys/class/infiniband/rdmap0s26
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Starting to serve on /var/lib/kubelet/device-plugins/aws-efa-device-plugin.sock
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Registered device plugin with Kubelet
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:51:24 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:51:24 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:53:24 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:53:24 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:55:48 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:55:48 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:58:18 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:58:18 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:59:59 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 12:59:59 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:01:04 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:01:04 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:06:19 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:06:19 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:08:58 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:08:58 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:15:50 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-4kc9h aws-efa-k8s-device-plugin 2024/09/16 13:15:50 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Fetching EFA devices.
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 device: rdmap0s26,uverbs0,/sys/class/infiniband_verbs/uverbs0,/sys/class/infiniband/rdmap0s26
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 EFA Device list: [{rdmap0s26 uverbs0 /sys/class/infiniband_verbs/uverbs0 /sys/class/infiniband/rdmap0s26}]
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Starting FS watcher.
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Starting OS watcher.
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 device: rdmap0s26,uverbs0,/sys/class/infiniband_verbs/uverbs0,/sys/class/infiniband/rdmap0s26
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Starting to serve on /var/lib/kubelet/device-plugins/aws-efa-device-plugin.sock
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:21:44 Registered device plugin with Kubelet
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:51:24 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 12:51:24 Checking if device:\`rdmap0s26\` exists
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 13:15:50 Request IDs: [&ContainerAllocateRequest{DevicesIDs:[rdmap0s26],}]
efa-aws-efa-k8s-device-plugin-vp978 aws-efa-k8s-device-plugin 2024/09/16 13:15:50 Checking if device:\`rdmap0s26\` exists
```
- Cilium connectivity tests failed for 1 test with an error code as `failed to obtain the eni link list`, which most likely would be fixed by upgrading to [Cilium 1.16](https://github.com/cilium/cilium/issues/31974).
```c
cilium connectivity test
ℹ️  Monitor aggregation detected, will skip some flow validation steps
✨ [efa-cluster.us-west-2.eksctl.io] Creating namespace cilium-test for connectivity check...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying echo-same-node service...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying DNS test server configmap...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying same-node deployment...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying client deployment...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying client2 deployment...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying client3 deployment...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying echo-other-node service...
✨ [efa-cluster.us-west-2.eksctl.io] Deploying other-node deployment...
✨ [host-netns] Deploying efa-cluster.us-west-2.eksctl.io daemonset...
✨ [host-netns-non-cilium] Deploying efa-cluster.us-west-2.eksctl.io daemonset...
ℹ️  Skipping tests that require a node Without Cilium
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for deployment cilium-test/client to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for deployment cilium-test/client2 to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for deployment cilium-test/echo-same-node to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for deployment cilium-test/client3 to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for deployment cilium-test/echo-other-node to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client-d48766cfd-wst2v to reach DNS server on cilium-test/echo-same-node-6698bd45b-225ss pod...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client2-6b89df6c77-bzkgh to reach DNS server on cilium-test/echo-same-node-6698bd45b-225ss pod...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client3-7f986c467b-gn6k5 to reach DNS server on cilium-test/echo-same-node-6698bd45b-225ss pod...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client-d48766cfd-wst2v to reach DNS server on cilium-test/echo-other-node-5d67f9786b-fpc6b pod...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client2-6b89df6c77-bzkgh to reach DNS server on cilium-test/echo-other-node-5d67f9786b-fpc6b pod...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client3-7f986c467b-gn6k5 to reach DNS server on cilium-test/echo-other-node-5d67f9786b-fpc6b pod...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client-d48766cfd-wst2v to reach default/kubernetes service...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client2-6b89df6c77-bzkgh to reach default/kubernetes service...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for pod cilium-test/client3-7f986c467b-gn6k5 to reach default/kubernetes service...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for Service cilium-test/echo-other-node to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for Service cilium-test/echo-other-node to be synchronized by Cilium pod kube-system/cilium-9kbgf
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for Service cilium-test/echo-other-node to be synchronized by Cilium pod kube-system/cilium-kbcxt
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for Service cilium-test/echo-same-node to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for Service cilium-test/echo-same-node to be synchronized by Cilium pod kube-system/cilium-9kbgf
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for Service cilium-test/echo-same-node to be synchronized by Cilium pod kube-system/cilium-kbcxt
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for NodePort 192.168.67.38:32275 (cilium-test/echo-other-node) to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for NodePort 192.168.67.38:30519 (cilium-test/echo-same-node) to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for NodePort 192.168.66.72:32275 (cilium-test/echo-other-node) to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for NodePort 192.168.66.72:30519 (cilium-test/echo-same-node) to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for DaemonSet cilium-test/host-netns-non-cilium to become ready...
⌛ [efa-cluster.us-west-2.eksctl.io] Waiting for DaemonSet cilium-test/host-netns to become ready...
ℹ️  Skipping IPCache check
🔭 Enabling Hubble telescope...
⚠️  Unable to contact Hubble Relay, disabling Hubble telescope and flow validation: rpc error: code = Unavailable desc = connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4245: connect: connection refused"
ℹ️  Expose Relay locally with:
   cilium hubble enable
   cilium hubble port-forward&
ℹ️  Cilium version: 1.15.8
🏃[cilium-test] Running 91 tests ...
[=] [cilium-test] Test [no-unexpected-packet-drops] [1/91]
..
[=] [cilium-test] Test [no-policies] [2/91]
.............................................
[=] [cilium-test] Skipping test [no-policies-from-outside] [3/91] (skipped by condition)
[=] [cilium-test] Test [no-policies-extra] [4/91]
............
[=] [cilium-test] Test [allow-all-except-world] [5/91]
........................
[=] [cilium-test] Test [client-ingress] [6/91]
......
[=] [cilium-test] Test [client-ingress-knp] [7/91]
......
[=] [cilium-test] Test [allow-all-with-metrics-check] [8/91]
......
[=] [cilium-test] Test [all-ingress-deny] [9/91]
............
[=] [cilium-test] Skipping test [all-ingress-deny-from-outside] [10/91] (skipped by condition)
[=] [cilium-test] Test [all-ingress-deny-knp] [11/91]
............
[=] [cilium-test] Test [all-egress-deny] [12/91]
........................
[=] [cilium-test] Test [all-egress-deny-knp] [13/91]
........................
[=] [cilium-test] Test [all-entities-deny] [14/91]
............
[=] [cilium-test] Test [cluster-entity] [15/91]
...
[=] [cilium-test] Skipping test [cluster-entity-multi-cluster] [16/91] (skipped by condition)
[=] [cilium-test] Test [host-entity-egress] [17/91]
......
[=] [cilium-test] Test [host-entity-ingress] [18/91]
....
[=] [cilium-test] Test [echo-ingress] [19/91]
......
[=] [cilium-test] Skipping test [echo-ingress-from-outside] [20/91] (skipped by condition)
[=] [cilium-test] Test [echo-ingress-knp] [21/91]
......
[=] [cilium-test] Test [client-ingress-icmp] [22/91]
......
[=] [cilium-test] Test [client-egress] [23/91]
......
[=] [cilium-test] Test [client-egress-knp] [24/91]
......
[=] [cilium-test] Test [client-egress-expression] [25/91]
......
[=] [cilium-test] Test [client-egress-expression-knp] [26/91]
......
[=] [cilium-test] Test [client-with-service-account-egress-to-echo] [27/91]
......
[=] [cilium-test] Test [client-egress-to-echo-service-account] [28/91]
......
[=] [cilium-test] Test [to-entities-world] [29/91]
.........
[=] [cilium-test] Test [to-cidr-external] [30/91]
......
[=] [cilium-test] Test [to-cidr-external-knp] [31/91]
......
[=] [cilium-test] Skipping test [from-cidr-host-netns] [32/91] (skipped by condition)
[=] [cilium-test] Test [echo-ingress-from-other-client-deny] [33/91]
..........
[=] [cilium-test] Test [client-ingress-from-other-client-icmp-deny] [34/91]
............
[=] [cilium-test] Test [client-egress-to-echo-deny] [35/91]
............
[=] [cilium-test] Test [client-ingress-to-echo-named-port-deny] [36/91]
....
[=] [cilium-test] Test [client-egress-to-echo-expression-deny] [37/91]
....
[=] [cilium-test] Test [client-with-service-account-egress-to-echo-deny] [38/91]
....
[=] [cilium-test] Test [client-egress-to-echo-service-account-deny] [39/91]
..
[=] [cilium-test] Test [client-egress-to-cidr-deny] [40/91]
......
[=] [cilium-test] Test [client-egress-to-cidr-deny-default] [41/91]
......
[=] [cilium-test] Skipping test [clustermesh-endpointslice-sync] [42/91] (skipped by condition)
[=] [cilium-test] Test [health] [43/91]
..
[=] [cilium-test] Skipping test [north-south-loadbalancing] [44/91] (Feature node-without-cilium is disabled)
[=] [cilium-test] Test [pod-to-pod-encryption] [45/91]
.
[=] [cilium-test] Skipping test [pod-to-pod-with-l7-policy-encryption] [46/91] (requires Feature encryption-pod mode wireguard, got disabled)
[=] [cilium-test] Test [node-to-node-encryption] [47/91]
...
[=] [cilium-test] Skipping test [egress-gateway-with-l7-policy] [50/91] (skipped by condition)
[=] [cilium-test] Skipping test [egress-gateway] [48/91] (skipped by condition)
[=] [cilium-test] Skipping test [egress-gateway-excluded-cidrs] [49/91] (Feature enable-ipv4-egress-gateway is disabled)
[=] [cilium-test] Skipping test [pod-to-node-cidrpolicy] [51/91] (Feature cidr-match-nodes is disabled)
[=] [cilium-test] Skipping test [north-south-loadbalancing-with-l7-policy] [52/91] (Feature node-without-cilium is disabled)
[=] [cilium-test] Test [echo-ingress-l7] [53/91]
..................
[=] [cilium-test] Test [echo-ingress-l7-named-port] [54/91]
..................
[=] [cilium-test] Test [client-egress-l7-method] [55/91]
..................
[=] [cilium-test] Test [client-egress-l7] [56/91]
...............
[=] [cilium-test] Test [client-egress-l7-named-port] [57/91]
...............
[=] [cilium-test] Skipping test [client-egress-l7-tls-deny-without-headers] [58/91] (Feature secret-backend-k8s is disabled)
[=] [cilium-test] Skipping test [client-egress-l7-tls-headers] [59/91] (Feature secret-backend-k8s is disabled)
[=] [cilium-test] Skipping test [client-egress-l7-set-header] [60/91] (Feature secret-backend-k8s is disabled)
[=] [cilium-test] Skipping test [echo-ingress-auth-always-fail] [61/91] (Feature mutual-auth-spiffe is disabled)
[=] [cilium-test] Skipping test [echo-ingress-mutual-auth-spiffe] [62/91] (Feature mutual-auth-spiffe is disabled)
[=] [cilium-test] Skipping test [pod-to-ingress-service] [63/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [pod-to-ingress-service-deny-all] [64/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [pod-to-ingress-service-deny-ingress-identity] [65/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [pod-to-ingress-service-deny-backend-service] [66/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [pod-to-ingress-service-allow-ingress-identity] [67/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [outside-to-ingress-service] [68/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [outside-to-ingress-service-deny-world-identity] [69/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [outside-to-ingress-service-deny-cidr] [70/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Skipping test [outside-to-ingress-service-deny-all-ingress] [71/91] (Feature ingress-controller is disabled)
[=] [cilium-test] Test [dns-only] [72/91]
...............
[=] [cilium-test] Test [to-fqdns] [73/91]
............
[=] [cilium-test] Skipping test [pod-to-controlplane-host] [74/91] (skipped by condition)
[=] [cilium-test] Skipping test [pod-to-k8s-on-controlplane] [75/91] (skipped by condition)
[=] [cilium-test] Skipping test [pod-to-controlplane-host-cidr] [76/91] (skipped by condition)
[=] [cilium-test] Skipping test [pod-to-k8s-on-controlplane-cidr] [77/91] (skipped by condition)
[=] [cilium-test] Skipping test [local-redirect-policy] [78/91] (Feature enable-local-redirect-policy is disabled)
[=] [cilium-test] Test [pod-to-pod-no-frag] [79/91]
.
[=] [cilium-test] Skipping test [multicast-igmpv2-check] [85/91] (Feature multicast is disabled)
[=] [cilium-test] Skipping test [bgp-control-plane-v2] [81/91] (skipped by condition)
[=] [cilium-test] Skipping test [host-firewall-ingress] [82/91] (skipped by condition)
[=] [cilium-test] Skipping test [host-firewall-egress] [83/91] (skipped by condition)
[=] [cilium-test] Skipping test [cilium-dns-proxy-ha] [84/91] (Feature cilium-dnsproxy-ha is disabled)
[=] [cilium-test] Skipping test [bgp-control-plane-v1] [80/91] (skipped by condition)
[=] [cilium-test] Skipping test [enterprise-bgp-control-plane-v2] [88/91] (Feature enable-enterprise-bgp-control-plane is disabled)
[=] [cilium-test] Skipping test [multicast-igmpv3-check] [86/91] (Feature multicast is disabled)
[=] [cilium-test] Skipping test [multicast-connectivity] [87/91] (Feature multicast is disabled)
[=] [cilium-test] Skipping test [bfd-standalone] [89/91] (Feature enable-bfd is disabled)
[=] [cilium-test] Skipping test [bfd-bgp] [90/91] (Feature enable-bfd is disabled)
[=] [cilium-test] Test [check-log-errors] [91/91]
.
  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (config)]
  [-] Scenario [check-log-errors/no-errors-in-logs]
  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (cilium-agent)]
  ❌ Found 1 logs in efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (cilium-agent) matching list of errors that must be investigated:
time="2024-09-09T11:55:40Z" level=error msg="failed to obtain eni link list" error="interrupted system call" subsys=ipam (1 occurrences)
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (mount-cgroup)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (apply-sysctl-overwrites)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (mount-bpf-fs)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (clean-cilium-state)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (install-cni-binaries)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-kbcxt (cilium-agent)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-kbcxt (config)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-kbcxt (mount-cgroup)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-kbcxt (apply-sysctl-overwrites)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-kbcxt (mount-bpf-fs)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-kbcxt (clean-cilium-state)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-kbcxt (install-cni-binaries)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-operator-c55d96f4c-6cr97 (cilium-operator)]
.  [.] Action [check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-operator-c55d96f4c-n5hb4 (cilium-operator)]
.
📋 Test Report [cilium-test]
❌ 1/48 tests failed (1/467 actions), 43 tests skipped, 1 scenarios skipped:
Test [check-log-errors]:
  ❌ check-log-errors/no-errors-in-logs/efa-cluster.us-west-2.eksctl.io/kube-system/cilium-9kbgf (cilium-agent)
[cilium-test] 1 tests failed
```

## Install NVIDIA device plugin

The NVIDIA Collective Communications Library (NCCL) is a library of standard collective communication routines for multiple GPUs across a single node or multiple nodes. NCCL can be used together with EFA, Libfabric, and MPI to support various machine learning workloads.

- Install the NVIDIA device plugin and make sure that all pods are up and running.
```c
kubectl apply -f <https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.3/nvidia-device-plugin.yml>
```
```c
kubectl get pods -o wide -A

NAMESPACE     NAME                                        READY   STATUS    RESTARTS      AGE   IP               NODE                                           NOMINATED NODE   READINESS GATES
kube-system   aws-efa-k8s-device-plugin-daemonset-48nms   1/1     Running   0             25m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system   aws-efa-k8s-device-plugin-daemonset-r2p2g   1/1     Running   0             25m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-cvt6q                                1/1     Running   0             17m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-operator-c55d96f4c-hf7x7             1/1     Running   3 (15m ago)   17m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-operator-c55d96f4c-hjw9j             1/1     Running   3 (16m ago)   17m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system   cilium-pjm9z                                1/1     Running   0             17m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system   coredns-5b8cc885bc-8ltgd                    1/1     Running   0             17m   192.168.90.131   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system   coredns-5b8cc885bc-cn425                    1/1     Running   0             17m   192.168.94.57    ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system   kube-proxy-6fz6m                            1/1     Running   0             26m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system   kube-proxy-6ttdr                            1/1     Running   0             27m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system   nvidia-device-plugin-daemonset-26tb6        1/1     Running   0             22s   192.168.92.125   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system   nvidia-device-plugin-daemonset-mtnjv        1/1     Running   0             22s   192.168.71.71    ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
```

## Install the EFA device plugin

- Add the helm repo and install the EFA device plugin.
```c
helm repo add eks <https://aws.github.io/eks-charts>

helm install efa eks/aws-efa-k8s-device-plugin -n kube-system
```
- Check the status of the daemonset
```c
kubectl get ds -A
NAMESPACE     NAME                                  DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR                     AGE
kube-system   aws-efa-k8s-device-plugin-daemonset   2         2         2       2            2           <none>                            34m
kube-system   aws-node                              0         0         0       0            0           io.cilium/aws-node-enabled=true   41m
kube-system   cilium                                2         2         2       2            2           kubernetes.io/os=linux            26m
kube-system   kube-proxy                            2         2         2       2            2           <none>                            41m
kube-system   nvidia-device-plugin-daemonset        2         2         2       2            2           <none>                            8m52s
```

## Install MPI operator

- Create a clusterrole-mpi-operator.yaml file
```c
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    app: mpi-operator
    app.kubernetes.io/component: mpijob
    app.kubernetes.io/name: mpi-operator
    kustomize.component: mpi-operator
  name: mpi-operator
rules:
- apiGroups:
  - ""
  resources:
  - configmaps
  - secrets
  - services
  verbs:
  - create
  - list
  - watch
  - update
- apiGroups:
  - ""
  resources:
  - pods
  verbs:
  - create
  - get
  - list
  - watch
  - delete
  - update
  - patch
- apiGroups:
  - ""
  resources:
  - pods/exec
  verbs:
  - create
- apiGroups:
  - ""
  resources:
  - endpoints
  verbs:
  - create
  - get
  - update
- apiGroups:
  - ""
  resources:
  - events
  verbs:
  - create
  - patch
- apiGroups:
  - apps
  resources:
  - statefulsets
  verbs:
  - create
  - list
  - update
  - watch
- apiGroups:
  - batch
  resources:
  - jobs
  verbs:
  - create
  - list
  - update
  - watch
- apiGroups:
  - apiextensions.k8s.io
  resources:
  - customresourcedefinitions
  verbs:
  - create
  - get
- apiGroups:
  - kubeflow.org
  resources:
  - mpijobs
  - mpijobs/finalizers
  - mpijobs/status
  verbs:
  - '*'
- apiGroups:
  - scheduling.incubator.k8s.io
  - scheduling.sigs.dev
  resources:
  - queues
  - podgroups
  verbs:
  - '*'
- apiGroups:
  - coordination.k8s.io
  resources:
  - leases
  verbs:
  - get
  - create
  - delete
  - update
- apiGroups:
  - scheduling.k8s.io
  resources:
  - priorityclasses
  verbs:
  - list
  - watch
  - get
  - create
  - delete
  - update
```
- Deploy the mpi-operator
```c
kubectl apply -f clusterrole-mpi-operator.yaml
namespace/mpi-operator created
customresourcedefinition.apiextensions.k8s.io/mpijobs.kubeflow.org created
serviceaccount/mpi-operator created
clusterrole.rbac.authorization.k8s.io/kubeflow-mpijobs-admin created
clusterrole.rbac.authorization.k8s.io/kubeflow-mpijobs-edit created
clusterrole.rbac.authorization.k8s.io/kubeflow-mpijobs-view created
clusterrole.rbac.authorization.k8s.io/mpi-operator created
clusterrolebinding.rbac.authorization.k8s.io/mpi-operator created
deployment.apps/mpi-operator created
```
- Check the status of the pods
```c
kubectl get pods -A -o wide
NAMESPACE      NAME                                        READY   STATUS    RESTARTS      AGE   IP               NODE                                           NOMINATED NODE   READINESS GATES
kube-system    aws-efa-k8s-device-plugin-daemonset-48nms   1/1     Running   0             39m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system    aws-efa-k8s-device-plugin-daemonset-r2p2g   1/1     Running   0             39m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system    cilium-cvt6q                                1/1     Running   0             31m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system    cilium-operator-c55d96f4c-hf7x7             1/1     Running   3 (29m ago)   31m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system    cilium-operator-c55d96f4c-hjw9j             1/1     Running   3 (29m ago)   31m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system    cilium-pjm9z                                1/1     Running   0             31m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system    coredns-5b8cc885bc-8ltgd                    1/1     Running   0             30m   192.168.90.131   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system    coredns-5b8cc885bc-cn425                    1/1     Running   0             30m   192.168.94.57    ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system    kube-proxy-6fz6m                            1/1     Running   0             40m   192.168.74.213   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system    kube-proxy-6ttdr                            1/1     Running   0             41m   192.168.91.236   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
kube-system    nvidia-device-plugin-daemonset-26tb6        1/1     Running   0             13m   192.168.92.125   ip-192-168-74-213.us-west-2.compute.internal   <none>           <none>
kube-system    nvidia-device-plugin-daemonset-mtnjv        1/1     Running   0             13m   192.168.71.71    ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
mpi-operator   mpi-operator-7477b5bdbd-6ccdd               1/1     Running   0             42s   192.168.67.252   ip-192-168-91-236.us-west-2.compute.internal   <none>           <none>
```
- Add lease permissions for the mpi-operator cluster role.
```c
kubectl apply -f ./clusterrole-mpi-operator.yaml
clusterrole.rbac.authorization.k8s.io/mpi-operator configured
```

## Build container image to run tests on EKS

- Make sure you have [docker desktop or docker](https://docs.docker.com/engine/install/) on your machine from where you are building the image.
- Clone the [repo](https://github.com/aws-samples/awsome-distributed-training/tree/main/micro-benchmarks/nccl-tests).
- To run the NCCL tests on EKS, you must build the container image and then push it to a container registry, such as the private [ECR](https://aws.amazon.com/ecr/) in your AWS account.
```c
EFA_INSTALLER_VERSION=1.33.0
AWS_OFI_NCCL_VERSION=v1.9.2-aws
NCCL_VERSION=v2.21.5-1
NCCL_TESTS_VERSION=v2.13.9
ECR_REPOSITORY_NAME="nccl-tests"
TAG="${EFA_INSTALLER_VERSION}-${AWS_OFI_NCCL_VERSION}-${NCCL_VERSION}-${NCCL_TESTS_VERSION}"

aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME}
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:ap-northeast-2:#################:repository/nccl-tests",
        "registryId": "#################",
        "repositoryName": "nccl-tests",
        "repositoryUri": "#################.dkr.ecr.ap-northeast-2.amazonaws.com/nccl-tests",
        "createdAt": "2024-09-11T20:41:01.443000+05:30",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}
```
- Get the ECR repository URI.
```c
REPO_URI=\`aws ecr describe-repositories --query repositories[].[repositoryUri] | grep "/${ECR_REPOSITORY_NAME}" | tr -d '"' | xargs\`
ECR_URI=${REPO_URI%"/${ECR_REPOSITORY_NAME}"}
```
- Build the container image
```c
docker image build -t ${REPO_URI}:${TAG} -f ./nccl-tests.Dockerfile .
```
- Once the container image is built, you can check if it is present with `docker images`. You should see an output similar to this one:

**Note- the build time takes roughly 45 minutes**

```c
docker image build -t ${REPO_URI}:${TAG} -f ./nccl-tests.Dockerfile .
[+] Building 2676.2s (20/20) FINISHED                                                                                      docker:default
 => [internal] load build definition from nccl-tests.Dockerfile                                                                      0.0s
 => => transferring dockerfile: 5.09kB                                                                                               0.0s
 => [internal] load metadata for docker.io/nvidia/cuda:12.2.2-devel-ubuntu22.04                                                      2.3s
 => [auth] nvidia/cuda:pull token for registry-1.docker.io                                                                           0.0s
 => [internal] load .dockerignore                                                                                                    0.0s
 => => transferring context: 2B                                                                                                      0.0s
 => CACHED [ 1/15] FROM docker.io/nvidia/cuda:12.2.2-devel-ubuntu22.04@sha256:#####################################################  0.0s
 => [ 2/15] RUN apt-get update -y && apt-get upgrade -y                                                                             65.5s
 => [ 3/15] RUN apt-get remove -y --allow-change-held-packages     ibverbs-utils     libibverbs-dev     libibverbs1     libmlx5-1    1.7s
 => [ 4/15] RUN rm -rf /opt/hpcx     && rm -rf /usr/local/mpi     && rm -f /etc/ld.so.conf.d/hpcx.conf     && ldconfig               0.4s
 => [ 5/15] RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated     apt-utils     autoconf     automake   80.9s
 => [ 6/15] RUN mkdir -p /var/run/sshd                                                                                               0.3s
 => [ 7/15] RUN sed -i 's/[ #]\\(.*StrictHostKeyChecking \\).*/ \\1no/g' /etc/ssh/ssh_config &&     echo "    UserKnownHostsFile /dev/  0.5s
 => [ 8/15] RUN curl <https://bootstrap.pypa.io/get-pip.py> -o /tmp/get-pip.py     && python3 /tmp/get-pip.py     && pip3 install aw  17.4s
 => [ 9/15] RUN git clone -b v2.4.1 <https://github.com/NVIDIA/gdrcopy.git> /tmp/gdrcopy     && cd /tmp/gdrcopy     && make prefix=/o  8.9s
 => [10/15] RUN cd $HOME     && curl -O <https://efa-installer.amazonaws.com/aws-efa-installer-1.34.0.tar.gz>     && tar -xf $HOME/  320.3s
 => [11/15] RUN git clone -b v2.22.3-1 <https://github.com/NVIDIA/nccl.git>  /opt/nccl     && cd /opt/nccl     && make -j $(nproc)  2090.2s
 => [12/15] RUN DEBIAN_FRONTEND=noninteractive apt-get install -y libhwloc-dev                                                       5.4s
 => [13/15] RUN curl -OL <https://github.com/aws/aws-ofi-nccl/releases/download/${AWS_OFI_NCCL_VERSION}/aws-ofi-nccl-$>{AWS_OFI_NCCL  11.3s
 => [14/15] RUN git clone -b v2.13.10 <https://github.com/NVIDIA/nccl-tests.git> /opt/nccl-tests     && cd /opt/nccl-tests     && ma  60.5s
 => [15/15] RUN rm -rf /var/lib/apt/lists/*                                                                                          0.5s
 => exporting to image                                                                                                               9.9s
 => => exporting layers                                                                                                              9.9s
 => => writing image sha256:#####################################################                                         0.0s
 => => naming to #################.dkr.ecr.ap-northeast-2.amazonaws.com/nccl-tests:1.33.0-v1.9.2-aws-v2.21.5-1-v2.13.9                    0.0s
```
- Login to the container registry
```c
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}
```
- Push the container image to the registry
```c
docker image push ${REPO_URI}:${TAG}
The push refers to repository [#################.dkr.ecr.ap-northeast-2.amazonaws.com/nccl-tests]
241a8f2bba5c: Pushed
f03edb2c7a13: Pushed
7dcd97951db5: Pushed
679e0c0bc4db: Pushed
b45de17a8545: Pushed
62620982ee29: Pushed
a6195e5acb78: Pushed
84c22d0d520d: Pushed
d87b84cc71be: Pushed
80c4373d8c6e: Pushed
7f19e87b6573: Pushed
b8006e828af3: Pushed
0f8e361ccf92: Pushed
401c0edfce5a: Pushed
679cc72df930: Pushed
216b978392cf: Pushed
598c4c0e7d71: Pushed
97da79745aa1: Pushed
4deb6be00699: Pushed
bd4791c0dfbe: Pushed
d3e5eae7a625: Pushed
adf2c0a553e9: Pushed
77b174470c94: Pushed
c735aeb4de50: Pushed
256d88da4185: Pushed
1.33.0-v1.9.2-aws-v2.21.5-1-v2.13.9: digest: sha256:##################################################### size: 5578
```

## Run NCCL tests

- Verify the number of GPU’s on each node
```c
kubectl describe nodes  |  tr -d '\\000' | sed -n -e '/^Name/,/Roles/p' -e '/^Capacity/,/Allocatable/p' -e '/^Allocated resources/,/Events/p'  | grep -e Name  -e  nvidia.com  | perl -pe 's/\\n//'  |  perl -pe 's/Name:/\\n/g' | sed 's/nvidia.com\\/gpu:\\?//g'  | sed '1s/^/Node Available(GPUs)  Used(GPUs)/' | sed 's/$/ 0 0 0/'  | awk '{print $1, $2, $3}'  | column -t
Node                                          Available(GPUs)  Used(GPUs)
ip-192-168-144-49.us-west-2.compute.internal  4                0
ip-192-168-151-36.us-west-2.compute.internal  4                0
```
- Apply the MPIJob manifest to the cluster
```c
apiVersion: kubeflow.org/v2beta1
kind: MPIJob
metadata:
  name: test-nccl
spec:
  runPolicy:
    cleanPodPolicy: Running
    backoffLimit: 20
  slotsPerWorker: 1
  mpiReplicaSpecs:
    Launcher:
      replicas: 1
      template:
         spec:
          restartPolicy: OnFailure
          containers:
          - image: #################.dkr.ecr.ap-northeast-2.amazonaws.com/nccl-tests:1.33.0-v1.9.2-aws-v2.21.5-1-v2.13.9
            imagePullPolicy: IfNotPresent
            name: test-nccl-launcher
            env:
             - name: LD_LIBRARY_PATH
               value: /opt/amazon/openmpi/lib:/opt/nccl/build/lib:/opt/amazon/efa/lib:/opt/aws-ofi-nccl/install/lib:/usr/local/nvidia/lib:$LD_LIBRARY_PATH
             - name: PATH
               value: $PATH:/opt/amazon/efa/bin:/usr/bin
            command:
            - /opt/amazon/openmpi/bin/mpirun
            - --allow-run-as-root
            - --tag-output
            - -np
            - "1"
            - -N
            - "1"
            - --bind-to
            - none
            - -x
            - PATH
            - -x
            - LD_LIBRARY_PATH
            - -x
            - FI_PROVIDER=efa
            - -x
          # - FI_EFA_USE_DEVICE_RDMA=1
          # - -x
            - FI_EFA_FORK_SAFE=1
            - -x
            - NCCL_DEBUG=INFO
            - -x
            - NCCL_BUFFSIZE=8388608
            - -x
            - NCCL_P2P_NET_CHUNKSIZE=524288
            - --mca
            - pml
            - ^cm,ucx
            - --mca
            - btl
            - tcp,self
            - --mca
            - btl_tcp_if_exclude
            - lo,docker0,veth_def_agent
            - /opt/nccl-tests/build/all_reduce_perf
            - -b
            - "1"
            - -e
            - "16G"
            - -f
            - "2"
            - -g
            - "1"
            - -c
            - "1"
            - -n
            - "100"
    Worker:
      replicas: 2
      template:
        spec:
          nodeSelector:
            node.kubernetes.io/instance-type: "g5.12xlarge"
          containers:
          - image: #################.dkr.ecr.ap-northeast-2.amazonaws.com/nccl-tests:1.33.0-v1.9.2-aws-v2.21.5-1-v2.13.9
            imagePullPolicy: IfNotPresent
            name: test-nccl-worker
            volumeMounts:
            - name: shmem
              mountPath: /dev/shm
            resources:
              limits:
                nvidia.com/gpu: 1
                hugepages-2Mi: 5120Mi
                vpc.amazonaws.com/efa: 1
                memory: 8000Mi
              requests:
                nvidia.com/gpu: 1
                hugepages-2Mi: 5120Mi
                vpc.amazonaws.com/efa: 1
                memory: 8000Mi
          volumes:
          - name: shmem
            hostPath:
              path: /dev/shm
```
```c
kubectl apply -f nccl-tests.yaml
```

**Note- the nccl-tests.yaml file from the repo didn’t work and hence made some changes to it.**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*cR4kF-1Kp5S8OrTRyYEtmQ.png)

- The following is an example excerpt from the logs of a NCCL all\_reduce\_perf test, executed on a cluster with two g5.12xlarge instances:
```c
kubectl logs -f $(kubectl get pods | grep launcher | cut -d ' ' -f 1)
Warning: Permanently added 'test-nccl-worker-1.test-nccl.default.svc' (ED25519) to the list of known hosts.
Warning: Permanently added 'test-nccl-worker-0.test-nccl.default.svc' (ED25519) to the list of known hosts.
[1,0]<stdout>:# nThread 1 nGpus 1 minBytes 1 maxBytes 2147483648 step: 2(factor) warmup iters: 5 iters: 100 agg iters: 1 validation: 1 graph: 0
[1,0]<stdout>:#
[1,0]<stdout>:# Using devices
[1,0]<stdout>:#  Rank  0 Group  0 Pid     21 on test-nccl-worker-0 device  0 [0x00] NVIDIA A10G
[1,0]<stdout>:test-nccl-worker-0:21:21 [0] NCCL INFO Bootstrap : Using eth0:192.168.148.137<0>
[1,0]<stdout>:test-nccl-worker-0:21:21 [0] NCCL INFO cudaDriverVersion 12040
[1,0]<stdout>:test-nccl-worker-0:21:21 [0] NCCL INFO NCCL version 2.22.3+cuda12.2
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/Plugin: Failed to find ncclCollNetPlugin_v8 symbol.
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/Plugin: Failed to find ncclCollNetPlugin symbol (>= v5). ncclCollNetPlugin symbols v4 and lower are not supported.
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Initializing aws-ofi-nccl 1.11.0-aws
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Using Libfabric version 1.22
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Using CUDA driver version 12040
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Configuring AWS-specific options
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Setting NCCL_NVLSTREE_MAX_CHUNKSIZE to 512KiB
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Setting NCCL_NVLS_CHUNKSIZE to 512KiB
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Internode latency set at 150.0 us
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Creating one domain per process
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Using transport protocol SENDRECV
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Selected Provider is efa (found 1 nics)
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Could not disable CUDA API usage for HMEM, disabling GDR
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Setting FI_OPT_EFA_SENDRECV_IN_ORDER_ALIGNED_128_BYTES not supported.
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Setting NCCL_PROTO to "simple"
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Global registrations supported
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Using network AWS Libfabric
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO ncclCommInitRank comm 0x55c4c398fed0 rank 0 nranks 1 cudaDev 0 nvmlDev 0 busId 1e0 commId 0x957c4f4bad7eaafa - Init START
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NET/OFI Global registrations supported
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO comm 0x55c4c398fed0 rank 0 nRanks 1 nNodes 1 localRanks 1 localRank 0 MNNVL 0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 00/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 01/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 02/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 03/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 04/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 05/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 06/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 07/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 08/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 09/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 10/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 11/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 12/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 13/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 14/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 15/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 16/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 17/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 18/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 19/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 20/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 21/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 22/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 23/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 24/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 25/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 26/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 27/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 28/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 29/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 30/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Channel 31/32 :    0
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Trees [0] -1/-1/-1->0->-1 [1] -1/-1/-1->0->-1 [2] -1/-1/-1->0->-1 [3] -1/-1/-1->0->-1 [4] -1/-1/-1->0->-1 [5] -1/-1/-1->0->-1 [6] -1/-1/-1->0->-1 [7] -1/-1/-1->0->-1 [8] -1/-1/-1->0->-1 [9] -1/-1/-1->0->-1 [10] -1/-1/-1->0->-1 [11] -1/-1/-1->0->-1 [12] -1/-1/-1->0->-1 [13] -1/-1/-1->0->-1 [14] -1/-1/-1->0->-1 [15] -1/-1/-1->0->-1 [16] -1/-1/-1->0->-1 [17] -1/-1/-1->0->-1 [18] -1/-1/-1->0->-1 [19] -1/-1/-1->0->-1 [20] -1/-1/-1->0->-1 [21] -1/-1/-1->0->-1 [22] -1/-1/-1->0->-1 [23] -1/-1/-1->0->-1 [24] -1/-1/-1->0->-1 [25] -1/-1/-1->0->-1 [26] -1/-1/-1->0->-1 [27] -1/-1/-1->0->-1 [28] -1/-1/-1->0->-1 [29] -1/-1/-1->0->-1 [30] -1/-1/-1->0->-1 [31] -1/-1/-1->0->-1
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO NCCL_BUFFSIZE set by environment to 8388608.
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO P2P Chunksize set to 131072
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO 32 coll channels, 32 collnet channels, 0 nvls channels, 32 p2p channels, 32 p2p channels per peer
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO CC Off, Multi-GPU CC Off, workFifoBytes 1048576
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO TUNER/Plugin: Failed to find ncclTunerPlugin_v3 symbol.
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO TUNER/Plugin: Failed to find ncclTunerPlugin_v2 symbol, using internal tuner instead.
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO ncclCommInitRank comm 0x55c4c398fed0 rank 0 nranks 1 cudaDev 0 nvmlDev 0 busId 1e0 commId 0x957c4f4bad7eaafa - Init COMPLETE
[1,0]<stdout>:test-nccl-worker-0:21:28 [0] NCCL INFO Init timings: rank 0 nranks 1 total 0.17 (kernels 0.12, bootstrap 0.03, allgathers 0.00, topo 0.00, graphs 0.00, connections 0.02, rest 0.00)
[1,0]<stdout>:#
[1,0]<stdout>:#                                                              out-of-place                       in-place
[1,0]<stdout>:#       size         count      type   redop    root     time   algbw   busbw #wrong     time   algbw   busbw #wrong
[1,0]<stdout>:#        (B)    (elements)                               (us)  (GB/s)  (GB/s)            (us)  (GB/s)  (GB/s)
[1,0]<stdout>:           0             0     float     sum      -1     0.11    0.00    0.00      0     0.10    0.00    0.00      0
[1,0]<stdout>:           0             0     float     sum      -1     0.10    0.00    0.00      0     0.10    0.00    0.00      0
[1,0]<stdout>:           4             1     float     sum      -1     3.54    0.00    0.00      0     0.11    0.03    0.00      0
[1,0]<stdout>:           8             2     float     sum      -1     3.51    0.00    0.00      0     0.11    0.07    0.00      0
[1,0]<stdout>:          16             4     float     sum      -1     3.53    0.00    0.00      0     0.11    0.14    0.00      0
[1,0]<stdout>:          32             8     float     sum      -1     3.48    0.01    0.00      0     0.12    0.28    0.00      0
[1,0]<stdout>:          64            16     float     sum      -1     3.62    0.02    0.00      0     0.12    0.55    0.00      0
[1,0]<stdout>:         128            32     float     sum      -1     3.50    0.04    0.00      0     0.12    1.11    0.00      0
[1,0]<stdout>:         256            64     float     sum      -1     3.50    0.07    0.00      0     0.12    2.22    0.00      0
[1,0]<stdout>:         512           128     float     sum      -1     3.50    0.15    0.00      0     0.12    4.42    0.00      0
[1,0]<stdout>:        1024           256     float     sum      -1     3.49    0.29    0.00      0     0.11    9.01    0.00      0
[1,0]<stdout>:        2048           512     float     sum      -1     3.51    0.58    0.00      0     0.11   17.95    0.00      0
[1,0]<stdout>:        4096          1024     float     sum      -1     3.49    1.18    0.00      0     0.11   35.96    0.00      0
[1,0]<stdout>:        8192          2048     float     sum      -1     3.53    2.32    0.00      0     0.12   70.86    0.00      0
[1,0]<stdout>:       16384          4096     float     sum      -1     3.49    4.70    0.00      0     0.11  143.72    0.00      0
[1,0]<stdout>:       32768          8192     float     sum      -1     3.57    9.18    0.00      0     0.12  282.73    0.00      0
[1,0]<stdout>:       65536         16384     float     sum      -1     3.58   18.30    0.00      0     0.12  565.45    0.00      0
[1,0]<stdout>:      131072         32768     float     sum      -1     3.52   37.19    0.00      0     0.12  1129.93    0.00      0
[1,0]<stdout>:      262144         65536     float     sum      -1     3.58   73.13    0.00      0     0.12  2267.68    0.00      0
[1,0]<stdout>:      524288        131072     float     sum      -1     4.18  125.28    0.00      0     0.12  4534.97    0.00      0
[1,0]<stdout>:     1048576        262144     float     sum      -1     6.48  161.76    0.00      0     0.13  8236.40    0.00      0
[1,0]<stdout>:     2097152        524288     float     sum      -1    11.21  187.15    0.00      0     0.12  18092.93    0.00      0
[1,0]<stdout>:     4194304       1048576     float     sum      -1    21.11  198.71    0.00      0     0.12  36314.32    0.00      0
[1,0]<stdout>:     8388608       2097152     float     sum      -1    38.56  217.57    0.00      0     0.12  72817.78    0.00      0
[1,0]<stdout>:    16777216       4194304     float     sum      -1    72.82  230.40    0.00      0     0.12  145006.19    0.00      0
[1,0]<stdout>:    33554432       8388608     float     sum      -1    141.3  237.54    0.00      0     0.12  289262.34    0.00      0
[1,0]<stdout>:    67108864      16777216     float     sum      -1    278.1  241.31    0.00      0     0.12  580024.75    0.00      0
[1,0]<stdout>:   134217728      33554432     float     sum      -1    552.0  243.15    0.00      0     0.12  1157049.38    0.00      0
[1,0]<stdout>:   268435456      67108864     float     sum      -1   1099.5  244.14    0.00      0     0.12  2296086.36    0.00      0
[1,0]<stdout>:   536870912     134217728     float     sum      -1   2194.7  244.62    0.00      0     0.12  4600436.26    0.00      0
[1,0]<stdout>:  1073741824     268435456     float     sum      -1   4376.7  245.33    0.00      0     0.12  9240463.20    0.00      0
[1,0]<stdout>:  2147483648     536870912     float     sum      -1   8741.9  245.65    0.00      0     0.12  18401745.06    0.00      0
[1,0]<stdout>:test-nccl-worker-0:21:21 [0] NCCL INFO comm 0x55c4c398fed0 rank 0 nranks 1 cudaDev 0 busId 1e0 - Destroy COMPLETE
```

## References

- [https://aws.amazon.com/hpc/efa/](https://aws.amazon.com/hpc/efa/)
- [https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html#efa-instance-types](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html#efa-instance-types)
- [https://docs.aws.amazon.com/eks/latest/userguide/node-efa.html](https://docs.aws.amazon.com/eks/latest/userguide/node-efa.html)
- [https://github.com/NVIDIA/nccl-tests](https://github.com/NVIDIA/nccl-tests)
- [https://github.com/aws-samples/aws-efa-eks](https://github.com/aws-samples/aws-efa-eks)
- [https://github.com/aws-samples/aws-efa-eks/blob/main/examples/simple/nccl-efa-tests.yaml](https://github.com/aws-samples/aws-efa-eks/blob/main/examples/simple/nccl-efa-tests.yaml)
- [https://github.com/aws-samples/awsome-distributed-training/tree/main/micro-benchmarks/nccl-tests](https://github.com/aws-samples/awsome-distributed-training/tree/main/micro-benchmarks/nccl-tests)
- [https://aws.amazon.com/ec2/instance-types/g5/](https://aws.amazon.com/ec2/instance-types/g5/)
- [https://github.com/aws-samples/aws-do-eks/blob/main/Container-Root/eks/deployment/nvidia-device-plugin/deploy.sh](https://github.com/aws-samples/aws-do-eks/blob/main/Container-Root/eks/deployment/nvidia-device-plugin/deploy.sh)
- [https://github.com/aws-samples/aws-do-eks/blob/main/Container-Root/eks/deployment/efa-device-plugin/deploy.sh](https://github.com/aws-samples/aws-do-eks/blob/main/Container-Root/eks/deployment/efa-device-plugin/deploy.sh)
- [https://github.com/aws-samples/aws-do-eks/blob/main/Container-Root/eks/deployment/kubeflow/mpi-operator/clusterrole-mpi-operator.yaml](https://github.com/aws-samples/aws-do-eks/blob/main/Container-Root/eks/deployment/kubeflow/mpi-operator/clusterrole-mpi-operator.yaml)

## Try out Cilium

- [Try out Cilium](https://isovalent.com/resource-library/labs/) and get a first-hand experience of how it solves some real problems and use-cases in your cloud-native or on-prem environments related to Networking, Security or Observability.

## 🌟Conclusion 🌟

Hopefully, this post gave you a good overview how to install Cilium on an EKS cluster with the EFA adapter and run [NCCL Tests](https://github.com/NVIDIA/nccl-tests) to evaluate the performance of the network using the Nvidia Collective Communication Library.

Thank you for Reading!! 🙌🏻😁📃, see you in the next blog.

🚀 Feel free to connect/follow with me/on:

**LinkedIn**: [linkedin.com/in/agamitgupta](https://www.linkedin.com/in/agamitgupta)

[![AWS Tip](https://miro.medium.com/v2/resize:fill:96:96/1*LXqMmX8rKuWEc3D_apZ1rQ.jpeg)](https://awstip.com/?source=post_page---post_publication_info--249987d043eb---------------------------------------)

[![AWS Tip](https://miro.medium.com/v2/resize:fill:128:128/1*LXqMmX8rKuWEc3D_apZ1rQ.jpeg)](https://awstip.com/?source=post_page---post_publication_info--249987d043eb---------------------------------------)

[Last published 5 hours ago](https://awstip.com/from-kafka-to-iceberg-on-aws-s3-a-complete-guide-to-confluent-tableflow-with-aws-glue-24eb01571c72?source=post_page---post_publication_info--249987d043eb---------------------------------------)

Best AWS, DevOps, Serverless, and more from top Medium writers.

## More from Amit Gupta and AWS Tip

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--249987d043eb---------------------------------------)