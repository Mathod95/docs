---
title: "GitOps Workflow On A Kind Kubernetes Cluster Using ArgoCD"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://olymahmud.medium.com/gitops-workflow-on-a-kind-kubernetes-cluster-using-argocd-aeeb85b15704"
author:
  - "[[M. Oly Mahmud]]"
---
<!-- more -->

[Sitemap](https://olymahmud.medium.com/sitemap/sitemap.xml)

![GitOps Workflow on kind Kubernetes Using ArgoCD](https://miro.medium.com/v2/resize:fit:640/format:webp/1*6KMcoL7e2-ly716obBa9wg.png)

GitOps Workflow on kind Kubernetes Using ArgoCD

GitOps is a modern approach to continuous deployment where Git is the single source of truth for infrastructure and application configurations. In this guide, we’ll set up GitOps using **ArgoCD** on a **Kind Kubernetes cluster**.

## What is GitOps?

**GitOps** is a way of managing Kubernetes (and other systems) using Git repositories as the source of truth. With GitOps:

- You define your entire system configuration and applications in Git.
- Tools like ArgoCD automatically sync changes from Git to your Kubernetes cluster.
- Every change is version-controlled, reviewable, and reversible.

## What is ArgoCD?

**ArgoCD** is a declarative, GitOps continuous delivery tool for Kubernetes. It:

- Watches a Git repository for manifest changes
- Automatically or manually syncs these changes into your Kubernetes cluster
- Provides a web UI and CLI for managing apps

***Now, we will deploy an app using ArgoCD on Kubernetes.***

## Prerequisites

Before you begin, make sure you have the following installed:

- [Docker](https://www.docker.com/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kind](https://kind.sigs.k8s.io/)
- [Git](https://git-scm.com/)

## Step 1: Create a Kind Cluster

We’ll use a custom configuration to expose the ArgoCD UI on port `8080`.

`cluster-config.yaml`

```c
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    image: kindest/node:v1.32.2
    extraPortMappings:
      - containerPort: 30443
        hostPort: 8080
        protocol: TCP
        listenAddress: "0.0.0.0"
  - role: worker
    image: kindest/node:v1.32.2
```

## Create the Cluster

Run this command to create the Kubernetes cluster.

```c
kind create cluster --name random-cluster --config cluster-config.yaml
```

You should see something like this:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*94IY-_EBChUMsY55ujQdLw.png)

Verify the cluster:

```c
kubectl cluster-info --context kind-random-cluster
```

You will see

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*pstBtXFYplrqImxJIsPOrQ.png)

## Step 2: Install ArgoCD

Let’s create a namespace called `argocd`

```c
kubectl create namespace argocd
```

## Apply ArgoCD Installation Manifests

```c
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## Expose ArgoCD Server

By default, the ArgoCD server is a `ClusterIP` service, not accessible outside the cluster. We'll change it to `NodePort`.

```c
kubectl patch svc argocd-server -n argocd -p \
'{"spec": {"type": "NodePort", "ports": [
  {"name": "http", "nodePort": 30080, "port": 80, "protocol": "TCP", "targetPort": 8080},
  {"name": "https", "nodePort": 30443, "port": 443, "protocol": "TCP", "targetPort": 8080}
]}}'
```

Now the ArgoCD UI will be accessible at: [**https://localhost:8080**](https://localhost:8080/)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*lnVUWZzr0xRcSAUFOpj_dw.png)

## Log in to ArgoCD UI

Get the initial admin password:

```c
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d && echo
```

Visit [https://localhost:8080](https://localhost:8080/). Log in with:

- **Username**: `admin`
- **Password**: *(from above command)*
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ioxdHL7tTlnvXHkisSsMlA.png)

## Deploy an App Using GitOps

On the homepage, you will see the UI

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*TU5G1b6XoyobOW2904l_cg.png)

argoCD UI

Now let’s deploy a sample Express.js app directly from a GitHub repo using GitOps!

We can use both ArgoCD and a manifest file to deploy apps. But in this post, we will use a manifest file.

## ArgoCD Application Manifest

Save the following YAML file as `express-app-application.yaml`:

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: express-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/OlyMahmudMugdho/kube-express
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: demo
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

## Apply the Manifest

```c
kubectl apply -f express-app-application.yaml
```
- **repoURL**: GitHub repository with your app’s manifests.
- **targetRevision**: Git revision to track (HEAD = latest commit on main/master).
- **path**: The folder in the repo contains Kubernetes YAMLs.
- **destination.server**: Kubernetes API server (here we use the in-cluster default).
- **destination.namespace**: Namespace to deploy to (demo) will be created automatically.
- **syncPolicy.automated.prune**: Removes orphaned resources that are not in Git.
- **syncPolicy.automated.selfHeal**: Fixes any drift between the live cluster and Git.
- **syncOptions.CreateNamespace**: Automatically creates the target namespace if it doesn’t exist.

## Verify Deployment

Go to the ArgoCD UI, you will see something like this:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*-YTRGnpEnP7iU2GdjbNfQA.png)

Check the deployed resources:

```c
kubectl get all -n demo
```

## Access the Express App

Port forward the app to access it from the browser

```c
kubectl port-forward svc/express-app-service 5000:80 -n demo
```

Visit: [http://localhost:5000](http://localhost:5000/)

Congratulations! 🎉 We’ve now built a full GitOps pipeline using:

- A local Kind cluster
- ArgoCD for Git-based deployment
- A GitHub repo containing Kubernetes manifests

## More from M. Oly Mahmud

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--aeeb85b15704---------------------------------------)