---
title: "Crossplane Explained | Creating S3 Buckets in Kubernetes with Crossplane"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.devgenius.io/crossplane-explained-creating-s3-buckets-in-kubernetes-with-crossplane-74a9ba8dfb11"
author:
  - "[[Manish Sharma]]"
---
<!-- more -->

[Sitemap](https://blog.devgenius.io/sitemap/sitemap.xml)## [Dev Genius](https://blog.devgenius.io/?source=post_page---publication_nav-4e2c1156667e-74a9ba8dfb11---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*JemqY5zA9V8ybPkQFOupUg.png)

Fig: Image taken from the Crossplane official documentation

## Table of Contents

- Crossplane
- Upbound
- What is Control Plane
- Key Components of the Crossplane Control Plane
- How the Crossplane Control Plane Works
- Example Workflow
- Upbound Marketplace
- Key Features of Upbound Marketplace
- Benefits of Upbound Marketplace
- Example Use case
- Crossplane Components Overview
- Install Crossplane

## Crossplane

- **Crossplane** is an open-source project that extends Kubernetes to enable the management of infrastructure through Kubernetes APIs.
- It acts as a control plane, allowing developers to define, deploy, and manage cloud infrastructure resources using Kubernetes-style declarative configurations.
- Crossplane lets you manage anything, anywhere, all through standard Kubernetes APIs.
- Crossplane brings all your non-Kubernetes resources under one roof.

Here are some key features and components of Crossplane:

1. **Kubernetes Native**: Crossplane integrates with Kubernetes, allowing you to manage infrastructure using Kubernetes manifests.
2. **Declarative API**: You can define your infrastructure requirements declaratively using YAML files.
3. **Extensibility**: Crossplane supports a wide range of cloud providers and on-premises environments through its providers (e.g., AWS, Azure, GCP).
4. **Composability**: It enables composing infrastructure stacks and offering them as self-service APIs for application teams.
5. **Multi-Cloud Management**: You can manage resources across multiple cloud providers from a single Kubernetes cluster.

Crossplane Helm Chart Repo [https://charts.crossplane.io/stable](https://charts.crossplane.io/stable)

Crossplane GitHub Repo [https://github.com/crossplane/crossplane/](https://github.com/crossplane/crossplane/)

Crossplane Official Documentation [https://docs.crossplane.io/latest/](https://docs.crossplane.io/latest/)

## Upbound

**Upbound** is the company behind Crossplane, and it offers a set of commercial products and services that build on top of the open-source Crossplane project. Upbound provides:

1. **Upbound Universal Crossplane (UXP)**: An enterprise-grade distribution of Crossplane, designed to provide additional stability, security, and support.
2. **Upbound Cloud**: A managed service that provides a hosted Crossplane control plane, making it easier to deploy and manage Crossplane without needing to run it yourself.
3. **Commercial Support and Services**: Upbound offers enterprise support, consulting, and training services to help organizations adopt and manage Crossplane in production.

UXP Helm Chart Repo [https://charts.upbound.io/stable/](https://charts.upbound.io/stable/)

UXP GitHub Repo [https://github.com/upbound/universal-crossplane](https://github.com/upbound/universal-crossplane)

Upbound Official Documentation [https://docs.upbound.io/](https://docs.upbound.io/)

## What is a Control Plane?

Control planes oversee and manage the entire lifecycle of resources. They continuously monitor to ensure that the desired resources are present, report any discrepancies between the intended state and the actual state, and take corrective actions to align them.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*3uXkdYQJ0ZrzRBlS3WP42g.png)

Fig: Image taken from the Crossplane official documentation

## Key Components of the Crossplane Control Plane

1. **Crossplane Core**: This is the central part of Crossplane that integrates with the Kubernetes control plane. It includes controllers, Custom Resource Definitions (CRDs), and other components necessary to manage infrastructure resources.
2. **Providers**: Providers are ***plugins*** that extend Crossplane’s capabilities to manage resources across different cloud platforms (e.g., AWS, Azure, GCP) and on-premises environments. Each provider includes controllers and CRDs specific to the resources of that provider, such as databases, storage, and compute instances. A provider is generally linked with a suite of APIs. Examples include AWS, Google Cloud, and Azure providers. Installing any of these extends the Kubernetes API with numerous Custom Resource Definitions (CRDs), typically mapping to specific API endpoints. It is crucial to note that providers are not limited to the aforementioned cloud services. There are also *Kubernetes providers*, *SQL providers*, *Helm providers*, among many others. The Upbound Marketplace, a platform where providers are aggregated and cataloged.

We will explore the functionality of providers in more detail shortly. For now, let’s briefly examine the Upbound Marketplace, a platform where providers are aggregated and cataloged.

1. It is crucial to note that providers are not limited to the aforementioned cloud services. There are also Kubernetes providers, SQL providers, Helm providers, among many others.
2. We will explore the functionality of providers in more detail shortly. For now, let’s briefly examine the Upbound Marketplace, a platform where providers are aggregated and cataloged.”
3. **Custom Resource Definitions (CRDs)**: Crossplane defines a set of CRDs to represent infrastructure resources. These CRDs are similar to those used in Kubernetes to manage custom resources, allowing you to define, configure, and manage infrastructure in a Kubernetes-native way.
4. **Controllers**: Controllers are responsible for the reconciliation loop, which ensures that the current state of the infrastructure matches the desired state defined in the CRDs. They continuously monitor the state of the resources and take actions to reconcile any differences.

## How the Crossplane Control Plane Works

1. **Declarative Configuration**: Users define the desired state of their infrastructure using Kubernetes manifests. These manifests include resources like `CompositeResourceDefinitions` (XRDs), `Compositions`, and claims.
2. **Resource Reconciliation**: Crossplane controllers watch for changes in these manifests and reconcile the actual state of the infrastructure to match the desired state. This involves creating, updating, or deleting cloud resources as necessary.
3. **Providers Integration**: When a resource defined in the CRDs requires an action (e.g., provisioning an RDS instance on AWS), the relevant provider’s controller takes over. It uses the cloud provider’s API to manage the resource, ensuring it aligns with the specified configuration.
4. **Composite Resources and Claims**: Crossplane allows you to create higher-level abstractions called composite resources, which bundle multiple infrastructure resources into a single unit. Claims are used by application teams to request these composite resources, abstracting away the complexity of individual resource management.

## Example Workflow

1. **Define Infrastructure**: An infrastructure engineer defines a composite resource for a database that includes configuration for instances, backups, and networking.
2. **Deploy Configuration**: This definition is applied to the Kubernetes cluster, where Crossplane’s control plane manages the creation of the necessary cloud resources.
3. **Claim Resources**: Application developers create claims for the database resource, specifying their requirements. Crossplane provisions the necessary resources and ensures they remain in the desired state.

## Upbound Marketplace

The **Upbound Marketplace (**[https://marketplace.upbound.io/providers](https://marketplace.upbound.io/providers)) is a platform provided by Upbound, the company behind Crossplane, which offers a curated collection of Crossplane Providers, Configurations, and other infrastructure management tools. It aims to simplify the discovery, sharing, and deployment of infrastructure management solutions within the Crossplane ecosystem.

The Upbound Marketplace is free for the entire Crossplane community. Documentation and public package consumption is free for all users, while adding your own only requires a free Upbound account.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*8Or_rLCLOgpKEimp2Q6mrg.png)

More providers are available in the [Crossplane Contrib repository](https://github.com/crossplane-contrib/).

### Key Features of Upbound Marketplace

1. **Providers**: These are integrations that allow Crossplane to manage resources on various cloud platforms and services. Providers in the marketplace cover a wide range of cloud services, including AWS, Azure, Google Cloud, and others, as well as specialized services like databases, monitoring tools, and more.
2. **Configurations**: Pre-built Crossplane configurations are available in the marketplace to help users get started quickly with common infrastructure setups. These configurations include best practices and standardized setups for various use cases, such as multi-cloud deployments, CI/CD pipelines, and more.
3. **Compositions**: Higher-level abstractions or composite resources can be shared through the marketplace. These compositions bundle multiple resources and configurations into a single, reusable package, simplifying complex infrastructure setups.
4. **Community and Enterprise Solutions**: The marketplace includes both community-contributed and enterprise-grade solutions. Community solutions are typically open-source and maintained by the Crossplane community, while enterprise solutions may offer additional features, support, and guarantees.
5. **Integration with Upbound Cloud**: The marketplace is tightly integrated with Upbound Cloud, a managed service offering by Upbound. This integration allows users to easily deploy and manage marketplace resources within their Upbound Cloud environments.

### Benefits of Upbound Marketplace

- **Ease of Use**: By providing a centralized location for discovering and deploying Crossplane resources, the marketplace reduces the complexity involved in setting up and managing cloud infrastructure.
- **Best Practices**: Users can leverage pre-built configurations and compositions that incorporate best practices, ensuring robust and efficient infrastructure setups.
- **Collaboration**: The marketplace fosters collaboration within the Crossplane community, allowing users to share their solutions and benefit from the contributions of others.
- **Accelerated Deployment**: Ready-to-use providers and configurations accelerate the deployment of infrastructure resources, reducing the time required to set up and manage cloud environments.
- **Scalability**: Enterprises can find scalable solutions that are designed to work seamlessly in large-scale, multi-cloud environments.

### Example Use Case

Imagine a development team needing to set up a standardized infrastructure environment for a new application. They can browse the Upbound Marketplace to find a pre-built configuration that includes everything they need: a Kubernetes cluster, a managed database, storage solutions, and monitoring tools. By deploying this configuration through the marketplace, they can quickly get their environment up and running with minimal effort.

## Crossplane Components Overview

### Providers

- Providers enable Crossplane to provision infrastructure on an external service.
- Responsible for all aspects of connecting to non-Kubernetes resources.
- Providers are cluster scoped and available to all cluster namespaces.
- View all installed Providers with the command `kubectl get providers`.
- The Upbound Marketplace contains a large [collection of Crossplane Providers](https://marketplace.upbound.io/providers).
- More providers are available in the [Crossplane Contrib repository](https://github.com/crossplane-contrib/).
- Installing a provider also creates a Provider pod that’s responsible for reconciling the Provider’s APIs into the Kubernetes cluster. Providers constantly watch the state of the desired managed resources and create any external resources that are missing.
- *Beginning with Crossplane version 1.15.0 Crossplane* uses the Upbound Marketplace Crossplane package registry at `xpkg.upbound.io` by default for downloading and installing packages.

Example Configurations

```c
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-family-aws:v1.6.0

apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-ec2
spec:
  package: xpkg.upbound.io/upbound/provider-aws-ec2:v1.6.0
```

### Provider Configurations

- Providers have *ProviderConfigs*. *ProviderConfigs* configure settings related to the Provider like authentication or global defaults for the Provider.
- *ProviderConfigs* are cluster scoped and available to all cluster namespaces.
- View all installed ProviderConfigs with the command `kubectl get providerconfig`.

Example Configurations

```c
touch aws-credentials-dev.txt

echo "[default]
aws_access_key_id = <aws_access_key>
aws_secret_access_key = <aws_secret_key>" > aws-credentials-dev.txt

kubectl create secret generic aws-secret \
-n upbound-system \
--from-file=creds=./aws-credentials-dev.txt
```
```c
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: provider-config-aws-dev
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: upbound-system
      name: aws-secret
      key: creds
```

### Managed resources

- A provider’s CRDs (Custom Resource Definitions) map to individual resources within the provider.
- When Crossplane creates and monitors a resource, it is termed a Managed Resource.
- Utilizing a provider’s CRD generates a unique Managed Resource. For instance: Using the AWS provider’s bucket CRD, Crossplane creates a bucket Managed Resource within the Kubernetes cluster, which corresponds to an AWS S3 storage bucket.
- The Crossplane controller ensures state enforcement for Managed Resources, maintaining their settings and existence.
- This “Controller Pattern” is analogous to how the Kubernetes *kube-controller-manager* enforces state for pods.
- Managed Resources are cluster-scoped and accessible across all cluster namespaces.
- To view all managed resources, use the command: `kubectl get managed`.

Example Configurations

```c
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
spec:
  forProvider:
    # Removed for brevity
    vpcId: vpc-92464dgf0461b9gg
```

### Compositions

- A Composition is a ***template*** for a collection of managed resources, enabling platform teams to define a set of managed resources as a single object. For example, a compute managed resource may necessitate the creation of storage and virtual network resources. A single Composition can encapsulate all these resources.
- Compositions simplify the deployment of infrastructure composed of multiple managed resources, enforcing standards and settings across deployments.
- Platform teams can specify fixed or default settings for each managed resource within a Composition, or define fields and settings that users can modify. For instance, platform teams might set compute resource sizes and virtual network configurations, while allowing users to adjust storage resource sizes.
- Creating a Composition in Crossplane *does not instantiate any managed resources.* Instead, the Composition serves as a template, while a Composite Resource generates the actual resources.
- Use `kubectl get compositions` to view all *compositions*.

Example Configurations

```c
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  resources:
    - name: StorageBucket
      base:
        apiVersion: s3.aws.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            region: "us-east-2"
    - name: VM
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: Instance
        spec:
          forProvider:
            ami: ami-0d9858aa3c6322f73
            instanceType: t2.medium
            region: "us-east-2"
```

When a Composite Resource uses this Composition template, the Composite Resource creates two new managed resources with all the provided `spec.forProvider` settings.

### Composite Resources

- A *Composite Resource* (`XR`) is a set of provisioned *managed resources*. A *Composite Resource* uses the template defined by a *Composition* and applies any user defined settings.
- *Compositions* are templates for a set of *managed resources*.
- *Composite Resources* fill out the template and create *managed resources*.
- Deleting a *Composite Resource* deletes all the *managed resources* it created.
- *Composite Resources* are cluster scoped and available to all cluster namespaces.
- Use `kubectl get composite` to view all *Composite Resources*.

### Composite Resource Definitions

- *Composite Resource Definitions* (`XRDs`) create custom Kubernetes APIs used by *Claims* and *Composite Resources*.

### Claims

- *Claims* are the primary way developers interact with Crossplane.
- *Claims* access the custom APIs defined by the platform team in a *Composite Resource Definition*.
- *Claims* look like *Composite Resources*, but they’re namespace scoped, while *Composite Resources* are cluster scoped.
- Directly creating *Composite Resources* requires cluster-wide permissions, shared with all teams. *Claims* create the same set of resources, but on a namespace level. Ex: The compute resources of team A are unique to the compute resources of team B.
- View all available Claims `kubectl get claim`.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QyQfOdmA7w9SRlgsamwaxQ.png)

Fig: Image is taken from Crossplane official documentation ( https://docs.crossplane.io/latest/concepts/composite-resources/ )

## Install Crossplane

- Create `namesapce.yaml ` file to create namespace
```c
apiVersion: v1
kind: Namespace
metadata:
  name: crossplane-system
```
- create `kustomization.yaml` to install Crossplane Helm Chart
```c
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: crossplane-system
helmCharts:
  - name: crossplane
    releaseName: crossplane
    repo: https://charts.crossplane.io/stable
    version: 1.16.0
resources:
  - namespace.yaml
```
- Install crossplane using command `kubectl apply -k .` but I got this error
```c
error: trouble configuring builtin HelmChartInflationGenerator with config: \`
name: crossplane
releaseName: crossplane
repo: https://charts.crossplane.io/stable
version: 1.16.0
\`: must specify --enable-helm
```

then I used this command `kubectl kustomize --enable-helm | kubectl apply -f -`

Output

```c
namespace/crossplane-system created
serviceaccount/crossplane created
serviceaccount/rbac-manager created
clusterrole.rbac.authorization.k8s.io/crossplane created
clusterrole.rbac.authorization.k8s.io/crossplane-admin created
clusterrole.rbac.authorization.k8s.io/crossplane-browse created
clusterrole.rbac.authorization.k8s.io/crossplane-edit created
clusterrole.rbac.authorization.k8s.io/crossplane-rbac-manager created
clusterrole.rbac.authorization.k8s.io/crossplane-view created
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-admin created
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-browse created
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-edit created
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-view created
clusterrole.rbac.authorization.k8s.io/crossplane:allowed-provider-permissions created
clusterrole.rbac.authorization.k8s.io/crossplane:system:aggregate-to-crossplane created
clusterrolebinding.rbac.authorization.k8s.io/crossplane created
clusterrolebinding.rbac.authorization.k8s.io/crossplane-admin created
clusterrolebinding.rbac.authorization.k8s.io/crossplane-rbac-manager created
secret/crossplane-root-ca created
secret/crossplane-tls-client created
secret/crossplane-tls-server created
service/crossplane-webhooks created
deployment.apps/crossplane created
deployment.apps/crossplane-rbac-manager created
```

NOTE: Kustomization is natively built into `kubectl`. You can check with this command

```c
$ kubectl version --client
Client Version: v1.29.1
Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
```

Verify Crossplane installation with `kubectl get all -n crossplane-system`

```c
NAME                                          READY   STATUS    RESTARTS   AGE
pod/crossplane-594f8d6c86-s2tnt               1/1     Running   0          31s
pod/crossplane-rbac-manager-948695754-srjwp   1/1     Running   0          31s

NAME                          TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
service/crossplane-webhooks   ClusterIP   10.101.190.188   <none>        9443/TCP   31s

NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/crossplane                1/1     1            1           31s
deployment.apps/crossplane-rbac-manager   1/1     1            1           31s

NAME                                                DESIRED   CURRENT   READY   AGE
replicaset.apps/crossplane-594f8d6c86               1         1         1       31s
replicaset.apps/crossplane-rbac-manager-948695754   1         1         1       31s
```

Installing Crossplane creates new Kubernetes API end-points. Check new API end-points with `kubectl api-resources | grep crossplane`.

```c
$ kubectl api-resources | grep crossplane
NAME                              SHORTNAMES   APIVERSION                             NAMESPACED   KIND
compositeresourcedefinitions      xrd,xrds     apiextensions.crossplane.io/v1         false        CompositeResourceDefinition
compositionrevisions              comprev      apiextensions.crossplane.io/v1         false        CompositionRevision
compositions                      comp         apiextensions.crossplane.io/v1         false        Composition
environmentconfigs                envcfg       apiextensions.crossplane.io/v1alpha1   false        EnvironmentConfig
usages                                         apiextensions.crossplane.io/v1alpha1   false        Usage
configurationrevisions                         pkg.crossplane.io/v1                   false        ConfigurationRevision
configurations                                 pkg.crossplane.io/v1                   false        Configuration
controllerconfigs                              pkg.crossplane.io/v1alpha1             false        ControllerConfig
deploymentruntimeconfigs                       pkg.crossplane.io/v1beta1              false        DeploymentRuntimeConfig
functionrevisions                              pkg.crossplane.io/v1beta1              false        FunctionRevision
functions                                      pkg.crossplane.io/v1beta1              false        Function
locks                                          pkg.crossplane.io/v1beta1              false        Lock
providerrevisions                              pkg.crossplane.io/v1                   false        ProviderRevision
providers                                      pkg.crossplane.io/v1                   false        Provider
storeconfigs                                   secrets.crossplane.io/v1alpha1         false        StoreConfig
```

Now,

## Create S3 Bucket

### 1\. Install the AWS Provider

To begin with I am Installing the AWS S3 provider into the Kubernetes cluster with a Kubernetes configuration file.

Create `provider-aws-s3.yaml` manifest file.

```c
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.upbound.io/upbound/provider-aws-s3:v1.6.0
```

now, update existing *kustomization.yaml* file and add this line `provider-aws-s3.yaml` under *namespace.yaml* line.

Rerun, `kubectl kustomize --enable-helm | kubectl apply -f -` command. Check last 3 lines in below output.

```c
namespace/crossplane-system unchanged
serviceaccount/crossplane unchanged
serviceaccount/rbac-manager unchanged
clusterrole.rbac.authorization.k8s.io/crossplane unchanged
clusterrole.rbac.authorization.k8s.io/crossplane-admin unchanged
clusterrole.rbac.authorization.k8s.io/crossplane-browse unchanged
clusterrole.rbac.authorization.k8s.io/crossplane-edit unchanged
clusterrole.rbac.authorization.k8s.io/crossplane-rbac-manager unchanged
clusterrole.rbac.authorization.k8s.io/crossplane-view unchanged
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-admin unchanged
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-browse unchanged
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-edit unchanged
clusterrole.rbac.authorization.k8s.io/crossplane:aggregate-to-view unchanged
clusterrole.rbac.authorization.k8s.io/crossplane:allowed-provider-permissions unchanged
clusterrole.rbac.authorization.k8s.io/crossplane:system:aggregate-to-crossplane unchanged
clusterrolebinding.rbac.authorization.k8s.io/crossplane unchanged
clusterrolebinding.rbac.authorization.k8s.io/crossplane-admin unchanged
clusterrolebinding.rbac.authorization.k8s.io/crossplane-rbac-manager unchanged
secret/crossplane-root-ca unchanged
secret/crossplane-tls-client unchanged
secret/crossplane-tls-server unchanged
service/crossplane-webhooks unchanged
deployment.apps/crossplane configured
deployment.apps/crossplane-rbac-manager configured
provider.pkg.crossplane.io/provider-aws-s3 created
```

Verify *provider-aws-s3* installation with `kubectl get po -n crossplane-system`

```c
$ kubectl get po -n crossplane-system

NAME                                                        READY   STATUS    RESTARTS   AGE
crossplane-594f8d6c86-s2tnt                                 1/1     Running   0          74m
crossplane-rbac-manager-948695754-srjwp                     1/1     Running   0          74m
provider-aws-s3-56468ed6f1ee-7ffcc49688-9sbgj               1/1     Running   0          6m38s
upbound-provider-family-aws-0241afc15762-6c4646d465-fv45k   1/1     Running   0          6m43s
```

NOTE: *provider-aws-s3* package has a dependency on its family (*upbound-provider-family*) which gets automatically installed with this package. The family provider manages *authentication to AWS across all AWS family Providers*.

You can also verify the provider installed with `kubectl get providers`.

```c
$ kubectl get providers

NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
provider-aws-s3               True        True      xpkg.upbound.io/upbound/provider-aws-s3:v1.6.0       17m
upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v1.6.0   17m
```

The Crossplane Provider installs Kubernetes Custom Resource Definitions (**CRDs**) that represent AWS S3 services. These **CRDs** enable the creation and management of AWS S3 resources directly within Kubernetes.

You can view the new CRDs with `kubectl get crds`

```c
$ kubectl get crds | grep s3

bucketaccelerateconfigurations.s3.aws.upbound.io             2024-06-08T13:21:17Z
bucketacls.s3.aws.upbound.io                                 2024-06-08T13:21:17Z
bucketanalyticsconfigurations.s3.aws.upbound.io              2024-06-08T13:21:17Z
bucketcorsconfigurations.s3.aws.upbound.io                   2024-06-08T13:21:17Z
bucketintelligenttieringconfigurations.s3.aws.upbound.io     2024-06-08T13:21:17Z
bucketinventories.s3.aws.upbound.io                          2024-06-08T13:21:17Z
bucketlifecycleconfigurations.s3.aws.upbound.io              2024-06-08T13:21:17Z
bucketloggings.s3.aws.upbound.io                             2024-06-08T13:21:17Z
bucketmetrics.s3.aws.upbound.io                              2024-06-08T13:21:17Z
bucketnotifications.s3.aws.upbound.io                        2024-06-08T13:21:17Z
bucketobjectlockconfigurations.s3.aws.upbound.io             2024-06-08T13:21:17Z
bucketobjects.s3.aws.upbound.io                              2024-06-08T13:21:17Z
bucketownershipcontrols.s3.aws.upbound.io                    2024-06-08T13:21:17Z
bucketpolicies.s3.aws.upbound.io                             2024-06-08T13:21:17Z
bucketpublicaccessblocks.s3.aws.upbound.io                   2024-06-08T13:21:17Z
bucketreplicationconfigurations.s3.aws.upbound.io            2024-06-08T13:21:17Z
bucketrequestpaymentconfigurations.s3.aws.upbound.io         2024-06-08T13:21:17Z
buckets.s3.aws.upbound.io                                    2024-06-08T13:21:17Z
bucketserversideencryptionconfigurations.s3.aws.upbound.io   2024-06-08T13:21:17Z
bucketversionings.s3.aws.upbound.io                          2024-06-08T13:21:17Z
bucketwebsiteconfigurations.s3.aws.upbound.io                2024-06-08T13:21:17Z
objectcopies.s3.aws.upbound.io                               2024-06-08T13:21:18Z
objects.s3.aws.upbound.io                                    2024-06-08T13:21:18Z
```

### 2\. Create AWS IAM User

### 3\. Create a Kubernetes secret for AWS

- The provider requires credentials to create and manage AWS S3 resources.
- Providers use a Kubernetes *Secret* to connect the credentials to the provider.
- Generate a Kubernetes *Secret* from AWS Access & Secret Key and then configure the Provider to use it.
- Create a text file `crossplane_provider_aws_creds.txt` containing the AWS account `aws_access_key_id` and `aws_secret_access_key`
```c
[default]
aws_access_key_id = "00000000000000000000"
aws_secret_access_key = "0000000000000000000000000000000000000000"
```
- Secret must be base64 encoded
```c
$ cat crossplane_provider_aws_creds.txt | base64
```
- Create `crossplane-provider-aws-creds.yaml` file with below content
```c
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: crossplane-provider-aws-creds
  namespace: crossplane-system
data:
  creds: W2RlZmF1bHRdCmF3c19hY2Nlc3Nfa2V5X2lkID0gQUtJQTRNVFdOS0FDNUI0WlQ0WFQKYXdzX3NlY3JldF9hY2Nlc3Nfa2V5ID0gTVMxdjFzVWRFZ1RhQ3htS0JydkxGcG5OeDdDVDRLOVl5bkx5S3VzQw==
```
- Update existing *kustomization.yaml* file and add this line `crossplane-provider-aws-creds.yaml` after line number 12
- Rerun, `kubectl kustomize --enable-helm | kubectl apply -f -` command.
```c
secret/crossplane-provider-aws-creds configured
```

### 4\. Create a ProviderConfig

- The ProviderConfig in Crossplane for AWS is used to configure settings related to the provider, such as authentication or global defaults. These configurations allow Crossplane to communicate with AWS services.
- ProviderConfigs are *cluster-scoped* and available to all namespaces within the cluster.
- Create `crossplane-providerconfig-aws-creds.yaml` file with below content
```c
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: crossplane-aws
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: crossplane-provider-aws-creds
      key: creds
```
- Update existing *kustomization.yaml* file and add this line `crossplane-providerconfig-aws.yaml` after line number 13
- Rerun, `kubectl kustomize --enable-helm | kubectl apply -f -` command.
```c
deployment.apps/crossplane configured
deployment.apps/crossplane-rbac-manager configured
providerconfig.aws.upbound.io/crossplane-aws created
```

You can view all installed ProviderConfigs using the command `kubectl get providerconfig`

```c
$ kubectl get providerconfig

NAME                                           AGE
providerconfig.aws.upbound.io/crossplane-aws   46s
```

### 5\. Create a managed resource — S3 Bucket

- A *managed resource* is anything Crossplane creates and manages outside of the Kubernetes cluster.
- Now, we are going to create AWS S3 bucket which is a *managed resource*.
- Create `crossplane-managed-resource-s3-buckets.yaml` file with below content
```c
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: crossplane-test-bucket-mcj
  namespace: crossplane-system
spec:
  forProvider:
    region: ap-south-1
  providerConfigRef:
    name: crossplane-aws
```
- Update existing *kustomization.yaml* file and add this line `crossplane-managed-resource-s3-buckets.yaml` after line number 14. Final *kustomization.yaml* file should look like below
```c
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: crossplane-system
helmCharts:
  - name: crossplane
    releaseName: crossplane
    repo: https://charts.crossplane.io/stable
    version: 1.16.0
    namespace: crossplane-system
resources:
  - namespace.yaml
  - provider-aws-s3.yaml
  - crossplane-provider-aws-creds.yaml
  - crossplane-providerconfig-aws.yaml
  - crossplane-managed-resource-s3-buckets.yaml
```
- Rerun, `kubectl kustomize --enable-helm | kubectl apply -f -` command.
```c
bucket.s3.aws.upbound.io/crossplane-test-bucket-mcj created
```
- Login to AWS account and navigate to S3 page. You will notice S3 bucket is created.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*_Ltlhfg40Nvia1m6hIWfMQ.png)

- You can also use `kubectl get buckets -n crossplane-system` to verify Crossplane created the bucket.
```c
$ kubectl get buckets -n crossplane-system

NAME                         SYNCED   READY   EXTERNAL-NAME                AGE
crossplane-test-bucket-mcj   True     True    crossplane-test-bucket-mcj   9m32s
```

## All Commands

```c
# View all installed Providers
kubectl get providers

# View all installed ProviderConfigs 
kubectl get providerconfig

# To view all managed resources. This command creates a lot of Kubernetes API queries. Both the kubectl client and kube-apiserver throttle the API queries
kubectl get managed

# to view all compositions
kubectl get compositions

# to view all Composite Resources
kubectl get composite

# to view all available Claims
kubectl get claim

# Install using kustomize
kubectl kustomize --enable-helm | kubectl apply -f -

# Check Crossplane API endpoints
kubectl api-resources | grep crossplane

# List All Pods/Services/Deployments/Services in crossplane-system namespace
kubectl get all -n crossplane-system

# to view all S3 CRDs 
kubectl get crds | grep s3

# Create Kubernetes Secret
kubectl create secret generic crossplane-provider-aws-creds -n crossplane-system

# Describe Kubernetes Secret
kubectl describe secret crossplane-provider-aws-creds -n crossplane-system

# to view all installed ProviderConfigs
kubectl get providerconfig

# to verify bucket creation OR to list all buckets
kubectl get buckets
```

If you enjoyed this article, please show your support by clapping and following me for more content like this!

More complex designs and in-depth articles are on the way.

Cloud, DevOps & GenAI Architect | AWS, GCP, Hybrid Infra | Kubernetes, Terraform, ArgoCD | CI/CD | MLOps | Bedrock, SageMaker, Vertex AI.

## More from Manish Sharma and Dev Genius

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--74a9ba8dfb11---------------------------------------)