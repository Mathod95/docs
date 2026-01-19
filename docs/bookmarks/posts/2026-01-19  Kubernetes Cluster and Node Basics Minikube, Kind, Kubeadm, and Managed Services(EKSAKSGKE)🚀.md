---
title: "Kubernetes Cluster and Node Basics: Minikube, Kind, Kubeadm, and Managed Services(EKS/AKS/GKE)🚀"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@subhampradhan966/kubernetes-cluster-and-node-basics-minikube-kind-kubeadm-and-managed-services-eks-aks-gke-92de81623d5d"
author:
  - "[[Subham Pradhan]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0Xtajh51ys1XMEOIGmafEQ.png)

Think of Kubernetes as the **orchestra conductor** for your applications. It manages where, when, and how your apps (containers) run.

## What Is Kubernetes?## [What Is Kubernetes?](https://medium.com/@subhampradhan966/what-is-kubernetes-17fa64f7dcfb?source=post_page-----92de81623d5d---------------------------------------)

### [“Before transitioning to Kubernetes, let’s understand why it was necessary.”](https://medium.com/@subhampradhan966/what-is-kubernetes-17fa64f7dcfb?source=post_page-----92de81623d5d---------------------------------------)

[

medium.com

](https://medium.com/@subhampradhan966/what-is-kubernetes-17fa64f7dcfb?source=post_page-----92de81623d5d---------------------------------------)

## Kubernetes Architecture:## [𝐊𝐮𝐛𝐞𝐫𝐧𝐞𝐭𝐞𝐬(K8S) 𝐀𝐫𝐜𝐡𝐢𝐭𝐞𝐜𝐭𝐮𝐫𝐞](https://medium.com/@subhampradhan966/k8s-f9939fc51e51?source=post_page-----92de81623d5d---------------------------------------)

☸️ 𝐊𝐮𝐛𝐞𝐫𝐧𝐞𝐭𝐞𝐬 𝐀𝐫𝐜𝐡𝐢𝐭𝐞𝐜𝐭𝐮𝐫𝐞: 𝐊𝐞𝐲 𝐂𝐨𝐦𝐩𝐨𝐧𝐞𝐧𝐭𝐬 ☸️ Kubernetes, the leading container…

medium.com

[View original](https://medium.com/@subhampradhan966/k8s-f9939fc51e51?source=post_page-----92de81623d5d---------------------------------------)

## 🏗️ What is a Cluster?

🧠 **Layman’s analogy:**  
Imagine a **team of computers working together** as one big system — that’s a **Kubernetes cluster**.

💡 **Technical meaning:**  
A **Kubernetes cluster** is a **group of nodes (machines)** managed by Kubernetes where your applications run.

- It has one **Master (Control Plane)** that gives instructions.
- It has one or more **Workers (Nodes)** that follow the instructions and run your apps.

## 🧱 What is a Node?

🧠 **Layman’s analogy:**  
A **node** is like a **worker** in a factory. Each worker (node) has the tools (CPU, memory, etc.) to do its job — which is running apps (containers).

💡 **Technical meaning:**  
A **node** is a **single machine (virtual or physical)** in the Kubernetes cluster. It runs the actual **pods** (which contain your app containers).

There are 2 types of nodes:

- 🧠 **Master Node** (Control Plane): The brain — decides what runs where.
- 💪 **Worker Node**: The muscle — runs your applications (pods).

## 🔄 Putting It All Together:

Term Layman Explanation Technical Role **Cluster** A team of machines working together A group of nodes managed by Kubernetes **Node** A worker machine that does the actual work A physical or virtual machine that runs pods **Master Node** The team leader giving instructions Controls the cluster, schedules pods **Worker Node** The team members doing the work Executes pods and runs containers

## 🖼️ Real-Life Example:

You’re running a food delivery app like Swiggy.

- **Cluster** = The entire system managing the app (control + workers)
- **Master Node** = The manager who decides how many delivery agents (pods) are needed
- **Worker Node** = The delivery agents who actually deliver the food (run your app)

## 🧱 Types of Kubernetes Clusters You Can Deploy

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*KFZoGL7PIZrm81fzNKjl_g.png)

## 🔧 Quick Use Cases

- **✅ Minikube**: “I want to learn Kubernetes and test things on my laptop.”
- **✅ Kind**: “I need to test Kubernetes resources in CI pipelines or develop locally using Docker.”
- **✅ Kubeadm:** “I want full control to build my own Kubernetes cluster manually (on-prem or VM).”
- **✅ EKS / AKS / GKE:** “I need a scalable, secure, and managed Kubernetes cluster in AWS for production workloads.”

## 1\. Setup Kubernetes kubectl and Minikube on Ubuntu 22.04 LTS:## [Setup Kubernetes kubectl and Minikube on Ubuntu 22.04 LTS](https://medium.com/@subhampradhan966/setup-kubernetes-kubectl-and-minikube-on-ubuntu-22-04-lts-ca9e39c35d8a?source=post_page-----92de81623d5d---------------------------------------)

Kubernetes has become the go-to container orchestration platform for deploying, managing, and scaling containerized…

medium.com

[View original](https://medium.com/@subhampradhan966/setup-kubernetes-kubectl-and-minikube-on-ubuntu-22-04-lts-ca9e39c35d8a?source=post_page-----92de81623d5d---------------------------------------)

## 2\. Setting Up a Multi-Node Kubernetes Cluster with Kind## [Setting Up a Multi-Node Kubernetes Cluster with Kind: A Comprehensive Guide](https://medium.com/@subhampradhan966/setting-up-a-multi-node-kubernetes-cluster-with-kind-a-comprehensive-guide-146ee5994226?source=post_page-----92de81623d5d---------------------------------------)

Introduction

medium.com

[View original](https://medium.com/@subhampradhan966/setting-up-a-multi-node-kubernetes-cluster-with-kind-a-comprehensive-guide-146ee5994226?source=post_page-----92de81623d5d---------------------------------------)

## 3\. Kubeadm Setup for Ubuntu 24.04 LTS## [Kubeadm Setup for Ubuntu 24.04 LTS](https://medium.com/@subhampradhan966/kubeadm-setup-for-ubuntu-24-04-lts-f6a5fc67f0df?source=post_page-----92de81623d5d---------------------------------------)

Demystifying Kubernetes Architecture:

medium.com

[View original](https://medium.com/@subhampradhan966/kubeadm-setup-for-ubuntu-24-04-lts-f6a5fc67f0df?source=post_page-----92de81623d5d---------------------------------------)

## 4\. EKS Cluster Setup:## [EKS Cluster Creation on Windows: Deploying Kubernetes Locally](https://medium.com/@subhampradhan966/eks-cluster-creation-on-windows-deploying-kubernetes-locally-13a44b75c9e2?source=post_page-----92de81623d5d---------------------------------------)

Introduction:

medium.com

[View original](https://medium.com/@subhampradhan966/eks-cluster-creation-on-windows-deploying-kubernetes-locally-13a44b75c9e2?source=post_page-----92de81623d5d---------------------------------------)

## 5\. Google Kubernetes Engine (GKE) Cluster Setup and Deployment Guide:## [Google Kubernetes Engine (GKE) Cluster Setup and Deployment Guide](https://medium.com/@subhampradhan966/google-kubernetes-engine-gke-cluster-setup-and-deployment-guide-ac6a832eac75?source=post_page-----92de81623d5d---------------------------------------)

In this guide, we will walk you through the process of creating a Google Kubernetes Engine (GKE) Standard Cluster…

medium.com

[View original](https://medium.com/@subhampradhan966/google-kubernetes-engine-gke-cluster-setup-and-deployment-guide-ac6a832eac75?source=post_page-----92de81623d5d---------------------------------------)

**Hope you found this helpful!**

If you have any related queries, feel free to reach out. I’d be happy to assist if I can. Stay connected! 🙂

If you enjoyed this post, a clap would be greatly appreciated.

**GitHub**: [https://github.com/Subham966/](https://github.com/Subham966/)  
**LinkedIn**: https:// [www.linkedin.com/in/subham-pradhan-31613a1a4](https://www.linkedin.com/in/subham-pradhan-31613a1a4/)

Happy automating and deploying! 🚀

DevOps Engineer | CI/CD | K8S | Docker | Jenkins | Ansible | Git | Terraform | ArgoCD |Helm|Prometheus|Grafana|SonarQube|Trivy|Azure| Data Engineer| DevSecOps |

## More from Subham Pradhan

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--92de81623d5d---------------------------------------)