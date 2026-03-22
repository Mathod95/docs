---
title: Crossplane
status: draft
hide:
  - toc
---

<p align="center">
  <a href="https://github.com/crossplane/crossplane">
    <img src="https://opengraph.githubassets.com/Mathod/crossplane/crossplane" />
  </a>
</p>

> In this course, you'll learn how to use Crossplane, a powerful cloud-native framework for managing infrastructure using Kubernetes.

---

- [ ] [Qu’est-ce que Crossplane ?](What’s Crossplane?)
- [x] [Installation de crossplane](https://docs.crossplane.io/v2.2/get-started/install/)
- [x] [Resources Store]()
- [x] [CrossplaneDiff]()
- [x] [Crossview]()

---

Master Crossplane and turn Kubernetes into a powerful control plane for cloud infrastructure. Build reusable infrastructure APIs, automate provisioning, and manage cloud resources declaratively through hands-on, real-world labs.

This hands-on course introduces you to Crossplane, a powerful open-source CNCF project that extends Kubernetes to manage cloud infrastructure using Kubernetes-native APIs and tools.

You will learn how to define, compose, and provision infrastructure declaratively, treating infrastructure as code that can be versioned, reviewed, and managed alongside your applications.

## Through hands-on labs, you will

- Install Crossplane
- Configure providers for platform integration
- Create custom infrastructure APIs using Compositions
- Build dynamic resource provisioning pipelines using Composition Functions with patch-and-transform

## Course Highlights

**Getting Started with Crossplane**

This module takes you from understanding what Crossplane is to building production-ready infrastructure abstractions.

You will learn how Crossplane extends Kubernetes to become a universal control plane, enabling teams to provision and manage infrastructure using familiar Kubernetes workflows and tooling.

Through progressive labs, you will:

Install Crossplane
Work with providers to manage external resources
Create custom APIs using Compositions
Implement dynamic resource provisioning with Composition Functions

1. Introduction and Installation

    - Install Crossplane on a Kubernetes cluster using Helm
    - Verify the installation and explore Crossplane components and CRDs
    - Understand core concepts: control plane, providers, and managed resources
    - Install and explore the Crossplane CLI

2. Working with Providers

    - Install the Kubernetes Provider and verify its health
    - Create a ProviderConfig for credential management using InjectedIdentity
    - Create Managed Resources to provision Kubernetes namespaces and ConfigMaps
    - Understand the lifecycle of managed resources and how changes propagate

3. Composite Resources and Compositions

    - Create a CompositeResourceDefinition (XRD) for a custom resource type
    - Build a Composition using pipeline mode with Composition Functions
    - Provision infrastructure using Composite Resources
    - Explore resource relationships, owner references, and composition selection

4. Composition Functions: Patch and Transform

    - Install the patch-and-transform Composition Function
    - Configure patches using FromCompositeFieldPath to flow user inputs to managed resources
    - Apply string transforms to format resource names dynamically
    - Create Composite Resources with custom values and verify dynamic provisioning

---

- [ ] Providers
- [ ] Managed Resources
- [ ] Composition
- [ ] Functions

---
!!! abstract "Links and References"
    - https://github.com/crossplane/crossplane