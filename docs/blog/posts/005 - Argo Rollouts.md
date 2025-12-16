---
title: Argo Rollouts
date: 2025-12-03
draft: true
categories:
  - Argo Rollouts
tags:
  - Argo Rollouts
  - Lab
---


## Introduction

Versions déployées lors de la rédaction de cet article:




<!-- more -->

```bash title="Structure de base du wrapper"
argo-rollouts/
├── Chart.yaml
├── values.yaml
├── README.md
└── templates/
    ├── _helpers.tpl
    ├── service.yaml
    ├── servicemonitor.yaml
    ├── network-policy.yaml
    ├── pod-disruption-budget.yaml
    └── priority-class.yaml
```

```shell hl_lines="1" title="Ajouter le repository Helm"
helm repo add argo https://argoproj.github.io/argo-helm
"argo" has been added to your repositories
```

```bash hl_lines="1" title="Mettre à jour les repositories"
helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "argo" chart repository
Update Complete. ⎈Happy Helming!⎈
```

!!! Tip "VERSION"

    ```bash hl_lines="1" title="Voir la dernière version"
    helm search repo argo/argo-rollouts
    NAME                    CHART VERSION   APP VERSION     DESCRIPTION
    argo/argo-rollouts      2.40.5          v1.8.3          A Helm chart for Argo Rollouts
    ```

    ??? tip "USEFUL COMMANDS"

        ```bash hl_lines="1" title="Lister toutes les versions disponibles"
        helm search repo argo/argo-rollouts --versions
        NAME                    CHART VERSION   APP VERSION     DESCRIPTION
        argo/argo-rollouts      2.40.5          v1.8.3          A Helm chart for Argo Rollouts
        argo/argo-rollouts      2.40.4          v1.8.3          A Helm chart for Argo Rollouts
        argo/argo-rollouts      2.40.3          v1.8.3          A Helm chart for Argo Rollouts
        ... Omis par souci de brièveté
        ```

!!! info "CHART"

    ```bash hl_lines="1" title="Voir la Chart"
    helm show chart argo/argo-rollouts
    ```

    ??? quote "OUTPUT"

        ```yaml linenums="1" title="Chart.yaml"
        annotations:
          artifacthub.io/changes: |
            - kind: changed
              description: use named port for service
          artifacthub.io/signKey: |
            fingerprint: 2B8F22F57260EFA67BE1C5824B11F800CD9D2252
            url: https://argoproj.github.io/argo-helm/pgp_keys.asc
        apiVersion: v2
        appVersion: v1.8.3
        description: A Helm chart for Argo Rollouts
        home: https://github.com/argoproj/argo-helm
        icon: https://argoproj.github.io/argo-rollouts/assets/logo.png
        keywords:
        - argoproj
        - argo-rollouts
        maintainers:
        - name: argoproj
          url: https://argoproj.github.io/
        name: argo-rollouts
        sources:
        - https://github.com/argoproj/argo-rollouts
        version: 2.40.5
        ```

!!! info "VALUES"

    ```bash hl_lines="1" title="Voir les values par défaut"
    helm show values argo/argo-rollouts
    ```

    ??? tip "USEFUL COMMANDS"

        ```bash hl_lines="1" title="Lister toutes les versions disponibles"
        helm show values argo/argo-rollouts > values.yaml
        ```
    
    !!! Tip 

        Un `values.yaml` vide applique automatiquement les valeurs par défaut.

        **Surcharge des valeurs Kyverno**

        Si tu veux personnaliser des valeurs Kyverno, tu peux le faire dans ton values.yaml

        ```yaml linenums="1" title="values.yaml"
        kyverno:
          replicaCount: 2
          serviceAccount:
            create: false
        ```

        Helm va fusionner tes valeurs avec les valeurs par défaut de Kyverno.  
        Tout ce qui n’est pas défini reste par défaut
















































![](../../assets/images/argo/argo.svg)

<!-- more -->

## Introduction
Contexte + intérêt du sujet.  
Phrase contenant ton mot-clé principal.

### Objectifs
  - découvrir comment organiser un article dans MkDocs Material
  - utiliser une structure claire et hiérarchique
  - faciliter la lecture grâce à des sections adaptées

### Prérequis
  - Un cluster kind

### Ma configuration
  - **OS :** Deban 13
  - **Kind:** kind v0.30.0 go1.25.4 linux/amd64
  - **Kubectl :** v1.34.2 

---

## Installation d'Argo Rollouts

```shell hl_lines="1 2"
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
namespace/argo-rollouts created
customresourcedefinition.apiextensions.k8s.io/analysisruns.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/analysistemplates.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/clusteranalysistemplates.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/experiments.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/rollouts.argoproj.io created
serviceaccount/argo-rollouts created
clusterrole.rbac.authorization.k8s.io/argo-rollouts created
clusterrole.rbac.authorization.k8s.io/argo-rollouts-aggregate-to-admin created
clusterrole.rbac.authorization.k8s.io/argo-rollouts-aggregate-to-edit created
clusterrole.rbac.authorization.k8s.io/argo-rollouts-aggregate-to-view created
clusterrolebinding.rbac.authorization.k8s.io/argo-rollouts created
configmap/argo-rollouts-config created
secret/argo-rollouts-notification-secret created
service/argo-rollouts-metrics created
deployment.apps/argo-rollouts created
```

## Conclusion

### En rapport avec cet article
### Liens utile

```embed
url: https://argo-cd.readthedocs.io/en/stable/getting_started/
```