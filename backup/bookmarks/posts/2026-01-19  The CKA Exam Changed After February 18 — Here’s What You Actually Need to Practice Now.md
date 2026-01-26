---
title: "The CKA Exam Changed After February 18 — Here’s What You Actually Need to Practice Now"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@DynamoDevOps/the-cka-exam-changed-after-february-18-heres-what-you-actually-need-to-practice-now-a9941213a65a"
author:
  - "[[DevOpsDynamo]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

For the Certified Kubernetes Administrator (CKA) exam in 2025, the main thing you need is not just to memorize commands. The exam has changed since **February 18**, and the new is more hands-on, scenario-based, and realistic than ever. I’ve selected four examples that perfectly match the spirit of the new CKA.

👉 if you’re not a Medium member, rea this story for free, [here](https://medium.com/@DynamoDevOps/the-cka-exam-changed-after-february-18-heres-what-you-actually-need-to-practice-now-a9941213a65a?sk=908017bfae720c23f464ae59cadd8015).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*XEawsywY81HfoBSPX_6tlA.png)

**Table of Contents**

· [Scenario 1: Leave Room on the Node with CPU/Memory Calculations](https://medium.com/@DynamoDevOps/#eda7)  
∘ [Context](https://medium.com/@DynamoDevOps/#2026)  
∘ [Always Remember](https://medium.com/@DynamoDevOps/#a1ee)  
∘ [Step 1: Calculate Per-Container Requests](https://medium.com/@DynamoDevOps/#c0e0)  
∘ [Step 2: Apply Resource Requests in Manifest](https://medium.com/@DynamoDevOps/#77a1)  
∘ [Step 3: Validate Allocation](https://medium.com/@DynamoDevOps/#7847)  
∘ [Explanation](https://medium.com/@DynamoDevOps/#8f6a)  
∘ [Expected Outcome](https://medium.com/@DynamoDevOps/#c324)  
∘ [Exam Tip](https://medium.com/@DynamoDevOps/#74e8)  
· [Scenario 2: Managing Pod Scheduling with PriorityClass](https://medium.com/@DynamoDevOps/#59b3)  
∘ [Key Concepts](https://medium.com/@DynamoDevOps/#723b)  
∘ [Step 1: Create PriorityClasses](https://medium.com/@DynamoDevOps/#4565)  
∘ [Step 2: Deploy Low-Priority Workload](https://medium.com/@DynamoDevOps/#b33f)  
∘ [Step 3: Deploy High-Priority Workload](https://medium.com/@DynamoDevOps/#32e5)  
∘ [Step 4: Observe Preemption](https://medium.com/@DynamoDevOps/#7e35)  
∘ [Step 5: Troubleshooting](https://medium.com/@DynamoDevOps/#7708)  
∘ [Summary](https://medium.com/@DynamoDevOps/#3b77)  
∘ [Exam Tip](https://medium.com/@DynamoDevOps/#410b)  
· [Scenario 3: Installing and Testing Gateway API with NGINX Gateway](https://medium.com/@DynamoDevOps/#7068)  
∘ [Step 1: Install Gateway API CRDs](https://medium.com/@DynamoDevOps/#dc41)  
∘ [Step 2: Deploy NGINX Gateway Fabric Controller](https://medium.com/@DynamoDevOps/#b91e)  
∘ [Step 3: Check GatewayClass](https://medium.com/@DynamoDevOps/#41d0)  
∘ [Step 4: Deploy Backend Application](https://medium.com/@DynamoDevOps/#7119)  
∘ [Step 5: Create Gateway](https://medium.com/@DynamoDevOps/#d6e2)  
∘ [Step 6: Create HTTPRoute](https://medium.com/@DynamoDevOps/#9bdf)  
∘ [Step 7: Validate Gateway and Route](https://medium.com/@DynamoDevOps/#3061)  
∘ [Step 8: Test Routing](https://medium.com/@DynamoDevOps/#962b)  
∘ [Explanation](https://medium.com/@DynamoDevOps/#15ee)  
∘ [Expected Outcome](https://medium.com/@DynamoDevOps/#2b11)  
∘ [Exam Tip](https://medium.com/@DynamoDevOps/#7c60)  
· [Scenario 4: Creating and Using a DatabaseBackup CRD](https://medium.com/@DynamoDevOps/#6ea0)  
∘ [Step 1: Create the CRD](https://medium.com/@DynamoDevOps/#c2a6)  
∘ [Step 2: Create Valid Instance](https://medium.com/@DynamoDevOps/#6d55)  
∘ [Step 3: Test Invalid Instance](https://medium.com/@DynamoDevOps/#eff1)  
∘ [Explanation](https://medium.com/@DynamoDevOps/#6372)  
∘ [Expected Outcome](https://medium.com/@DynamoDevOps/#90ff)  
∘ [Exam Tip](https://medium.com/@DynamoDevOps/#275f)  
· [Final Advice for Exam Day](https://medium.com/@DynamoDevOps/#73f0)

## Scenario 1: Leave Room on the Node with CPU/Memory Calculations

**Domain:** Workloads & Scheduling (15%)  
**Objective:** Distribute CPU and memory requests across multiple containers while intentionally leaving capacity free for other workloads.

### Context

You have a node with:

- **4Gi allocatable memory**
- **2 CPU (2000 millicores)**

You must deploy **3 Pods**, each with **2 containers** (total of 6 containers), while using only about **two-thirds of the node’s capacity**.

### Always Remember

- “Leave room” in exam tasks means you should **not allocate full node capacity**.
- Use quick **mental math** to divide resources evenly.
- Always check `kubectl describe node` for allocatable values before calculating.

### Step 1: Calculate Per-Container Requests

**Target usage: ≈ 66% of total capacity**

- **Memory per container**: `4Gi × 0.66 ÷ 6 ≈ 450Mi`
- **CPU per container**: `2000m × 0.66 ÷ 6 ≈ 220m`

**Total usage:** ≈ 2.64Gi memory and 1320m CPU  
**Remaining:** ≈ 1.36Gi memory and 680m CPU

### Step 2: Apply Resource Requests in Manifest

```c
resources:
  requests:
    memory: "450Mi"
    cpu: "220m"
```

Apply this block to each container.

### Step 3: Validate Allocation

```c
kubectl describe node <node-name>
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'
```

### Explanation

- Overcommitting nodes causes throttling or eviction.
- Requests affect scheduling; limits affect usage.
- “Leave room” requires manual calculation.

### Expected Outcome

- All Pods scheduled successfully.
- Node retains unallocated capacity.

### Exam Tip

- Convert CPUs to **millicores**, Gi to **Mi**.
- If Pods are Pending, recheck requests.
- No calculators allowed, practice mental math.

## Scenario 2: Managing Pod Scheduling with PriorityClass

**Domain:** Scheduling (5%)  
**Objective:** Influence Kubernetes scheduler using `PriorityClass`, ensuring higher-priority workloads are scheduled first and can preempt lower-priority Pods.

### Key Concepts

- `value`: Higher number = higher priority.
- `preemptionPolicy`: `PreemptLowerPriority` allows eviction of lower-priority pods.
- `PriorityClass` is cluster-scoped.
- Preemption only happens when absolutely needed.

### Step 1: Create PriorityClasses

**File:**`priorityclasses.yaml`

```c
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 100000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "High priority class"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority
value: 100
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "Low priority class"
```
```c
kubectl apply -f priorityclasses.yaml
kubectl get priorityclass
```

### Step 2: Deploy Low-Priority Workload

**File:**`nginx-low.yaml`

```c
...
priorityClassName: low-priority
```

### Step 3: Deploy High-Priority Workload

**File:**`nginx-high.yaml`

```c
...
priorityClassName: high-priority
```
```c
kubectl apply -f nginx-low.yaml
kubectl apply -f nginx-high.yaml
```

### Step 4: Observe Preemption

```c
kubectl get deployments
kubectl get pods -o wide
kubectl describe pod <pod-name>
```

**Expect:** Low-priority pods evicted or Pending. High-priority pods running.

### Step 5: Troubleshooting

- Node might have enough resources, adjust values.
- Preemption takes time.
- Confirm `preemptionPolicy`.

### Summary

- Use `PriorityClass` to control pod scheduling.
- High-priority workloads can evict lower-priority ones.
- Check `kubectl describe` to confirm preemption.

### Exam Tip

- Stuck Pods with `0/1 nodes available` = no pods to evict.
- Fastest solution: high-value `PriorityClass` + attach to Pod.
- Look for preemption events to verify behavior.

## Scenario 3: Installing and Testing Gateway API with NGINX Gateway

**Domain:** Services & Networking (20%)  
**Objective:** Deploy NGINX Gateway Fabric, configure Gateway API (`Gateway`, `HTTPRoute`), and verify routing to backend application.

### Step 1: Install Gateway API CRDs

```c
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.1.0/standard-install.yaml
kubectl get crd | grep gateway
```

### Step 2: Deploy NGINX Gateway Fabric Controller

```c
kubectl create namespace nginx-gateway
kubectl apply -k https://github.com/nginxinc/nginx-gateway-fabric/tree/main/deploy/default
kubectl get pods -n nginx-gateway
```

### Step 3: Check GatewayClass

```c
kubectl get gatewayclass
```

**Expect:**`nginx`

### Step 4: Deploy Backend Application

**File:**`whoami.yaml`

```c
apiVersion: apps/v1
...
kind: Deployment
...
image: docker.io/containous/whoami:v1.5.0
```
```c
kubectl apply -f whoami.yaml
kubectl get pods,svc
```

### Step 5: Create Gateway

**File:**`gateway.yaml`

```c
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
...
gatewayClassName: nginx
```

### Step 6: Create HTTPRoute

**File:**`route.yaml`

```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
...
hostnames:
- example.com
```
```c
kubectl apply -f gateway.yaml
kubectl apply -f route.yaml
```

### Step 7: Validate Gateway and Route

```c
kubectl get gateway
kubectl describe httproute whoami-route
```

**Expect:**`Accepted=True`, `PROGRAMMED=True`

### Step 8: Test Routing

Map in `/etc/hosts`:

```c
<EXTERNAL-IP> example.com
```

Test:

```c
curl http://example.com
```

### Explanation

- `GatewayClass` ties to controller.
- `Gateway` exposes cluster traffic.
- `HTTPRoute` maps requests to services.
- Troubleshoot top-down: CRDs → Controller → Gateway → Route → Backend.

### Expected Outcome

- Gateway and HTTPRoute accepted.
- Curl returns valid app response.

### Exam Tip

- No DNS? Use `/etc/hosts`.
- Always test with `curl`.
- If controller exists, skip to resource creation.

## Scenario 4: Creating and Using a DatabaseBackup CRD

**Domain:** Cluster Architecture, Installation & Configuration (25%)  
**Objective:** Create a `CustomResourceDefinition` for database backups with validation, and test schema enforcement.

### Step 1: Create the CRD

**File:**`databasebackup-crd.yaml`

```c
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databasebackups.dbadmin.com
spec:
  group: dbadmin.com
  ...
  versions:
  - name: v1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              database:
                type: string
              schedule:
                type: string
              retentionDays:
                type: integer
                minimum: 1
            required:
              - database
              - schedule
              - retentionDays
```
```c
kubectl apply -f databasebackup-crd.yaml
```

### Step 2: Create Valid Instance

**File:**`prod-db-backup.yaml`

```c
apiVersion: dbadmin.com/v1
kind: DatabaseBackup
metadata:
  name: prod-db-backup
spec:
  database: prod-db
  schedule: "0 2 * * *"
  retentionDays: 7
```
```c
kubectl apply -f prod-db-backup.yaml
kubectl get databasebackups
```

### Step 3: Test Invalid Instance

**File:**`invalid-db-backup.yaml`

```c
retentionDays: 0
```
```c
kubectl apply -f invalid-db-backup.yaml
```

**Expect:**

```c
spec.retentionDays: Invalid value: 0: must be greater than or equal to 1
```

### Explanation

- `required` enforces presence.
- `minimum` enforces range.
- CRDs store and validate data only, no logic unless a controller exists.

### Expected Outcome

- Valid instance works.
- Invalid instance fails with schema error.

### Exam Tip

- Use `kubectl explain crd` to explore structure.
- Existing CRD? Skip to creating instances.
- Schema nesting errors are common.

**A Small Recommendation**  
For anyone planning the CKA in 2026, I maintain a practical guide that’s continuously refined with real feedback and updated labs.

It’s available on [**Gumroad**](https://devopsdynamo.gumroad.com/l/Conquer-cka-exam) or [**Payhip**](https://payhip.com/b/3iAsH) with full details there.

This weekend only (**January 17–18**), there’s **40% off** with the code **JANUARY26**.

You can grab the free one here if you want:

- [**Gumroad**](https://devopsdynamo.gumroad.com/l/devopsdynamo)
- [**Payhip**](https://payhip.com/b/1HK5t)

## Final Advice for Exam Day

The CKA exam is not only about your knowledge of Kubernetes that you possess but also your ability to handle the stress of the situation. Be prepared for things that don’t go well: Your terminal may freeze, your browser may lag, or maybe the YAML you wrote yesterday suddenly won’t apply. Practice real situations, and also simulate how to overcome inconveniences while dealing with issues such as switching to different SSH sessions, a strange DNS failure, or even low screen resolution. Conclusively focus on setting up your environment to set up your alias, without making excessive optimizations that may confuse your brain by being entangled in dotfiles. In addition, it’s essential to reserve time for revision. Mistakes happen when one is in a hurry. Make sure you finish with at least 10–15 minutes for revision.

If you want to get some practice in without setting anything up, KodeKloud has a bunch of **free hands-on Kubernetes labs** you can run straight from your browser: [**https://kodekloud.com/pages/free-labs/kubernetes**](https://kodekloud.com/pages/free-labs/kubernetes)

They’re great for getting familiar with the basics or quickly simulating exam-style tasks.

**But honestly?**  
The best way that worked for me, and for a lot of people I know, is **setting up your own cluster**. Nothing beats hitting real issues, debugging them, and figuring things out under pressure. That’s where the real learning happens.

📘 Conquer the CKA Exam 🔥 40% OFF with JANUARY26 (valid January 17–18 only) Gumroad: [devopsdynamo.gumroad.com/l/Conquer-cka-exam](http://devopsdynamo.gumroad.com/l/Conquer-cka-exam) Payhip: [payhip.com/b/3iAsH](http://payhip.com/b/3iAsH)

## More from DevOpsDynamo

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--a9941213a65a---------------------------------------)