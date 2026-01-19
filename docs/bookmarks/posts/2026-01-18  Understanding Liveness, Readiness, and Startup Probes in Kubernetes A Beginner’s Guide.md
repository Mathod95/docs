---
title: "Understanding Liveness, Readiness, and Startup Probes in Kubernetes: A Beginner’s Guide"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@cloudandnodejstutorials/understanding-liveness-readiness-and-startup-probes-in-kubernetes-a-beginners-guide-5b71b584fb3e"
author:
  - "[[cloud & nodejs tutorials]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@cloudandnodejstutorials)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*tvFx2vNSEH5ZPYU6lIxbdA.png)

## Introduction

Kubernetes is a powerful platform for managing containerized applications. It automates deployment, scaling, and operations of application containers. One of the key features of Kubernetes is its ability to ensure the health of your applications. Liveness, Readiness, and Startup Probes are essential mechanisms to help manage and maintain the stability of your applications. In this article, we will discuss these probes and their attributes, and provide examples of how to configure them in YAML files.

### Liveness Probe

A Liveness Probe is used to check if your application is running. If it fails, Kubernetes will restart the container. This helps to ensure that your application is always up and running. To configure a Liveness Probe, you can use the following attributes in your YAML file:

1. `httpGet`: This checks if your application is running by sending an HTTP GET request to a specific path and port.
2. `tcpSocket`: This checks if your application is running by opening a TCP connection to a specific port.
3. `exec`: This checks if your application is running by executing a command inside the container.

Example:

```c
apiVersion: v1
kind: Pod
metadata:
  name: liveness-httpget-example
spec:
  containers:
  - name: liveness-httpget
    image: your-image
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 20
```

### Readiness Probe

A Readiness Probe is used to check if your application is ready to accept requests. If it fails, Kubernetes will stop sending traffic to the container. This helps to ensure that your application is ready to serve users. To configure a Readiness Probe, you can use the same attributes as the Liveness Probe.

Example:

```c
apiVersion: v1
kind: Pod
metadata:
  name: readiness-tcpsocket-example
spec:
  containers:
  - name: readiness-tcpsocket
    image: your-image
    readinessProbe:
      tcpSocket:
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
```

### Startup Probe

A Startup Probe is used to check if your application has started. If it fails, Kubernetes will assume that your application is still starting and will not start any Liveness or Readiness Probes. To configure a Startup Probe, you can use the same attributes as the Liveness and Readiness Probes.

Example:

```c
apiVersion: v1
kind: Pod
metadata:
  name: startup-exec-example
spec:
  containers:
  - name: startup-exec
    image: your-image
    startupProbe:
      exec:
        command:
        - node
        - /app/startup.js
      initialDelaySeconds: 10
      periodSeconds: 5
```

## Conclusion

Liveness, Readiness, and Startup Probes are crucial components to maintain the stability of your applications in a Kubernetes environment. By understanding their functions and how to configure them in your YAML files using httpGet, tcpSocket, and exec, you can effectively monitor and manage the health of your containerized applications.

## More from cloud & nodejs tutorials

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--5b71b584fb3e---------------------------------------)