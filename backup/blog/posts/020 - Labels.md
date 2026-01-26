---
title: Labels Argo CD UI
date: 2025-12-15
categories:
  - Argo CD
tags:
  - Argo CD
  - Argo CD UI
  - Labels
---

```yaml title="podinfo-appset.yaml" hl_lines="20-22" linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  labels:
    app.kubernetes.io/name: podinfo
  name: podinfo
  namespace: argocd
spec:
  goTemplate: true
  generators:
  - list:
      elements:
      - name: production
        server: https://production-control-plane:6443
      - name: staging
        server: https://staging-control-plane:6443
  template:
    metadata:
      name: 'podinfo-{{.name}}'
      labels:
        environment: '{{.name}}'
        app: podinfo
      finalizers:
        - resources-finalizer.argocd.argoproj.io
    spec:
      project: default
      source:
        repoURL: https://github.com/stefanprodan/podinfo.git
        targetRevision: HEAD
        path: kustomize
      destination:
        server: '{{.server}}'
        namespace: podinfo
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
```

Pour filtrer dans l'UI ArgoCD, vous avez besoin des labels dans `template.metadata.labels`