---
title: "Challenge 13: All you can eat"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@danielepolencic/challenge-13-all-you-can-eat-c93045d17388"
author:
  - "[[Daniele Polencic]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

In Kubernetes, you can use limits to restrict the amount of resources, such as CPU and memory, that a container can use.

While (not) setting limits is a contentious subject in the community, setting requests is considered a best practice.

Requests for memory and CPU are necessary for the Kubernetes scheduler to decide where the pod should be deployed in the cluster.

Imagine a Kubernetes cluster with a single node with 2 vCPU and 16GB of memory.

You try to deploy a container with at least 2GB of memory and 0.1 vCPU, but when you define the Deployment, you forget requests and limits.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*RamZjx_ZrOAA6lPySTZygw.png)

What happens next if you try to scale the Deployment to 1000 replicas?

- Only 8 replicas are running. The remaining pods are pending.
- Kubernetes will schedule 1000 pods on the same node. All of them are in the “Running” state.
- Less than 8 replicas are running, and the rest are pending.
- None of the above.

## Solution

Kubernetes will schedule 1000 pods on the same node, but not all will be running (answer: none of the above).

The reason is straightforward: there are no requests, and the scheduler will assign pods on a best-effort basis.

The scheduler doesn’t consider current memory or CPU utilization, only requests, and with none of those defined, every pod has 0 memory and CPU requirements.

In other words, the scheduler will try to assign all pods to the same node because there is always space to run a process that uses 0 memory and CPU.

When the scheduler is done, 1000 pods are assigned to the node.

The kubelet will try to run all 1000 pods on the node, but things are more complex here.

The kubelet is aware of the memory utilization of the node. As soon as the memory passes the eviction threshold, it will try to evict pods to avoid running out of memory.

But once one pod is evicted, the kubelet will try to run another pod since the scheduler assigned it.

The process will likely go on forever.

How many pods are actually running? It depends on the actual memory usage.

If memory never crosses the eviction threshold, you could run a few dozen or only one.

One more thing to remember: most kubelets are configured to run up to 250 pods per node.

So, at best, you could have 250 pods running in the same node, not 1000.

If you liked this, you might also like:

- The [Kubernetes courses that we run at Learnk8s.](https://learnk8s.io/training)
- I publish the [Learn Kubernetes Weekly newsletter](https://learnk8s.io/learn-kubernetes-weekly) every week.
- This series of [20 Kubernetes concepts that I published over 20 weeks.](https://twitter.com/danielepolencic/status/1666063542011977728)

## Links

If you’d like to learn more about resource allocation, make sure you check out those resources:

- [Allocatable memory and CPU in Kubernetes Nodes](https://learnk8s.io/allocatable-resources)
- [Setting the right requests and limits in Kubernetes](https://learnk8s.io/setting-cpu-memory-limits-requests)
- [Assign Memory Resources to Containers and Pods](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/)

## More from Daniele Polencic

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--c93045d17388---------------------------------------)