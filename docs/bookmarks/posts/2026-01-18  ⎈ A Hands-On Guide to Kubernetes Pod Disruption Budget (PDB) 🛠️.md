---
title: "⎈ A Hands-On Guide to Kubernetes Pod Disruption Budget (PDB) 🛠️"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@muppedaanvesh/a-hand-on-guide-to-kubernetes-pod-disruption-budget-pdb-%EF%B8%8F-ebe3155a4b7c"
author:
  - "[[Anvesh Muppeda]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Eu-tyRoKKMCxEa8lbMbi4Q.png)

PDB

In Kubernetes, managing application availability during cluster maintenance, scaling events, or other disruptions is crucial. Pod Disruption Budgets (PDB) provide a means to ensure that a certain number of pods in a deployment or replica set are available during such events. In this blog, we’ll explore what PDBs are, why they’re important, and how to use them effectively.

## What is a Pod Disruption Budget (PDB)?

A Pod Disruption Budget is a Kubernetes resource that specifies the minimum number of pods that must remain available during a disruption caused by voluntary actions (like scaling down) or involuntary actions (like node failures). PDBs help maintain application stability by preventing too many pods from being simultaneously unavailable.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*AF4qWa5Q8gCks184.png)

## Why are Pod Disruption Budgets important?

Imagine a scenario where a Kubernetes cluster needs to undergo maintenance or scale down due to resource constraints. Without a `PDB`, Kubernetes could potentially terminate too many pods simultaneously, causing downtime or service degradation. `PDBs` ensure that a minimum number of pods are kept running to maintain service availability.

## PDB Example

### 1\. Create Nginx Application

Let’s create a simple nginx deployment using the below manifest file.

Apply the above nginx deployment manifest file using the blow command.

```c
kubectl apply -f nginx-deployment.yaml
```

Tha above will create a new deployment in kubernetes cluster with **6 replicas**.

```c
$ kubectl get po
NAME                     READY   STATUS    RESTARTS   AGE
nginx-6f4cfc8479-glrgb   1/1     Running   0          9s
nginx-6f4cfc8479-mcrsd   1/1     Running   0          9s
nginx-6f4cfc8479-pn5xz   1/1     Running   0          9s
nginx-6f4cfc8479-vfvvd   1/1     Running   0          9s
nginx-6f4cfc8479-x2kfk   1/1     Running   0          9s
nginx-6f4cfc8479-xrgcb   1/1     Running   0          9s
```

### 2\. Create the PDB

Now let’s create a **(Pod Disruption Budget)PDB** to specifies a minimum of 2 Pods available for Nginx Pods with the label **“app: nginx-controller”**.

In thePDB manifest file you may use `maxUnavailable` as well instead of `minAvailable`.

Apply the above `PDB` manifest file using the below command.

```c
kubectl apply -f nginx-pdb.yaml
```

The above will create a new PDB with the name `nginx-pdb`. This PDB ensure the minimum of 2 Pods available for Nginx Pods with the label **“app: nginx-controller”**.

```c
$ kubectl get pdb
NAME        MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
nginx-pdb   3               N/A               3                     35s
```

Let’s describe the PDB.

```c
$ kubectl describe pdb nginx-pdb
Name:           nginx-pdb
Namespace:      pdb-testing
Min available:  3
Selector:       app=nginx-controller
Status:
    Allowed disruptions:  3
    Current:              6
    Desired:              3
    Total:                6
Events:                   <none>
```

### 3\. Now let’s test the PDB (Create a Disruption)

Let’s now put our `Pod Disruption Budget` (`PDB`) to the test. We’ve set up the PDB and associated it with our Nginx application. To see the PDB in action, we’ll drain the single worker node in our cluster and observe if it gets deleted.

```c
$ kubectl get node              
NAME                   STATUS   ROLES    AGE   VERSION
pool-t5ss0fagn-jeb47   Ready    <none>   26h   v1.29.1
```

Since our PDB specifies a minimum of 3 Nginx pods, draining the node should not result in its deletion. Kubernetes should prevent the node from being deleted because it needs at least one worker node to maintain the required number of Nginx pods. Let’s proceed to observe this behavior.

Use the below command to drain:

```c
$ kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```

In my case i am using the below command:

```c
$ kubectl drain pool-t5ss0fagn-jeb47 --ignore-daemonsets --delete-emptydir-data
```

I have tried to drain the node using the above command but getting below errors:

```c
error when evicting pods/"nginx-6f4cfc8479-vfvvd" -n "pdb-testing" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
error when evicting pods/"nginx-6f4cfc8479-xrgcb" -n "pdb-testing" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
error when evicting pods/"nginx-6f4cfc8479-x2kfk" -n "pdb-testing" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
```

As expected our node is not terminating due to our pdb.

```c
$ kubectl get node              
NAME                   STATUS                     ROLES    AGE   VERSION
pool-t5ss0fagn-jeb47   Ready,SchedulingDisabled   <none>   26h   v1.29.1
```

See our node is not terminated

```c
$ kubectl get po -n pdb-testing
NAME                     READY   STATUS    RESTARTS   AGE
nginx-6f4cfc8479-bprl8   0/1     Pending   0          17s
nginx-6f4cfc8479-m2gn2   0/1     Pending   0          17s
nginx-6f4cfc8479-qkmnz   0/1     Pending   0          17s
nginx-6f4cfc8479-vfvvd   1/1     Running   0          8m54s
nginx-6f4cfc8479-x2kfk   1/1     Running   0          8m54s
nginx-6f4cfc8479-xrgcb   1/1     Running   0          8m54s
```

In this scenario, the first three Nginx pods were attempted to be removed, but they couldn’t due to our `Pod Disruption Budget` (`PDB`). However, the last three Nginx pods remained intact, demonstrating the PDB’s enforcement of maintaining a minimum number of pods.

That’s it, we have successfully tested the `PDB` and confirmed that it’s working as expected.

## Additional Tip

If you set `maxUnavailable` to 0% or 0, or you set `minAvailable` to 100% or the number of replicas, you are requiring zero voluntary evictions. When you set zero voluntary evictions for a workload object such as ReplicaSet, then you cannot successfully drain a Node running one of those Pods. If you try to drain a Node where an unevictable Pod is running, the drain never completes. This is permitted as per the semantics of `PodDisruptionBudget`.

## Conclusion:

Pod Disruption Budgets are a vital resource in Kubernetes for maintaining application availability during disruptions. By setting minimum availability requirements, PDBs help ensure that your applications remain operational even in challenging circumstances. Understanding and utilizing PDBs effectively can significantly enhance the reliability of your Kubernetes workloads.

## Source Code

You’re invited to explore our [GitHub repository](https://github.com/anveshmuppeda/kubernetes), which houses a comprehensive collection of source code for Kubernetes.## [GitHub - anveshmuppeda/kubernetes: Kuberntes Complete Notes](https://github.com/anveshmuppeda/kubernetes?source=post_page-----ebe3155a4b7c---------------------------------------)

Kuberntes Complete Notes. Contribute to anveshmuppeda/kubernetes development by creating an account on GitHub.

github.com

[View original](https://github.com/anveshmuppeda/kubernetes?source=post_page-----ebe3155a4b7c---------------------------------------)

Also, if we welcome your feedback and suggestions! If you encounter any issues or have ideas for improvements, please open an issue on our [GitHub repository](https://github.com/anveshmuppeda/kubernetes/issues). 🚀

## Connect With Me

If you found this blog insightful and are eager to delve deeper into topics like AWS, cloud strategies, Kubernetes, or anything related, I’m excited to connect with you on [LinkedIn](https://www.linkedin.com/in/anveshmuppeda/). Let’s spark meaningful conversations, share insights, and explore the vast realm of cloud computing together.

Feel free to reach out, share your thoughts, or ask any questions. I look forward to connecting and growing together in this dynamic field!

Happy deploying! 🚀

Happy Kubernetings! ⎈

I’m a Kubernetes developer and cloud architect Certifications: 3x AWS | 2x Kubernetes Connect with me on [www.linkedin.com/in/anveshmuppeda](http://www.linkedin.com/in/anveshmuppeda)

## More from Anvesh Muppeda

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--ebe3155a4b7c---------------------------------------)