---
title: Managed Resource Activation Policies
date: 22-03-26
categories:
  - Crossplane
tags:
  - Crossplane
  - MRAP
  - MRD
source:
  - https://docs.crossplane.io/v2.2/managed-resources/managed-resource-activation-policies/
  - https://medium.com/@chaima.belhedi/from-monolithic-providers-to-provider-families-to-mrap-testing-crossplane-v2-673e761d1135
---

!!! warning
    Il s’agit d’une fonctionnalité alpha introduite dans la v2 de Crossplane.  
    Crossplane peut modifier ou supprimer cette fonctionnalité à tout moment.  
    [Feature Lifecycle](https://docs.crossplane.io/v2.2/learn/feature-lifecycle/){target=_blank}

## Introduction

Il y a quelques années, utiliser le **provider AWS** dans Crossplane était lourd. Installer le `provider-aws` monolithique créait **des centaines de CRD**, même si vous n’aviez besoin que de quelques resources comme S3. Cela pouvait ralentir ou rendre le control plane non réactif, et la gestion des mises à jour était compliquée.

Pour résoudre ce problème, la communauté Crossplane a introduit les **Provider Families**. Au lieu d’un gros provider unique, AWS est maintenant divisé en **sub-providers** plus petits comme `provider-aws-s3` et `provider-aws-ec2`. Tous les sub-providers partagent un **family provider** (`provider-family-aws`) pour la configuration commune, comme les credentials. Les avantages des Provider Families sont clairs :

- **Fewer CRDs:** Installer seulement ce dont vous avez besoin.
- **Better performance:** Les controllers se concentrent sur moins de resources.
- **Easier upgrades:** Mettre à jour un sub-provider sans toucher aux autres.

Même avec les **Provider Families**, un défi subsiste. Les providers Crossplane modernes peuvent embarquer des dizaines, voire des centaines de resources managées, mais la plupart des utilisateurs n’en utilisent qu’une infime partie. Installer un provider signifiait récupérer toutes les ressources managées qu’il supporte, ce qui consommait inutilement des ressources du cluster.

Exemple, pour utiliser seulement la resource `vpcs.ec2.aws.upbound.io`, il fallait installer **tous les CRD du provider EC2** (102 dans la version 1, ou **204 CRD** avec un provider EC2 v2(modern)). Cela ajoutait une charge inutile au control plane et augmentait la complexité du cluster, même avec les Provider Families.

## ManagedResourceActivationPolicy

**Crossplane** dans sa `v2` introduit la feature `ManagedResourceActivationPolicy` (**MRAP**) qui contrôle quelles `ManagedResourceDefinitions` (**MRD**) deviennent actives dans ton cluster.

Les **MRAP** résolvent les problèmes cités précédemment en permettant une activation sélective des `ManagedResourceDefinitions` basée sur des patterns, ce qui permet de choisir précisément quelles resources du provider activer.

## Comment fonctionnent les MRAP

Les **MRAP** contiennent des **patterns d’activation** qui correspondent aux noms des `ManagedResourceDefinition`.  
Lorsque tu crées ou mets à jour un **MRAP**, Crossplane va:

1. Liste toutes les **MRDs** dans le cluster
1. Compare les noms des **MRDs** avec les patterns d’activation
1. Active les **MRDs** correspondantes en définissant leur `state` sur `active`
1. Mettre à jour le statut du **MRAP** avec la liste des ressources activées

**Example MRAP**

```yaml linenums="1" title="mrap-example.yaml"
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: mrap-aws
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io
  - instances.rds.aws.m.crossplane.io
  - "*.ec2.aws.m.crossplane.io"
```

Quand tu appliques ce **MRAP**, Crossplane active:

- **MRD:** `bucket` du `provider-aws-s3`
- **MRD:** `instance` du `provider-aws-rds`
- **MRDs:** `*` du `provider-aws-ec2`

### Principales fonctionnalités

- **Pattern-based matching:** Activer des groupes de resources à l’aide de wildcards, pour plus de flexibilité.
- **Activation sélective:** N’activer que les resources dont vous avez réellement besoin, par exemple les S3 buckets, les RDS instances ou les EC2 VPCs.
- **Multiple policy support:** Plusieurs **MRAP** peuvent coexister et activer différents ensembles de resources.
- **Status tracking:** Suivre quelles resources sont actives ou inactives pour toujours connaître l’état du cluster.
- **Automatic activation:** Les nouvelles **MRD** correspondant aux patterns existants s’activent automatiquement.

---

## Workshop

Pour voir les **MRAP** en action, exécutons un test simple sur un cluster **Kind** local. Dans cet exemple, nous allons installer le `provider-aws-ec2` et observer comment **MRAP** influencent sur l’utilisation mémoire et le nombre de **CRDs**.


### 1. Créer un cluster Kind

```bash
kind create cluster --name crossplane-mrap
```

### 2. Installer Crossplane

```bash hl_lines="1 4 9-12 30" linenums="1"
helm repo add crossplane-stable https://charts.crossplane.io/stable
"crossplane-stable" has been added to your repositories

helm repo update crossplane-stable
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "crossplane-stable" chart repository
Update Complete. ⎈Happy Helming!⎈

helm install crossplane crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace \
--set "provider.defaultActivations={}"
NAME: crossplane
LAST DEPLOYED: Wed Mar 25 01:02:35 2026
NAMESPACE: crossplane-system
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
Release: crossplane

Chart Name: crossplane
Chart Description: Crossplane is an open source Kubernetes add-on that enables platform teams to assemble infrastructure from multiple vendors, and expose higher level self-service APIs for application teams to consume.
Chart Version: 2.2.0
Chart Application Version: 2.2.0

Kube Version: v1.35.0

kubectl get pods -n crossplane-system
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-5cb76b766d-zjc8s                1/1     Running   0          36s
crossplane-rbac-manager-74494cb9bf-wmvj2   1/1     Running   0          36s
```

!!! info

    Par défaut, Crossplane active **toutes les managed resources (MRDs)** lorsqu’un provider est installé. Ici, nous définissons `provider.defaultActivations={}` pour **désactiver les activations par défaut**, afin de pouvoir créer notre propre **MRAP** et activer uniquement les resources nécessaires.

### 3. Installer Metrics Server

Les clusters Kind n’incluent pas Metrics Server par défaut, ce qui est nécessaire pour utiliser `kubectl top`. Installe-le avec :

```bash hl_lines="1-3"
wget -qO- https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml \
| sed '/- --kubelet-preferred-address-types/a\        - --kubelet-insecure-tls' \
| kubectl apply -f -
```

### 4. Installer le provider EC2

Créer un fichier YAML pour le provider :

```yaml linenums="1" title="provider-aws-ec2.yaml"
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: upbound-provider-aws-ec2
spec:
  package: xpkg.upbound.io/upbound/provider-aws-ec2:v2.5.0
```

Appliquer le manifest :

```bash hl_lines="1"
kubectl apply -f provider-aws-ec2.yaml
```

Lors de l’installation de ce provider, le **Provider Family** `upbound-provider-family-aws` est installé automatiquement. Il n’est donc pas nécessaire de l’installer manuellement.

```bash hl_lines="1"
kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
upbound-provider-aws-ec2      True        True      xpkg.upbound.io/upbound/provider-aws-ec2:v2.5.0      60s
upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v2.5.0   49s
```

### 5. Observer les CRDs

Après l’installation du `provider-aws-ec2`, vérifions **le nombre de CRDs installés** et **l’utilisation mémoire** de l’API server Kubernetes :

```bash hl_lines="1"
kubectl get mrds | grep ec2 | wc -l
204
kubectl get crds | grep ec2 | wc -l
0
```

>0 **CRDs** pour 204 **MRDs** car nous avons le flag `--set "provider.defaultActivations={}"`

```bash hl_lines="1"
kubectl top pod -A
NAMESPACE            NAME                                                       CPU(cores)   MEMORY(bytes)
crossplane-system    crossplane-554f75b79b-22vv5                                2m           76Mi
crossplane-system    crossplane-rbac-manager-74494cb9bf-fp25s                   1m           15Mi
crossplane-system    upbound-provider-aws-ec2-956e2688224c-6d994cd897-dsj8s     1m           297Mi
crossplane-system    upbound-provider-family-aws-604659292671-6d946748b-2ls9p   1m           262Mi
kube-system          coredns-7d764666f9-c2q29                                   2m           13Mi
kube-system          coredns-7d764666f9-tpcsw                                   2m           13Mi
kube-system          etcd-crossplane-mrap-control-plane                         23m          78Mi
kube-system          kindnet-sgqch                                              1m           10Mi
kube-system          kube-apiserver-crossplane-mrap-control-plane               39m          428Mi
kube-system          kube-controller-manager-crossplane-mrap-control-plane      15m          59Mi
kube-system          kube-proxy-bdpwk                                           1m           14Mi
kube-system          kube-scheduler-crossplane-mrap-control-plane               6m           23Mi
kube-system          metrics-server-c7b5cbc45-klk9r                             2m           21Mi
local-path-storage   local-path-provisioner-67b8995b4b-fsk5j                    1m           7Mi
```

### 6. MRAP minimal

Maintenant, nous allons créer un **ManagedResourceActivationPolicy (MRAP)** pour activer uniquement les resources nécessaires. Cela permet de réduire la charge du control plane.

```yaml linenums="1" title="mrap.yaml"
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: minimal-ec2
spec:
  activate:
  - vpcs.ec2.aws.m.upbound.io
```

Appliquer le **MRAP**:

```bash hl_lines="1"
kubectl apply -f mrap.yaml
managedresourceactivationpolicy.apiextensions.crossplane.io/minimal-ec2 created
```

Vérifions à présent:

```bash hl_lines="1 3"
kubectl get crds | grep ec2 | wc -l
1
kubectl get crds | awk 'NR==1 || /ec2/'
NAME                        CREATED AT
vpcs.ec2.aws.m.upbound.io   2026-03-25T00:58:48Z
```

```bash hl_lines="1 3-6"
kubectl top pod -A
NAMESPACE            NAME                                                        CPU(cores)   MEMORY(bytes)
crossplane-system    crossplane-554f75b79b-7krfs                                 2m           66Mi
crossplane-system    crossplane-rbac-manager-74494cb9bf-gtv8r                    1m           14Mi
crossplane-system    upbound-provider-aws-ec2-956e2688224c-7d64b96b7-jrwtm       4m           171Mi
crossplane-system    upbound-provider-family-aws-604659292671-6c9b84b485-w5tbm   3m           169Mi
kube-system          coredns-7d764666f9-b2h7l                                    2m           13Mi
kube-system          coredns-7d764666f9-n628f                                    2m           13Mi
kube-system          etcd-crossplane-mrap-control-plane                          24m          86Mi
kube-system          kindnet-g4sl8                                               1m           10Mi
kube-system          kube-apiserver-crossplane-mrap-control-plane                40m          427Mi
kube-system          kube-controller-manager-crossplane-mrap-control-plane       14m          56Mi
kube-system          kube-proxy-jn827                                            1m           13Mi
kube-system          kube-scheduler-crossplane-mrap-control-plane                7m           24Mi
kube-system          metrics-server-c7b5cbc45-wlxjj                              3m           20Mi
local-path-storage   local-path-provisioner-67b8995b4b-vw7s6                     1m           8Mi
```

### 7. Before/After MRAP

Nous allons modifier et appliquer notre **MRAP** pour activer l'ensemble des resources modern que fournit le `provider-aws-ec2` afin d'observer les changements.

```yaml linenums="1" hl_lines="6" title="mrap.yaml"
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: minimal-ec2
spec:
  activate:
  - "*.ec2.aws.m.upbound.io"
```

!!! warning
    Activer tous les **CRDs** via un manifest **MRAP** entraîne l’activation de l’ensemble des **ManagedResourceDefinitions**, mais toute modification ultérieure du **MRAP** ne désactivera ni ne supprimera les **CRDs** déjà créés, celles-ci restant persistantes dans le cluster.

```bash hl_lines="1"
kubectl apply -f mrap.yaml
managedresourceactivationpolicy.apiextensions.crossplane.io/minimal-ec2 configured
```

**Observons:**

```bash hl_lines="1 3 5"
kubectl get mrds | grep ec2 | wc -l
204
kubectl get crds | grep ec2 | wc -l
102
kubectl top pod -A
NAMESPACE            NAME                                                        CPU(cores)   MEMORY(bytes)
crossplane-system    crossplane-554f75b79b-7krfs                                 2m           142Mi
crossplane-system    crossplane-rbac-manager-74494cb9bf-gtv8r                    1m           14Mi
crossplane-system    upbound-provider-aws-ec2-956e2688224c-7d64b96b7-jrwtm       21m          263Mi
crossplane-system    upbound-provider-family-aws-604659292671-6c9b84b485-w5tbm   1m           219Mi
kube-system          coredns-7d764666f9-b2h7l                                    2m           13Mi
kube-system          coredns-7d764666f9-n628f                                    2m           12Mi
kube-system          etcd-crossplane-mrap-control-plane                          31m          130Mi
kube-system          kindnet-g4sl8                                               1m           12Mi
kube-system          kube-apiserver-crossplane-mrap-control-plane                57m          886Mi
kube-system          kube-controller-manager-crossplane-mrap-control-plane       15m          68Mi
kube-system          kube-proxy-jn827                                            1m           15Mi
kube-system          kube-scheduler-crossplane-mrap-control-plane                6m           23Mi
kube-system          metrics-server-c7b5cbc45-wlxjj                              3m           20Mi
local-path-storage   local-path-provisioner-67b8995b4b-vw7s6                     1m           8Mi
```

### Récapitulatifs

|                  | Sans MRAP | MRAP Minimal | MRAP Modern resources | Default |
|------------------|:---------:|:------------:|:---------------------:|:-------:|
| MRDs             | 204       | 204          | 204                   | 204     |
| CRDs             | 0         | 1            | 102                   | 204     |
| **MEMORY**       |           |              |                       |         |
| `kube-apiserver` | 428Mi     | 432Mi        | 886Mi                 | 1218Mi  |
| `crossplane `    | 76Mi      | 76Mi         | 142Mi                 | 236Mi   |
| Provider EC2     | 297Mi     | 164Mi        | 263Mi                 | 353Mi   |
| Provider Family  | 262Mi     | 165Mi        | 219Mi                 | 237Mi   |

Comme le montre ce tableau, l’utilisation memory diminue drastiquement entre une installation d’un provider par défaut et une installation où un **MRAP** est utilisé pour n’activer qu’une partie des CRDs.  
Cela montre comment les **MRAP** améliorent l’efficacité: les controllers se concentrent uniquement sur les resources nécessaires, ce qui rend le cluster plus performant et plus simple à gérer.

!!! info
    Il y a également un gain **CPU**, mais beaucoup moins impactant que le gain en **MEMORY**.