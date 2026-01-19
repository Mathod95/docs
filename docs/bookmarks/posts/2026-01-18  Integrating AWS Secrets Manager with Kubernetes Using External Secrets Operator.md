---
title: "Integrating AWS Secrets Manager with Kubernetes Using External Secrets Operator"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/hostspaceng/integrating-aws-secrets-manager-with-kubernetes-using-external-secrets-operator-9a909e32ccf8"
author:
  - "[[Teslim Salu]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)## [HostSpace Cloud Solutions](https://medium.com/hostspaceng?source=post_page---publication_nav-dd143266f35e-9a909e32ccf8---------------------------------------)

[![HostSpace Cloud Solutions](https://miro.medium.com/v2/resize:fill:38:38/1*7uJ6feUkhJEoHkyacRqqBg.jpeg)](https://medium.com/hostspaceng?source=post_page---post_publication_sidebar-dd143266f35e-9a909e32ccf8---------------------------------------)

Streamline your deployment process and empower your teams with our DevOps as a Service solutions

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*MPCBPtHDo-16364R.png)

External Secrets

## Introduction

Traditionally, secrets, such as API keys, passwords, and certificates, are managed within Kubernetes itself. This approach poses security and operational risks. Storing sensitive secrets alongside application infrastructure increases the risk of exposure. Additionally, manually updating secrets is error-prone and inefficient, particularly in large or dynamic environments.

## The External Secrets Operator

The External Secrets Operator mitigates these risks by securely integrating Kubernetes clusters with external secrets management systems, including AWS Secrets Manager, HashiCorp Vault, and Azure Key Vault. This article focuses on leveraging the External Secrets Operator with AWS Secrets Manager to efficiently fetch secrets.

## Prerequisites

- AWS Account
- An Amazon EKS cluster
- ArgoCD installed on your cluster for GitOps-style deployment of *external secrets operator -* [documentation](https://faun.pub/continuous-deployments-of-kubernetes-applications-using-argo-cd-gitops-helm-charts-9df917caa2e4)
- AWS CLI installed
- KUBECTL installed
1. Create an IAM role:

First, create an IAM role. You’ll be specifying an IAM username to associate with the access key that’ll be used later. Use the following trust policy., replacing *<ACCOUNT-ID>* and *<IAM-USER-NAME>* with your details.

```c
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<ACCOUNT-ID>:user/<IAM-USER-NAME>“
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

2\. Create a IAM Policy

Next, create an IAM policy that allows the necessary actions for the External Secrets Operator to interact with AWS Secrets Manager. Replace *<ACCOUNT-ID>* with your AWS account ID.

```c
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetResourcePolicy",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:ListSecretVersionIds"
      ],
      "Resource": [
        "arn:aws:secretsmanager:<REGION>:<ACCOUNT-ID>:secret:*"
      ]
    }
  ]
}
```

3\. Install External Secrets Operator

To install the External Secrets Operator, create a file named external-secrets-operator.yml In this file, specify the details of your EKS cluster and the IAM role created earlier. Push this YAML file to the repository from which [*ArgoCd*](https://faun.pub/continuous-deployments-of-kubernetes-applications-using-argo-cd-gitops-helm-charts-9df917caa2e4) syncs your deployment manifests.

> *external-secrets-operator.yml*

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: external-secrets
  namespace: external-secrets
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  destination:
    namespace: external-secrets
    server: https://kubernetes.default.svc
  project: default
  sources:
  - repoURL: https://charts.external-secrets.io
    chart: external-secrets
    targetRevision: 0.9.4
    helm:
      values: |         
        replicaCount: 1
        fullnameOverride: "external-secrets"
        clusterName: <cluster name>
        clusterEndpoint: ${dependency.eks.outputs.cluster_endpoint}
        serviceAccount:
         name: external-secrets-operator
         annotations:
          eks.amazonaws.com/role-arn: <IAM ROLE>

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=false
```

4\. Create a SecretStore

Before creating a SecretStore, store your AWS access key and secret-key in a Kubernetes secret within your cluster. Create a file named *creds.txt* replacing *<ACCESS\_KEY>* and *<SECRET\_ACCESS\_KEY>* with your actual credentials.

> *creds.txt*

```c
AWS_ACCESS_KEY_ID=<ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<SECRET_ACCESS_KEY>
```

Then, use the following command to create the Kubernetes secret

```c
kubectl create secret generic awssm-secrets \\
  --from-literal=access-key=$(grep AWS_ACCESS_KEY_ID creds.txt | cut -d= -f2) \\
  --from-literal=secret-access-key=$(grep AWS_SECRET_ACCESS_KEY creds.txt | cut -d= -f2) \\
  --namespace external-secret\
```

> *secret-store.yml*

```c
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secretsmanager
  namespace: external-secrets
spec:
  provider:
    aws:
      service: SecretsManager
      role: arn:aws:iam::<ACCOUNT-ID>:role/<IAM ROLE>
      region: eu-west-1
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: awssm-secret
            key: access-key
          secretAccessKeySecretRef:
            name: awssm-secret
            key: secret-access-key
```

now let’s apply this…

> kubectl apply -f secret-store.yml

let’s check if out secrets store has been created and configured.

> kubectl get secretstore -n external-secrets

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*haQiXU7I6o4ngFgy63SUiQ.png)

kubectl get secretstore -n external-secrets

after creating the secret store, we’ll now proceed to pull an already saved secret from AWS Secrets Manager.

> secrets.yml

```c
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: secret
  namespace: external-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: secrets-manager-secret
    creationPolicy: Owner
  data:
    - secretKey: <secret-name>
      remoteRef:
        key: <secret-key>
    - secretKey: <secret-name>
      remoteRef:
        key: <secret-key>
```

Make sure to replace **secret-name** with your Secrets Manager Secrets name and **secret-key** as the name it’ll save it as on your secret store.

The above YML file stores the secret on the target **secrets-manager-secret** on the namespace **external-secrets**.

For every 1hr it refreshes and updates the secrets from the SecretStore.

It fetches the species secret from SecretStore **aws-secretsmanager** and stores it in the target secret **secrets-manager-secret**.

Use the provided commands to check that your AWS Secrets Manager secret has been successfully retrieved and stored within your Kubernetes cluster

> kubectl get secret secrets-manager-secret -n external-secrets

you’ll get the output below

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*XWiNdVRacf-wf8lq84EZng.png)

## Conclusion

In this guide, we have demonstrated how to automate the management of secrets in Kubernetes using External Secrets Operator and AWS Secrets Manager. This approach does not only enhance the security of secret management within Kubernetes but also simplifies and automates updates making it more efficient and manageable for DevOps teams. Adopting this method ensures that sensitive information is kept out of your application’s infrastructure and is dynamically manageable, scaling seamlessly with your environment’s needs.

[![HostSpace Cloud Solutions](https://miro.medium.com/v2/resize:fill:48:48/1*7uJ6feUkhJEoHkyacRqqBg.jpeg)](https://medium.com/hostspaceng?source=post_page---post_publication_info--9a909e32ccf8---------------------------------------)

[![HostSpace Cloud Solutions](https://miro.medium.com/v2/resize:fill:64:64/1*7uJ6feUkhJEoHkyacRqqBg.jpeg)](https://medium.com/hostspaceng?source=post_page---post_publication_info--9a909e32ccf8---------------------------------------)

[Last published Apr 15, 2025](https://medium.com/hostspaceng/building-ai-agents-with-google-adk-fastapi-and-mcp-031447925896?source=post_page---post_publication_info--9a909e32ccf8---------------------------------------)

Streamline your deployment process and empower your teams with our DevOps as a Service solutions

## More from Teslim Salu and HostSpace Cloud Solutions

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--9a909e32ccf8---------------------------------------)