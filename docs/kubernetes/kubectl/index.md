---
title: Kubectl
#status: draft
hide:
  - toc
---

<p align="center">
  <a href="https://github.com/kubernetes/kubectl">
    <img src="https://opengraph.githubassets.com/Mathod/kubernetes/kubectl" />
  </a>
</p>

---

> This course teaches application developers how to troubleshoot Kubernetes issues through real-world scenarios and hands-on labs.

## Introduction

Welcome to Kubernetes Troubleshooting for Application Developers! I'm Nourhan Khaled, your instructor for this course.

Learning Kubernetes from tutorials is one thing, but deploying a production application introduces a unique set of challenges that often feel like you're constantly putting out fires. This lesson bridges the gap between theory and practice—the very course I wish I had during those frustrating debugging sessions.

<Callout icon="lightbulb" color="#1CB2FE">
  Ensure you have a basic understanding of Kubernetes resources such as pods, deployments, services, storage, and network policies before you begin.
</Callout>

## Course Overview

We start with a concise refresher on essential kubectl commands for troubleshooting common Kubernetes errors. Then, the course dives into real-world scenarios that mirror the challenges you may face in production environments. You’ll learn how to inspect resources, identify failures, and apply fixes in a structured and repeatable way.

## Hands-On Troubleshooting

This course stands out because you'll troubleshoot and resolve issues in real time—exactly as I do in my day-to-day work. We’ll cover pod configuration errors, deployment rollouts, container image problems, and more, guiding you through each step with clear explanations and best practices.

## Real-World Scenarios

Throughout the lesson, you will explore a range of troubleshooting challenges including:

* Pod configuration errors
* Deployment and rollout issues
* Container settings and image pull problems
* Networking challenges such as service misconfigurations, network policies, and ingress troubleshooting
* Diagnosing RBAC and storage-related issues

<Callout icon="triangle-alert" color="#FF6B6B">
  Always test changes in a controlled environment before applying fixes to production. Insufficient testing can lead to unexpected disruptions.
</Callout>

## Hands-On Labs

Like all KodeKloud courses, this lesson features multiple hands-on labs. These browser-based labs enable you to immediately apply the troubleshooting techniques you learn, ensuring you gain practical, real-world experience.

If you're ready for a challenge, enroll now and start mastering Kubernetes troubleshooting!

- Crashing/pending pods
- Case of the missing pods
- Schrodinger's Deployment
- Container Errors
- EnableServiceLinks
- LeakyNetworkPolicies
- What the Ingress?
- Interns can see our secrets
- Multi-attach Volume Errors

---

Tackle real-world Kubernetes issues. Elevate your confidence and skills by diagnosing and resolving issues in crashing pods, unreachable services, and more.

Learning to Kubernetes is one thing, working with Kubernetes however, is an entirely different story. This course is intended to bridge the gap. The focus of this course is to show real-life scenarios that Kubernetes application developers run into in practice.  

In this fully hands-on scenario-based course, we will be troubleshooting a variety of issues relating to Kubernetes application development, from crashing pods to unreachable services. By the end of the course, you will be familiar with the commonly encountered issues while working with Kubernetes as well as how to navigate your way around new ones.

What You'll Learn:

-  Kubectl Essentials: Revisit fundamental `kubectl` commands with a special focus on commands used for troubleshooting.
-  Common Errors: Understand, diagnose, and resolve frequent issues such as image pull errors, create container errors, pod crashloopbackoffs and much more.
-  Practical Tips & Tricks: Learn hands-on tips and tricks that you might not have learned in theory but will definitely need in practice.
-  Common Kubernetes Pitfalls: Learn how to navigate your way around well-known configuration pitfalls in Kubernetes including deployment configurations, RBAC, and network policies.
-  New Tools: Add a couple of new Kubernetes tools to your toolset.

This highly practical condensed course is based on scenarios that mimic many of the real-world scenarios that you will encounter when you work with Kubernetes. Complemented by the hands-on labs, this course will ensure you're well-equipped to handle a wide range of Kubernetes troubleshooting scenarios efficiently.

Target Audience:

-  Kubernetes application developers and beginners seeking to augment their theoretical knowledge of Kubernetes with practical experience.
-  DevOps Engineers seeking Kubernetes troubleshooting skills.
-  Site Reliability Engineers (SREs)
-  Cloud Engineers managing Kubernetes clusters
-  Technical Support Engineers focusing on Kubernetes environments
-  Technical Leads overseeing cloud-native applications

---

# Prerequisites
- [ ] kubectl refresher Intro
- [ ] kubectl get
- [ ] kubectl describe
- [ ] kubectl get events
- [ ] kubectl logs
- [ ] kubectl logs label
- [ ] kubectl logs timestamps
- [ ] kubectl logs follow
- [ ] kubectl exec
- [ ] kubectl port forward
- [ ] kubectl auth can i
- [ ] kubectl top
- [ ] kubectl explain
- [ ] kubectl diff
- [ ] Kubernetes EphemeralDebug Containers
- [ ] k9s Walkthrough

# Troubleshooting Scenarios
- [ ] Case of the Missing Pods
- [ ] Config Out of Date
- [ ] Crashing Pods
- [ ] Create Container Errors
- [ ] Endlessly Terminating Pods
- [ ] Field Immutability
- [ ] Image Pull Errors
- [ ] Interns can see our secrets
- [ ] Multi Attach Volume Errors
- [ ] Pending Pods
- [ ] Port Mania
- [ ] Reloader
- [ ] Schrodingers Deployment
- [ ] Unreachable Pods Leaky Network Policies
- [ ] What the Ingress
- [ ] enableServiceLinks


---
!!! abstract "Links and References"
    - https://github.com/kubernetes/kubectl