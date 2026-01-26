---
title: Démarrer avec Crossplane installation, providers et ressources
date: 2025-12-03
categories:
  - Crossplane
tags:
  - Crossplane
todo: Checker et ajouter un peu plus de resources
sources:
  - https://www.youtube.com/watch?v=jw8mMslpqOI
  - https://docs.crossplane.io/v2.1/guides/upgrade-to-crossplane-v2/
  - https://docs.crossplane.io/v2.1/whats-new/
---

![](../../assets/images/crossplane/crossplane.svg)

Crossplane est une extension Kubernetes qui agit comme un framework de control-plane permettant de gérer des ressources cloud (AWS, GCP, Azure…) directement via des manifestes Kubernetes.
Il transforme votre cluster en une Control Plane capable de provisionner, gérer et standardiser l’infrastructure.

Crossplane fonctionne de manière 100% déclarative, il applique en permanence l’état désiré, détecte les dérives (drift) et corrige automatiquement les écarts entre la configuration déclarée et l’état réel dans le cloud.

!!! Note
    Contrairement à Terraform (exécuté ponctuellement), Crossplane:

    - Réconcilie en continu.  
    - Corrige automatiquement les écarts.  
    - Garantit un état désiré permanent.  

<!-- more -->

## Install Crossplane

### Ajouter le dépôt Helm Crossplane
```shell hl_lines="1"
helm repo add crossplane-stable https://charts.crossplane.io/stable
"crossplane-stable" has been added to your repositories
```

```shell hl_lines="1"
helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "crossplane-stable" chart repository
Update Complete. ⎈Happy Helming!⎈
```

### Vérifier la disponibilité du chart Crossplane
```shell hl_lines="1"
helm search repo crossplane
NAME                            CHART VERSION   APP VERSION     DESCRIPTION
crossplane-stable/crossplane    2.1.1           2.1.1           Crossplane is an open source Kubernetes add-on ...
```

!!! Tips
    Vérifiez les changements appliqués au cluster sans installer Crossplane grâce à:
    ```shell hl_lines="1"
    helm install crossplane crossplane-stable/crossplane --namespace crossplane-system --create-namespace --dry-run=client --debug
    ```


### Installer Crossplane
```shell hl_lines="1"
helm install crossplane crossplane-stable/crossplane --namespace crossplane-system --create-namespace
NAME: crossplane
LAST DEPLOYED: Sun Nov 16 19:22:29 2025
NAMESPACE: crossplane-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Release: crossplane

Chart Name: crossplane
Chart Description: Crossplane is an open source Kubernetes add-on that enables platform teams to assemble infrastructure from multiple vendors, and expose higher level self-service APIs for application teams to consume.
Chart Version: 2.1.1
Chart Application Version: 2.1.1

Kube Version: v1.34.0
```

### Vérifier les ressources installées
#### Pods Crossplane

```shell hl_lines="1"
kubectl get pods -n crossplane-system
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-6896f6fbff-rt7fz                1/1     Running   0          2m19s
crossplane-rbac-manager-65f6d66c76-tcm5r   1/1     Running   0          2m19s
```

#### CRDs Crossplane

Crossplane installe de nombreuses CRDs nécessaires au fonctionnement du Control Plane:

- Provider (pkg.crossplane.io)
- Composition & XRD (apiextensions.crossplane.io)
- Usage policies
- Fonctions, configurations, packages…

```shell hl_lines="1"
kubectl get crds | grep crossplane
clusterusages.protection.crossplane.io                          2025-11-16T18:22:34Z
compositeresourcedefinitions.apiextensions.crossplane.io        2025-11-16T18:22:34Z
compositionrevisions.apiextensions.crossplane.io                2025-11-16T18:22:34Z
compositions.apiextensions.crossplane.io                        2025-11-16T18:22:34Z
configurationrevisions.pkg.crossplane.io                        2025-11-16T18:22:34Z
configurations.pkg.crossplane.io                                2025-11-16T18:22:34Z
cronoperations.ops.crossplane.io                                2025-11-16T18:22:34Z
deploymentruntimeconfigs.pkg.crossplane.io                      2025-11-16T18:22:34Z
environmentconfigs.apiextensions.crossplane.io                  2025-11-16T18:22:34Z
functionrevisions.pkg.crossplane.io                             2025-11-16T18:22:34Z
functions.pkg.crossplane.io                                     2025-11-16T18:22:34Z
imageconfigs.pkg.crossplane.io                                  2025-11-16T18:22:34Z
locks.pkg.crossplane.io                                         2025-11-16T18:22:34Z
managedresourceactivationpolicies.apiextensions.crossplane.io   2025-11-16T18:22:34Z
managedresourcedefinitions.apiextensions.crossplane.io          2025-11-16T18:22:34Z
operations.ops.crossplane.io                                    2025-11-16T18:22:34Z
providerrevisions.pkg.crossplane.io                             2025-11-16T18:22:34Z
providers.pkg.crossplane.io                                     2025-11-16T18:22:34Z
usages.apiextensions.crossplane.io                              2025-11-16T18:22:34Z
usages.protection.crossplane.io                                 2025-11-16T18:22:34Z
watchoperations.ops.crossplane.io                               2025-11-16T18:22:34Z
```

---

## Installer des Providers
Les providers permettent à Crossplane d'interagir avec des API externes (AWS, GCP, Azure, GitHub…).
Chaque provider fonctionne comme un plugin isolé dans son propre pod, ce qui améliore :

- La sécurité,
- La stabilité du control plane,
- La possibilité de mettre à jour un provider indépendamment du reste.

### Exemple : provider AWS S3
```yaml linenums="1" title="provider-aws-s3.yaml"
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: upbound-provider-aws-s3
spec:
  package: xpkg.upbound.io/upbound/provider-aws-s3:v2.2.0
```

Apply the providers for the resources IAM

```shell hl_lines="1"
kubectl apply -f provider-aws-s3.yaml
provider.pkg.crossplane.io/upbound-provider-aws-s3 created
```

### Vérifier l'état des providers
```shell hl_lines="1"
kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
upbound-provider-aws-s3       True        True      xpkg.upbound.io/upbound/provider-aws-s3:v2.2.0       2m30s
upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v2.2.0   2m25s
```

!!! info 
    Tous les providers AWS dépendent automatiquement de provider-family-aws, installé automatiquement lors de l'installation de n'importe quelle provider-aws-*.

### Vérifier les pods associés
```shell hl_lines="1"
kubectl get pods -n crossplane-system
NAME                                                        READY   STATUS    RESTARTS   AGE
crossplane-6896f6fbff-sn2x8                                 1/1     Running   0          12m
crossplane-rbac-manager-65f6d66c76-76ffs                    1/1     Running   0          12m
upbound-provider-aws-s3-dd62e217befa-85fffd899-qjpzj        1/1     Running   0          4m23s
upbound-provider-family-aws-0e8a4558ea96-6bff6ccb65-f2x5s   1/1     Running   0          4m24s
```

---

## Configurer l'accès AWS
Pour que Crossplane interagisse avec AWS, il doit disposer d'identifiants valides.

Les ProviderConfigs peuvent utiliser IRSA, STS, Web Identity ou des credentials statiques
La doc officielle en production d'éviter les credentials statiques et de préférer:

- IAM Roles for Service Accounts (IRSA)
- AssumeRole
- AWS WebIdentity

### Créer un fichier credentials AWS
```shell title="aws-credentials.txt" linenums="1"
[default]
aws_access_key_id = XXXXXXXXXXXXXXXXXXXX
aws_secret_access_key = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Créer le secret Kubernetes
```shell hl_lines="1"
kubectl create secret generic aws-secret -n crossplane-system --from-file=creds=./aws-credentials.txt
```

### Définir la configuration du provider

```yaml linenums="1" title="provider-config.yaml"
apiVersion: aws.m.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
        namespace: crossplane-system
        name: aws-secret
        key: creds
```

---

## Créer une ressource AWS
Voici un exemple de bucket S3 géré par Crossplane:

```yaml linenums="1" title="bucket.yaml"
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: app1-production-mathod-bucket
  namespace: crossplane-system
spec:
  forProvider:
    region: eu-west-3
      tags:
        company: mathod
        project: app1
        environment: production
    providerConfigRef:
      name: default
      kind: ProviderConfig
```

```yaml hl_lines="1"
kubectl apply -f bucket.yaml
```

Crossplane crée, configure et maintient la ressource AWS comme une ressource Kubernetes standard.

---

```embed
url: https://docs.crossplane.io/latest/get-started/install/
```

```embed
url: https://marketplace.upbound.io/providers/upbound/provider-family-aws/latest
```