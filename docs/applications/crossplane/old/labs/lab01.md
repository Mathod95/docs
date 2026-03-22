# Welcome to Crossplane for Beginners




## What You'll Learn
In this first lab, you will:

1. Install Crossplane on a Kubernetes cluster using Helm
2. Verify the installation and explore Crossplane components
3. Understand core Crossplane concepts
4. Install the Crossplane kubectl plugin

## Prerequisites
This course assumes you have:

- Basic Kubernetes knowledge (pods, deployments, services)
- Familiarity with kubectl commands
- Understanding of YAML manifests

---

## Installing Crossplane with Helm
Crossplane is installed on Kubernetes using Helm, the package manager for Kubernetes.

In this task, you are required to install Crossplane by adding its helm repository, then installing the `crossplane-stable/crossplane` chart in the `crossplane-system` namespace.

Upon accomplishing this, you would have:

- Created the `crossplane-system` namespace
- Installed Crossplane components (control plane, CRDs, webhooks)
- Started the Crossplane pod that manages infrastructure resources

!!! Note ""

    Step 1: Add the Crossplane Helm repository


    ```bash
    helm repo add crossplane-stable https://charts.crossplane.io/stable
    helm repo update
    ```


    Step 2: Install Crossplane in the crossplane-system namespace

    ```bash
    helm install crossplane crossplane-stable/crossplane \
      --namespace crossplane-system \
      --create-namespace
    ```

    !!! Example "OUTPUT"

        ```bash hl_lines="1 3 8"
        helm repo add crossplane-stable https://charts.crossplane.io/stable
        "crossplane-stable" has been added to your repositories
        helm repo update
        Hang tight while we grab the latest from your chart repositories...
        ...Successfully got an update from the "crossplane-stable" chart repository
        Update Complete. ⎈Happy Helming!⎈

        helm install crossplane crossplane-stable/crossplane \
          --namespace crossplane-system \
          --create-namespace
        NAME: crossplane
        LAST DEPLOYED: Sun Feb  1 20:43:02 2026
        NAMESPACE: crossplane-system
        STATUS: deployed
        REVISION: 1
        TEST SUITE: None
        NOTES:
        Release: crossplane

        Chart Name: crossplane
        Chart Description: Crossplane is an open source Kubernetes add-on that enables platform teams to assemble infrastructure from multiple vendors, and expose higher level self-service APIs for application teams to consume.
        Chart Version: 2.1.3
        Chart Application Version: 2.1.3

        Kube Version: v1.34.1
        ```

---

## Verifying Crossplane Installation
Let's verify that Crossplane has been successfully installed and is running.

Check Crossplane pods:
```bash hl_lines="1"
kubectl get pods -n crossplane-system
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-5f6cd547ff-68j9t                1/1     Running   0          3m41s
crossplane-rbac-manager-6d7d5844bd-b874t   1/1     Running   0          3m41s
```
You should see pods in a Running state:

- crossplane-* - The main Crossplane controller
- crossplane-rbac-manager-* - Manages RBAC for Crossplane resources
**Check Crossplane's Custom Resource Definitions (CRDs) **:

```bash hl_lines="1"
kubectl api-resources | grep crossplane
NAME                                SHORTNAMES   APIVERSION                             NAMESPACED   KIND
compositeresourcedefinitions        xrd,xrds     apiextensions.crossplane.io/v2         false        CompositeResourceDefinition
compositionrevisions                comprev      apiextensions.crossplane.io/v1         false        CompositionRevision
compositions                        comp         apiextensions.crossplane.io/v1         false        Composition
environmentconfigs                  envcfg       apiextensions.crossplane.io/v1beta1    false        EnvironmentConfig
managedresourceactivationpolicies   mrap         apiextensions.crossplane.io/v1alpha1   false        ManagedResourceActivationPolicy
managedresourcedefinitions          mrd,mrds     apiextensions.crossplane.io/v1alpha1   false        ManagedResourceDefinition
usages                                           apiextensions.crossplane.io/v1beta1    false        Usage
cronoperations                      cronops      ops.crossplane.io/v1alpha1             false        CronOperation
operations                          ops          ops.crossplane.io/v1alpha1             false        Operation
watchoperations                     watchops     ops.crossplane.io/v1alpha1             false        WatchOperation
configurationrevisions                           pkg.crossplane.io/v1                   false        ConfigurationRevision
configurations                                   pkg.crossplane.io/v1                   false        Configuration
deploymentruntimeconfigs                         pkg.crossplane.io/v1beta1              false        DeploymentRuntimeConfig
functionrevisions                                pkg.crossplane.io/v1                   false        FunctionRevision
functions                                        pkg.crossplane.io/v1                   false        Function
imageconfigs                                     pkg.crossplane.io/v1beta1              false        ImageConfig
locks                                            pkg.crossplane.io/v1beta1              false        Lock
providerrevisions                                pkg.crossplane.io/v1                   false        ProviderRevision
providers                                        pkg.crossplane.io/v1                   false        Provider
clusterusages                                    protection.crossplane.io/v1beta1       false        ClusterUsage
usages                                           protection.crossplane.io/v1beta1       true         Usage
```

This will show all the custom resources that Crossplane has installed. You should see resources like:

- providers
- compositeresourcedefinitions
- compositions
- And many more!

Run these verification commands to ensure everything is working correctly.

Tip: If pods are not in Running state, wait a minute and check again. It may take some time for images to pull and pods to start.


---

Understanding Crossplane Architecture
Now that Crossplane is installed, let's understand its core components.

What is the primary role of the Crossplane Control Plane?
To watch Crossplane resources and reconcile infrastructure state with external providers

---

Understanding Custom Resource Definitions
Crossplane extends Kubernetes using Custom Resource Definitions (CRDs).

What do CRDs allow Crossplane to do?

Missing answer !!!!

---

Installing the Crossplane CLI
The Crossplane CLI provides helpful commands for working with Crossplane packages and configurations.

For Linux (amd64):

curl -sL "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh" | sh
sudo mv crossplane /usr/local/bin

Verify the installation:

crossplane --help

You should see the Crossplane CLI help output with various commands like:

beta - Beta commands for Crossplane
xpkg - Manage Crossplane packages
render - Render compositions
Install the Crossplane CLI using the commands above.


Note: The Crossplane CLI is a standalone binary that you can use to manage Crossplane packages and configurations.


```bash
curl -sL "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh" | sh
sudo mv crossplane /usr/local/bin
crossplane --help
```


```bash
curl -sL "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh" | sh
sudo mv crossplane /usr/local/bin
crossplane --help
crossplane CLI downloaded successfully! Run the following commands to finish installing it:

sudo mv crossplane /usr/local/bin
crossplane --help

Visit https://crossplane.io to get started. 🚀
Have a nice day! 👋

Usage: crossplane <command> [flags]

A command line tool for interacting with Crossplane.

Commands:
  xpkg batch         Batch build and push a family of provider packages.
  xpkg build         Build a new package.
  xpkg init          Initialize a new package from a template.
  xpkg install       Install a package in a control plane.
  xpkg push          Push a package to a registry.
  xpkg update        Update a package in a control plane.
  xpkg extract       Extract package contents into a Crossplane cache compatible
                     format. Fetches from a remote registry by default.
  render             Render a composite resource (XR).
  alpha render op    Render an operation.
  alpha render xr    Render a composite resource (XR).
  beta convert composition-environment
                     Convert a Pipeline Composition to use
                     function-environment-configs.
  beta top           Display resource (CPU/memory) usage by Crossplane related
                     pods.
  beta trace         Trace a Crossplane resource to get a detailed output of its
                     relationships, helpful for troubleshooting.
  beta validate      Validate Crossplane resources.
  version            Print the client and server version information for the
                     current context.
  completions        Get shell (bash/zsh/fish) completions. You can source this
                     command to get completions for the login shell. Example:
                     'source <(crossplane completions)'

Flags:
  -h, --help       Show context-sensitive help.
      --verbose    Print verbose logging statements.

Run "crossplane <command> --help" for more information on a command.
```

---

Core Crossplane Concepts - Providers
One of the key concepts in Crossplane is Providers.

What is the purpose of a Crossplane Provider?

To extend Crossplane with support for managing resources on specific platforms

---

Core Crossplane Concepts - Managed Resources
Another important concept is Managed Resources (MRs).

What is a Managed Resource in Crossplane?

A custom resource representing infrastructure in an external system maanged by crossplane

---

Crossplane Workflow
Let's test your understanding of how Crossplane works.

When you create a Crossplane resource in Kubernetes, what happens?

Crossplane watches the resource and reconsiles it by calling provider APIs to manage infrastructure

---

Crossplane Workflow
Let's test your understanding of how Crossplane works.

When you create a Crossplane resource in Kubernetes, what happens?


Exploring Crossplane Resources
Now, let's explore the resources that Crossplane has created.

List all Crossplane-related CRDs:

kubectl get crds | grep crossplane

You should see many CRDs including:

- providers.pkg.crossplane.io
- compositeresourcedefinitions.apiextensions.crossplane.io
- compositions.apiextensions.crossplane.io
- And more!

Check Crossplane configuration:

kubectl get deployment -n crossplane-system

This shows the Crossplane deployments running in the cluster.

Run these commands to familiarize yourself with Crossplane resources.



```bash
kubectl get crds | grep crossplane
clusterusages.protection.crossplane.io                          2026-02-02T01:43:07Z
compositeresourcedefinitions.apiextensions.crossplane.io        2026-02-02T01:43:07Z
compositionrevisions.apiextensions.crossplane.io                2026-02-02T01:43:07Z
compositions.apiextensions.crossplane.io                        2026-02-02T01:43:07Z
configurationrevisions.pkg.crossplane.io                        2026-02-02T01:43:07Z
configurations.pkg.crossplane.io                                2026-02-02T01:43:07Z
cronoperations.ops.crossplane.io                                2026-02-02T01:43:07Z
deploymentruntimeconfigs.pkg.crossplane.io                      2026-02-02T01:43:07Z
environmentconfigs.apiextensions.crossplane.io                  2026-02-02T01:43:07Z
functionrevisions.pkg.crossplane.io                             2026-02-02T01:43:07Z
functions.pkg.crossplane.io                                     2026-02-02T01:43:07Z
imageconfigs.pkg.crossplane.io                                  2026-02-02T01:43:07Z
locks.pkg.crossplane.io                                         2026-02-02T01:43:07Z
managedresourceactivationpolicies.apiextensions.crossplane.io   2026-02-02T01:43:07Z
managedresourcedefinitions.apiextensions.crossplane.io          2026-02-02T01:43:07Z
operations.ops.crossplane.io                                    2026-02-02T01:43:07Z
providerrevisions.pkg.crossplane.io                             2026-02-02T01:43:07Z
providers.pkg.crossplane.io                                     2026-02-02T01:43:07Z
usages.apiextensions.crossplane.io                              2026-02-02T01:43:07Z
usages.protection.crossplane.io                                 2026-02-02T01:43:07Z
watchoperations.ops.crossplane.io                               2026-02-02T01:43:07Z
```


```bash
kubectl get deployment -n crossplane-system
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
crossplane                1/1     1            1           13m
crossplane-rbac-manager   1/1     1            1           13m
```

---

Understanding the Crossplane Namespace
Crossplane is installed in the crossplane-system namespace.

Why is it important to use a dedicated namespace for Crossplane?

To isolate Crossplane components and simplify RBAC and resource management

---

Congratulations!
You have successfully completed Lab 1!

What You've Learned
In this lab, you:

Installed Crossplane on a Kubernetes cluster using Helm
Verified the Crossplane installation and explored its components
Learned about core Crossplane concepts: Control Plane, CRDs, Providers, and Managed Resources
Installed the Crossplane CLI
Understood the Crossplane reconciliation workflow
What's Next?
In Lab 2: Working with Providers, you will:

Learn about Crossplane Providers in depth
Install the Kubernetes Provider
Configure provider credentials using ProviderConfig
Create your first Managed Resources
Provision actual infrastructure using Crossplane
Key Takeaways
Crossplane is a powerful framework that:

Extends Kubernetes to manage infrastructure
Treats infrastructure as code using Kubernetes resources
Provides a unified API for multi-cloud management
Enables platform teams to build self-service abstractions
You're now ready to start provisioning infrastructure with Crossplane!

---















---
