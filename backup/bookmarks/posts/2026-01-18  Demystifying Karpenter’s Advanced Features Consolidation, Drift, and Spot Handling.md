---
title: "Demystifying Karpenter’s Advanced Features: Consolidation, Drift, and Spot Handling"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@gajaoncloud/demystifying-karpenters-advanced-features-consolidation-drift-and-spot-handling-007fbad29549"
author:
  - "[[Gajanan Chandgadkar]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Karpenter, an open-source project from AWS, automates provisioning and management of Kubernetes worker nodes, simplifying cluster scaling and resource optimization. Beyond its core functionalities, Karpenter offers powerful advanced features that enhance its capabilities and empower you to fine-tune your cluster’s behavior. This blog post delves into three of these features: **consolidation**, **drift detection** & **handling**, and **spot instance handling.**

**Before diving into these advanced features, I recommend that you have a solid understanding of the fundamentals covered in below posts:**

- **Post 1**: [Unleash the Power of Karpenter: Automating AWS EKS Scaling and Cost Optimization](https://medium.com/@gaja.devops/unleash-the-power-of-karpenter-automating-aws-eks-scaling-and-cost-optimization-7e236319eda4)
- **Blog 2**: [Karpenter Mastery: NodePools & NodeClasses for Workload Nirvana](https://medium.com/@gaja.devops/karpenter-mastery-nodepools-nodeclasses-for-workload-nirvana-bc89850fa934)

Familiarity with these topics will provide a strong foundation for comprehending and effectively implementing Karpenter’s advanced features.

## Workload Consolidation

Consolidation helps maintain optimal resource utilization by automatically identifying and addressing underutilized nodes in your cluster, leading to **cost savings**. Karpenter achieves this through several strategies:

- **Identifying Underutilized Nodes:** Karpenter continuously monitors the resource utilization of nodes in a NodePool.
- **Empty Nodes:** When a node becomes **empty** (no pods scheduled), Karpenter can **remove** it from the cluster entirely.
- **Right-sizing Nodes:** Based on the evolving workload demands, Karpenter can **recommend** or **automatically** replace existing nodes with instances of **lower pricing tiers** that meet the current resource requirements.

**Steps to enable the feature: In nodepool configuration, set following policy**

Refer — [Code repo](https://github.com/gajacloudninja/aws-eks-karpenter-cost-optimization/blob/main/manifests/cost-optimized-spot-pool-nodepool.yaml#L33) (so simple)

```c
# Describes which types of Nodes Karpenter should consider for consolidation
# If using 'WhenUnderutilized', Karpenter will consider all nodes for
# consolidation and attempt to remove or replace Nodes when it discovers 
# that the Node is underutilized and could be changed to reduce cost
# If using \`WhenEmpty\`, Karpenter will only consider nodes for consolidation 
# that contain no workload pods
    consolidationPolicy: WhenUnderutilized | WhenEmpty
```

Lets walk through using few examples: Over a period of time your cluster may look like this. You have four residual instances running. The first one is really awesome, nicely bin-packed tight. Last three not so much, lot of underutilized nodes. With Karpenter, all you need to do is in the NodePool put this consolidation policy *WhenUnderutilized | WhenEmpty* and Karpenter will automatically bin-pack the pods and get rid of other EC2 instances.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*99oBQ2TspaRkvTaKBq9pjQ.png)

After Bin-packing:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*NBJ_4Vwt7pHliky9tKYdiQ.png)

Not only this, it is also intelligent enough…So let’s say in this case the last two EC2 instances are m5.xlarge. Even if we consolidate these two pods into one m5.xlarge, that will still be waste (based on pod requirement). So Karpenter will get rid of those two m5.xlarge and provision a m5.large and bin-pack your nodes. So it’s better selection of worker nodes and reduced cost.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*tPZuww2FjdoTllQP8UOUxw.png)

After Bin-packing:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*xzfomSVuRwer4VPjfT2XMA.png)

### Kaprenter logs for consolidation:

```c
{"level":"INFO","time":"2024-03-02T19:58:09.544Z","logger":"controller.disruption",
"message":"disrupting via emptiness delete, 
terminating 1 candidates ip-172-xx-xx-xx.ec2.internal/t3.small/spot","commit":"17d6c05","command-id":"e0f63152-4fc2-41b3-ae43-c2345d1b851d"}

{"level":"INFO","time":"2024-03-02T19:58:10.102Z","logger":"controller.disruption.queue","message":"command succeeded","commit":"17d6c05","command-id":"e0f63152-4fc2-41b3-ae43-c2345d1b851d"}

{"level":"INFO","time":"2024-03-02T19:58:10.164Z","logger":"controller.node.termination","message":"tainted node","commit":"17d6c05","no
de":"ip-172-xx-xx-xx.ec2.internal"}
{"level":"INFO","time":"2024-03-02T19:58:10.602Z","logger":"controller.node.termination","message":"deleted node","commit":"17d6c05","
node":"ip-172-xx-xx-xx.ec2.internal"}
{"level":"INFO","time":"2024-03-02T19:58:10.959Z","logger":"controller.nodeclaim.termination",
"message":"deleted nodeclaim","commit":"17d6c05","nodeclaim":"cost-optimized-spot-pool-86fmb","node":"ip-172-xx-xx-xx.ec2.internal"
```

### Karpenter Log Summary

These logs indicate Karpenter successfully terminated a spot instance (IP address redacted) due to it being empty:

- **19:58:09**: Karpenter initiated the termination process.
- **19:58:10**: The termination command was successfully queued.
- **19:58:10**: The node was marked as tainted.
- **19:58:10**: The node and its associated node claim were deleted.

This behavior aligns with Karpenter’s resource optimization strategy, where it removes idle nodes to reduce costs.

## Karpenter Drift

Drift feature helps day two operation. One of the big challenges for us is Kubernetes version is upgraded or as AWS releases new AMIs, you need to constantly go and change those AMIs and constantly trigger the upgrades. Karpenter actually solves that problem using a concept called the Drift.

**Scenario 1: Patching/upgrading with default AMI means you dont specify any AMI id in EC2NodeClass configuration.**

*EC2NodeClass* default behavior

- Amazon EKS Optimized Linux AMI is used (for *v1.26*)
- AWS publishes recommended AMIs for each version in AWS Systems Manager
- Karpenter selects the AMI from the parameter store
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*uZgwX1eQEn7WRtbNL6tfFg.png)

- If there is Drift, Karpenter updates the worker nodes with new AMIs automatically
- Done in rolling deployment fashion
- Here you can see the new AMI’ updated for worker nodes
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*uZgwX1eQEn7WRtbNL6tfFg.png)

**Scenario 2: Patching/upgrading with Drift — Custom AMI**

Behavior is similar to Default AMI

- Custom AMIs are used in your application
- [Select AMIs using *amiSelector* field in *EC2NodeClass*](https://github.com/gajacloudninja/aws-eks-karpenter-cost-optimization/blob/main/manifests/cost-optimized-spot-pool-nodeclass.yaml#L15)
- If multiple AMIs found, Karpenter will use the latest one
- If no AMIs found, no nodes will be provisioned
- *EC2NodeClass status.amis* field lists discovered AMIs

Karpenter logs for Drift in AMI:

```c
{"level":"INFO","time":"2024-03-02T20:17:52.079Z","logger":"controller.disruption",
"message":"disrupting via drift replace, terminating 1 candidates ip-172-xx-xx-xx.ec2.internal/t3.small/spot and replacing with spot node }
{"level":"INFO","time":"2024-03-02T20:17:56.199Z","logger":"controller.nodeclaim.lifecycle","message":"launched nodeclaim","commit":"17d6c05",
"nodeclaim":"cost-optimized-spot-pool-vng4j","provider-id":"aws:///us-east-1c/i-0d552f10ba2227800","instance-type":"t3.small","zone":"us-east-1c","capacity-type":"spot","allocatable":{"cpu":"1930m","ephemeral-storage":"17Gi","memory":"1418Mi","pods":"11"}}
{"level":"INFO","time":"2024-03-02T20:18:42.495Z","logger":"controller.nodeclaim.lifecycle","message":"initialized nodeclaim","commit":"17d6c05","nodeclaim":"cost-optimized-spot-pool-vng4j","provider-id":"aws:///us-east-1c/i-0d552f10ba2227800","node":"ip-172-xx-xx-xx.ec2.internal"}
{"level":"INFO","time":"2024-03-02T20:18:50.110Z","logger":"controller.disruption.queue",
"message":"command succeeded","commit":"17d6c05","command-id":"0e1bdae7-5ae8-41db-80c5-55a186633978"}
{"level":"INFO","time":"2024-03-02T20:18:50.168Z","logger":"controller.node.termination",
"message":"tainted node","commit":"17d6c05","node":"ip-172-17-190-112.ec2.internal"}
{"level":"INFO","time":"2024-03-02T20:18:53.169Z","logger":"controller.node.termination",
"message":"deleted node","commit":"17d6c05","node":"ip-172-xx-xx-xx.ec2.internal"}
```

**Scenario 3: Updates to EKS control plane**

*EC2NodeClass* default behavior

- Karpenter monitors the parameter store
- Karpenter selects the recommended AMI for the new EKS version
- Karpenter updates the worker nodes AMIs automatically
- Done in rolling deployment fashion

> Zero touch and secure — always latest EKS optimized AMI

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*6d_OegnL_b6ZoEeZ-Q8FKA.png)

## Spot Interruption Handling

Spot interruption, Spots are awesome. Here node pools can be configured for a mix of on-demand and Spot, but here’s the kicker, Karpenter has built-in Spot interruption handler.

You do not need to trap the Spot interruption and use bunch of other additional software. Karpenter watches an SQS queue which receives critical events from AWS services which may affect your nodes. Karpenter requires that an SQS queue be provisioned and EventBridge rules and targets be added that forward interruption events from AWS services to the SQS queue.

And when you install Karpenter you can give the name of the sqs queue, EventBridge sends spot interruption to sqs queue. Once this is done, Karpenter does the rest.

It traps the two minute interruption warning and then it spins up the Spot instance. You are not required to use no termination handlers.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PmzDTrnzg2B8qKVDQMRdsA.png)

**To enable interruption handling,** configure the `--interruption-queue-name` CLI argument with the name of the interruption queue provisioned to handle interruption events. If you are using helm charts, update below mentioned value:

- interruptionQueue is disabled if not specified. Enabling interruption handling may require additional permissions on the controller service account.  
	*interruptionQueue: “ ”*

> Karpenter’s advanced features empower you to fine-tune your Kubernetes cluster for optimal resource utilization, cost efficiency, and reliability. By leveraging consolidation, drift detection and handling, and spot instance handling, you can:

- **Minimize node count**: Remove empty nodes and consolidate workloads, reducing unnecessary infrastructure costs.
- **Maintain consistent state**: Detect and address configuration drift, ensuring your nodes adhere to desired specifications.
- **Optimize resource utilization**: Scale efficiently with Spot instances while managing interruptions gracefully.

Remember, thorough testing and adaptation are crucial for successful implementation. Explore these features, experiment in a controlled environment, and leverage the documentation and community resources to further enhance your cluster management expertise using Karpenter.

I trust this blog post has provided valuable insights into Karpenter’s advanced features. If you have any questions or require further assistance, feel free to explore the official Karpenter documentation or engage with the community forums.

Principal - Cloud Operations Architect HP Inc

## More from Gajanan Chandgadkar

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--007fbad29549---------------------------------------)