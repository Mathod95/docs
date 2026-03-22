---
title: ProviderConfig
#date:
status: draft
categories:
  - Crossplane
tags:
  - Crossplane
  - ProviderConfig
source:
  - https://docs.crossplane.io/v2.2/packages/providers/#provider-configuration
---

## Provider configuration

The ProviderConfig determines settings the Provider uses communicating to the external provider. Each Provider determines available settings of their ProviderConfig.

Provider authentication is usually configured with a ProviderConfig. For example, to use basic key-pair authentication with Provider AWS a ProviderConfig spec defines the credentials and that the Provider pod should look in the Kubernetes Secrets objects and use the key named aws-creds.

```yaml linenums="1" title="providerConfig.yaml"
apiVersion: aws.m.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  namespace: default
  name: aws-provider
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-creds
      key: creds
```

!!! warning "Authentication configuration may be different across Providers."
    Read the documentation on a specific Provider for instructions on configuring authentication for that Provider.

### ProviderConfig types

The AWS provider supports two types of ProviderConfig resources:

**ProviderConfig** (namespace-scoped):
```yaml
apiVersion: aws.m.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  namespace: default
  name: my-config
# Applies only to MRs in the same namespace
```

**ClusterProviderConfig** (cluster-wide):
```yaml
apiVersion: aws.m.upbound.io/v1beta1
kind: ClusterProviderConfig
metadata:
  name: my-cluster-config
# Applies to MRs across all namespaces
```

When referencing any ProviderConfig, managed resources must specify both `name` and `kind`:
```yaml
spec:
  providerConfigRef:
    name: my-cluster-config
    kind: ClusterProviderConfig
```

```yaml
spec:
  providerConfigRef:
    name: my-config
    kind: ProviderConfig  # References namespaced ProviderConfig
```

If you omit `providerConfigRef` entirely, it defaults to:
```yaml
spec:
  providerConfigRef:
    name: default
    kind: ClusterProviderConfig
```

ProviderConfig objects apply to individual Managed Resources. A single Provider can authenticate with multiple users or accounts through ProviderConfigs.

Each account’s credentials tie to a unique ProviderConfig. When creating a managed resource, attach the desired ProviderConfig.

For example, two AWS ProviderConfigs, named user-keys and admin-keys use different Kubernetes secrets.

```yaml linenums="1"
apiVersion: aws.m.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  namespace: default
  name: user-keys
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: my-key
      key: secret-key
```

```yaml linenums="1"
apiVersion: aws.m.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  namespace: default
  name: admin-keys
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: admin-key
      key: admin-secret-key
```

Apply the ProviderConfig when creating a managed resource.

This creates an AWS `Bucket` resource using the user-keys ProviderConfig.

```yaml {label="user-bucket"}
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  namespace: default
  name: user-bucket
spec:
  forProvider:
    region: us-east-2
  providerConfigRef:
    name: user-keys
    kind: ProviderConfig
```

This creates a second `Bucket` resource using the admin-keys ProviderConfig.

```yaml {label="admin-bucket"}
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  namespace: default
  name: admin-bucket
spec:
  forProvider:
    region: us-east-2
  providerConfigRef:
    name: admin-keys
    kind: ProviderConfig
```