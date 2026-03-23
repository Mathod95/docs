# Composition Functions: Patch and Transform

## The Problem with Static Compositions
What We Had in Lab 3
In Lab 3, compositions used hardcoded values:

```yaml
spec:
  resources:
  - name: app-namespace
    base:
      spec:
        forProvider:
          manifest:
            kind: Namespace
            metadata:
              name: placeholder-namespace  # Static!
              labels:
                app: placeholder-app       # Static!
```

The Problem:

- All composite resources create the same resources with same names
- User inputs (appName, environment) are ignored
- No way to customize based on user values
- Not production-ready

## What We Need

**User provides:**

```yaml
spec:
  appName: webapp
  environment: prod
```

**We want to create:**

```yaml
metadata:
  name: webapp-namespace    # From appName + "-namespace"
  labels:
    app: webapp             # From appName
    environment: prod       # From environment
```

How? Composition Functions with Patch and Transform!

---

## Introduction to Composition Functions

### What are Composition Functions?
Composition Functions are programs that transform composite resources into managed resources.

**Think of them as:**

- Middleware in the composition pipeline
- Programs that process and transform resource definitions
- Extensions that add logic to compositions

### The patch-and-transform Function
The most common function is function-patch-and-transform:

**Capabilities:**

- Copy values from composite to managed resources
- Transform values (format strings, convert types, math operations)
- Set conditional values
- Combine multiple values

**Installation:**

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.8.2
```

Installed like a provider - downloads OCI image and runs as a pod.

### Functions vs Providers

| Aspect  | Provider	                | Function               |
|---------|---------------------------|------------------------|
| Purpose |	Manage external resources	| Transform compositions |
| Runs    |	Controller pod            | Sidecar function pod   |
| Input   |	Managed resources	        | Composite resources    |
| Output  |	External infrastructure	  | Managed resource specs |

---

## Pipeline Mode

### Resources Mode vs Pipeline Mode
**Resources Mode (Lab 3):**

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  compositeTypeRef:
    kind: XSimpleApp
  resources:              # Resources defined inline
  - name: namespace
    base:
      # Resource template
```

**Pipeline Mode (Lab 4):**

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  mode: Pipeline          # Enable pipeline mode
  compositeTypeRef:
    kind: XSimpleApp
  pipeline:               # Functions in pipeline
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      # Function configuration
```

### How Pipeline Mode Works

```bash
Composite Resource (cluster-scoped XR)
         │
         ▼
┌────────────────────────┐
│  Pipeline Step 1       │
│  patch-and-transform   │
│  (copies & transforms) │
└────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  Pipeline Step 2       │
│  (other function)      │
└────────────────────────┘
         │
         ▼
Managed Resources (final output)
```

**Benefits:**

- Functions run in sequence
- Each function can modify the output
- More powerful and flexible
- Supports complex transformations

---

## Patch Types

### What is Patching?
Patching copies values from one place to another.

1. FromCompositeFieldPath
**Most common patch type** - copies from composite resource to managed resource.

**Syntax:**

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName           # Source
  toFieldPath: metadata.labels.app      # Destination
```

**Example:**

**Composite resource has:**

```yaml
spec:
  appName: webapp
```

**Patch copies it to managed resource:**

```
metadata:
  labels:
    app: webapp  # Copied from spec.appName
```

2. ToCompositeFieldPath
Copies from managed resource to composite resource (less common).

**Use case:** Copy generated values back to composite

```yaml
patches:
- type: ToCompositeFieldPath
  fromFieldPath: status.atProvider.arn
  toFieldPath: status.bucketArn
```

3. FromCompositeFieldPath to Multiple Fields

**Copy one value to multiple places:**

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.environment
  toFieldPath: metadata.labels.environment
- type: FromCompositeFieldPath
  fromFieldPath: spec.environment
  toFieldPath: spec.forProvider.manifest.data.env
```

4. CombineFromComposite

**Combine multiple fields into one:**

```yaml
patches:
- type: CombineFromComposite
  combine:
    variables:
    - fromFieldPath: spec.appName
    - fromFieldPath: spec.environment
    strategy: string
    string:
      fmt: "%s-%s-bucket"  # webapp-prod-bucket
  toFieldPath: metadata.name
```

---

## Transform Types

### What are Transforms?
Transforms modify values during patching.

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName
  toFieldPath: metadata.name
  transforms:              # Modify the value
  - type: string
    string:
      fmt: "%s-namespace"  # Add suffix
```

1. String Transforms

**Format String:**

```yaml
transforms:
- type: string
  string:
    fmt: "%s-namespace"
    type: Format
```

**Input:** `webapp`
**Output:** `webapp-namespace`

**Convert Case:**

```yaml
transforms:
- type: string
  string:
    type: Convert
    convert: ToUpper
```

**Input:** `webapp`
**Output:** `WEBAPP`

**Trim:**

```yaml
transforms:
- type: string
  string:
    type: TrimPrefix
    trim: "app-"
```

**Input:** `app-webapp`
**Output:** `webapp`

### 2. Math Transforms

**Multiply:**

transforms:
- type: math
  math:
    type: Multiply
    multiply: 1024  # Convert GB to MB

**Input:** `10`
**Output:** `10240`

**Add:**

```yaml
transforms:
- type: math
  math:
    type: Add
    add: 100
```

3. Map Transforms
Map input values to output values:

```yaml
transforms:
- type: map
  map:
    small: db.t3.micro
    medium: db.t3.medium
    large: db.r5.xlarge
```

**Input:** `medium`
**Output:** `db.t3.medium`

**Use case:** Convert user-friendly sizes to provider-specific instance types.

4. Match Transforms
Conditional values based on patterns:

```yaml
transforms:
- type: match
  match:
    patterns:
    - type: literal
      literal: "prod"
      result: "true"
    - type: literal
      literal: "dev"
      result: "false"
    fallbackValue: "false"
  toFieldPath: spec.forProvider.encrypted
```

**Input:** `prod → Output: true`
**Input:** `dev → Output: false`

5. Convert Transforms
Convert between types:

```yaml
transforms:
- type: convert
  convert:
    toType: string
```

**Also supports:**

- `toType: int64`
- `toType: bool`
- `toType: float64`

---

## Practical Patterns

### Pattern 1: Simple Value Copy

**Goal:** Copy appName to namespace name

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName
  toFieldPath: spec.forProvider.manifest.metadata.name
```

### Pattern 2: Add Suffix
**Goal:** Create namespace name like webapp-namespace

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName
  toFieldPath: spec.forProvider.manifest.metadata.name
  transforms:
  - type: string
    string:
      fmt: "%s-namespace"
      type: Format
```

### Pattern 3: Multiple Labels
**Goal:** Set multiple labels from different fields

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName
  toFieldPath: spec.forProvider.manifest.metadata.labels.app
- type: FromCompositeFieldPath
  fromFieldPath: spec.environment
  toFieldPath: spec.forProvider.manifest.metadata.labels.environment
```

### Pattern 4: Combine Fields
**Goal:** Create bucket name from app and environment

```yaml
patches:
- type: CombineFromComposite
  combine:
    variables:
    - fromFieldPath: spec.appName
    - fromFieldPath: spec.environment
    strategy: string
    string:
      fmt: "%s-%s-bucket"
  toFieldPath: spec.forProvider.manifest.metadata.name
```

**Result:** webapp-prod-bucket

### Pattern 5: Size Mapping

**Goal:** Map user-friendly sizes to instance types

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.size
  toFieldPath: spec.forProvider.instanceClass
  transforms:
  - type: map
    map:
      small: db.t3.micro
      medium: db.t3.medium
      large: db.r5.xlarge
```

### Pattern 6: Environment-Based Config

**Goal:** Enable features only in production

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.environment
  toFieldPath: spec.forProvider.backupRetentionPeriod
  transforms:
  - type: map
    map:
      production: "30"
      staging: "7"
      dev: "0"
```

## Complete Example
Here's a full composition with patches and transforms:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: simpleapp-with-functions
spec:
  mode: Pipeline
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1alpha1
    kind: XSimpleApp
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
                metadata:
                  name: will-be-patched
            providerConfigRef:
              name: kubernetes-provider
        patches:
        # Patch 1: Set namespace name
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.metadata.name
          transforms:
          - type: string
            string:
              fmt: "%s-namespace"
        # Patch 2: Set app label
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.metadata.labels.app
        # Patch 3: Set environment label
        - type: FromCompositeFieldPath
          fromFieldPath: spec.environment
          toFieldPath: spec.forProvider.manifest.metadata.labels.environment
```

**When user creates:**

```yaml
apiVersion: example.crossplane.io/v1alpha1
kind: XSimpleApp
metadata:
  name: my-production-app
spec:
  crossplane:
    compositionRef:
      name: simpleapp-with-functions
  appName: webapp
  environment: prod
```
**Result:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: webapp-namespace        # Patched + transformed
  labels:
    app: webapp                  # Patched
    environment: prod            # Patched
```

## Key Takeaways

- **Composition Functions** add logic and transformations to compositions
- **Pipeline Mode** enables function execution in compositions
- **Patches** copy values from composite to managed resources
- **Transforms** modify values during patching (format, convert, map, etc.)
- **FromCompositeFieldPath** is the most common patch type
- **String transforms** are most useful for creating names and labels
- **Map transforms** convert user-friendly values to provider-specific values
- **Combine patches** merge multiple fields into one value

## Quick Reference

```bash
# Basic patch (copy value)
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName
  toFieldPath: metadata.name

# Patch with string format
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName
  toFieldPath: metadata.name
  transforms:
  - type: string
    string:
      fmt: "%s-suffix"

# Patch with map
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.size
  toFieldPath: spec.instanceClass
  transforms:
  - type: map
    map:
      small: t3.micro
      large: r5.xlarge

# Combine multiple fields
patches:
- type: CombineFromComposite
  combine:
    variables:
    - fromFieldPath: spec.field1
    - fromFieldPath: spec.field2
    strategy: string
    string:
      fmt: "%s-%s"
  toFieldPath: metadata.name
```