!!! Warning
    Changer toute les versions utiliser !

# Welcome to Lab 2: Working with Providers
In the previous lab, you installed Crossplane and learned about its core concepts. Now it's time to extend Crossplane with Providers and create your first managed resources!

## What are Providers?
**Providers** are the mechanism by which Crossplane manages external infrastructure. Think of them as plugins that extend Crossplane with support for specific platforms:

- AWS Provider - Manages AWS resources (EC2, S3, RDS, etc.)
- GCP Provider - Manages Google Cloud resources
- Azure Provider - Manages Microsoft Azure resources
- Kubernetes Provider - Manages Kubernetes resources (even on the same cluster!)
- And many more!

## How Providers Work
When you install a provider:

- It adds new **CRDs** for that platform's resources.
- It deploys a **controller pod** that watches those resources.
- The controller makes **API calls** to the external platform to reconcile resources.

## The Kubernetes Provider
In this lab, we'll use the **Kubernetes Provider**, which allows Crossplane to manage Kubernetes resources. This is perfect for learning because:

- It runs on the same cluster.
- It is simple to understand.
- It is great for building platform abstractions.

## What You'll Learn
In this lab, you will:

- Examine and install the Kubernetes Provider
- Configure provider credentials using `ProviderConfig`
- Create Managed Resources (`Namespace` and `ConfigMap`)
- Understand YAML structure and key fields
- Verify and manage resource lifecycle

Let's get started!

---

## Examining the Provider Manifest
Before installing a provider, let's examine its manifest to understand what we're creating.

View the provider manifest:

```bash
cat /root/code/provider.yaml
```
You should see:

```yaml linenums="1"
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-kubernetes
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-kubernetes:v0.14.1
```

Question: Which field in the Provider manifest specifies the container image that contains the provider's CRDs and controller?

spec.package

---

## Installing the Kubernetes Provider
Now that you understand the Provider manifest structure, let's install it.

**Apply the provider:**

```bash hl_lines="1"
kubectl apply -f /root/code/provider.yaml
provider.pkg.crossplane.io/provider-kubernetes created
```
This tells Crossplane to:

1. Download the provider package from the registry
2. Extract and install the CRDs
3. Deploy the provider controller pod

**Verify the provider was created:**

```bash hl_lines="1"
kubectl get providers
NAME                  INSTALLED   HEALTHY   PACKAGE                                                          AGE
provider-kubernetes   True        True      xpkg.upbound.io/crossplane-contrib/provider-kubernetes:v0.15.0   49s
```

You should see provider-kubernetes in the list.


!!! Note
    The provider may not be healthy immediately - it needs time to download and start.

---

## Verifying Provider Health
After applying the provider, Crossplane downloads the package and starts the controller. Let's verify that it's healthy.

**Check the provider status:**

```bash
kubectl get providers
```

Look for these columns:

- **INSTALLED:** True when CRDs are installed
- **HEALTHY:** True when the provider pod is running
- **AGE:** How long since creation

**Check the provider pod:**

```bash "TODO"
kubectl get pods -n crossplane-system | grep provider-kubernetes
provider-kubernetes-c3daebeb97e2-6f6775b879-p9g5x   1/1     Running   0          3m9s
```

You should see a pod in Running status.

Wait for the provider to be healthy (may take 1-2 minutes):

```bash
kubectl wait --for=condition=healthy --timeout=300s provider/provider-kubernetes
provider.pkg.crossplane.io/provider-kubernetes condition met
```

Tip: If the provider is not healthy, check the pod logs with kubectl logs -n crossplane-system <pod-name>

---

## Understanding Provider Packages

Providers are distributed as OCI container images (similar to Docker images).

What does the provider package contain?

CRDs for resource types and a controller to reconcile them

---

## Examining the ProviderConfig Manifest
Before we can use a provider, we need to configure how it authenticates. Let's examine the ProviderConfig.

View the ProviderConfig:

```bash
cat /root/code/providerconfig.yaml
```

You should see:

```yaml linenums="1"
apiVersion: kubernetes.crossplane.io/v1alpha1
kind: ProviderConfig
metadata:
  name: kubernetes-provider
spec:
  credentials:
    source: InjectedIdentity
```

Question: What does the spec.credentials.source: InjectedIdentity field mean for the Kubernetes provider?
The provider uses the pod's ServiceAccount credentials

---

## Creating the ProviderConfig
Now, let's create the ProviderConfig resource to configure the provider's authentication.

**Apply the ProviderConfig:**

```bash
kubectl apply -f /root/code/providerconfig.yaml
providerconfig.kubernetes.crossplane.io/kubernetes-provider created
```

**Verify the ProviderConfig was created:**

```bash
kubectl get providerconfig
NAME                  AGE
kubernetes-provider   13s
```

You should see kubernetes-provider in the list.

Note: Different providers have different credential sources. AWS provider might use a Secret with access keys, while Kubernetes provider can use InjectedIdentity.

---

## Understanding ProviderConfig
What is the primary purpose of a ProviderConfig resource?
To specify authentication credentials for the provider

---

## Examining a Managed Resource
Now, let's examine a Managed Resource - this is how Crossplane represents infrastructure.

**View the namespace managed resource:**

```bash
cat /root/code/managed-resource-namespace.yaml
```

You should see something like:

```yaml linenums="1"
apiVersion: kubernetes.crossplane.io/v1alpha2
kind: Object
metadata:
  name: sample-namespace
spec:
  forProvider:
    manifest:
      apiVersion: v1
      kind: Namespace
      metadata:
        name: crossplane-demo
        labels:
          managed-by: crossplane
  providerConfigRef:
    name: kubernetes-provider
```

Question: What is the purpose of the spec.forProvider.manifest field in the Kubernetes provider's Object resource?
it contains the kubernetes manifest to be created

---

## Creating the Namespace Managed Resource
Now, let's create the managed resource to provision a Kubernetes namespace.

**Apply the managed resource:**

```bash
kubectl apply -f /root/code/managed-resource-namespace.yaml
object.kubernetes.crossplane.io/sample-namespace created
```

**Verify the managed resource was created:**

```bash
kubectl get object
NAME               KIND        PROVIDERCONFIG        SYNCED   READY   AGE
sample-namespace   Namespace   kubernetes-provider   True     True    21s
```

You should see sample-namespace in the list.

**Check the status:**

```bash
kubectl get object sample-namespace
NAME               KIND        PROVIDERCONFIG        SYNCED   READY   AGE
sample-namespace   Namespace   kubernetes-provider   True     True    41s
```

Look for READY and SYNCED columns - they should both show True when the resource is successfully created.

Note: The required RBAC has been defined to grant the provider's service account the necessary permissions to manage the required resources.

---

## Verifying the Actual Resource
Remember: The managed resource (Object) is separate from the actual Kubernetes resource. Let's verify both.

**Check the managed resource:**

```bash
kubectl get object sample-namespace
NAME               KIND        PROVIDERCONFIG        SYNCED   READY   AGE
sample-namespace   Namespace   kubernetes-provider   True     True    109s
```

This shows Crossplane's managed resource.

**Check the actual namespace:**

```bash
kubectl get namespace crossplane-demo
NAME              STATUS   AGE
crossplane-demo   Active   119s
```

This shows the actual namespace that Crossplane created!

**View the namespace labels:**

```bash
kubectl get namespace crossplane-demo -o jsonpath='{.metadata.labels}' | jq .
{
  "kubernetes.io/metadata.name": "crossplane-demo",
  "managed-by": "crossplane"
}
```

You should see the managed-by: crossplane label we specified in the manifest.

Important: The managed resource (Object) and the actual resource (Namespace) are two different things. Crossplane manages the lifecycle of the actual resource through the managed resource.

---

## Hands-On Challenge: Complete the ConfigMap Manifest
Now, it's your turn! Complete a managed resource manifest for a ConfigMap using what you've learned.

Task: Edit the file /root/code/managed-resource-configmap.yaml and fill in the TODOs to create a managed resource that:

Has a name of my-configmap
Creates a ConfigMap named my-config in the crossplane-demo namespace
Contains data with the following key-value pair: message: Hello from Crossplane
References the kubernetes-provider ProviderConfig
Hint: Use the namespace example as a reference:

cat /root/code/managed-resource-namespace.yaml

After completing the TODOs, apply your manifest:

kubectl apply -f /root/code/managed-resource-configmap.yaml

Verify:

kubectl get configmap my-config -n crossplane-demo

!!! note "Hint"

    Think about the requirements:

    The Object resource itself needs a name (metadata.name)
    The ConfigMap inside the manifest needs a name and namespace
    The ConfigMap needs data with a message key
    The managed resource needs to reference which ProviderConfig to use
    Look at the namespace example at /root/code/managed-resource-namespace.yaml to see how these fields are structured.

!!! note "Solution"

    Replace the file with the completed manifest:

    cat <<'EOF' > /root/code/managed-resource-configmap.yaml
    apiVersion: kubernetes.crossplane.io/v1alpha2
    kind: Object
    metadata:
      name: my-configmap
    spec:
      forProvider:
        manifest:
          apiVersion: v1
          kind: ConfigMap
          metadata:
            name: my-config
            namespace: crossplane-demo
          data:
            message: Hello from Crossplane
      providerConfigRef:
        name: kubernetes-provider
    EOF
    Apply the manifest:

    kubectl apply -f /root/code/managed-resource-configmap.yaml
    Verify the resources were created:

    kubectl get object my-configmap
    kubectl get configmap my-config -n crossplane-demo

```bash
root@controlplane ~ ➜  kubectl apply -f /root/code/managed-resource-configmap.yaml
object.kubernetes.crossplane.io/my-configmap created

root@controlplane ~ ➜  kubectl get object my-configmap
kubectl get configmap my-config -n crossplane-demo
NAME           KIND        PROVIDERCONFIG        SYNCED   READY   AGE
my-configmap   ConfigMap   kubernetes-provider   True     True    5s
NAME        DATA   AGE
my-config   1      5s
```

---

## Understanding Managed Resource Lifecycle
What happens if you delete the managed resource (Object) from Crossplane?

Crossplane deletes the actual infrastructure resoure as well

---

## Provider Resource Types
The Kubernetes provider uses the Object kind as a generic resource type.

Why does the Kubernetes provider use a generic Object kind instead of having separate CRDs for each Kubernetes resource type?

To support any Kubernetes resource type without individual CRDs

---

## Congratulations!
You have successfully completed Lab 2!

**What You've Learned**
In this lab, you:

- Examined and understood Provider manifest structure
- Installed the Kubernetes Provider
- Configured provider credentials using ProviderConfig
- Examined managed resource YAML structure
- Created managed resources for a Namespace and ConfigMap
- Built your own ConfigMap managed resource from scratch
- Verified resource creation and lifecycle management
- Understood the relationship between managed resources and actual infrastructure

**What's Next?**

In Lab 3: Creating Composite Resources and Compositions, you will:

- Learn about Composite Resources (XRs) and Claims (XRCs)
- Create CompositeResourceDefinitions (XRDs)
- Build Compositions that provision multiple resources
- Create reusable infrastructure abstractions
- Implement platform engineering patterns

**Important Note**
So far, you've created individual managed resources. In the next lab, you'll learn how to create Compositions that bundle multiple resources together as a single logical unit, which is the key to building self-service platforms with Crossplane!