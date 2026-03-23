---
title: Composite Resource Definitions
weight: 20
description: "Define schemas for composite resources"
---

```yaml linenums="1"
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xbuckets.storage.mathod.io
spec:
  scope: Namespaced
  group: storage.mathod.io
  names:
    kind: XBucket #(1)!
    plural: xbuckets # (2)!
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required:
                - parameters
              properties:
                parameters:
                  type: object
                  required:
                    - region
                    - environment
                  properties:
                    region:
                      type: string
                      description: "Région AWS cible (ex: eu-west-3)"
                    environment:
                      type: string
                      description: "Environnement (production, staging, management)"
                      enum:
                        - production
                        - staging
                        - management
                    versioning:
                      type: boolean
                      description: "Activer le versioning sur le bucket"
                      default: false
                    providerConfigRef:
                      type: string
                      description: "Nom du ProviderConfig à utiliser"
                      default: "default"
            status:
              type: object
              properties:
                bucketName:
                  type: string
                  description: "Nom du bucket S3 créé"
```

1.  test
2.  test

---

Les **CompositeResourceDefinition (XRD)** définissent le schéma d'une API personnalisée (similaires aux [Kubernetes custom resource definitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)). Les utilisateurs créent des **Composite Resources (XR)** en utilisant le schéma d'API défini par une **CompositeResourceDefinition (XRD)**.

## XRD

Créer une **CompositeResourceDefinition (XRD)** consiste à définir :

- Un `group` d'API personnalisé
- Un `name` d'API personnalisé
- Un `schema` et une `version` d'API personnalisés
- Un `scope` (namespaced ou cluster-scoped)

Les **CompositeResourceDefinition (XRD)** créent de nouveaux endpoints d'API dans un cluster Kubernetes.
Créer une nouvelle API nécessite de définir un `group`, un `name` et une `version`

```yaml linenums="1" title="xbucket.yaml"
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xbuckets.storage.mathod.io
spec:
  scope: Namespaced
  group: storage.mathod.io
  names:
    kind: XBucket
    plural: xbuckets
  versions:
    - name: v1alpha1
    # Removed for brevity
```

<!--
```yaml linenums="1" title="xbucket.yaml"
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xbuckets.storage.mathod.io
spec:
  scope: Namespaced
  group: storage.mathod.io
  names:
    kind: XBucket
    plural: xbuckets
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required:
                - parameters
              properties:
                parameters:
                  type: object
                  required:
                    - region
                    - environment
                  properties:
                    region:
                      type: string
                      description: "Région AWS cible (ex: eu-west-3)"
                    environment:
                      type: string
                      description: "Environnement (production, staging, management)"
                      enum:
                        - production
                        - staging
                        - management
                    versioning:
                      type: boolean
                      description: "Activer le versioning sur le bucket"
                      default: false
                    providerConfigRef:
                      type: string
                      description: "Nom du ProviderConfig à utiliser"
                      default: "default"
            status:
              type: object
              properties:
                bucketName:
                  type: string
                  description: "Nom du bucket S3 créé"
```
-->

```bash hl_lines="1"
kubectl apply -f xrd.yaml
compositeresourcedefinition.apiextensions.crossplane.io/xbuckets.storage.mathod.io created
```

```bash hl_lines="1"
kubectl get xrd xbuckets.storage.mathod.io
NAME                         ESTABLISHED   OFFERED   AGE
xbuckets.storage.mathod.io   True                    14m
```

Après avoir appliqué une **CompositeResourceDefinition (XRD)**, Crossplane crée une nouvelle custom resource definition Kubernetes correspondant à l'API définie.

Par exemple, la **CompositeResourceDefinition (XRD)** `xbuckets.storage.mathod.io` crée une custom resource definition `xbuckets.storage.mathod.io`.

```shell hl_lines="1"
kubectl api-resources | awk 'NR==1 || /mathod.io/'
NAME      SHORTNAMES  APIVERSION                  NAMESPACED  KIND
xbuckets              storage.mathod.io/v1alpha1  true        XBucket
```

!!! warning
    Vous ne peux pas changer le `group` ou le `names` d'une **CompositeResourceDefinition (XRD)**. Tu dois la supprimer et la recréer pour changer ces valeurs.

---

### XRD groups
Les groups définissent une collection d'endpoints d'API liés. Le `group` peut être n'importe quelle valeur, mais la convention est de le mapper sur un nom de domaine pleinement qualifié.
Plusieurs CompositeResourceDefinition (XRD) peuvent utiliser le même `group` pour créer une collection logique d'APIs.
Par exemple un group `storage` peut avoir un kind `XBucket`, un kind `XEFS` et un kind `XEBS`

### XRD names
Le champ `names` définit comment référencer cette CompositeResourceDefinition (XRD). Les champs requis sont :

- **kind:** La valeur `kind` à utiliser lors de l'appel de cette API, en [UpperCamelCase](https://kubernetes.io/docs/contribute/style/style-guide/#use-upper-camel-case-for-api-objects). 
- **plural:** Le nom pluriel utilisé pour l'URL de l'API, en minuscule.

!!! Tip
    **Crossplane** recommande de commencer les kinds des XRD avec un `X` pour montrer que c'est une définition d'API Crossplane personnalisée.

!!! warning

    Le `metadata.name` de la CompositeResourceDefinition (XRD) doit être {**plural**}{**.**}{**group**}.
    Par exemple xbuckets.storage.mathod.io correspond au {`plural`=**xbuckets**}{**.**}{`group`=**storage.mathod.io**}.

    ```yaml linenums="1" hl_lines="4 6 9"
    apiVersion: apiextensions.crossplane.io/v2
    kind: CompositeResourceDefinition
    metadata:
      name: xbuckets.storage.mathod.io
    spec:
      group: storage.mathod.io
      names:
        kind: XBucket
        plural: xbuckets
      # Removed for brevity
    ```

### XRD versions
La `version` d'une **CompositeResourceDefinition (XRD)** est similaire au [versioning d'API Kubernetes](https://kubernetes.io/docs/reference/using-api/#api-versioning). La version montre la maturité de l'API et s'incrémente lors de changements, ajouts ou suppressions de champs.

Crossplane recommande de suivre les conventions de versioning Kubernetes :

- **v1alpha1:**: une nouvelle API qui peut changer à tout moment
- **v1beta1:**: une API existante considérée comme stable, les breaking changes sont fortement déconseillés
- **v1:**: une API stable sans breaking changes

#### Schema

Le `schema` définit les noms des paramètres, leurs types et lesquels sont requis ou optionnels.

!!! info
    Tous les `schemas` suivent le [OpenAPIv3 structural schema](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#specifying-a-structural-schema) de Kubernetes.

Dans cet exemple, `region` est un `string` et `versioning` est un `boolean` :

```yaml linenums="1" hl_lines="19-22"
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xbuckets.storage.mathod.io
spec:
  group: storage.mathod.io
  names:
    kind: XBucket
    plural: xbuckets
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string
              environment:
                type: string
              versioning:
                type: boolean
            required:
              - region
              - environment
    # Removed for brevity
```

Un Composite Resource (XR) utilisant cette API référence le `group`/`version` et le `kind`. Le `spec.parameters` contient les paramètres définis :

```yaml linenums="1"
apiVersion: storage.mathod.io/v1alpha1
kind: XBucket
metadata:
  name: bucket-management
spec:
  parameters:
    region: "eu-west-3"
    versioning: true
```

!!! info
    Modifier ou étendre le schéma d'une CompositeResourceDefinition (XRD) nécessite de redémarrer le pod Crossplane pour que les changements prennent effet.

##### Required fields

Par défaut tous les champs d'un schéma sont optionnels. Définir un paramètre comme requis avec l'attribut `required`.

Dans cet exemple la **CompositeResourceDefinition (XRD)** requiert `region` et `environment` mais `versioning` est optionnel :

```yaml linenums="9" hl_lines="17-19"
...
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required:
                - parameters
              properties:
                parameters:
                  type: object
                  required:
                    - region
                    - environment
                  properties:
                    region:
                      type: string
                      description: "Région AWS cible (ex: eu-west-3)"
                    environment:
                      type: string
                      description: "Environnement (production, staging, management)"
                      enum:
                        - production
                        - staging
                        - management
                    versioning:
                      type: boolean
                      description: "Activer le versioning sur le bucket"
                      default: false
...
```

<!--
##### Crossplane reserved fields

Crossplane doesn't allow the following fields in a schema:
* Any field under the object `spec.crossplane`
* Any field under the object `status.crossplane`
* `status.conditions`
-->

#### Serve and reference a schema

Pour utiliser un schéma il doit être `served: true` et `referenceable: true` :

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: xDatabase
    plural: xdatabases
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string
```

Composite resources can use any schema version set as
{{<hover label="served" line="12" >}}served: true{{</hover >}}.
Kubernetes rejects any composite resource using a schema version set as `served:
false`.

{{< hint "tip" >}}
Setting a schema version as `served:false` causes errors for users using an older
schema. This can be an effective way to identify and upgrade users before
deleting the older schema version.
{{< /hint >}}

The {{<hover label="served" line="13" >}}referenceable: true{{</hover>}}
field indicates which version of the schema Compositions use. Only one
version can be `referenceable`.

{{< hint "note" >}}
Changing which version is `referenceable:true` requires [updating the `compositeTypeRef.apiVersion`]({{<ref "./compositions#match-composite-resources" >}})
of any Compositions referencing that XRD.
{{< /hint >}}


#### Multiple schema versions

{{<hint "warning" >}}
Crossplane supports defining multiple `versions`, but the schema of each version
can't change any existing fields, also called "making a breaking change."

Breaking schema changes between versions requires the use of [conversion webhooks](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/#webhook-conversion).

New versions may define new optional parameters, but new required fields are
a "breaking change."

<!-- vale Crossplane.Spelling = NO -->
<!-- ignore to allow for CRDs -->
<!-- don't add to the spelling exceptions to catch when it's used instead of XRD -->
Crossplane XRDs use Kubernetes custom resource definitions for versioning.
Read the Kubernetes documentation on
[versions in CustomResourceDefinitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/)
for more background on versions and breaking changes.
<!-- vale Crossplane.Spelling = YES -->

Crossplane recommends implementing breaking schema changes as brand new XRDs.
{{< /hint >}}

For XRDs, to create a new version of an API add a new
{{<hover label="ver" line="21">}}name{{</hover>}} in the
{{<hover label="ver" line="10">}}versions{{</hover>}}
list.

For example, this XRD version
{{<hover label="ver" line="11">}}v1alpha1{{</hover>}} only has the field
{{<hover label="ver" line="19">}}region{{</hover>}}.

A second version,
{{<hover label="ver" line="21">}}v1{{</hover>}} expands the API to have both
{{<hover label="ver" line="29">}}region{{</hover>}} and
{{<hover label="ver" line="31">}}size{{</hover>}}.

```yaml {label="ver",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: xDatabase
    plural: xdatabases
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string
  - name: v1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string
              size:
                type: string
```

{{<hint "important" >}}

Changing or expanding the XRD schema requires restarting the [Crossplane pod]({{<ref "../guides/pods#crossplane-pod">}}) to take effect.
{{< /hint >}}

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
### XRD scope
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

The {{<hover label="xrdscope" line="6">}}scope{{</hover>}} field determines
whether composite resources created from this XRD exist in a namespace or
at cluster scope.

```yaml {label="xrdscope",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: mydatabases.example.org
spec:
  scope: Namespaced
  # Removed for brevity
```

The scope field supports three values:

* `Namespaced` - **(Default in v2)** - Composite resources exist in a
  namespace and can only compose resources in the same namespace.
* `Cluster` - Composite resources are cluster-scoped and can compose resources
  in any namespace or at cluster scope.
* `LegacyCluster` - Cluster-scoped with support for claims (v1 compatibility
  mode).

{{<hint "note" >}}
Most XRDs should use `Namespaced` scope. This provides better security
isolation and follows standard Kubernetes patterns. Use `Cluster` scope only
for platform level resources like RBAC or cluster configuration.
{{< /hint >}}

### Set composite resource defaults
XRDs can set default parameters for composite resources.

<!-- vale off -->
#### defaultCompositionRef
<!-- vale on -->
It's possible for multiple [Compositions]({{<ref "./compositions">}}) to
reference the same XRD. If more than one Composition references the same XRD,
the composite resource must select which Composition to use.

An XRD can define the default Composition to use with the
`defaultCompositionRef` value.

Set a
{{<hover label="defaultComp" line="6">}}defaultCompositionRef{{</hover>}}
to set the default Composition.

```yaml {label="defaultComp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  defaultCompositionRef:
    name: myComposition
  group: custom-api.example.org
  names:
  # Removed for brevity
  versions:
  # Removed for brevity
```

<!-- vale off -->
#### defaultCompositionUpdatePolicy
<!-- vale on -->

Changes to a Composition generate a new Composition revision. By default all
composite resources use the updated Composition revision.

Set the XRD `defaultCompositionUpdatePolicy` to `Manual` to prevent composite
resources from automatically using the new revision.

The default value is `defaultCompositionUpdatePolicy: Automatic`.

Set {{<hover label="compRev" line="6">}}defaultCompositionUpdatePolicy: Manual{{</hover>}}
to set the default Composition update policy for composite resources and using
this XRD.

```yaml {label="compRev",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  defaultCompositionUpdatePolicy: Manual
  group: custom-api.example.org
  names:
  # Removed for brevity
  versions:
  # Removed for brevity
```

<!-- vale off -->
#### enforcedCompositionRef
<!-- vale on -->
To require all composite resources to use a specific Composition use the
`enforcedCompositionRef` setting in the XRD.

For example, to require all composite resources using this XRD to use the
Composition
{{<hover label="enforceComp" line="6">}}myComposition{{</hover>}}
set
{{<hover label="enforceComp" line="6">}}enforcedCompositionRef.name: myComposition{{</hover>}}.

```yaml {label="defaultComp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  enforcedCompositionRef:
    name: myComposition
  group: custom-api.example.org
  names:
  # Removed for brevity
  versions:
  # Removed for brevity
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
## Verify a CompositeResourceDefinition
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

Verify an XRD with `kubectl get compositeresourcedefinition` or the short form,
{{<hover label="getxrd" line="1">}}kubectl get xrd{{</hover>}}.

```yaml {label="getxrd",copy-lines="1"}
kubectl get xrd
NAME                                ESTABLISHED   OFFERED   AGE
xdatabases.custom-api.example.org   True          True      22m
```

The `ESTABLISHED` field indicates Crossplane installed the Kubernetes custom
resource definition for this XRD.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
### XRD conditions
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->
Crossplane uses a standard set of `Conditions` for XRDs.
View the conditions of a XRD under their `Status` with
`kubectl describe xrd`.

```yaml {copy-lines="none"}
kubectl describe xrd
Name:         xpostgresqlinstances.database.starter.org
API Version:  apiextensions.crossplane.io/v1
Kind:         CompositeResourceDefinition
# Removed for brevity
Status:
  Conditions:
    Reason:                WatchingCompositeResource
    Status:                True
    Type:                  Established
# Removed for brevity
```

<!-- vale off -->
#### WatchingCompositeResource
<!-- vale on -->
`Reason: WatchingCompositeResource` indicates Crossplane defined the new
Kubernetes custom resource definitions related to the composite resource and is
watching for the creation of new composite resources.

```yaml
Type: Established
Status: True
Reason: WatchingCompositeResource
```

<!-- vale off -->
#### TerminatingCompositeResource
<!-- vale on -->
`Reason: TerminatingCompositeResource` indicates Crossplane is deleting the
custom resource definitions related to the composite resource and is
terminating the composite resource controller.

```yaml
Type: Established
Status: False
Reason: TerminatingCompositeResource
```