---
title: "Disaster Recovery: Rebuilding a Kubernetes Environment in 10 Minutes with ArgoCD"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@alipolatbt/disaster-recovery-rebuilding-a-kubernetes-environment-in-10-minutes-with-argocd-a2ce4727f9f7"
author:
  - "[[aliplt]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Hello friends. We experienced earthquake disasters in my country and this brought up the subject of Disaster Recovery. Not only earthquakes but also an admin error may require DR. In this article, I will talk about how even if you completely lose your Kubernetes infrastructure, if you have a Git repository where you code all resources such as application, service, configmap, ingress, you can get the entire system back on its feet in minutes with ArgoCD’s GitOps approaches.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*y9qqY51KlfekkoJ9.png)

**1\. DR Approach with GitOps & ArgoCD**  
**GitOps:** Keeps Kubernetes manifests under version control in Git. Provides automatic synchronization between the real state of the environment and Git.

**ArgoCD:** A control plane deployed in a Kubernetes cluster; tracks manifest changes and synchronizes with the running environment in a pull-based manner.

In this way, in disaster recovery (DR) scenarios, it is sufficient to simply recreate the cluster.

**2\. DR Scenario: Cluster Deleted, What Do We Do?**  
Steps:  
**a) Create a new cluster**

> eksctl create cluster — name my-cluster

**b) Install ArgoCD**

> kubectl create ns argocd
> 
> kubectl apply -n argocd -f [https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml](https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml)

**c) Introduce the Git repo to ArgoCD**

> argocd login <ARGO\_SERVER>  
> argocd app create my-app \\  
> — repo [https://github.com/username/gitops-demo.git](https://github.com/username/gitops-demo.git) \\  
> — path k8s/ \\  
> — dest-server [https://kubernetes.default.svc](https://kubernetes.default.svc/) \\  
> — dest-namespace default \\  
> — sync-policy automated

**d) Start the sync process or wait for it to be automatic**

> argocd app sync my-app

Once these steps are completed, ArgoCD reads the manifests and performs the deploy operation, and everything is up and running automatically.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GXJyvhkCChZNHaL5K0PqgA.png)

Example Git Repo Structure

With these definitions, even if the cluster is destroyed, ArgoCD can recreate all resources by looking at the App CR in application.yaml.

**4\. Why GitOps in DR Plans?**

Speed: In classic DR methods, it can take hours to deploy with dashes; with GitOps, this process is reduced to seconds.

Traceability: It is clearly visible on Git who made all changes and when.

Repeatability: With defined processes, “system installation from scratch” can be done without errors.

Minimized human error: There is no need for classic “kubectl apply” errors; all manifests come from Git.

ArgoCD isn’t just a deployment tool — it’s also your disaster recovery solution. As long as your manifests are versioned, you can get your system back on track with just a few commands, even if your existing cluster is deleted.

Thanks!

## More from aliplt

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--a2ce4727f9f7---------------------------------------)