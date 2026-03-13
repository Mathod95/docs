---
title: Argo
---

## Chapter Overview and Objectives
Before you start working with Argo and exploring its powerful workflow management features in Kubernetes, it’s important to establish a strong understanding of the core concepts. This chapter provides that foundation by introducing the essential ideas you’ll need to understand how Argo operates in a Kubernetes environment.

By the end of this chapter, you should be able to:

Explain the key concepts behind Argo.
Describe common use cases for the Argo suite.
Identify Kubernetes's role in supporting Argo.
Install Kubernetes to prepare your environment for the Argo suite.

## What Is Argo?

**Open source tools for Kubernetes to run workflows, manage clusters, and do GitOps right.**

![](../../assets/images/argo/argo-horizontal-color.svg)

Argo is a set of Kubernetes-native tools that enhance the workflow management capabilities of Kubernetes. It includes Argo Continuous Delivery (CD) for state management, Argo Workflows for running complex jobs, Argo Events for event-based dependency management, and Argo Rollouts for progressive delivery. These tools are designed to help you automate and manage tasks in a Kubernetes environment, making it easier to deploy, update, and manage applications. Each of these tools can run independently and do not require the others to work, but they are capable of working together.

Let’s discuss them in more detail.

---

## Argo Continuous Delivery (CD)

**Declarative continuous delivery with a fully-loaded UI.**

![](../../assets/images/argo/gitops-cd.avif){ align=right width="200" }

Argo CD is a declarative GitOps continuous delivery (CD) tool designed for Kubernetes. It automates the process of applying Kubernetes manifests from a Git repository to a cluster and continuously monitors the repository for changes. When updates are detected, Argo CD automatically synchronizes the cluster to match the desired configuration defined in Git. This makes it an ideal tool for managing both infrastructure and application deployments, ensuring that production environments always reflect the exact state specified in version control.

---

## Argo Workflows

**Kubernetes-native workflow engine supporting DAG and step-based workflows.**

![](../../assets/images/argo/workflows.avif){ align=left width="200" }

Argo Workflows, as an extension of the Kubernetes API, introduces a new Workflow CRD, providing companies with a highly adaptable batch resource akin to a Kubernetes Job. This extensibility renders Workflows versatile and applicable across various domains, with a particular spotlight on its efficacy in Machine Learning (ML) and Data pipelines. Using Argo Workflows in these contexts has become a strategic move for numerous companies, unraveling its potential in orchestrating complex processes seamlessly.

At its core, Argo Workflows operate on a unique set of characteristics and use cases. Each step within a workflow runs as a pod, contributing to the modularity and scalability of the overall process. This design allows for streamlined parallelism and efficient resource utilization. Predominantly, Argo Workflows work well in data processing and automation scenarios, exemplified by the fan-out fan-in pattern. This pattern enables the workflow to distribute tasks widely, execute them concurrently, and then consolidate the results, making Argo Workflows a robust choice for scenarios demanding intricate data manipulation and automated processes.

??? Note "TLDR"
    **What is Argo Workflows?**

    Argo Workflows is an open source container-native workflow engine for orchestrating parallel jobs on Kubernetes. Argo Workflows is implemented as a Kubernetes CRD.

    - Define workflows where each step in the workflow is a container.
    - Model multi-step workflows as a sequence of tasks or capture the dependencies between tasks using a graph (DAG).
    - Easily run compute intensive jobs for machine learning or data processing in a fraction of the time using Argo Workflows on Kubernetes.
    - Run CI/CD pipelines natively on Kubernetes without configuring complex software development products.

    **Why Argo Workflows?**

    - Designed from the ground up for containers without the overhead and limitations of legacy VM and server-based environments.
    - Cloud agnostic and can run on any Kubernetes cluster.
    - Easily orchestrate highly parallel jobs on Kubernetes.
    - Argo Workflows puts a cloud-scale supercomputer at your fingertips!

    [Documentation](https://argo-workflows.readthedocs.io/en/latest/){ .md-button }
---

## Argo Rollouts

**Advanced Kubernetes deployment strategies such as Canary and Blue-Green made easy.**

![](../../assets/images/argo/rollouts.avif){ align=right width="200" }

Argo Rollouts is a progressive delivery controller for Kubernetes. It was born out of necessity due to Kubernetes’ lack of more sophisticated deployment strategies. Argo Rollouts provides blue-green and canary update strategies, integrates with service meshes and ingress controllers to shape traffic, and automates promotion and rollback based on analysis. It is used to safely deploy new application features into Production without manual analysis, testing, or intervention.

??? Note "TLDR"

    **What is Argo Rollouts?**

    Argo Rollouts is a Kubernetes controller and set of CRDs which provide advanced deployment capabilities such as blue-green, canary, canary analysis, experimentation, and progressive delivery features to Kubernetes.

    Argo Rollouts (optionally) integrates with ingress controllers and service meshes, leveraging their traffic shaping abilities to gradually shift traffic to the new version during an update. Additionally, Rollouts can query and interpret metrics from various providers to verify key KPIs and drive automated promotion or rollback during an update.

    **Why Argo Rollouts?**

    The native Kubernetes Deployment Object supports the RollingUpdate strategy which provides a basic set of safety guarantees (readiness probes) during an update. However the rolling update strategy faces many limitations:

    - Few controls over the speed of the rollout
    - Inability to control traffic flow to the new version
    - Readiness probes are unsuitable for deeper, stress, or one-time checks
    - No ability to query external metrics to verify an update
    - Can halt the progression, but unable to automatically abort and rollback the update

    For these reasons, in large scale high-volume production environments, a rolling update is often considered too risky of an update procedure since it provides no control over the blast radius, may rollout too aggressively, and provides no automated rollback upon failures.

    **Controller Features**

    - Blue-Green update strategy
    - Canary update strategy
    - Fine-grained, weighted traffic shifting
    - Automated rollbacks and promotions
    - Manual judgement
    - Customizable metric queries and analysis of business KPIs
    - Ingress controller integration: NGINX, ALB
    - Service Mesh integration: Istio, Linkerd, SMI
    - Metric provider integration: Prometheus, Wavefront, Kayenta, Web, Kubernetes Jobs

    [Documentation](https://argo-rollouts.readthedocs.io/en/stable/){ .md-button }

---

## Argo Events

**Event based dependency management for Kubernetes**

![](../../assets/images/argo/events.avif){ align=left width="200" }

Argo Events is an event-driven workflow automation framework for Kubernetes that helps you trigger Kubernetes objects, Argo Workflows, serverless workloads, and other processes in response to events from various sources such as webhooks, S3, schedules, messaging queues, GCP PubSub, and more. It supports events from over 20 event sources and allows you to customize business-level constraint logic for workflow automation.

Argo Events is composed of two main components: Triggers and Event Sources. Triggers are responsible for executing actions when an event occurs, while Event Sources are responsible for generating events.

Some of the use cases of Argo Events include automating research workflows, designing a complete CI/CD pipeline, and automating everything by combining Argo Events, Workflows & Pipelines, CD, and Rollouts.

??? note "TLDR"

    **What is Argo Events?**

    Argo Events is an event-based dependency manager for Kubernetes which helps you define multiple dependencies from a variety of event sources like webhook, s3, schedules, streams etc. and trigger Kubernetes objects after successful event dependencies resolution.

    **Features**

    - Manage dependencies from a variety of event sources.
    - Ability to customize business-level constraint logic for event dependencies resolution.
    - Manage everything from simple, linear, real-time dependencies to complex, multi-source, batch job dependencies.
    - Ability to extends framework to add your own event source listener.
    - Define arbitrary boolean logic to resolve event dependencies.
    - CloudEvents compliant.
    - Ability to manage event sources at runtime.

    [Documentation](https://argoproj.github.io/argo-events/){ .md-button }

---

## Benefits of Using Argo
Using Argo for continuous delivery offers several benefits. We will now explore some of them.

Argo is a popular open source tool that brings the practicality of GitOps to anyone who uses Kubernetes. By enabling GitOps, Argo can enhance the robustness, security, and reliability of Kubernetes environments. This technical practice can be highly beneficial to DevOps teams, improving their efficiency.

Argo is designed from the ground up for a modern containerized environment. Argo CD as an example is equipped with a powerful GUI and CLI, enabling all seniority levels of engineers to work with it and implement highly sophisticated custom solutions. Argo Rollouts on the other hand supports progressive delivery strategies like canary and blue-green deployments, which are difficult to implement in plain Kubernetes.

The automation provided by Argo speeds up the entire process of pushing new features, leading to faster and more frequent deployments. If any issues are detected based on defined metrics, the deployment can be automatically rolled back to the previous working deployment, allowing for faster error resolution.

One of the benefits of using Git and GitOps principles is the built-in auditing, which gives you the benefit of having the entire history of your software tracked over time. Argo makes it easy to specify, schedule, and coordinate the running of complex workflows and applications on Kubernetes.

Argo's integration with other Cloud Native Computing Foundation (CNCF) projects is a significant advantage. It uses or integrates with CNCF projects like gRPC, Prometheus, NATS, Helm, and CloudEvents. This integration allows for seamless interoperability and enhanced functionality within the cloud native ecosystem. For instance, Prometheus can be used for monitoring and alerting purposes, while Helm can help manage Kubernetes applications. NATS can provide a high-performance messaging system, and CloudEvents can offer a standard way to define the format of event data in a consistent way across services, platforms, and systems. Therefore, by using Argo, you can leverage the benefits of these CNCF projects, leading to more robust, scalable, and efficient cloud native applications.