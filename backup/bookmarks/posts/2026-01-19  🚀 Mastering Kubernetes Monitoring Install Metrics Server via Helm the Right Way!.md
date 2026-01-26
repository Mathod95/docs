---
title: "🚀 Mastering Kubernetes Monitoring: Install Metrics Server via Helm the Right Way!"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@mahernaija/mastering-kubernetes-monitoring-install-metrics-server-via-helm-the-right-way-058586744db9"
author:
  - "[[Mahernaija]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

A **complete step-by-step guide** to install and troubleshoot Metrics Server on Kubernetes using Helm — perfect for EKS, GKE, Minikube & Kubeadm clusters! 💡

## 👋 Introduction

Metrics Server is the **heartbeat of Kubernetes performance monitoring** 🫀. Whether you’re tuning autoscaling or simply checking node usage, it’s an essential component. However, Helm installation can get tricky if syntax or flags are off.

In this guide, you’ll learn how to:

✅ Add the Helm repo  
✅ Install Metrics Server correctly (with `--kubelet-insecure-tls`)  
✅ Verify the setup  
✅ Use a custom `values.yaml` for better flexibility  
Let’s dive in! 🏊♂️✨

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*BKpxTOV2w2XXejy6)

## 🧩 Step 1: Add the Metrics Server Helm Repository

```c
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
```

📌 *This adds and refreshes the repo so you can access the latest Metrics Server chart.*

## 📦 Step 2: Install Metrics Server via Helm

```c
helm install metrics-server metrics-server/metrics-server \
  --namespace kube-system \
  --set "args={--kubelet-insecure-tls,--kubelet-preferred-address-types=InternalIP}"
```

💡 *Why this matters:*  
Many clusters (like Minikube or bare-metal) need `--kubelet-insecure-tls` or they’ll **fail TLS verification** 🔒.

## 🔎 Step 3: Verify Your Installation

Check pod status:

```c
kubectl get pods -n kube-system -l "app.kubernetes.io/name=metrics-server"
```

Check metrics API:

```c
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/nodes"

{"kind":"NodeMetricsList","apiVersion":"metrics.k8s.io/v1beta1","metadata":{},"items":[{"metadata":{"name":"kube1","creationTimestamp":"2025-05-21T10:56:12Z","labels":{"beta.kubernetes.io/arch":"amd64","beta.kubernetes.io/os":"linux","kubernetes.io/arch":"amd64","kubernetes.io/hostname":"kube1","kubernetes.io/os":"linux","node-role.kubernetes.io/control-plane":"","node.kubernetes.io/exclude-from-external-load-balancers":""}},"timestamp":"2025-05-21T10:55:59Z","window":"20.039s","usage":{"cpu":"210243026n","memory":"3123988Ki"}}]}
```

✅ You should see a JSON output with node stats.  
❌ If not, run:

```c
kubectl describe pod <metrics-server-pod-name> -n kube-system
```

## ⚙️ Step 4: (Optional but Recommended) Use a Custom values.yaml

📄 Create `values.yaml`:

```c
args:
  - --kubelet-insecure-tls
  - --kubelet-preferred-address-types=InternalIP
```

Install using:

```c
helm install metrics-server metrics-server/metrics-server \
  --namespace kube-system -f values.yaml
```

✨ *Bonus:* You can add options like `nodeSelector`, `affinity`, or `tolerations` here for advanced scheduling.

## ✅ Conclusion

Installing Metrics Server might seem like a small step, but it’s **crucial for autoscaling and performance visibility** 🚀.  
Using the **right Helm syntax** or a clean `values.yaml` file can save you from cryptic errors and hours of debugging ⏱️.

👉 Now your Kubernetes cluster is ready to **report accurate metrics like a pro!**

## 🚀 Stay Ahead with BenchHub.co

Want to dive deeper into the tools that power today’s tech stacks?  
At [**BenchHub**](https://www.benchhub.co/)**.co**, we’re constantly benchmarking the latest DevOps, ML, and Cloud-native tools — so you don’t have to.

Don’t get left behind — **subscribe now** and supercharge your tech decisions with data that matters.## [Empowering Smarter Tech & AI Decisions: Benchmarks,Insigths](https://www.benchhub.co/?source=post_page-----058586744db9---------------------------------------)

Explore BenchHub.co - your ultimate resource for comparing tech and AI solutions. Gain actionable insights, detailed…

www.benchhub.co

[View original](https://www.benchhub.co/?source=post_page-----058586744db9---------------------------------------)

👉 [Subscribe here](https://www.benchhub.co/) and join a community of builders, engineers, and decision-makers staying sharp in a fast-moving ecosystem.

🔍 **Why subscribe?**  
By joining our newsletter, you’ll get:

- 🧠 **Advanced tutorials** on real-world use cases
- 📊 **Unbiased benchmarks** of tools from the marketplace
- 🛠️ Expert insights to help you make smarter tech decisions
- ⚡ Early access to upcoming evaluations and performance reports

#Kubernetes #Helm #MetricsServer #DevOps #K8sMonitoring #Kubeadm #EKS #GKE #Minikube #ClusterMonitoring #KubernetesAutoscaling

## More from Mahernaija

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--058586744db9---------------------------------------)