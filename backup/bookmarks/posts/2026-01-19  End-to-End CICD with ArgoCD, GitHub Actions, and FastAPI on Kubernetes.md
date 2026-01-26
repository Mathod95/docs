---
title: "End-to-End CI/CD with ArgoCD, GitHub Actions, and FastAPI on Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@spiegelhaltercurt/end-to-end-ci-cd-with-argocd-github-actions-and-fastapi-on-kubernetes-8fdcab6c12df"
author:
  - "[[Curt Spiegelhalter]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

In this tutorial, you’ll create a full CI/CD pipeline using GitHub Actions and ArgoCD to automatically build and deploy a FastAPI app into a local Kubernetes cluster. You’ll also integrate Prometheus and Grafana for monitoring, all running locally with `kind`.

This tutorial will guide you through:

- Setting up a local Kubernetes cluster with `kind`
- Building a FastAPI app with Prometheus metrics
- Creating a CI/CD pipeline using GitHub Actions
- Deploying and syncing changes with ArgoCD
- Visualizing metrics in Grafana

This assumes you already have `[kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)`, `[helm](https://helm.sh/docs/intro/install/)`, and `[kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)` installed.

Project Structure:

```c
CICDpipeline/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── todo-api/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── k8s-manifest/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── servicemonitor.yaml
│   └── argocd-app.yaml
```
1. Create a local kubernetes cluster
```c
kind create cluster --name todo-dev
```

2\. Build a FastAPI app with Prometheus metrics

`todo-api/main.py`

```c
from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from starlette.responses import Response

app = FastAPI()
hits = Counter("hits", "Number of hits to the root")

@app.get("/")
def read_root():
    hits.inc()
    return {"message": "Hello World"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

`todo-api/test_main.py`

```c
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

`todo-api/requirements.txt`

```c
fastapi
uvicorn
prometheus-client
pytest
httpx
```

`todo-api/Dockerfile`

```c
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

3\. Setup Github actions

This workflow:

- Runs tests
- Builds and pushes a Docker image
- Updates the Kubernetes manifest with the new tag
```c
.github/workflows/deploy.yml
```
```c
name: Build and Deploy

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    env:
      TAG: ${{ github.sha }}

    steps:
    - name: Checkout source code
      uses: actions/checkout@v3

    - name: Stop infinite loop if commit is from GitHub Actions
      if: github.actor == 'github-actions'
      run: |
        echo "Triggered by GitHub Actions bot — skipping workflow."
        exit 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies and run tests
      run: |
        pip install -r todo-api/requirements.txt
        pytest todo-api

    - name: Set lowercase owner
      run: |
        echo "owner_lc=${GITHUB_REPOSITORY_OWNER,,}" >> $GITHUB_ENV
        echo "image_name=ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/todo-api" >> $GITHUB_ENV

    - name: Log in to GHCR
      run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ env.owner_lc }} --password-stdin

    - name: Build Docker image
      run: docker build -t ${{ env.image_name }}:${{ env.TAG }} -f todo-api/Dockerfile todo-api

    - name: Push Docker image
      run: docker push ${{ env.image_name }}:${{ env.TAG }}

    - name: Clone manifests repo (same repo in this case)
      run: |
        git config --global user.name "GitHub Actions"
        git config --global user.email "actions@github.com"

        git clone https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/CSpiegelhalter/CICDpipeline.git
        cd CICDpipeline/k8s-manifest

        sed -i "s|image: .*|image: ${{ env.image_name }}:${{ env.TAG }}|" deployment.yaml

        git add deployment.yaml
        if git diff --cached --quiet; then
          echo "No changes to commit"
        else
          git commit -m "Update image to ${{ env.TAG }} [skip ci]"
          git push
        fi
```

4\. Install ArgoCD into the cluster ([from ArgoCD](https://argo-cd.readthedocs.io/en/stable/getting_started/#1-install-argo-cd))

```c
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Access the UI

```c
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Go to: [https://localhost:8080/](https://localhost:8080/)

Login with:

- **Username**: `admin`
- **Password** (run this command and copy the output)**:**
```c
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```

(You can port-forward and log into the ArgoCD UI right away, even before you deploy any apps.)

5\. Add Prometheus + Grafana

```c
kubectl create namespace monitoring

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.maximumStartupDurationSeconds=300
```

Port-forward Grafana

```c
kubectl port-forward svc/monitoring-grafana 3000:3000
```

Go to `[http://localhost:3000](http://localhost:3000/)`

Login with:

- **Username**: `admin`
- **Password**: `prom-operator`

(Grafana will launch and be accessible even if your app hasn’t been deployed yet. We’ll deploy your app and connect the metrics shortly.)

6\. Create Kubernetes manifests

`k8s-manifest/deployment.yaml`

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/path: "/metrics"
        prometheus.io/port: "80"
    spec:
      containers:
        - name: todo-api
          image: ghcr.io/cspiegelhalter/todo-api # Change to be your own
          ports:
            - containerPort: 80
```

`k8s-manifest/service.yaml`

```c
apiVersion: v1
kind: Service
metadata:
  name: todo-api
  labels:
    app: todo-api
spec:
  selector:
    app: todo-api
  ports:
    - name: http   # <– MUST match the \`port:\` in the ServiceMonitor
      protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

`k8s-manifest/servicemonitor.yaml`

```c
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-api
  labels:
    release: monitoring  # must match your Prometheus release name
spec:
  selector:
    matchLabels:
      app: todo-api
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
  namespaceSelector:
    matchNames:
      - default
```

7\. Connect ArgoCD to your App

`k8s-manifest/argocd_app.yaml`:

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: todo-api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/CSpiegelhalter/CICDpipeline
    targetRevision: HEAD
    path: k8s-manifest
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply your manifests:

```c
kubectl apply -f k8s-manifest/deployment.yaml
kubectl apply -f k8s-manifest/service.yaml
kubectl apply -f k8s-manifest/servicemonitor.yaml 
kubectl apply -f argocd-app.yaml
```

You now have:

- A working CI/CD pipeline from GitHub to Kubernetes
- Automated ArgoCD sync
- Live Prometheus metrics
- Grafana dashboards for observability

Here’s the repo: [https://github.com/CSpiegelhalter/CICDpipeline](https://github.com/CSpiegelhalter/CICDpipeline)

Let me know in the comments if you want a follow-up tutorial with Ingress, TLS, or external cloud hosting!

Software Engineer, Problem Solver, System Designer, Lifelong Learner

## More from Curt Spiegelhalter

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--8fdcab6c12df---------------------------------------)