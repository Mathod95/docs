---
title: Two Kubernetes Scenarios That Quietly Decide Whether You Pass the CKA
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://medium.com/@DynamoDevOps/two-kubernetes-scenarios-that-quietly-decide-whether-you-pass-the-cka-ca468bcc434f
author:
  - "[[DevOpsDynamo]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

==If you’re not a Medium member, read this story for free,== ==[**here**](https://medium.com/@DynamoDevOps/two-kubernetes-scenarios-that-quietly-decide-whether-you-pass-the-cka-ca468bcc434f?sk=9c10d96959b329d119e90290c59be2fe)====.==

First of all, most people don’t fail the CKA because Kubernetes is too complex. They fail because their examination temperament doesn’t match the way the exam expects you to work. I’ve witnessed this phenomenon over and over. Candidates gain confidence after watching videos and following guided labs, but when the cluster no longer behaves as expected, they hesitate and lose confidence. The CKA exam is not a test of command memorization. It measures your understanding of Kubernetes fundamentals, specifically how Kubernetes behaves under failure scenarios, misconfigurations, and real-world pressure.

This is exactly why scenario-based Kubernetes practice is critical for the CKA exam. Forget polished demos and happy paths. The exam rewards your ability to detect subtle misconfigurations under time pressure.

At first glance, the scenarios below look simple. HPA and control plane recovery are topics everyone thinks they’ve covered. In reality, they’re where candidates hesitate, panic, or break things by fixing the wrong problem. If you can work through them calmly and in order, you’re already thinking the way the exam expects.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*OJqumJ90isttgbJ5Z9eC4w.png)

## Scenario 1: Configuring a Horizontal Pod Autoscaler (HPA)

**Domain:** Workloads and Scheduling (15%)

### Objective

Deploy a CPU-bound web application, expose it internally, and configure a Horizontal Pod Autoscaler with the following requirements:

- Minimum replicas: **1**
- Maximum replicas: **5**
- CPU utilization target: **50 percent**

Finally, simulate CPU load and confirm that autoscaling occurs.

### Context

HPA dynamically scales a deployment based on observed CPU or memory usage. In the CKA exam, HPA tasks fail most often because the application does not define CPU requests, Metrics Server is missing or not functioning, or the candidate does not sustain CPU load long enough for scaling to trigger. When scaling doesn’t happen immediately, many people assume something is broken and start changing random things. That’s usually where time gets burned.

### Always Remember

- CPU percentage in HPA calculations is based on resource requests, not limits.
- Metrics must be available or the HPA will remain in an Unknown state.
- Autoscaling decisions occur periodically. Scaling is not instant.

If you want to simulate this scenario, any Kubernetes environment works. You only need a working Metrics Server and the ability to run a busybox load generator pod.

**Step 1: Deploy the Application With CPU Requests**

File: `php-apache-deploy.yaml`

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-apache
spec:
  replicas: 1
  selector:
    matchLabels:
      app: php-apache
  template:
    metadata:
      labels:
        app: php-apache
    spec:
      containers:
        - name: php-apache
          image: k8s.gcr.io/hpa-example
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 200m
            limits:
              cpu: 500m
```

Apply it:

```c
kubectl apply -f php-apache-deploy.yaml
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*bFycYlTNcwb8_EhoR4dfQw.png)

**Step 2: Expose the Deployment**

```c
kubectl expose deployment php-apache \
  --port=80 \
  --target-port=80 \
  --name=web-app
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*WWwCdYh5CE9JB9v4Xx9YqQ.png)

Confirm:

```c
kubectl get svc web-app
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9ovzT4BQRPrKr-01N1drJw.png)

**Step 3: Verify That Metrics Server Is Installed**

```c
kubectl top pods
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*KgqsOqIgFmVsD0Mjj50ctw.png)

**Lab tip:** If you see “Metrics API not available”, deploy Metrics Server:

```c
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Wait a minute and test again:

```c
kubectl top pods
```

This step matters more than people realize. Creating an HPA before metrics are available almost always leads to confusion.

**Step 4: Create the HPA**

```c
kubectl autoscale deployment php-apache \
  --cpu-percent=50 \
  --min=1 \
  --max=5
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ykIJCfaF9eRrrNwtsAf5TA.png)

Check status:

```c
kubectl get hpa
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*MIS-FKf6uk8c974FL4oqoQ.png)

Expected output:

```c
php-apache   Deployment/php-apache   0% / 50%    1   5   1
```

At this point, nothing should scale yet. That’s normal.

**Step 5: Simulate CPU Load**

Start a load generator:

```c
kubectl run -i --tty load-generator --rm \
  --image=busybox \
  -- /bin/sh
```

Inside the shell:

```c
while true; do wget -q -O- http://web-app; done
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*oN1C7KTpn6xm8Y5GhIPnDw.png)

Keep this running for several minutes. HPA reacts to sustained load, not spikes.

**Step 6: Monitor the HPA Scaling Events**

```c
kubectl get hpa --watch
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Nob-hMu2yvOdHUREZdmj2Q.png)

Example output after load:

```c
php-apache   Deployment/php-apache   75% / 50%   1   5   3
```

When the load stops, replicas will slowly scale down.

**Explanation**

- `resources.requests.cpu` must exist or HPA cannot calculate percentages.
- TARGETS shows current usage versus target usage.
- Replicas increase when current usage is greater than target.
- Stable windows prevent rapid oscillation.

**Expected Outcome**

The deployment starts with one replica, scales up under CPU load, and scales down automatically when the load stops.

**Exam Tip:** If scaling does not occur, `kubectl describe hpa` almost always tells you why.

## Scenario 2: Debugging a Broken Control Plane Static Pod

**Domain:** Troubleshooting (30%)

### Objective

A control plane component, such as the kube-apiserver, is failing. Restore the service by fixing its static pod manifest in `/etc/kubernetes/manifests`.

This scenario tests discipline more than speed. The biggest mistake here is touching things that don’t need to be touched.

### What the Exam Requires

- You must edit the static pod file, not restart or delete the pod.
- Save and exit. The kubelet will recreate the container.
- Validate recovery using `kubectl get pods` and `kubectl get nodes`.

**Step 1: Confirm Control Plane Failure**

```c
kubectl get pods -n kube-system
```

One component will usually be in CrashLoopBackOff or missing.

Inspect logs if needed:

```c
kubectl logs kube-apiserver-$(hostname) -n kube-system
```

The error usually points to a missing file, wrong flag, or invalid certificate.

**Step 2: Edit the Static Pod Manifest**

Static pods live here:

```c
ls /etc/kubernetes/manifests/
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rq7MK5Pmxz13604NkQk5qQ.png)

Open the failing manifest:

```c
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Cg-l7m8wYuuK9cMLA1rNxQ.png)

Change: — client-ca-file=/etc/kubernetes/pki/ca-BROKEN.crt

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*mQ7I8NJr89kvdOVAGxn2XA.png)

Fix the incorrect line, for example:

```c
--client-ca-file=/etc/kubernetes/pki/ca.crt
```

Save the file. No restart is needed. The kubelet detects the change automatically.

**Step 3: Validate Recovery**

```c
kubectl get pods -n kube-system
kubectl get nodes
```

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*uRH28HdsNyAD6ZzdEmPzQA.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*SMTxWZu4ab5G8n9y_Vgtqw.png)

Expected result:

- The component returns to Running
- The node shows Ready

### Optional Practice: Break and Fix It Yourself

For practice only, you can intentionally break the API server by changing a valid path to an invalid one, watch the pod fail, then restore the correct value and observe the recovery. Doing this once makes the behavior stick far better than reading about it.

### Explanation

Static pods are created from files in `/etc/kubernetes/manifests`. The kubelet watches this directory and restarts pods when files change. You never delete static pods. You fix the manifest.

### Expected Outcome

The control plane component is restored, no manual restart commands are used, and the cluster returns to a healthy Ready state.

**Exam Tip:** If a control plane pod is failing or missing, your first stop should always be `/etc/kubernetes/manifests`.

## How to Practice These Scenarios for Free

You don’t need paid labs to practice this properly. You can reproduce both scenarios on Killercoda using a real Kubernetes environment, without fees. The key is how you practice. Reproduce the failure intentionally, apply the minimal fix, validate using multiple signals, then reset and repeat. If you can do both scenarios calmly without referencing notes, you’re practicing at exam level.

## Final Thoughts

**CKA Exam Prep: 40% OFF This Weekend (Jan 17–18 Only)**

Passing the **Certified Kubernetes Administrator (CKA)** exam is not about knowing more Kubernetes features. It’s about knowing **where to look first, what to ignore, and what not to touch** when things break.

That’s exactly what the **Conquer CKA Exam** book teaches.

The scenarios come from **real failure patterns**, not polished demo setups. These are the same issues that repeatedly show up in the CKA exam.

This weekend only (**January 17–18**), the full book is **40% OFF**.

**Get the full book (40% OFF):**

- [https://payhip.com/b/3iAsH](https://payhip.com/b/3iAsH)
- [https://devopsdynamo.gumroad.com/l/Conquer-cka-exam](https://devopsdynamo.gumroad.com/l/Conquer-cka-exam)

You can also start with the **free version** and see the approach before buying:

- [https://payhip.com/b/1HK5t](https://payhip.com/b/1HK5t)
- [https://devopsdynamo.gumroad.com/l/devopsdynamo](https://devopsdynamo.gumroad.com/l/devopsdynamo)

**How to actually prepare for the CKA**

- Read a scenario
- Open a lab
- Break something
- Fix it cleanly
- Repeat

You can practice for free on **Killercoda**.  
If you can afford it and want a more structured setup, run these scenarios on **KodeKloud labs**.

Repetition matters more than any resource. When troubleshooting feels boring and mechanical, you’re ready for the exam.

📘 Conquer the CKA Exam 🔥 40% OFF with JANUARY26 (valid January 17–18 only) Gumroad: [devopsdynamo.gumroad.com/l/Conquer-cka-exam](http://devopsdynamo.gumroad.com/l/Conquer-cka-exam) Payhip: [payhip.com/b/3iAsH](http://payhip.com/b/3iAsH)