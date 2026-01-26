---
title: "Setup GitOps with ArgoCD"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@searcheulong/setup-gitops-with-argocd-ac2da0ed887c"
author:
  - "[[Cheulong Sear]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ZhoWWU5Pv6ZwNag3n4K9jA.png)

- **GitOps** is a set of practices for managing infrastructure and application configurations to expand upon existing processes and improve the application lifecycle.
- **ArgoCD** is a declarative, GitOps continuous delivery tool for Kubernetes. It does this by comparing the config repo to desired state.

## Benefit

- Declarative GtOps Tool
- Kubernetes Native Continous Deployment
- Disaster Recovery
- Control Multiple Clusters

## Prerequisites

- Kubernetes
- Configuration Repository

Here is the common pipeline that companies to use with ArgoCD

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*v4dDoIJvgWiDE-EN.png)

## Setup ArgoCD

### Create namespace and apply the argocd manifest installation file

```c
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Access ArgoCD GUI

```c
kubectl port-forward service/argocd-server -n argocd 8080:443
```

then goto `localhost:8080`

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*qyqk8n9GdiVtf__l.png)

`username: admin`

to get `password`, you need to go back to command line and type

```c
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

now you will see the dashboard

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*iIofX_4TojKO8AuZ.png)

## Example

Now, I will show you how to use ArgoCD in a small helm chart project.  
Usually, there are at least 2 repos for `application` and `deployment`.  
In this example, I have a `nodejs repo` and a `k8s repo`.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*NU7_vxo9OStbQK3c.png)

in application repo

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*WZXsjoiMcDR8BVDN.png)

in k8s repo

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*LiR6-9vU3s96PGSG.png)

### Workflow

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*K18cysVWX-aeawsR.png)

1.Add k8s repo to ArgoCD to monitor when it is changed to update the deployment

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*59FS41xYBg9NSf9-.png)

complete the detail of the app and repo

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*o7j-oi3hpa3KW7Pc.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*7welncwgzMWWXJuk.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*nFeS1fIz-RNO8dJt.png)

click `create`

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*stxBBr9ugyFgSJKH.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*IDRmNextxWlRfH9N.png)

2.When user commit or merge to `main` branch, the github action will build the new docker image and push it to dockerhub

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*irT1LhOUatOm0_bb.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*nyxVZXLXpSQQgeci.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*NoOspDdpRIc5von8.png)

3.After push successfully, the same pipeline will update the image tag number in k8s repo

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*sRCVKcK4Tpy34GEJ.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*jdyhf8akI4KpNdiu.png)

4.ArgoCD detects the change in k8s repo and apply the new manifest from the repo

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*jEr_vZWM6Y6_qMUN.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*JEF7aAZ_VndytadF.png)

[Code](https://github.com/cheulong/devops/tree/main/gitops/argocd) used in this article

**Keep Learning**

Leave a comment if you have any questions.

\===========  
**Please keep in touch**  
[Portfolio](https://cheulongsear.dev/)  
[Linkedin](https://www.linkedin.com/in/cheulongsear/)  
[Github](https://github.com/cheulong)  
[Youtube](https://www.youtube.com/@allo-devops)

Software Engineer @Alstom | DevOps Advocate [cheulongsear.dev](http://cheulongsear.dev/)

## More from Cheulong Sear

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--ac2da0ed887c---------------------------------------)