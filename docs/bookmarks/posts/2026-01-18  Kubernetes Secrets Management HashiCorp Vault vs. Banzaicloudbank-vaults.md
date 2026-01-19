---
title: "Kubernetes Secrets Management: HashiCorp Vault vs. Banzaicloud/bank-vaults"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.devops.dev/kubernetes-secrets-management-hashicorp-vault-vs-banzaicloud-bank-vaults-5a793c4de18d"
author:
  - "[[Denis Gorokhov]]"
---
<!-- more -->

[Sitemap](https://blog.devops.dev/sitemap/sitemap.xml)## [DevOps.dev](https://blog.devops.dev/?source=post_page---publication_nav-33f8b2d9a328-5a793c4de18d---------------------------------------)

[![DevOps.dev](https://miro.medium.com/v2/resize:fill:76:76/1*3SZtM9yhQyfh-dfWk5gGFw.jpeg)](https://blog.devops.dev/?source=post_page---post_publication_sidebar-33f8b2d9a328-5a793c4de18d---------------------------------------)

[Devops.dev](http://devops.dev/) is a community of DevOps enthusiasts sharing insight, stories, and the latest development in the field.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*ktO6R-WFKGdQXCjv)

**Introduction**

In my quest to secure our IT infrastructure, I was faced with a critical decision: choosing the right secret management tool. The choice boiled down to two prominent solutions: HashiCorp Vault and Banzaicloud/bank-vaults. Despite their growing popularity and essential roles in safeguarding sensitive data, I found a surprising lack of comprehensive comparisons between them, especially from a practical, real-world application perspective.

[**HashiCorp Vault**](https://github.com/hashicorp/vault) emerged as a strong contender with its extensive features for securely handling secrets such as tokens, passwords, and certificates. Its robust security mechanisms and flexibility, supporting multiple storage backends and secret engines, made it a compelling choice for a diverse set of IT environments.

Meanwhile, [**Banzaicloud/bank-vaults**](https://bank-vaults.dev/docs/) caught my attention as a specialized enhancer for HashiCorp Vault in Kubernetes environments. It promised to simplify many of the complexities involved in managing Vault in Kubernetes, offering features like secure secret injection, automatic unsealing, and sophisticated access management.

Before we dive in, here’s a brief outline of what we’ll cover in this article:

**Banzaicloud/bank-vaults**

- **Components**: Detailing the key components that make up Banzaicloud/bank-vaults and how they operate within Kubernetes.
- **Installation**: A guide on how to install and configure Banzaicloud/bank-vaults in a Kubernetes environment.
- **Advantages**: Discussing the benefits and unique features that Banzaicloud/bank-vaults brings to secret management in Kubernetes.
- **Disadvantages**: Addressing potential drawbacks, limitations, and considerations when implementing Banzaicloud/bank-vaults.

**HashiCorp Vault**

- **Components**: Describing the core components of HashiCorp Vault and their roles in secret management.
- **Installation**: Outlining the steps and considerations for installing HashiCorp Vault in various environments, including Kubernetes.
- **Advantages**: Highlighting the strengths and key features of HashiCorp Vault that make it a preferred choice for secret management.
- **Disadvantages**: Discussing any challenges, complexities, or limitations associated with using HashiCorp Vault, particularly in Kubernetes.

**Now, let’s get started with a detailed exploration.**

## Banzaicloud/bank-vaults

**Components:** Banzaicloud/bank-vaults complements HashiCorp Vault by enhancing its capabilities and simplifying its integration within Kubernetes environments. It’s not a complete replacement for HashiCorp Vault but rather an extension that facilitates easier installation, configuration, and management. The key components deployed by Banzaicloud/bank-vaults typically include:

1. **vault-secrets-webhook**: This pod is responsible for the injection of Vault secrets into applications running in Kubernetes. It operates using annotations and environment variables, ensuring that no sensitive data is stored on disk or etcd. All secrets are kept in memory and are accessible only to the processes that request them.
2. **vault-configurer**: This pod contains the bank-vaults container and is crucial for monitoring CRDs and automatically applying configuration changes, ensuring that your Vault instance remains up-to-date with your desired state.
3. **vault**: This primary pod houses the Vault containers and additional containers that are critical for the operation of the system, including:
- **config-templating**: An initialization container that assists in generating configuration files.
- **vault**: The main container holding the Vault component responsible for storing and managing secrets.
- **bank-vaults**: The primary container for automating the initialization, unsealing, and configuration of Vault. It contains a command-line utility written in Go.
- **valero-fsfreeze (optional)**: A container responsible for creating backups of Vault. This can be disabled if backup functionality is not required.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*cU7vGCRZdz7LfcIfAYpx5w.png)

Banzaicloud/bank-vaults components

**Installation:** The installation of Banzaicloud/bank-vaults is facilitated through [Helm chart](https://bank-vaults.dev/docs/installing/#deploy-with-helm) and [custom resource definitions (CRDs)](https://bank-vaults.dev/docs/installing/#deploy-operator).

**Advantages:** Banzaicloud/bank-vaults offers several benefits for secret management in Kubernetes:

- **Autounseal**: Supports automatic unsealing using a secret that stores unseal keys, typically named `vault-unseal-keys`. This is configured in the `spec.unsealConfig` parameter of the Vault CRD.
- **Infrastructure as Code (IaC)**: Allows managing Vault’s configuration through CRDs in YAML format. This is particularly beneficial when used with tools like [Flux](https://github.com/fluxcd/flux2) / [ArgoCD](https://github.com/argoproj/argo-cd) for managing changes in Vault’s configuration. The `externalConfig` section of the CRD can define policies, roles, authentication methods, secret engines, and other Vault settings.

**Disadvantages:** However, there are some considerations and potential drawbacks to using Banzaicloud/bank-vaults:

1. **Autounseal Issues**: There have been instances where the vault container failed to start due to unseal errors, with the bank-vaults container unable to find specific unseal keys. [This issue](https://github.com/banzaicloud/bank-vaults/issues/1802) is documented and discussed in the community but can pose a significant challenge in production environments.
2. **Updates and Compatibility**: Delays in updates and compatibility issues with newer versions of Vault or Kubernetes APIs might occur, which can affect the stability and security of your setup.
3. **Additional Dependencies**: The use of extra components can increase the complexity and potential points of failure within your system.
4. **Support and Community**: As a third-party product, the support and community around Banzaicloud/bank-vaults may not be as extensive or active as the official HashiCorp Vault, potentially making troubleshooting and assistance more challenging.

## HashiCorp Vault

**Installation through the Official Helm Chart:** HashiCorp Vault can be easily deployed in Kubernetes using its [official Helm chart](https://github.com/hashicorp/vault-helm). The following components are typically created by default when deploying HashiCorp Vault with the official Helm chart:

1. **Vault StatefulSet**: This contains one or more Vault pods. Each pod houses a single Vault container responsible for managing and storing secrets.
2. **Vault ConfigMap**: A ConfigMap holding the Vault configuration, including storage parameters, authentication, auditing settings, and other configurations.
3. **Vault Service**: A Kubernetes service that provides access to the Vault pods within the cluster. It usually uses a ClusterIP or LoadBalancer service type, depending on the configuration chosen.
4. **Vault Ingress (optional)**: If enabled, it creates a Kubernetes Ingress for external access to Vault. This is often used in conjunction with TLS certificates to ensure secure access to Vault from outside the cluster.

**Advantages:**

- **Developer and Maintainer Support**: Developed and maintained by the official HashiCorp team, ensuring reliable updates and official support.
- **Independence from Kubernetes**: While it’s optimized for Kubernetes, standard HashiCorp Vault can also be deployed on virtual machines, providing flexibility in deployment environments.

**Disadvantages:**

- **Infrastructure as Code (IaC)**: The standard installation of Vault supports IaC primarily through [Terraform](https://registry.terraform.io/providers/hashicorp/vault/latest/docs). While powerful, this might limit options for teams using other IaC tools.

## Conclusion

As a conclusion to our exploration of HashiCorp Vault and Banzaicloud/bank-vaults, the following table provides a concise comparison based on various factors:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Bef1fvB-Iad_dumPS7XssA.png)

This table summarizes the key differences and similarities between HashiCorp Vault and Banzaicloud/bank-vaults. While HashiCorp Vault offers a more traditional and widely supported approach with flexibility in deployment and strong IaC integration via Terraform, Banzaicloud/bank-vaults is tailored specifically for Kubernetes environments, offering ease of setup and management with its integration into CRDs and automatic unsealing features. However, this specialization comes with the caveat of being a third-party product and having additional dependencies.

Ultimately, the choice between HashiCorp Vault and Banzaicloud/bank-vaults will depend on your specific needs, infrastructure, and the environment in which you are working. Consider the factors most important to your organization, such as ease of use, support, and integration capabilities, to make the most informed decision.

[![DevOps.dev](https://miro.medium.com/v2/resize:fill:96:96/1*3SZtM9yhQyfh-dfWk5gGFw.jpeg)](https://blog.devops.dev/?source=post_page---post_publication_info--5a793c4de18d---------------------------------------)

[![DevOps.dev](https://miro.medium.com/v2/resize:fill:128:128/1*3SZtM9yhQyfh-dfWk5gGFw.jpeg)](https://blog.devops.dev/?source=post_page---post_publication_info--5a793c4de18d---------------------------------------)

[Last published 1 day ago](https://blog.devops.dev/mongodb-installation-replica-set-configuration-on-linux-8913b5e02318?source=post_page---post_publication_info--5a793c4de18d---------------------------------------)

[Devops.dev](http://devops.dev/) is a community of DevOps enthusiasts sharing insight, stories, and the latest development in the field.

## More from Denis Gorokhov and DevOps.dev

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--5a793c4de18d---------------------------------------)