# Welcome to Lab 4: Composition Functions - Patch and Transform
Welcome to the final lab! In Lab 3, you created Compositions, but the resources had placeholder values instead of using the actual user inputs. Now, you'll learn how to make your compositions dynamic using Composition Functions!

## The Problem We're Solving
In Lab 3, our Composition created resources with hardcoded values:

```yaml
metadata:
  name: placeholder-namespace
  labels:
    app: placeholder-app
```

But users provided:

```yaml
spec:
  appName: demo
  environment: production
```

How do we copy those user values into the managed resources?

## The Solution: Composition Functions
Composition Functions are programs that transform the desired state of your composite resource into managed resources. The most popular function is function-patch-and-transform.

## What is Patch and Transform?

**Patching allows you to:**

- Copy values from the composite resource to managed resources
- Copy values between managed resources
- Set static values

**Transforming allows you to:**

- Format strings (e.g., "demo" → "demo-namespace")
- Convert types (string to int, etc.)
- Perform calculations
- Apply complex logic

## Pipeline Mode

To use functions, compositions must use Pipeline mode:

```yaml
spec:
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
```

## What You'll Learn
In this lab, you will:

1. Install the function-patch-and-transform function
2. Create a Composition using Pipeline mode
3. Use FromCompositeFieldPath patches to copy user inputs
4. Use string format transforms to modify values
5. Provision infrastructure with dynamic values

Let's make your compositions production-ready!

Note: Crossplane, the Kubernetes Provider, and a base XRD have been pre-installed for this lab.

---

## Examining the Function Manifest
Composition Functions are installed as Kubernetes resources, similar to Providers.

Review the Function manifest:

cat /root/code/function.yaml

You should see:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.8.2
```

Question: Based on the manifest structure, how are Functions similar to Providers in Crossplane?

Both Functions and Providers are Crossplane packages distributed as OCI images. They use similar manifest structures with `kind` (`Function`/`Provider`), `apiVersion` (`pkg.crossplane.io`), and `spec.package` pointing to a container registry. Both extend Crossplane's capabilities.

---

## Installing the Patch and Transform Function
Let's install the function so we can use it in our compositions.

Apply the Function:

```bash
kubectl apply -f /root/code/function.yaml
```

Crossplane will download and install the function, similar to how it installs providers.

Verify if the function was created:

```bash
kubectl get functions
NAME                           INSTALLED   HEALTHY   PACKAGE                                                                  AGE
function-patch-and-transform   True        True      xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.8.2   8s
```

You should see `function-patch-and-transform` in the list.

---

## Verifying the Function Installation
Let's verify that the function has been installed and is ready to use.

**Check function status:**

```bash
kubectl get functions
NAME                           INSTALLED   HEALTHY   PACKAGE                                                                  AGE
function-patch-and-transform   True        True      xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.8.2   8s
```

You should see function-patch-and-transform with INSTALLED and HEALTHY showing True.

**Check the function pod:**

```bash
kubectl get pods -n crossplane-system | grep function
function-patch-and-transform-c05a9add149b-769d9458b4-xn6mf   1/1     Running   0          113s
```

There should be a pod running the function.

**Wait for the function to be ready** (may take 1-2 minutes):

```bash
kubectl wait --for=condition=healthy --timeout=300s function/function-patch-and-transform
function.pkg.crossplane.io/function-patch-and-transform condition met
```

Tip: Functions run as pods in the `crossplane-system` namespace, just like providers.

---

## Understanding Composition Functions
What is the primary purpose of Composition Functions?

Composition Functions are programs that transform the desired state of a composite resource into the desired state of managed resources. They enable advanced logic like patching, transforming, conditional resource creation, and more, making compositions much more powerful and dynamic.

---

## Examining the Composition with Functions
Now, let's examine a Composition that uses the patch-and-transform function!

Review the Composition:

cat /root/code/composition-with-functions.yaml

You should see key sections like:

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
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.metadata.name
          transforms:
          - type: string
            string:
              fmt: "%s-namespace"
```

```yaml title="files"
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: simpleapp-with-functions
  labels:
    crossplane.io/xrd: xsimpleapps.example.crossplane.io
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
                  labels:
                    app: will-be-patched
                    environment: will-be-patched
                    managed-by: crossplane
            providerConfigRef:
              name: kubernetes-provider
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.metadata.name
          transforms:
          - type: string
            string:
              fmt: "%s-namespace"
              type: Format
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.metadata.labels.app
        - type: FromCompositeFieldPath
          fromFieldPath: spec.environment
          toFieldPath: spec.forProvider.manifest.metadata.labels.environment
      - name: app-config
        base:
          apiVersion: kubernetes.crossplane.io/v1alpha2
          kind: Object
          spec:
            forProvider:
              manifest:
                apiVersion: v1
                kind: ConfigMap
                metadata:
                  namespace: will-be-patched
                  name: will-be-patched
                data:
                  app: will-be-patched
                  environment: will-be-patched
                  config: "This is a demo configuration"
            providerConfigRef:
              name: kubernetes-provider
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.metadata.namespace
          transforms:
          - type: string
            string:
              fmt: "%s-namespace"
              type: Format
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.metadata.name
          transforms:
          - type: string
            string:
              fmt: "%s-config"
              type: Format
        - type: FromCompositeFieldPath
          fromFieldPath: spec.appName
          toFieldPath: spec.forProvider.manifest.data.app
        - type: FromCompositeFieldPath
          fromFieldPath: spec.environment
          toFieldPath: spec.forProvider.manifest.data.environment
```

Question: What does the FromCompositeFieldPath patch type do?

FromCompositeFieldPath copies a value from a field in the composite resource (like spec.appName) to a field in a managed resource (like the namespace name). This is how user inputs are passed to the infrastructure resources being created.

---

## Creating the Composition with Pipeline Mode
Let's create the Composition that uses patches and transforms!

**Apply the Composition:**

kubectl apply -f /root/code/composition-with-functions.yaml

**This composition:**

- Uses Pipeline mode (spec.mode: Pipeline)
- References the patch-and-transform function
- Defines patches to copy user inputs to resources
- Uses transforms to format values

Verify if the Composition was created:

```bash
kubectl get composition
NAME                       XR-KIND      XR-APIVERSION                    AGE
simpleapp-with-functions   XSimpleApp   example.crossplane.io/v1alpha1   13s
```

You should see simpleapp-with-functions in the list.

---

## Understanding the Composition Mode
Let's verify the composition is using Pipeline mode.

**Check the composition mode:**

```bash
kubectl get composition simpleapp-with-functions -o jsonpath='{.spec.mode}'
Pipeline
```

**You should see:** `Pipeline`

**View the pipeline configuration:**

```bash
kubectl get composition simpleapp-with-functions -o jsonpath='{.spec.pipeline[0]}' | jq .
{
  "functionRef": {
    "name": "function-patch-and-transform"
  },
  "input": {
    "apiVersion": "pt.fn.crossplane.io/v1beta1",
    "kind": "Resources",
    "resources": [
      {
        "base": {
          "apiVersion": "kubernetes.crossplane.io/v1alpha2",
          "kind": "Object",
          "spec": {
            "forProvider": {
              "manifest": {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                  "labels": {
                    "app": "will-be-patched",
                    "environment": "will-be-patched",
                    "managed-by": "crossplane"
                  },
                  "name": "will-be-patched"
                }
              }
            },
            "providerConfigRef": {
              "name": "kubernetes-provider"
            }
          }
        },
        "name": "app-namespace",
        "patches": [
          {
            "fromFieldPath": "spec.appName",
            "toFieldPath": "spec.forProvider.manifest.metadata.name",
            "transforms": [
              {
                "string": {
                  "fmt": "%s-namespace",
                  "type": "Format"
                },
                "type": "string"
              }
            ],
            "type": "FromCompositeFieldPath"
          },
          {
            "fromFieldPath": "spec.appName",
            "toFieldPath": "spec.forProvider.manifest.metadata.labels.app",
            "type": "FromCompositeFieldPath"
          },
          {
            "fromFieldPath": "spec.environment",
            "toFieldPath": "spec.forProvider.manifest.metadata.labels.environment",
            "type": "FromCompositeFieldPath"
          }
        ]
      },
      {
        "base": {
          "apiVersion": "kubernetes.crossplane.io/v1alpha2",
          "kind": "Object",
          "spec": {
            "forProvider": {
              "manifest": {
                "apiVersion": "v1",
                "data": {
                  "app": "will-be-patched",
                  "config": "This is a demo configuration",
                  "environment": "will-be-patched"
                },
                "kind": "ConfigMap",
                "metadata": {
                  "name": "will-be-patched",
                  "namespace": "will-be-patched"
                }
              }
            },
            "providerConfigRef": {
              "name": "kubernetes-provider"
            }
          }
        },
        "name": "app-config",
        "patches": [
          {
            "fromFieldPath": "spec.appName",
            "toFieldPath": "spec.forProvider.manifest.metadata.namespace",
            "transforms": [
              {
                "string": {
                  "fmt": "%s-namespace",
                  "type": "Format"
                },
                "type": "string"
              }
            ],
            "type": "FromCompositeFieldPath"
          },
          {
            "fromFieldPath": "spec.appName",
            "toFieldPath": "spec.forProvider.manifest.metadata.name",
            "transforms": [
              {
                "string": {
                  "fmt": "%s-config",
                  "type": "Format"
                },
                "type": "string"
              }
            ],
            "type": "FromCompositeFieldPath"
          },
          {
            "fromFieldPath": "spec.appName",
            "toFieldPath": "spec.forProvider.manifest.data.app",
            "type": "FromCompositeFieldPath"
          },
          {
            "fromFieldPath": "spec.environment",
            "toFieldPath": "spec.forProvider.manifest.data.environment",
            "type": "FromCompositeFieldPath"
          }
        ]
      }
    ]
  },
  "step": "patch-and-transform"
}
```

This shows the function reference and the patches configuration.

**Count the patches for the namespace resource:**

```bash
kubectl get composition simpleapp-with-functions -o jsonpath='{.spec.pipeline[0].input.resources[0].patches}' | jq 'length'
3
```

This shows how many patches are defined for the first resource.

---

## Understanding Transforms
In our composition, we use this transform:

```yaml
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.appName
  toFieldPath: spec.forProvider.manifest.metadata.name
  transforms:
  - type: string
    string:
      fmt: "%s-namespace"
```

If the user provides appName: webapp, what will the final value be after this transform?

The transform will replace `%s` with the input value `webapp`, resulting in `webapp-namespace`. String format transforms are commonly used to add prefixes, suffixes, or combine multiple values.

---

## Creating a Composite Resource with Dynamic Values
Now, let's create a Composite Resource and watch the patches in action!

**Review the Composite Resource:**

```bash
cat /root/code/composite-resource.yaml
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

**Notice:**

- `kind: XSimpleApp` - The namespaced composite resource
- `spec.crossplane.compositionRef.name: simpleapp-with-functions` - Explicitly selects our composition
- `spec.appName: webapp` - Will be patched into resource names and labels
- `spec.environment: prod` - Will be patched into labels and ConfigMap data

**Apply the Composite Resource:**

```bash
kubectl apply -f /root/code/composite-resource.yaml
xsimpleapp.example.crossplane.io/my-production-app created
```

**Crossplane will:**

1. Process the composite resource spec
2. Run the patch-and-transform function
3. Apply patches to transform values
4. Create the managed resources with dynamic values!

---

## Verifying the Patched Namespace
Let's verify that the patches worked correctly!

**Check the Composite Resource status:**

```bash
kubectl get xsimpleapp my-production-app
NAME                APP NAME   ENVIRONMENT   READY   AGE   SYNCED   READY   COMPOSITION                AGE
my-production-app   webapp     prod          True    57s   True     True    simpleapp-with-functions   57s
```

Wait for READY and SYNCED to be True.

**Verify the namespace was created with patched name:**

```bash
kubectl get namespace webapp-namespace
NAME               STATUS   AGE
webapp-namespace   Active   108s
```

The namespace should exist! Notice it's `webapp-namespace` (from appName + transform), not `placeholder-namespace`.

**Check the namespace labels:**

```bash
kubectl get namespace webapp-namespace -o jsonpath='{.metadata.labels}' | jq .
{
  "app": "webapp",
  "environment": "prod",
  "kubernetes.io/metadata.name": "webapp-namespace",
  "managed-by": "crossplane"
}
```

**You should see:**

- app: webapp` (from spec.appName)
- environment: production` (from spec.environment)
- managed-by: crossplane`

---

## Verifying the ConfigMap Patches
Let's check the ConfigMap to see all the patches in action.

**Get the ConfigMap:**

```bash
kubectl get configmap -n webapp-namespace
NAME               DATA   AGE
kube-root-ca.crt   1      3m15s
webapp-config      3      3m15s
```

You should see `webapp-config` (appName + "-config" transform).

**View the ConfigMap data:**

```bash
kubectl get configmap webapp-config -n webapp-namespace -o yaml
apiVersion: v1
data:
  app: webapp
  config: This is a demo configuration
  environment: prod
kind: ConfigMap
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: '{"apiVersion":"v1","data":{"app":"webapp","config":"This
      is a demo configuration","environment":"prod"},"kind":"ConfigMap","metadata":{"name":"webapp-config","namespace":"webapp-namespace"}}'
  creationTimestamp: "2026-02-16T08:21:11Z"
  name: webapp-config
  namespace: webapp-namespace
  resourceVersion: "3237"
  uid: 51796bff-82a2-4111-82d6-1de017707faa
```

**Check the data section:**

```yaml
data:
  app: webapp
  environment: production
  config: "This is a demo configuration"
```

**Extract specific values:**

```bash
kubectl get configmap webapp-config -n webapp-namespace -o jsonpath='{.data}' | jq .
{
  "app": "webapp",
  "config": "This is a demo configuration",
  "environment": "prod"
}
```

All the values came from patches - no more placeholders!

---

## Understanding Pipeline Mode
What is the key difference between Pipeline mode and the traditional Resources mode in Compositions?

In Pipeline mode, Composition Functions (like patch-and-transform) are invoked to generate the managed resources dynamically. Traditional mode (Resources mode) uses inline resource templates with patches defined directly in the composition. Pipeline mode is more powerful and flexible, supporting advanced transformations and custom logic.

---

## Transform Types
Besides string formatting, what are other types of transforms supported by patch-and-transform?

The `patch-and-transform` function supports multiple transform types including: `string` (`format`, `convert`, `trim`), `math` (`multiply`, `add`, `subtract`), `convert` (`toBase64`, `fromBase64`), `map` (`mapping` `values`), and `match` (`conditional` `values`). These enable complex data transformations.

---

## Congratulations! You've reached the end of our Crossplane course!

## Key Takeaways
**Crossplane enables:**

- Infrastructure as Code using Kubernetes-native tools
- Platform engineering and self-service infrastructure
- Multi-cloud resource management with a unified API
- GitOps workflows for infrastructure

**The Crossplane Stack:**

1. **Providers** - Extend Crossplane with platform-specific resources
2. **Managed Resources** - Individual infrastructure components
3. **XRDs & Compositions** - Custom APIs and blueprints
4. **Composite Resources** - User-facing infrastructure requests
5. **Functions** - Advanced transformation logic

### Next Steps
Now that you understand the fundamentals, you can:

**1. Explore More Providers:**

- **AWS Provider:** Manage S3, RDS, EKS, etc.
- **GCP Provider:** Manage GCS, Cloud SQL, GKE, etc.
- **Azure Provider:** Manage Blob Storage, SQL, AKS, etc.

**2. Build Advanced Compositions:**

- Multi-resource applications (database + cache + networking)
- Conditional resource creation
- Cross-resource references

**3. Learn More Functions:**

- function-auto-ready: Automatic readiness detection
- function-go-templating: Go template-based compositions
- Write your own custom functions!

**4. Create Production Patterns:**

- RBAC for Composite Resources and Compositions
- GitOps with ArgoCD or Flux
- Multi-cluster management
- Configuration management

**Resources**
Official Docs: https://docs.crossplane.io/
Community: https://crossplane.io/community
GitHub: https://github.com/crossplane/crossplane
Slack: https://slack.crossplane.io/

---