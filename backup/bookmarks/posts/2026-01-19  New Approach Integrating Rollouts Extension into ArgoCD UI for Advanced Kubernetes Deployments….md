---
title: "New Approach: Integrating Rollouts Extension into ArgoCD UI for Advanced Kubernetes Deployments…"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@osascourage27/new-approach-integrating-rollouts-extension-into-argocd-ui-for-advanced-kubernetes-deployments-61de89cd6a24"
author:
  - "[[Osakpolor Courage Ihensekhien]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*KvjtTTnTf_tvo_sLTvIKLA.png)

Kubernetes has revolutionized the way we manage containerized applications, enabling dynamic scaling and rapid deployment. However, as deployments become more complex, managing them efficiently can become challenging. ArgoCD and Argo Rollouts are two powerful tools designed to address these complexities, offering sophisticated deployment strategies and continuous delivery (CD) capabilities. By integrating Argo Rollouts UI into ArgoCD UI, we can streamline the deployment process, providing a unified interface for managing and visualizing advanced deployment strategies.

## Argo Rollouts:

Argo Rollouts is a Kubernetes controller and CRD (Custom Resource Definition) that automates the deployment strategies for Kubernetes resources. It builds upon the standard Kubernetes Deployment controller but adds additional features and deployment strategies, such as Blue-Green, A/B testing as well as Canary deployments.

### Key Features of Argo Rollouts:

1. Canary Deployments: Argo Rollouts simplifies the implementation of Canary deployments within Kubernetes clusters, allowing for fine-grained control over rollout strategies.
2. Progressive Delivery: Beyond Canary deployments, Argo Rollouts supports other progressive delivery strategies like Blue-Green and A/B testing.
3. Traffic Shifting: Automated traffic shifting mechanisms enable smooth transitions between different versions of an application, minimizing downtime and user impact.

## ArgoCD UI:

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. ArgoCD UI is its web-based user interface that provides visibility and management capabilities for Kubernetes applications and their deployments.

### Features of ArgoCD UI:

1. Application Management: ArgoCD UI allows users to define, manage, and synchronize applications and their configurations stored in Git repositories.
2. Deployment Automation: It automates the deployment process by continuously monitoring the desired state of applications in Git and reconciling them with the actual state in the Kubernetes cluster.
3. Rollout Visualization: ArgoCD UI without the Argo-Rollout UI provides visualizations of deployment status, including the progress of Canary deployments managed by Argo Rollouts.

## Integrating Argo Rollouts UI into ArgoCD UI as an extension

Even though there are some visualization of Argo Rollout resources on the argocd UI, this is not really as it will be in a native Argo Rollout web UI, To have a more unified interface with enhanced visibility and control and enhanced collaboration, there is a need to find a way to integrate it into ArgoCD UI. One way to do this is using ArgoCD UI extensions, before now, we use the ArgoCDExtension CR from argoproj-labs which is now [deprecated](https://github.com/argoproj-labs/argocd-extensions). According to recent version of ArgoCD, There is a new way to integrate a UI extension, you can look up the documentation [here](https://argo-cd.readthedocs.io/en/stable/developer-guide/extensions/ui-extensions/#:~:text=Flyout%20widget-,UI%20Extensions,-%C2%B6) for more details.

[Argo Rollout extension](https://github.com/argoproj-labs/rollout-extension) is one of the argoproj-labs project, and due to the recent change in the way a UI extension is added to ArgoCD, there is also a new project in argoproj-lab called Argo CD Extension Installer, you can look at it to create your own docker image of the installer extension or just used the already create image. This extension installer can be used to add any other extension to Argo CD UI.

**Below are the steps to add the rollout extension to ArgoCD UI**

1. Ensure that Argo CD is already running in the cluster:  
	You can look at the documentation [here](https://argo-cd.readthedocs.io/en/stable/getting_started/) to setup Argo CD in your cluster
2. Using kubectl command, edit the argocd-server deployment resource running in your cluster
```c
kubectl edit deployment argocd-server -n argocd
```

Edit the argocd-server deployment adding the initContainer, volumeMount and volume parts as below. as below as indincated in the Argo CD UI extension [documenation](https://argo-cd.readthedocs.io/en/stable/developer-guide/extensions/ui-extensions/#:~:text=Flyout%20widget-,UI%20Extensions,-%C2%B6)

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-server
spec:
  template:
    spec:
      initContainers:
        - name: rollout-extension
          image: quay.io/argoprojlabs/argocd-extension-installer:v0.0.1
          env:
          - name: EXTENSION_URL
            value: https://github.com/argoproj-labs/rollout-extension/releases/download/v0.3.5/extension.tar
          volumeMounts:
            - name: extensions
              mountPath: /tmp/extensions/
          securityContext:
            runAsUser: 1000
            allowPrivilegeEscalation: false
      containers:
        - name: argocd-server
          volumeMounts:
            - name: extensions
              mountPath: /tmp/extensions/
      volumes:
        - name: extensions
          emptyDir: {}
```

After the update has been applied successfully, logon on to the ArgoCD UI if you don’t have an ingress or loadbalancer url yet you can quickly do kubectl portforward to access the UI

```c
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**Canay Deployment example**

In the Argo CD UI create a new application referencing the repository with the canary deployment configurations. The result is as below

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*oimWLB1aII9W-SUlJi2BMg.png)

Click on the rollout resource and you will see this, then click on the ROLLOUT tab to access the rollout UI for the application

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*TyORD7OVja5g6wTeIAJJaw.png)

Rollout UI  
Below is the rollout UI for the application and we are able to view the details the deployment strategy and the clicking on three vertical dots icon in the top right, you can access all the various rollout options.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2Y2TYegdVXz268kfj5Jwmw.png)

Rollout options

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Jx0K_P97gIbk7XRyYeV7dQ.png)

## Conclussion

Integrating Argo Rollouts UI into ArgoCD UI streamlines the management of advanced Kubernetes deployments. It offers a unified interface, enhanced visibility, and simplified operations, empowering teams to deliver applications more efficiently and reliably. By following the steps outlined above, you can harness the full potential of both ArgoCD and Argo Rollouts, optimizing your deployment workflows and achieving continuous delivery excellence in your Kubernetes environment.  
You can check out the rollout deployment repository [**here**](https://github.com/CourageOI/tpss-api/tree/dev/rollout-test/argocd-canary)

You can reach out to me if you have any question and also follow me for more DevOps and SRE posts.

DevOps Engineer | SRE | Software Engineering | AI enthusiast

## More from Osakpolor Courage Ihensekhien

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--61de89cd6a24---------------------------------------)