---
title: "Istio: In Simple Words with Hands-On (part 1/3)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@eshant.sah/istio-in-simple-words-with-hands-on-34fef2b2735d"
author:
  - "[[Eshant Sah]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*dMUjE6KzQ4EUDcq8vCmljA.jpeg)

### What is Istio?

> Istio is a service mesh, a dedicated infrastructure layer that controls service-to-service communication over a network. It is designed to make it easier to observe, secure, and manage traffic between microservices, especially within a Kubernetes cluster.

### So now question comes what is Service Mesh then?

> A service mesh is used primarily for managing microservices traffic, focusing on east-west traffic, which is the communication between services within the same environment.

> **East-West Traffic:**  
> Imagine a network of microservices communicating within the same cluster. This internal communication is called east-west traffic.
> 
> **North-South Traffic:**  
> This refers to traffic between an external world and the Kubernetes cluster.

### Life Before Istio:

> In a world dominated by microservices, each service needs to communicate with others, leading to several challenges. Understanding these challenges is key to appreciating the value a service mesh like Istio brings.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*iaMBG0SM67DdsTF0ZUGYVQ.png)

### Challenges in Microservice Architectures

### 1\. Visibility into Service-to-Service Communication:

> **Problem**: Kubernetes does not natively provide detailed insights into how services interact with each other. Without proper visibility, it’s difficult to monitor traffic patterns, identify bottlenecks, and understand the flow of data between services.

### 2\. Troubleshooting:

> **Problem**: In a microservices architecture, pinpointing the root cause of issues becomes complex due to the multitude of services and their interdependencies. Each service might be developed in different languages and frameworks, further complicating the debugging process.

### 3\. Security of Services:

> **Problem**: Ensuring secure communication between services is critical. However, setting up and maintaining mutual TLS (mTLS) for encrypting service-to-service communication is challenging without a unified approach.

### 4\. Routing and Service Discovery:

> Problem: Kubernetes provides basic service discovery, but advanced routing and traffic management (like canary deployments, blue-green deployments, etc.) require more sophisticated solutions.

## Here Comes the Hero: Istio

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*DMttjdXpMaDtqStjufu76A.png)

### Benefits

### 1\. Enhanced Visibility:

> Istio provides powerful observability features, including metrics, distributed tracing, and logging. Tools like Kiali, Grafana, and Jaeger integrate with Istio to give a comprehensive view of the service mesh.

### 2\. Simplified Troubleshooting:

> Istio’s detailed telemetry data and observability tools allow for efficient root cause analysis. Distributed tracing helps track requests across service boundaries.

### 3\. Robust Security:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GTF0hwWQsZWfx5M4KFKuGA.png)

> Istio enables mTLS by default for all service-to-service communication within the mesh. It also supports fine-grained access control policies and secure service authentication.

### 4\. Advanced Traffic Management:

> **Solution**: Istio provides powerful traffic management capabilities, including intelligent routing, load balancing, and service discovery.

## Istio Under the hood:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*4FXimey88ARE81erHtK71g.png)

**Istio’s architecture can be simplified into two main parts:**

1. **Control Plane:***This is like the brain of Istio. It manages how traffic should flow between services and ensures they communicate securely.*

*Control Plane consist of:*

> **Pilot (Traffic Rules)**: Pilot is like the traffic director. It’s responsible for figuring out how traffic should flow between different services.
> 
> **Citadel (Security):** Citadel acts like the security guard. It ensures that all communication between services is secure. It issues and manages certificates for each service so that they can verify each other’s identity and encrypt their communication using mutual TLS (mTLS). This keeps the data safe from prying eyes.
> 
> **Galley** (Configuration): Galley is like the configuration manager. It reads the yaml configuration and converts Kubernetes format to Istio format.

2.**Data Plane:***These are like the workers. Each service gets a little helper called Envoy proxy. These proxies handle the actual traffic, making sure it goes where it’s supposed to, stays secure, and provides insights into what’s happening.*

### Key Features of Istio

**1\. Canary Deployments:**  
*Istio allows you to roll out new versions of services gradually and observe their impact. This can be configured using traffic management rules.*

**2\. Observability:**  
*Out-of-the-box observability features like the Kiali dashboard provide insights into microservice interactions and performance.*

**3\. Circuit Breaking:**  
*Prevents cascading failures by controlling the traffic between services. It helps maintain system stability by handling service outages gracefully.*

### How Does Istio Work?

Istio works by injecting a sidecar proxy (Envoy) into each pod. This sidecar proxy intercepts and manages all network traffic in and out of the pod.

> **Sidecar Injection:**  
> When a new pod is created, Istio uses Kubernetes admission controllers to automatically inject the Envoy sidecar container. This is done using the following sequence:

**1\. Pod Creation Request:**  
*A request to create a new pod is made to the Kubernetes API server.*  
  
**2\. Admission Controllers:**  
*Before the pod is created, the admission controllers intercept the request. Istio’s dynamic admission controller then modifies the request to include the Envoy sidecar container.*

**3\. Pod Creation:**  
*The modified request is processed, and the pod is created with the Envoy sidecar.*

### Istio Hands-On: Installing Istio and Deploying a Microservice

> In this hands-on guide, we’ll walk through installing Istio in a Kubernetes cluster, deploying a microservice, and exploring key Istio features such as sidecar injection and mutual TLS (mTLS).

### Step 1: Install Istio

1. **Download Istio:**
```rb
curl -L https://istio.io/downloadIstio | sh -
 cd istio-<version>
 export PATH=$PWD/bin:$PATH
```

**2\. Install Istio in the Cluster:**

```rb
istioctl install — set profile=demo -y
```

**3\. Enable Istio Injection:**  
Label the namespace to enable Istio automatic sidecar injection.

```rb
kubectl label namespace default istio-injection=enabled
```

### Step 2: Deploy a Microservice

1. Deploy Sample Application:  
	We’ll deploy a simple microservice. For this example, let’s use a sample deployment available in Istio.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0gR9KLr5FgKda6Ty3FQZUA.png)

```rb
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
```

**2\. Check the Pods:**  
Verify that the pods are running and that each pod has two containers (the main container and the Istio sidecar).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*En90IG-lxOqRf9nZp9DdDA.png)

### Step 3: Understanding Sidecar Injection

1. **Inspect a Pod:**  
	Edit the details pod to see the containers.
```rb
kubectl edit pod details-v1–64bcb758dc-gvfnz
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*LtpFZJJrK3xDW8wsJPmN9w.png)

Look for the \`containers\` section to see both the main container and the sidecar container injected by Istio.

### Step 4: Accessing the Service

1. Create Gateway and Virtual Service: **we will learn more about gateway** and service in later section
```rb
kubectl apply -f samples/bookinfo/gateway-api/bookinfo-gateway.yaml
```

**2\. Access the Application:**  
Get the external IP of the Istio Ingress Gateway:

```rb
#Access the application by navigating to
http://<EXTERNAL_IP>/productpage\` in your browser.
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GWiqirv2TTzHCWsjIB6O8Q.png)

### Exploring Istio Features

**Mutual TLS (mTLS)**

> **1\. Enable mTLS:**  
> Istio provides mutual TLS for service-to-service communication. By default, Istio uses permissive mode.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*RVupxvQsDtGZIfHQ5LQrug.png)

> **To enforce strict mode, create a \`PeerAuthentication\` resource.**

```rb
apiVersion: security.istio.io/v1beta1
 kind: PeerAuthentication
 metadata:
 name: default
 namespace: default
 spec:
 mtls:
 mode: STRICT
```

**Apply the configuration:**

```rb
kubectl apply -f peer-authentication.yaml
```

**2\. Test mTLS:**  
Try to access a service directly using curl from a pod that doesn’t have the required certificates.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9-C1VgWxS3OU3WfUrTRzlg.png)

**You should see an error like:**

```rb
curl: (56) Recv failure: Connection reset by peer
```

> This error occurs because mTLS is enabled, and the client doesn’t have the necessary certificates. However, when services within the mesh communicate, they use mTLS and can successfully communicate because they have the required certificates.

Thank you for reading!

For understanding more about Admission Controllers in kubernetes, please refer my blog [https://medium.com/@eshant.sah/admission-controllers-in-kubernetes-with-istio-in-simple-words-74cafc373edc](https://medium.com/@eshant.sah/admission-controllers-in-kubernetes-with-istio-in-simple-words-74cafc373edc)

In our next blog, we’ll explore Istio’s Virtual Services, Gateways, and Kiali. Stay tuned for more insights and hands-on examples.

Devops Engineer at Blenheim Chalcot