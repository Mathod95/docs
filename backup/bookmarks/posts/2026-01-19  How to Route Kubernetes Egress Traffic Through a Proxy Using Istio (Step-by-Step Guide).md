---
title: "How to Route Kubernetes Egress Traffic Through a Proxy Using Istio (Step-by-Step Guide)"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@DynamoDevOps/how-to-route-kubernetes-egress-traffic-through-a-proxy-using-istio-step-by-step-guide-d76879410e01"
author:
  - "[[DevOpsDynamo]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

**Want to secure and control outbound traffic from your Kubernetes apps?** This guide will focus on the procedure of setting the egress traffic through a proxy using Istio but the legitimate and appropriate way, with the help of clean YAML, and with the use of realistic and even achievable configurations.

==👉 if you’re not a Medium member, read this story for free,== ==[here](https://medium.com/@DynamoDevOps/how-to-route-kubernetes-egress-traffic-through-a-proxy-using-istio-step-by-step-guide-d76879410e01?sk=71304333c46f05f68039dd8da819ffdb)====.==

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*_I6lKcVfe49eDwlh)

## Why This Guide Matters

In most cases of real-world Kubernetes deployments, especially in enterprise environments, one is forbidden to direct traffic to the internet immediately. This will necessitate the proxy that any traffic passes through first:

- **HTTP/S proxies**
- **Corporate firewalls**
- **Allow-list-based routing**

This is where **Istio’s Egress Gateway + ServiceEntry combo** becomes essential.

**This guide will teach you how to:**

- Configure Kubernetes to **route outbound traffic through a proxy**
- Use **Istio Egress Gateway** to enforce policies
- Avoid common pitfalls like IP-based routing

> *Perfect for: DevOps engineers, SREs, and Kubernetes practitioners working in regulated or security-conscious environments.*

## Use Case

Let’s assume you want all your pods to access `api.github.com`, but only through a **corporate proxy** at `proxy.corp.internal:3128`.

We will proceed to build it from the very beginning, the Istio way.

## Step 1: Basic Kubernetes Deployment

We’ll begin with a basic Kubernetes deployment using a `curl` container to validate outbound network traffic.

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: curlimages/curl
          command: ["sleep", "infinity"]
```

## Step 2: Enable Istio Sidecar Injection

Sidecar injection is the key to unlocking Istio’s traffic control, it lets you intercept, inspect, and route outbound traffic with precision.

```c
kubectl label namespace default istio-injection=enabled
```

Redeploy your pods afterward so sidecars get injected.## [🚀 8 FREE DevOps Labs That’ll Actually Make You Better — Not Just Busy](https://medium.com/@DynamoDevOps/8-free-devops-labs-thatll-actually-make-you-better-not-just-busy-8db4ae616a05?source=post_page-----d76879410e01---------------------------------------)

When attempting to get into DevOps or enhance what you already have, free or low-cost alternatives are as good as the…

medium.com

[View original](https://medium.com/@DynamoDevOps/8-free-devops-labs-thatll-actually-make-you-better-not-just-busy-8db4ae616a05?source=post_page-----d76879410e01---------------------------------------)## [I Passed the CKA and Created a Free Kubernetes Lab Book With 20+ Exam-Style Scenarios](https://medium.com/@DynamoDevOps/i-passed-the-cka-and-created-a-free-kubernetes-lab-book-with-20-exam-style-scenarios-93277a14dd62?source=post_page-----d76879410e01---------------------------------------)

🆓 Not a Medium member? You can still read this full story for free — no paywall, no catch. 👉 Click here to access it…

medium.com

[View original](https://medium.com/@DynamoDevOps/i-passed-the-cka-and-created-a-free-kubernetes-lab-book-with-20-exam-style-scenarios-93277a14dd62?source=post_page-----d76879410e01---------------------------------------)

[DevOpsDynamo](https://medium.com/@DynamoDevOps?source=post_page-----d76879410e01---------------------------------------)

## Istio Learning List

[View list](https://medium.com/@DynamoDevOps/list/istio-learning-list-b2aa0cd4d580?source=post_page-----d76879410e01---------------------------------------)

7 stories

![](https://miro.medium.com/v2/da:true/resize:fill:388:388/0*_I6lKcVfe49eDwlh) ![](https://miro.medium.com/v2/da:true/resize:fill:388:388/0*mKGiyYuoEKeRNdTM) ![](https://miro.medium.com/v2/da:true/resize:fill:388:388/0*mUKViOaXvQ0_izWX)

## Step 3: Define a ServiceEntry

This tells Istio which external domains are allowed and how to treat them.

```c
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: allow-github
spec:
  hosts:
    - api.github.com
  location: MESH_EXTERNAL
  ports:
    - number: 443
      name: https
      protocol: HTTPS
  resolution: DNS
```

## Step 4: Configure the Istio Egress Gateway

The Egress Gateway acts as your traffic exit point, and where the proxy logic kicks in.

```c
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: istio-egressgateway
spec:
  selector:
    istio: egressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      hosts:
        - api.github.com
```

## Step 5: Route Traffic Through the Gateway

Use a `VirtualService` to explicitly route traffic for GitHub through the egress gateway.

```c
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: github-egress
spec:
  hosts:
    - api.github.com
  gateways:
    - istio-egressgateway
  tls:
    - match:
        - port: 443
          sniHosts:
            - api.github.com
      route:
        - destination:
            host: api.github.com
            port:
              number: 443
```

## Step 6: Originate TLS at Gateway (Best Practice)

This ensures TLS handshake happens at the gateway level, not in the pod.

```c
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: tls-github
spec:
  host: api.github.com
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
```

## Optional: Add Explicit Proxy Env Variables (Non-Istio)

If your pods need to route via HTTP\_PROXY directly:

```c
env:
  - name: HTTP_PROXY
    value: http://proxy.corp.internal:3128
  - name: HTTPS_PROXY
    value: http://proxy.corp.internal:3128
  - name: NO_PROXY
    value: localhost,127.0.0.1,.svc.cluster.local
```

This works outside of Istio, but is less controllable for multi-tenant clusters.## [The CKA Exam Changed After February 18 — Here’s What You Actually Need to Practice Now](https://medium.com/@DynamoDevOps/the-cka-exam-changed-after-february-18-heres-what-you-actually-need-to-practice-now-a9941213a65a?source=post_page-----d76879410e01---------------------------------------)

For the Certified Kubernetes Administrator (CKA) exam in 2025, the main thing you need is not just to memorize…

medium.com

[View original](https://medium.com/@DynamoDevOps/the-cka-exam-changed-after-february-18-heres-what-you-actually-need-to-practice-now-a9941213a65a?source=post_page-----d76879410e01---------------------------------------)## [Kubernetes Deployment Best Practices That Actually Work in Production](https://medium.com/@DynamoDevOps/kubernetes-deployment-best-practices-that-actually-work-in-production-e8acf5b80fc7?source=post_page-----d76879410e01---------------------------------------)

Kubernetes is a powerful tool if employed on purpose. Throwing together YAML files and hoping your app survives…

medium.com

[View original](https://medium.com/@DynamoDevOps/kubernetes-deployment-best-practices-that-actually-work-in-production-e8acf5b80fc7?source=post_page-----d76879410e01---------------------------------------)

## Step 7: Test It

```c
kubectl exec -it <pod-name> -- curl https://api.github.com
```

Monitor your proxy logs or Istio telemetry (`istioctl proxy-config`) to confirm traffic flow.

## Wrap-Up

You have now acquired the various setup methods of:

- Set up **Kubernetes egress routing**
- Use **Istio Egress Gateway** to control outbound access
- Enforce traffic **through a secure proxy**

This setup is **battle-tested in production environments** and makes your cluster network policies **compliant, observable, and secure**.

## What’s Next?

👉 In **Part 3**, we’ll cover:

- How to **enforce outbound mTLS**
- Handle **DNS wildcards**
- And route **multiple domains through different proxies**

## Found this helpful?

- Clap 👏 and follow for more no-fluff Kubernetes + Istio content.

**P.S:** For anyone digging into Istio routing, this [deep dive](https://medium.com/@guy.saar/part-6-istio-virtualservice-routing-inside-the-mesh-10d79b902e2e) by Guy Saar is gold.

📘 Conquer the CKA Exam 🔥 40% OFF with JANUARY26 (valid January 17–18 only) Gumroad: [devopsdynamo.gumroad.com/l/Conquer-cka-exam](http://devopsdynamo.gumroad.com/l/Conquer-cka-exam) Payhip: [payhip.com/b/3iAsH](http://payhip.com/b/3iAsH)

## More from DevOpsDynamo

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d76879410e01---------------------------------------)