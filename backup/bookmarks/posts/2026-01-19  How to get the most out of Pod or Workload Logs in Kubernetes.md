---
title: "How to get the most out of Pod or Workload Logs in Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/kubernetes-how-to-get-the-most-out-of-pod-or-workload-logs-in-kubernetes-48f8a00f8c24"
author:
  - "[[Guillermo Quiros]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@gquiman)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-48f8a00f8c24---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*gW1FkOkpCXLL1JkesmEZag.png)

If you’re a serious DevOps engineer managing a Kubernetes cluster, you’ll quickly realize that mastering logs is essential to your craft. Logs help us understand what’s happening inside pods, the components that run containers and host our applications.

**1\. What we can get out of the logs**

Logs provide insights into:

So we are going to start with **kubectl** and see how we can get logs from pods and deployment, after we will present some alternatives.

**2\. Kubectl Basic Commands**

If a pod only have one container we can just:

```c
kubectl logs <pod-name>
```

If we have multiple containers we need to choose the container we want the logs for:

```c
kubectl logs <pod-name> -c <container-name>
```

If we want to actively monitor logs we probably want to tail then, here is how is done:

```c
kubectl logs -f <pod-name>
```

Something I didn’t know for a while is that even if a pod crashes, we can still retrieve the logs from before the crash. This is really useful since pods are ephemeral.

```c
kubectl logs <pod-name> -c <container-name> --previous
```

**3\. Time-Based Log Filtering**

Being able to avoid getting lost in a bunch of logs can be super useful. Here are some commands I use every day.

Show the last 50 lines for example:

```c
kubectl logs --tail=50 <pod-name>
```

Show logs from the past hour:

```c
kubectl logs --since=1h <pod-name>
```

Show logs since a specific date:

```c
kubectl logs --since-time="2024-06-25T12:00:00Z" <pod-name>
```

**4\. How to Make Logs More Readable**  
The output from these commands isn’t always easy to read, so here are some tips to make logs easier to consume. Trust me — after a full day of work, you’ll appreciate this.

Include dates in logs output:

```c
kubectl logs --timestamps <pod-name>
```

Combine with UNIX tools to only show what is relevant:

```c
kubectl logs <pod-name> | grep "ERROR"
```
```c
kubectl logs <pod-name> | jq '.'
```
```c
kubectl logs <pod-name> | less
```

**5\. Viewing Logs from Deployments and ReplicaSets**

Since deployments manage multiple pods, you’ll need to fetch logs from all pods associated with a deployment.

View logs from all pods under a deployment:

```c
kubectl logs -l app=<label> --all-containers=true
```

Alternatively, list the pods first:

```c
kubectl get pods -l app=<label>
```
```c
kubectl logs <pod-name>
```

Or use a loop:

```c
for pod in $(kubectl get pods -l app=myapp -o name); do
  kubectl logs $pod;
done
```

But they are way better tools to manage Kubernetes logs.

One tool that I like is **stern** for colored, live streaming of logs across multiple pods.

```c
stern <pod-name-prefix>
```

This would give you this kind of output:

```c
api-server-5d68df8676-bk9gq app 2025-06-27T10:12:45.123Z Connected to database successfully
api-server-5d68df8676-xvljm app 2025-06-27T10:12:45.456Z Received request: GET /healthz
api-server-5d68df8676-bk9gq app 2025-06-27T10:12:46.001Z Processed job #1234
api-server-5d68df8676-xvljm app 2025-06-27T10:12:46.332Z Returned status 200 for /healthz
api-server-5d68df8676-bk9gq app 2025-06-27T10:12:47.876Z ERROR: Timeout while processing job #1235
```

Some other features of stern:

- Tail logs from multiple pods
- Color-coded output by pod/container
- RegEx matching for pod names
- Automatic updates as pods scale or restart.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GKoJsyMw0rJdhYBFtrcQdQ.png)

Another tool is [K8studio](https://k8studio.io/)

With **K8studio**, you can select a pod and access its logs, or choose a workload to see the combined logs of all the pods managed by a deployment or replicaset. You can also cherry-pick which pods and containers you want to view. Logs are color-coded — typically the pod or container names, as well as the timestamps.  
You can **tail** logs, or filter them by time or range. There’s also support for **searching and filtering text**, and yes — you can **download** the log file.

## More from Guillermo Quiros and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--48f8a00f8c24---------------------------------------)