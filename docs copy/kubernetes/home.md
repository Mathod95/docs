---
title: Home
categories: Kubernetes
tags:
  - Kubernetes
---

![Kubernetes](../assets/images/kubernetes/brand/kubernetes-horizontal-all-blue-color.svg)

- [x] [Container Runtime](containerRuntime.md)
- [x] [Container Runtime Interface](containerRuntimeInterface.md)

Introduction:

  - Course Introduction
  - Certification

Core Concepts:

- Core Concepts Section Introduction
- Cluster Architecture
- Docker vs ContainerD
- A note on Docker Deprecation
- ETCD for Beginners
- [x] [ETCD in Kubernetes](etcd.md)
- Kube API Server
- Kube Controller Manager
- [x] [Kube Scheduler](kube-scheduler.md)
- [x] [Kubelet](kubelet.md)
- [x] Kube Proxy
- [x] Pods
- Pods with YAML
- Demo Pods with YAML
- Practice Test Introduction
- Solution Pods optional
- ReplicaSets
- Solution ReplicaSets optional
- [x] Deployments
- Solution Deploymentoptional
- [x] Services
- [x] Services Cluster IP
- Services Loadbalancer
- Solution Services optional
- Namespaces
- Solution Namespaces optional
- Imperative vs Declarative
- Solution Imperative Commands optional
- Kubectl Apply Command
- A Quick Reminder

Scheduling:

- Scheduling Section Introduction
- Manual Scheduling
- Solution Manual Scheduling optional
- Labels and Selectors
- Solution Labels and Selectors
- Taints and Tolerations
- Solution Taints and Toleration Optional
- Node Selectors
- Node Affinity
- Solution Node Affinity Optional
- Taints and Tolerations vs Node Affinity
- [x] Resource Limits
- Solution Resource Limits
- DaemonSets
- Solution DaemonSets optional
- Static Pods
- Solution Static Pods Optional
- Priority Classes
- Multiple Schedulers
- Solution Multiple Scheduler
- Configuring Scheduler Profiles
- Admission Controllers 2025 Updates
- Solution Admission Controllers 2025 Updates
- Validating and Mutating Admission Controllers 2025 Updates
- Solution Validating and Mutating Admission Controllers 2025 Updates

Logging Monitoring:

- Logging and Monitoring Section Introduction
- Monitor Cluster Components
- Solution Monitor Cluster Components
- Managing Application Logs
- Solution Logging Optional

Application Lifecycle Management:

- Application Lifecycle Management Section Introduction
- Rolling Updates and Rollbacks
- Solution Rolling update
- Commands and Arguments in Docker
- Commands and Arguments in Kubernetes
- Solution Commands and Arguments Optional
- Configure Environment Variables in Applications
- Configure ConfigMaps in Applications
- Solution Env Variables Optional
- Secrets
- Solution Secrets Optional
- Demo Encrypting Secret Data at Rest
- Multi Container Pods
- Solution Multi Container Pods Optional
- Solution Init Containers Optional
- Introduction to Autoscaling 2025 Updates
- Horizontal Pod Autoscaler HPA 2025 Updates
- In place Resize of Pods 2025 Updates
- Vertical Pod Autoscaling VPA 2025 Updates

Cluster Maintenance:

- Cluster Maintenance Section Introduction
- OS Upgrades
- Solution OS Upgrades optional
- Kubernetes Software Versions
- Cluster Upgrade Introduction
- Demo Cluster upgrade
- Solution Cluster Upgrade Process
- Backup and Restore Methods

Security:

- Security Section Introduction
- Kubernetes Security Primitives
- Authentication
- TLS Introduction
- TLS Basics
- TLS in Kubernetes
- TLS in Kubernetes Certificate Creation
- View Certificate Details
- Solution View Certification Details
- Certificates API
- Solution Certificates API
- KubeConfig
- Solution KubeConfig
- API Groups
- Authorization
- Role Based Access Controls
- Solution Role Based Access Controls
- Cluster Roles
- Solution Cluster Roles
- Service Accounts
- Solution Service Accounts
- Image Security
- Solution Image Security
- Pre requisite Security in Docker
- Security Contexts
- Solution Security Contexts
- Network Policies
- Developing network policies
- Solution Network Policies optional
- [x] [Custom Resource Definition CRD](customResourceDefinitions.md)
- Custom Controllers 2025 Updates
- Operator Framework 2025 Updates

Storage:

- Storage Section Introduction
- Introduction to Docker Storage
- Storage in Docker
- Volume Driver Plugins in Docker
- Container Storage Interface
- Volumes
- Persistent Volumes
- Persistent Volume Claims
- Solution Persistent Volumes and Persistent Volume Claims optional
- Storage Class
- Solution Storage Class

Networking:

- Networking Introduction
- Prerequisite Switching Routing Gateways CNI in kubernetes
- Prerequisite DNS
- Prerequisite Network Namespaces
- Prerequisite Docker Networking
- Prerequisite CNI
- Cluster Networking
- Solution Explore Environment optional
- Pod Networking
- CNI in kubernetes
- CNI weave
- Solution Explore CNI optional
- ipam weave
- Service Networking
- Solution Service Networking optional
- DNS in kubernetes
- CoreDNS in Kubernetes
- Solution Explore DNS optional
- Ingress
- Solution Ingress Networking 1 optional
- Solution Ingress Networking 2 optional
- Introduction to Gateway API 2025 Updates

Design and Install a Kubernetes Cluster:

- Design a Kubernetes Cluster
- Choosing Kubernetes Infrastructure
- Configure High Availability
- ETCD in HA

Install Kubernetes the kubeadm way:

- Introduction to Deployment with kubeadm
- Deploy with Kubeadm Provision VMs with Vagrant
- Demo Deployment with Kubeadm
- Solution Install a Kubernetes Cluster using kubeadm

Troubleshooting:

- Troubleshooting Section Introduction
- Application Failure
- Solution Application Failure
- Control Plane Failure
- Solution Control Plane Failure
- Worker Node Failure
- Solutions Worker Node Failure

Other Topics:

- Advanced Kubectl Commands

Mock Exams:

- Mock Exam 1 Step by Step Solutions
- Mock Exam 2 Step by Step Solutions
- Mock Exam 3 Step by Step Solutions
- Whats Next

Helm Basics 2025 Updates:

- What is Helm
- Installation and configuration
- A quick note about Helm2 vs Helm3
- Helm Components
- Helm charts
- Working with Helm basics
- Customizing chart parameters
- Lifecycle management with Helm

Kustomize Basics 2025 Updates:

- Kustomize Problem Statement idealogy
- Kustomize vs Helm
- InstallationSetup
- kustomization
- Kustomize Output
- Kustomize ApiVersion Kind
- Managing Directories
- Managing Directories Demo
- Common Transformers
- Image Transformers
- Transformers Demo
- Patches Intro
- Different Types of Patches
- Patches Dictionary
- Patches list
- Overlays
- Components