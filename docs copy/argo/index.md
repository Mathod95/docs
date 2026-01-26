---
title: Introduction to Argo 
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
  - GitOps
author: "Mathias FELIX"
---

# KODEKLOUD #

## GITOPS

### Introduction:

- [What is GitOps](https://blog.mathod.fr/argo/gitops/introduction/#what-is-gitops)
- GitOps Workflow
- GitOps Principles
- DevOps vs GitOps
- Push vs Pull
- GitOps Feature Set
- GitOps Benefits Drawbacks
- GitOps Projects Tools

---

## ARGO

### ArgoCD Basics:

- WhatWhyHow ArgoCD
- ConceptsTerminology
- Features
- Architecture
- Installation Options
- ArgoCD Installation
- ArgoCD App projects
- Create Application using UI
- Create Application using CLI
- Create ArgoCD Project

### ArgoCD Intermediate:

- Reconciliation loop
- Git Webhook Configuration
- Application health
- Application Custom Health Check
- Types of Sync Strategies
- Application Synchronization Options
- Declarative Setup
- Declarative Setup Mono Application
- App of Apps
- Declarative Setup App of Apps
- Deploy apps using HELM Chart
- Deploy apps using HELM Chart
- Multi cluster application deployment
- Multi cluster application deployment

### ArgoCD AdvancedAdmin:

- User Management RBAC ArgoCD
- ArgoCD User Management RBAC
- Dex Okta Connector
- Dex Okta Connector
- Bitnami Sealed Secrets
- Bitnami Sealed Secrets
- Hashicorp Vault
- Hashicorp Vault 2
- ArgoCD Vault Plugin CLI
- ArgoCD Vault Plugin with ArgoCD
- ArgoCD Metrics Monitoring
- ArgoCD Metrics Monitoring 2
- Monitoring through Prometheus Grafana
- Raise Alert using AlertManager
- ArgoCD Notifications
- ArgoCD Notifications with Slack

### ArgoCD with Jenkins CI Pipeline:

- CICD with GitOps
- Git Reposiories Dockerfile and Application Walkthrough
- Jenkinsfile Walkthrough
- CICD Pipeline Demo

---

# CNCF 

## ARGO

### Introduction

- Chapter Overview and Objectives

### Essential Concepts for Argo

- What Is GitOps?

### Argo Overview

- What Is Argo?
- Argo Continuous Delivery (CD)
- Argo Workflows
- Argo Events
- Argo Rollouts
- Benefits of Using Argo

### Benefits of Using Argo

- Step-by-Step: Deploying Kubernetes for Argo
- Installing Docker
- Installing kubectl
- Installing kind and Creating a Cluster

---

## ARGO CD

### Introduction

- Chapter Overview and Objectives

### Argo CD Overview

- What Is Argo CD?

## The Architecture of Argo CD

- Vocabulary

### Core Components

- Controllers
- API Server
- Repository Server
- Application Controller
- 
### Understanding Reconciliation and Synchronization Control

- How Does the Argo CD Reconciliation Loop Work?
- Synchronization Principles

### Objects & Resources

- Simplifying Application Management

### Argo CD Extensions & Integrations

- Plugins
- Understanding Plugins in Argo CD
- Configuring Plugins with ConfigMaps
- How Plugins Work in Argo CD
- Plugins in Action: Notifications and Beyond

### Best Practices

- Securing Argo CD

### Note on Helm and Kustomize

- Enhancing Deployment Efficiency with Helm and Kustomize

### Lab Exercises

- Lab 3.1. Installing Argo CD
- Lab 3.2. Managing Applications with Argo CD
- Lab 3.3. Argo CD Security and RBAC

---

## ARGO WORKFLOWS

### [Introduction](https://blog.mathod.fr/argo/argo_workflows/introduction/#introduction)

- [Chapter Overview and Objectives](https://blog.mathod.fr/argo/argo_workflows/introduction/#chapter-overview-and-objectives)

### [Argo Workflows Core Concepts](https://blog.mathod.fr/argo/argo_workflows/coreConcepts/#argo-workflows-core-concepts)

- [Workflow](https://blog.mathod.fr/argo/argo_workflows/coreConcepts/#workflow)
- [Template Types](https://blog.mathod.fr/argo/argo_workflows/coreConcepts/#workflow)
- [Outputs](https://blog.mathod.fr/argo/argo_workflows/coreConcepts/#outputs)
- [WorkflowTemplate](https://blog.mathod.fr/argo/argo_workflows/coreConcepts/#workflowtemplate)

### [Argo Workflows Architecture](https://blog.mathod.fr/argo/argo_workflows/architecture/#argo-workflows-architecture)

- [Defining Argo Workflows and Its Components](https://blog.mathod.fr/argo/argo_workflows/architecture/#defining-argo-workflows-and-its-components)
- [Argo Workflow Overview](https://blog.mathod.fr/argo/argo_workflows/architecture/#argo-workflow-overview)

### [Use Cases for Argo Workflow](https://blog.mathod.fr/argo/argo_workflows/useCase/)

- [Examples](https://blog.mathod.fr/argo/argo_workflows/useCase/#examples)

### Lab Exercises

- [Lab 4.1. Installing Argo Workflows](https://blog.mathod.fr/argo/argo_workflows/labs/labs01/#installing-argo-workflows)
- [Lab 4.2. A Simple DAG Workflow](https://blog.mathod.fr/argo/argo_workflows/labs/labs02/#a-simple-dag-workflow)
- [Lab 4.3. CI/CD Using Argo Workflows](https://blog.mathod.fr/argo/argo_workflows/labs/labs03/#cicd-using-argo-workflows)

---

## ARGO ROLLOUTS

### [Introduction](https://blog.mathod.fr/argo/argo_rollouts/introduction/introduction/)

- [Chapter Overview and Objectives](https://blog.mathod.fr/argo/argo_rollouts/introduction/introduction/#chapter-overview-and-objectives)

### [A Primer on Progressive Delivery](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/)

- [Essentials of CI/CD and Progressive Delivery in Software Development](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#essentials-of-cicd-and-progressive-delivery-in-software-development)
- [Continuous Integration](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#continuous-integration)
- [Continuous Delivery](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#continuous-delivery)
- [Progressive Delivery](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#progressive-delivery_1)
- [Deployment Strategies](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#deployment-strategies)
- [Recreate/Fixed Deployment](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#deployment-strategies)
- [Rolling Update](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#rolling-update)
- [Blue-Green Deployment](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#blue-green-deployment)
- [Canary Deployment](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#canary-deployment)
- [Strategies for Smooth and Reliable Releases](https://blog.mathod.fr/argo/argo_rollouts/progressiveDelivery/progressiveDelivery/#strategies-for-smooth-and-reliable-releases)

### [Argo Rollouts Architecture and Core Components](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/)

- [Building Blocks of Argo Rollouts](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#building-blocks-of-argo-rollouts)
- [A Refresher: The Kubernetes Replica Set](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#a-refresher-the-kubernetes-replica-set)
- [Argo Rollouts](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#argo-rollouts)
- [Key Features of Argo Rollouts](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#key-features-of-argo-rollouts)
- [Migrating Existing Deployments to Rollouts](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#migrating-existing-deployments-to-rollouts)
- [Discussion: Create Rollouts or Reference Deployments from Rollouts?](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#key-features-of-argo-rollouts)
- [Ingress and Service Resources](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#ingress-and-service-resources)
- [Rollout Analysis & Experiments](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#key-features-of-argo-rollouts)
- [Experiments](https://blog.mathod.fr/argo/argo_rollouts/coreComponents/coreComponents/#experiments)

### Lab Exercises

- [Lab 5.1. Installing Argo Rollouts](https://blog.mathod.fr/argo/argo_rollouts/labs/labs01/)
- [Lab 5.2. Argo Rollouts Blue-Green](https://blog.mathod.fr/argo/argo_rollouts/labs/labs02/)
- [Lab 5.3. Migrating an Existing Deployment to Argo Rollouts](https://blog.mathod.fr/argo/argo_rollouts/labs/labs03/)

---

## ARGO EVENTS

Introduction

- Chapter Overview and Objectives

The Main Components

- Event-Driven Architecture

Lab Exercises

- Lab 6.1. Setting Up Event Triggers with Argo
- Lab 6.2. Integrating Argo Events with External Systems

---

!!! info ""

    - https://argoproj.github.io/
    - https://github.com/akuity/awesome-argo
    - https://argo-workflows.readthedocs.io/en/latest/
    - https://argo-cd.readthedocs.io/en/stable/
    - https://argoproj.github.io/argo-rollouts/
    - https://argoproj.github.io/argo-events/
    - https://training.linuxfoundation.org/certification/certified-argo-project-associate-capa/