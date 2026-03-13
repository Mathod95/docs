---
title: Kubectl Introduction
status: draft
sources:
  - https://notes.kodekloud.com/docs/Kubernetes-Troubleshooting-for-Application-Developers/Prerequisites/kubectl-refresher-Intro/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/kubernetes-troubleshooting-for-application-developers/module/09c2c8a6-ba29-4d55-bea1-cd8584be9107/lesson/16ea3475-744e-44ea-9285-b1e4dba694ec
---

> A comprehensive guide on kubectl commands for troubleshooting and diagnosing Kubernetes applications, highlighting commonly used options for quick issue resolution.

Welcome to our comprehensive guide on kubectl commands—a must-read refresher for anyone working with Kubernetes. In this article, we cover a series of powerful commands tailored for troubleshooting and diagnosing Kubernetes applications. While this is not an exhaustive catalog of all available kubectl commands, it highlights some of the most commonly used options for quickly solving common issues.

!!! note
    This guide is intended as a quick reference for troubleshooting with kubectl. For a complete list of commands and options, please refer to the [Kubernetes Documentation](https://kubernetes.io/docs/).

## Commands Overview

Each of these commands plays a key role in managing Kubernetes clusters effectively:

| Command                | Use Case Description                                               |
| ---------------------- | ------------------------------------------------------------------ |
| `kubectl get`          | Retrieves Kubernetes resources in a concise format                 |
| `kubectl describe`     | Provides detailed information on Kubernetes objects                |
| `kubectl logs`         | Fetches logs from pods to debug issues                             |
| `kubectl explain`      | Displays detailed documentation on Kubernetes resources and fields |
| `kubectl exec`         | Runs commands directly in a container                              |
| `kubectl port-forward` | Forwards one or more local ports to a pod                          |
| `kubectl top node`     | Displays resource (CPU/memory) usage statistics on nodes           |
| `kubectl diff`         | Compares configurations and resources between revisions            |
| `kubectl auth-can-i`   | Determines whether a user or service account can perform an action |

## Diving Deeper

Let's dive into each command to understand how they can help you troubleshoot and diagnose Kubernetes applications:

- **kubectl get:** Start by listing your resources to understand the current state of your cluster.
- **kubectl describe:** After identifying a resource, use this command for deeper insight into its configuration and status.
- **kubectl logs:** If a pod is experiencing issues, view its logs to help isolate the problem.
- **kubectl explain:** Use this command to learn about the fields and configuration options available for any resource.
- **kubectl exec:** Run commands inside a container for real-time debugging.
- **kubectl port-forward:** When direct network access is limited, forward local ports to your pod.
- **kubectl top node:** Monitor nodes to ensure they have adequate resources.
- **kubectl diff:** Compare current and desired states to understand configuration changes.
- **kubectl auth-can-i:** Check if your permissions allow a certain operation to avoid authorization issues.

<Callout icon="lightbulb" color="#1CB2FE">
  For more in-depth guidance on these commands, including examples and best practices, consider exploring the official [Kubernetes Basics](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/) guide.
</Callout>

With the commands outlined above, you're well-equipped to effectively troubleshoot and diagnose issues within your Kubernetes environment. Happy debugging!