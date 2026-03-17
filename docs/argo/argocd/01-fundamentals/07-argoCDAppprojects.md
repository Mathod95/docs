---
title: App projects
status: draft
sources:
  - https://notes.kodekloud.com/docs/GitOps-with-ArgoCD/ArgoCD-Basics/ArgoCD-App-projects/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/gitops-with-argocd/module/546d7ffa-8e6e-4197-9dff-443bb15dcdf6/lesson/715620fc-f104-40b5-9be4-7f59571e517d
---

> Learn to use ArgoCD applications and projects for effective deployment and management of applications in Kubernetes clusters.

Discover how to leverage ArgoCD applications and projects to deploy and manage applications in Kubernetes clusters effectively. In this guide, we explore the core concepts of ArgoCD, explain how to create applications using both the CLI and YAML, and provide detailed code examples.

ArgoCD revolves around two main concepts: the application and the project.

An application in ArgoCD is a Custom Resource Definition (CRD) that represents a deployed instance within your Kubernetes cluster. It includes two primary components:

1. **Source:**\
   Points to the Git repository (or supported alternatives like Helm charts, Kustomize, or Jsonnet) where the desired state of your Kubernetes manifests is defined.

2. **Destination:**\
   Defines the target Kubernetes cluster and namespace where the resources will be deployed.

Additionally, an application specifies the project it belongs to and incorporates synchronization policies that ensure the deployed state stays in sync with the source repository.

<Frame>
  ![The image is a diagram of an ArgoCD application, showing different sources like Git, Helm, and Jsonnet, along with destination, project, sync policy, and ignore diff settings.](https://kodekloud.com/kk-media/image/upload/v1752877506/notes-assets/images/GitOps-with-ArgoCD-ArgoCD-App-projects/argocd-application-diagram-sources.jpg)
</Frame>

There are several methods to create an ArgoCD application, including using the CLI, YAML specification, or the user interface.

***

<Callout icon="lightbulb" color="#1CB2FE">
  When choosing the creation method, consider your team's workflow. The CLI is great for quick operations while YAML is preferred for version-controlled deployments.
</Callout>

***

## Creating an Application

### Creating an Application Using the CLI

When managing ArgoCD via the Command Line Interface (CLI), you supply critical parameters including the repository URL, manifest path, destination Kubernetes server, and destination namespace. Use the following example:

```bash
$ argocd app create color-app \
  --repo https://github.com/sid/app-1.git \
  --path team-a/color-app \
  --dest-namespace color \
  --dest-server https://kubernetes.default.svc
Application `color-app` created
```

After running this command, ArgoCD retrieves the manifest from the provided Git repository and deploys the resources to the specified namespace.

***

### Creating an Application Using YAML

For a more declarative approach, you can define your application using a YAML file. Below is a sample YAML manifest for an ArgoCD application, where the application is created within the default ArgoCD project:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: color-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/sid/app-1.git
    targetRevision: HEAD
    path: team-a/color
  destination:
    server: https://kubernetes.default.svc
    namespace: color
  syncPolicy:
    automated:
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

The manifest details illustrate how the components—source, destination, and sync policy—integrate to ensure consistent deployment and automatic rollback if needed.

***

<Callout icon="lightbulb" color="#1CB2FE">
  For additional guidance on managing and configuring ArgoCD projects, explore our detailed documentation and recommended practices.
</Callout>

ArgoCD projects offer a way to centrally manage permissions and settings across multiple applications, providing a more scalable approach to modern GitOps workflows.

For more detailed information, check out the following resources:



By integrating these best practices into your GitOps pipeline, you can streamline application deployments and maintain robust, scalable infrastructure management in Kubernetes.