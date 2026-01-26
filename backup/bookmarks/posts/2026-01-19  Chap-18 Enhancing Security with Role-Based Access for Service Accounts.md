---
title: "Chap-18: Enhancing Security with Role-Based Access for Service Accounts"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@maheshwar.ramkrushna/rbac-in-kubernetes-b6c4c23432ef"
author:
  - "[[Ramkrushna Maheshwar]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*4N4HevfDd8lBdxURt9tEoQ.png)

RBAC is all about **managing access to resources.** It’s not about identifying a specific user or authenticating them. With lots of people and resources, it’s difficult to manage a inventory of who can access what. So needed an automated system in place, which can **allow or deny access to a resource.**

With RBAC, Users mapped to roles, roles mapped to set of permissions that opens to the door to access a resource.

## Benefits of RBAC

- Reduced admin load as RBAC largely reduces manual redundant access provisioning
- Reduce costs by cutting manual efforts
- Enhance compliance, as this is more of automation with defined ruleset
- Risk of breach avoided as human error avoided.

In Kubernetes, Role-Based Access Control (RBAC) regulates access to resources based on the roles assigned to users within a given namespace*.*

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*94ru_ZcEdYfovtXB)

RBAC uses four main Kubernetes objects: Role, ClusterRole, RoleBinding, and ClusterRoleBinding.

- **Role** is a set of permissions that grants access to resources in a specific namespace.
- **ClusterRole** grants access to resources across the entire cluster.
- **RoleBinding** associates a set of users or groups with a Role.
- **ClusterRoleBinding** associates a set of users or groups with a ClusterRole.

## RBAC sequence of flow in Kubernetes

1. The User authenticates with Kubernetes.
2. Kubernetes generates an authorization token and sends it to the User.
3. The User tries to access resources.
4. Kubernetes checks the permissions of the User with RBAC.
5. RBAC decides whether the User has permission to access the resources.
6. Kubernetes informs the User about whether access is granted or denied.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Stiq4deN7ixIDIOc)

## Simple Example of implementing an RBAC in Kubernetes

**Step 1: Service Account**

A service account is **a type of non-human account that, in Kubernetes, provides a distinct identity in a Kubernetes** cluster. This identity is useful in various situations, including **authenticating to the API server** or implementing **identity-based security policies.**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rU1MAK0eRI6dsScJfcXGbA.png)

```c
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    kubernetes.io/enforce-mountable-secrets: "true"
  name: testserviceaccount
  namespace: default
```
```c
kubectl create sa testserviceaccount
```

**Step 2:**

```c
kubectl get sa testserviceaccount
```

**Step 3: Role Creation**

Create a file named reader-role.yml and copy the code here

```c
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```
```c
kubectl apply -f reader-role.yml
```

**Step 4: Role Binding to Service Account**

Create a file named role-binding.yml and copy the code here

Note: Cluster Role binding is at the cluster level, so a namespace is not required at a production-grade cluster, but in Minikube, you will need to specify the namespace

```c
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods
subjects:
- kind: ServiceAccount
  name: testserviceaccount
  namespace: default
roleRef:
  kind: ClusterRole
  name: reader
  apiGroup: rbac.authorization.k8s.io
```

Then execute

```c
kubectl apply -f role-binding.yml
```

**Step 5:**

After you complete all the steps, you can log in to the cluster using a service account login and issue a command like the one below to check if the role applied as intended.

```c
kubectl describe pod test-pod  --namespace default
```

**Verify service account has access to default namespace for pod creation:**

```c
kubectl auth can-i --as system:serviceaccount:test:foo get pod -n test

output is: yes

kubectl auth can-i --as system:serviceaccount:test:foo crate pod -n test

output is: no
```

**Reference:** [https://www.youtube.com/watch?v=rMVHtNNEzmE](https://www.youtube.com/watch?v=rMVHtNNEzmE)

DevOps / MLOPS / DLOPS Engineer

## More from Ramkrushna Maheshwar

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--b6c4c23432ef---------------------------------------)