---
title: "Beyond Kubernetes — CI/CD with argoCD"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://howtodoitincloud.medium.com/beyond-kubernetes-ci-cd-with-argocd-5eb1d35f3c12"
author:
  - "[[Suman Dhakal]]"
---
<!-- more -->

[Sitemap](https://howtodoitincloud.medium.com/sitemap/sitemap.xml)

This is the last part of the series [Beyond Kubernetes](https://howtodoitincloud.medium.com/beyond-kubernetes-part-i-b2d3397b87d3), and this article is going to discuss adding the argoCD to a demo application to build a complete automated infrastructure and application as code.

We have already created a Kubernetes cluster and installed the ArgoCD application on the cluster in the [previous](https://howtodoitincloud.medium.com/beyond-kubernetes-installing-cluster-components-782885a1d67b) chapters. With this final chapter, we are trying to achieve the following:.

- Creating a [demo application](https://github.com/sumandhakal04/argocd-demo-app) for the presentation purpose.
- Setting up CI/CD in the demo application to automatically build and push the Docker images to the Docker registry, as well as update the image tag on the [deployment manifests](https://github.com/sumandhakal04/argocd).
- Setting up argoCD hooks on the Kubernetes manifests repository. Whenever there is a new tag on the deployment, argoCD would pull and deploy the latest application image on the cluster.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*RI2PL5A0_VElTgOH.png)

GitOps with argoCD

## Creating a Demo application and setting up CI/CD

We will be creating a very basic application, a nginx Docker image serving a single HTML file on a repository; let’s call it [argocd-demo-app](https://github.com/sumandhakal04/argocd-demo-app). The same idea could well be extended to setup CI/CD for more complex applications.

The application is hosted on a Kubernetes cluster, and the Kubernetes manifests are stored in another repository, lets call it [argocd](https://github.com/sumandhakal04/argocd)

We are setting up CI/CD on the [argocd-demo-app](https://github.com/sumandhakal04/argocd-demo-app) repo to 1. Build, tag, and push Docker images to Amazon ECR and 2. Update the image tag on the deployment file on the [argocd](https://github.com/sumandhakal04/argocd) repo.

The following varaibles need to be added as secrets on the github repository for the pipeline:

- `DOCKER_REGISTRY`
- `IMAGE_NAME`
- `CI_REGISTRY_USER`
- `CI_REGISTRY_PASSWORD`
- `CI_ACCESS_TOKEN`

## Automated builds with argoCD

Like mentioned earlier, argoCD is hooked on the Kubernetes manifests repo. Whenever it detects a change on the Docker image tag on the repo, it pulls the same image tag from the Docker registry and deploys the image with the new tag on the cluster.

Let’s dive into this now. How does ArgoCD do this? With applicationset. An [**ApplicationSet**](https://argo-cd.readthedocs.io/en/latest/user-guide/application-set/) in Argo CD can scan a Git repo (e.g., by folder or file structure) and automatically create application resources to deploy the same app across multiple target clusters, streamlining multi-cluster GitOps deployments. In our case, it is a single cluster only.

## Beyond Kubernetes project Diagram

The overall project diagram looks like the following:. There are four separate git repositories, namely 1. terraform-eks-module, to provision EKS Clusters 2. beyond-kubernetes, to create cluster components, platform applications and other applications 3. argocd, to create Kubernetes objects for the demo application, and finally 4. demo-app, the application repo itself. Each repository has it’s own CI/CD building mechanism and CI/CD tool.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*UUmdBaVyReFB5gb8oSPwJg.png)

Final Project Diagram

## Conclusion

We set the following objectives when starting this project:

1. Declarative Environments
2. Automate everything
3. State Management

In the first chapter, we created the Cluster in Amazon EKS as well as related AWS services and Service Accounts with Terraform. A github actions pipeline was also setup to automate builds for the new changes on Terraform configurations.

In the second chapter, we configured the Cluster components—platform applications and user applications—as code with Kustomize. We set up FluxCD to automate the build and manage the state of the applications.

Finally, in the third and last chapter, we set up CI/CD on the demo application with github actions. We also set up argoCD to automatically detect the image tag change, pull the latest image, and deploy it in the cluster.

We set up the entire project as a declarative setup, automated the deployment of applications and platforms at every level, and the state management is handled by the system itself.

## References

- [https://howtodoitincloud.medium.com/beyond-kubernetes-part-i-b2d3397b87d3](https://howtodoitincloud.medium.com/beyond-kubernetes-part-i-b2d3397b87d3)
- [https://howtodoitincloud.medium.com/beyond-kubernetes-installing-cluster-components-782885a1d67b](https://howtodoitincloud.medium.com/beyond-kubernetes-installing-cluster-components-782885a1d67b)
- [https://argo-cd.readthedocs.io/en/latest/user-guide/application-set/](https://argo-cd.readthedocs.io/en/latest/user-guide/application-set/)
- [https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/)

AWS Certified Security Specialist and AWS certified Solutions Architect — Associate

## More from Suman Dhakal

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--5eb1d35f3c12---------------------------------------)