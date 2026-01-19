---
title: "⎈ A Hands-On Guide to ArgoCD on Kubernetes  —  PART-1 ⚙️"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@muppedaanvesh/a-hands-on-guide-to-argocd-on-kubernetes-part-1-%EF%B8%8F-7a80c1b0ac98"
author:
  - "[[Anvesh Muppeda]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*63BNapaOyuP8hyA_NvDP7g.jpeg)

ArgoCD Architecture by Anvesh Muppeda

## Introduction

In the Kubernetes ecosystem, GitOps has become a popular approach for managing infrastructure and application deployment. ArgoCD is a powerful GitOps tool that synchronizes your Kubernetes resources with your Git repositories.

In this guide, we’ll walk you through installing ArgoCD on a Kubernetes cluster and deploying your first application using ArgoCD.

## Table of Contents

1. Prerequisites
2. What is ArgoCD?
3. Installing ArgoCD on Kubernetes
4. Accessing the ArgoCD Dashboard
5. Deploying Your First Application with ArgoCD
6. Syncing and Monitoring Your Application
7. Conclusion

## 1\. Prerequisites

Before we begin, ensure you have the following:

- A running Kubernetes cluster (minikube, EKS, GKE, etc.)
- `kubectl` configured to interact with your cluster
- Basic knowledge of Kubernetes resources

## 2\. What is ArgoCD?

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It follows the GitOps paradigm, where the desired state of your application is defined in Git, and ArgoCD ensures that your Kubernetes cluster matches this desired state.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9FtgirOBsLeN-OOz4Gey8g.gif)

Animated ArgoCD Architecture by Anvesh Muppeda

## 3\. Installing ArgoCD on Kubernetes

Let’s start by installing ArgoCD in your Kubernetes cluster. There are two different ways to do this: using manifest files or a Helm chart.

### Step 1: Install ArgoCD

**Method 1: Using Manifest Files**

You can install ArgoCD using the official manifest files provided by the ArgoCD team.

```c
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

This command installs all the necessary ArgoCD components, including the API server, controller, and UI.

**Method 2: Using a Helm Chart**

Alternatively, you can install ArgoCD using the Helm chart, which allows for more customization through Helm values.

1. Add the ArgoCD Helm repository:
```c
helm repo add argo https://argoproj.github.io/argo-helm
```

2\. Install the Helm chart with a custom values file:

```c
helm install argocd-demo argo/argo-cd -f argocd-custom-values.yaml
```

In this example, `argocd-custom-values.yaml` might look like this:

```c
server:
  service:
    type: NodePort
```

This overrides the ArgoCD service type from the default `ClusterIP` to `NodePort`, allowing you to access the ArgoCD UI via a NodePort.

### Step 2: Verify the Installation

To check if ArgoCD is running correctly, use the following command:

```c
kubectl get pods -n argocd
```

All pods should be in a `Running` state.

## 4\. Accessing the ArgoCD Dashboard

### Step 1: Forward the ArgoCD Server Port

To access the ArgoCD UI, you need to forward the ArgoCD server port(if you don’t use service type NodePort):

```c
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*VSEQzQZ2cRBWkkc-HSDICg.png)

ArgoCD Login Page

### Step 2: Login to the Dashboard

Open your browser and go to \`https://localhost:8080\` or http://<public-ip>:<nodeport>

The default username is `admin`, and to retrieve the password, use:

```c
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath={.data.password} | base64 -d
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*aqM1aq6KAAar21TtMOg8Vg.png)

ArgoCD Dashboard

## 5\. Deploying Your First Application with ArgoCD

### Step 1: Create a Git Repository

First, create a Git repository that contains your Kubernetes manifests. This repository will serve as the source for ArgoCD to deploy your application.

### Step 2: Create an Application in ArgoCD

**Method 1: Using the ArgoCD UI**

1. **Create a Git Repository**: First, create a Git repository that contains your Kubernetes manifests. This repository will serve as the source for ArgoCD to deploy your application.
2. **Create an Application in ArgoCD**:
- In the ArgoCD dashboard, click on `New App` and fill in the following details:
- **Application Name**: `my-first-app`
- **Project**: `default`
- **Sync Policy**: Manual or Automatic (your choice)
- **Repository URL**: URL of your Git repository
- **Path**: Path to your Kubernetes manifests in the repository
- **Cluster URL**: Leave as default for your current cluster
- **Namespace**: The namespace where the application should be deployed
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Fn22rC95RosnfqlEiZDf9g.png)

Step 1: ArgoCD Application Creation

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*jRSL-R6QtCWvDbFvYBp4Bg.png)

Step 2: ArgoCD Application Creation

Once the application is created, click on `Sync` to deploy the application to your Kubernetes cluster. If Sync Policy Set to Automatic then application will be deployed to kubernetes automatically.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*eTxKdMIxZkeHtmiinlSGPQ.png)

## Method 2: Using a Manifest File

You can also create an ArgoCD application by defining it in a manifest file and applying it with `kubectl`.

1. **Create the Manifest**: Save the following content to a file named `argocd-demo-app.yaml`:
```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: first-argocd-demo-app
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/anveshmuppeda/argo-cd-demo
    targetRevision: HEAD
    path: development

  destination: 
    server: https://kubernetes.default.svc
    namespace: argocd-demo

  syncPolicy:
    syncOptions:
    - CreateNamespace=true

    automated:
      selfHeal: true
      prune: true
```

2\. **Apply the Manifest**:

Use `kubectl` to apply the manifest:

```c
kubectl apply -f argocd-demo-app.yaml
```

This command creates an ArgoCD application named `first-argocd-demo-app` in the `argocd` namespace, which will sync your Kubernetes manifests from the specified Git repository.

## 6\. Syncing and Monitoring Your Application

After syncing, ArgoCD will start deploying the application. You can monitor the progress in the dashboard. If there are any issues, ArgoCD will highlight them, and you can take corrective actions directly from the UI.

ArgoCD also supports features like automated rollbacks, self-healing, and more, ensuring your Kubernetes cluster is always in the desired state as defined in your Git repository.

### Step 6.1: Automatic Sync on GitHub Updates

One of the powerful features of ArgoCD is its ability to automatically sync your Kubernetes cluster with your Git repository. This means that any changes you make to your manifests in GitHub will be automatically applied to your cluster.

**Example: Updating an NGINX Deployment**

Let’s walk through an example to demonstrate this feature

1. **Initial Deployment**:

Initially, your GitHub repository contains the following `nginx-deploy-1` deployment:

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy-1
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx-container
        image: nginx:latest
```

After deploying this application using ArgoCD, the `nginx-deploy-1` deployment will be running in your Kubernetes cluster.

**2\. Updating the Deployment**:

Suppose you decide to change the deployment in your GitHub repository to the following:

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy-2
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx-container
        image: nginx:latest
```

This update changes the deployment name from `nginx-deploy-1` to `nginx-deploy-2`.

**3\. Automatic Sync and Deployment**:

With ArgoCD’s automatic sync policy enabled, as soon as you push this change to your GitHub repository, ArgoCD will detect the update and automatically apply it to your Kubernetes cluster.

The following actions will occur:

- The `nginx-deploy-1` deployment will be deleted.
- The `nginx-deploy-2` deployment will be created.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Hzwwu5fb4JeXLmu3yxDNwQ.png)

ArgoCD Automatically updating the application

You can observe these changes in the ArgoCD dashboard, where ArgoCD will show the status of the new deployment and confirm that the cluster is in sync with the Git repository.

This automatic sync feature is incredibly powerful for continuous deployment, ensuring that your cluster always matches the desired state defined in your Git repository.

## 7\. Conclusion

In this guide, we’ve walked through the installation of ArgoCD on a Kubernetes cluster and deployed your first application using ArgoCD. ArgoCD is a powerful tool that simplifies the process of managing Kubernetes resources using GitOps practices. With this setup, you can now explore more advanced features of ArgoCD, such as automated rollbacks, application health monitoring, and multi-cluster management.

## Source Code

You’re invited to explore our [GitHub repository](https://github.com/anveshmuppeda/kubernetes), which houses a comprehensive collection of source code for Kubernetes.## [GitHub — anveshmuppeda/kubernetes: Kuberntes Complete Notes](https://github.com/anveshmuppeda/kubernetes?source=post_page-----7a80c1b0ac98---------------------------------------)

Kuberntes Complete Notes. Contribute to anveshmuppeda/kubernetes development by creating an account on GitHub.

github.com

[View original](https://github.com/anveshmuppeda/kubernetes?source=post_page-----7a80c1b0ac98---------------------------------------)

Also, if we welcome your feedback and suggestions! If you encounter any issues or have ideas for improvements, please open an issue on our [GitHub repository](https://github.com/anveshmuppeda/kubernetes/issues). 🚀

## Connect With Me

If you found this blog insightful and are eager to delve deeper into topics like AWS, cloud strategies, Kubernetes, or anything related, I’m excited to connect with you on [LinkedIn](https://www.linkedin.com/in/anveshmuppeda/). Let’s spark meaningful conversations, share insights, and explore the vast realm of cloud computing together.

Feel free to reach out, share your thoughts, or ask any questions. I look forward to connecting and growing together in this dynamic field!

> *My LinkedIn:* [*https://www.linkedin.com/in/anveshmuppeda/*](https://www.linkedin.com/in/anveshmuppeda/)
> 
> *My GitHub:* [*https://github.com/anveshmuppeda*](https://github.com/anveshmuppeda)

Happy deploying! 🚀

Happy Kubernetings! ⎈

I’m a Kubernetes developer and cloud architect Certifications: 3x AWS | 2x Kubernetes Connect with me on [www.linkedin.com/in/anveshmuppeda](http://www.linkedin.com/in/anveshmuppeda)

## More from Anvesh Muppeda

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--7a80c1b0ac98---------------------------------------)