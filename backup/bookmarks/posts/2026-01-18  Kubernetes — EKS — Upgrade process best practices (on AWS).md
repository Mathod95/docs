---
title: "Kubernetes — EKS — Upgrade process best practices (on AWS)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/atmosly/kubernetes-eks-upgrade-process-best-practices-on-aws-aed30e16bac1"
author:
  - "[[Ankush Madaan]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)## [Atmosly](https://medium.com/atmosly?source=post_page---publication_nav-e7498643eda9-aed30e16bac1---------------------------------------)

[![Atmosly](https://miro.medium.com/v2/resize:fill:76:76/1*4j2JyC8HPzDTaFs9c90vyA.png)](https://medium.com/atmosly?source=post_page---post_publication_sidebar-e7498643eda9-aed30e16bac1---------------------------------------)

Self Service Devops platform

Kubernetes, the popular container orchestrator, is a rapidly evolving platform. There are new version releases every few months, each bringing new features, bug fixes, and security updates. To stay up to date, users need to upgrade their Elastic Kubernetes Service (EKS). While upgrading your Elastic Kubernetes Service (EKS) is a critical practice that requires best practices, we have put this article together to help you learn the best practices of Elastic Kubernetes Service (EKS) upgrades. It also addresses, not only the importance of EKS upgrades. This is where [**Atmosly**](http://atmosly.com/) comes in, offering an engineering platform that streamlines the entire EKS lifecycle, including creation, deployment, and upgrades — all with just a few clicks.

## Amazon EKS and Kubernetes Version Releases

Often abbreviated as K8s, Kubernetes is an open-source platform designed to automate deploying, scaling, and operating application containers. It allows you to build, deploy, and manage containerized applications in a highly efficient and scalable manner. Kubernetes eliminates many of the manual processes involved in deploying and scaling containerized applications, making it easier to manage applications in a dynamic environment.

[**Kubernetes**](https://www.atmosly.com/blog/kubernetes-updates-and-maintenance-minimizing-downtime-challenges) provides a robust platform for managing containerized applications at scale. Amazon Elastic Kubernetes Service (EKS) on the other hand is a fully managed Kubernetes service that makes it easy to deploy, manage, and scale containerized applications using Kubernetes on Amazon Web Services (AWS). With Amazon EKS, you can run Kubernetes on AWS without installing, operating, and maintaining your own Kubernetes control plane or nodes. Amazon EKS provides a highly available and scalable Kubernetes control plane, and you only pay for the compute and storage resources consumed by your [**Kubernetes clusters**](https://www.atmosly.com/blog/mastering-kubernetes-troubleshooting-atmosly).

## The Need for Kubernetes Version Releases

As Kubernetes evolves, new features, enhancements, and bug fixes are introduced in each new version. These updates address issues, improve performance, and introduce new capabilities to the platform. Amazon EKS must follow the upstream Kubernetes release cycle to ensure that its users have access to the latest features and improvements.

The Kubernetes community releases new minor versions (such as 1.29) approximately once every four months. Amazon Elastic Kubernetes Service (EKS) follows the upstream release and deprecation cycle for these minor versions, ensuring compatibility and support for its users.

## Standard and Extended Support

When a new Kubernetes version becomes available in Amazon EKS, it is recommended to proactively update your clusters to use the latest available version. Each minor version in Amazon EKS is under standard support for the first 14 months after its release. After the standard support period ends, the version enters extended support for the next 12 months. During extended support, you can stay at a specific Kubernetes version for a longer period, but at an additional cost per cluster hour.

If you haven’t updated your cluster before the extended support period ends, your cluster is auto-upgraded to the oldest currently supported extended version. It’s important to stay aware of the support timelines for each Kubernetes version to ensure your clusters remain supported.

## Creating Clusters with Specific Versions

When creating an Amazon EKS cluster, you can choose the Kubernetes version. It’s recommended to use the latest available version to take advantage of the latest features and improvements. However, if your application requires a specific version, you can select an older version during cluster creation.

## Available Versions and Release Calendar

Amazon EKS offers multiple Kubernetes versions in both standard and extended support. Users can choose from a range of versions to meet their specific requirements. The release calendar for each version provides important dates such as the upstream release date, Amazon EKS release date, end of standard support, and end of extended support.

## Versions in Standard Support

There are various Amazon EKS standard supports as of today. However, as more and more changes are needed, other versions will become necessary. Current Amazon EKS standard support includes:

- 1.29
- 1.28
- 1.27
- 1.26

## Versions in Extended Support

The following Kubernetes versions are currently available in Amazon EKS extended support:

- 1.25
- 1.24
- 1.23

## Release Dates and Support Timelines

![](https://miro.medium.com/v2/resize:fit:640/1*X9EY3dB4nB6vjhZ6jxoq6A.png)

The table below shows important release and support dates for each Kubernetes version in Amazon EKS:

## Kubernetes EKS Upgrade Process Best Practices

To start with, let’s focus on the technical aspects of the Kubernetes EKS upgrade process. The upgrade processes are in phases; before, during, and post upgrade processes as would be shown in the subsequent section. Before upgrades, there are tasks required of you, during upgrades, there are things you must do as well and after the upgrades, you must do some routine tasks to ensure that EKS is well-upgraded and running effectively with the current or updated version.

In Amazon EKS, both the control and data planes should run the same Kubernetes minor version for smooth operation. AWS manages and upgrades the control plane, while you are responsible for updating the worker nodes in the data plane. Below are basic explanations of control and node plane before we get into details;

- **Control Plane Upgrade:** Upgrading the EKS control plane involves deploying a new control plane version and migrating your existing configuration and settings. The upgrade process is managed by AWS and typically does not require direct user intervention. However, you can use the AWS Management Console, AWS CLI, or AWS SDKs to trigger the upgrade manually if needed.
- **Node Group Upgrade:** Upgrading the node groups in your EKS cluster involves updating the underlying EC2 instances to a newer Amazon EKS-optimized AMI that corresponds to the target Kubernetes version. This process can be automated using tools like eksctl or managed node groups.

## Before Upgrading your EKS cluster

1. **Understand Deprecation Policies**: Familiarize yourself with the Kubernetes deprecation policy to anticipate changes that may affect your applications.
2. **Review Kubernetes Change Log**: Thoroughly review the Kubernetes change log alongside Amazon EKS Kubernetes versions to understand any possible impacts.
3. **Assess Cluster Add-Ons Compatibility**: Review and update your existing cluster add-ons for compatibility with the new Kubernetes version.
4. **Enable Control Plane Logging**: Enable control plane logging to capture any issues during the upgrade process for troubleshooting.

## Upgrading Your Cluster

1. **Plan Sequential Upgrades:** For multiple version updates, plan a series of sequential upgrades to minimize downtime and risks.
2. **Upgrade Control Plane**: Initiate the control plane upgrade through the AWS API or console.
3. **Review Add-Ons Compatibility**: Ensure all Kubernetes add-ons and custom controllers are compatible with the new version.
4. **Upgrade Kubectl**: Update your kubectl version to match the new Kubernetes version.
5. **Upgrade Data Plane (Worker Nodes)**: Upgrade your worker nodes to the same Kubernetes minor version as the control plane.
6. **Use eksctl for Management**: Consider using eksctl to simplify and manage your EKS cluster upgrades.
7. **Validate and Test**: Perform tests in a non-production environment or through automated tests to ensure compatibility and stability.

## Post-Upgrade

1. **Update Add-Ons**: Ensure all Kubernetes components and add-ons are updated to match the new Kubernetes version. Remember that if they are not updated, they will likely not function well with the new version.
2. **Monitor and Maintain**: Regularly monitor your upgraded cluster for any issues and maintain compatibility with new versions. You can do these by reviewing your resource allocation, pod placement, and network configuration.

## Step-by-Step Technical Guide to EKS Upgrades

1. **Planning the Upgrade**
- **Review Release Notes:** Start by reviewing the release notes for the new Kubernetes version to understand the changes and new features.
- **Check Compatibility:** Ensure that your current configurations and add-ons are compatible with the new Kubernetes version.
- **Backup Data:** Before proceeding with the upgrade, backup your EKS cluster data using AWS Backup or other backup solutions.

**2\. Upgrading the Cluster Control Plane**

- **Update kubelet and kubectl:** Upgrade the kubelet and kubectl versions on your worker nodes to match the new Kubernetes version.
![](https://miro.medium.com/v2/resize:fit:640/1*ZZ099oZjOpbYMwUaKgzNEg.png)

- **Upgrade the Control Plane:** Use the eksctl command-line tool to upgrade the control plane of your EKS cluster to the new Kubernetes version.
![](https://miro.medium.com/v2/resize:fit:640/1*viI7-t8QNvnkaJvD0ad84A.png)

- **Verify Upgrade:** After the upgrade is complete, verify that the control plane is running the new Kubernetes version.

**3\. Upgrading Worker Nodes**

- **Drain Nodes:** Before upgrading the worker nodes, drain them to ensure that no pods are running on them.
![](https://miro.medium.com/v2/resize:fit:640/1*xsfDaTJdPg6oJbLApd8Kwg.png)

- **Update Node AMI:** Update the Amazon Machine Image (AMI) for your worker nodes to the latest version that supports the new Kubernetes version.
- **Upgrade Node Group:** Use the eksctl command-line tool to upgrade the node group to the new Kubernetes version.
![](https://miro.medium.com/v2/resize:fit:640/1*9j2N1xPQmps68ASuacvwdg.png)

- **Verify Upgrade:** After upgrading the node group, verify that the worker nodes are running the new Kubernetes version.
![](https://miro.medium.com/v2/resize:fit:640/1*NeD-xQGt9UKKuHvIbb0OtA.png)

**4\. Rolling Update for Pods**

- **Uncordon Nodes:** After upgrading the worker nodes, uncordon them to allow pods to be scheduled on them again.
![](https://miro.medium.com/v2/resize:fit:640/1*PxAVVPcrsWUsWYjv5nq07g.png)

- **Rolling Update for Pods:** Kubernetes will automatically start rolling updates for pods running on the upgraded nodes. Monitor the progress of the rolling update using the following command:
![](https://miro.medium.com/v2/resize:fit:640/1*CAQwPKoCpGwsHKghK6ktrQ.png)

**5\. Upgrade Add-Ons**

## Manual Upgrades

*Some add-ons require manual intervention to upgrade. This typically involves following the specific documentation for the add-on you’re using. The documentation will outline the upgrade steps, which may include:*

- *Downloading new binaries or container images.*
- *Updating configuration files.*
- *Restarting the add-on pods or deployments.*

***Examples of Add-Ons Requiring Manual Upgrades:***

- *Custom metrics collectors not included as EKS add-ons.*
- *Third-party monitoring tools not natively supported by EKS.*
- *Self-managed tools deployed on your cluster (e.g., cert-manager).*

***Important Note:*** *Before performing a manual upgrade, ensure you understand the specific steps involved and any potential downtime associated with the process. It’s recommended to test the upgrade process in a non-production environment first.*

## Upgrading EKS-Managed Add-Ons

*For add-ons managed by Amazon EKS (like Argo CD or Prometheus Operator), you can leverage the update-addon API for a simpler upgrade process. This command streamlines the upgrade by handling tasks like fetching new container images and restarting pods.*

*Here’s how to use the update-addon command:*

*Bash*

*aws eks update-addon — cluster-name <cluster-name> — addon-name <addon-name> — addon-version <new-version>*

***Explanation of Arguments:***

- *<cluster-name>: This refers to the name of your specific EKS cluster.*
- *<addon-name>: This specifies the name of the EKS add-on you want to upgrade (e.g., “argocd” or “prometheus”).*
- *<new-version>: This indicates the desired version you’re upgrading to (check available versions in the EKS documentation).*

**Monitoring and Testing**

- **Monitor Cluster Health:** Use the Kubernetes dashboard or other monitoring tools to monitor the health of your cluster after the upgrade.
- **Test Applications:** Test your applications to ensure they are working correctly with the new Kubernetes version.

**Rollback (If Necessary)**

- **Backup Configuration:** Before upgrading, ensure you have a backup of your previous configuration.
- **Rollback Control Plane:** If the upgrade causes issues, you can rollback the control plane using the eksctl command-line tool.
![](https://miro.medium.com/v2/resize:fit:640/1*0T6nkd6boOR6B6306nd_kQ.png)

- **Rollback Worker Nodes:** If necessary, you can rollback the worker nodes by restoring the previous AMI or node group configuration.

Following these steps will help you successfully upgrade your EKS cluster to the new Kubernetes version. Remember to always back up your data and configurations before proceeding with any upgrades.

## How Atmosly Simplified EKS Upgrades

Upgrading Kubernetes clusters in Amazon EKS can be complex and time-consuming, often involving manual checks, backups, and careful monitoring. However, with Atmosly, the process is streamlined and simplified, allowing users to upgrade their clusters with ease.

## Add-ons: Automated Compatibility Checks for Add-ons with EKS Version

Atmosly offers a more comprehensive approach to compatibility checks, specifically for custom add-ons it provides during initial cluster deployment. This eliminates the need for users to manually research compatibility before upgrades for these add-ons.

Here’s how it simplifies the process:

1. **Version Tracking:** Atmosly tracks the specific versions of its custom add-ons currently deployed in your cluster. This information is stored and managed using Infrastructure as Code (IaC) templates.
2. **Compatibility Matching:** During the upgrade process, Atmosly automatically checks its internal repository to see if the targeted Kubernetes version is compatible with the versions of its deployed add-ons.
3. **Upgrade Guidance & Version Push:**some text
4. If compatibility exists, Atmosly proceeds with the upgrade as planned.
5. If compatibility issues are detected, Atmosly provides clear guidance and recommendations specific to its add-ons. This may include suggesting and even automating the process of fetching and deploying upgraded versions of Atmosly’s add-ons that are compatible with the target Kubernetes version.

## IaC Update and Karpenter Provisioner

Atmosly streamlines EKS upgrades for both node groups and Karpenter-managed nodes by performing comprehensive compatibility checks. It verifies if the target Kubernetes version is compatible with both the node group AMIs and the Karpenter provisioner version used in your cluster. This ensures a smooth upgrade process. Atmosly then automates the entire upgrade through a single rolling update. Karpenter provides new nodes with the compatible AMI version, while workloads are gracefully drained from old nodes managed by both EKS and Karpenter before termination. This minimizes downtime and ensures a seamless upgrade experience.

## Conclusion

Upgrading Kubernetes clusters in Amazon EKS is a critical operation that requires careful planning and execution. By following best practices and leveraging tools like Atmosly, the upgrade process can be streamlined and simplified, ensuring a smooth transition to the new Kubernetes version.

As shown in this article, EKS upgrade best practices include; Planning the upgrade, reviewing release notes, and ensuring compatibility of custom configurations are essential steps, backup and restore functionality, gradual rollout, testing, and monitoring are crucial for a successful upgrade.

To effectively navigate the murky waters of EKS upgrades, you need a platform like Atmsoly, built to enhance efficiency, security, and scalability. [**Atmosly**](https://www.atmosly.com/) simplifies upgrades with automated compatibility checks, backup and restore functionality, a simplified rollout process, and integrated monitoring.

![](https://miro.medium.com/v2/resize:fit:640/1*q8c2dgugFYGksaVzza-BGw.png)

[![Atmosly](https://miro.medium.com/v2/resize:fill:96:96/1*4j2JyC8HPzDTaFs9c90vyA.png)](https://medium.com/atmosly?source=post_page---post_publication_info--aed30e16bac1---------------------------------------)

[![Atmosly](https://miro.medium.com/v2/resize:fill:128:128/1*4j2JyC8HPzDTaFs9c90vyA.png)](https://medium.com/atmosly?source=post_page---post_publication_info--aed30e16bac1---------------------------------------)

[Last published 5 days ago](https://medium.com/atmosly/15-aws-resources-you-should-always-deploy-with-terraform-20d917a9ca9a?source=post_page---post_publication_info--aed30e16bac1---------------------------------------)

Self Service Devops platform

Leading the tech team at Atmosly, developing a self-service DevOps platform for seamless cloud infrastructure & app deployment with Kubernetes.