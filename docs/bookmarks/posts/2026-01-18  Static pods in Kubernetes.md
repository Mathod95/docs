---
title: "Static pods in Kubernetes"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/google-cloud/static-pods-in-kubernetes-703357901d7d"
author:
  - "[[The kube guy]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@thekubeguy)## [Google Cloud - Community](https://medium.com/google-cloud?source=post_page---publication_nav-e52cf94d98af-703357901d7d---------------------------------------)

[![Google Cloud - Community](https://miro.medium.com/v2/resize:fill:38:38/1*FUjLiCANvATKeaJEeg20Rw.png)](https://medium.com/google-cloud?source=post_page---post_publication_sidebar-e52cf94d98af-703357901d7d---------------------------------------)

A collection of technical articles and blogs published or curated by Google Cloud Developer Advocates. The views expressed are those of the authors and don't necessarily reflect those of Google.

As we already know, a pod is the smallest deployable unit that can be created and managed. Typically, pods are managed by controllers such as Deployments, ReplicaSets, and StatefulSets, which handle the lifecycle of pods according to the desired state defined by the user. However, there are scenarios where you might want to create and manage pods directly on a specific node without involving these higher-level abstractions. This is where static pods come into play.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0zPTJa3JsZIRSQK_HvYyLA.png)

Image by Author

Static pods are managed directly by the kubelet on a specific node and are not part of the Kubernetes API server’s management. They are defined in the node’s filesystem and are useful in situations where you need to ensure that certain critical pods are always running on specific nodes.

### How Static Pods Work?

Static pods are created and managed by the kubelet rather than the Kubernetes API server. The kubelet watches the specified directory on the node’s filesystem for static pod manifests (YAML files). When it detects a new pod manifest, it creates the pod and starts the containers defined within it. The ==kubelet is responsible for monitoring and restarting the static pod if it crashes.==

### Creating Static Pods

To create a static pod, you need to place a pod manifest file in a specific directory on the node. By default, this directory is `/etc/kubernetes/manifests`, but it can be configured differently depending on your kubelet setup. Here’s an example of a simple static pod manifest file:

```c
apiVersion: v1
kind: Pod
metadata:
  name: static-webserver
  labels:
    app: webserver
spec:
  containers:
  - name: webserver
    image: nginx:latest
    ports:
    - containerPort: 80
```

Save this file as `static-webserver.yaml` and place it in the `/etc/kubernetes/manifests` directory on the node. The kubelet will automatically detect this file and create the pod.

### Scenarios Where Static Pods Are Useful

### 1\. Bootstrapping a Kubernetes Cluster

Static pods are often used during the initial bootstrapping of a Kubernetes cluster. For instance, the control plane components such as `kube-apiserver`, `kube-scheduler`, and `kube-controller-manager` are usually deployed as static pods to ensure they are always running on the master nodes.

### 2\. Running Critical System Components

Certain critical system components that need to be running before the Kubernetes API server is fully operational can be deployed as static pods. This ensures that these components are always available, even if the API server is down.

### 3\. Custom Node-Level Services

If you have custom services that need to run on specific nodes and should not be managed by the Kubernetes scheduler, static pods are an ideal solution. For example, monitoring agents, logging agents, or node-specific daemons can be deployed as static pods.

### 4\. Ensuring High Availability

Static pods can be used to ensure high availability of essential services by running them on specific nodes. This is particularly useful in edge computing scenarios where certain services need to be guaranteed to run on remote or isolated nodes.

### Example: Monitoring Agent as a Static Pod

Consider a scenario where you need to run a monitoring agent on each node in your Kubernetes cluster to collect and send metrics to a central monitoring system. Using static pods is a straightforward and reliable way to achieve this.

### Step-by-Step Example

1. **Create the Pod Manifest**
```c
apiVersion: v1
kind: Pod
metadata:
  name: node-monitor-agent
  labels:
    app: monitor-agent
spec:
  containers:
  - name: monitor-agent
    image: monitoring-agent:latest
    volumeMounts:
    - name: host-root
      mountPath: /host
      readOnly: true
  volumes:
  - name: host-root
    hostPath:
      path: /
      type: Directory
```
1. **Save the Manifest File:** Save the above manifest as `node-monitor-agent.yaml`.
2. **Deploy the Static Pod:** Place the `node-monitor-agent.yaml` file in the `/etc/kubernetes/manifests` directory on each node.

The kubelet on each node will detect the manifest file and create the monitoring agent pod, ensuring that the agent runs on every node in the cluster.

### Conclusion

By bypassing the Kubernetes API server, they ensure that vital components are always available, even during API server outages. Understanding and leveraging static pods can significantly enhance the reliability and availability of your Kubernetes deployments.

Whether you are bootstrapping a cluster, running node-specific services, or ensuring high availability, static pods offer a simple yet powerful tool to achieve your goals

If you’ve learned a new thing today then I deserve few claps and a slap on that follow button

[The kube guy](https://medium.com/u/54b070394829?source=post_page---user_mention--703357901d7d---------------------------------------)

. Also share it with your friends and colleagues

[![Google Cloud - Community](https://miro.medium.com/v2/resize:fill:48:48/1*FUjLiCANvATKeaJEeg20Rw.png)](https://medium.com/google-cloud?source=post_page---post_publication_info--703357901d7d---------------------------------------)

[![Google Cloud - Community](https://miro.medium.com/v2/resize:fill:64:64/1*FUjLiCANvATKeaJEeg20Rw.png)](https://medium.com/google-cloud?source=post_page---post_publication_info--703357901d7d---------------------------------------)

[Last published 2 days ago](https://medium.com/google-cloud/the-keyless-cloud-implementing-workload-identity-for-gke-and-cloud-run-c1c294d794db?source=post_page---post_publication_info--703357901d7d---------------------------------------)

A collection of technical articles and blogs published or curated by Google Cloud Developer Advocates. The views expressed are those of the authors and don't necessarily reflect those of Google.

I'll help you sail through the ocean of Kubernetes with minimal efforts

## More from The kube guy and Google Cloud - Community

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--703357901d7d---------------------------------------)