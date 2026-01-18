---
title: "Argo CD + GitOps: A Practical Guide to Safer Kubernetes Deployments"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://medium.com/@nitishjsr7209/argo-cd-gitops-a-practical-guide-to-safer-kubernetes-deployments-b1dd3e900e42
author:
  - "[[Nitish kumar]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Deploying applications to Kubernetes often starts simple — but as environments grow, so do the risks.

A common deployment pattern looks like this:

```c
CI Pipeline → Helm → Kubernetes
```

While functional, this approach introduces several problems:

- CI pipelines require **direct cluster access**
- No automatic drift detection
- Rollbacks depend on rerunning pipelines
- Deployment history is fragmented
- Production credentials live in CI systems

This is where **GitOps** — powered by **Argo CD** — becomes a game changer.

## What is Argo CD?

**Argo CD is a GitOps Continuous Delivery (CD) tool for Kubernetes.**

Its core principle is simple:

> ***The live Kubernetes cluster must always match what is defined in Git.***
> 
> Argo CD:

- Runs inside the Kubernetes cluster
- Continuously compares **Git vs live state**
- Automatically synchronizes differences
- Detects and self-heals configuration drift

Git becomes the **single source of truth**.

## What Argo CD Is (and Is Not)

**Argo CD is:**

- A Kubernetes-native CD system
- Declarative and Git-driven
- Automated and auditable

**Argo CD is NOT:**

- A CI tool
- A Docker image builder
- A test runner
- A replacement for Terraform

CI and CD remain clearly separated.

## CI vs CD: Clear Separation of Responsibilities

## Continuous Integration (CI)

- Build Docker images
- Push images to a container registry
- Generate immutable image tags
- Update Helm values in Git

## Continuous Delivery (CD) — Argo CD

- Watch Helm chart repositories
- Read image versions from Git
- Deploy to Kubernetes
- Detect and heal drift automatically

This separation is the foundation of GitOps.

## Why Move Away from Pipeline-Driven Deployments?

## Traditional approach

```c
CI Pipeline → Helm → Kubernetes
```

**Limitations:**

- CI requires cluster-admin permissions
- No automatic drift correction
- Rollbacks are manual and error-prone
- Poor auditability
- High security risk in production

## GitOps approach with Argo CD

```c
CI Pipeline → Git → Argo CD → Kubernetes
```

**Advantages:**

- CI never accesses the cluster
- Git history = deployment history
- Rollbacks via `git revert`
- Continuous drift detection
- Strong security boundaries

## Repository Structure (Best Practice)

## Application Code Repository

```c
app-service/
├── src/
├── Dockerfile
├── ci-pipeline.yml
```

Purpose:

- Application source code
- Build and push container images

\_No Helm charts  
*No Kubernetes manifests*

## Helm Charts Repository

```c
helm-charts/
├── app-service/
│   ├── Chart.yaml
│   ├── templates/
│   │   └── deployment.yaml
│   ├── values-staging.yaml
│   └── values-prod.yaml
```

Purpose:

- Desired Kubernetes state
- Watched by Argo CD

## Helm Chart Requirements for GitOps

Helm charts must be **image-tag driven**.

**values-staging.yaml**

```c
image:
  repository: registry.example.com/app-service
  tag: app-service-123
```

**deployment.yaml**

```c
image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

**Best practices:**

- Never hardcode image tags
- Never use `latest`

## What Changes in the CI Pipeline?

## Remove:

- Helm deployment steps
- `--set image.tag=...`
- Kubernetes cluster credentials

## Add:

CI updates the Helm values file instead:

```c
- bash: |
    set -e

    echo "Cloning Helm charts repo"
    git clone @dev.azure.com/YOUR_ORG/DevOps/_git/helm-charts">https://$(System.AccessToken)@dev.azure.com/YOUR_ORG/DevOps/_git/helm-charts
    cd helm-charts/$(chartName)

    echo "Updating image tag in values-staging.yaml"
    yq -i '.image.tag = "$(tag)"' values-staging.yaml

    git config user.email "ci@devops.com"
    git config user.name "azure-devops-ci"

    git commit -am "chore(staging): update agent-neo image to $(tag)"
    git push origin main
  displayName: Update Helm values repo
```

This **Git commit becomes the deployment trigger**.

## How Argo CD Knows What to Deploy

1. CI builds and pushes a new image
2. CI updates the Helm values file
3. A Git commit is created
4. Argo CD detects the change
5. Argo CD deploys automatically

Argo CD never guesses versions — **Git explicitly defines them**.

## The Argo CD Application Object

Argo CD deploys applications using an `Application` custom resource:

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-service-staging
  namespace: argocd
spec:
  source:
    repoURL: https://git.example.com/helm-charts
    path: app-service
    helm:
      valueFiles:
        - values-staging.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

This can be created using:

- Argo CD UI
- YAML (`kubectl apply`)

Both approaches are equivalent.

## Rollbacks Become Simple

```c
git revert <commit>
git push
```

Argo CD detects the change and rolls back automatically — no pipeline reruns required.

## Security and Permissions Model

**CI Pipeline**

- Pushes images
- Pushes Git commits
- No Kubernetes access

**Argo CD**

- Uses Kubernetes RBAC
- Runs inside the cluster
- No cloud credentials required

This dramatically reduces the blast radius.

#GitOps #ArgoCD #Kubernetes #DevOps #CloudNative

## More from Nitish kumar

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--b1dd3e900e42---------------------------------------)