# Composite Resources and Compositions
In the previous labs, you installed Crossplane and created individual managed resources. Now it's time to unlock the real power of Crossplane: **building reusable infrastructure abstractions!**

**The Challenge**

Creating individual managed resources works, but it has limitations:

- Users must know provider-specific details
- Each application requires multiple resource definitions
- No standardization across teams
- Difficult to enforce best practices

**The Solution: Compositions**

Compositions allow you to:

- Bundle multiple resources into a single logical unit
- Hide complexity behind simple APIs
- Create platform abstractions for self-service
- Standardize infrastructure patterns

**Key Concepts**

Two main components work together:

1. CompositeResourceDefinition (XRD) - Defines your custom API

    - Like a blueprint for your infrastructure type
    - Specifies the schema and fields users provide
    - Supports namespaced and cluster-scoped resources

2. Composition - The implementation blueprint

    - Defines what resources to create
    - Maps user inputs to resource configurations
    - Can create multiple managed resources

**Real-World Example**

Instead of users creating:

- A Namespace
- A ConfigMap
- Resource quotas
- Network policies

They create a single *XSimpleApp* composite resource, and Crossplane provisions everything!

**The Crossplane Resource Model**

CompositeResourceDefinitions (XRDs) provide a simplified, intuitive approach:

- Composite Resources can be namespaced or cluster-scoped
- Single resource type - no separate abstractions needed
- Better namespace isolation and RBAC
- Flexible scope configuration

**What You'll Learn**
In this lab, you will:

- Examine and create a CompositeResourceDefinition (XRD)
- Understand the scope field (namespaced vs cluster-scoped)
- Build a Composition that provisions multiple resources
- Create a Composite Resource to provision infrastructure
- Understand the relationship between XRDs, Compositions, and Composite Resources

Let's build your first platform abstraction with Crossplane!

Note: Crossplane and the Kubernetes Provider have been pre-installed for this lab.

---

## Examining the CompositeResourceDefinition (XRD)
The XRD defines your custom API - it's the schema that users will use to request infrastructure.

Review the XRD:

```bash
cat /root/code/xrd.yaml
```

You should see key sections like:

```yaml linenums="1"
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xsimpleapps.example.crossplane.io
spec:
  group: example.crossplane.io
  names:
    kind: XSimpleApp
    plural: xsimpleapps
  scope: Namespaced
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        properties:
          spec:
            properties:
              appName:
                type: string
              environment:
                type: string
```

!!! note "Le fichier déployer dans le tutorial"
    ```yaml linenums="1"
    apiVersion: apiextensions.crossplane.io/v2
    kind: CompositeResourceDefinition
    metadata:
      name: xsimpleapps.example.crossplane.io
    spec:
      group: example.crossplane.io
      names:
        kind: XSimpleApp
        plural: xsimpleapps
      scope: Cluster
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
                  appName:
                    type: string
                    description: "The name of the application"
                  environment:
                    type: string
                    description: "The environment (dev, staging, prod)"
                    enum:
                    - dev
                    - staging
                    - prod
                required:
                - appName
                - environment
              status:
                type: object
                properties:
                  ready:
                    type: boolean
                    description: "Whether the application is ready"
        additionalPrinterColumns:
        - name: App Name
          type: string
          jsonPath: .spec.appName
        - name: Environment
          type: string
          jsonPath: .spec.environment
        - name: Ready
          type: string
          jsonPath: .status.conditions[?(@.type=='Ready')].status
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
    ```


Question: What does the spec.scope field determine in an XRD?
Wether composite resources are namespaced or cluster-scoped

!!! Warning
    https://app.userback.io/viewer/10703/133111/7154725mqHQrQcx3JqGMWQMPrGfvFRcH3RhV6h875cJJ5/

---

## Creating the XRD
Now, let's create the XRD to define our custom API.

Apply the XRD:

```bash
kubectl apply -f /root/code/xrd.yaml
compositeresourcedefinition.apiextensions.crossplane.io/xsimpleapps.example.crossplane.io created
```

This creates:

- A cluster-scoped composite resource type: XSimpleApp
- The API schema with appName and environment fields
- Custom printer columns for better kubectl get output

Verify the XRD was created:

```bash
kubectl get xrd
NAME                                ESTABLISHED   OFFERED   AGE
xsimpleapps.example.crossplane.io   True                    27s
```

You should see xsimpleapps.example.crossplane.io in the list.

---

## Verifying the XRD
After creating the XRD, Crossplane installs a new CRD for your custom API.

**Check XRD status:**

kubectl get xrd

Look for the ESTABLISHED column - it should show True when the CRD is ready.

**Check the new CRD created:**

kubectl api-resources | grep example.crossplane.io
NAME                                SHORTNAMES   APIVERSION                             NAMESPACED   KIND
xsimpleapps                                      example.crossplane.io/v1alpha1         false        XSimpleApp

**You should see:**

xsimpleapps - The composite resource (namespaced)

**Explore the new API:**

```bash
kubectl explain xsimpleapp.spec
GROUP:      example.crossplane.io
KIND:       XSimpleApp
VERSION:    v1alpha1

FIELD: spec <Object>


DESCRIPTION:
    <empty>
FIELDS:
  appName       <string> -required-
    The name of the application

  crossplane    <Object>
    Configures how Crossplane will reconcile this composite resource

  environment   <string> -required-
  enum: dev, staging, prod
    The environment (dev, staging, prod)
```

This shows the fields users can specify: appName and environment.

!!! Warning
    Error !

---

## Understanding XRDs
What is the main purpose of a CompositeResourceDefinition (XRD)?
To define a custom api schema for infrastructure requests

An XRD defines a new custom API (resource type) that users can use to request infrastructure. It specifies the schema, fields, validation rules, and whether resources are namespaced or cluster-scoped (via the scope field). It creates a composite resource type that users interact with directly.

---

## Examining the Composition
Now, let's examine the Composition - this defines what resources to provision.

**Review the Composition:**

cat /root/code/composition.yaml

You should see:

```yaml linenums="1"
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: simpleapp-composition
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1alpha1
    kind: XSimpleApp
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: app-namespace
        base:
          apiVersion: kubernetes.crossplane.io/v1alpha2
          kind: Object
          spec:
            forProvider:
              manifest:
                apiVersion: v1
                kind: Namespace
```

!!! Note "Le vrai fichier"

    ```yaml linenums="1"
    apiVersion: apiextensions.crossplane.io/v1
    kind: Composition
    metadata:
      name: simpleapp-composition
      labels:
        crossplane.io/xrd: xsimpleapps.example.crossplane.io
        environment: all
    spec:
      compositeTypeRef:
        apiVersion: example.crossplane.io/v1alpha1
        kind: XSimpleApp
      mode: Pipeline
      pipeline:
      - step: patch-and-transform
        functionRef:
          name: function-patch-and-transform
        input:
          apiVersion: pt.fn.crossplane.io/v1beta1
          kind: Resources
          resources:
          - name: app-namespace
            base:
              apiVersion: kubernetes.crossplane.io/v1alpha2
              kind: Object
              metadata:
                name: app-namespace
              spec:
                forProvider:
                  manifest:
                    apiVersion: v1
                    kind: Namespace
                    metadata:
                      name: placeholder-namespace
                      labels:
                        app: placeholder-app
                        environment: placeholder-env
                        managed-by: crossplane
                providerConfigRef:
                  name: kubernetes-provider
          - name: app-config
            base:
              apiVersion: kubernetes.crossplane.io/v1alpha2
              kind: Object
              metadata:
                name: app-config
              spec:
                forProvider:
                  manifest:
                    apiVersion: v1
                    kind: ConfigMap
                    metadata:
                      namespace: placeholder-namespace
                      name: app-config
                    data:
                      app: placeholder-app
                      environment: placeholder-env
                providerConfigRef:
                  name: kubernetes-provider
    ```

Question: What does the spec.compositeTypeRef field specify?

The compositeTypeRef specifies which XRD this composition implements. It references the composite resource type (XSimpleApp) defined by the XRD, allowing Crossplane to match composite resources to this composition.

---

## Creating the Composition
Now, let's create the Composition to define our infrastructure blueprint.

**Apply the Composition:**

```bash
kubectl apply -f /root/code/composition.yaml
composition.apiextensions.crossplane.io/simpleapp-composition created
```

**This composition will create:**

- A Namespace (via the app-namespace resource)
- A ConfigMap (via the app-config resource)

**Verify the Composition was created:**

```bash
kubectl get composition
NAME                    XR-KIND      XR-APIVERSION                    AGE
simpleapp-composition   XSimpleApp   example.crossplane.io/v1alpha1   37s
```

You should see simpleapp-composition in the list.

**Note:** This composition uses Pipeline mode with the patch-and-transform function, which is the modern Crossplane approach. The used values are static for now - in the next lab, you'll learn to use patches to make them dynamic.

---

## Verifying the Composition
Let's verify that the Composition has been created successfully.

**Check Composition status:**

kubectl get composition

You should see simpleapp-composition in the list.

**View Composition details:**

```bash
kubectl get composition simpleapp-composition -o yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apiextensions.crossplane.io/v1","kind":"Composition","metadata":{"annotations":{},"labels":{"crossplane.io/xrd":"xsimpleapps.example.crossplane.io","environment":"all"},"name":"simpleapp-composition"},"spec":{"compositeTypeRef":{"apiVersion":"example.crossplane.io/v1alpha1","kind":"XSimpleApp"},"mode":"Pipeline","pipeline":[{"functionRef":{"name":"function-patch-and-transform"},"input":{"apiVersion":"pt.fn.crossplane.io/v1beta1","kind":"Resources","resources":[{"base":{"apiVersion":"kubernetes.crossplane.io/v1alpha2","kind":"Object","metadata":{"name":"app-namespace"},"spec":{"forProvider":{"manifest":{"apiVersion":"v1","kind":"Namespace","metadata":{"labels":{"app":"placeholder-app","environment":"placeholder-env","managed-by":"crossplane"},"name":"placeholder-namespace"}}},"providerConfigRef":{"name":"kubernetes-provider"}}},"name":"app-namespace"},{"base":{"apiVersion":"kubernetes.crossplane.io/v1alpha2","kind":"Object","metadata":{"name":"app-config"},"spec":{"forProvider":{"manifest":{"apiVersion":"v1","data":{"app":"placeholder-app","environment":"placeholder-env"},"kind":"ConfigMap","metadata":{"name":"app-config","namespace":"placeholder-namespace"}}},"providerConfigRef":{"name":"kubernetes-provider"}}},"name":"app-config"}]},"step":"patch-and-transform"}]}}
  creationTimestamp: "2026-02-10T18:38:42Z"
  generation: 1
  labels:
    crossplane.io/xrd: xsimpleapps.example.crossplane.io
    environment: all
  name: simpleapp-composition
  resourceVersion: "7165"
  uid: bb394282-1456-4b21-8028-d75c717850b5
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1alpha1
    kind: XSimpleApp
  mode: Pipeline
  pipeline:
  - functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - base:
          apiVersion: kubernetes.crossplane.io/v1alpha2
          kind: Object
          metadata:
            name: app-namespace
          spec:
            forProvider:
              manifest:
                apiVersion: v1
                kind: Namespace
                metadata:
                  labels:
                    app: placeholder-app
                    environment: placeholder-env
                    managed-by: crossplane
                  name: placeholder-namespace
            providerConfigRef:
              name: kubernetes-provider
        name: app-namespace
      - base:
          apiVersion: kubernetes.crossplane.io/v1alpha2
          kind: Object
          metadata:
            name: app-config
          spec:
            forProvider:
              manifest:
                apiVersion: v1
                data:
                  app: placeholder-app
                  environment: placeholder-env
                kind: ConfigMap
                metadata:
                  name: app-config
                  namespace: placeholder-namespace
            providerConfigRef:
              name: kubernetes-provider
        name: app-config
    step: patch-and-transform
```

This shows the full composition with all resource templates in the pipeline.

**Check how many resources it will create:**

```bash
kubectl get composition simpleapp-composition -o jsonpath='{.spec.pipeline[0].input.resources[*].name}'
app-namespace app-config
```

You should see: app-namespace app-config

---

## Understanding Compositions
What does a Composition define?

A Composition defines the blueprint for provisioning infrastructure. It specifies which managed resources to create, their configurations, and how to map user inputs to resource fields (via patches). One Composition can create multiple managed resources as a single logical unit.

---

## Examining a Composite Resource
Now, let's examine a Composite Resource - this is how users request infrastructure.

**Review the resource:**

cat /root/code/composite-resource.yaml

**You should see:**

```yaml linenums="1"
apiVersion: example.crossplane.io/v1alpha1
kind: XSimpleApp
metadata:
  name: my-demo-app
spec:
  appName: demo
  environment: prod
```

Question: What type of resource is this?
This is a Composite Resource of kind XSimpleApp. It's a cluster-scoped custom resource defined by the XRD. Users create these simple resources, and Crossplane provisions all the underlying infrastructure.

---

## Creating a Composite Resource
Now, let's create a Composite Resource to provision infrastructure!

**Apply the Composite Resource:**

kubectl apply -f /root/code/composite-resource.yaml

When you create this composite resource, Crossplane will:

- Find the matching Composition (simpleapp-composition)
- Create the managed resources defined in the Composition
- Manage their lifecycle

Verify if the Composite Resource was created:

```bash
kubectl get xsimpleapp
NAME          APP NAME   ENVIRONMENT   READY   AGE   SYNCED   READY   COMPOSITION             AGE
my-demo-app   demo       prod          True    60s   True     True    simpleapp-composition   60s
```

You should see my-demo-app in the list.

---

## Verifying the Provisioned Resources
Let's verify that Crossplane has provisioned all the resources.

**Check the Composite Resource status:**

```bash
kubectl get xsimpleapp my-demo-app
NAME          APP NAME   ENVIRONMENT   READY   AGE   SYNCED   READY   COMPOSITION             AGE
my-demo-app   demo       prod          True    24s   True     True    simpleapp-composition   24s
```

Look for READY and SYNCED columns to be True.

**Check the managed resources:**

```bash
kubectl get object
NAME            KIND        PROVIDERCONFIG        SYNCED   READY   AGE
app-config      ConfigMap   kubernetes-provider   True     True    46s
app-namespace   Namespace   kubernetes-provider   True     True    46s
```

You should see two Object resources created by the composition.

**Verify the actual Kubernetes resources:**

```bash
kubectl get namespace | grep placeholder
NAME                    STATUS   AGE
placeholder-namespace   Active   90s
kubectl get configmap -A | grep app-config
NAMESPACE               NAME                                                   DATA   AGE
placeholder-namespace   app-config                                             2      74s
```

Note: The namespace is called placeholder-namespace instead of crossplane-demo because we haven't set up patches to copy user inputs yet.

---

## Exploring Resource Relationships
Let's explore how Composite Resources and Managed Resources are connected.

**View the Composite Resource details:**

```bash
kubectl get xsimpleapp my-demo-app -o yaml
apiVersion: example.crossplane.io/v1alpha1
kind: XSimpleApp
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"example.crossplane.io/v1alpha1","kind":"XSimpleApp","metadata":{"annotations":{},"name":"my-demo-app"},"spec":{"appName":"demo","environment":"prod"}}
  creationTimestamp: "2026-02-13T01:59:42Z"
  finalizers:
  - composite.apiextensions.crossplane.io
  generation: 4
  labels:
    crossplane.io/composite: my-demo-app
  name: my-demo-app
  resourceVersion: "1677"
  uid: 3e191ef9-d959-4d11-8c7b-0ba1313d7c69
spec:
  appName: demo
  crossplane:
    compositionRef:
      name: simpleapp-composition
    compositionRevisionRef:
      name: simpleapp-composition-12c721d
    compositionUpdatePolicy: Automatic
    resourceRefs:
    - apiVersion: kubernetes.crossplane.io/v1alpha2
      kind: Object
      name: app-config
    - apiVersion: kubernetes.crossplane.io/v1alpha2
      kind: Object
      name: app-namespace
  environment: prod
status:
  conditions:
  - lastTransitionTime: "2026-02-13T01:59:42Z"
    observedGeneration: 4
    reason: ReconcileSuccess
    status: "True"
    type: Synced
  - lastTransitionTime: "2026-02-13T01:59:42Z"
    observedGeneration: 4
    reason: Available
    status: "True"
    type: Ready
  - lastTransitionTime: "2026-02-13T01:59:42Z"
    observedGeneration: 4
    reason: WatchCircuitClosed
    status: "True"
    type: Responsive
```

Look for spec.crossplane.resourceRefs - this lists all the managed resources created.

**View a managed resource:**


```bash
kubectl get object -o yaml | head -50 
apiVersion: v1
items:
- apiVersion: kubernetes.crossplane.io/v1alpha2
  kind: Object
  metadata:
    annotations:
      crossplane.io/composition-resource-name: app-config
      crossplane.io/external-create-pending: "2026-02-13T01:59:42Z"
      crossplane.io/external-create-succeeded: "2026-02-13T01:59:42Z"
      crossplane.io/external-name: app-config
    creationTimestamp: "2026-02-13T01:59:42Z"
    finalizers:
    - finalizer.managedresource.crossplane.io
    generation: 2
    labels:
      crossplane.io/composite: my-demo-app
    name: app-config
    ownerReferences:
    - apiVersion: example.crossplane.io/v1alpha1
      blockOwnerDeletion: true
      controller: true
      kind: XSimpleApp
      name: my-demo-app
      uid: 3e191ef9-d959-4d11-8c7b-0ba1313d7c69
    resourceVersion: "1667"
    uid: 30ec39a0-392a-4890-8e20-e1d0e5bc7a69
  spec:
    deletionPolicy: Delete
    forProvider:
      manifest:
        apiVersion: v1
        data:
          app: placeholder-app
          environment: placeholder-env
        kind: ConfigMap
        metadata:
          name: app-config
          namespace: placeholder-namespace
    managementPolicies:
    - '*'
    providerConfigRef:
      name: kubernetes-provider
    readiness:
      policy: SuccessfulCreate
    watch: false
  status:
    atProvider:
      manifest:
        apiVersion: v1
        data:
```

Look for metadata.ownerReferences - this shows it's owned by the Composite Resource.

**This creates a hierarchy:**

Composite Resource (XSimpleApp - cluster-scoped)
  └─> Managed Resource 1 (Object - Namespace)
  └─> Managed Resource 2 (Object - ConfigMap)

---

## Understanding Resource Lifecycle
What happens when you delete a Composite Resource?

When you delete a Composite Resource, Crossplane will automatically delete all the managed resources it created. This ensures clean deletion of the entire infrastructure stack provisioned by that composite resource.

---

## Composition Selection
Crossplane allows multiple Compositions for the same XRD.

How does Crossplane choose which Composition to use when you create a Composite Resource?

Crossplane selects a Composition based on:

1. `compositionRef` explicitly specified in the composite resource
2. `compositionSelector` using labels to match compositions
3. A default composition if defined in the XRD
This allows multiple implementations of the same infrastructure type (e.g., dev vs prod configurations).

---

## Congratulations!
You have successfully completed Lab 3!

What You've Learned
In this lab, you:

- Examined and understood XRD structure with the scope field
- Created a CompositeResourceDefinition
- Learned about namespaced vs cluster-scoped composite resources
- Built a Composition using pipeline mode with composition functions
- Created a Composite Resource to provision infrastructure
- Explored the relationships between Composite Resources and Managed Resources
- Understood resource lifecycle management and composition selection

### The Limitation We Saw
You noticed that our resources had placeholder values instead of the actual appName and environment values from the composite resource. This is because we haven't configured patches yet!

What's Next?
In the next lab, you will:

- Use the patch-and-transform function you saw in this lab
- Configure patches to copy values from Composite Resources to Managed Resources
- Use transforms to modify values (format strings, convert types)
- Build truly dynamic compositions with real user inputs

Get ready to make your compositions dynamic and production-ready!