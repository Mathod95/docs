---
title: Argo CD
status: draft
hide:
  - toc
---

<p align="center">
  <a href="https://github.com/argoproj/argo-cd">
    <img src="https://opengraph.githubassets.com/Mathod/argoproj/argo-cd" />
  </a>
</p>

---

> This course teaches GitOps fundamentals, ArgoCD implementation, and integration with third-party tools for effective CI/CD practices.

Welcome to the GitOps with ArgoCD course!

My name is Barahalikar Siddharth, and I serve as a technical architect specializing in API management tools and DevOps technologies. In this course, you will master the fundamentals of GitOps, discover its core principles, and learn how to implement GitOps practices in real-world scenarios.

We will begin by comparing DevOps with GitOps and examining major deployment models—including push-based and pull-based methods. Then, you'll explore ArgoCD basics: its applications, key concepts, common terminology, and underlying architecture. We also cover advanced topics such as various reconciliation methods and the app-of-apps pattern.

<Frame>
  ![The image shows a curriculum outline for a course on GitOps and ArgoCD, listing topics such as GitOps principles, ArgoCD architecture, and integration with Jenkins CI pipeline.](https://kodekloud.com/kk-media/image/upload/v1752877597/notes-assets/images/GitOps-with-ArgoCD-Course-Introduction/gitops-argocd-course-outline.jpg)
</Frame>

!!! note
    Throughout this course, you will integrate essential third-party tools like Okta, Bitnami Sealed Secrets, and HashiCorp Vault for enhanced user and secret management. Additionally, you'll configure monitoring, alerts, and notifications using industry-standard tools such as Prometheus, Grafana, Alertmanager, and Slack.

We conclude the course with an end-to-end CI/CD pipeline example, demonstrating how ArgoCD and GitOps principles work together seamlessly.

The course is structured into lesson modules, each designed to simplify complex concepts through engaging illustrations and hands-on exercises. In many modules, interactive labs allow you to practice what you learn directly in your browser.

!!! note
    If you encounter any issues or have questions during the course, please join our community channel for support. Active participation in the labs and community discussions will enhance your learning experience.

***

If you're ready to dive into the world of GitOps with ArgoCD, let's get started and revolutionize the way you think about continuous delivery and deployment!

---

Unlock the power of GitOps with ArgoCD, the leading GitOps tool for Kubernetes application deployment, through in-depth learning, hands-on exercises, and real-world practical applications in this course

About the course
GitOps is a framework where the entire code delivery process is controlled via Git and can fully manage infrastructure and application definition’s as code. 

It can be considered an extension of Infrastructure as Code (IaC). The fundamental concept is to use Git commits and pull requests to approve changes while managing resources on Kubernetes. GitOps is not limited to Kubernetes. In principle, GitOps can manage any infrastructure defined as code.

In this course, we will look into GitOps and ArgoCD. ArgoCD is a declarative GitOps tool designed for Kubernetes application deployment. 

ArgoCD is one of the world’s most popular open-source GitOps tools today, and it automates the deployment of the desired applications in the specified Kubernetes target environments.

This course is for aspiring learners looking to integrate ArgoCD and GitOps principles within their CICD pipelines. 

**What you will learn in this course:**

- GitOps Methodology
- DevOps vs GitOps Deployment Models.
- What/Why/How ArgoCD?
- ArgoCD Concepts, Features, Terminology.
- Detailed ArgoCD Architecture & Core Components.
- Reconciliation Loop Options.
- Custom Application Health Checks.
- Synchronization Strategies.
- Imperative vs declarative approach.
- User Management with RBAC.
- Secret management using HashiCorp Vault & Sealed Secrets.
- SSO with Okta.
- Metrics with Prometheus, Grafana & Alertmanager.
- Custom Slack Notification.

We will discuss each concept with a demo followed by practical hands-on exercises, provide simple scripts to set up your Kubernetes cluster, and have a GitHub repository with various code snippets throughout this course.

---

## Introduction
- [ ] Course Introduction
- [ ] Meeting with Task Dash DevOps Team
- [ ] What is GitOps
- [ ] GitOps Principles

## GitOps Introduction
- [ ] DevOps vs GitOps
- [ ] GitOps Feature Set
- [ ] GitOps Benefits Drawbacks
- [ ] GitOps Projects Tools

## ArgoCD Basics
- [ ] WhatWhyHow ArgoCD
- [ ] ConceptsTerminology
- [ ] Features
- [ ] Architecture
- [ ] Installation Options
- [ ] ArgoCD Installation
- [ ] ArgoCD App projects
- [ ] Create Application using UI
- [ ] Create Application using CLI
- [ ] Create ArgoCD Project

## ArgoCD Intermediate
- [ ] Reconciliation loop
- [ ] Git Webhook Configuration
- [ ] Application health
- [ ] Application Custom Health Check
- [ ] Types of Sync Strategies
- [ ] Application Synchronization Options
- [ ] Declarative Setup
- [ ] Declarative Setup Mono Application
- [ ] App of Apps
- [ ] Declarative Setup App of Apps
- [ ] Deploy apps using HELM Chart
- [ ] Deploy apps using HELM Chart
- [ ] Multi cluster application deployment
- [ ] Multi cluster application deployment

## ArgoCD Advanced/Admin
- [ ] User Management RBAC ArgoCD
- [ ] ArgoCD User Management RBAC
- [ ] Dex Okta Connector
- [ ] Dex Okta Connector
- [ ] Bitnami Sealed Secrets
- [ ] Bitnami Sealed Secrets
- [ ] Hashicorp Vault
- [ ] Hashicorp Vault 2
- [ ] ArgoCD Vault Plugin CLI
- [ ] ArgoCD Vault Plugin with ArgoCD
- [ ] ArgoCD Metrics Monitoring
- [ ] ArgoCD Metrics Monitoring 2
- [ ] Monitoring through Prometheus Grafana
- [ ] Raise Alert using AlertManager
- [ ] ArgoCD Notifications
- [ ] ArgoCD Notifications with Slack

## ArgoCD with Jenkins CI Pipeline
- [ ] CICD with GitOps
- [ ] Jenkinsfile Walkthrough
- [ ] CICD Pipeline Demo

---
!!! abstract "Links and References"
    - https://github.com/argoproj/argo-cd