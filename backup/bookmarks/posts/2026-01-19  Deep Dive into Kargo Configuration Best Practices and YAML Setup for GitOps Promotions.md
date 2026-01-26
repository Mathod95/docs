---
title: "Deep Dive into Kargo Configuration: Best Practices and YAML Setup for GitOps Promotions"
date: 2026-01-19
categories:
  - Kargo
tags:
  - Kargo
source: "https://medium.com/@DynamoDevOps/deep-dive-into-kargo-configuration-best-practices-and-yaml-setup-for-gitops-promotions-b8afce83811a"
author:
  - "[[DevOpsDynamo]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

This is our **Kargo** GitOps series’ third chapter with a focus on the best practices of Kargo configuration. Whether you use **Argo CD** in an **AWS** deployment or in a **GitOps based CI/CD pipeline**, this article takes you through the process of how to structure your Kargo YAML configuration, make it scalable, and at the same time, align it with the production-grade reliability and security. There will be the use of real-world examples and production patterns to help you in your implementation.

==👉 if you’re not a Medium member, read this story for free,== ==[here](https://medium.com/@DynamoDevOps/deep-dive-into-kargo-configuration-best-practices-and-yaml-setup-for-gitops-promotions-b8afce83811a?sk=8c9fbd3c3c8cc510c2189363519d224b)====.==

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*R6Opb9QO5NiBEZJs)

## Why Kargo Configuration Matters

From a fundamental standpoint, Kargo is a program that allows automated promotions through a GitOps process across environments. However, how you structure the components of your system -Warehouses, Stages, and PromotionTemplates- will determine how robust and maintainable the workflow can be.

## Core Kargo Resources Explained (YAML-Focused)

Let’s take a look at the principal CRDs of the Kargo ecosystem:

## 1\. Warehouse (Version Detection Engine)

Through a Warehouse, your application is informed about new versions of artifacts from the image registries or Git repositories which manage your application. It is advisable to use semantic versioning and a variety of filters to prevent noise from unstable builds.

### Example: Warehouse for Image Version Detection

```c
apiVersion: kargo.akuity.io/v1alpha1
kind: Warehouse
metadata:
  name: api-warehouse
  namespace: devops
spec:
  subscriptions:
    images:
    - repoURL: public.ecr.aws/myorg/api
      semverConstraint: ">=1.0.0"
```

## Best Practices:

- Use `semverConstraint` to avoid promoting `latest` tags
- Separate Warehouses by microservice for better isolation
- Monitor logs: misconfigured registries are silent failures

## 2\. Stage (Environment Logic)

A `Stage` defines how Kargo moves Freight (detected changes) into an environment like `dev`, `staging`, or `prod`. It includes **promotion rules** and **approval logic**.

### Example: Stage with GitOps Push and Argo CD Sync

```c
apiVersion: kargo.akuity.io/v1alpha1
kind: Stage
metadata:
  name: staging
  namespace: devops
spec:
  requestedFreight:
  - origin:
      kind: Warehouse
      name: api-warehouse
    sources:
      stages:
        - dev
  promotionTemplate:
    spec:
      steps:
      - kustomizeSetImage:
          image: api
          newTag: '{{ .freight.version }}'
      - gitCommit:
          commitMessage: "Promote API to {{ .freight.version }}"
      - gitPush: {}
      - argocdAppUpdate:
          appName: api-staging
```

## Best Practices:

- Always annotate Argo CD apps with `kargo.akuity.io/authorized-stage`
- Use Git PRs instead of direct pushes for prod when needed
- Include rollback strategies if applicable

## 3\. Promotion Approvals & Verification

The **manualPromotionApprovals** feature is employed for the production stages, and the validation logic via **Argo Rollouts** or **custom tests** is also enlisted.

### Example: Approval-Based Stage with Analysis Template

```c
apiVersion: kargo.akuity.io/v1alpha1
kind: Stage
metadata:
  name: prod
  namespace: devops
spec:
  manualPromotionApprovals: true
  requestedFreight:
  - origin:
      kind: Warehouse
      name: api-warehouse
    sources:
      stages:
        - staging
  promotionTemplate:
    spec:
      steps:
        - verify:
            analysisTemplate:
              name: rollout-smoke-test
        - kustomizeSetImage:
            image: api
            newTag: '{{ .freight.version }}'
        - gitCommit:
            commitMessage: "Release API {{ .freight.version }} to production"
        - gitPush: {}
        - argocdAppUpdate:
            appName: api-prod
```

## Best Practices:

- Use `verify` steps to prevent bad changes from reaching production
- Build a Slack or email notifier for manual approval waits
- Track which Freight versions are deployed where

## Git Repository Structure for Kargo

Keep Git repositories declarative, separated by environment, and audit-friendly.

## Recommended Layout with Kustomize

```c
my-app-gitops/
├── base/
├── overlays/
│   ├── dev/
│   ├── staging/
│   └── prod/
```

Each overlay will be pointed to by an Argo CD Application, which in turn Kargo promotes through.

## Security in GitOps:

- Lock branches (require PRs for `prod`)
- Use SealedSecrets for credentials
- Rotate Git tokens or deploy keys every 90 days## [Kargo GitOps Promotion Workflows, Scalability & Security](https://medium.com/@DynamoDevOps/kargo-gitops-promotion-workflows-scalability-security-37ebfb7fa9c8?source=post_page-----b8afce83811a---------------------------------------)

Having your plan in place and executing stages via Kargo, it is now time for you to start implementing the actual…

medium.com

[View original](https://medium.com/@DynamoDevOps/kargo-gitops-promotion-workflows-scalability-security-37ebfb7fa9c8?source=post_page-----b8afce83811a---------------------------------------)## [Running Kargo in Production: A Practical Guide for SREs & DevOps on AWS with Argo CD (Part 1)](https://medium.com/@DynamoDevOps/running-kargo-in-production-a-practical-guide-for-sres-devops-on-aws-with-argo-cd-part-1-95ba77ec30a3?source=post_page-----b8afce83811a---------------------------------------)

When deploying and managing applications across dev, staging, and production, manual promotion workflows endanger you…

medium.com

[View original](https://medium.com/@DynamoDevOps/running-kargo-in-production-a-practical-guide-for-sres-devops-on-aws-with-argo-cd-part-1-95ba77ec30a3?source=post_page-----b8afce83811a---------------------------------------)## [Master Argo CD Access: A Smart DevOps Guide to Secure, Scalable CI/CD](https://medium.com/@DynamoDevOps/master-argo-cd-access-a-smart-devops-guide-to-secure-scalable-ci-cd-b6cc41e3c014?source=post_page-----b8afce83811a---------------------------------------)

Tags: Argo CD, Kubernetes DevOps, CI/CD Security, Role-Based Access Control, SSO Integration, GitOps, YAML Automation…

medium.com

[View original](https://medium.com/@DynamoDevOps/master-argo-cd-access-a-smart-devops-guide-to-secure-scalable-ci-cd-b6cc41e3c014?source=post_page-----b8afce83811a---------------------------------------)

## Advanced Kargo Patterns

### Multi-Service Promotion

Use grouped Warehouses or shared stages for tightly-coupled apps.

### Event-Driven Promotions

Trigger external tools (e.g. Slack, PagerDuty) via webhook on promotion success.

### Failure Recovery

Enable automatic rollback or catch with Canary + AnalysisTemplate.

### Test Strategy

Embed test jobs or hooks in Stages:

```c
- verify:
    job:
      name: run-api-tests
      namespace: qa
```

## Security Best Practices Recap

- Use IRSA for AWS ECR/CodeCommit access
- Apply `NetworkPolicies` to restrict controller egress
- Validate all Freight with SCA or image scanning tools
- Use OIDC for audit-tracked user auth to Kargo UI

## Conclusion: Build with Confidence

Configuring Kargo properly is the key to building a **secure, scalable, and production-ready GitOps pipeline**. With clearly defined Warehouses, Stages, and PromotionTemplates, your CI/CD workflow becomes traceable, automated, and resilient.

By implementing the YAML examples and applying best practices from this guide, you’ll:

- Accelerate delivery across environments
- Reduce errors via controlled promotions
- Maintain full Git-based audit trails
- Stay in control of your production pipeline

Stay GitOps. Stay automated. Stay secure.

Enjoyed this? Hit that clap button, subscribe, and follow for sharp insights on Cloud, DevOps, DevSecOps, and AI.

📘 Conquer the CKA Exam 🔥 40% OFF with JANUARY26 (valid January 17–18 only) Gumroad: [devopsdynamo.gumroad.com/l/Conquer-cka-exam](http://devopsdynamo.gumroad.com/l/Conquer-cka-exam) Payhip: [payhip.com/b/3iAsH](http://payhip.com/b/3iAsH)