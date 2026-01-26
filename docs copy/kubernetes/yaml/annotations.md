---
title: Annotations
date: 2026-01-22
categories: Kubernetes
tags:
  - Kubernetes
status:
sources:
  - Annotations: https://thekubeguy.com/kubernetes-annotations-the-hidden-feature-that-boosts-your-devops-game-e6c1688b1bcf
---

Welcome to Kubernetes adventure series, In this blog I came up with a feature that often flies under the radar, yet holds substantial power in customizing and managing Kubernetes resources, is annotations. This blog post is designed to unravel the complexities of Kubernetes annotations, with a comprehensive understanding of their purpose, use cases, and best practices.

### Understanding Kubernetes Annotations

Imagine you have a bunch of containers and services running in Kubernetes. You want to keep track of extra details about them, like notes or reminders, that don’t fit into their basic descriptions. That’s where annotations come in. They’re like labels but more detailed. You can use them to add all sorts of information to your Kubernetes objects that don’t directly affect how things run.

## The Anatomy of Annotations

Annotations, like labels, are key-value pairs attached to Kubernetes objects. They are defined in the metadata section of object definitions, allowing you to store additional information that can be leveraged by tools and libraries working with these objects. Here is a simple example of an annotation within a Pod manifest:

```c
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
  annotations:
    example.com/log-level: "debug"
    example.com/update-policy: "auto"
spec:
  containers:
  - name: example-container
    image: nginx
```

In this example, two annotations are defined: `example.com/log-level` and `example.com/update-policy`. These annotations can be used to convey configuration information to utilities that process Pods but are not directly involved in their creation or management.

## Why Use Annotations?

Annotations provide a mechanism for storing additional information about Kubernetes objects, enabling a variety of use cases:

- **Storing build/release information:** Annotations can hold information such as build/release IDs, PR numbers, git branch, docker image hashes, etc., that can be useful for debugging and tracing.
- **Configuration and management:** Tools and controllers can use annotations to manage and configure objects in a more flexible way than labels.
- **Signaling between tools:** Annotations can act as a signal between different tools controlling the same object, conveying information like whether an object should be auto-scaled, whether a service requires an external load balancer, etc.

### Use Cases and Examples

Let’s explore some practical use cases where annotations can be particularly useful:

### 1\. Tracking Deployment Information

Annotations are ideal for tracking information like deployment version, repository URL, or commit hashes. This can be invaluable for debugging purposes and understanding the provenance of deployed resources.

### 2\. Signaling to Ingress Controllers

Ingress controllers can use annotations to customize behavior. For example, you might use an annotation to specify a custom rate limit or to enable client certificate authentication for a specific Ingress resource.

### 3\. Configuring Pod Behavior

Annotations can influence the behavior of Pods or their containers. For instance, you could use annotations to specify a sidecar container should be injected into a Pod, with the annotation holding configuration data for the sidecar.

### Best Practices for Using Annotations

While annotations offer great flexibility, it’s important to use them judiciously. Here are some best practices to keep in mind:

- **Use domain-prefixed names:** To avoid conflicts, use domain-prefixed names (e.g., `example.com/my-annotation`) for your annotations.
- **Keep them small:** Annotations are not designed to hold large amounts of data. If you find yourself needing to store large blobs of information, consider using a ConfigMap or another storage mechanism.
- **Document your annotations:** Since annotations can be used freely, it’s crucial to document the annotations you use, their purposes, and their expected values. This is especially important for annotations used by tools and applications across your team or organization.
- **Use them for non-identifying information:** Remember, annotations are not meant to be used for identifying and selecting Kubernetes objects. Use labels for that purpose.

In conclusion, while Kubernetes labels might get the spotlight for their role in organizing and selecting resources, annotations work quietly in the background, offering a flexible mechanism for storing metadata, conveying configuration, and enabling integrations. By understanding and leveraging annotations wisely, you can unlock new possibilities for managing your Kubernetes resources more effectively and efficiently.

I'll help you sail through the ocean of Kubernetes with minimal efforts