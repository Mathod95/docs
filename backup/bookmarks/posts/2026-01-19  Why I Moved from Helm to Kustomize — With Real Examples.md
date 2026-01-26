---
title: "Why I Moved from Helm to Kustomize — With Real Examples"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://towardsdev.com/why-i-moved-from-helm-to-kustomize-with-real-examples-33ea172d5113"
author:
  - "[[Bill WANG]]"
---
<!-- more -->

[Sitemap](https://towardsdev.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@bill)## [Towards Dev](https://towardsdev.com/?source=post_page---publication_nav-a648dc4ecb66-33ea172d5113---------------------------------------)

[![Towards Dev](https://miro.medium.com/v2/resize:fill:76:76/1*c2OaLMtxURd1SJZOGHALWA.png)](https://towardsdev.com/?source=post_page---post_publication_sidebar-a648dc4ecb66-33ea172d5113---------------------------------------)

A publication for sharing projects, ideas, codes, and new theories.

In Kubernetes land, Helm is often the go-to tool for templating and deploying applications. I used Helm for years, and while it served me well, I gradually ran into limitations — especially as I scaled into GitOps, multi-env setups, and more opinionated CI/CD pipelines.

Eventually, I migrated much of my infrastructure and app deployments to **Kustomize**. In this blog, I’ll explain **why** I made the switch, and give **real code comparisons** to show how **Kustomize simplified configuration management** — especially around environment-specific changes.

## 🌩️ Problem: Helm Gets Complex as You Scale

Helm is powerful, but its templating model can become overly complex when:

- Managing multiple environments (e.g., dev, staging, prod)
- Making small changes across multiple values.yaml files
- Trying to diff or audit rendered manifests
- Avoiding logic mixed with YAML via Go templates

Let’s look at a simple example: deploying an NGINX app and modifying the **replica count** and **image tag** for different environments.

## 🧪 Helm Example: Overhead in values.yaml

`**templates/deployment.yaml**`

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.app.name }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: {{ .Values.app.name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

`**values.yaml**` **(base)**

```c
app:
  name: nginx
replicaCount: 2
image:
  repository: nginx
  tag: "1.25"
```

`**values-prod.yaml**`

```c
replicaCount: 4
image:
  tag: "1.26"
```

**To deploy:**

```c
helm install nginx ./nginx-chart -f values.yaml -f values-prod.yaml
```

At first glance, this seems fine. But what happens when:

- You add new environments?
- You want GitOps to diff changes?
- You want overlays but not maintain 5 different values files?
- Need to add the new variables like `{{ .Values.xxxx }}` if they don’t already exist—not just in the `values.yaml` file, but also in the template YAML files?

**Imagine you’re not just dealing with a few templated YAML files, but managing thousands of them. All template Yaml files are full of weird** `**{{ }}**`

## ✅ Kustomize Example: Simple and Layered

`**base/deployment.yaml**`

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
```

This plain YAML file is easy to read and understand, correct?

`**overlays/prod/kustomization.yaml**`

```c
resources:
  - ../../base
patchesStrategicMerge:
  - deployment-patch.yaml
```

`**overlays/prod/deployment-patch.yaml**`

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 4
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:1.26
```

**To deploy:**

```c
kustomize build overlays/prod | kubectl apply -f -
```

## 🔄 Making a Change: Helm vs Kustomize

Let’s say we want to increase replicas from 4 to 5 **in production**.

## 🛠️ In Helm:

You edit `values-prod.yaml`:

```c
replicaCount: 5
```

Then re-run:

```c
helm upgrade nginx ./nginx-chart -f values.yaml -f values-prod.yaml
```

But:

- Helm must re-render templates every time.
- Small changes are hidden inside values.
- Git diffs aren’t easily readable from the rendered manifests.

## 🛠️ In Kustomize:

You update just this file:

`**overlays/prod/deployment-patch.yaml**`

```c
spec:
  replicas: 5
```

Then re-run:

```c
kustomize build overlays/prod | kubectl apply -f -
```

✅ Clear.  
✅ Declarative.  
✅ Easy to track changes in Git.

More real and complext example to compare

Helm chart: [https://github.com/grafana/grafana-operator/blob/master/deploy/helm/grafana-operator/templates/deployment.yaml](https://github.com/grafana/grafana-operator/blob/master/deploy/helm/grafana-operator/templates/deployment.yaml)

Kustomize: [https://github.com/grafana/grafana-operator/blob/master/deploy/kustomize/base/deployment.yaml](https://github.com/grafana/grafana-operator/blob/master/deploy/kustomize/base/deployment.yaml)

## 🧠 Lessons Learned

- Kustomize **forces clarity** — no hidden logic, no magic defaults.
- Helm **can get messy** when managing environments at scale.
- Kustomize **plays better with GitOps** tools like ArgoCD, Flux, and GitHub Actions.
- I still use Helm **for third-party apps** (like Prometheus or Redis) where community charts save time.

[![Towards Dev](https://miro.medium.com/v2/resize:fill:96:96/1*c2OaLMtxURd1SJZOGHALWA.png)](https://towardsdev.com/?source=post_page---post_publication_info--33ea172d5113---------------------------------------)

[![Towards Dev](https://miro.medium.com/v2/resize:fill:128:128/1*c2OaLMtxURd1SJZOGHALWA.png)](https://towardsdev.com/?source=post_page---post_publication_info--33ea172d5113---------------------------------------)

[Last published 18 hours ago](https://towardsdev.com/why-vibe-coding-feels-right-until-it-doesnt-ea92e623dba0?source=post_page---post_publication_info--33ea172d5113---------------------------------------)

A publication for sharing projects, ideas, codes, and new theories.

## More from Bill WANG and Towards Dev

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--33ea172d5113---------------------------------------)