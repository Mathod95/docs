# Compositions

## Platform Engineering with Crossplane

### The Problem
Creating infrastructure resource-by-resource has limitations:

**For Developers:**

- Must understand provider-specific details (AWS APIs, GCP schemas, etc.)
- Need to create many resources for one application
- No standardization across teams
- Complex YAML configurations

**For Platform Teams:**

- Hard to enforce best practices
- No way to abstract complexity
- Difficult to provide self-service
- Manual reviews and approvals needed

### The Solution: Platform Abstractions
Crossplane enables platform engineering through compositions:

**Before (Raw Managed Resources):**

Developer needs a database →
  Creates RDS Instance
  Creates Security Group
  Creates Subnet Group
  Configures Backups
  Sets up Monitoring
  = 5+ resources, complex configuration

**After (Platform Abstraction):**

Developer needs a database →
  Creates one Database composite resource
  = 1 simple resource, platform handles the rest

### The Two Components

```bash
┌─────────────────────────────────────────────────────┐
│  CompositeResourceDefinition (XRD)                  │
│  "Defines the custom API schema"                    │
└─────────────────────────────────────────────────────┘
                       │
                       │ defines schema for
                       ▼
┌─────────────────────────────────────────────────────┐
│  Composition                                        │
│  "The blueprint: what resources to create"          │
└─────────────────────────────────────────────────────┘
                       │
                       │ creates resources for
                       ▼
┌─────────────────────────────────────────────────────┐
│  Composite Resource (XR)                            │
│  "User's request for infrastructure"                │
└─────────────────────────────────────────────────────┘
```

---

## CompositeResourceDefinitions (XRDs)

### What is an XRD?
An XRD (CompositeResourceDefinition) defines a new custom API for infrastructure.

**Think of it as:**

- A schema definition for your platform API
- Similar to how CRDs define resource types, but for your custom infrastructure types
- A contract between platform team and developers

### XRD Structure
```yaml linenums="1"
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.example.com
spec:
  group: example.com
  names:
    kind: XDatabase
    plural: xdatabases
  scope: Namespaced
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
              size:
                type: string
                enum: [small, medium, large]
              environment:
                type: string
    additionalPrinterColumns:
    - name: Size
      type: string
      jsonPath: .spec.size
    - name: Ready
      type: string
      jsonPath: .status.conditions[?(@.type=='Ready')].status
```

### Key Fields Explained

- **apiVersion:** apiextensions.crossplane.io/v2 - The XRD API version
- **group:** API group for your custom resources (like example.com)
- **names.kind:** The composite resource type (like XDatabase)
- **scope:** Either Namespaced or Cluster - determines resource scope
- **schema:** Defines what fields users can specify (using OpenAPI v3 schema)
- **additionalPrinterColumns:** Custom columns for kubectl get output

### Understanding Scope
The scope field determines resource scoping:

**Namespaced (Default):**

```yaml
spec:
  scope: Namespaced
```

- Composite resources are namespaced
- Teams can have their own resources in their namespaces
- Enables namespace-level RBAC
- Most common for multi-tenant environments

**Cluster-Scoped:**

```yaml
spec:
  scope: Cluster
```

- Composite resources are cluster-wide
- Useful for shared infrastructure
- Requires cluster-level permissions
- Good for platform-level resources

### The Schema
The **openAPIV3Schema** defines the user-facing API:

```yaml
schema:
  openAPIV3Schema:
    properties:
      spec:
        properties:
          size:
            type: string
            enum: [small, medium, large]  # Allowed values
          storageGB:
            type: integer
            minimum: 10
            maximum: 1000
          backupEnabled:
            type: boolean
            default: true
```

Users will create resources like:

```yaml linenums="1"
apiVersion: example.com/v1alpha1
kind: XDatabase
metadata:
  name: my-db
  namespace: team-alpha
spec:
  size: medium
  storageGB: 100
  backupEnabled: true
```

## Namespaced vs Cluster-Scoped
**Namespaced Composite Resources:**

- Created in a specific namespace
- Isolated between teams/namespaces
- Subject to namespace RBAC
- Can compose both namespaced and cluster-scoped managed resources
- This is the default behavior

**Cluster-Scoped Composite Resources:**

- Cluster-wide visibility
- Require cluster-level permissions
- Can compose any resources
- Used for platform infrastructure

```bash
Namespaced XR (XDatabase)  →  Managed Resources
  namespace: team-alpha         (RDS, VPC, etc.)

Cluster XR (XInfrastructure) →  Managed Resources
  cluster-scoped                  (VPCs, IAM, etc.)
```

---

## Compositions

### What is a Composition?
A Composition is the blueprint that defines what resources to create.

**Think of it as:**

- An implementation of the XRD
- A template for infrastructure
- The logic that turns a simple XR into complex infrastructure

### Basic Structure

```yaml linenums="1"
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: database-aws-prod
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: XDatabase           # Links to XRD
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: rds-instance
        base:
          apiVersion: rds.aws.crossplane.io/v1alpha1
          kind: DBInstance
          spec:
            forProvider:
              engine: postgres
              instanceClass: db.t3.medium
```

### How Compositions Work

```bash
1. User creates a Composite Resource (XR)
         ↓
2. Crossplane finds matching Composition
         ↓
3. Composition creates Managed Resources from templates
         ↓
4. Providers reconcile Managed Resources
         ↓
5. Infrastructure is created
```

### Resource Templates
Each resource in a composition is a template:

```yaml
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
          metadata:
            name: placeholder-namespace  # Static value for now
            labels:
              managed-by: crossplane
      providerConfigRef:
        name: kubernetes-provider
```

!!! Note
    In this lab, values are static (placeholders). In Lab 4, you'll learn to use patches to make them dynamic.

### Composition Mode: Pipeline
Pipeline mode enables composition functions:

```yaml
spec:
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: my-resource
        base:
          # Resource template
```

**Benefits:**

- Modular and extensible
- Can chain multiple functions
- Better error handling
- More flexibility than legacy mode

### Multiple Compositions
You can have multiple compositions for the same XRD:

```yaml
# Composition 1: Small dev environment
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: database-dev
  labels:
    environment: dev
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: XDatabase
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: rds
        base:
          spec:
            forProvider:
              instanceClass: db.t3.micro  # Small instance

---
# Composition 2: Large prod environment
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: database-prod
  labels:
    environment: prod
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: XDatabase
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: rds
        base:
          spec:
            forProvider:
              instanceClass: db.r5.xlarge  # Large instance
```

Users can select which composition to use.

---

## Composite Resources

### What is a Composite Resource?
A Composite Resource (XR) is a custom infrastructure resource that users create to request infrastructure.

Example:

```yaml linenums="1"
apiVersion: example.crossplane.io/v1alpha1
kind: XSimpleApp
metadata:
  name: my-app
  namespace: team-alpha  # Namespaced!
spec:
  appName: webapp
  environment: production
Composition Selection
How does Crossplane choose which Composition to use?
```

**Option 1: compositionRef (Explicit)**

```yaml
apiVersion: example.com/v1alpha1
kind: XDatabase
metadata:
  name: my-db
  namespace: default
spec:
  compositionRef:
    name: database-prod  # Explicitly choose this composition
  size: large
```

**Option 2: compositionSelector (Label-based)**

```yaml
apiVersion: example.com/v1alpha1
kind: XDatabase
metadata:
  name: my-db
  namespace: default
spec:
  compositionSelector:
    matchLabels:
      environment: prod  # Match compositions with this label
  size: large
```

**Option 3: Default Composition (in XRD)**

```yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
spec:
  defaultCompositionRef:
    name: database-dev  # Use this if no selection specified
```

---

## Resource Relationships

**The Hierarchy**
```bash
Composite Resource (XSimpleApp)
  namespace: default
  name: my-app
       │
       │ owns
       ▼
Managed Resources
  ├── Object (Namespace)
  │    └── Creates: Namespace in Kubernetes
  └── Object (ConfigMap)
       └── Creates: ConfigMap in Kubernetes
```

**Ownership and Deletion**  
Resources are linked via owner references:

# Managed Resource
```bash
metadata:
  ownerReferences:
  - apiVersion: example.crossplane.io/v1alpha1
    kind: XSimpleApp
    name: my-app
    controller: true
```

**What this means:**

- Deleting the Composite Resource deletes all Managed Resources
- Deleting Managed Resources individually is prevented (controlled by XR)

**Deletion Flow:**
```bash
kubectl delete xsimpleapp my-app -n default
         ↓
All Managed Resources deleted
         ↓
All external infrastructure deleted
```

**Viewing Relationships**
Find Managed Resources from Composite:

```bash
kubectl get xsimpleapp my-app -o yaml | grep resourceRefs -A 10
```

See all resources together:
```bash
# The composite resource
kubectl get xsimpleapp

# The managed resources
kubectl get object
```

---

## Key Takeaways

- XRDs define custom infrastructure APIs for your platform
- Compositions are blueprints that implement those APIs
- Composite Resources can be namespaced or cluster-scoped depending on the XRD's scope field
- Scope determines if XRs are namespaced or cluster-scoped
- Multiple Compositions can implement the same XRD for different scenarios
- Resource lifecycle is fully managed through ownership references
- Composition selection can be explicit, label-based, or use default selection
- The Crossplane model provides a simplified, intuitive approach to infrastructure management

---

## Quick Reference

```bash
# Create XRD
kubectl apply -f xrd.yaml

# Check XRD status
kubectl get xrd

# Create Composition
kubectl apply -f composition.yaml

# List compositions
kubectl get composition

# Create a Composite Resource
kubectl apply -f my-app.yaml

# Check XR status
kubectl get xsimpleapp my-app

# View managed resources
kubectl get object

# Delete everything (deletes XR and all managed resources)
kubectl delete xsimpleapp my-app
```