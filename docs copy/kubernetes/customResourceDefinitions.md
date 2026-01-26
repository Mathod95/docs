---
title: Custom Resource Definitions
date: 2026-01-23
status: draft
categories: Kubernetes
tags:
  - Kubernetes
  - Custom Resource Definitions
source: https://thekubeguy.com/everything-you-need-to-know-about-custom-resource-definitions-in-kubernetes-4c17502e76c4
---

With great infrastructure we need a great level of customisation, this is where Kubernetes Custom Resource Definitions (CRDs) come into play, offering a powerful way to extend Kubernetes capabilities beyond its default set of resources. In this article, we’ll learn about CRDs, breaking down everything you need to know into simple, plain English.

Everything You Need to Know About Custom Resource Definitions in Kubernetes

### What is a Kubernetes CRD?

At its core, a CRD is a way to create your own, custom resources in Kubernetes. Imagine you’re using LEGO bricks to build models. Each LEGO set comes with standard bricks, but what if you need a special piece that’s not included? CRDs are like creating that special LEGO piece, allowing you to define new resources that work seamlessly within the Kubernetes ecosystem.

A Custom Resource Definition enables you to define a new kind of resource, such as `VPCs`, `Firewalls`, or even `TodoLists`, that Kubernetes doesn't offer out of the box. This new resource can then be used to manage your application's specific needs, making Kubernetes even more flexible and powerful.

### Why Use CRDs?

CRDs allow for the extension of Kubernetes capabilities in ways that were previously not possible with the default set of resources. They offer several benefits:

- **Customization:** Tailor Kubernetes to your specific application needs.
- **Automation**: Automate the management of complex services.
- **Integration:** Seamlessly integrate external services into your Kubernetes cluster.

### How Do CRDs Work?

CRDs work by defining a new resource type in your Kubernetes cluster. This process involves creating a YAML file that specifies the new resource’s attributes and behavior. Once applied to your cluster, the Kubernetes API server recognizes this new resource type and allows you to create, update, delete, and manage instances of it, just like any standard Kubernetes resource.

### The CRD Lifecycle

1. **Define:** You start by defining your CRD, specifying its name, version, scope, and the structure of its spec (the desired state of your resource).
2. **Deploy:** Apply the CRD to your Kubernetes cluster using `kubectl apply`. This tells the Kubernetes API server about the new resource.
3. **Create Custom Resources:** With the CRD in place, you can now create custom resources based on it. These custom resources are instances of your CRD, representing the actual objects you want to manage in your cluster.
4. **Manage:** Use `kubectl` to manage your custom resources just like you would with built-in resources. You can create, read, update, and delete custom resources, integrating them into your applications and workflows.

### Creating a Simple CRD: An Example

Let’s create a simple CRD for a `TodoList`. This example will help illustrate the process of defining and using a custom resource in Kubernetes.

**Define the CRD:** First, we need to define what a `TodoList` looks like in YAML format. This definition includes metadata like the name and group of our CRD, and the schema that describes the structure of each `TodoList` resource.

```c
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: todolists.mydomain.com
spec:
  group: mydomain.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: string
  scope: Namespaced
  names:
    plural: todolists
    singular: todolist
    kind: TodoList
    shortNames:
      - tl
```

**Deploy the CRD:** Apply this definition to your cluster using `kubectl apply -f todolist-crd.yaml`. This step registers the `TodoList` custom resource within your Kubernetes cluster.

**Create a** `**TodoList**` **Instance:** Now that the CRD is in place, you can create instances of `TodoList`. Here's an example of a `TodoList` resource:

```c
apiVersion: mydomain.com/v1
kind: TodoList
metadata:
  name: my-first-todolist
spec:
  items:
    - Learn Kubernetes CRDs
    - Write a blog post
```

Apply this using `kubectl apply -f my-todolist.yaml` to create your `TodoList` in Kubernetes.

Manage Your `TodoList`: You can use `kubectl` commands to manage your `TodoList` instances, such as viewing, editing, and deleting them.

### Best Practices for Using CRDs

When working with CRDs, it’s essential to follow best practices to ensure your Kubernetes cluster remains efficient, secure, and easy to manage:

- **Validation:** Use OpenAPI validation schemas to enforce the structure and validity of your custom resources.
- **Versioning:** Properly version your CRDs to manage changes and upgrades smoothly.
- **Namespaces:** Consider whether your custom resources should be namespaced or cluster-wide and define them accordingly.
- **Documentation:** Document your CRDs and custom resources thoroughly for users and future maintainers.

Whether you’re automating complex workflows or integrating external services, CRDs offer the flexibility and power to make it happen. Remember, the key to success with CRDs lies in thoughtful definition, careful management, and adherence to best practices. Stay tuned and don’t forget to follow