---
title: Usage
date: 25-03-26
categories:
  - Crossplane
tags:
  - Crossplane
  - Usage
source:
  - https://docs.crossplane.io/v2.2/managed-resources/usages/
---

!!! warning
    Il s’agit d’une fonctionnalité **Beta** introduite dans la v1.19. de Crossplane.  
    Les features en **Beta** sont à activer par défaut lors de l'installation de Crossplane.  
    Pour plus d’informations, consultez [Feature Lifecycle](https://docs.crossplane.io/v2.2/learn/feature-lifecycle/){target=_blank}

### **Usages**

Un **`Usage`** indique qu’une ressource est utilisée. Il y a deux cas d’usage principaux pour les **Usages** :

1. Protéger une ressource contre une suppression accidentelle.
2. Assurer l’ordre de suppression en garantissant qu’une ressource ne soit pas supprimée avant ses ressources dépendantes. ([GitHub][1])

Voir la section *Usage for Deletion Protection* pour le premier cas d’usage et la section *Usage for Deletion Ordering* pour le second. ([GitHub][1])

---

## **Activer les usages**

Les **Usages** sont une fonctionnalité beta. Crossplane active les fonctionnalités beta par défaut.
Désactive la prise en charge des **Usages** en modifiant la configuration du pod Crossplane et en ajoutant l’argument `--enable-usages=false`. ([GitHub][1])

Exemple :

```yaml
$ kubectl edit deployment crossplane --namespace crossplane-system
apiVersion: apps/v1
kind: Deployment
spec:
  # ...
  template:
    spec:
      containers:
      - args:
        - core
        - start
        - --enable-usages=false
```

Le guide d’installation de Crossplane décrit comment activer/désactiver des *feature flags* comme `--enable-usages` avec Helm. ([GitHub][1])

---

## **Créer un Usage**

Un `Usage` a un champ obligatoire **of** pour définir la ressource utilisée ou protégée.
Le champ **reason** définit la raison de la protection et le champ **by** définit la ressource qui l’utilise.
Les deux champs sont optionnels, mais au moins **l’un des deux doit être fourni**. ([GitHub][1])

---

### **Usage pour la protection contre la suppression**

L’exemple suivant empêche la suppression de la ressource `my-database` en rejetant toute demande de suppression en raison de la raison définie.

```yaml
apiVersion: protection.crossplane.io/v1beta1
kind: Usage
metadata:
  namespace: default
  name: protect-production-database
spec:
  of:
    apiVersion: rds.aws.m.upbound.io/v1beta1
    kind: Instance
    resourceRef:
      name: my-database
  reason: "Production Database - should never be deleted!"
```

([GitHub][1])

---

### **Usage pour l’ordre de suppression**

L’exemple suivant empêche la suppression de la ressource `my-cluster` en rejetant toute demande de suppression **avant** la suppression de la ressource `my-prometheus-chart`.

```yaml
apiVersion: protection.crossplane.io/v1beta1
kind: Usage
metadata:
  namespace: default
  name: release-uses-cluster
spec:
  of:
    apiVersion: eks.m.upbound.io/v1beta1
    kind: Cluster
    resourceRef:
      name: my-cluster
  by:
    apiVersion: helm.m.crossplane.io/v1beta1
    kind: Release
    resourceRef:
      name: my-prometheus-chart
```

([GitHub][1])

---

## **Utiliser des sélecteurs avec les Usages**

Les **Usages** peuvent utiliser des **selectors** pour définir la ressource utilisée (`of`) ou celle qui l’utilise (`by`).
Cela permet d'utiliser des **labels** ou des références de contrôleur (**matchControllerRef**) pour définir la ressource au lieu de fournir directement le nom de la ressource. ([GitHub][1])

Exemple :

```yaml
apiVersion: protection.crossplane.io/v1beta1
kind: Usage
metadata:
  namespace: default
  name: release-uses-cluster
spec:
  of:
    apiVersion: eks.m.upbound.io/v1beta1
    kind: Cluster
    resourceSelector:
      matchControllerRef: false  # valeur par défaut, peut être omise
      matchLabels:
        foo: bar
  by:
    apiVersion: helm.m.crossplane.io/v1beta1
    kind: Release
    resourceSelector:
      matchLabels:
        baz: qux
```

([GitHub][1])

Après que le contrôleur **Usage** ait résolu les sélecteurs, il enregistre le nom de la ressource résolue dans le champ `resourceRef.name`. ([GitHub][1])

L’exemple ci‑dessous montre l’objet **Usage** après résolution des sélecteurs. Les résolveurs de sélecteurs ne s’exécutent qu’une seule fois. Si plusieurs ressources correspondent, une ressource est sélectionnée au hasard parmi celles qui correspondent.

```yaml
apiVersion: protection.crossplane.io/v1beta1
kind: Usage
metadata:
  namespace: default
  name: release-uses-cluster
spec:
  of:
    apiVersion: eks.m.upbound.io/v1beta1
    kind: Cluster
    resourceRef:
      name: my-cluster
    resourceSelector:
      matchLabels: foo: bar
  by:
    apiVersion: helm.m.crossplane.io/v1beta1
    kind: Release
    resourceRef:
      name: my-cluster
    resourceSelector:
      matchLabels: baz: qux
```

([GitHub][1])

---

### **Rejouer une suppression bloquée**

Par défaut, la suppression d’une ressource *Usage* ne déclenche pas la suppression de la ressource utilisée même si cette suppression avait été bloquée par le *Usage*.
La lecture de la suppression bloquée est possible en définissant `replayDeletion: true`.

```yaml
apiVersion: protection.crossplane.io/v1beta1
kind: Usage
metadata:
  namespace: default
  name: release-uses-cluster
spec:
  replayDeletion: true
  of:
    apiVersion: eks.m.upbound.io/v1beta1
    kind: Cluster
    resourceRef:
      name: my-cluster
  by:
    apiVersion: helm.m.crossplane.io/v1beta1
    kind: Release
    resourceRef:
      name: my-prometheus-chart
```

Le **replay de suppression** est utile lorsque la ressource utilisée fait partie d’une Composition.
Cette configuration diminue radicalement le temps nécessaire à la suppression de la ressource utilisée, donc de la Composition qui la possède, en rejouant immédiatement la suppression de la ressource utilisée dès que la ressource utilisatrice disparaît — au lieu d’attendre les longs délais d’exponential backoff du garbage collector Kubernetes. ([GitHub][1])

---

## **Usage dans une Composition**

Un cas d’utilisation typique pour les **Usages** est de définir un **ordre de suppression** entre les ressources à l’intérieur d’une *Composition*.
Les *Usages* supportent *matchControllerRef* dans les sélecteurs pour garantir que la ressource correspondante se trouve dans la même ressource composite, de la même manière que les références inter‑ressources classique (*cross‑resource referencing*).
Lorsque plusieurs ressources du même type existent dans une Composition, la ressource **Usage** doit identifier de façon unique la ressource utilisée ou utilisatrice. Cela peut être accompli en combinant des labels supplémentaires avec `matchControllerRef` et/ou `matchLabels`. ([GitHub][1])

---

## **Usage à travers des namespaces**

Un **Usage** avec `of` et `by` représente une relation d’usage entre deux ressources dans le **même namespace** que le **Usage** par défaut.
Un **Usage** peut représenter une relation d’usage entre une ressource utilisée `of` dans un namespace différent et une ressource utilisatrice `by` dans le namespace du **Usage**.
Pour utiliser une ressource dans un namespace différent, il suffit de spécifier le namespace dans la `resourceRef` correspondante.

Exemple :

```yaml
apiVersion: protection.crossplane.io/v1beta1
kind: Usage
metadata:
  namespace: default
  name: release-uses-cluster
spec:
  of:
    apiVersion: eks.m.upbound.io/v1beta1
    kind: Cluster
    resourceRef:
      namespace: cluster-infra
      name: my-cluster
  by:
    apiVersion: helm.m.crossplane.io/v1beta1
    kind: Release
    resourceRef:
      name: my-prometheus-chart
```

([GitHub][1])

---

## **ClusterUsages**

Utilise un **`ClusterUsage`** pour protéger des ressources *cluster scoped*. Exemple :

```yaml
apiVersion: protection.crossplane.io/v1beta1
kind: ClusterUsage
metadata:
  name: protect-important-crd
spec:
  of:
    apiVersion: apiextensions.k8s.io/v1
    kind: CustomResourceDefinition
    resourceRef:
      name: importantresources.example.crossplane.io
  reason: "Very important CRD - should never be deleted!"
```

([GitHub][1])

---

Si tu veux, je peux aussi **fournir une traduction YAML annotée** ou un **exemple illustratif** plus approfondi expliquant comment utiliser les *Usages* dans un vrai workflow Crossplane.

[1]: https://raw.githubusercontent.com/crossplane/docs/refs/heads/master/content/v2.2/managed-resources/usages.md "raw.githubusercontent.com"
