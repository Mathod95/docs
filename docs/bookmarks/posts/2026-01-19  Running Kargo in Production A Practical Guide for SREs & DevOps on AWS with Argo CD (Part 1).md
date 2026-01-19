---
title: "Running Kargo in Production: A Practical Guide for SREs & DevOps on AWS with Argo CD (Part 1)"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@DynamoDevOps/running-kargo-in-production-a-practical-guide-for-sres-devops-on-aws-with-argo-cd-part-1-95ba77ec30a3"
author:
  - "[[DevOpsDynamo]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

When deploying and managing applications across dev, staging, and production, manual promotion workflows endanger you and slow things down. Meet **Kargo**, a GitOps design tool that goes beyond Argo CD by automating the promotions between your environment. It allows you to do this through automated, safe, auditable promotions using your existing Git repositories.

This guide leads you through running Kargo in AWS, along with Argo CD, with actual configuration examples adapted for SREs and DevOps teams.

==👉 if you’re not a Medium member, read this story for free,== ==[here](https://medium.com/@DynamoDevOps/running-kargo-in-production-a-practical-guide-for-sres-devops-on-aws-with-argo-cd-part-1-95ba77ec30a3?sk=ed923de1223644cfb8488f201a7c0b64)====.==

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*o5_1x1Gjm0LSJ9vq)

## Setting Up Kargo on AWS (Installation & Infrastructure)

- **Co-locate with Argo CD**: Install Kargo in the same EKS cluster as Argo CD. The Helm Chart from Akuity can be used to deploy in a separate `kargo` namespace.
- **Cluster Layout**: Use separate EKS clusters or namespaces for prod and non-prod. Centralize Argo CD to manage multiple clusters if needed.
- **Authentication & Permissions**: Use IRSA to assign Kargo the least IAM permissions required to access ECR. Safely store Git credentials in Kubernetes secrets.
- **Secure Exposure**: Kargo’s UI should be exposed behind an authenticated ALB Ingress or VPN. Enforce RBAC, and integrate with OIDC for authentication.

Example Helm install command:

```c
helm repo add akuity https://helm.akuity.io
helm install kargo akuity/kargo -n kargo --create-namespace
```

## GitOps Repository Structure

Your Git structure should cleanly separate environment-specific configurations:

**Option 1: Kustomize layout**

```c
myapp/
  base/
  overlays/
    dev/
    staging/
    prod/
```

**Option 2: Helm layout**

```c
myapp/
  charts/
  values/
    dev.yaml
    staging.yaml
    prod.yaml
```

**Mono-repo vs Multi-repo**: Kargo works with both. Mono-repo offers simplicity; multi-repo provides stronger access control. Use Warehouse path filters to scope triggers.

## Argo CD Applications Configuration

Each environment must have its own Argo CD Application.

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-dev
  namespace: argocd
  annotations:
    kargo.akuity.io/authorized-stage: "myteam:dev"
spec:
  destination:
    server: https://<cluster-api>
    namespace: myapp-dev
  source:
    repoURL: https://github.com/example/myapp-gitops.git
    targetRevision: env/dev
    path: .
  project: default
```

Add the Kargo annotation to let a specific Stage manage that Application. This prevents unauthorized stage-to-app interaction.## [Master Argo CD Access: A Smart DevOps Guide to Secure, Scalable CI/CD](https://medium.com/@DynamoDevOps/master-argo-cd-access-a-smart-devops-guide-to-secure-scalable-ci-cd-b6cc41e3c014?source=post_page-----95ba77ec30a3---------------------------------------)

Tags: Argo CD, Kubernetes DevOps, CI/CD Security, Role-Based Access Control, SSO Integration, GitOps, YAML Automation…

medium.com

[View original](https://medium.com/@DynamoDevOps/master-argo-cd-access-a-smart-devops-guide-to-secure-scalable-ci-cd-b6cc41e3c014?source=post_page-----95ba77ec30a3---------------------------------------)## [🚀 8 FREE DevOps Labs That’ll Actually Make You Better — Not Just Busy](https://medium.com/@DynamoDevOps/8-free-devops-labs-thatll-actually-make-you-better-not-just-busy-8db4ae616a05?source=post_page-----95ba77ec30a3---------------------------------------)

When attempting to get into DevOps or enhance what you already have, free or low-cost alternatives are as good as the…

medium.com

[View original](https://medium.com/@DynamoDevOps/8-free-devops-labs-thatll-actually-make-you-better-not-just-busy-8db4ae616a05?source=post_page-----95ba77ec30a3---------------------------------------)## [Karpenter in Production: Best Practices for Cost-Effective, Scalable Kubernetes](https://medium.com/@DynamoDevOps/karpenter-in-production-best-practices-for-cost-effective-scalable-kubernetes-775cca255037?source=post_page-----95ba77ec30a3---------------------------------------)

Karpenter has gathered full speed and is one of the most choice for dynamic node provisioning in Kubernetes. Designed…

medium.com

[View original](https://medium.com/@DynamoDevOps/karpenter-in-production-best-practices-for-cost-effective-scalable-kubernetes-775cca255037?source=post_page-----95ba77ec30a3---------------------------------------)

## Warehouses and Stages in Kargo

- **Warehouse**: Watches artifact sources like Git repos or ECR. Detects new versions and generates Freight.
- **Stage**: Represents each environment (dev, staging, prod). Accepts Freight from Warehouses or upstream Stages.

Example:

```c
apiVersion: kargo.akuity.io/v1alpha1
kind: Stage
metadata:
  name: dev
  namespace: myteam
spec:
  requestedFreight:
  - origin:
      kind: Warehouse
      name: myapp-warehouse
    sources:
      direct: true
  promotionTemplate:
    spec:
      steps:
      - kustomizeSetImage:
          image: myapp
          newTag: '{{ .freight.version }}'
```

This sets up automatic detection and promotion of new images to your dev environment.

## What’s Next

In **Part 2**, we’ll walk through:

- How Kargo automates end-to-end promotion workflows
- Integrating verification and testing before promotion
- Scaling Kargo across teams and environments
- Locking down access and securing your GitOps pipeline

Stay tuned for the follow-up that turns this foundation into a production-grade promotion engine.

Enjoyed this? Hit that clap button, subscribe, and follow for sharp insights on Cloud, DevOps, DevSecOps, and AI.## [I Passed the CKA and Created a Free Kubernetes Lab Book With 20+ Exam-Style Scenarios](https://medium.com/@DynamoDevOps/i-passed-the-cka-and-created-a-free-kubernetes-lab-book-with-20-exam-style-scenarios-93277a14dd62?source=post_page-----95ba77ec30a3---------------------------------------)

🆓 Not a Medium member? You can still read this full story for free — no paywall, no catch. 👉 Click here to access it…

medium.com

[View original](https://medium.com/@DynamoDevOps/i-passed-the-cka-and-created-a-free-kubernetes-lab-book-with-20-exam-style-scenarios-93277a14dd62?source=post_page-----95ba77ec30a3---------------------------------------)## [What is Trivy and Why DevSecOps Teams Can’t Miss out on It](https://medium.com/@DynamoDevOps/what-is-trivy-and-why-devsecops-teams-cant-miss-out-on-it-448546e3a6e3?source=post_page-----95ba77ec30a3---------------------------------------)

The open-source scanner that is transforming shift-left security

medium.com

[View original](https://medium.com/@DynamoDevOps/what-is-trivy-and-why-devsecops-teams-cant-miss-out-on-it-448546e3a6e3?source=post_page-----95ba77ec30a3---------------------------------------)

📘 Conquer the CKA Exam 🔥 40% OFF with JANUARY26 (valid January 17–18 only) Gumroad: [devopsdynamo.gumroad.com/l/Conquer-cka-exam](http://devopsdynamo.gumroad.com/l/Conquer-cka-exam) Payhip: [payhip.com/b/3iAsH](http://payhip.com/b/3iAsH)