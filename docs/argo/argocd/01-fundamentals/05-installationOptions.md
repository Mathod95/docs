---
title: Installation Options
status: draft
sources:
  - https://notes.kodekloud.com/docs/GitOps-with-ArgoCD/ArgoCD-Basics/Installation-Options/page
  - https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/gitops-with-argocd/module/546d7ffa-8e6e-4197-9dff-443bb15dcdf6/lesson/36d1856a-8c10-4fb8-97f9-b3804847f5bf
---

> This article explores ArgoCD installation models, including core and multi-tenant options, along with installation commands and configurations for different environments.

Explore the various ArgoCD installation models to determine which best suits your deployment needs. ArgoCD can be installed in two primary modes: a core installation for single-tenant use and a multi-tenant installation for environments requiring isolated access for multiple teams.

## Core Installation

The Argo CD Core installation is primarily used to deploy Argo CD in headless mode. This type of installation is most suitable for cluster administrators who independently use Argo CD and don't need multi-tenancy features. This installation includes fewer components and is easier to setup. The bundle does not include the API server or UI, and installs the lightweight (non-HA) version of each component.

Installation manifest is available at [core-install.yaml](https://github.com/argoproj/argo-cd/blob/master/manifests/core-install.yaml).

For more details about Argo CD Core please refer to the [official documentation](https://argo-cd.readthedocs.io/en/stable/operator-manual/core/)

## Multi-Tenant Installation

Multi-tenant deployments are ideal for organizations with multiple application development teams, typically managed by a centralized platform team. Within the multi-tenant model, you have two installation variants:

### Non-High Availability

This variant is excellent for evaluation, testing, and proof-of-concept deployments, even though it is not recommended for production use.

- **install.yaml:**

  Deploys ArgoCD with cluster-admin access, making it suitable for clusters where ArgoCD also deploys applications. Additionally, the provided credentials allow for deploying to remote clusters.

- **namespace-installed.yaml:**

  Configures ArgoCD for namespace-level access, offering restricted permissions. This option is useful when you want to limit ArgoCD’s access while still deploying applications in the same cluster if needed.

### High Availability

For production environments, the high availability option is the recommended choice. It improves resilience by deploying multiple replicas for critical components. Two manifests are provided:

- [ha-install.yaml](https://github.com/argoproj/argo-cd/blob/master/manifests/ha/install.yaml)
- [ha-namespace-installed.yaml](https://github.com/argoproj/argo-cd/blob/master/manifests/ha/namespace-install.yaml)

!!! note
    In this lesson, we will deploy ArgoCD within the `argocd` namespace using the non-HA installation manifest (install.yaml).

## Installing ArgoCD with Helm

In addition to the standard installation, ArgoCD can be installed using Helm through a [community-maintained chart](https://github.com/argoproj/argo-helm/tree/main/charts/argo-cd). By default, the Helm chart deploys the non-HA version of ArgoCD.

After installation, download the ArgoCD CLI from its GitHub repository and move it to your local binary directory. The CLI allows you to efficiently interact with the ArgoCD API server.

## Installation Commands

Use the following commands to install ArgoCD:

```bash
# Deploy ArgoCD using Kubernetes manifest
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Add the Helm repository for ArgoCD
helm repo add argo https://argoproj.github.io/argo-helm

# Install ArgoCD using Helm (non-HA version)
helm install my-argo-cd argo/argo-cd --version 4.8.0
```

### QuickStart

### Helm

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace
```

```bash hl_lines="1" title="Install Argo CD CLI"
brew install argocd
```

https://formulae.brew.sh/formula/argocd#default


!!! abstract ""

    ## Links and References

    - https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/
    - [Argo CD Core](https://argo-cd.readthedocs.io/en/stable/operator-manual/core/)