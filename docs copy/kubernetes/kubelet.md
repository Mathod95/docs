---
title: Kubelet
date: 2026-01-23
status: draft
categories: Kubernetes
tags:
  - Kubernetes
  - Kubelet
source: https://blog.devops.dev/understanding-kubelet-94868f3adc07
---

**Kubelet** is one of the key component in Kubernetes. This article will help you understand what Kubelet is, what it does, and why it’s important, all explained in simple terms with examples.

### What is Kubelet?

Kubelet is an agent that runs on every node (a machine in the cluster) in a Kubernetes cluster. Its main job is to ensure that containers are running in a Pod as expected. Think of Kubelet as a caretaker that looks after the containers on its node, making sure they are healthy and running smoothly.

### Key Responsibilities of Kubelet

1. **Pod Management**: Kubelet watches for new Pod specifications and ensures they are running as described. A Pod is a group of one or more containers with shared storage and network, and a specification (a YAML or JSON file) tells Kubelet how to manage it.
2. **Health Monitoring**: Kubelet regularly checks the health of the containers in a Pod. If a container is not running correctly, Kubelet can restart it based on the defined policies.
3. **Node Communication**: Kubelet communicates with the Kubernetes API server to report the status of the node and its Pods. This helps the entire cluster stay updated on the state of each node.
4. **Container Runtime Interface (CRI)**: Kubelet uses CRI to interact with container runtimes like Docker or containerd. This allows Kubelet to manage the lifecycle of containers efficiently.

### How Kubelet Works?

Let’s break down how Kubelet functions with an example. Suppose you have a Kubernetes cluster with three nodes, and you want to deploy a web application.

1. **Defining a Pod**: You create a Pod specification file (`webapp-pod.yaml`) which includes details like the container image (e.g., `nginx`), ports, and resource limits.
```hs
apiVersion: v1 kind: Pod metadata:   
name: webapp 
spec:   
containers:   - name: 
webapp-container     
image: nginx    
ports:     - containerPort: 80
```
1. **API Server Interaction**: You submit this specification to the Kubernetes API server using `kubectl apply -f webapp-pod.yaml`. The API server stores this configuration and informs the Kubelet on each node.
2. **Pod Scheduling**: The Kubernetes scheduler decides which node should run the Pod based on resource availability and other constraints.
3. **Kubelet Actions**: Once a node is selected, Kubelet on that node takes over:
- **Pod Creation**: Kubelet reads the Pod specification and interacts with the container runtime (e.g., Docker) to pull the `nginx` image and start the container.
- **Health Checks**: Kubelet continuously monitors the health of the `webapp` container. If the container crashes, Kubelet restarts it as specified in the Pod's restart policy.
- **Status Reporting**: Kubelet updates the API server with the status of the Pod, ensuring that the cluster has the latest information.

### Why is Kubelet Important?

Kubelet is crucial for the following reasons:

- **Automation**: It automates the process of starting, stopping, and monitoring containers, reducing manual intervention.
- **Reliability**: Kubelet ensures that applications remain running and healthy, contributing to the overall reliability of the system.
- **Scalability**: By managing containers on each node, Kubelet helps Kubernetes scale applications effortlessly across multiple nodes.

### Kubelet Configuration

**Configuration Files**: Kubelet is configured using command-line flags, environment variables, and configuration files. These configurations define how Kubelet should behave and interact with other components in the Kubernetes cluster.

**Example Configuration**: Here’s a sample Kubelet configuration file:

```hs
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
address: 0.0.0.0
port: 10250
readOnlyPort: 10255
clusterDNS:
  - 10.96.0.10
clusterDomain: cluster.local
```
- `address`: The IP address for the Kubelet to serve on.
- `port`: The port for the Kubelet to serve on.
- `clusterDNS`: The DNS server IP addresses.
- `clusterDomain`: The DNS domain for the cluster.

### Kubelet’s Role in the Kubernetes Architecture

**Integration with Other Components**: Kubelet interacts with the Kubernetes API server, scheduler, and etcd. It receives Pod specifications from the API server, schedules Pods as directed by the scheduler, and maintains the state of Pods in etcd.

**Flow of Operations**: The typical flow of operations in Kubernetes involves:

1. Submitting a Pod specification to the API server.
2. The scheduler selects a node for the Pod.
3. Kubelet on the chosen node creates and manages the Pod.

### Detailed Explanation of Health Checks

Health checks are crucial for maintaining the stability and reliability of your applications in Kubernetes. Kubelet uses two primary types of health checks: **liveness probes** and **readiness probes**.

### Liveness Probes

Liveness probes determine if a container is still running. If a liveness probe fails, Kubelet will restart the container to try to fix the issue.

Example:

```hs
apiVersion: v1
kind: Pod
metadata:
  name: liveness-pod
spec:
  containers:
  - name: liveness-container
    image: nginx
    livenessProbe:
      httpGet:
        path: /healthz
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 3
```

In this example, Kubelet checks the `/healthz` endpoint of the `nginx` container every 3 seconds after an initial delay of 3 seconds. If this endpoint returns a non-200 status code, Kubelet will restart the container.

### Readiness Probes

Readiness probes determine if a container is ready to start accepting traffic. If a readiness probe fails, Kubelet will temporarily remove the Pod from the service endpoints.

Example:

```hs
apiVersion: v1
kind: Pod
metadata:
  name: readiness-pod
spec:
  containers:
  - name: readiness-container
    image: nginx
    readinessProbe:
      httpGet:
        path: /ready
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 3
```

Here, Kubelet checks the `/ready` endpoint of the `nginx` container. If this endpoint fails, the container will not receive any traffic until it passes the readiness check.

By understanding and implementing these health checks, you can ensure your applications are more resilient and capable of self-healing in the face of failures.

### Conclusion

Kubelet, acts as the node-level agent that ensures containers are running as expected. It handles Pod creation, health monitoring, and communication with the Kubernetes API server, making it an essential part of maintaining the health and efficiency of your Kubernetes cluster.