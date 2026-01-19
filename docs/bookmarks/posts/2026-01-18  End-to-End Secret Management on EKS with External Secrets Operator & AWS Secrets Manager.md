---
title: "End-to-End Secret Management on EKS with External Secrets Operator & AWS Secrets Manager"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@sandeshnavsare1/end-to-end-secret-management-on-eks-with-external-secrets-operator-aws-secrets-manager-20df3129b29f"
author:
  - "[[Sandesh Navsare]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

While researching secret management on Kubernetes, I sifted through countless docs and YouTube tutorials — but never found a single end-to-end walkthrough that showed how to wire up AWS Secrets Manager (or HashiCorp Vault) all the way through to a running application. It felt fragmented and confusing.

In this hands-on lab, I’ll show you every step: from storing credentials in AWS Secrets Manager, to syncing them into your cluster with the External Secrets Operator (ESO), to consuming them in a MySQL StatefulSet, and even dynamically provisioning storage with the AWS EBS CSI driver. If you’ve struggled with “vault → Kubernetes → app” workflows, this practical guide is for you. Let’s dive in!

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rgoWRP_QV8bcWCIpoQDsBQ.png)

## Prerequisites

Before we begin, make sure you have:

1. **An AWS Secrets Manager secret** (e.g. `mysql-credentials`) containing at least two key/value pairs: (ussername, password )  
	This is the source of truth that ESO will sync into Kubernetes.
2. **An EKS cluster** (we’ll call ours `lab2-eks`).
3. **kubectl**, **eksctl**, and **Helm 3** installed and configured to talk to your cluster.
4. **AWS CLI** configured with an IAM principal that can:
5. Read your AWS Secrets Manager secret
6. Manage EKS (for IRSA & node scaling)
7. (Optional for storage) **IAM & OIDC provider** set up on your cluster to allow IRSA for the AWS EBS CSI driver addon.

## Step 1: Install the External Secrets Operator

**Add & update the Helm chart repo**

- `helm repo add external-secrets https://charts.external-secrets.io helm repo update`

**Deploy ESO with CRDs: Which we gonna needed in further to Define SecretSore and ExternalSecret**

```c
helm upgrade --install external-secrets external-secrets/external-secrets \
  --namespace external-secrets --create-namespace \
  --set installCRDs=true
```

**Verify the CRDs are present:**

```c
kubectl get crd | grep external-secrets
# → secretstores.external-secrets.io
#   clustersecretstores.external-secrets.io
#   externalsecrets.external-secrets.io
```

## Step 2: Store AWS Credentials in Kubernetes

We’ll give ESO permission to call AWS Secrets Manager by storing access keys in a Kubernetes Secret.

```c
kubectl create namespace external-secrets
kubectl -n external-secrets create secret generic aws-credentials \
  --from-literal=access-key-id=<AWS_KEY_ID> \
  --from-literal=secret-access-key=<AWS_SECRET>
```

## Step 3: Define a ClusterSecretStore

Create `cluster-secretstore.yml`:

```c
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: aws-secretstore
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-credentials
            key: access-key-id
            namespace: external-secrets
          secretAccessKeySecretRef:
            name: aws-credentials
            key: secret-access-key
            namespace: external-secrets
```

Apply it:

```c
kubectl apply -f cluster-secretstore.yml
```

## Step 4: Create an ExternalSecret

Next, map a Secrets Manager entry into a native Kubernetes Secret.

```c
# external-secret-mysql.yml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: mysql-credentials-es
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretstore
    kind: ClusterSecretStore
  target:
    name: mysql-credentials  # Secret name used in AWS secret namager
    creationPolicy: Owner
  data:
    - secretKey: username
      remoteRef:
        key: arn:aws:secretsmanager:us-east-1:123456789012:secret:mysql-credentials
        property: username
    - secretKey: password
      remoteRef:
        key: arn:aws:secretsmanager:us-east-1:123456789012:secret:mysql-credentials 
        property: password

# User your ARN id of AWS secret Manager for Key refference.
```
```c
kubectl apply -f external-secret-mysql.yml
```

Check its status:

```c
kubectl describe externalsecret mysql-credentials-es -n default
```

## Step 5: Verify the Secret Sync

```c
kubectl get secret mysql-credentials -n default -o yaml
```

You should see base64-encoded `username` and `password`. Decode to verify:

```c
echo "<base64-username>" | base64 --decod
```

## Step 6: Install the AWS EBS CSI Driver & Migrate to IRSA

```c
eksctl create addon \
  --name aws-ebs-csi-driver \
  --cluster lab2-eks

# - Missing Step! -
eksctl utils migrate-to-pod-identity \
  --cluster lab2-eks \
  --name aws-ebs-csi-driver
```

This IRSA migration gives the CSI driver pod permission to create EBS volumes. Mandatory if you want to use Persistent Volume claim for your deployment application.

## Step 7: Deploy MySQL as a StatefulSet

Create `statefulset.yml`:

```c
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: default
spec:
  clusterIP: None
  ports:
    - name: mysql
      port: 3306
  selector:
    app: mysql
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: default
spec:
  serviceName: mysql
  replicas: 1
  selector:
    matchLabels: { app: mysql }
  template:
    metadata:
      labels: { app: mysql }
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports: [{ containerPort: 3306, name: mysql }]
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-credentials
                  key: password
            - name: MYSQL_USER
              valueFrom:
                secretKeyRef:
                  name: mysql-credentials
                  key: username
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-credentials
                  key: password
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        storageClassName: gp2           
        accessModes: ["ReadWriteOnce"]
        resources:
          requests: { storage: 10Gi }
   # Specify storage class name assgined to your Cluster by Verifying using
   # kubectl get storageclass
```
```c
kubectl apply -f statefulset.yml
kubectl get pods -l app=mysql
```

Your pod will stay **Pending** until storage is configured.

## Step 8:Validate the Running MySQL Application & Secrets

Once your pod transitions to **Running**, your MySQL application is now up and serving. To confirm that the secrets from AWS Secrets Manager were injected correctly, exec into the container and use the injected env vars:

```c
# 1. Get the pod name
kubectl get pod -l app=mysql
```
```c
# 2. Exec and show all databases
kubectl exec -it $POD -- bash -c '
  echo "Listing all databases:";
  mysql \
    -u"$MYSQL_USER" \
    -p"$MYSQL_PASSWORD" \
    -e "SHOW DATABASES;"
'
```

You should see output similar to:

```c
Listing all databases:
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
```

This confirms your pod picked up the AWS-provided credentials and that MySQL is serving correctly.

## 🎉 Conclusion

You’ve just built a fully automated secret-management pipeline:

1. **AWS Secrets Manager** holds your credentials
2. **External Secrets Operator** syncs them into Kubernetes
3. **MySQL StatefulSet** consumes them via native `Secret` references
4. **AWS EBS CSI driver + IRSA** dynamically provisions persistent volumes

No hard-coded credentials, no manual volume provisioning, and a clear, repeatable workflow. I hope this guide saves you hours of frustration — happy deploying!🚀

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--20df3129b29f---------------------------------------)