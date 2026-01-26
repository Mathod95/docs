---
title: "Kubernetes Networking in Action: A Full Demo with Services, Ingress, and Network Policies"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://poojabolla.medium.com/kubernetes-networking-in-action-a-full-demo-with-services-ingress-and-network-policies-bbfa5e8eb06c"
author:
  - "[[Pooja Bolla]]"
---
<!-- more -->

[Sitemap](https://poojabolla.medium.com/sitemap/sitemap.xml)

In continuation to the previous post on [Kubernetes Networking](https://poojabolla.medium.com/a-beginners-guide-to-kubernetes-networking-a77317938b82), in this post lets do an end-to-end project. Now, let’s bring everything together in a practical **end-to-end hands-on lab** by deploying a sample multi-tier application that includes:

- A frontend
- A backend API
- A database

We’ll wire them together using **Services**, expose them externally with **Ingress**, and lock down communications with **Network Policies**.

### 🧱 App Architecture Overview

We’ll use a simplified ecommerce-like structure:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ZZDUmv23v4fRArHSDDel4Q.png)

### 🛠️ Step 1: Set Up the Namespace

We’ll use a separate namespace for this demo:

```c
kubectl create namespace networking-demo
```

### 📦 Step 2: Deploy the Database (PostgreSQL)

Create a basic PostgreSQL Deployment and Service.

```c
# db.yaml
apiVersion: v1
kind: Service
metadata:
  name: db
  namespace: networking-demo
spec:
  ports:
    - port: 5432
  selector:
    app: db
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
  namespace: networking-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_USER
          value: "admin"
        - name: POSTGRES_PASSWORD
          value: "password"
```
```c
kubectl apply -f db.yaml
```

✅ **Verify**:

```c
kubectl get pods -n networking-demo
kubectl get svc -n networking-demo
```

### ⚙️ Step 3: Deploy the Backend API

```c
# backend.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: networking-demo
spec:
  selector:
    app: backend
  ports:
    - port: 3000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: networking-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/backend:latest
        env:
        - name: DB_HOST
          value: "db"
        - name: DB_USER
          value: "admin"
        - name: DB_PASS
          value: "password"
        ports:
        - containerPort: 3000
```
```c
kubectl apply -f backend.yaml
```

### 🎨 Step 4: Deploy the Frontend (React)

```c
# frontend.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: networking-demo
spec:
  selector:
    app: frontend
  ports:
    - port: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: networking-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/frontend:latest
        env:
        - name: API_URL
          value: "http://backend:3000"
        ports:
        - containerPort: 80
```
```c
kubectl apply -f frontend.yaml
```

### 🌐 Step 5: Add Ingress Controller & Ingress Rule

Install NGINX Ingress Controller (skip if already installed):

```c
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
```

Create an Ingress resource:

```c
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
  namespace: networking-demo
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: demo.local
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
```c
kubectl apply -f ingress.yaml
```

Add this to your `/etc/hosts` file:

```c
<Minikube_IP> demo.local
```

Open `http://server-ip.ingress-port` in your browser!

If using minikube, use `[http://demo.loca](http://demo.local/)l` just like the jost mentioned in the ingress file.

### 🔐 Step 6: Apply Network Policies

We’ll block traffic **except** what’s needed.

**Allow backend to talk to db**

```c
# allow-backend-to-db.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-to-db
  namespace: networking-demo
spec:
  podSelector:
    matchLabels:
      app: db
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend
```

**Allow frontend to talk to backend**

```c
# allow-frontend-to-backend.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-to-backend
  namespace: networking-demo
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
```
```c
kubectl apply -f allow-backend-to-db.yaml
kubectl apply -f allow-frontend-to-backend.yaml
```

## 🧪 Verification & Testing

1. ✅ `curl` from frontend to backend works.
2. ❌ A busybox pod not labeled properly cannot access backend or db.
3. ✅ Ingress URL (`http://server-ip:ingress-port`) serves the React frontend.
4. ✅ Frontend loads data from backend, which in turn connects to PostgreSQL.

### 🧠 Wrap-Up

In this hands-on demo, you’ve built a real-world Kubernetes networking setup:

- Used **Services** to expose Pods
- Used **Ingress** to allow external access
- Created **Network Policies** to enforce security boundaries

This demo represents a **production-like blueprint** of secure microservice communication.

DevOps | SRE | Cloud Book an appointment here - [https://topmate.io/poojabolla/](https://topmate.io/poojabolla/)

## More from Pooja Bolla

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--bbfa5e8eb06c---------------------------------------)