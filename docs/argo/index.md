---
hide:
  - tags
title: Introduction to Argo
description: "Courte description pour l’aperçu et le SEO"
date: 2025-12-01
tags:
  - Argo
  - Argo CD
  - Argo Workflows
  - Argo Events
  - Argo Rollouts
categories:
  - Documentation
  - Argo
author: "Mathias FELIX"
---

## Introduction

### Chapter Overview and Objectives
Before you start working with Argo and exploring its powerful workflow management features in Kubernetes, it’s important to establish a strong understanding of the core concepts. This chapter provides that foundation by introducing the essential ideas you’ll need to understand how Argo operates in a Kubernetes environment.

By the end of this chapter, you should be able to:

- Explain the key concepts behind Argo.
- Describe common use cases for the Argo suite.
- Identify Kubernetes's role in supporting Argo.
- Install Kubernetes to prepare your environment for the Argo suite.

---

## Essential Concepts for Argo

### What Is GitOps?

GitOps is a collection of principles that guide modern software delivery and operations. It provides a structured, reliable way to manage infrastructure and applications through version control. Let's explore the five key aspects of GitOps that streamline, standardize, and optimize development and deployment.

- **Declarative configuration**
The first principle of GitOps is declarative configuration. This means defining what the desired state of your system should look like, rather than how to get there. In practice, developers describe the intended outcome—for example, specifying that an application should run three containers. Automated agents then compare the current system state to this desired configuration and make the necessary adjustments, such as adding or removing containers. This approach contrasts with the traditional imperative style, in which specific commands are issued step by step to achieve the desired setup.

- **Immutable storage**
In GitOps, Git serves not only as a version-control system but also as an immutable storage for configurations. Once a configuration is committed to Git, it becomes a fixed reference point, providing a reliable record that supports reproducibility and traceability. This makes Git the single source of truth for your system’s desired state. Although Git is the most commonly used tool for this purpose, the core principles of GitOps can also be applied with other version control systems.

- **Automation**
Automation is a core principle of GitOps. It focuses on removing manual steps after changes are committed to version control. Once an update is made, software agents take over, analyzing the difference between the system’s current state and the desired state defined in the repository. They then apply the necessary changes to implement the newly declared configuration, bringing the system into alignment. This continuous reconciliation process represents the closed-loop nature of GitOps, ensuring that deployments remain consistent, reliable, and up to date without human intervention.

- **Closed loop**
In GitOps, the term closed loop refers to the continuous feedback process that compares the system’s actual state with its desired state. Automated agents constantly monitor for differences between the two and take corrective action whenever the system drifts from the configuration defined in version control. This ensures the environment is always moving toward the declared state, maintaining consistency, reliability, and predictability in operations.

---

## Argo Overview

### What Is Argo?

Argo is a set of Kubernetes-native tools that enhance the workflow management capabilities of Kubernetes. It includes Argo Continuous Delivery (CD) for state management, Argo Workflows for running complex jobs, Argo Events for event-based dependency management, and Argo Rollouts for progressive delivery. These tools are designed to help you automate and manage tasks in a Kubernetes environment, making it easier to deploy, update, and manage applications. Each of these tools can run independently and do not require the others to work, but they are capable of working together.

Let’s discuss them in more detail.

---

### Argo Continuous Delivery (CD)
Argo CD is a declarative GitOps continuous delivery (CD) tool designed for Kubernetes. It automates the process of applying Kubernetes manifests from a Git repository to a cluster and continuously monitors the repository for changes. When updates are detected, Argo CD automatically synchronizes the cluster to match the desired configuration defined in Git. This makes it an ideal tool for managing both infrastructure and application deployments, ensuring that production environments always reflect the exact state specified in version control.

---

### Argo Workflows
Argo Workflows, as an extension of the Kubernetes API, introduces a new Workflow CRD, providing companies with a highly adaptable batch resource akin to a Kubernetes Job. This extensibility renders Workflows versatile and applicable across various domains, with a particular spotlight on its efficacy in Machine Learning (ML) and Data pipelines. Using Argo Workflows in these contexts has become a strategic move for numerous companies, unraveling its potential in orchestrating complex processes seamlessly.

At its core, Argo Workflows operate on a unique set of characteristics and use cases. Each step within a workflow runs as a pod, contributing to the modularity and scalability of the overall process. This design allows for streamlined parallelism and efficient resource utilization. Predominantly, Argo Workflows work well in data processing and automation scenarios, exemplified by the fan-out fan-in pattern. This pattern enables the workflow to distribute tasks widely, execute them concurrently, and then consolidate the results, making Argo Workflows a robust choice for scenarios demanding intricate data manipulation and automated processes.

---

### Argo Events
Argo Events is an event-driven workflow automation framework for Kubernetes that helps you trigger Kubernetes objects, Argo Workflows, serverless workloads, and other processes in response to events from various sources such as webhooks, S3, schedules, messaging queues, GCP PubSub, and more. It supports events from over 20 event sources and allows you to customize business-level constraint logic for workflow automation.

Argo Events is composed of two main components: Triggers and Event Sources. Triggers are responsible for executing actions when an event occurs, while Event Sources are responsible for generating events.

Some of the use cases of Argo Events include automating research workflows, designing a complete CI/CD pipeline, and automating everything by combining Argo Events, Workflows & Pipelines, CD, and Rollouts.

---

### Argo Rollouts
Argo Rollouts is a progressive delivery controller for Kubernetes. It was born out of necessity due to Kubernetes’ lack of more sophisticated deployment strategies. Argo Rollouts provides blue-green and canary update strategies, integrates with service meshes and ingress controllers to shape traffic, and automates promotion and rollback based on analysis. It is used to safely deploy new application features into Production without manual analysis, testing, or intervention.

---

### Benefits of Using Argo
Using Argo for continuous delivery offers several benefits. We will now explore some of them.

Argo is a popular open source tool that brings the practicality of GitOps to anyone who uses Kubernetes. By enabling GitOps, Argo can enhance the robustness, security, and reliability of Kubernetes environments. This technical practice can be highly beneficial to DevOps teams, improving their efficiency.

Argo is designed from the ground up for a modern containerized environment. Argo CD as an example is equipped with a powerful GUI and CLI, enabling all seniority levels of engineers to work with it and implement highly sophisticated custom solutions. Argo Rollouts on the other hand supports progressive delivery strategies like canary and blue-green deployments, which are difficult to implement in plain Kubernetes.

The automation provided by Argo speeds up the entire process of pushing new features, leading to faster and more frequent deployments. If any issues are detected based on defined metrics, the deployment can be automatically rolled back to the previous working deployment, allowing for faster error resolution.

One of the benefits of using Git and GitOps principles is the built-in auditing, which gives you the benefit of having the entire history of your software tracked over time. Argo makes it easy to specify, schedule, and coordinate the running of complex workflows and applications on Kubernetes.

Argo's integration with other Cloud Native Computing Foundation (CNCF) projects is a significant advantage. It uses or integrates with CNCF projects like gRPC, Prometheus, NATS, Helm, and CloudEvents. This integration allows for seamless interoperability and enhanced functionality within the cloud native ecosystem. For instance, Prometheus can be used for monitoring and alerting purposes, while Helm can help manage Kubernetes applications. NATS can provide a high-performance messaging system, and CloudEvents can offer a standard way to define the format of event data in a consistent way across services, platforms, and systems. Therefore, by using Argo, you can leverage the benefits of these CNCF projects, leading to more robust, scalable, and efficient cloud native applications.

Please note that we will delve deeper into each of these topics in the subsequent chapters.

---

## Installing Kubernetes Locally

### Step-by-Step: Deploying Kubernetes for Argo
This section serves as a general guide to installing a Kubernetes cluster locally. This basic setup of a local Kubernetes cluster can be used for any labs throughout this course.

Kubernetes serves as the underlying orchestration platform that facilitates the deployment, scaling, and management of containerized applications. Argo, which includes projects like Argo Workflows and Argo CD, leverages Kubernetes to seamlessly integrate and automate workflows and continuous delivery pipelines. Kubernetes provides the essential infrastructure for container orchestration, allowing Argo to effectively coordinate and execute tasks, manage dependencies, and ensure the efficient deployment and operation of applications in a distributed and scalable environment.

---

### Installing Docker
Ensure Docker is installed and running on your machine:

- Visit the Docker website for detailed installation instructions and to download the software.
- Choose the appropriate version for your operating system.
- Download and install Docker by following the on-screen instructions.
- After installing, verify that Docker is correctly installed by opening the terminal and typing docker –version. If Docker is installed correctly, this command will display the installed version of Docker.
The labs in this course were tested on Ubuntu 24.04 on a 2 CPU, 8GB machine.

If you are on Ubuntu 24.04, you can install Docker using the convenience script with the following command:

curl https://get.docker.com | bash

---

### Installing kubectl
Instructions for downloading and installing kubectl can be found in the Kubernetes official documentation.

Make sure kubectl is installed by running the kubectl version –client command in your terminal. If kubectl is installed correctly, this command will display the installed version of kubectl.

To install kubectl on Ubuntu 24.04, use the following commands:

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

---

### Installing kind and Creating a Cluster
Download and install kind following the instructions from the kind official website.

On Ubuntu 24.04, use the following command to download the latest (as of November 7, 2025) kind client:

[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.30.0/kind-linux-amd64

Then move the binary to a directory in your PATH so you can freely use it as a regular user.

Commands:

chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

Create a cluster by running the following command (you may need to use sudo):

kind create cluster

This command creates a single-node Kubernetes cluster running inside a Docker container and automatically configures kubectl’s config file and sets the current context to use kind.

If you installed kind with sudo, only the root user can reach the cluster. To reach the cluster as a regular user, create a copy of the kind kubeconfig that your user owns in your home directory:

mkdir -p ~/.kube
sudo cp /root/.kube/config ~/.kube
sudo chown $(whoami):$(whoami) ~/.kube/config

To verify everything is working you can use the kubectl config current-context command to check the currently active context. It should display kind-kind as the current context.

To check if kubectl can reach your kind cluster, you can use the command kubectl get nodes. This command will display your Kubernetes nodes, which in a single-node kind cluster only consists of the kind-control-plane node.

---

# ARGO CD

Declarative continuous delivery with a fully-loaded UI.

## Introduction

### Chapter Overview and Objectives
In this chapter, we explore the detailed aspects of Argo CD, a pivotal tool within the Argo suite, designed specifically for Continuous Delivery (CD) and GitOps practices. Through thematic discussions and hands-on labs, we aim to equip you with a comprehensive understanding of Argo CD's architecture, installation, configuration, security considerations, and its extensibility.

By the end of this chapter, you should be able to:

- Explain how Argo CD leverages the GitOps principles.
- Describe the core components of Argo CD, their roles and tasks.
- Install and configure Argo CD on a Kubernetes cluster.
- Deploy and update applications using Argo CD.

---

## Argo CD Overview

### What Is Argo CD?
[Argo CD](https://argoproj.github.io/cd/) is a declarative, GitOps continuous delivery tool for Kubernetes. Compared to the standard Kubernetes workflow, Argo CD introduces a number of enhancements.

Key Advancements:

- **GitOps:** Argo CD enforces the desired state of your application as it is described in a Git repository. This means that all changes to your application are version-controlled and can be easily tracked. This is a significant improvement over the standard Kubernetes workflow, where changes are made directly on the cluster and can be difficult to track.

- **Continuous Delivery:** Argo CD continuously monitors the application's Git repository and automatically deploys any changes to your Kubernetes cluster. This eliminates the need to manually run the kubectl apply command whenever you want to deploy changes, making the deployment process more efficient, easier to track, and less error-prone.

- **Rollbacks:** If something goes wrong with a deployment, Argo CD allows you to easily roll back to a previous version of your application. This is much more difficult with the standard Kubernetes workflow, where you would need to either manually revert your changes in the cluster or reapply old manifests to the cluster.

- **Multi-environment management:** Argo CD makes it easy to manage multiple environments (like Dev, Staging, Production) from a single Git repository. This is a significant improvement over the standard Kubernetes workflow, where managing multiple environments can be complex and error-prone.

- **UI and API:** Argo CD provides a user-friendly UI and a powerful API, making it easier to manage and monitor your applications. This is a significant improvement over the standard Kubernetes workflow, which relies heavily on command-line tools.

In the next few sections, we'll explore fundamental aspects of Argo CD. Our focus will be on essential terminology within the Argo CD ecosystem, the core components that constitute Argo CD, and the concept of the reconciliation loop. Understanding these elements is key to efficiently managing your application deployments.

---

## The Architecture of Argo CD

### Vocabulary
In the world of Argo CD, understanding the specific vocabulary is crucial for effectively managing and deploying applications within Kubernetes environments. These terms form the core language used to describe various aspects and operations within Argo CD, a declarative, GitOps continuous delivery tool for Kubernetes. By familiarizing yourself with this vocabulary, you gain the ability to precisely communicate and execute tasks related to application deployment and management. This knowledge not only streamlines your workflow but also enhances collaboration with team members, as you all share a common understanding of these key concepts.

Each term encapsulates a distinct aspect of the Argo CD ecosystem. From defining the structure and sources of your applications to understanding their operational states and health, this vocabulary covers the breadth of the deployment process. Knowing the difference between 'Target state' and 'Live state', for instance, is essential for maintaining the integrity and desired functionality of your applications. Similarly, grasping the nuances of various statuses and actions like 'Sync status' and 'Refresh' enables you to effectively monitor, troubleshoot, and update your Kubernetes resources. In essence, these terms are the building blocks for mastering Argo CD and ensuring a smooth, efficient deployment pipeline in Kubernetes.

Main Concepts:

- **Configuration:**
    - A Custom Resource Definition (CRD) provided by Argo CD that defines a collection of Kubernetes resources and serves as the primary interface for managing software deployed by Argo CD.
    - Application source type: The tool utilized for building applications, such as Helm or Kustomize.

- **States:**
    - Target state: The desired state of an application, represented in a Git repository, serving as the source of truth.
    - Live state: The current state of the application, indicating the deployed Kubernetes resources.

- **Statuses:**
    - Sync status: The status indicating whether the live state aligns with the target state. Essentially, it confirms if the application deployed in Kubernetes matches the desired states outlined in the Git repository.
    - Sync operation status: The status during the sync phase, specifying whether it has failed or succeeded.
    - Health status: The well-being of the application, assessing its running condition and ability to handle requests.

- **Actions:**
    - Refresh: The act of comparing the latest code in Git with the live state to identify any differences.
    - Sync: The process of transitioning an application to the target state by applying changes in the Kubernetes cluster.

---

## Core Components

### Controllers
To get started, we will take a look at Argo CDs core components and how they work with each other.

Argo CD employs [Kubernetes controllers](https://kubernetes.io/docs/concepts/architecture/controller/) for its core functions. A Kubernetes controller, including those in Argo CD, monitors the cluster's state and ensures it aligns with the desired state by initiating or requesting changes when necessary. This is achieved by observing Kubernetes resource objects, each specifying the intended state through a spec field.

---

### API Server
The API server in Argo CD serves as a central communication hub that enables different systems like the Web UI, CLI, Argo Events, and CI/CD tools to interact with it. Think of it as a central control tower for managing applications. Its main job is to keep track of the applications, providing status updates so you know what's happening with them. When it's time to make changes or updates, the API server triggers the necessary operations on these applications.

Beyond that, the API server has other responsibilities. It takes care of handling Git repositories and Kubernetes clusters, ensuring a smooth connection between your code and your infrastructure. Security-wise, it is the gatekeeper, handling authentication and Single Sign-On (SSO) support. Additionally, the API server enforces Role-Based Access Control (RBAC) policies, making sure that the right people have the right level of access to keep everything secure and organized. In essence, it's the behind-the-scenes maestro making sure everything in your Argo CD setup plays in harmony. The following actions encapsulate its specific roles in managing applications and facilitating communication:

- Manages applications and provides status updates
- Triggers operations on applications when needed
- Handles Git repositories for version control
- Manages connections with Kubernetes clusters
- Takes care of authentication and support Single Sign-On (SSO)
- Enforces Role-Based Access Control (RBAC) policies
- Serves as a central hub for communication with Web UI, CLI, Argo Events, and CI/CD systems

---

### Repository Server
Connected to the API Server is the Argo CD [Repository Server](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/#repository-server), which is responsible for retrieving the desired state of applications from Git repositories and packaging it into a format that can be understood by Kubernetes. This server communicates with your Git repositories and fetches the necessary information. It maintains a local cache of the Git repositories holding the application manifests.

Other services of Argo request Kubernetes manifests using the following arguments:

- Repository URL
- Git revision
- Application path
- Templating relevant information such as parameters or Helm's `values.yaml`

---

### Application Controller
The Argo CD Application Controller is another crucial component. It continuously compares the desired application state (as defined in your Git repositories) with the live state in your Kubernetes cluster (as defined in the Application CRDs provided by the user). If it detects any discrepancies, it will take corrective action to ensure that the live state matches the desired state.

https://d36ai2hkxl16us.cloudfront.net/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/usw9tkp4ummq-LFS256_CourseTrainingGraphics-01.png

---

## Understanding Reconciliation and Synchronization Control

### How Does the Argo CD Reconciliation Loop Work?
Argo CD's reconciliation process involves aligning the intended configuration specified in a Git repository with the current state in the Kubernetes cluster. This continuous loop, known as the [reconciling loop](https://argo-cd.readthedocs.io/en/stable/proposals/applicationset-plugin-generator/#reconciliation-logic), is illustrated in the following figure.

 
https://d36ai2hkxl16us.cloudfront.net/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/22rl587rhioq-LFS256_CourseTrainingGraphics_5.png


Argo CD reconciliation loop

 

When using Helm, Argo CD monitors the Git repository, employs Helm to generate Kubernetes manifest YAML through template execution, and compares it with the cluster's desired state, known as sync status. If disparities are identified, Argo CD utilizes kubectl apply to implement the changes and update the Kubernetes desired state. It is noteworthy that Argo CD, in this process, opts for kubectl apply over helm install to support various templating tools while maintaining its role as a GitOps declarative tool without being tied to a specific templating tool.

The Argo CD reconciliation loop embodies the principles of GitOps by maintaining a Git repository as the single source of truth for infrastructure definitions. This process aligns with the GitOps principles of having a declarative desired state, which is versioned and immutable, and is automatically pulled by software agents. The agents continuously observe the actual system state and attempt to reconcile it with the desired state, mirroring the continuous reconciliation principle of GitOps. Thus, the Argo CD reconciliation loop is a practical implementation of GitOps principles.

---

### Synchronization Principles
The sync phase is a very important operation and its behavior can be customized by using resource hooks and sync waves. In this section, we explore both ways of customization and learn how to use them.

Customization Solutions:

**Resource hooks:**
A sync, as described in the "Vocabulary" section, is the transition of an application into the target state. There are five possible definitions of when a resource hook can be run:

- PreSync, execute before the Sync phase (e.g., create a backup before syncing)
- Sync, execute after all PreSync hooks completed successfully and do actions during application of the manifests (e.g., for more complex rollout strategies like blue-green or canary instead of Kubernetes rolling update)
- PostSync, execute after all successful Sync hooks and application, and all resources are in Healthy state (e.g., run additional health checks after deployment or run integration checks)
- Skip, indicates Argo CD to skip the application of the manifest
- SyncFail, executes when Sync fails (e.g., clean up operations)
To keep things simple, resource hooks use the Kubernetes kind Job and are identified by an annotation. Using the annotation Argo CD identifies Jobs and when they should be executed.

The following is an example for a database schema migration resource hook:

```yaml linenums="1"
apiVersion: batch/v1
kind: Job
metadata:
  generateName: schema-migrate-
  annotations:
    argocd.argoproj.io/hook: PreSync
```

More information regarding resource hooks can be found in the [official Argo CD documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/).

**Sync waves:**
Sync waves are a convenient way to split and order to-be-synced manifests. Waves can range from negative to positive values and occur from lowest to highest value. If not defined, the default value is wave zero. Using sync waves is achieved in the same way as resource hooks; by using annotations.

```yaml linenums="1"
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "5"
```

Both approaches can be utilized simultaneously. The sync operation in Argo CD initiates with the ordering of resources based on the following criteria:

- Resource hook phase annotation
- Sync wave annotation
- Kubernetes kind (for example, namespaces are prioritized, followed by other Kubernetes resources and then custom resources)
- Name
Afterwards the next wave number to be applied is identified. This number is always the lowest among any out-of-sync or unhealthy resources. Argo CD then applies this wave.

This process is repeated until all phases and waves are in sync and healthy.

However, if an application has unhealthy resources in the initial wave, it may prevent the application from ever reaching a healthy state.

For safety reasons, Argo CD adds a 2-second delay between each sync wave. This can be customized using the ARGOCD_SYNC_WAVE_DELAY environment variable.

---

## Objects & Resources

### Simplifying Application Management
Argo CD simplifies the management of your applications in Kubernetes environments by utilizing Custom Resource Definitions (CRDs).

Key Elements:

**Application**
Argo CD introduces the Application CRD, serving as a representation of the application instance you intend to deploy in your Kubernetes cluster. Applications define the source repository and the target cluster. They also provide settings for synchronization and application configuration overrides. Example:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'htt‌ps://github.com/argoproj/argocd-example-apps.git'
    targetRevision: HEAD
    path: guestbook
destination:
  server: 'htt‌ps://kubernetes.default.svc'
  namespace: guestbook
```

**AppProject**
For efficient organization, Argo CD provides the AppProject CRD. This allows you to group related applications for organization and governance purposes. An example use case involves segregating applications from utility services, enhancing the clarity of your project structure. Example:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production applications
  sourceRepos:
    - '*'
  destinations:
    - namespace: production
      server: 'htt‌ps://kubernetes.default.svc'
  clusterResourceWhitelist:
    - group: '*'
      kind: '*'
```

**Repository credentials**
In real-world scenarios, accessing private repositories is common. Argo CD facilitates this by using Kubernetes Secrets and ConfigMaps with specific labels. To grant Argo CD access, create the necessary Secret Kubernetes resources with a specific label: argocd.argoproj.io/secret-type: repository. Example:

```yaml linenums="1"
apiVersion: v1
kind: Secret
metadata:
  name: private-repo-creds
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  url: 'htt‌ps://github.com/private/repo.git'
  username: <username>
  password: <password>
```

**Cluster credentials**
In cases where Argo CD manages multiple Kubernetes clusters, additional access may be required. For this purpose, Argo CD utilizes a distinct Secret type with the label: argocd.argoproj.io/secret-type: cluster. This ensures secure access to external clusters not initially included in Argo CD's managed environments. Example:

```yaml linenums="1"
apiVersion: v1
kind: Secret
metadata:
  name: external-cluster-creds
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: external-cluster
  server: 'ht‌tps://external-cluster-api.com'
  config: |
    {
      "bearerToken": "<token>",
      "tlsClientConfig": {
         "insecure": false,
         "caData": "<certificate encoded in base64>"
      }
    }
```

By understanding and utilizing these fundamental Argo CD objects, you can effectively streamline the deployment and management of your applications across diverse Kubernetes environments.

---

## Argo CD Extensions & Integrations

### Plugins
Argo CD's strength lies in its extensibility through plugins, allowing users to tailor the tool to their specific needs. In this section, we will explore the concept of Argo CD plugins, understand how to configure them using ConfigMaps, and witness the Notifications plugin in action. Additionally, we'll highlight a few other notable plugins to showcase the versatility of Argo CD extensions.

---

### Understanding Plugins in Argo CD
Argo CD plugins extend the core functionalities of the system, offering additional features beyond the default capabilities. We will focus on Notifications plugins, which play a crucial role in keeping users informed about deployment events.

---

### Configuring Plugins with ConfigMaps
ConfigMaps in Kubernetes provide a way to manage configuration data, and in the context of Argo CD, they are employed to configure plugins. Let's explore the configuration of the Notifications plugin using a ConfigMap:

```yaml linenums="1"
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
data:
  context: |
    region: east
    environmentName: staging

  template.a-slack-template-with-context: |
    message: "Something happened in {{ .context.environmentName }} in the {{ .context.region }} data center!"
```

In this example:

- The context section provides contextual information such as the region and environment name.
- The template.a-slack-template-with-context section defines a Slack notification template using Go templating. It references values from the context section to personalize the message.
- This ConfigMap enables users to dynamically adjust notification content based on contextual information, providing flexibility in responding to different deployment scenarios.

---

### How Plugins Work in Argo CD
Plugins in Argo CD follow a specific lifecycle, including registration, initialization, and execution phases. During startup, Argo CD discovers and loads available plugins, initializing them for use throughout the application lifecycle. Critical events, such as application synchronization or deployment, trigger the associated plugins.

---

### Plugins in Action: Notifications and Beyond
Let's practically apply our knowledge by considering a scenario where a deployment fails in the staging environment in the east region. The [Notifications plugin](https://argocd-notifications.readthedocs.io/en/stable/), configured with the provided template, triggers a notification over Slack or email such as: "Something happened in staging in the east data center!". This immediate notification empowers users to swiftly identify and address deployment issues.

Beyond the Notifications plugin, Argo CD supports various other plugins that cater to diverse needs. Some noteworthy examples include:

- [Image Updater Plugin](https://argocd-image-updater.readthedocs.io/en/stable/): Automates the process of updating container images in Kubernetes manifests, ensuring applications are always using the latest versions.
- [ArgoCD Autopilot](https://github.com/argoproj-labs/argocd-autopilot): Streamlines GitOps workflows by automating the management of Helm releases, making it easier to maintain and deploy applications.
- [ArgoCD Interlace](https://github.com/argoproj-labs/argocd-interlace): Enhances Argo CD's UI with additional features, providing an interactive and dynamic interface for managing applications and deployments.

---

## Best Practices

### Securing Argo CD

**Use RBAC!**
- Why: Using RBAC is one of the most important best practices for securing Argo CD as it is vital to manage user permissions effectively, ensuring that only authorized personnel have access to specific resources. This approach minimizes the risk of unauthorized changes or access, which is crucial in a continuous deployment environment.
- How: To implement RBAC in Argo CD, define roles with specific permissions in the argocd-rbac-cm ConfigMap, aligning with user responsibilities. Assign these roles to users or groups through RoleBindings or ClusterRoleBindings for appropriate access levels. Ensure minimal access necessary per role, adhering to the principle of least privilege. Regularly audit RBAC settings to reflect current needs and security policies, adjusting roles and permissions as necessary. Utilize Argo CD's predefined roles for common access patterns, customizing as needed. Test configurations to ensure proper enforcement and security.

**Manage Secrets Securely**
- Why: Secrets management is critical for safeguarding sensitive information such as API keys, passwords, and certificates. Effective secrets management prevents unauthorized access and potential security breaches. In the context of Kubernetes and Argo CD, this involves handling secrets in a way that they are not exposed or logged.
- How: Use Kubernetes' native secrets management to store and handle sensitive data. Ensure that secrets are encrypted at rest and in transit. For enhanced security, consider implementing additional layers of security like using environment variables, Kubernetes' native encryption capabilities, or integrating with other secret management solutions that fit within the Kubernetes ecosystem.

**Regularly Update Argo CD**

- Why: Keeping Argo CD updated is crucial for security. Updates often include patches for vulnerabilities, improvements in functionality, and enhanced security features. Staying updated helps in protecting against emerging threats and taking advantage of the latest security enhancements.
- How: Establish a routine for checking and applying updates to Argo CD. This can be done through automated update checks or manual monitoring of Argo CD releases. Use standard Kubernetes deployment strategies to apply updates with minimal disruption. Ensure that the update process includes testing in a staging environment before deploying to production to avoid unexpected issues.

For additional detailed information on Argo CD security practices, especially topics like Single Sign-On (SSO), Audit Logging, and Network Policies, refer to the [Argo CD Security Documentation](https://argo-cd.readthedocs.io/en/stable/operator-manual/security/).

---

## Note on Helm and Kustomize

### Enhancing Deployment Efficiency with Helm and Kustomize
Transitioning from standard deployments, Helm enhances ArgoCD with templating and package management, streamlining deployments across environments. Kustomize adds customization layers to deployments without changing base manifests, simplifying environment-specific adjustments. These tools facilitate scalable and error-reduced deployments in ArgoCD.

Argo CD uses either Helm or Kustomize to deploy applications depending on the contents of its source repository.

For more, visit the ArgoCD guides on [Helm](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/) and [Kustomize](https://argo-cd.readthedocs.io/en/stable/user-guide/kustomize/).

---

## Lab Exercises

### Lab 3.1. Installing Argo CD
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

- When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
- Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

### Lab 3.2. Managing Applications with Argo CD
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

- When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
- Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

### Lab 3.3. Argo CD Security and RBAC
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

# ARGO WORKFLOWS

## Introduction

### Chapter Overview and Objectives
In this chapter, we will explore the details of Argo Workflows, an extension of Argo, a popular GitOps tool designed for declarative continuous delivery of Kubernetes applications. Argo Workflows allows you to define and manage complex workflows as code, providing a way to orchestrate and automate multi-step processes within the Kubernetes environment.

By the end of this chapter, you should be able to comprehend the basics and architecture of Argo Workflows. This involves understanding its key components, how they interact, and the fundamental concepts that govern the execution of workflows. Here are learning objectives for gaining proficiency in Argo Workflows:

- Define and explain the structure of an Argo Workflow.
- Recognize key elements such as metadata, spec, entrypoint, and templates.
- Understand the role of templates in workflows.
- Identify and explain the primary components of Argo Workflows, including the Workflow Controller, and UI.
- Understand how Argo Workflows schedules and executes tasks.
- Dive into the responsibilities of the Workflow Controller.

## Argo Workflows Core Concepts

### Workflow
A workflow is a series of tasks, processes, or steps that are executed in a specific sequence to achieve a particular goal or outcome. Workflows are prevalent in various domains, including business, software development, and project management. In the context of Argo and other DevOps tools, a workflow specifically refers to a sequence of automated steps involved in the deployment, testing, and promotion of software applications.

In Argo, the term Workflow is a Kubernetes Custom Resource that represents a sequence of tasks or steps that are defined and orchestrated to achieve a specific goal. It is a higher-level abstraction that allows users to describe complex processes, dependencies, and conditions in a structured and declarative manner. A Workflow also maintains the state of a workflow.

Next, we will take a look at the specs of a simple Workflow.

The main part of a Workflow spec contains an entrypoint and list of templates, as shown in the example below:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  entrypoint: whalesay
  templates:
- name: whalesay
  container:
    image: docker/whalesay
    command: [cowsay]
    args: ["hello world"]
```

A Workflow spec has two core parts:

Entrypoint: Specifies the name of the template that serves as the entrypoint for the workflow. It defines the starting point of the workflow execution.
Templates: A template represents a step or task in the workflow that should be executed. There are six types of templates that we will introduce next.

---

### Template Types
A template can be containers, scripts, DAGs (Directed-Acyclic Graphs), or other types depending on the workflow structure and is divided into two groups: template definitions (which define work to be done) and template invocators (which invoke/call other templates and provide execution control).

**Template Definitions:**

**Container:**
A Container is the most common template type and represents a step in the workflow that runs a container. It is suitable for executing containerized applications or scripts. 

Example:
```yaml linenums="1"
- name: whalesay
  container:
    image: docker/whalesay
    command: [cowsay]
    args: ["hello world"]
```

**Resource:**
A Resource represents a template for creating, modifying, or deleting Kubernetes resources. It is useful for performing operations on Kubernetes objects in the cluster Workflows is currently running. 

Example:
```yaml linenums="1"
- name: k8s-owner-reference
  resource:
    action: create
    manifest: |
      apiVersion: v1
      kind: ConfigMap
      metadata:
        generateName: owned-eg-
      data:
        some: value
```

**Script:**
A Script is similar to the container template but allows specifying the script inline without referencing an external container image. It can be used for simple scripts or one-liners. 

Example:
```yaml linenums="1"
- name: gen-random-int
  script:
    image: python:alpine3.6
    command: [python]
    source: |
      import random
      i = random.randint(1, 100)
      print(i)
```

**Suspend:**
A Suspend is a template that suspends execution, either for a duration or until it is resumed manually. It can be resumed using the CLI, the API endpoint, or the UI. 

Example:
```yaml linenums="1"
- name: delay
  suspend:
    duration: "20s"
```
**Template Invocators:**

**DAG (Directed-Acyclic Graph)**
A DAG allows defining our tasks as a graph of dependencies. It is beneficial for workflows with complex dependencies and conditional execution. 

Example:

- name: diamond
  dag:
    tasks:
    - name: A
      template: echo
    - name: B
      dependencies: [A]
      template: echo
    - name: C
      dependencies: [A]
      template: echo
    - name: D
      dependencies: [B, C]
      template: echo


**Steps**
Steps are defining multiple steps within a template as several steps need to be executed sequentially or in parallel.

- name: hello-hello-hello
  steps:
  - - name: step1
      template: prepare-data
  - - name: step2a
      template: run-data-first-half
    - name: step2b
      template: run-data-second-half

---

### Outputs

In Argo Workflows, the outputs section within a step template allows you to define and capture outputs that can be accessed by subsequent steps or referenced in the workflow definition. Outputs are useful when you want to pass data, values, or artifacts from one step to another. Here's an overview of how outputs work in Argo Workflows. The Output comprises two key concepts:

Defining Outputs: You define outputs within a step template using the outputs section. Each output has a name and a path within the container where the data or artifact is produced.
Accessing Outputs: You can reference the outputs of a step using templating expressions in subsequent steps or the workflow definition.
Let’s consider a simple example where one step generates an output parameter and an output artifact, and another step consumes them:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: artifact-passing-
spec:
  entrypoint: artifact-example
  templates:
  - name: artifact-example
    steps:
    - - name: generate-artifact
        template: whalesay
    - - name: consume-artifact
        template: print-message
        arguments:
          artifacts:
          - name: message
            from: "{{steps.generate-artifact.outputs.artifacts.hello-art}}"

  - name: whalesay
    container:
      image: docker/whalesay:latest
      command: [sh, -c]
      args: ["cowsay hello world | tee /tmp/hello_world.txt"]
    outputs:
      artifacts:
    - name: hello-art
      path: /tmp/hello_world.txt

  - name: print-message
    inputs:
      artifacts:
      - name: message
        path: /tmp/message
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["cat /tmp/message"]
```

First the `whalesay` template creates a file name `/tmp/hello-world.txt` by using the cowsay command. Next, it outputs this file as an artifact called hello-art. The `artifact-example` template provides the generated hello-art artifact as an output of the generate-artifact step. Finally, the `print-message` template takes an input artifact called message and consumes it by unpacking it in `/tmp/message` path and using the cat command to print it into standard output.

---

### WorkflowTemplate
In Argo Workflows, a WorkflowTemplate is a resource that defines a reusable and shareable workflow template, allowing users to encapsulate workflow logic, parameters, and metadata. This abstraction promotes modularity and reusability, enabling the creation of complex workflows from pre-defined templates.

Here is an example of a simple WorkflowTemplate definition in Argo Workflows:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: sample-template
spec:
  templates:
   - name: hello-world
     inputs:
       parameters:
         - name: msg
           value: "Hello World!"
     container:
       image: docker/whalesay
       command: [cowsay]
       args: ["{{inputs.parameters.msg}}"]
```

In this example:

- The WorkflowTemplate is named `sample-template`
- It contains a template: `hello-world`
- The `hello-world` template takes a parameter message (with a default value of "Hello, World!") and generates a file with the specified message.
Once defined, this WorkflowTemplate can be referenced and instantiated within multiple workflows. For example:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
entrypoint: whalesay
templates:
  - name: whalesay
    steps:
      - - name: hello-world
          templateRef:
            name: sample-template
            template: hello-world
```

This workflow references the WorkflowTemplate named sample-template effectively inheriting the structure and logic defined in the template.

Using WorkflowTemplates is beneficial when you want to standardize and reuse specific workflow patterns, making it easier to manage, maintain, and share workflow definitions within your organization. They also help in enforcing consistency and reducing redundancy across multiple workflows.

---

## Argo Workflows Architecture

### Defining Argo Workflows and Its Components
Argo Workflows is an open source workflow orchestration platform designed for Kubernetes. It enables users to define, run, and manage complex workflows using Kubernetes as the underlying execution environment. All of Argo Workflows’ components are independent of other Argo projects and are usually deployed into their own Kubernetes namespace in a cluster.

**Argo Server**
The Argo Server is a central component that manages the overall workflow resources, state, and interactions. It exposes a REST API for workflow submission, monitoring, and management. The server maintains the state of workflows and their execution and interacts with the Kubernetes API server to create and manage resources.

**Workflow Controller**
The Argo Workflows Controller is a critical component within the Argo Workflows system. It is responsible for managing the lifecycle of workflows, interacting with the Kubernetes API server, and ensuring the execution of workflows according to their specifications. The Argo Workflows Controller continuously watches the Kubernetes API server for changes related to Argo Workflows Custom Resources (CRs). The primary CR involved is the Workflow, which defines the workflow structure and steps. Upon detecting the creation or modification of a Workflow CR, the controller initiates the corresponding workflow execution. The controller is responsible for managing the complete lifecycle of a workflow, including its creation, execution, monitoring, and completion. It also resolves dependencies between steps within a workflow. It ensures that steps are executed in the correct order, based on dependencies specified in the workflow definition.

**Argo UI**
The Argo UI is a web-based user interface for visually monitoring and managing workflows. It allows users to view workflow status, logs, and artifacts, as well as submit new workflows.

Both the Workflow Controller and Argo Server run in the argo namespace. We can opt for one of the cluster or namespaced installations, however, the generated Workflows and the Pods will be run in the respective namespace.

The diagram below shows an overview of a Workflow and also details of a namespace with generated pods.

https://d36ai2hkxl16us.cloudfront.net/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/utgl42dbrozx-LFS256_CourseTrainingGraphics-3.png

Argo Workflow building blocks

 

A user defines a workflow using YAML or JSON files, specifying the sequence of steps, dependencies, inputs, outputs, parameters, and any other relevant configurations. Then the workflow definition file is submitted to the Kubernetes cluster where Argo Workflows is deployed. This submission can be done via the Argo CLI, Argo UI, or programmatically through Kubernetes API clients.

The Workflow Controller component of Argo Workflows continuously monitors the Kubernetes cluster for new workflow submissions or updates to existing workflows. When a new workflow is submitted, the Workflow Controller parses the workflow definition to validate its syntax and semantics. If there are any errors or inconsistencies, the Workflow Controller reports them to the user for correction.

Once the workflow definition is validated, the Workflow Controller creates the necessary Kubernetes resources to represent the workflow, such as Workflow CRDs (Custom Resource Definitions) and associated Pods, Services, ConfigMaps, and Secrets.

Finally, Workflow Controller begins executing the steps defined in the workflow. Each step may involve running containers, executing scripts, or performing other actions specified by the user. Argo Workflows ensures that steps are executed in the correct order based on dependencies defined in the workflow.

## Argo Workflows Architecture

### Argo Workflow Overview
Each Step and DAG causes the generation of a Pod which comprises three containers:

- init: a template that contains an init container that performs initialization tasks. In this case, it echoes a message and sleeps for 30 seconds, but you can replace these commands with your actual initialization steps.
- main: a template contains the main container that executes the primary process once the initialization is complete.
- wait: a container that executes tasks such as clean up, saving off parameters, and artifacts.
To learn more about Experiments, please consult the [official documentation](https://argo-workflows.readthedocs.io/en/latest/workflow-concepts/).

---

## Use Cases for Argo Workflow
### Examples
Argo Workflows is a versatile tool with a wide range of use cases in the context of Kubernetes and containerized environments. Here are some common use cases where Argo Workflows can be beneficial:

- To orchestrate end-to-end data processing pipelines, including data extraction, transformation, and loading (ETL) tasks.
- In machine learning projects, Argo Workflows can orchestrate tasks such as data preprocessing, model training, evaluation, and deployment.
- Argo Workflows can serve as the foundation for continuous integration and continuous deployment (CI/CD) pipelines. It enables the automation of building, testing, and deploying applications in a Kubernetes environment.
- For batch processing and periodic tasks, Argo Workflows can be configured to run at specified intervals or based on cron schedules. This is useful for automating routine tasks, report generation, and other scheduled jobs.

---

## Lab Exercises

### Lab 4.1. Installing Argo Workflows
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

### Lab 4.2. A Simple DAG Workflow
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

### Lab 4.3. CI/CD Using Argo Workflows
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

# ARGO ROLLOUTS
Advanced Kubernetes deployment strategies such as Canary and Blue-Green made easy.

## Introduction
### Chapter Overview and Objectives
In this chapter, we delve into Argo Rollouts, a pivotal tool within the Argo suite, designed specifically for Continuous Delivery (CD) and GitOps practices. Argo Rollouts can be used as a stand-alone tool and therefore does not require any prior knowledge of ArgoCD (or other Argo-related tools). Through thematic discussions and hands-on labs, we aim to equip you with a comprehensive understanding of Argo Rollouts’ architecture, installation, and usage.

By the end of this chapter, you should be able to:

- Understand and differentiate various Progressive Delivery patterns and decide when to use which.
- Have a thorough understanding of what Argo Rollouts is and in what scenarios it might help.
- Have an overview of Argo Rollouts architecture and functionality.

---

## A Primer on Progressive Delivery

### Essentials of CI/CD and Progressive Delivery in Software Development
Continuous Integration (CI), Continuous Delivery (CD), and Progressive Delivery are key concepts in modern software development, particularly in the context of DevOps and agile practices. They represent different stages or approaches in the software release process. We will discuss them more in this chapter.

Continuous Integration
Continuous Integration is a development practice where developers frequently integrate their code into a shared repository, preferably several times daily. Each integration is then verified by an automated build and automated tests.

CI Features

Frequent code commits
Encourage developers to often integrate their code into the main branch, reducing integration challenges.

Automated tests
Cover frequent code commits. Automatically running tests on the new code to ensure it integrates well with the existing codebase. This does not only include unit tests, but also any other higher-order testing method, such as integration- or end-to-end tests.

Immediate problem detection
Allows for quick detection and fixing of integration issues.

Reduced integration problems
Help to minimize the problems associated with integrating new code.

The main goal of CI is to provide rapid feedback so that if a defect is introduced into the code base, it is identified and corrected as soon as possible.

Once code is in our main branch, it is **not deployed** in production or even released. This is where the concept of Continuous Delivery comes into play.

---

### Continuous Delivery
Continuous Delivery is an extension of CI, ensuring the software can be reliably released anytime. It involves the automation of the entire software release process.

CD Features

Automated release process
Every change that passes the automated tests can be released to production through an automated process.

Reliable deployments
Ensure that the software is always in a deployable state.

Rapid release cycles
Facilitate frequent and faster release cycles.

Close collaboration between teams
A close alignment between development, QA, and operations teams is required.

The objective of Continuous Delivery is to establish a process where software deployments become predictable, routine, and can be executed on demand.

---

### Progressive Delivery
Progressive delivery is often described as an evolution of continuous delivery. It focuses on releasing updates of a product in a controlled and gradual manner, thereby reducing the risk of the release, typically coupling automation and metric analysis to drive the automated promotion or rollback of the update.

Progressive Delivery Features

Canary releases
Gradually roll out the change to a small subset of users before rolling it out to the entire user base.

Feature flags
Control who gets to see what feature in the application, allowing for selective and targeted deployment.

Experiments & A/B testing
Test different versions of a feature with different segments of the user base.

Phased rollouts
Slowly roll out features to incrementally larger segments of the user base, monitoring and adjusting based on feedback.

The primary goal of Progressive Delivery is to reduce the risk associated with releasing new features and to enable faster iteration by getting early feedback from users.

---

### Deployment Strategies
Every software system is different, and deploying complex systems oftentimes requires additional steps and checks. This is why different deployment strategies emerged over time to manage the process of deploying new software versions in a production environment.

These strategies are an integral part of DevOps practices, especially in the context of CI/CD workflows. The choice of a deployment strategy can significantly impact the availability, reliability, and user experience of a software application or software service.

On the following pages, we will present the four most important deployment strategies and discuss their impact on user experience during deployment:

- Recreate/fixed deployment
- Rolling update
- Blue-green deployment
- Canary deployment

---

### Recreate/Fixed Deployment
A Recreate deployment deletes the old version of the application before bringing up the new version. As a result, this ensures that two versions of the application never run at the same time, but there is downtime during the deployment. This strategy is an option for the Kubernetes Deployment object.

https://d36ai2hkxl16us.cloudfront.net/thoughtindustries/image/upload/a_exif,c_fill,w_400/v1/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/cgubr0nkyehu-LFS256_CourseTrainingGraphics_6.png

Distribution of old and new versions using the fixed deployment strategy

---

### Rolling Update
A Rolling Update slowly replaces the old version with the new version. As the new version comes up, the old version is scaled down in order to maintain the overall count of the application. This reduces downtime and risk as the new version is gradually deployed. This is the default strategy of the Kubernetes Deployment object.

https://d36ai2hkxl16us.cloudfront.net/thoughtindustries/image/upload/a_exif,c_fill,w_400/v1/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/d8b2bseu83sj-LFS256_CourseTrainingGraphics_10.png

Distribution of old and new versions using the rolling update strategy

---

### Blue-Green Deployment
A blue-green deployment (sometimes referred to as a red/black) has both the new and old versions of the application deployed at the same time. During this time, only the old version of the application will receive production traffic. This allows the developers to run tests against the new version before switching the live traffic to the new version. Once the new version is ready and tested, the traffic is switched (often at the load balancer level) from the old environment to the new one. The advantage here is a quick rollback in case of issues and minimal downtime during deployment.

An important drawback of a blue-green deployment is, that twice the amount of instances is created during the time of the deployment. This is a common show-stopper for this pattern.

To learn more about the [blue-green deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html), see the article by Martin Fowler.

https://d36ai2hkxl16us.cloudfront.net/thoughtindustries/image/upload/a_exif,c_fill,w_400/v1/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/rehxyk8d5sbj-LFS256_CourseTrainingGraphics_9.png

Distribution of old and new versions using the blue-green deployment strategy

---

### Canary Deployment
A small subset of users are directed to the new version of the application while the majority still use the old version. Based on the feedback and performance of the new version, the deployment is gradually rolled out to more users. This reduces risk by affecting a small user base initially, allows for A/B testing and real-world feedback. While this is technically possible in native Kubernetes by manually adjusting Service Selectors between the “old” and “new” versions of a deployment, having an automated solution is more ideal.

Some more detailed information can be found in the [Canary Release](https://martinfowler.com/bliki/CanaryRelease.html) article by Danilo Sato.

https://d36ai2hkxl16us.cloudfront.net/thoughtindustries/image/upload/a_exif,c_fill,w_400/v1/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/lahfmp29r1rn-LFS256_CourseTrainingGraphics_8.png

Distribution of old and new versions using the canary deployment strategy

---

### Strategies for Smooth and Reliable Releases
In summary, deployment strategies are fundamental in modern software development and operations for ensuring smooth, safe, and efficient software releases. They cater to the need for balancing rapid deployment with the stability and reliability of production environments.

Table 5.1: Benefits of Introducing Deployment Strategies
Benefit	Description
Risk mitigation	They allow for safer deployments by reducing the risk of introducing bugs or performance issues into the production environment. Strategies like canary deployments enable gradual exposure to new changes.
User experience	Maintaining a consistent and high-quality user experience is essential. Strategies like blue-green deployments minimize downtime and potential disruptions to the user experience.
Feedback and testing	They provide a framework for gathering real-world user feedback. Canary deployments, in particular, are valuable for understanding how changes perform in a live environment.
Rollback capabilities	In case new versions have critical issues, strategies like blue-green deployments allow for quick rollbacks to the previous stable version.
 

Table 5.2: Common Use Cases for Each Strategy
Strategy	Supported By	Common Use Cases
Fixed deployment	Kubernetes Native	
The most basic way to deploy a workload is whenever downtime is acceptable.
Often stateful workloads (e.g., Databases) require a “recreation” to avoid data corruption.
Rolling update	Kubernetes Native	
Commonly used for stateless, low-maintenance workloads like proxies, RESTful APIs, etc.
Blue-green deployment	Argo Rollouts	
Use when a) you can afford the extra cost of running twice the resources and b) need a quick and easy rollback option.
B/G can also be helpful for experimentation scenarios.
Can be advantageous to update services that depend on stateful connections, e.g., via WebSockets.
Canary deployment	Argo Rollouts	
Use it whenever a partial rollout is desirable (experimentation with a subset of users, desire a gradual rollout over hours or days, want to make rollout dependent on certain conditions).
It can be a good alternative if the deployments are too large and the infra cost of running a full blue-green is too high.

---

## Argo Rollouts Architecture and Core Components

### Building Blocks of Argo Rollouts
In this section, we will discuss the building blocks of Argo Rollouts. To give you an overview of what to expect, we’ll briefly describe the relevant components of an Argo Rollouts setup before we discover them in more detail.

https://d36ai2hkxl16us.cloudfront.net/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/l5bt5neeyrwv-OverviewofcomponentsthattakepartinadeploymentmanagedbyArgoRollouts.png
Overview of components that take part in a deployment managed by Argo Rollouts
Image source: Argo

Argo Rollouts Components

Argo Rollouts Controller
An operator that manages Argo Rollout Resources. It reads all the details of a rollout (and other resources) and ensures the desired cluster state.

Argo Rollout Resource
A custom Kubernetes resource managed by the Argo Rollouts Controller. It is largely compatible with the native Kubernetes Deployment resource, adding additional fields that manage the stages, thresholds, and techniques of sophisticated deployment strategies, including canary and blue-green deployments.

Ingress and the Gateway API
The Kubernetes Ingress resource is used to enable traffic management for various traffic providers such as service meshes (e.g., Istio or Linkerd) or Ingress Controllers (e.g., Nginx Ingress Controller).

The Kubernetes Gateway API is also supported with a separate plugin and provides similar functionality.

Service
Argo Rollouts utilizes the Kubernetes Service resource to redirect ingress traffic to the respective workload version by adding specific metadata to a Service.

ReplicaSet
Standard Kubernetes ReplicaSet resource used by Argo Rollouts to keep track of different versions of an application deployment.

AnalysisTemplate and AnalysisRun
Analysis is an optional feature of Argo Rollouts and enables the connection of Rollouts to a monitoring system. This allows automation of promotions and rollbacks. To perform an analysis an AnalysisTemplate defines a metric query and their expected result. If the query matches the expectation, a Rollout will progress or rollback automatically, if it doesn’t. An AnalysisRuns is an instantiation of an AnalysisTemplate (similar to Kubernetes Jobs).

Metric Providers
Metric providers can be used to automate promotions or rollbacks of a rollout. Argo Rollouts provides native integration for popular metric providers such as Prometheus and other monitoring systems.

Please note, that not all of the mentioned components are mandatory to every Argo Rollouts setup. The usage of Analysis resources or metric providers is entirely optional and relevant for more advanced use cases. Also note that the Argo Rollouts components are independent of other Argo projects (like Argo CD or Argo Workflows) and do not require them to function properly.

---

### A Refresher: The Kubernetes Replica Set

To grasp the workings of Argo Rollouts in handling workloads, it's essential to understand some basics of Kubernetes. Essentially, Argo Rollouts functions in a manner quite similar to Kubernetes Deployment resources. What is less commonly known is that Deployments provide another layer of abstraction for workload management. The Deployment resource was a relatively later addition to Kubernetes, debuting in version 1.5 as part of the apps/v1beta1 API and achieving stability in version 1.9 with the apps/v1 API. Before the introduction of Deployments, workload management was accomplished using ReplicaSets. And under the hood, they are used until today!

A Kubernetes ReplicaSet is a resource used to ensure that a specified number of pod replicas are running at any given time. Essentially, it's a way to manage the lifecycle of pods. The main function of a ReplicaSet is to maintain a stable set of pod replicas running at any given time. It does so by scheduling pods as needed to reach the desired number.

If a pod fails, the ReplicaSet will replace it; if there are more pods than needed, it will terminate the extra pods. ReplicaSets are used to achieve redundancy and high availability within Kubernetes applications.

For more sophisticated orchestration like rolling updates, rollbacks or scaling a ReplicaSet is not enough. Kubernetes introduced a higher-level (and usually better known) concept called Deployment resource that manages both the deployment and updating of applications.

A deployment is managed by the Kubernetes deployment controller and is responsible for updating ReplicaSets by providing declarative updates for them.

Lets create a Deployment of nginx proxies to demonstrate the ownership between Deployment and ReplicaSet.

Command:

$ kubectl create deploy nginx-deployment --image=nginx --replicas=3

Output:

deployment.apps/nginx-deployment created

Now make sure it properly scaled up.

Command:

```shell hl_lines="1"
$ kubectl get deployment
```

Output:

NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           47s

Command:

$ kubectl get replicaset

Output:

NAME                          DESIRED   CURRENT   READY   AGE
nginx-deployment-66fb7f764c   3         3         3       47s

The ReplicaSet nginx-deployment-66fb7f764c is managed by nginx-deployment. You can tell this by inspecting the ReplicaSet with the following command:

kubectl get replicaset nginx-deployment-66fb7f764c -ojsonpath='{.metadata.ownerReferences}' | jq
[
  {
    "apiVersion": "apps/v1",
    "blockOwnerDeletion": true,
    "controller": true,
    "kind": "Deployment",
    "name": "nginx-deployment",
    "uid": "1dd44efd-aab5-4475-aff2-32670201e2ef"
  }
]

As we see, the ownerReferences of the ReplicaSet state, that this resource is “owned” by a Deployment resource with the uid “1dd44efd-aab5-4475-aff2-32670201e2ef”. And indeed, this uid matches with the other Deployment we just created.

Command:

```shell hl_lines="1"
kubectl get deployment nginx-deployment -ojsonpath='{.metadata.uid}'
```

Output:

1dd44efd-aab5-4475-aff2-32670201e2ef

Deployments are a great invention of vanilla Kubernetes and are a successful abstraction. Rarely do people manage their pods manually through ReplicaSets. Deployments are the standard.

But despite all the praise, Deployment resources are still limited in their capabilities. They still do not support all deployment strategies we described in the previous section, “A Primer on Progressive Delivery”.

Let's talk about Argo Rollouts!

---

### Argo Rollouts
Here, we will explore the Argo Rollouts resource, which is the central element in Argo Rollouts, enabling advanced deployment strategies. A Rollout, in essence, is a Kubernetes resource that closely mirrors the functionality of a Kubernetes Deployment object. However, it steps in as a more advanced substitute for Deployment objects, particularly in scenarios demanding intricate deployment of progressive delivery techniques.

---

### Key Features of Argo Rollouts
Argo Rollouts outshine regular Kubernetes Deployments with several enhanced features.

Select "Expand" to learn more about them.

Argo Rollouts Functionalities

Blue-green deployments
This approach minimizes downtime and risk by switching traffic between two versions of the application.

Canary deployments
Gradually roll out changes to a subset of users to ensure stability before full deployment.

Advanced traffic routing
Integrates seamlessly with ingress controllers and service meshes, facilitating sophisticated traffic management.

Integration with metric providers
Offers analytical insights for blue-green and canary deployments, enabling informed decisions.

Automated decision making
Automatically promote or roll back deployments based on the success or failure of defined metrics.

The Rollout resource is a custom Kubernetes resource introduced and managed by the Argo Rollouts Controller. This Kubernetes controller monitors resources of type Rollout and ensures that the described state will be reflected in the cluster.

The Rollout resource maintains high compatibility with the conventional Kubernetes Deployment resource but is augmented with additional fields. These fields are instrumental in governing the phases, thresholds, and methodologies of advanced deployment approaches, such as canary and blue-green strategies.

It’s crucial to understand that the Argo Rollouts controller is attuned exclusively to changes in Rollout resources. It remains inactive for standard deployment resources. Consequently, to use the Argo Rollouts for existing Deployments, a migration from traditional Deployments to Rollouts is required.

Overall, Deployment and Rollout resources look pretty similar. Refer to the following table to understand the minimal differences between both.

 

Table 5.3: Deployment and Argo Rollout Resource in Comparison
Deployment Resource	Argo Rollout Resource	Comment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:	apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: nginx-rollout
spec:	Basic resource metadata.
  replicas: 3	  replicas: 3	Number of desired pods. Defaults to 1.
  selector:
    matchLabels:
      app: nginx	  selector:
    matchLabels:
      app: nginx	Label selector for pods.
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx	  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx	Describes the pod template that will be used to instantiate pods. The template does not differ.
  strategy:
    type: RollingUpdate	  strategy:
    blueGreen: {}	
A Deployment strategy can be either “RollingUpdate” (default) or “Recreate”.

A Rollout strategy can either be “blueGreen” or “canary”.

 

Of course, there are way more configuration options to control the behavior of a Rollout. Please refer to the official Argo Rollouts specification for more options.

---

### Migrating Existing Deployments to Rollouts
The similarity of Deployments and Rollouts spec makes it easier to convert from one to the other resource type. Argo Rollouts supports a great way to migrate existing Deployment resources to Rollouts.

By providing a spec.workloadRef instead of spec.template a Rollout can refer to a Deployments template:

apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: nginx-rollout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  workloadRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
[...]

The Rollout will fetch the template information from the Deployment (in our example named nginx-deployment) and start the in the Rollout specified number of pods.

Please note, that lifecycles of Deployment and Rollouts are distinct and managed by their respective controllers. This means that the Kubernetes Deployment controller will not start to manage Pods created by the Rollout. Also, the Rollout will not start to manage pods that are controlled by the Deployment.

This enables a zero-downtime introduction of Argo Rollouts to your existing cluster. It furthermore makes experimentation with multiple deployment scenarios possible.

---

### Discussion: Create Rollouts or Reference Deployments from Rollouts?
As Rollout resources can exist and operate without vanilla Deployments, the following question might arise: Should I always reference Deployments or is it better to start over with an independent Rollout resource, without the dependency of a reference?

And the simple answer to it is… it depends.

Generally, workloadRef has been invented to enable a simple and seamless way of migrating from Deployments to Rollouts. We even consider it useful as Administrators who are unfamiliar with Argo Rollouts might be confused if they see an array of Pods running but neither a running Deployment nor StatefulSet. To lower the barrier, referencing existing Deployments from a Rollout can be a good option.

If you use Deployment referencing, the Argo controller will copy the generation number of the referenced Deployment and stores it in a status field called workloadObservedGeneration. Therefore the rollouts own rollout.argoproj.io/workload-generation annotation should always match the generation of the deployment. This helps to identify deviation due to manipulation of either of the resources.

However, referencing comes at the cost of another resource dependency. Yet another resource to check in case of failure!

So, if you are sure you want to work with Argo Rollouts, use the native Rollout Resource.

Hint: It is also possible to migrate a Rollout resource to a native Deployment. Please refer to the official documentation for further information.

Additional learning resources:

- To explore the detailed specification of a Rollout, visit Argo Rollouts Specification.
- For guidance on transitioning from a Deployment to a Rollout, consult Migrating a Deployment to Rollout.

---

### Additional Building Blocks
While the Argo Rollouts Controller and the corresponding Rollout resource are the core components, there are further building blocks that enable and extend the functionality of Argo Rollouts.

https://d36ai2hkxl16us.cloudfront.net/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/c6ns8puvi6ia-LFS256_CourseTrainingGraphics_4.png

Overview of components that take part in a deployment managed by Argo Rollouts
Image source: Argo

Let's learn more about them.

---

### Ingress and Service Resources
Select "Expand" for more information.

Relevant Resources for Traffic Routing

Close Kubernetes Ingress
A Kubernetes Ingress is a Kubernetes native resource that manages external access to services in a cluster (typically via HTTP). An Ingress allows defining rules for inbound connections to reach cluster-internal Kubernetes Services. As such, they are an important abstraction to programmatically control the flow of incoming network traffic. They can even be used for SSL/TLS termination.

This approach is expanded by the Kubernetes Gateway API. The Gateway API splits the Ingress approach into the Kubernetes Gateway and Kubernetes HTTPRoute - the latter of which is managed by Argo Rollouts as it did Ingress. The advantage is that the Gateway API provides additional modes of access beyond HTTP/HTTPS and does not require controller-specific code like Ingress did.

Close Kubernetes Service
A Kubernetes Service is a resource that abstracts how to expose an application running on a set of Pods. Services can load-balance traffic and provide service discovery within the cluster. The primary role of a Service is to provide a consistent IP address and port number for accessing the running application, irrespective of the changes in the pods.

In the context of Argo Rollouts, these resources play a pivotal role when it comes to, for example, canary deployments. The general behavior of Service and Ingress resources is no different when used with Argo. Argo Rollouts uses Kubernetes Services to manage traffic flow to different versions of an application during a rollout process and they do so by augmenting the service with additional metadata.

Close Pod Template Hash
Argo Rollouts utilizes the Pod Template Hash, which uniquely identifies Pods of a common ReplicaSset. So to switch incoming traffic from the “old” ReplicaSet to our new ReplicaSet, the Argo Rollouts controller mutates the Service spec.selector to match the new Pod Template Hash.

https://d36ai2hkxl16us.cloudfront.net/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/n49apqkxyhwu-LFS256_CourseTrainingGraphics_7.png

Kubernetes Services have selectors that find matching pods according to their label set; the pod-template-hash label is added to every ReplicaSet and used to make routing decisions

Close Stable/Canary ReplicaSets
By introducing a “stable service” and “canary services” in the Rollouts Spec, Argo can not only switch the traffic to Stable/Canary ReplicaSets, but also decide about the distribution of which ReplicaSet should receive how much traffic.

---

### Rollout Analysis & Experiments
The ability to split traffic between stable and canary workloads is good. But how do we decide if the canary workload is performing well and is therefore considered "stable"? That's right, metrics! An operator would closely observe the monitoring system (e.g., Prometheus, VMWare Wavefront or others) for certain metrics that indicate the application is working well. If you're thinking that this "observing metrics and making a decision" could be automated, you're right!

Argo Rollouts allows the user to run “Analysis” during the progressive delivery process. It primarily focuses on evaluating and ensuring the success of deployment based on defined criteria. These criteria can include custom metrics of your specific metric monitoring provider (see the official documentation for a conclusive list of supported metric providers).

The analysis process in Argo Rollouts involves following custom resources that work hand in hand with the already discussed resources.

Table 5.4: Analysis Custom Resource Definitions
Templates	Description/Use Case
AnalysisTemplate	This template defines the metrics to be queried and the conditions for success or failure. The AnalysisTemplate specifies what metrics should be monitored and the thresholds for determining the success or failure of a deployment. It can be parameterized with input values to make it more dynamic and adaptable to different situations.
AnalysisRun	An AnalysisRun is an instantiation of an AnalysisTemplate. It is a Kubernetes resource that behaves similarly to a job in that it runs to completion. The outcome of an AnalysisRun can be successful, failed, or inconclusive, and this result directly impacts the progression of the Rollout's update. If the AnalysisRun is successful, the update continues; if it fails, the update is aborted; and if it's inconclusive, the update is paused.

Analysis resources allow Argo Rollouts to make informed decisions during the deployment process, like promoting a new version, rolling back to a previous version, or pausing the rollout for further investigation based on real-time data and predefined success criteria.

AnalysisRuns support various providers like Prometheus or multiple other monitoring solutions to obtain measurements for analysis. Those measurements can then be used to automate promotion decisions.

Besides just looking at metrics, there are other ways to decide if your rollout is doing well. The most basic (but commonly used) one might be the Kubernetes “Job” provider: if a job is successful, the metric is considered “successful". If the job returns with anything else than return code zero, the metric is considered “failed”.

The Web provider helps with seamless integration to custom services to help make promotion decisions.

Remember, it's not mandatory to use analysis and metrics when you're rolling out updates in Argo Rollouts.

If you want, you can control the rollout yourself. This means you can stop or advance the rollout whenever you choose. You can do this through the API or the command line. Also, you don't have to rely on automatic metrics for using Argo Rollouts. It's totally fine to combine automatic steps, like those based on analysis, with your own manual steps.

---

### Experiments
Experiments are an extended feature of Argo Rollouts designed to test and evaluate changes in two or more versions of an application in a controlled, temporary environment. The Experiment custom resource can launch AnalysisRuns alongside ReplicaSets. This is useful to confirm that new ReplicaSets are running as expected.

You can use experiments in Argo Rollouts to test different versions of your app at the same time. This is like doing A/B/C testing. You can set up each experiment with its own version of the app to see which one works best. Each experiment uses a template to define its specific version of the app.

The great thing about these experiments is that you can run several of them simultaneously, and each one is separate from the others. This means they don't interfere with each other.

To learn more about Analysis or Experiments, please consult the official documentation.

---

## Lab Exercises

### Lab 5.1. Installing Argo Rollouts
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

### Lab 5.2. Argo Rollouts Blue-Green
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

### Lab 5.3. Migrating an Existing Deployment to Argo Rollouts
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

# ARGO EVENTS

## Introduction
### Chapter Overview and Objectives
In this chapter, we discuss Argo Events, exploring its role in implementing event-driven architecture within Kubernetes. Starting with a conceptual overview, we'll understand the key components of Argo Events—Event Sources, Sensors, EventBus, and Triggers, and their significance in Kubernetes. The chapter then transitions to practical learning, with labs focused on configuring event sources and triggers, and integrating Argo Events with external systems like webhooks and message queues.

By the end of this chapter, you should be able to:

- Learn how event sources initiate the event-driven process in Kubernetes.
- Understand the detection and response mechanism of sensors and triggers in event-driven systems.
- Grasp the importance of the EventBus in managing event flow within Argo Events.

---

## The Main Components
### Event-Driven Architecture
In this section, we explore the concept of event-driven architecture (EDA) and its practical application in Kubernetes environments. Unlike traditional architectures where components operate in a linear, request-response manner, EDA is based on a more dynamic and fluid model. This model is particularly relevant in Kubernetes, a system that manages containerized applications across clusters and thrives on responsiveness and adaptability.

At the core of Kubernetes are events - these are various actions or changes within the system, like pod lifecycle changes or service updates. EDA in Kubernetes involves responding to these events in a way that's both automated and scalable. This method of operation allows for a more efficient handling of the ever-changing state within a Kubernetes cluster.

Argo Events enters the picture as a tool designed for Kubernetes, aimed at facilitating the implementation of event-driven paradigms. It isn't just an add-on but rather an integration that amplifies Kubernetes' capabilities. Let's take a look at the main components of Argo Events.

Event Source: This is where events are generated. Event sources in Argo Events can be anything from a simple webhook or a message from a message queue, to a scheduled event. Understanding event sources is key to knowing how your system will interact with various external and internal stimuli. An example of an event source is provided below:

apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: webhook-example
spec:
  service:
    ports:
      - port: 12000
        targetPort: 12000
  webhook:
    example-endpoint:
      endpoint: /example
      method: POST

Sensor: Sensors are the event listeners in Argo Events. They wait for specific events from the event sources and, upon detecting these events, trigger predefined actions. Understanding sensors involves knowing how to respond to different types of events. A sensor would be specified with the following spec:

apiVersion: argoproj.io/v1alpha1
kind: Sensor
metadata:
  name: webhook-sensor
spec:
  dependencies:
    - name: example-dep
      eventSourceName: webhook-example
      eventName: example-endpoint
  triggers:
    - template:
        name: k8s-trigger
        k8s:
          group: batch
          version: v1
          resource: jobs
          operation: create
          source:
            resource:
              apiVersion: batch/v1
              kind: Job
              metadata:
                generateName: webhook-job-
              spec:
                template:
                  spec:
                    containers:
                      - name: hello
                        image: busybox
                        command: ["echo", "Hello from Argo Sensor!"]
                    restartPolicy: Never

EventBus: The EventBus acts as a backbone for event distribution within Argo Events. It's responsible for managing the delivery of events from sources to sensors. Understanding the EventBus is crucial for managing the flow of events within your system.

apiVersion: argoproj.io/v1alpha1
kind: EventBus
metadata:
  name: default
spec:
  nats:
    native:
      replicas: 1

Trigger: Triggers in Argo Events are the mechanisms that respond to events detected by sensors. They can perform a wide range of actions, from starting a workflow to updating a resource. Understanding triggers is essential for automating responses to events. Triggers are defined within a sensor specification, so the following excerpt focuses on the trigger itself:

trigger:
  template:
    name: argo-workflow-trigger
    argoWorkflow:
      source:
        resource:
          apiVersion: argoproj.io/v1alpha1
          kind: Workflow
          metadata:
            generateName: hello-world-
          spec:
            entrypoint: whalesay
            templates:
            - name: whalesay
              container:
                image: docker/whalesay:latest
                command: [cowsay]
                args: ["Hello from Argo Events!"]

Architecture of Argo Events

 

The image depicts the architecture of Argo Events, showing three main components: Event Source, Event Bus, and Sensor, each with a controller and deployment. The Event Source receives various events (like SNS, SQS, GCP PubSub, S3, Webhooks, etc.), which are managed by the Event Source Controller and passed on to the Event Source Deployment. This connects to the Event Bus with NATS Streaming through the Event Bus Controller. Finally, the Sensor Controller manages the Sensor Deployment, which triggers workflows in Kubernetes and functions in AWS Lambda, illustrated by respective icons.

--- 

## Lab Exercises
### Lab 6.1. Setting Up Event Triggers with Argo
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

### Lab 6.2. Integrating Argo Events with External Systems
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

## Argo Rollouts


## Argo Events
Event based dependency management for Kubernetes.


<div class="admonition note">
  <p class="admonition-title">Documentations</p>

```embed
url: https://argoproj.github.io/
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg
```

```embed
url: https://github.com/akuity/awesome-argo
```

```embed
url: https://argo-workflows.readthedocs.io/en/latest/
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg
```

```embed
url: https://argo-cd.readthedocs.io/en/stable/
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg
```

```embed
url: https://argoproj.github.io/argo-rollouts/
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg
```

```embed
url: https://argoproj.github.io/argo-events/
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg
```

```embed
url: https://training.linuxfoundation.org/certification/certified-argo-project-associate-capa/
```
</div>
