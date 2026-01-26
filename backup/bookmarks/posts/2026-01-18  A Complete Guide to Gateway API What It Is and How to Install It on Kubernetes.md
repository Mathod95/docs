---
title: "A Complete Guide to Gateway API: What It Is and How to Install It on Kubernetes"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://medium.com/@karasahinerdem/a-complete-guide-to-gateway-api-what-it-is-and-how-to-install-it-on-kubernetes-2a2e73d4dbcb
author:
  - "[[Erdem Karasahin]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*xkfILkGlPe1zE7lGRbFxTA.png)

For years, Kubernetes Ingress has been the default way to expose HTTP and HTTPS applications. It worked, it was simple, and it became a familiar part of the Kubernetes ecosystem.  
But the truth is clear now: **the Ingress era is ending**.

With the Kubernetes announcement that Ingress-NGINX is entering retirement, a major shift is happening in how we manage traffic in Kubernetes. And leading that shift is the **Gateway API** — a more modern, extensible, and powerful alternative designed to solve the limitations of traditional Ingress.

In this article, we will take you step by step through setting up the Gateway API in a Kubernetes cluster. You will learn how to install the necessary CRDs, deploy the NGINX Gateway Fabric Controller, create GatewayClass and Gateway objects, configure HTTPRoute objects, and finally, route traffic to a demo web application. By the end, you’ll have a solid understanding of how Gateway API works in practice and how it provides a more flexible, production-ready alternative to Ingress.

Before walking through installation and configuration, let’s answer the fundamental question:

## Why Should We Use Gateway API?

## 1\. Ingress Was Too Minimalistic

Ingress was intentionally built with a very narrow, HTTP-only scope. Over time, real-world needs demanded more: TCP, gRPC, mTLS, header-based routing, cross-namespace delegation, and advanced traffic policies.  
Because Ingress was too limited, each controller started building its own custom annotations. That led to:

- Vendor lock-in
- Thousands of inconsistent annotations
- Hard-to-maintain configs
- Lack of portability between environments

Gateway API solves this.

## 2\. Gateway API Is Designed for Real Production Traffic

Gateway API provides **resource types** for the entire traffic flow:

- **GatewayClass** — defines the load balancer / data plane
- **Gateway** — defines the listeners (ports, protocols, TLS termination)
- **Routes (HTTPRoute, TCPRoute, GRPCRoute, …)** — define the actual routing rules
- **Policies** — attach behavior (timeouts, retries, auth, etc.)

This is a **clean, extensible model** that finally decouples “infrastructure concerns” (what ports/protocols are exposed) from “application concerns” (how traffic is routed).

## 3\. Multi-Team and Multi-Namespace Friendly

Ingress forces everything into a single shared object controlled by cluster admins.

Gateway API supports delegation:

- Platform team manages Gateways.
- Application teams manage their own routes.

This means no giant Ingress object shared by 10 teams.  
**No accidental overwrites.**  
**No conflicts.**

## 4\. Built-In Extensibility Without Annotations

Gateway API doesn’t rely on annotations for configuration.  
Instead, it uses **CRDs and policy APIs** that are:

- Standardized
- Controller-agnostic
- Declarative
- Versioned

This solves the long-standing problem where you needed to memorize NGINX-specific annotation hacks.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*IAC71fK69TO-U-qD4X2EFg.png)

## Ingress vs. Gateway API: Practical Comparison

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9WJGY1n8bqIjD0RsCzbgHg.png)

## Step-by-Step: Setting Up Gateway API in Your Cluster

Setting up the Gateway API involves three main steps.

1. **Gateway API CRD Installation**
2. **Gateway API controller Installation**
3. **Gateway API object creation and traffic validation.**

> All relevant manifest files referenced in this document are available on my GitHub repository. [https://github.com/Erdem7/gateway-api-test](https://github.com/Erdem7/gateway-api-test)

## 1\. Gateway API CRD Installation

**Gateway API resources are not included in Kubernetes by default. To use them, we must install the Gateway API Custom Resource Definitions (CRDs).**  
You can install the CRDs with the command below. For the most recent version, check the official release page. As of this update, the latest release is **v1.3.0**.

```c
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/standard-install.yaml
```

To confirm the installation, execute the following command. The output should list the five Gateway API CRDs introduced above.

```c
kubectl get crds | grep gateway

gatewayclasses.gateway.networking.k8s.io    
gateways.gateway.networking.k8s.io          
grpcroutes.gateway.networking.k8s.io         
httproutes.gateway.networking.k8s.io         
referencegrants.gateway.networking.k8s.io
```

You can also take a look at the API resources to see more information about the CRDs you just registered.

```c
kubectl api-resources --api-group=gateway.networking.k8s.io

NAME              SHORTNAMES   APIVERSION                          NAMESPACED   KIND
gatewayclasses    gc           gateway.networking.k8s.io/v1        false        GatewayClass
gateways          gtw          gateway.networking.k8s.io/v1        true         Gateway
grpcroutes                     gateway.networking.k8s.io/v1        true         GRPCRoute
httproutes                     gateway.networking.k8s.io/v1        true         HTTPRoute
referencegrants   refgrant     gateway.networking.k8s.io/v1beta1   true         ReferenceGrant
```

## 2.Gateway API controller Installation

In this tutorial, we will use the NGINX Gateway Fabric Controller, which is now generally available (GA).

We will deploy the controller via Helm. Use the following command to pull the Helm chart:

```c
git clone https://github.com/Erdem7/gateway-api-test.git

cd gateway-api-test/nginx-gateway-fabric/
```

> *By default, the controller Helm chart sets the service type in* `*values.yaml*` *to* `*LoadBalancer*`*, so deploying in a cloud will automatically create a LoadBalancer.  
> If you’re running outside the cloud, you’ll need to expose the controller using* `*NodePort*`*. Check the NodePort section for deployment steps.*

We are not modifying the controller configuration for now.  
The NGINX Gateway Fabric Controller (Control Plane) can be installed directly with the command below:

```c
helm install ngf . -n nginx-gateway --create-namespace
```

After the installation completes, check that all controller components are up and running with the following command.

```c
kubectl -n nginx-gateway get all

NAME                                           READY   STATUS    RESTARTS   AGE
pod/ngf-nginx-gateway-fabric-55c134c5a-b37f6   1/1     Running   0          13s

NAME                               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/ngf-nginx-gateway-fabric   ClusterIP   10.XXX.XXX.XXX   <none>       443/TCP   14s

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ngf-nginx-gateway-fabric   1/1     1            1           14s

NAME                                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/ngf-nginx-gateway-fabric-55c134c5a   1         1         1       14s
```

As expected, the control plane controller pods are up and running without any problems.

The installation also took care of setting up the NGINX Fabric CRDs.

```c
kubectl get crds | grep -iE "gateway.nginx"

clientsettingspolicies.gateway.nginx.org     
nginxgateways.gateway.nginx.org             
nginxproxies.gateway.nginx.org               
observabilitypolicies.gateway.nginx.org      
snippetsfilters.gateway.nginx.org            
upstreamsettingspolicies.gateway.nginx.org
```

## Create Gateway Class

Create a file called `gateway.yaml` for your `GatewayClass` and paste in the following configuration:

```c
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: nginx-gateway-class
spec:
  controllerName: gateway.nginx.org/nginx-gateway-controller
  parametersRef:
    group: gateway.nginx.org
    kind: NginxProxy
    name: ngf-proxy-config
    namespace: nginx-gateway
```

Deploy the Gateway Class manifest

```c
kubectl apply -f gateway.yaml
```

Before setting up the Gateway object, remember to note the GatewayClass name — you’ll need it when configuring the Gateway.

To check the available Gateway Classes in your cluster:

```c
kubectl get gatewayclasses

NAME                  CONTROLLER                                   ACCEPTED   AGE
nginx-gateway-class   gateway.nginx.org/nginx-gateway-controller   True       33s
```

Let’s deploy a simple app to test Gateway API routing.

## 3\. Gateway API object creation and traffic validation.

To see the Gateway API in action, we’ll deploy a sample web application and expose it with a `ClusterIP` service.

```c
apiVersion: v1
kind: Namespace
metadata:
  name: gateway-api-test
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: gateway-api-test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      containers:
      - name: demo-app
        image: hashicorp/http-echo
        args:
          - "-text=Hello from Gateway API Test!"
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: demo-app
  namespace: gateway-api-test
spec:
  selector:
    app: demo-app
  ports:
  - port: 80
    targetPort: 5678
    protocol: TCP
  type: ClusterIP
```

To deploy this, use the following command.

```c
kubectl apply -f gateway-test-deploy.yaml
```

To get the deploy status.

```c
kubectl get pods -n gateway-api-test
NAME                                       READY   STATUS    RESTARTS   AGE
demo-app-c769c649-dts5z                    1/1     Running   0          3m32s
```

In the following section, we’ll create a Gateway and set up listeners to handle incoming traffic ports and protocols.,

### Create Gateway object

The Gateway acts as the entry point for all traffic coming into your cluster. When you create a Gateway, the Control Plane automatically sets up a Data Plane in the cluster, which is essentially a Sample deployment with its service.

The Control Plane takes the configuration from your Gateway manifest and translates it into the NGINX configuration, so that when traffic arrives, the Gateway knows exactly how to route it based on the listeners you’ve defined.

Now, let’s create a Gateway for the demo application and deploy it in the ***gateway-api-test*** namespace.

```c
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: demo-gateway
  namespace: gateway-api-test
spec:
  gatewayClassName: nginx-gateway-class
  listeners:
  - allowedRoutes:
      namespaces:
        from: Same
    hostname: demo-app.example.com
    name: http
    port: 80
    protocol: HTTP
```

> It’s important to note a key part of this YAML: `gatewayClassName: nginx-gateway-class` associates the Gateway with the GatewayClass named `nginx-gateway-class`.

With that in mind, let’s go ahead and create the Gateway.

```c
kubectl apply -f demo-gateway.yaml
```

To view the Gateway in the ***gateway-api-test*** namespace, run the following command:

```c
kubectl get gateway -n gateway-api-test
NAME           CLASS                 ADDRESS         PROGRAMMED   AGE
demo-gateway   nginx-gateway-class   20.XXX.XXX.XXX  True         100s
```

Here you can see that the Gateway has been created as a LoadBalancer due to the default Gateway API Helm configuration, and because we deployed it on AKS. To get more details, you can describe the Gateway using the following command.

*At this point, the listeners don’t have any routes assigned. We’ll configure them in the following step, as no services are connected to the Gateway API so far.*

### Create a HTTP Route Object

HTTPRoute is a Gateway API Custom Resource that defines how traffic should be routed to HTTP/HTTPS applications. Since our demo application is a web server handling HTTP/HTTPS traffic, we create this resource to manage its routing. HTTPRoute supports features such as path-based routing, hostname-based routing, custom header routing, and routing across namespaces.

```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: demo-app-route
  namespace: gateway-api-test
spec:
  hostnames:
  - demo-app.example.com
  parentRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: demo-gateway
    namespace: gateway-api-test
  rules:
  - backendRefs:
    - name: demo-app
      group: ""
      kind: Service
      port: 80
      weight: 1
    matches:
    - path:
        type: PathPrefix
        value: /
```
```c
kubectl apply -f demo-httproute.yaml
```

To see the HTTPRoute resource in your cluster, use this command:

```c
kubectl get httpRoute -n gateway-api-test
NAME                HOSTNAMES                      AGE
demo-app-route      ["demo-app.example.com"]       83s
```

Now, we can check our application over the browser.

Paste the **Load Balancer DNS** name as a **URL** in any web browser.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ffmux0Bb3qYSBJuKWdhd0g.jpeg)

## Summary

In this tutorial, we walked through setting up the Gateway API in a Kubernetes cluster from start to finish. We installed the necessary CRDs, deployed the NGINX Gateway Fabric Controller via Helm, created a Gateway and GatewayClass, and configured HTTPRoute objects to route traffic to our demo web application. Along the way, we explored how the Control Plane translates configurations into actual Web App deployments and how listeners manage incoming traffic.

With Gateway API, Kubernetes traffic management becomes more extensible, flexible, and production-ready, paving the way for advanced routing, multi-team collaboration, and modern microservices architectures. By following these steps, you now have a solid foundation for implementing Gateway API in your own clusters.

DevOps Engineer at TAV Technologies

## More from Erdem Karasahin

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--2a2e73d4dbcb---------------------------------------)