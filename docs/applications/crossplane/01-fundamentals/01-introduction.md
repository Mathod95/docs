---
title: Introduction
date: 22-03-26
status: draft
categories:
  - Crossplane
tags:
  - Crossplane
source:
  - https://docs.crossplane.io/v2.2/
---

## Qu'est-ce que Crossplane ?

Crossplane est un projet open source hébergé par la Cloud Native Computing Foundation (CNCF) et principalement développé par Upbound. C'est un framework de control plane pour le platform engineering : il permet de construire des control planes pour gérer des logiciels cloud native, en vous laissant concevoir les APIs et abstractions que vos utilisateurs emploient pour interagir avec vos control planes.

Pour cela, Crossplane étend Kubernetes avec les capacités suivantes :

- Des Custom Resource Definitions (CRDs) qui permettent de provisionner et gérer les ressources d'infrastructure (AWS, GCP, Azure, etc.) comme des objets Kubernetes natifs, via `kubectl` ou tout outil GitOps
- Des controllers chargés de réconcilier en continu l'état réel de l'infrastructure avec l'état déclaré (drift detection)
- Une gestion déclarative du cycle de vie complet des ressources au travers de manifestes YAML (création, mise à jour, suppression)
- Des Compositions et XRDs permettant d'abstraire et de composer plusieurs ressources en une API interne personnalisée, offrant du self-service aux équipes
- Une intégration native avec l'écosystème Kubernetes (ArgoCD, Kyverno, etc.), permettant de gérer l'infrastructure avec les mêmes workflows GitOps que les applications



!!! note
    ## What is Crossplane?
    Crossplane is an open-source CNCF project that extends Kubernetes to orchestrate anything. It allows you to:

    - Manage cloud resources using Kubernetes-native tools and APIs
    - Define infrastructure declaratively using YAML manifests
    - Create platform abstractions for self-service infrastructure provisioning
    - Unify multi-cloud infrastructure management under a single control plane

    ## Why Use Crossplane?
    Traditional infrastructure management often involves:

    - Multiple tools for different cloud providers
    - Complex scripts and automation
    - Separate management planes for applications and infrastructure

    Crossplane solves these challenges by:

    - Treating infrastructure as Kubernetes custom resources
    - Providing a consistent API across cloud providers
    - Enabling GitOps workflows for infrastructure
    - Allowing developers to provision infrastructure without direct cloud access




---

### Crossplane components
#### Composition

#### Managed Resources

Les **Managed Resources (MRs)** sont des Kubernetes custom resources prêtes à l'emploi. Chaque MR représente une ressource réelle dans le cloud ou chez un fournisseur de service externe — par exemple, une MR `RDSInstance` représente une instance AWS RDS réelle.

---

Crossplane dispose d'une bibliothèque étendue de MRs couvrant la quasi-totalité des cloud providers et des logiciels cloud native. **Tu n'as donc pas à écrire de controller** si tu veux gérer des ressources hors de ton cluster Kubernetes via une custom resource : il en existe déjà une.

Caractéristiques :

- Mapping 1:1 avec la ressource externe correspondante
- **Namespaced par défaut** depuis Crossplane V2
- Gestion complète du cycle de vie (création, mise à jour, suppression)
- Le `status` reflète l'état réel de la ressource distante

### Structure d'une Managed Resource

```yaml
apiVersion: <provider-api-group>/<version>
kind: <ResourceType>
metadata:
  name: <resource-name>
spec:
  forProvider:
    # Configuration spécifique au provider
  providerConfigRef:
    name: <provider-config-name>
status:
  conditions:
    # État de santé de la ressource
  atProvider:
    # Champs de statut retournés par le provider
```

**Exemple : Bucket S3**

```yaml linenums="1" title="bucket.yaml"
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  name: my-app-bucket
spec:
  forProvider:
    region: us-east-1
  providerConfigRef:
    name: aws-config
```

Après création, le controller réconcilie l'état réel et met à jour le `status` :

```yaml
status:
  conditions:
  - type: Ready
    status: "True"
  - type: Synced
    status: "True"
  atProvider:
    arn: arn:aws:s3:::my-app-bucket
    region: us-east-1
```

---

#### Operations
#### Package manager



## Providers




---

## Get Started



---

### Get Started With Composition
### Get Started With Managed Resources
### Get Started With Operations