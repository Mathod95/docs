---
title: Argo CD - Installation production-ready avec argocd-extension-metrics et Prometheus
date: 2025-12-10
draft: true
categories:
  - Argo CD
  - Prometheus
tags:
  - Argo CD
  - Prometheus
  - PodInfo
  - Metrics
  - UI
  - Extension
---

![](../../assets/images/argo/argo.svg)
<!-- more -->

# Complete Guide: Installing Argo CD with Prometheus Metrics via GitOps

This comprehensive tutorial will guide you through installing Argo CD and integrating Prometheus metrics into the Argo CD UI using a **pure GitOps approach**. After the initial Argo CD bootstrap, everything else will be deployed through Argo CD Applications.

## Prerequisites

- **Docker** installed and running
- **kubectl** installed
- **helm** (v3+) installed
- **kind** (Kubernetes in Docker) installed
- Basic understanding of Kubernetes concepts

### Installing Prerequisites

If you don't have the tools installed:

```bash
# Install kubectl
# macOS
brew install kubectl
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install kind
# macOS
brew install kind
# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

## Overview

We'll complete these steps using a **pure GitOps approach**:
1. **Create a Kind Cluster** (local Kubernetes cluster)
2. **Install Argo CD** (bootstrap - only manual step)
3. **Deploy Everything Else via Argo CD**:
   - Prometheus (via Argo CD's Helm wrapper)
   - Argo CD Metrics Server
   - Podinfo application

**Philosophy:** After the initial Argo CD installation, everything else is deployed through Argo CD Applications - true GitOps! No more `helm install` or manual `kubectl apply` commands for applications.

---

## Step 0: Create a Kind Cluster

We'll create a local Kubernetes cluster using Kind (Kubernetes in Docker). This is perfect for testing and development.

### 0.1 Create Kind Configuration File

Create a file named `kind-config.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: argocd-demo
nodes:
  - role: control-plane
    kubeadmConfigPatches:
    - |
      kind: InitConfiguration
      nodeRegistration:
        kubeletExtraArgs:
          node-labels: "ingress-ready=true"
    extraPortMappings:
    - containerPort: 80
      hostPort: 80
      protocol: TCP
    - containerPort: 443
      hostPort: 443
      protocol: TCP
    - containerPort: 30080
      hostPort: 30080
      protocol: TCP
```

This configuration:
- Creates a single-node cluster named `argocd-demo`
- Maps ports 80, 443, and 30080 for easier access to services
- Labels the node for Ingress support

### 0.2 Create the Cluster

```bash
kind create cluster --config kind-config.yaml
```

This will take a few minutes. You'll see output like:
```
Creating cluster "argocd-demo" ...
 ✓ Ensuring node image (kindest/node:v1.27.3) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-argocd-demo"
```

### 0.3 Verify the Cluster

```bash
# Check the cluster is running
kind get clusters

# Check nodes
kubectl get nodes

# Check context
kubectl config current-context
```

You should see:
```
NAME                        STATUS   ROLES           AGE   VERSION
argocd-demo-control-plane   Ready    control-plane   1m    v1.27.3
```

---

## Step 1: Install Argo CD (Bootstrap)

This is the **only manual installation step**. Once Argo CD is running, we'll use it to deploy everything else.

### 1.1 Add the Argo CD Helm Repository

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

### 1.2 Create Argo CD Configuration File

Create a file named `argocd-values.yaml`:

```yaml
# Argo CD Server configuration
server:
  # Enable and configure extensions
  extensions:
    enabled: true
    extensionList:
      - name: extension-metrics
        env:
          - name: EXTENSION_URL
            value: https://github.com/argoproj-labs/argocd-extension-metrics/releases/download/v1.0.3/extension.tar.gz
          - name: EXTENSION_CHECKSUM_URL
            value: https://github.com/argoproj-labs/argocd-extension-metrics/releases/download/v1.0.3/extension_checksums.txt

# Argo CD configuration
configs:
  # ConfigMap for extension configuration
  cm:
    extension.config: |
      extensions:
        - name: metrics
          backend:
            services:
              - url: http://argocd-metrics-server.argocd.svc:9003
  
  # Server parameters
  params:
    # Enable the proxy extension feature (required for metrics)
    server.enable.proxy.extension: "true"
  
  # RBAC configuration
  rbac:
    policy.csv: |
      p, role:readonly, extensions, invoke, metrics, allow
      p, role:admin, extensions, invoke, metrics, allow
```

### 1.3 Install Argo CD

```bash
helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --values argocd-values.yaml \
  --wait
```

This will take a few minutes. Wait for all pods to be ready.

### 1.4 Verify Argo CD Installation

```bash
# Check all pods are running
kubectl get pods -n argocd

# You should see:
# - argocd-server
# - argocd-repo-server
# - argocd-application-controller
# - argocd-redis
# - argocd-applicationset-controller
# - argocd-notifications-controller
```

### 1.5 Get Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

**Save this password!** Username is `admin`.

### 1.6 Access Argo CD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open https://localhost:8080 and login with `admin` and the password from step 1.5.

**Note:** You'll see a certificate warning. This is normal for self-signed certificates. Click "Advanced" and proceed.

---

## Step 2: Deploy Prometheus via Argo CD

Now we'll deploy Prometheus using Argo CD's Helm wrapper. This is **pure GitOps** - no manual helm commands!

### 2.1 Create Prometheus Application Manifest

Create a file named `prometheus-app.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kube-prometheus-stack
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    # Using Helm chart directly from the repository
    repoURL: https://prometheus-community.github.io/helm-charts
    chart: kube-prometheus-stack
    targetRevision: 65.1.1  # Pin to a specific version for reproducibility
    helm:
      # Helm values can be customized here
      values: |
        # Disable components we don't need for this demo
        alertmanager:
          enabled: false
        
        # Reduce resource usage for local development
        prometheus:
          prometheusSpec:
            resources:
              requests:
                cpu: 200m
                memory: 512Mi
              limits:
                cpu: 500m
                memory: 1Gi
            retention: 6h
            storageSpec:
              volumeClaimTemplate:
                spec:
                  accessModes: ["ReadWriteOnce"]
                  resources:
                    requests:
                      storage: 5Gi
        
        grafana:
          enabled: true
          adminPassword: admin
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
  
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

### 2.2 Deploy Prometheus via Argo CD

```bash
kubectl apply -f prometheus-app.yaml
```

### 2.3 Watch the Deployment

You can watch Prometheus being deployed in two ways:

**Via CLI:**
```bash
# Watch the application sync
kubectl get application kube-prometheus-stack -n argocd -w

# Watch pods being created in monitoring namespace
kubectl get pods -n monitoring -w
```

Press `Ctrl+C` to stop watching once all pods are running.

**Via Argo CD UI:**
1. Refresh the Argo CD UI (https://localhost:8080)
2. You'll see the `kube-prometheus-stack` application
3. Click on it to see the deployment progress
4. Wait until the status is "Healthy" and "Synced"

### 2.4 Verify Prometheus Installation

```bash
# Check all monitoring pods are running
kubectl get pods -n monitoring

# You should see pods for:
# - prometheus-operator
# - prometheus
# - grafana
# - kube-state-metrics
# - node-exporter
```

Wait until all pods show `Running` status before proceeding.

---

## Step 3: Deploy Argo CD Metrics Server

Now we'll deploy the metrics server. Since this is a simple deployment, we'll apply the manifests directly (not via an Argo CD Application).

### 3.1 Create Metrics Server ConfigMap

Create a file named `metrics-server-configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-metrics-server-configmap
  namespace: argocd
data:
  # Define metrics for Deployments
  extension.metrics.deployments: |
    - name: "CPU Usage"
      description: "CPU usage for the deployment"
      type: "graph"
      graphType: "area"
      yAxisLabel: "CPU Cores"
      query: 'sum(rate(container_cpu_usage_seconds_total{namespace="{{.metadata.namespace}}", pod=~"{{.metadata.name}}-.*"}[5m])) by (pod)'

    - name: "Memory Usage"
      description: "Memory usage for the deployment"
      type: "graph"
      graphType: "area"
      yAxisLabel: "Memory (MB)"
      query: 'sum(container_memory_working_set_bytes{namespace="{{.metadata.namespace}}", pod=~"{{.metadata.name}}-.*"}) by (pod) / 1024 / 1024'

    - name: "Network Received"
      description: "Network bytes received"
      type: "graph"
      graphType: "line"
      yAxisLabel: "Bytes/sec"
      query: 'sum(rate(container_network_receive_bytes_total{namespace="{{.metadata.namespace}}", pod=~"{{.metadata.name}}-.*"}[5m])) by (pod)'

  # Define metrics for Pods
  extension.metrics.pods: |
    - name: "CPU Usage"
      description: "CPU usage for the pod"
      type: "graph"
      graphType: "area"
      yAxisLabel: "CPU Cores"
      query: 'sum(rate(container_cpu_usage_seconds_total{namespace="{{.metadata.namespace}}", pod="{{.metadata.name}}"}[5m])) by (container)'

    - name: "Memory Usage"
      description: "Memory usage for the pod"
      type: "graph"
      graphType: "area"
      yAxisLabel: "Memory (MB)"
      query: 'sum(container_memory_working_set_bytes{namespace="{{.metadata.namespace}}", pod="{{.metadata.name}}"}) by (container) / 1024 / 1024'

    - name: "Container Restarts"
      description: "Number of container restarts"
      type: "graph"
      graphType: "line"
      yAxisLabel: "Restarts"
      query: 'kube_pod_container_status_restarts_total{namespace="{{.metadata.namespace}}", pod="{{.metadata.name}}"}'

  # Prometheus connection settings
  prometheus.url: "http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090"
```

Apply it:

```bash
kubectl apply -f metrics-server-configmap.yaml
```

### 3.2 Create Metrics Server Deployment

Create a file named `metrics-server-deployment.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: argocd-metrics-server
  namespace: argocd
  labels:
    app: argocd-metrics-server
spec:
  ports:
  - name: http
    port: 9003
    protocol: TCP
    targetPort: 9003
  selector:
    app: argocd-metrics-server
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-metrics-server
  namespace: argocd
  labels:
    app: argocd-metrics-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: argocd-metrics-server
  template:
    metadata:
      labels:
        app: argocd-metrics-server
    spec:
      containers:
      - name: argocd-metrics-server
        image: quay.io/argoprojlabs/argocd-extension-metrics:v1.0.3
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9003
          name: http
          protocol: TCP
        env:
        - name: PROMETHEUS_URL
          valueFrom:
            configMapKeyRef:
              name: argocd-metrics-server-configmap
              key: prometheus.url
        volumeMounts:
        - name: config
          mountPath: /etc/argocd-metrics-server/
        resources:
          limits:
            cpu: 100m
            memory: 128Mi
          requests:
            cpu: 50m
            memory: 64Mi
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: true
          runAsNonRoot: true
      volumes:
      - name: config
        configMap:
          name: argocd-metrics-server-configmap
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
```

Apply it:

```bash
kubectl apply -f metrics-server-deployment.yaml
```

### 3.3 Verify Metrics Server

```bash
# Check the metrics server pod
kubectl get pods -n argocd -l app=argocd-metrics-server

# Check logs
kubectl logs -n argocd -l app=argocd-metrics-server
```

You should see the server starting and listening on port 9003.

---

## Step 4: Deploy Podinfo via Argo CD

Now let's deploy Podinfo using Argo CD. This demonstrates the full GitOps workflow.

### 4.1 Create Podinfo Application Manifest

Create a file named `podinfo-app.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: podinfo
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/stefanprodan/podinfo.git
    targetRevision: HEAD
    path: kustomize
  destination:
    server: https://kubernetes.default.svc
    namespace: podinfo
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### 4.2 Deploy Podinfo

```bash
kubectl apply -f podinfo-app.yaml
```

### 4.3 Watch the Deployment in Argo CD UI

1. Go to the Argo CD UI (https://localhost:8080)
2. You'll see the **podinfo** application appear
3. Click on it to watch the deployment progress
4. Wait until status shows "Healthy" and "Synced"

**Via CLI:**
```bash
# Watch application status
kubectl get application podinfo -n argocd -w

# Watch pods
kubectl get pods -n podinfo -w
```

### 4.4 Verify Podinfo is Running

```bash
kubectl get pods -n podinfo
```

You should see 2 podinfo pods running.

---

## Step 5: Verify the Complete Setup

Now let's verify that everything is working together!

### 5.1 Check All Applications in Argo CD UI

In the Argo CD UI (https://localhost:8080), you should now see:
1. **kube-prometheus-stack** - Status: Healthy & Synced
2. **podinfo** - Status: Healthy & Synced

### 5.2 Generate Traffic to Podinfo

Let's generate some traffic to see dynamic metrics:

```bash
# Port forward to podinfo
kubectl port-forward -n podinfo svc/podinfo 9898:9898 &

# Generate traffic
for i in {1..100}; do
  curl -s http://localhost:9898 > /dev/null
  echo "Request $i completed"
  sleep 0.1
done
```

### 5.3 View Metrics in Argo CD UI

1. In Argo CD UI, click on the **podinfo** application
2. Click on the **podinfo Deployment**
3. Look for the **"Metrics"** tab
4. Click on it to see:
   - CPU Usage graphs
   - Memory Usage graphs
   - Network I/O graphs

🎉 **Success!** You're now seeing Prometheus metrics directly in Argo CD!

### 5.4 View Pod-Level Metrics

1. From the podinfo application view, click on any **Pod**
2. Go to the **Metrics** tab
3. You'll see individual pod metrics

### 5.5 Generate Continuous Traffic

For more interesting graphs:

```bash
# Stop the previous port-forward if running
pkill -f "port-forward.*podinfo"

# Start new port-forward
kubectl port-forward -n podinfo svc/podinfo 9898:9898 &

# Generate continuous traffic
while true; do
  curl -s http://localhost:9898 > /dev/null
  sleep 0.5
done
```

Refresh the Metrics tab to see CPU and network usage increase!

---

## Step 6: Understanding the GitOps Workflow

### What We Accomplished

✅ **Single Bootstrap Step:** Only Argo CD was installed manually
✅ **Everything Else via GitOps:** Prometheus and Podinfo deployed through Argo CD
✅ **Declarative:** All configuration in YAML files
✅ **Observable:** Metrics visible directly in Argo CD UI
✅ **Self-Healing:** Argo CD auto-syncs and heals applications

### The GitOps Advantages

**Before (Traditional):**
```bash
helm install prometheus ...
helm install argocd ...
kubectl apply -f metrics-server.yaml
kubectl apply -f podinfo.yaml
```
❌ Multiple manual commands
❌ Hard to track what's deployed
❌ No automatic sync

**After (GitOps with Argo CD):**
```bash
# Bootstrap
helm install argocd ...

# Everything else
kubectl apply -f prometheus-app.yaml
kubectl apply -f podinfo-app.yaml
```
✅ Centralized in Argo CD
✅ Visible in UI
✅ Auto-sync enabled
✅ Git as source of truth (if you commit these YAMLs)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Argo CD                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Prometheus  │  │    Metrics   │  │   Podinfo    │     │
│  │  Application │  │    Server    │  │  Application │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         ▼                  │                  ▼             │
│  ┌──────────────┐          │           ┌──────────────┐    │
│  │  Prometheus  │◄─────────┘           │   Podinfo    │    │
│  │   (Helm)     │                      │     Pods     │    │
│  └──────────────┘                      └──────────────┘    │
│         │                                      │            │
│         │  (scrapes metrics)                   │            │
│         └──────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘

Argo CD UI Extension reads metrics from Metrics Server
Metrics Server queries Prometheus
Prometheus scrapes metrics from Podinfo pods
```

---

## Step 7: Taking It Further - Full GitOps

### 7.1 Store Everything in Git (Recommended)

For a true GitOps workflow, create a Git repository with this structure:

```
my-argocd-apps/
├── bootstrap/
│   └── argocd-values.yaml          # Argo CD initial config
├── infrastructure/
│   ├── prometheus-app.yaml         # Prometheus Application
│   ├── metrics-server-configmap.yaml
│   └── metrics-server-deployment.yaml
└── applications/
    └── podinfo-app.yaml            # Podinfo Application
```

Then deploy everything with:

```bash
# Deploy infrastructure
kubectl apply -f infrastructure/

# Deploy applications
kubectl apply -f applications/
```

Or better yet, use Argo CD's **App of Apps** pattern!

### 7.2 App of Apps Pattern

Create a file named `app-of-apps.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/YOUR-USERNAME/YOUR-REPO.git
    targetRevision: HEAD
    path: applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

This one Application manages all other Applications!

### 7.3 Modify Prometheus Values via GitOps

Want to change Prometheus configuration? Just update the Application manifest:

**Edit `prometheus-app.yaml`:**
```yaml
spec:
  source:
    helm:
      values: |
        prometheus:
          prometheusSpec:
            retention: 24h  # Changed from 6h
```

Then:
```bash
kubectl apply -f prometheus-app.yaml
```

Argo CD will automatically sync the changes! No manual helm upgrade needed.

### 7.4 Deploy More Applications

Create `nginx-app.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://charts.bitnami.com/bitnami
    chart: nginx
    targetRevision: 15.4.4
    helm:
      values: |
        replicaCount: 2
  destination:
    server: https://kubernetes.default.svc
    namespace: nginx
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Apply it:
```bash
kubectl apply -f nginx-app.yaml
```

Watch it deploy in Argo CD UI!

---

## Step 8: Explore Additional Features

### 8.1 Access Podinfo UI

```bash
kubectl port-forward -n podinfo svc/podinfo 9898:9898
```

Open http://localhost:9898 to see:
- Version information
- Runtime details
- Health endpoints
- Metrics endpoint at /metrics

### 8.2 Access Prometheus UI

```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

Open http://localhost:9090 and try queries like:
- `container_cpu_usage_seconds_total{namespace="podinfo"}`
- `container_memory_usage_bytes{namespace="podinfo"}`

### 8.3 Access Grafana

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
```

Open http://localhost:3000
- **Username:** admin
- **Password:** admin (as configured in the Prometheus Application)

Explore pre-configured Kubernetes dashboards!

### 8.4 View All Applications

```bash
# List all applications
kubectl get applications -n argocd

# View application details
kubectl describe application podinfo -n argocd

# View sync status
kubectl get applications -n argocd -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.health.status}{"\t"}{.status.sync.status}{"\n"}{end}'
```

---

## Customizing Metrics

The metrics displayed are configured in the `argocd-metrics-server-configmap` ConfigMap.

### Edit Metrics Configuration

```bash
kubectl edit configmap argocd-metrics-server-configmap -n argocd
```

After editing, restart the metrics server:

```bash
kubectl rollout restart deployment argocd-metrics-server -n argocd
```

### Adding Metrics for Other Resources

You can add metrics for any Kubernetes resource type. For example, to add metrics for StatefulSets:

```yaml
extension.metrics.statefulsets: |
  - name: "CPU Usage"
    description: "CPU usage for the statefulset"
    type: "graph"
    graphType: "area"
    yAxisLabel: "CPU Cores"
    query: 'sum(rate(container_cpu_usage_seconds_total{namespace="{{.metadata.namespace}}", pod=~"{{.metadata.name}}-.*"}[5m])) by (pod)'
```

### Available Query Variables

In your Prometheus queries, you can use these template variables:
- `{{.metadata.name}}` - Resource name
- `{{.metadata.namespace}}` - Resource namespace
- `{{.metadata.labels.KEY}}` - Any label value

### Example: Custom Application Metrics

If your application exposes custom metrics:

```yaml
extension.metrics.deployments: |
  - name: "Request Rate"
    description: "HTTP requests per second"
    type: "graph"
    graphType: "line"
    yAxisLabel: "req/s"
    query: 'rate(http_requests_total{namespace="{{.metadata.namespace}}", pod=~"{{.metadata.name}}-.*"}[5m])'
```

---

## Troubleshooting

### Metrics Tab Not Appearing

**Check if the extension is loaded:**
```bash
kubectl logs -n argocd deployment/argocd-server | grep extension
```

**Verify the proxy extension is enabled:**
```bash
kubectl get configmap argocd-cmd-params-cm -n argocd -o yaml | grep proxy
```

Should show: `server.enable.proxy.extension: "true"`

### No Metrics Data Displayed

**Verify metrics server is running:**
```bash
kubectl get pods -n argocd | grep metrics-server
```

**Check metrics server logs:**
```bash
kubectl logs -n argocd deployment/argocd-metrics-server
```

**Test Prometheus connectivity:**
```bash
kubectl exec -n argocd deployment/argocd-metrics-server -- wget -O- http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090/api/v1/query?query=up
```

### Prometheus Application Not Syncing

**Check application status:**
```bash
kubectl describe application kube-prometheus-stack -n argocd
```

**View sync logs in Argo CD UI:**
1. Click on the application
2. View the sync status
3. Check for error messages

### Kind Cluster Issues

**Cluster won't start:**
```bash
# Check Docker is running
docker ps

# Delete and recreate
kind delete cluster --name argocd-demo
kind create cluster --config kind-config.yaml
```

**Can't access services:**
```bash
# Check port forwards
lsof -i :8080
lsof -i :9898

# Kill existing port forwards
pkill -f "port-forward"
```

---

## Clean Up

### Clean Up Specific Resources

To remove individual applications via Argo CD:

```bash
# Delete applications (Argo CD will clean up resources)
kubectl delete application podinfo -n argocd
kubectl delete application kube-prometheus-stack -n argocd

# Delete metrics server (not managed by Argo CD)
kubectl delete deployment argocd-metrics-server -n argocd
kubectl delete service argocd-metrics-server -n argocd
kubectl delete configmap argocd-metrics-server-configmap -n argocd

# Delete Argo CD
helm uninstall argocd -n argocd

# Delete namespaces
kubectl delete namespace argocd
kubectl delete namespace monitoring
kubectl delete namespace podinfo
```

### Delete the Entire Kind Cluster

To completely remove the cluster:

```bash
kind delete cluster --name argocd-demo
```

### Verify Cleanup

```bash
# Check no clusters remain
kind get clusters

# Verify context is removed
kubectl config get-contexts
```

---

## Quick Reference: Useful Commands

### Kind Cluster Management

```bash
# Create cluster
kind create cluster --config kind-config.yaml

# List clusters
kind get clusters

# Delete cluster
kind delete cluster --name argocd-demo

# Load local Docker image into Kind
kind load docker-image my-image:tag --name argocd-demo
```

### Argo CD Operations

```bash
# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward to UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# List applications
kubectl get applications -n argocd

# Get application details
kubectl get application podinfo -n argocd -o yaml

# Force sync
kubectl patch application podinfo -n argocd --type merge -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{"revision":"HEAD"}}}'
```

### Monitoring

```bash
# Watch all pods across namespaces
kubectl get pods -A -w

# Check application sync status
kubectl get applications -n argocd -w

# View Argo CD server logs
kubectl logs -n argocd deployment/argocd-server -f

# View metrics server logs
kubectl logs -n argocd deployment/argocd-metrics-server -f
```
