---
title: KUSTOMIZE
#status: draft
hide:
  - toc
sourcesofthispage:
  - https://notes.kodekloud.com/docs/Kustomize/Introduction/Course-Introduction/page
sources:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Kustomize-Basics/Components/page
  - https://notes.kodekloud.com/docs/Kustomize/Introduction/Course-Introduction/page
---

<p align="center">
  <a href="https://github.com/kubernetes-sigs/kustomize">
    <img src="https://opengraph.githubassets.com/Mathod/kubernetes-sigs/kustomize" />
  </a>
</p>

---

> This course teaches deploying and customizing Kubernetes resources using Kustomize, covering core features, CI/CD integration, and a capstone project.

Welcome to the **Kustomize** course! I’m **Sanjeev Thiyagarajan**, and I’ll guide you through deploying and customizing Kubernetes resources across multiple environments. By the end of this course, you’ll master Kustomize’s core features, integrate it into CI/CD pipelines, and complete a capstone project.

## What You’ll Learn

| Module                        | Description                                                                                  |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| Why Kustomize Was Created     | Understand the challenges in Kubernetes manifests and how Kustomize simplifies customization |
| Installing Kustomize          | Install Kustomize locally and configure prerequisites                                        |
| Defining `kustomization.yaml` | Learn the syntax, reference resources, and organize overlays                                 |
| Basic Resource Example        | Create a simple Deployment and Service with Kustomize                                        |
| Advanced Features             | Explore transformers, patches, components, generators (ConfigMaps & Secrets)                 |
| CLI Subcommands               | Use `kustomize edit`, `kustomize set`, and other subcommands in CI/CD                        |
| Hands-On Labs                 | Practice after each lecture with interactive challenges                                      |
| Final Project                 | Apply all features in a capstone deployment                                                  |
| Community Support             | Join our [Slack channel](https://example.com/slack) for Q\&A and peer assistance             |

!!! note
    Kustomize is now built into `kubectl` (v1.14+). You can run `kubectl kustomize` instead of installing a separate binary.

## What’s Next?

Now that you know the course structure, we’ll dive into Kustomize’s core features:

1. **Transformers & Patches** – Modify fields without touching original YAML.
2. **Overlays & Components** – Compose reusable customization layers.
3. **Generators** – Automate ConfigMap and Secret creation.
4. **CLI Workflow** – Leverage `kustomize build`, `edit`, `set`, and `apply`.

Ready to customize your first Kubernetes manifest? Let’s jump in!

---

!!! note "CKA"
    - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Kustomize-Basics/Components/page

    ### 2025 Updates Kustomize Basics
    - [ ] Common Transformers
    - [ ] Components
    - [ ] Different Types of Patches
    - [ ] Image Transformers
    - [ ] Page
    - [ ] Kustomize ApiVersion Kind
    - [ ] Kustomize Output
    - [ ] Kustomize Problem Statement idealogy
    - [ ] Kustomize vs Helm
    - [ ] Managing Directories
    - [ ] Managing Directories Demo
    - [ ] Overlays
    - [ ] Patches Dictionary
    - [ ] Patches Intro
    - [ ] Patches list
    - [ ] Transformers Demo
    - [ ] kustomization

!!! note "Kustomize"
    - https://notes.kodekloud.com/docs/Kustomize/Introduction/Course-Introduction/page

    ### Kustomize Overview
    - [ ] Kustomize Problem Statement Idealogy
    - [ ] Kustomize vs Helm
    ### Kustomize Basics
    - [ ] InstallationSetup
    - [ ] kustomization
    - [ ] Kustomize Output
    - [ ] Kustomize ApiVersion Kind
    - [ ] Managing Directories
    - [ ] Managing Directories Demo
    - [ ] Common Transformers
    - [ ] Image Transformers
    - [ ] Transformers Demo
    - [ ] Patches Intro
    - [ ] Different Types of Patches
    - [ ] Patches Dictionary
    - [ ] Patches list
    - [ ] Overlays
    - [ ] Components
    ### Secret Config Generator
    - [ ] Garbage Collection
    - [ ] SecretConfig Generator
    - [ ] Why Generators
    ### Other Commands
    - [ ] Edit CICD Use Case
    - [ ] Imperative Commands

---
!!! abstract "Links and References"
    - [Kustomize GitHub Repository](https://github.com/kubernetes-sigs/kustomize)
    - [Kubernetes Basics](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)
    - [Kubectl Plugin: kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)