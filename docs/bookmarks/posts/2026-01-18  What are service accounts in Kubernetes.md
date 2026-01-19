---
title: "What are service accounts in Kubernetes?"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://aws.plainenglish.io/what-are-service-accounts-in-kubernetes-01122cc38222"
author:
  - "[[The kube guy]]"
---
<!-- more -->

[Sitemap](https://aws.plainenglish.io/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@thekubeguy)## [AWS in Plain English](https://aws.plainenglish.io/?source=post_page---publication_nav-35e7a49c6df5-01122cc38222---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:76:76/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_sidebar-35e7a49c6df5-01122cc38222---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.

Let’s start of with a simple explanation, Think Kubernetes service accounts as special crew members aboard your ship, each with a specific role, ensuring everything runs smoothly and securely. In this guide, we’re going to understand Kubernetes Service Accounts inside and out.  
Let’s begin..

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9gaMFUcoEszaD7I-Z4ylDA.png)

Understanding service accounts in Kubernetes

Kubernetes Service Accounts are specialised accounts used by applications and services running on Kubernetes to interact with the Kubernetes API. Unlike user accounts managed outside Kubernetes, Service Accounts are managed within the Kubernetes ecosystem, offering a more granular and controlled approach to accessing cluster resources and performing operations.

### Why Service Accounts Matter?

Service Accounts are vital for several reasons:

- **Security:** They enable the principle of least privilege, ensuring applications have only the access they need.
- **Automation:** Service Accounts are essential for automated processes like CI/CD pipelines, where automated tools need to interact with the Kubernetes API.
- **Auditability:** By assigning specific accounts to applications, it’s easier to monitor and audit their actions within the cluster.## [How to Effectively Utilize Kubernetes Namespaces?](https://thekubeguy.com/how-to-effectively-utilize-kubernetes-namespaces-74a612f7f971?source=post_page-----01122cc38222---------------------------------------)

### [Kubernetes Namespaces are essentially labels that partition a cluster into smaller, distinct segments. They allow you…](https://thekubeguy.com/how-to-effectively-utilize-kubernetes-namespaces-74a612f7f971?source=post_page-----01122cc38222---------------------------------------)

[

thekubeguy.com

](https://thekubeguy.com/how-to-effectively-utilize-kubernetes-namespaces-74a612f7f971?source=post_page-----01122cc38222---------------------------------------)

### Creating and Managing Service Accounts

Kubernetes automatically creates a default Service Account within each namespace. However, for enhanced security and control, it’s often necessary to create dedicated Service Accounts for different applications or services.

### Creating a Service Account

To create a Service Account, you can use the following YAML manifest:

```c
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: my-namespace
```

Save this manifest as `service-account.yaml` and apply it using `kubectl apply -f service-account.yaml`. This command creates a Service Account named `my-service-account` in the `my-namespace` namespace.

### Granting Permissions

Permissions are granted to a Service Account through Roles and RoleBindings (or ClusterRoles and ClusterRoleBindings for cluster-wide permissions):

- **Role:** Defines permissions within a namespace.
- **RoleBinding:** Binds a Role to a Service Account within a namespace.
- **ClusterRole:** Similar to Role but for cluster-wide permissions.
- **ClusterRoleBinding:** Binds a ClusterRole to a Service Account for cluster-wide permissions.

Here’s an example of a Role and RoleBinding that grants a Service Account read-only access to Pods within a namespace:

```c
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: my-namespace
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: read-pods
  namespace: my-namespace
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: my-namespace
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## Using Service Accounts in Pods

To use a Service Account in a Pod, specify the account name in the Pod’s YAML:

```c
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
spec:
  serviceAccountName: my-service-account
  containers:
  - name: my-container
    image: my-image
```

This configuration ensures that the Pod operates under the permissions granted to the `my-service-account` Service Account.

### Practical Applications and Best Practices

### CI/CD Integration

Service Accounts are instrumental in CI/CD workflows, allowing automation tools to deploy applications, manage configurations, and execute other Kubernetes operations securely.

### Security Best Practices

- **Principle of Least Privilege**: Always grant Service Accounts the minimum necessary permissions to perform their tasks.
- **Regular Audits:** Regularly review Service Account permissions and usage to ensure compliance with security policies.
- **Use Namespaces:** Leverage namespaces to isolate Service Accounts and limit their scope of influence.

### Conclusion

By understanding their purpose, how to manage them, and best practices for their use, you can enhance the security and efficiency of your Kubernetes deployments.

Also checkout my other articles [here](https://medium.com/@thekubeguy) below, and if you wish to receive these articles further do follow

[The kube guy](https://medium.com/u/54b070394829?source=post_page---user_mention--01122cc38222---------------------------------------)

.

## In Plain English 🚀

*Thank you for being a part of the* [***In Plain English***](https://plainenglish.io/) *community! Before you go:*

- Be sure to **clap** and **follow** the writer ️👏 **️️**
- Follow us: [**X**](https://twitter.com/inPlainEngHQ) **|** [**LinkedIn**](https://www.linkedin.com/company/inplainenglish/) **|** [**YouTube**](https://www.youtube.com/channel/UCtipWUghju290NWcn8jhyAw) **|** [**Discord**](https://discord.gg/in-plain-english-709094664682340443) **|** [**Newsletter**](https://newsletter.plainenglish.io/)
- Visit our other platforms: [**Stackademic**](https://stackademic.com/) **|** [**CoFeed**](https://cofeed.app/) **|** [**Venture**](https://venturemagazine.net/) **|** [**Cubed**](https://blog.cubed.run/)
- More content at [**PlainEnglish.io**](https://plainenglish.io/)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:96:96/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--01122cc38222---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:128:128/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--01122cc38222---------------------------------------)

[Last published just now](https://aws.plainenglish.io/moving-from-static-inventory-to-ansible-dynamic-inventory-using-aws-ec2-f1ec251a79fc?source=post_page---post_publication_info--01122cc38222---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.

I'll help you sail through the ocean of Kubernetes with minimal efforts