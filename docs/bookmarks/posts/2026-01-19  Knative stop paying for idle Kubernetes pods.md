---
title: "Knative: stop paying for idle Kubernetes pods"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@christian.dussol/knative-stop-paying-for-idle-kubernetes-pods-ac5e6ec350fa"
author:
  - "[[Christian Dussol]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

***Hidden cost: why are you paying for servers that do nothing?***

Your Kubernetes pods are running 24/7/365. But here’s the uncomfortable truth: most business APIs sit idle for over 70% of the week.

Consider a typical trading API in a financial services environment. Markets are open Monday through Friday, 9 AM to 6 PM. That’s 45 hours of actual usage per week. Yet you’re paying for 168 hours of compute capacity.

**That’s 123 hours of pure waste every single week.**

This is not a hypothetical scenario. This is the reality I have observed managing Treasury and Risk Management solutions at scale in regulated financial environments.

## The traditional Kubernetes cost model is broken

When you deploy a standard Kubernetes deployment, you define a minimum number of replicas. Those replicas run continuously, consuming compute resources and generating costs whether they are processing requests or sitting idle.

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-api
spec:
  replicas: 3  # Always running
  template:
    spec:
      containers:
      - name: api
        image: trading-api:v1
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
```

This model made sense when we were lifting-and-shifting monolithic applications to Kubernetes. But for modern cloud-native architectures with dozens of microservices, the cost structure doesn’t align with actual usage patterns.

## Enter Knative: Vendor-Neutral Serverless for your Kubernetes

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*G4zOt14tsvO7OVA3cBPyDQ.png)

**Knative** recently achieved **CNCF Graduation status** (September 2025), joining the elite group of battle-tested cloud-native projects. What makes Knative transformative is not just the technology, it’s the economic model it enables.

Knative provides serverless capabilities directly on your existing Kubernetes infrastructure. No proprietary platforms, no vendor lock-in, no mysterious pricing models. Your cluster, your rules.

## Two core components

**Knative Serving**: Auto-scaling HTTP workloads from zero to N and back to zero based on traffic. This is where the cost optimization magic happens.

**Knative Eventing**: CloudEvents-based event processing for building event-driven architectures. While powerful, I’ll focus on Serving for this article since that’s where the immediate business value lies.

## How Scale-to-Zero actually works

The scale-to-zero mechanism follows a simple but effective lifecycle:

1. **IDLE State:** No traffic → Zero pods running → $0/hour
2. **REQUEST Arrives:** Cold start initiated → Pods launching → 1–2 second wait
3. **ACTIVE State:** Serving requests → Pods running → Billing active
4. **BACK TO IDLE:** After 60 seconds of no traffic → Scale back to zero → $0/hour
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*FRbPNLVZh9oP0NhswmxfVw.png)

Here’s what a Knative Service looks like:

```c
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: trading-api
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/target: "10"
        autoscaling.knative.dev/scale-down-delay: "60s"
    spec:
      containers:
      - image: trading-api:v1
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
```

That’s it. Knative handles the rest: routing, auto-scaling, revision management, and graceful scale-down.

## Real-World trading API example

Let me show you the actual impact from a scenario based on production financial services workloads.

**Traditional Kubernetes Deployment:**

- 3 replicas running 24/7
- 168 hours/week billed
- Full week of compute costs

**With Knative Scale-to-Zero:**

- Active only during market hours (45 hours/week)
- 45 hours/week billed
- **73% cost reduction** by eliminating idle time

The math is straightforward: you’re eliminating 123 hours of idle compute per week, per service. That’s the difference between paying for capacity “just in case” versus paying for actual usage.

For organizations running dozens of microservices, this reduction compounds quickly. The key is identifying which services have predictable idle periods where scale-to-zero makes sense.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*IvLnIuUWjBnOkz8Gba4u2w.png)

## When to use Knative (and when not to)

**Knative is perfect for:**

✅ **HTTP APIs:** REST APIs, webhooks, API gateways

✅ **Event-driven functions:** processing events from queues or streams

✅ **Request/response workloads:** synchronous processing patterns

✅ **Services with idle periods:** development environments, batch processors, scheduled jobs

✅ **Batch processing:** ETL jobs, report generation, data processing pipelines

**Knative is NOT suitable for:**

❌ **Databases**: Always-on, stateful services requiring persistent connections

❌ **Message queues:** Persistent, connection-based services

❌ **WebSockets:** Long-lived connections conflict with scale-to-zero model

❌ **Ultra-low latency requirements:** If you can’t tolerate 1–2 second cold starts

The cold start consideration is crucial. In financial services, a 1–2 second initial latency is perfectly acceptable for back-office operations, batch processes, and most internal APIs. But for high-frequency trading systems? Stick with traditional deployments.

## Calculating your potential savings

Here’s the formula I use when evaluating Knative adoption:

**Traditional cost:**

*services × replicas × 168 hours/week × hourly\_cost*

**Knative cost:**

*services × replicas × actual\_usage\_hours × hourly\_cost*

**Percentage savings:**

*((168 – actual\_usage\_hours) / 168) × 100*

The trading API example demonstrates this clearly: 45 hours of usage versus 168 hours billed equals 73% waste elimination. Your actual savings will depend on your specific usage patterns and the number of services that can benefit from scale-to-zero.

## Governance and security: the enterprise reality

In regulated financial services environments, you can’t just deploy serverless workloads without proper governance. This is where combining Knative with policy-as-code frameworks like Kyverno becomes essential.

Here’s a Kyverno policy that enforces security best practices for Knative Services:

```c
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: knative-security-requirements
spec:
  validationFailureAction: enforce
  rules:
  - name: require-resource-limits
    match:
      resources:
        kinds:
        - Service
        namespaces:
        - production
    validate:
      message: "Knative Services must define resource limits"
      pattern:
        spec:
          template:
            spec:
              containers:
              - resources:
                  limits:
                    memory: "?*"
                    cpu: "?*"
  
  - name: enforce-minimum-scale
    match:
      resources:
        kinds:
        - Service
        namespaces:
        - production
    validate:
      message: "Production services must maintain minimum 1 replica"
      pattern:
        spec:
          template:
            metadata:
              annotations:
                autoscaling.knative.dev/min-scale: ">=1"
```

This policy ensures production Knative Services maintain at least one replica (eliminating cold starts for critical services) while still benefiting from auto-scaling.

## Vendor neutrality: the strategic advantage

Here’s what vendor neutrality actually means in practice:

**Works on ANY Kubernetes:**

- Azure AKS
- AWS EKS
- Google GKE
- Red Hat OpenShift
- On-premise Kubernetes distributions

**Same API everywhere:** your Knative service manifests are portable. No cloud-specific syntax, no proprietary extensions.

**No proprietary pricing:** you pay for the underlying compute resources you’re already using. No additional serverless tax, no per-request fees, no surprise bills.

This matters enormously in enterprise environments where multi-cloud strategies aren’t idealistic aspirations but risk management requirements.

## Getting started: practical implementation path

I’ve created a complete educational GitHub repository with everything you need to evaluate and implement Knative:

[christian-dussol-cloud-native/knative](https://github.com/christian-dussol-cloud-native/knative)

The repository includes:

1. **Cost Calculator:** Python script to model your specific cost savings
2. **Demo Examples:** complete working examples of Knative Services
3. **Kyverno Policies:** governance policies
4. **Setup Scripts:** automated installation and configuration for Minikube

## Quick Start with Minikube

```c
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --kubernetes-version=v1.28.0

# Install Knative Serving CRDs
kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-crds.yaml

# Install Knative Serving core components
kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-core.yaml

# Install Kourier as networking layer
kubectl apply -f https://github.com/knative/net-kourier/releases/latest/download/kourier.yaml

# Configure Knative to use Kourier
kubectl patch configmap/config-network \
  --namespace knative-serving \
  --type merge \
  --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'

# IMPORTANT: Start minikube tunnel for Kourier (run in separate terminal)
# This creates a route to services with type LoadBalancer
minikube tunnel

# Verify Knative is ready
kubectl get pods -n knative-serving

# Deploy your first Knative service
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        env:
        - name: TARGET
          value: "Knative"
EOF

# Get the service URL
kubectl get ksvc hello

# Test the service (in another terminal, with minikube tunnel running)
curl $(kubectl get ksvc hello -o jsonpath='{.status.url}')
```

**Important notes:**

- Keep **minikube tunnel** running in a separate terminal – it’s required for Kourier to work
- The first request will take 1–2 seconds (cold start)
- Watch the pods scale up with: **kubectl get pods -w**
- After 60 seconds of inactivity, pods will scale to zero

## The FinOps perspective

As someone involved in **FinOps practices** for cloud-native environments, Knative represents a fundamental shift in how we approach cost optimization.

Traditional FinOps focuses on rightsizing, commitment discounts, and waste elimination. These are important but incremental. Knative enables structural cost optimization by aligning billing directly with usage at the workload level.

This is particularly relevant as organizations adopt AI and ML workloads. Training jobs, batch inference, and model serving are perfect Knative candidates: they’re highly variable, resource-intensive and often idle.

## Looking Ahead: CNCF graduation and ecosystem maturity

Knative’s CNCF Graduation status signals production readiness and ecosystem maturity. The project has proven itself at scale across diverse industries and cloud environments.

What excites me most isn’t just the technology, it’s the **standardization**. As Knative becomes the de facto serverless standard for Kubernetes, we’re seeing better tooling, stronger community support, and enterprise-grade support options.

## Conclusion: the business case is clear

If you’re running Kubernetes workloads with significant idle time (and most organizations are) Knative offers a straightforward path to substantial cost reduction without changing your application code or compromising on control.

The key questions to ask:

1. What percentage of your services have predictable idle periods?
2. Can your applications tolerate 1–2 second cold starts for the first request?
3. Do you have proper governance policies in place for serverless workloads?

If you answered yes to these questions, Knative deserves serious evaluation.

The technology is mature, the cost savings are substantial and the vendor neutrality protects your strategic flexibility. That’s a combination that makes sense in any economic environment.

**Want to explore Knative further?** Check out the complete learning toolkit with code examples, cost calculators and governance policies:  
[christian-dussol-cloud-native/knative](https://github.com/christian-dussol-cloud-native/knative/)

**This is episode #1 of my CNCF Project Focus series** where I dive deep into graduated CNCF projects that deliver measurable business value. Next up: **Crossplane** for infrastructure-as-code at scale.

***Christian Dussol*** *is a Senior Engineering Manager leading cloud modernization for Treasury solutions. He focuses on the intersection of Cloud Native technologies, FinOps and Financial Services.*

*Connect with him on* [*https://www.linkedin.com/in/christiandussol/*](https://www.linkedin.com/in/christiandussol/)

Senior Engineering Manager @ Finastra | Cloud & AI | FinTech Leadership

## More from Christian Dussol

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--ac5e6ec350fa---------------------------------------)