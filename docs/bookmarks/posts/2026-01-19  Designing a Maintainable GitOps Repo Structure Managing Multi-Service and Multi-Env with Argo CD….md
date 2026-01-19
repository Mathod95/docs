---
title: "Designing a Maintainable GitOps Repo Structure: Managing Multi-Service and Multi-Env with Argo CD…"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@zxc0905fghasd/designing-a-maintainable-gitops-repo-structure-managing-multi-service-and-multi-env-with-argo-cd-60692398bc75"
author:
  - "[[JosephCheng]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*WfKpsWXo40ChS31hVQeHmQ.png)

**From Namespace to ApplicationSet — a Clean, Trackable Setup with instance.yaml**

📘 This is Part 3 of the “Building a Real and Traceable GitOps Architecture” series.

👉 [Part 1: Why Argo CD Wasn’t Enough](https://medium.com/@zxc0905fghasd/why-argo-cd-wasnt-enough-real-gitops-pain-and-the-tools-that-fixed-it-53f705b9bcce)

👉 Part 2: [From Kro RGD to Full GitOps: How I Built a Clean Deployment Flow with Argo CD](https://medium.com/@zxc0905fghasd/how-kro-rgd-helped-me-clean-up-and-trace-my-gitops-deployments-91619b9beda9)

👉 Part 4: [GitOps Promotion with Kargo: Image Tag → Git Commit → Argo Sync](https://medium.com/@zxc0905fghasd/gitops-promotion-with-kargo-image-tag-git-commit-argo-sync-16ca3eec38d5)

👉 Part 5: Part 5: [Implementing a Modular Kargo Promotion Workflow: Extracting PromotionTask from Stage for Maintainability](https://medium.com/@zxc0905fghasd/implementing-a-modular-kargo-promotion-workflow-extracting-promotiontask-from-stage-for-long-term-1ed7dcb51b22)

👉 Part 6: [Designing a Maintainable GitOps Architecture: How I Scaled My Promotion Flow from a Simple Line to a System That Withstands Change](https://medium.com/@zxc0905fghasd/designing-a-maintainable-gitops-architecture-how-i-scaled-my-promotion-flow-from-a-simple-line-to-830320e6248f)

In Part 1, I explained why Argo CD wasn’t enough for my workflow. In Part 2, I shared how I used Kro to produce clean, declarative Deployments.  
In this post, I want to take a step back — because even with the right tools, your GitOps setup can still collapse if the **Git repo structure** isn’t well-designed.  
Here’s how I organize my repo using ApplicationSet to manage multiple environments and services in a clean, scalable, and maintainable way.

## 🧨 When My GitOps Repo Became a Mess

At first, I managed all the YAML manifests manually. We only had a few services, so I thought it was fine — until it wasn’t.

YAMLs were added to the root directory. Someone created a `deploy-prod/` folder. Someone else copied dev manifests into production and made changes directly.

There were no naming conventions or directory rules. Every change started with the same question:

> *“Wait… which file are we actually deploying?”*

One day, a small update accidentally got deployed to two environments at once. I spent the entire afternoon rolling back.  
That’s when I realized I needed a Git structure that could survive real-world GitOps.

## ⚙️ My Setup and What I Wanted to Achieve

This setup runs on a self-managed MicroK8s cluster, and integrates:

- **Kro**: to render clean Deployments, Services, and ConfigMaps
- **Argo CD**: to sync manifests from Git into the cluster
- **Kargo**: to promote image updates into Git commits

I had three goals:

- Clearly separate development and production environments
- Allow each service to update independently
- Make every deployment traceable to a Git commit

## 📦 Why I Switched to Argo CD ApplicationSet

Originally, I created every Argo CD Application manually. It worked — but as the number of services grew, so did the pain:

- I had to open the UI and duplicate settings every time
- A single typo could break an entire sync
- There was no consistent pattern to follow

Then I switched to **ApplicationSet**. Everything became more consistent and maintainable:

- One ApplicationSet per namespace
- Automatically generate Applications based on folder structure
- Use annotations to link each service to the correct Kargo Stage

This brought three major benefits:

1. I no longer needed to create Applications manually
2. I could pair `instance.yaml` + Kro for automatic deployment
3. I could bind each service to its promotion logic via annotation (more on this in Part 4)

## 🗂 How I Structure My Git Repo

Here’s the directory layout I use in the repo:

```c
project/
├── argo-applications/
│   ├── develop-applicationset.yaml
│   └── production-applicationset.yaml
├── develop/
│   ├── frontend/
│   │   └── instance.yaml
│   └── backend/
│       └── instance.yaml
└── production/
    └── frontend/
        └── instance.yaml
```
- `argo-applications/`: holds one ApplicationSet config per environment
- `develop/` and `production/`: each service has its own folder with `instance.yaml`
- ❗ The ResourceGraphDefinition (RGD) isn’t checked into Git — it’s managed on the platform side

This structure makes it easy to map services, environments, and deployments — and keeps everything traceable.

## ✍️ A Real ApplicationSet Example

Here’s my actual `develop-applicationset.yaml`:

```c
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: develop-applicationset
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: https://gitlab.com/your-name/your-repo.git
        revision: HEAD
        directories:
          - path: develop/*
  template:
    metadata:
      name: '{{path.basename}}-dev-app'
      annotations:
        kargo.akuity.io/authorized-stage: develop:{{path.basename}}-dev-stage
    spec:
      project: develop
      source:
        repoURL: https://gitlab.com/your-name/your-repo.git
        targetRevision: HEAD
        path: '{{path}}'
        directory:
          recurse: true
      destination:
        server: https://kubernetes.default.svc
        namespace: develop
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

With this setup, if I add a folder like `develop/backend/`, a new Argo Application called `backend-dev-app` is automatically generated.  
The annotation also links it directly to the correct Kargo Stage — zero manual setup required.

## 🌳 How I Handle the Root App

I don’t store the root App in Git.

Instead, I create it once manually in the Argo CD UI. Its only job is to point to the `argo-applications/` directory and sync all the ApplicationSets inside.

This gives the UI a single, stable entry point that reflects what’s in Git — easy to reason about and maintain.

## 🧼 Keeping Environments and Services Isolated

Each Kubernetes namespace maps to:

- One Argo CD Project
- One ApplicationSet
- One Kargo Project

Every `instance.yaml` lives in an environment-specific path.  
The RGD is shared, but each environment has its own values — so `develop` and `production` stay completely isolated.

## 🛠 How This Structure Helps My Day-to-Day

This repo layout doesn’t just keep things “clean” — it makes my daily workflow smoother:

- Need to check a config? Open the service’s folder
- Want to see what changed in a deployment? Run `git log` on the `instance.yaml`
- Adding a new service? Just create a folder and add an `instance.yaml` — that’s it

While I currently maintain most YAML myself, this structure sets a clear standard for future collaboration and handoff.  
It builds a shared deployment language that’s easy to extend and hard to mess up.

## ✅ Why instance.yaml Is My Single Source of Truth

Every service’s `instance.yaml` is:

- Managed in Git
- Synced automatically via Argo CD
- Updated by Kargo through `yaml-update`

In other words: **when this file changes, the deployment changes.**  
No more digging into multiple manifests or chasing sync bugs — one file drives the entire state.

That’s how I define control in a GitOps setup.

## 🧱 This Structure Is the Foundation for Promotion

At first glance, this post might look like it’s just about organizing folders and automating Argo CD.

But in reality, this structure is what makes the **entire promotion flow possible**.

Here’s how Kargo works:  
→ Detect a new image tag  
→ Create a Freight  
→ Update the `instance.yaml`  
→ Argo CD syncs the commit  
→ Kro applies the Deployment

If file paths, annotations, or Application names aren’t consistent, Kargo has no idea what to promote.  
That’s why the Git structure *is* the foundation of a scalable, traceable GitOps workflow.

## 🔜 Coming Up Next: Promotion with Kargo

With this repo structure in place, I now have:

- Clean, declarative Deployments from Kro
- Automated syncing from Argo CD
- Scalable Application generation via ApplicationSet

But we’re just getting started.

In the next post, I’ll cover:

- How promotion flows from image tag → Freight → instance.yaml → Argo CD → Kro
- How each service links to its own Kargo Stage
- How ApplicationSet annotations enable precise targeting and sync

If you’re designing a GitOps setup or juggling multiple environments and services, I hope this post gives you a solid reference.  
If it helped you, feel free to share it or follow the series — Part 4 is coming soon. And if you’ve built something similar, I’d love to hear how it went.

I write what I build — GitOps, Kubernetes, MLOps, and everything in between. Say hi or reach out: [joseph.mycena@gmail.com](https://medium.com/@zxc0905fghasd/)

## More from JosephCheng

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--60692398bc75---------------------------------------)