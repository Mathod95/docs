---
title: "🧠 Master Kubernetes in Minutes: This Kubernetes Cheatsheet Has Everything You Need"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.stackademic.com/master-kubernetes-in-minutes-this-kubernetes-cheatsheet-has-everything-you-need-c9af6967476a"
author:
  - "[[Ashish Singh]]"
---
<!-- more -->

[Sitemap](https://blog.stackademic.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@ashishnoob)## [Stackademic](https://blog.stackademic.com/?source=post_page---publication_nav-d1baaa8417a4-c9af6967476a---------------------------------------)

[![Stackademic](https://miro.medium.com/v2/resize:fill:76:76/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_sidebar-d1baaa8417a4-c9af6967476a---------------------------------------)

Stackademic is a learning hub for programmers, devs, coders, and engineers. Our goal is to democratize free coding education for the world.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*D97YgmKv8OOc0D-kSFLgAg.png)

Tired of searching for the same `kubectl` commands over and over? This practical Kubernetes cheatsheet covers deployments, services, YAML, logs, secrets, Ingress, and more. Ideal for DevOps engineers who want quick, reliable CLI commands and productivity hacks. Bookmark this for daily use.

## 1\. Common kubectl Options

**Basic Flags**

- `**-o yaml**` **/** `**-o json**`**:** Output resource in human-readable formats. Example: `**kubectl get pod nginx -o yaml**`
- `**-n <namespace>**`**:** Work within a specific namespace. Example: `**kubectl get pods -n kube-system**`
- `**-l <label>**`**:** Filter by label selector. Example: `**kubectl get pods -l app=nginx**`
- `**--watch**`**:** Live update stream of changes. Example: `**kubectl get pods --watch**`
- `**--all-namespaces**` or `**-A**`**:** View resources across all namespaces.

**Useful Aliases**

```c
alias k=kubectl
alias kgp="kubectl get pods"
alias kaf="kubectl apply -f"
alias kctx="kubectl config use-context"
alias kga="kubectl get all"
```

Add these to your `.bashrc`, `.zshrc`, or shell profile for efficiency.

## 2\. Working with YAML Manifests

YAML manifests define resources in a declarative way. They’re reusable and version-controllable.

**Generate a YAML Manifest**

```c
kubectl create deploy nginx --image=nginx --dry-run=client -o yaml > nginx-deploy.yaml
```

**Apply vs Create**

- `**kubectl apply -f file.yaml**`**:** Safely creates or updates existing resources.
- `**kubectl create -f file.yaml**`**:** Creates only; fails if resource already exists.

**Apply or Edit Configuration**

```c
kubectl apply -f deployment.yaml
kubectl edit deploy nginx
```

**Validate Before Applying**

```c
kubectl apply --dry-run=client -f service.yaml
```

## 3\. Cluster Management & Context Switching

Manage multiple clusters easily using `**kubectl config**` commands.

- `**kubectl config get-contexts**`**:** List available clusters/contexts.
- `**kubectl config use-context <context-name>**`**:** Switch to a different cluster.
- `**kubectl cluster-info**`**:** Show current cluster info.
- `**kubectl top nodes**` **/** `**kubectl top pods**`**:** View CPU and memory usage (requires metrics-server).
```c
kubectl config use-context gke_myproject_us-central1_cluster-1
```

## 4\. Managing Workloads

**Deployments**

```c
kubectl create deploy nginx --image=nginx:1.25
kubectl scale deploy nginx --replicas=3
kubectl rollout status deploy nginx
kubectl rollout undo deploy nginx
```

**Pods**

```c
kubectl run debug --image=busybox --rm -it -- sh
kubectl get pods -o wide
kubectl describe pod <pod-name>
```

**DaemonSets**

```c
kubectl get daemonsets -A
kubectl logs -l app=node-exporter
```

## 5\. Networking: Services, Ingress, DNS

**Expose a Service**

```c
kubectl expose deploy nginx --port=80 --target-port=80 --type=LoadBalancer
```

**Port Forwarding**

```c
kubectl port-forward svc/nginx 8080:80
```

**DNS Resolution**

```c
kubectl run dns-test --image=busybox --rm -it -- nslookup nginx
```

**Sample Ingress**

```c
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

## 6\. Storage & Configuration

**Secrets**

```c
kubectl create secret generic db-creds --from-literal=user=admin --from-literal=password=secret123
kubectl get secrets db-creds -o yaml
kubectl get secret db-creds -o jsonpath='{.data.user}' | base64 --decode
```

**Persistent Volumes**

```c
kubectl get pv
kubectl get pvc
kubectl describe pvc <pvc-name>
```

**ConfigMaps**

```c
kubectl create configmap app-settings --from-literal=MODE=debug
kubectl describe configmap app-settings
```

## 7\. Logs, Debugging & Troubleshooting

**Logs**

```c
kubectl logs nginx-xyz --tail=100 --follow
```

**Events**

```c
kubectl get events --sort-by=.lastTimestamp
```

**Exec into a Pod**

```c
kubectl exec -it nginx-xyz -- /bin/bash
```

**Ephemeral Containers (v1.25+)**

```c
kubectl debug -it nginx --image=busybox
```

## 8\. Pro Tips, Aliases & Best Practices

- Use `kubectl explain` to understand resource schemas:
```c
kubectl explain deployment.spec.template.spec
```
- Wait for a resource to be ready:
```c
kubectl wait --for=condition=ready pod nginx-xyz --timeout=60s
```
- Use custom output columns:
```c
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase
```
- View everything in the cluster:
```c
kubectl get all -A
```
- Use Kustomize for environment overlays:
```c
kubectl apply -k overlays/dev
```
- Perform static analysis on YAMLs:
- Use tools like `**kube-score**`, `**kubescape**`, or `**trivy**` for security.

## Final Thoughts

This cheatsheet is your daily companion for mastering Kubernetes with `kubectl`. Whether you're deploying microservices or debugging a cluster, these commands and examples will make your life easier.

> 💡 Like & Share if you found this useful!  
> 🔔 Follow to stay updated.  
> 🌟 Enjoyed this article? Give it 50 claps!

## Thank you for being a part of the community

*Before you go:*

- Be sure to **clap** and **follow** the writer ️👏 **️️**
- Follow us: [**X**](https://x.com/inPlainEngHQ) | [**LinkedIn**](https://www.linkedin.com/company/inplainenglish/) | [**YouTube**](https://www.youtube.com/@InPlainEnglish) | [**Newsletter**](https://newsletter.plainenglish.io/) | [**Podcast**](https://open.spotify.com/show/7qxylRWKhvZwMz2WuEoua0) | [**Twitch**](https://twitch.tv/inplainenglish)
- [**Start your own free AI-powered blog on Differ**](https://differ.blog/) 🚀
- [**Join our content creators community on Discord**](https://discord.gg/in-plain-english-709094664682340443) 🧑🏻💻
- For more content, visit [**plainenglish.io**](https://plainenglish.io/) + [**stackademic.com**](https://stackademic.com/)

[![Stackademic](https://miro.medium.com/v2/resize:fill:96:96/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_info--c9af6967476a---------------------------------------)

[![Stackademic](https://miro.medium.com/v2/resize:fill:128:128/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_info--c9af6967476a---------------------------------------)

[Last published 11 hours ago](https://blog.stackademic.com/5-oop-traps-that-fail-senior-java-developers-in-interviews-7f61d022bfb5?source=post_page---post_publication_info--c9af6967476a---------------------------------------)

Stackademic is a learning hub for programmers, devs, coders, and engineers. Our goal is to democratize free coding education for the world.