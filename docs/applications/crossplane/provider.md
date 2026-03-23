---
title: Provider
date: 22-03-26
status: draft
categories:
  - Crossplane
tags:
  - Crossplane
  - Provider
source:
  - https://docs.crossplane.io/v2.2/packages/providers/#install-a-provider
---

## Install a provider

Installing a provider creates new Kubernetes resources representing the Provider’s APIs. Installing a provider also creates a Provider pod that’s responsible for reconciling the Provider’s APIs into the Kubernetes cluster. Providers constantly watch the state of the desired managed resources and create any external resources that are missing.

### Install as Object 

Install a Provider with a Crossplane Provider object setting the spec.package value to the location of the provider package.

For example, to install the [provider-aws-ec2](https://marketplace.upbound.io/providers/upbound/provider-aws-ec2/),

```yaml linenums="1"
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: upbound-provider-aws-ec2
spec:
  package: xpkg.upbound.io/upbound/provider-aws-ec2:v2.5.0
```

!!! note 
    By default, the Provider pod installs in the same namespace as Crossplane `crossplane-system`

### Install with Helm 

Crossplane supports installing Providers during an initial Crossplane installation with the Crossplane Helm chart.

Use the --set provider.packages argument with helm install.

For example, to install the AWS S3 Provider,

```bash hl_lines="1-4"
helm install crossplane crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace
--set provider.packages='{xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v2.0.0}'
```

## Verify a Provider 
Providers install their own APIs representing the managed resources they support. Providers may also create Deployments, Service Accounts or RBAC configuration.

View the status of a Provider with

kubectl get providers

During the install a Provider report `INSTALLED` as `True` and `HEALTHY` as `Unknown`.

```bash hl_lines="1"
kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
upbound-provider-aws-ec2      True        False     xpkg.upbound.io/upbound/provider-aws-ec2:v2.5.0      17s
upbound-provider-family-aws   True        False     xpkg.upbound.io/upbound/provider-family-aws:v2.5.0   6s
```

After the Provider install completes and it’s ready for use the `HEALTHY` status reports `True`.

```bash hl_lines="1"
kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
upbound-provider-aws-ec2      True        True      xpkg.upbound.io/upbound/provider-aws-ec2:v2.5.0      52s
upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v2.5.0   41s
```

!!! warning
    Some Providers install hundreds of Kubernetes Custom Resource Definitions (CRDs). This can create significant strain on undersized API Servers, impacting Provider install times.

## Remove a provider

Remove a Provider by deleting the Provider object with kubectl delete provider.

!!! Warning
    Removing a Provider without first removing the Provider’s managed resources may abandon the resources. The external resources aren’t deleted.

    If you remove the Provider first, you must manually delete external resources through your cloud provider. Managed resources must be manually deleted by removing their finalizers.

    For more information on deleting abandoned resources read the Crossplane troubleshooting guide.




---



## What are Providers?
**Providers** are the mechanism by which Crossplane manages external infrastructure. Think of them as plugins that extend Crossplane with support for specific platforms:

## Understanding Providers

Les `Providers` sont des packages Crossplane qui étendent Crossplane en lui permettant de gérer des resources sur des plateformes spécifiques.

- Ajoutent de nouveaux types de resources (CRDs)
- Déploient des controllers pour gérer ces resources
- Connectent Crossplane à des plateformes externes telles que AWS, GCP, Azure, Kubernetes, etc.

**Provider Package Structure**

```bash
Provider Package (OCI Image)
├── CRDs (Custom Resource Definitions)
│   └── Define resource types (Bucket, Instance, etc.)
├── Controller (Pod)
│   └── Watches resources and reconciles them
└── Metadata
    └── Version, dependencies, configuration
```

## How Providers Work
When you install a provider:

- It adds new **CRDs** for that platform's resources.
- It deploys a **controller pod** that watches those resources.
- The controller makes **API calls** to the external platform to reconcile resources.

### Installer un Provider

Les providers sont installés en tant que ressources Kubernetes

```yaml linenums="1" title="provider-aws-ec2.yaml"
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: upbound-provider-aws-ec2
spec:
  package: xpkg.upbound.io/upbound/provider-aws-ec2:v2.5.0
```

**Que se passe-t-il lors de l’application de ce manifeste ?**

1. Crossplane télécharge le package du provider (image OCI)
1. Il extrait et installe les CRDs
1. Il déploie le pod du provider controller dans le namespace `crossplane-system`
1. Le provider devient prêt à gérer des resources

**Checking Provider Status:**
```bash
kubectl get providers
# INSTALLED   HEALTHY   AGE
# True        True      2m
```



---

## ProviderConfig

Un `ProviderConfig` indique à un `provider` comment s’authentifier sur sa plateforme. Il contient toutes les informations nécessaires pour que le provider accède à ses ressources de manière sécurisée.

- Chaque provider nécessite des credentials pour accéder à sa plateforme (ex. API key, token, password).
- Le ProviderConfig stocke cette configuration d’authentification.
- Les resources managées se réfèrent à un ProviderConfig.
- Il est possible de créer plusieurs ProviderConfigs pour différents environnements, comme développement, staging ou production.

### Authentication Methods

Different providers support different authentication methods:

1. **InjectedIdentity (Kubernetes Provider):**

    ```yaml
    apiVersion: kubernetes.crossplane.io/v1alpha1
    kind: ProviderConfig
    metadata:
      name: kubernetes-provider
    spec:
      credentials:
        source: InjectedIdentity  # Uses pod's ServiceAccount
    ```

2. **Secret (AWS Provider):**

    ```yaml
    apiVersion: aws.crossplane.io/v1beta1
    kind: ProviderConfig
    metadata:
      name: aws-config
    spec:
      credentials:
        source: Secret
        secretRef:
          name: aws-credentials
          namespace: crossplane-system
          key: credentials
    ```

3. **IRSA/Workload Identity (Cloud Providers):**

    - Uses IAM roles for service accounts
    - No long-lived credentials needed
    - More secure for production

### Why Multiple ProviderConfigs?

```yaml
# Development environment
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: aws-dev
spec:
  credentials:
    source: Secret
    secretRef:
      name: aws-dev-credentials

---
# Production environment
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: aws-prod
spec:
  credentials:
    source: Secret
    secretRef:
      name: aws-prod-credentials
```

Resources specify which config to use:
```yaml
spec:
  providerConfigRef:
    name: aws-prod  # Use production credentials
```

---

!!! Warning
    Changer toute les versions utiliser !




- AWS Provider - Manages AWS resources (EC2, S3, RDS, etc.)
- GCP Provider - Manages Google Cloud resources
- Azure Provider - Manages Microsoft Azure resources
- Kubernetes Provider - Manages Kubernetes resources (even on the same cluster!)
- And many more!



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