---
hide:
  - tags
title: "Argo"
description: "Courte description pour l’aperçu et le SEO"
date: 2025-12-01
tags:
  - Argo
  - Argo CD
  - Argo Workflows
  - Argo Events
  - Argo Rollouts
categories:
  - Documentation
  - Argo
author: "Mathias FELIX"
---

## Argo CD
Declarative continuous delivery with a fully-loaded UI.



---

### Rafraîchir le dépôt à une fréquence définie

Par défaut, ArgoCD rafraîchit le contenu du dépôt toutes les 3 minutes. Il est possible de modifier ce comportement pour alléger la charge sur le cluster, notamment lorsque ArgoCD est utilisé pour gérer de nombreux projets ou si le cluster est fortement sollicité.

!!! Info
    Il est important de noter que le rafraîchissement du dépôt ne déclenche pas automatiquement la réconciliation de l’application. Pour cela, l'option **auto-sync** doit être activée.

Pour ajuster cette fréquence, il faut définir la variable d’environnement `ARGOCD_RECOCILIATION_TIMEOUT` dans le pod `argocd-repo-server` (cette variable fait référence à `timeout.reconciliation` dans la configmap `argocd-cm`).

```shell hl_lines="1"
kubectl -n argocd describe pods argocd-repo-server-57bdcb5898-g68nv | grep "RECONCILIATION"
  ARGOCD_RECONCILIATION_TIMEOUT:                                <set to the key 'timeout.reconciliation' of config map 'argocd-cm'>                                          Optional: true
```

Ensuite, il faut mettre à jour la configmap `argocd-cm` pour ajuster la valeur de `timeout.reconciliation`:

```shell hl_lines="1"
kubectl -n argocd patch configmap argocd-cm -p '{"data": {"timeout.reconciliation": "3h"}}'
kubectl -n argocd rollout restart deployment argocd-repo-server
```

Cela permettra de rafraîchir le dépôt Git toutes les 3 heures. Si la réconciliation automatique est activée et qu’il n’y a pas de fenêtre de synchronisation en cours, la réconciliation du cluster aura lieu toutes les 3 heures.

---

## Argo Workflows
Kubernetes-native workflow engine supporting DAG and step-based workflows.

## Argo Events
Event based dependency management for Kubernetes.

## Argo Rollouts
Advanced Kubernetes deployment strategies such as Canary and Blue-Green made easy.

<div class="admonition note">
  <p class="admonition-title">Crossplane Docs</p>

```embed
url: https://argoproj.github.io/
```

```embed
url: https://argo-workflows.readthedocs.io/en/latest/
```

```embed
url: https://argo-cd.readthedocs.io/en/stable/
```

```embed
url: https://argoproj.github.io/argo-rollouts/
```

```embed
url: https://argoproj.github.io/argo-events/
```

```embed
url: https://training.linuxfoundation.org/certification/certified-argo-project-associate-capa/
```
</div>