---
title: Managed Resources
date: 22-03-2026
status: draft
categories:
  - Crossplane
tags:
  - Crossplane
  - ManagedResources
  - MR
source:
  - https://docs.crossplane.io/latest/managed-resources/managed-resources/#managementpolicies
---

### What are Managed Resources?
**Managed Resources** are Kubernetes custom resources that represent individual infrastructure components in external systems.

Characteristics:

- 1:1 mapping with external resources
- Can be either cluster-scoped or namespaced (namespaced support added in v2)
- Full lifecycle management (create, update, delete)
- Status reflects actual state

### Structure of a Managed Resource
```yaml
apiVersion: <provider-api-group>/<version>
kind: <ResourceType>
metadata:
  name: <resource-name>
spec:
  forProvider:
    # Provider-specific configuration
  providerConfigRef:
    name: <provider-config-name>
status:
  conditions:
    # Resource health status
  atProvider:
    # Provider-specific status fields
```

**Example: S3 Bucket**
```yaml
apiVersion: s3.aws.crossplane.io/v1beta1
kind: Bucket
metadata:
  name: my-app-bucket
spec:
  forProvider:
    region: us-east-1
    acl: private
  providerConfigRef:
    name: aws-config
```
After creation:
```yaml
status:
  conditions:
  - type: Ready
    status: "True"
  - type: Synced
    status: "True"
  atProvider:
    arn: arn:aws:s3:::my-app-bucket
    region: us-east-1
```

### Resource Status Conditions

- Ready: Resource exists and is available for use
- Synced: Crossplane has successfully reconciled the resource

## Check resource status

```bash
kubectl get bucket my-app-bucket
# NAME            READY   SYNCED   AGE
# my-app-bucket   True    True     5m
```

---

## Kubernetes Provider
The Special Case: Managing Kubernetes Resources
The Kubernetes Provider allows Crossplane to manage Kubernetes resources as managed resources.

Why is this useful?

Create Kubernetes resources declaratively via Crossplane
Build platform abstractions that provision both infrastructure and Kubernetes resources
Manage resources in remote clusters
Apply consistent governance and policies
The Object Resource Type
Unlike other providers with specific types (Bucket, Instance), the Kubernetes provider uses a generic Object type:

apiVersion: kubernetes.crossplane.io/v1alpha2
kind: Object
metadata:
  name: sample-namespace
spec:
  forProvider:
    manifest:
      # Any Kubernetes resource manifest goes here
      apiVersion: v1
      kind: Namespace
      metadata:
        name: my-namespace
  providerConfigRef:
    name: kubernetes-provider
Why use Object?

Kubernetes has too many resource types for individual CRDs
Object is flexible and can represent any Kubernetes resource
The actual resource type is specified in manifest.kind
Object Examples
Creating a Namespace:

apiVersion: kubernetes.crossplane.io/v1alpha2
kind: Object
spec:
  forProvider:
    manifest:
      apiVersion: v1
      kind: Namespace
      metadata:
        name: app-namespace
        labels:
          team: platform
Creating a ConfigMap:

apiVersion: kubernetes.crossplane.io/v1alpha2
kind: Object
spec:
  forProvider:
    manifest:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: app-config
        namespace: app-namespace
      data:
        database_url: postgres://db:5432
        cache_enabled: "true"
RBAC Requirements
The Kubernetes provider's ServiceAccount needs permissions to manage resources:

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: provider-kubernetes-access
rules:
  - apiGroups: [""]
    resources: ["namespaces", "configmaps", "secrets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
Without proper RBAC, the provider cannot create resources.

## Resource Lifecycle

### Creation Flow:
When you create a managed resource:

```bash
1. User applies managed resource YAML
         ↓
2. Kubernetes stores resource in etcd
         ↓
3. Provider controller detects new resource
         ↓
4. Controller calls external API to create resource
         ↓
5. Controller updates status (Ready, Synced)
         ↓
6. Continuous reconciliation begins
```

### Update Flow:
When you modify a managed resource:

```bash
1. User updates resource spec
         ↓
2. Provider detects change
         ↓
3. Provider calculates diff
         ↓
4. Provider updates external resource
         ↓
5. Status updated to reflect changes
```
### Deletion Flow:
When you delete a managed resource:

```bash
1. User runs: kubectl delete <resource>
2. Kubernetes adds deletionTimestamp
3. Provider controller detects deletion
4. Provider deletes external resource
5. Provider removes finalizer
6. Kubernetes removes resource from etcd
```

### managementPolicy

<!--
### deletionPolicy

Control what happens to external resources when managed resource is deleted:

```yaml
spec:
  deletionPolicy: Delete  # Delete external resource (default)
  # OR
  deletionPolicy: Orphan  # Keep external resource, only delete managed resource
```
-->

## Reconciliation

Providers continuously reconcile resources:

**Why?**

- Detect drift (manual changes outside Crossplane)
- Ensure actual state matches desired state
- Handle transient failures
- Update status information

**Reconciliation Frequency:**

- Triggered by changes to the resource
- Periodic checks (default: every 1 minute)
- Can be configured per provider

**Drift Detection Example:**

1. User creates bucket with ACL: private
2. Someone manually changes ACL in AWS console to public
3. Crossplane detects drift during next reconciliation
4. Crossplane changes ACL back to private
5. Desired state is restored

## Key Takeaways

- Providers extend Crossplane with platform-specific capabilities
- ProviderConfig defines authentication for providers
- Managed Resources represent individual infrastructure components
- Object type in Kubernetes provider is flexible and can represent any Kubernetes resource
- Lifecycle Management is fully automated: create, update, delete, reconcile
- RBAC must be configured for Kubernetes provider to manage resources

## Quick Reference

```bash
# Install a provider
kubectl apply -f provider.yaml

# Check provider status
kubectl get providers

# Create ProviderConfig
kubectl apply -f providerconfig.yaml

# List all managed resources
kubectl get managed

# Check specific resource
kubectl get object sample-namespace

# View resource details
kubectl describe object sample-namespace

# Delete a managed resource
kubectl delete object sample-namespace
```