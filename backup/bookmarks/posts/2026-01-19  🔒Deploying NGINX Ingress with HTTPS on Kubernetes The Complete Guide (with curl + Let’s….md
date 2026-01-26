---
title: "🔒Deploying NGINX Ingress with HTTPS on Kubernetes: The Complete Guide (with curl + Let’s…"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@mahernaija/deploying-nginx-ingress-with-https-on-kubernetes-the-complete-guide-with-curl-lets-64f15a076581"
author:
  - "[[Mahernaija]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

*From Ingress setup to testing your backend online using TLS — explained step by step with Helm, kubectl & cert-manager!*

## 🚀 Introduction

Kubernetes Ingress is the **gateway** to your services, enabling controlled access from the outside world 🌍. When combined with **NGINX Ingress Controller** and **Let’s Encrypt TLS certificates**, it becomes a **secure, production-ready solution**. This guide walks you through:

✅ Installing the Ingress controller  
✅ Setting up a sample NGINX backend  
✅ Exposing it to the internet  
✅ Adding HTTPS using Let’s Encrypt  
✅ Testing with `curl` 🔧

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*bx247aXfFYpG_Ek2)

Whether you’re on **cloud, Minikube, or bare-metal**, this tutorial has got you covered! 😎

## 🧰 Step 1: Install the NGINX Ingress Controller

## ✅ Option 1: With Helm (Recommended)

```c
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```
```c
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

🎯 **Verify installation:**

```c
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
```

## 🍱 Step 2: Deploy a Sample NGINX Backend (Optional for test)

```c
kubectl create deployment nginx-backend --image=nginx
kubectl expose deployment nginx-backend --port=80 --target-port=80 --name=nginx-backend
```

## 🌐 Step 3: Create a Basic Ingress Resource

```c
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-backend-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: hello-world.example # replace with actual
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-backend
            port:
              number: 80
```

📌 Apply it:

```c
kubectl apply -f nginx-ingress.yaml
```

## 🔗 Step 4: Expose It to the World (For mono Node Deployment)

Change ingress type from loadbalancer to nodeport

k edit svc -n ingress-nginx

## 🌍 Get Your External IP

```c
#!/bin/bash

# Set namespace and service variables
NAMESPACE="ingress-nginx"
SERVICE="ingress-nginx-controller"

# Fetch the NodePort and handle any potential errors
NODE_PORT=$(kubectl get --namespace $NAMESPACE -o jsonpath="{.spec.ports[0].nodePort}" services $SERVICE 2>/dev/null) 
if [ -z "$NODE_PORT" ]; then
  echo "Error: Unable to fetch the NodePort for service '$SERVICE' in namespace '$NAMESPACE'."
  exit 1
fi

# Fetch the Node IP and handle any potential errors
NODE_IP=$(kubectl get nodes --namespace $NAMESPACE -o jsonpath="{.items[0].status.addresses[0].address}" 2>/dev/null) 
if [ -z "$NODE_IP" ]; then
  echo "Error: Unable to fetch the Node IP in namespace '$NAMESPACE'."
  exit 1
fi

# Display the URL                                                                                                     
URL="http://$NODE_IP:$NODE_PORT"                                                                                      
echo "Service URL: $URL"
```
```c
Service URL: http://10.9.15.138:30810
```

## 🧪 Step 5: Test with cURL

```c
curl -H "Host: hello-world.example" http://10.9.15.138:30810
```

🎉 You should see the default **NGINX Welcome Page**.

## 🔐 Step 6: Enable HTTPS with Let’s Encrypt & cert-manager

## 📦 Install cert-manager

```c
helm repo add jetstack https://charts.jetstack.io
helm repo update
```
```c
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

✅ Verify pods:

```c
kubectl get pods -n cert-manager
```

## 📜 Step 7: Create a ClusterIssuer (Staging)

```c
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    email: your-email@example.com
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-staging-key
    solvers:
    - http01:
        ingress:
          class: nginx
```
```c
kubectl apply -f cluster-issuer-staging.yaml
```

## 🔧 Step 8: Update Your Ingress for HTTPS

```c
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-backend-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - hello-world.example # to be replaced 
    secretName: nginx-backend-tls
  rules:
  - host: hello-world.example   # to be replaced
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-backend
            port:
              number: 80
```
```c
kubectl apply -f nginx-ingress-tls.yaml
```

🔍 Check cert status:

```c
kubectl describe certificate -A

Name:         nginx-backend-tls
Namespace:    fast-api-app
Labels:       <none>
Annotations:  <none>
API Version:  cert-manager.io/v1
Kind:         Certificate
Metadata:
  Creation Timestamp:  2025-05-20T19:40:37Z
  Generation:          1
  Owner References:
    API Version:           networking.k8s.io/v1
    Block Owner Deletion:  true
    Controller:            true
    Kind:                  Ingress
```

## ✅ Step 9: Test HTTPS with cURL

```c
curl -k  -H "Host: hello-world.example" https://10.9.15.138:32243
```

🚀 Use `curl https://$HOST` (without `-k`) after switching to production issuer.

## 🏆 Step 10: Switch to Let’s Encrypt Production

```c
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: your-email@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
```
```c
kubectl apply -f cluster-issuer-prod.yaml
```

👉 Update your Ingress annotation to:

```c
cert-manager.io/cluster-issuer: letsencrypt-prod
```

Re-apply to enable real TLS 🔐

## 🚀 Stay Ahead with BenchHub.co

Want to dive deeper into the tools that power today’s tech stacks?  
At [**BenchHub**](https://www.benchhub.co/)**.co**, we’re constantly benchmarking the latest DevOps, ML, and Cloud-native tools — so you don’t have to.

Don’t get left behind — **subscribe now** and supercharge your tech decisions with data that matters.

[www.benchhub.co](https://www.benchhub.co/)

👉 [Subscribe here](https://www.benchhub.co/) and join a community of builders, engineers, and decision-makers staying sharp in a fast-moving ecosystem.

🔍 **Why subscribe?**  
By joining our newsletter, you’ll get:

- 🧠 **Advanced tutorials** on real-world use cases
- 📊 **Unbiased benchmarks** of tools from the marketplace
- 🛠️ Expert insights to help you make smarter tech decisions
- ⚡ Early access to upcoming evaluations and performance reports

#Kubernetes #NGINXIngress #LetsEncrypt #certmanager #CloudNative #DevOps #Minikube #K3s #KubernetesIngress #TLS #HTTPS #nipio #k8s #Helm #Networking

## 🧠 Conclusion

You’re now running a **fully secure**, **internet-accessible**, **NGINX-backed service** on Kubernetes using **Ingress + Let’s Encrypt**! 🎯 Whether it’s for dev or prod, this setup gives you a rock-solid foundation. 💪

Let me know if you want a full **automation script** or production-hardening tips! 😉

## More from Mahernaija

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--64f15a076581---------------------------------------)