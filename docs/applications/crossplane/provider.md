---
title: Provider
#date:
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