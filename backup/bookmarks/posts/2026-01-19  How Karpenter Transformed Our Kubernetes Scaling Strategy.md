---
title: "How Karpenter Transformed Our Kubernetes Scaling Strategy"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@spraneeth4/how-karpenter-transformed-our-kubernetes-scaling-strategy-2cbf14d72858"
author:
  - "[[praneeth_vvs]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*RBGw2b5V22k8aT9r)

## Introduction

Kubernetes has been the standard platform for a while for running microservices at scale, and managing scalability has evolved into a critical part of our daily operations. Previously, we relied on **Cluster Autoscaler** with predefined node groups in AWS EKS to manage scaling. While this setup initially worked well, the increasing complexity of our workloads highlighted its limitations.

We eventually transitioned to **Karpenter**, an open-source Kubernetes node lifecycle manager originally developed by AWS. Since its introduction in 2021 and subsequent donation to the Cloud Native Computing Foundation (CNCF), Karpenter has enabled faster, smarter, and more cost-effective provisioning of compute capacity. With the release of **Karpenter v1.0** in **August 2024**, the project has officially moved out of beta and is now offering a stable API with production-ready features. It’s almost been a year since this release, and Karpenter has proven to be a robust and reliable solution for dynamic Kubernetes scaling.

In this article, I’ll share our journey moving from Cluster Autoscaler with static node pools to Karpenter’s dynamic node provisioning. I’ll also explain how Karpenter helped simplify our scaling strategy, reduce costs, and make workload management much easier.

## The Problem with Predefined Node Groups

In our early EKS setup, we used Cluster Autoscaler with predefined node groups. While this was manageable at first, it quickly became complex as various teams introduced workloads with specific resource requirements:

- **GPU instances** for compute-heavy tasks like machine learning model training.
- **ARM64/x86\_64 instances** for architecture-specific optimization.
- **Memory-optimized instances** for workloads like in-memory databases.
- **CPU-focused instances** for stateless services, CI/CD pipelines, and web apps.

We had to manage and maintain multiple node pools. This approach led to inefficiencies, over-provisioning, and increased management overhead.

## Why Use a Single Cluster for All Workload Types?

You might be wondering, “ **Why use a single cluster for all these diverse workload types?**” The reason is simple: this is a shared development cluster for testing purposes. Since it’s not a production environment, consolidating multiple workloads into a single cluster allows us to efficiently experiment with different configurations without the overhead of managing multiple clusters and managing network setup.

In a production environment, we would choose to separate workloads across different clusters to optimize for performance, security, and compliance. However, even in these cases, Karpenter remains an excellent choice. From my understanding, its features would fit nearly 90% of scenarios, provided you have a clear picture of the scaling requirements. For testing and development, consolidating all workloads into a single cluster with Karpenter has proven to be an excellent decision, offering seamless scalability and efficiency.

## Moving to Karpenter

Realizing that we needed a more flexible and cost-effective solution, we decided to give Karpenter a try. Unlike Cluster Autoscaler, which requires predefined node pools, Karpenter automatically provisions EC2 instances based on real-time requirements. It dynamically selects the right instance type (whether it’s GPU, ARM64, CPU, or memory-based) for a new node to spawn a pending pod, depending on the workload, without requiring us to create and manage static node pools.

Karpenter allowed us to consolidate our workloads into one dynamic node pool. Instead of manually configuring node pools for each type of workload, Karpenter scales the resources dynamically based on actual demand. This not only simplified our infrastructure management but also optimized resource allocation, reducing waste and cutting costs.

## Benefits We Realized:

## 1\. Faster and More Efficient Scaling:

The standout feature of Karpenter is its direct interaction with the EC2 API. ***Unlike traditional setups where scaling decisions are managed through an Auto Scaling Group (ASG), Karpenter bypasses ASG entirely. When a pod is pending due to resource shortages, Karpenter directly calls the EC2 API to provision new instances***. This direct interaction eliminates delays associated with ASG scaling actions, ensuring that new instances are available faster and more accurately. Karpenter also has the flexibility to use Spot Instances, which helps us optimize cost savings during non-peak periods.

- **Karpenter:** Provisions nodes in **~45–60 seconds**.
- **Cluster Autoscaler:** Detects unschedulable pods in **30–60 seconds**, but node provisioning may take **3–5 minutes** due to ASG and instance boot time.

Also, in case of **Spot instance interruptions**, Karpenter can provision a new node **within the 2-minute AWS notice period**, minimizing disruption.

## 2\. Consolidating Multiple Workloads into a Dynamic Node Pool

Instead of maintaining node pools for each workload, we now define generalized requirements in a single `NodePool`. Karpenter dynamically provisions instances that match pod resource needs.

To illustrate the contrast clearly, here’s a real example I used during our transition:

### Cluster Autoscaler Example (Static NodeGroup):

```c
apiVersion: eks.amazonaws.com/v1alpha1
kind: NodeGroup
metadata:
  name: ca-cpu-nodegroup
spec:
  instanceTypes:
    - m5.large
  desiredCapacity: 2
  maxSize: 5
  minSize: 1
```

In this setup, all nodes are of type `m5.large`, and you must create **another NodeGroup** if you want a different instance type (e.g., `r5.large` for memory-heavy workloads). Managing this for multiple instance types becomes a burden as your infrastructure grows.

### Karpenter Example (v1.0 NodePool + EC2NodeClass):

```c
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    metadata:
      labels:
        type: karpenter
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: kubernetes.io/os
          operator: In
          values: ["linux"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      expireAfter: 720h
  limits:
    cpu: 1000
    memory: 1000Gi
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
```
```c
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default-nodeclass
spec:
  amiFamily: AL2
  role: "KarpenterNodeRole-cluster"
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: "my-cluster"
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: "my-cluster"
```

With Karpenter, we don’t predefine which instance type gets used for which workload. Instead, Karpenter evaluates each pod’s requirements and dynamically provisions the best-fit EC2 instance. This level of abstraction has been a major improvement for us.

## 3\. Cost Efficiency and Optimization

- **Only needed resources are provisioned, reducing idle costs:**  
	Karpenter dynamically provisions compute based on real-time pod requirements. This ensures you’re only paying for the resources your workloads actually need, avoiding the traditional practice of over-provisioning for peak traffic that may never come.
- **Spot Instances can be used for non-critical workloads:**  
	Karpenter supports mixing Spot and On-Demand instances. For non-critical or fault-tolerant workloads like batch jobs, CI pipelines, or development environments, Spot Instances provide a substantial cost advantage without compromising overall application availability.
- **Consolidation logic automatically removes underutilized nodes:**  
	When nodes are underused, such as during off-peak hours, Karpenter identifies them and reschedules their pods onto other nodes (if possible), then safely terminates the empty ones. This keeps your cluster lean and cost-efficient without manual intervention.

## Caveats and Lessons Learned

While Karpenter has delivered big improvements, here are a few considerations:

1. **Karpenter Consolidation and Disruption**: Karpenter is very good at saving costs by removing underutilized nodes quickly. This is called **consolidation:** it looks for nodes that aren’t being fully used and then tries to move the pods to other nodes so it can shut them down. **Karpenter can sometimes aggressively scale down. If not configured correctly, this may disrupt pods.** To prevent this, you can use **PodDisruptionBudgets (PDBs)**. A PDB tells Kubernetes how many pods can be disrupted (evicted) at the same time. For example, you can set it so that **at least one replica must always be running**, even during node consolidation. In high-scale environments, tuning is required. Metrics collection, logging, and tighter disruption controls become important to avoid unexpected behaviors

2\. Here are some isssues reported on github which may require some attention:

- **Aggressive underutilized consolidation causing node churn**  
	In a 15-node EKS cluster, Karpenter repeatedly terminated and replaced nodes during low-traffic hours, often cycling through 2–3 generations of nodes in quick succession. This resulted in frequent pod evictions and four restarts for some pods in a short time frame: [https://github.com/aws/karpenter-provider-aws/issues/7146](https://github.com/aws/karpenter-provider-aws/issues/7146)
- An issue highlights that new `NodeClaims` being deleted just **2 minutes after creation**, even while user pods were still initializing. This prevented pods from ever becoming stable and caused continual disruption: [https://github.com/aws/karpenter-provider-aws/issues/7356](https://github.com/aws/karpenter-provider-aws/issues/7356)

## Conclusion

Migrating to Karpenter has completely changed our approach to Kubernetes scaling. We’ve simplified infrastructure, cut costs using Spot Instances, and improved responsiveness to workload changes. Karpenter’s flexibility that aligns well with both dev/test and production-grade setups.

If you’re exploring more adaptive and cost-efficient Kubernetes scaling strategies, Karpenter is absolutely worth a look. With its now-stable v1.0 release, it’s fast, flexible, open-source, and production-ready.

From my experience, once you understand your scaling requirements clearly, Karpenter can fit into nearly any architecture scenario with minimal friction.

*Happy learning:)*

**If you enjoyed this article and want to connect, feel free to reach out to me on** [**LinkedIn**](https://www.linkedin.com/in/praneeth-vvs/)**.**

## More from praneeth\_vvs

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--2cbf14d72858---------------------------------------)