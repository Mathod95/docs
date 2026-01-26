---
title: "Use Kustomize to post-render Helm charts in ArgoCD"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://dev.to/camptocamp-ops/use-kustomize-to-post-render-helm-charts-in-argocd-2ml6"
author:
  - "[[Mickaël Canévet]]"
---
<!-- more -->

In an ideal world you wouldn't have to perform multiple steps for the rendering, but unfortunately we don't live in an ideal world...

## Kustomize

Nowadays, most applications that are meant to be deployed in Kubernetes provide a Helm chart to ease deployment. Unfortunately, sometimes the Helm chart is not flexible enough to do what you want to do, so you have to fork and contribute and hope that your contribution is quickly merged upstream so that you don't have to maintain your fork.

Instead of pointing to your fork, you could use [Kustomize](https://kustomize.io/) to apply some post-rendering to your templatized Helm release. This is possible natively since Helm 3.1 using the .

## Integration in ArgoCD

At Camptocamp, we use [ArgoCD](https://argoproj.github.io/argo-cd/) to manage the deployment of our objects into Kubernetes. Let's see how we can use Kustomize to do post-rendering of Helm charts in ArgoCD:

At first, declare a new config management plugin into your `argocd-cm` configMap (the way to do it depends on the way you deployed ArgoCD):  

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  configManagementPlugins: |
    - name: kustomized-helm
      init:
        command: ["/bin/sh", "-c"]
        args: ["helm dependency build || true"]
      generate:
        command: ["/bin/sh", "-c"]
        args: ["helm template . --name-template $ARGOCD_APP_NAME --namespace $ARGOCD_APP_NAMESPACE --include-crds > all.yaml && kustomize build"]
```

Then add a `kustomization.yaml` file next to your application's `Chart.yaml` file:  

```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - all.yaml

patchesJson6902:
  - target:
      group: apps
      version: v1
      kind: Deployment
      name: myapplication
    patch: |-
      - op: remove
        path: /spec/template/spec/securityContext
```

Now configure your `Applications` object to use this plugin:  

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapplication
  namespace: argocd
spec:
  project: myproject
  source:
    path: myapplication
    repoURL: {{ .Values.spec.source.repoURL }}
    targetRevision: {{ .Values.spec.source.targetRevision }}
    plugin:
      name: kustomized-helm
  destination:
    namespace: myproject
    server: {{ .Values.spec.destination.server }}
```

And... voilà!

## Integration in App of Apps

One thing that I often do is to use `spec.source.helm` in my `Application` object to pass some values that comes from my [app of apps](https://argoproj.github.io/argo-cd/operator-manual/cluster-bootstrapping/). This is not possible using a configuration plugin as the keys `helm` and `plugin` are mutually exclusive.

The workaround I found is to use plugin's envs. You have to change your config management plugin configuration to (note the `$HELM_ARGS`):  

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  configManagementPlugins: |
    - name: kustomized-helm
      init:
        command: ["/bin/sh", "-c"]
        args: ["helm dependency build || true"]
      generate:
        command: ["/bin/sh", "-c"]
        args: ["echo \"$HELM_VALUES\" | helm template . --name-template $ARGOCD_APP_NAME --namespace $ARGOCD_APP_NAMESPACE $HELM_ARGS -f - --include-crds > all.yaml && kustomize build"]
```

You'll then be able to use this in your `Application`:  

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapplication
  namespace: argocd
spec:
  project: myproject
  source:
    path: myapplication
    repoURL: {{ .Values.spec.source.repoURL }}
    targetRevision: {{ .Values.spec.source.targetRevision }}
    plugin:
      name: kustomized-helm
      env:
        - name: HELM_ARGS
          value: "--set targetRevision={{ .Values.spec.source.targetRevision }}"

  destination:
    namespace: myproject
    server: {{ .Values.spec.destination.server }}
```

Or  

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapplication
  namespace: argocd
spec:
  project: myproject
  source:
    path: myapplication
    repoURL: {{ .Values.spec.source.repoURL }}
    targetRevision: {{ .Values.spec.source.targetRevision }}
    plugin:
      name: kustomized-helm
      env:
        - name: HELM_VALUES
          value: |
            targetRevision: {{ .Values.spec.source.targetRevision }}

  destination:
    namespace: myproject
    server: {{ .Values.spec.destination.server }}
```

[![Image of Bright Data and n8n Challenge](https://media2.dev.to/dynamic/image/width=775%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2Fslp0b1u3ff18kt0s5yf3.png)](https://dev.to/joupify/soc-cert-automated-threat-intelligence-system-with-n8n-ai-5722?bb=246461)

## SOC-CERT: Automated Threat Intelligence System with n8n & AI

Check out this submission for the [AI Agents Challenge powered by n8n and Bright Data](https://dev.to/challenges/brightdata-n8n-2025-08-13?bb=246461).