---
title: Providers
date: 22-03-26
status: draft
categories:
  - Crossplane
tags:
  - Crossplane
  - Providers
  - ProviderConfig
#source:
#  - 
---



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

