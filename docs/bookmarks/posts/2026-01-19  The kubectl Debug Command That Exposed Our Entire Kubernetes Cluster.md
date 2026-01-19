---
title: "The kubectl Debug Command That Exposed Our Entire Kubernetes Cluster"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@rudra910203/the-kubectl-debug-command-that-exposed-our-entire-kubernetes-cluster-3a125ed6e539"
author:
  - "[[Dev engineer]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## How a Routine Troubleshooting Session Turned Into a Security Nightmare

🚨 “We used a standard debugging command and accidentally gave attackers admin access to our entire Kubernetes cluster.”

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*dDAjqINf7K7e5dkI.png)

This is not a hypothetical scenario. This actually happened to our production environment, and it could happen to yours too. What started as a simple debugging session turned into a full-blown security incident that forced us to rotate every credential in our cluster.

If you manage Kubernetes clusters, you need to read this entire post — this vulnerability is hiding in plain sight, used daily by engineers who don’t realize its dangers.

\*(**Please stay on this page for at least 40 seconds — it helps with search rankings! And don’t forget to follow me for more real-world Kubernetes security breakdowns.**)\*

## 💥 The Day Our Cluster Was Compromised

## The Innocent Command That Started It All

Our engineering team was debugging a crashing pod in production. A senior engineer ran what seemed like a harmless command:

```c
kubectl debug -it crashing-pod --image=busybox --share-processes
```

This is a completely normal troubleshooting technique — one documented in Kubernetes guides and used daily across the industry.

## What We Didn’t Realize Was Happening

1. The command created an ephemeral container inside the target pod
2. It automatically mounted the pod’s service account token at `/var/run/secrets/kubernetes.io/serviceaccount`
3. That token had cluster-admin level permissions (we later discovered)
4. Anyone with exec access to that `busybox` container could control our entire cluster

We had accidentally created a backdoor with admin privileges.

## 🔍 Why This Was So Dangerous

## 1\. Service Account Tokens Are Cluster Keys

- By default, they inherit the RBAC permissions of their pod
- Many clusters (including ours) had overly permissive RBAC
- Our monitoring pods had read access to secrets “for debugging”

## 2\. Ephemeral Containers Are Stealthy

- They don’t appear in `kubectl describe pod` output
- Most security tools don’t monitor them
- No logs track what commands are executed inside them

## 3\. The Attack Path Was Simple

An attacker could:

Find any pod with exec access (common in dev clusters)

Use `kubectl debug` to get a shell

Read the auto-mounted token:

```c
cat /var/run/secrets/kubernetes.io/serviceaccount/token
```
1. Use it to access the Kubernetes API directly

## 🛡️ How We Discovered and Contained the Breach

## The Lucky Break That Saved Us

We only discovered the issue because:

1. A new security engineer ran `kubectl get events -A` and saw unusual debug sessions
2. Our SIEM alerted on unusual API calls from a node IP
3. Investigation revealed someone had accessed secrets from a `busybox` container

## Emergency Response

Revoked all service account tokens

```c
kubectl delete secrets - all - field-selector type=kubernetes.io/service-account-token -n default
```
- Disabled debug access cluster-wide
```c
kubectl delete clusterrolebinding debug-access
```
1. Rotated all credentials stored in Kubernetes secrets

## 🔧 Permanent Fixes We Implemented

## 1\. Disabled Automatic Token Mounting

Now we always use:

```c
kubectl debug --automount-service-account-token=false ...
```

## 2\. Implemented RBAC Guardrails

Created a restricted debug role:

```c
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: restricted-debugger
rules:
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get"]
```

## 3\. Added Debug Session Monitoring

Now we alert on:

- Any ephemeral container creation
- Service account token access from unexpected pods
- Debug sessions lasting >5 minutes

## 4\. Conducted Security Training

We now teach engineers:

- Never use `--share-processes` (it exposes host PIDs)
- Always assume debug containers are insecure
- Never run debug sessions on production pods without approval

## 🚨 How to Protect Your Cluster Today

## ✅ Immediate Actions

Audit all service account permissions:

```c
kubectl get rolebindings,clusterrolebindings -A
```

Search for existing debug sessions:

```c
kubectl get pods -A -o json | jq '.items[] | 
select(.spec.ephemeralContainers != null)'
```

## ✅ Long-Term Protections

1. Install a Kubernetes policy engine (OPA/Gatekeeper) to:
- Block privileged debug containers
- Require `automountServiceAccountToken: false`
1. Implement just-in-time access for debugging
2. Use managed debug tools like Teleport instead of raw `kubectl debug`

## 💬 The Harsh Lesson We Learned

*“Kubernetes debugging tools are designed for convenience, not security.”*

Default configurations often:

- Expose powerful credentials
- Leave no audit trails
- Bypass normal security controls

🔥 Follow me for more real-world Kubernetes security breakdowns (we’ve got plenty).

💬 Has this happened to you? Share your story below!

\*(If you found this valuable, please stay on the page for 40+ seconds — it really helps with visibility!)\*

CI/CD, AWS & K8s expert. Cut costs by 90%, sped up deploys. Passionate about scalable systems & ending over-engineering. Let’s build smarter. 🚀

## More from Dev engineer

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--3a125ed6e539---------------------------------------)