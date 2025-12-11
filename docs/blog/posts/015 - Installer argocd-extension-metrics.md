---
title: Installer argocd-extension-metrics
date: 2025-12-11
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
  - Production Ready
  - GitOps
todo:
  - Changer le format de l'application de prometheus pour lire un fichier Charts.yaml values.yaml et pas inclure la charts dans l'application
  - des apply à la main pour metrics-server-deployment.yaml et metrics-server-configmap.yaml alors que Argocd Devrait le faire
  - Changer les helms par des wrapper
  - Verifier les variables utilisateur dans les codeBlocks
user-defined-values:
  - GIT_PROVIDER
  - USER
---

![](../../assets/images/argo/argo.svg)

## Introduction

Ce tutoriel complet vous guide pas à pas pour installer Argo CD et intégrer les métriques Prometheus dans l’interface Argo CD en utilisant une approche GitOps. Après l’installation initiale d’Argo CD, tout le reste sera déployé via des Applications Argo CD.

<!-- more -->

!!! Example "VARIABLES"
    {{{user-defined-values}}}

### Prérequis

- **Docker**
- **kubectl**
- **helm**
- **kind**
- Connaissances de base des concepts **Kubernetes**

#### Installation des prérequis

=== "Brew"

    ```bash hl_lines="1"
    brew install kubectl kind helm
    ```

=== "Binary"

    ```shell title="kind" hl_lines="1 2 3"
    [ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.30.0/kind-linux-amd64
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    ```

    ```shell title="kubectl" hl_lines="1 2"
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    ```

    ```shell title="helm"  hl_lines="1 2 3"
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4
    chmod 700 get_helm.sh
    ./get_helm.sh
    ```

### Objectif

- Installer Argo CD via `Helm`
- Déployer Prometheus et visualiser les métriques dans Argo CD
- Gérer toutes les applications via Argo CD Applications

### Vue d’ensemble

Le tutoriel couvre : création d’un cluster local Kind, installation d’Argo CD, déploiement d’applications via Argo CD, et intégration des métriques Prometheus.

Nous allons réaliser ces étapes en utilisant une approche **GitOps pure** :

1. **Créer un cluster Kind** (cluster Kubernetes local)
2. **Installer Argo CD** (bootstrap – seule étape manuelle)
3. **Déployer tout le reste via Argo CD** :

   * Prometheus (via le wrapper Helm d’Argo CD)
   * Serveur de métriques Argo CD
   * Application Podinfo

**Philosophie :** après l’installation initiale d’Argo CD, tout le reste est déployé via des Applications Argo CD – du vrai GitOps ! Plus besoin de `helm install` ou de `kubectl apply` manuels pour les applications.

Ce guide vous montre comment structurer votre dépôt Git pour déployer **tout** via Argo CD en utilisant le modèle **App of Apps**.

```shell title="Structure du dépôt"
argocd-gitops/
├── README.md
├── bootstrap/
│   └── argocd-values.yaml              # Initial Argo CD Helm values
├── apps/
│   ├── app-of-apps.yaml                # Root application (manages all others)
│   ├── prometheus.yaml                 # Prometheus Application
│   ├── metrics-server.yaml             # Metrics Server Application
│   └── podinfo.yaml                    # Podinfo Application
└── manifests/
    └── metrics-server/
        ├── kustomization.yaml
        ├── configmap.yaml
        └── deployment.yaml
```

## Créer un cluster Kind

Nous allons créer un cluster Kubernetes local en utilisant Kind (Kubernetes dans Docker). Cela convient parfaitement pour les tests et le développement.

```yaml hl_lines="1"
kind create cluster
```

??? quote "OUTPUT"
    ```shell hl_lines="1"
    Creating cluster "kind" ...
     ✓ Ensuring node image (kindest/node:v1.34.0) 🖼
     ✓ Preparing nodes 📦
     ✓ Writing configuration 📜
     ✓ Starting control-plane 🕹
     ✓ Installing CNI 🔌
     ✓ Installing StorageClass 💾
    Set kubectl context to "kind-kind"
    You can now use your cluster with:

    kubectl cluster-info --context kind-kind

    Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂
    ```

??? info "CHECK"

    ```bash hl_lines="1" title="Check the cluster is running"
    kind get clusters
    kind
    ```

    ```bash hl_lines="1" title="Check nodes"
    kubectl get nodes
    NAME                 STATUS   ROLES           AGE     VERSION
    kind-control-plane   Ready    control-plane   8m38s   v1.34.0
    ```

    ```bash hl_lines="1" title="Check context"
    kubectl config current-context
    kind-kind
    ```

## Déploiement d'Argo CD

C’est la seule étape d’installation manuelle. Une fois qu’Argo CD est opérationnel, nous l’utiliserons pour déployer tout le reste.

### Ajouter le dépôt Helm d’Argo CD
```bash hl_lines="1-2"
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```
??? quote "OUTPUT"

    ```bash hl_lines="1 3 7-11" 
    helm repo add argo https://argoproj.github.io/argo-helm
    "argo" has been added to your repositories
    helm repo update
    Hang tight while we grab the latest from your chart repositories...
    ...Successfully got an update from the "argo" chart repository
    Update Complete. ⎈Happy Helming!⎈
    ```


### Créer le fichier de configuration d’Argo CD

Créer un fichier nommé `bootstrap/argocd-values.yaml`
Ce fichier contient la configuration initiale d’Argo CD avec l’extension de métriques.

```yaml title="bootstrap/argocd-values.yaml" linenums="1"
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

### Installation d'Argo CD

```bash hl_lines="1-5"
helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --values bootstrap/argocd-values.yaml \
  --wait
```

??? quote "OUTPUT"

    ```bash
    NAME: argocd
    LAST DEPLOYED: Thu Dec 11 09:10:58 2025
    NAMESPACE: argocd
    STATUS: deployed
    REVISION: 1
    DESCRIPTION: Install complete
    TEST SUITE: None
    NOTES:
    In order to access the server UI you have the following options:

    1. kubectl port-forward service/argocd-server -n argocd 8080:443

        and then open the browser on http://localhost:8080 and accept the certificate

    2. enable ingress in the values file `server.ingress.enabled` and either
          - Add the annotation for ssl passthrough: https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#option-1-ssl-passthrough
          - Set the `configs.params."server.insecure"` in the values file and terminate SSL at your ingress: https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#option-2-multiple-ingress-objects-and-hosts


    After reaching the UI the first time you can login with username: admin and the random password generated during the installation. You can find the password by running:

    kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

    (You should delete the initial secret afterwards as suggested by the Getting Started Guide: https://argo-cd.readthedocs.io/en/stable/getting_started/#4-login-using-the-cli)
    ```

??? info "CHECK"

    ```bash hl_lines="1" title="Vérifier les pods d’Argo CD"
    kubectl get pods -n argocd
    NAME                                                READY   STATUS    RESTARTS   AGE
    argocd-application-controller-0                     1/1     Running   0          22m
    argocd-applicationset-controller-79f494df96-87l4z   1/1     Running   0          22m
    argocd-dex-server-c5685b4c4-ch7xv                   1/1     Running   0          22m
    argocd-notifications-controller-7cc7769574-7cmnw    1/1     Running   0          22m
    argocd-redis-767d85d48f-nwsvz                       1/1     Running   0          22m
    argocd-repo-server-568747db-nfvwp                   1/1     Running   0          22m
    argocd-server-64788f557d-zshgz                      1/1     Running   0          22m
    ```

### Obtenir le mot de passe administrateur

```bash hl_lines="1"
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
2KId8ZZbYuBMTK6u
```

### Accéder à l’interface utilisateur d’Argo CD

```bash hl_lines="1"
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

!!! Note 
    Ouvrez [https://localhost:8080](https://localhost:8080) et connectez-vous avec l’utilisateur `admin` et le mot de passe obtenu précédemment.

    Vous verrez un avertissement de certificat. C’est normal pour les certificats auto-signés. Cliquez sur Avancé puis Continuer.


## App of Apps

### Créer le manifeste Application pour App-of-Apps

This is the **root application** that manages all other applications.

```yaml linenums="1" title="apps/app-of-apps.yaml"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/YOUR-USERNAME/argocd-gitops.git
    targetRevision: HEAD
    path: apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Important:** Replace `YOUR-USERNAME` with your actual GitHub username!

## Prometheus

Nous allons maintenant déployer Prometheus en utilisant un wrapper Helm.

### Créer le manifeste de Application Prometheus

Create a file named `prometheus-app.yaml`:

```yaml title="prometheus-app.yaml" linenums="1"
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

??? info "CHECK"
    
    Vous pouvez suivre le déploiement de Prometheus de deux manières:

    === "CLI"

        ```bash hl_lines="1" title="Observer la synchronisation de l'application"
        kubectl get application kube-prometheus-stack -n argocd -w
        NAME                    SYNC STATUS   HEALTH STATUS
        kube-prometheus-stack   Synced        Healthy
        ```

        ```bash hl_lines="1" title="Observer la création des pods dans le namespace monitoring"
        kubectl get pods -n monitoring -w
        NAME                                                        READY   STATUS    RESTARTS   AGE
        kube-prometheus-stack-grafana-5b546b8c56-nqg2q              3/3     Running   0          113s
        kube-prometheus-stack-kube-state-metrics-74988dd77d-x7n74   1/1     Running   0          113s
        kube-prometheus-stack-operator-84df4fd8d-45wqd              1/1     Running   0          113s
        kube-prometheus-stack-prometheus-node-exporter-gsttg        1/1     Running   0          113s
        prometheus-kube-prometheus-stack-prometheus-0               2/2     Running   0          107s
        ```
        Appuyez sur `Ctrl+C` pour arrêter l'observation une fois que tous les pods sont en cours d'exécution.

    === "UI"

        1. Actualisez l'interface utilisateur d'Argo CD [https://localhost:8080](https://localhost:8080)
        2. Vous verrez l'application **kube-prometheus-stack**
        3. Cliquez dessus pour voir la progression du déploiement
        4. Attendez que l'état soit "Healthy" et "Synced"


## Argo CD Extension Metrics

### Créer le manifeste Application argocd-extension-metrics

```yaml title="apps/metrics-server.yaml" linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: argocd-metrics-server
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://gitea.mathod.fr/mathod/argocd-gitops.git
    targetRevision: HEAD
    path: manifests/metrics-server
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Créer le manifeste Service argocd-extension-metrics

```yaml title="manifests/metrics-server/service.yaml" linenums="1"
apiVersion: v1
kind: Service
metadata:
  name: argocd-metrics-server
  labels:
    app.kubernetes.io/name: argocd-metrics-server
    app.kubernetes.io/part-of: argocd
spec:
  ports:
  - name: metrics
    port: 9003
    protocol: TCP
    targetPort: 9003
  selector:
    app: argocd-metrics-server
```

### Créer le manifeste Kustomization argocd-extension-metrics

```yaml title="manifests/metrics-server/kustomization.yaml" linenums="1"
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- configmap.yaml
- deployment.yaml
- service.yaml
```

### Créer le manifeste Deployment argocd-extension-metrics

```yaml title="manifests/metrics-server/deployment.yaml" linenums="1"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-metrics-server
spec:
  selector:
    matchLabels:
      app: argocd-metrics-server
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: argocd-metrics-server
    spec:
      containers:
        - image: quay.io/argoprojlabs/argocd-extension-metrics:latest
          imagePullPolicy: IfNotPresent
          args:
            - '-enableTLS=false'
          name: argocd-metrics-server
          ports:
            - containerPort: 9003
              name: metrics
              protocol: TCP
          resources:
            requests:
              cpu: 100m
              memory: 100Mi
          volumeMounts:
            - name: config-volume
              mountPath: /app/config.json
              subPath: config.json
      volumes:
        - name: config-volume
          configMap:
            name: argocd-metrics-server-configmap
```

### Créer le manifeste ConfigMap argocd-extension-metrics

```yaml title="manifests/metrics-server/configmap.yaml" linenums="1"
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-metrics-server-configmap
data:
  config.json: |
    {
      "prometheus": {
        "applications": [
          {
            "name": "default",
            "default": true,
            "dashboards": [
              {
                "groupKind": "pod",
                "tabs": ["Golden Signal", "Resource Usage", "Network", "Storage"],
                "rows": [
                  {
                    "name": "pod_cpu",
                    "title": "CPU Usage",
                    "tab": "Golden Signal",
                    "graphs": [
                      {
                        "name": "pod_cpu_line",
                        "title": "CPU Usage",
                        "description": "CPU usage by pod over time",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_cpu_usage_seconds_total{pod=~\"{{.name}}\", image!=\"\", container!=\"POD\", container!=\"\"}[5m])) by (pod)"
                      },
                      {
                        "name": "pod_cpu_pie",
                        "title": "CPU Distribution",
                        "description": "Average CPU distribution",
                        "graphType": "pie",
                        "metricName": "pod",
                        "queryExpression": "avg(rate(container_cpu_usage_seconds_total{pod=~\"{{.name}}\", container!=\"POD\", image!=\"\", container!=\"\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "pod_memory",
                    "title": "Memory Usage",
                    "tab": "Golden Signal",
                    "graphs": [
                      {
                        "name": "pod_memory_line",
                        "title": "Memory Usage",
                        "description": "Memory usage by pod over time",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(container_memory_usage_bytes{pod=~\"{{.name}}\", container!=\"POD\", image!=\"\", container!=\"\"}) by (pod)"
                      },
                      {
                        "name": "pod_memory_pie",
                        "title": "Memory Distribution",
                        "description": "Average memory distribution",
                        "graphType": "pie",
                        "metricName": "pod",
                        "queryExpression": "avg(container_memory_usage_bytes{pod=~\"{{.name}}\", container!=\"POD\", image!=\"\", container!=\"\"}) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "cpu_throttling",
                    "title": "CPU Throttling",
                    "tab": "Resource Usage",
                    "graphs": [
                      {
                        "name": "cpu_throttle_line",
                        "title": "CPU Throttling",
                        "description": "CPU throttling periods",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_cpu_cfs_throttled_periods_total{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "memory_working_set",
                    "title": "Memory Working Set",
                    "tab": "Resource Usage",
                    "graphs": [
                      {
                        "name": "memory_working_set_line",
                        "title": "Memory Working Set",
                        "description": "Active memory in use",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(container_memory_working_set_bytes{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "memory_cache",
                    "title": "Memory Cache",
                    "tab": "Resource Usage",
                    "graphs": [
                      {
                        "name": "memory_cache_line",
                        "title": "Memory Cache",
                        "description": "Cached memory",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(container_memory_cache{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "network_receive",
                    "title": "Network Receive",
                    "tab": "Network",
                    "graphs": [
                      {
                        "name": "network_receive_bytes",
                        "title": "Network Receive Bytes/sec",
                        "description": "Network bytes received per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_network_receive_bytes_total{pod=~\"{{.name}}\"}[5m])) by (pod)"
                      },
                      {
                        "name": "network_receive_packets",
                        "title": "Network Receive Packets/sec",
                        "description": "Network packets received per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_network_receive_packets_total{pod=~\"{{.name}}\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "network_transmit",
                    "title": "Network Transmit",
                    "tab": "Network",
                    "graphs": [
                      {
                        "name": "network_transmit_bytes",
                        "title": "Network Transmit Bytes/sec",
                        "description": "Network bytes transmitted per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_network_transmit_bytes_total{pod=~\"{{.name}}\"}[5m])) by (pod)"
                      },
                      {
                        "name": "network_transmit_packets",
                        "title": "Network Transmit Packets/sec",
                        "description": "Network packets transmitted per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_network_transmit_packets_total{pod=~\"{{.name}}\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "network_errors",
                    "title": "Network Errors",
                    "tab": "Network",
                    "graphs": [
                      {
                        "name": "network_receive_errors",
                        "title": "Network Receive Errors",
                        "description": "Network receive errors",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_network_receive_errors_total{pod=~\"{{.name}}\"}[5m])) by (pod)"
                      },
                      {
                        "name": "network_transmit_errors",
                        "title": "Network Transmit Errors",
                        "description": "Network transmit errors",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_network_transmit_errors_total{pod=~\"{{.name}}\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "fs_reads",
                    "title": "Filesystem Reads",
                    "tab": "Storage",
                    "graphs": [
                      {
                        "name": "fs_read_bytes",
                        "title": "Filesystem Read Bytes/sec",
                        "description": "Filesystem bytes read per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_fs_reads_bytes_total{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}[5m])) by (pod)"
                      },
                      {
                        "name": "fs_reads_total",
                        "title": "Filesystem Reads/sec",
                        "description": "Filesystem read operations per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_fs_reads_total{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "fs_writes",
                    "title": "Filesystem Writes",
                    "tab": "Storage",
                    "graphs": [
                      {
                        "name": "fs_write_bytes",
                        "title": "Filesystem Write Bytes/sec",
                        "description": "Filesystem bytes written per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_fs_writes_bytes_total{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}[5m])) by (pod)"
                      },
                      {
                        "name": "fs_writes_total",
                        "title": "Filesystem Writes/sec",
                        "description": "Filesystem write operations per second",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_fs_writes_total{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "fs_usage",
                    "title": "Filesystem Usage",
                    "tab": "Storage",
                    "graphs": [
                      {
                        "name": "fs_usage_bytes",
                        "title": "Filesystem Usage",
                        "description": "Filesystem space used",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(container_fs_usage_bytes{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}) by (pod)"
                      },
                      {
                        "name": "fs_limit_bytes",
                        "title": "Filesystem Limit",
                        "description": "Filesystem capacity",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(container_fs_limit_bytes{pod=~\"{{.name}}\", container!=\"POD\", container!=\"\"}) by (pod)"
                      }
                    ]
                  }
                ]
              },
              {
                "groupKind": "deployment",
                "tabs": ["Application Metrics", "Resource Usage"],
                "rows": [
                  {
                    "name": "http_latency",
                    "title": "HTTP Latency",
                    "tab": "Application Metrics",
                    "graphs": [
                      {
                        "name": "http_200_latency",
                        "title": "HTTP 200 Latency",
                        "description": "HTTP request latency for successful requests",
                        "graphType": "line",
                        "metricName": "pod_template_hash",
                        "queryExpression": "sum(rate(http_server_requests_seconds_sum{namespace=\"{{.namespace}}\", status=\"200\"}[1m])) by (pod_template_hash)"
                      }
                    ]
                  },
                  {
                    "name": "http_error_rate",
                    "title": "HTTP Error Rate",
                    "tab": "Application Metrics",
                    "graphs": [
                      {
                        "name": "http_error_rate_500",
                        "title": "HTTP 5xx Errors",
                        "description": "HTTP 5xx server errors",
                        "graphType": "line",
                        "metricName": "pod_template_hash",
                        "queryExpression": "sum(rate(http_server_requests_seconds_count{namespace=\"{{.namespace}}\", status=~\"5..\"}[1m])) by (pod_template_hash)"
                      },
                      {
                        "name": "http_error_rate_400",
                        "title": "HTTP 4xx Errors",
                        "description": "HTTP 4xx client errors",
                        "graphType": "line",
                        "metricName": "pod_template_hash",
                        "queryExpression": "sum(rate(http_server_requests_seconds_count{namespace=\"{{.namespace}}\", status=~\"4..\"}[1m])) by (pod_template_hash)"
                      }
                    ]
                  },
                  {
                    "name": "http_traffic",
                    "title": "HTTP Traffic",
                    "tab": "Application Metrics",
                    "graphs": [
                      {
                        "name": "http_traffic",
                        "title": "Request Rate",
                        "description": "HTTP requests per second",
                        "graphType": "line",
                        "metricName": "pod_template_hash",
                        "queryExpression": "sum(rate(http_server_requests_seconds_count{namespace=\"{{.namespace}}\"}[1m])) by (pod_template_hash)"
                      }
                    ]
                  },
                  {
                    "name": "deployment_cpu",
                    "title": "CPU Usage",
                    "tab": "Resource Usage",
                    "graphs": [
                      {
                        "name": "deployment_cpu_line",
                        "title": "CPU Usage",
                        "description": "CPU usage by deployment",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(rate(container_cpu_usage_seconds_total{namespace=\"{{.namespace}}\", pod=~\"{{.name}}.*\", image!=\"\", container!=\"POD\"}[5m])) by (pod)"
                      }
                    ]
                  },
                  {
                    "name": "deployment_memory",
                    "title": "Memory Usage",
                    "tab": "Resource Usage",
                    "graphs": [
                      {
                        "name": "deployment_memory_line",
                        "title": "Memory Usage",
                        "description": "Memory usage by deployment",
                        "graphType": "line",
                        "metricName": "pod",
                        "queryExpression": "sum(container_memory_usage_bytes{namespace=\"{{.namespace}}\", pod=~\"{{.name}}.*\", container!=\"POD\", container!=\"\"}) by (pod)"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ],
        "provider": {
          "name": "default",
          "default": true,
          "address": "http://kube-prometheus-stack-prometheus.monitoring.svc:9090"
        }
      }
    }
```

??? info "CHECK"
    
    Vous pouvez suivre le déploiement de Arocd-Extension-Metrics de deux manières:

    === "CLI"

        ```bash hl_lines="1" title="Vérifier le pod du serveur de métriques."
        kubectl get pods -n argocd -l app=argocd-metrics-server
        NAME                                     READY   STATUS    RESTARTS   AGE
        argocd-metrics-server-7bb9646784-cbvbg   1/1     Running   0          18h
        ```

        ```bash hl_lines="1" title="Vérifier les logs."
        kubectl logs -n argocd -l app=argocd-metrics-server
        pod deployment
        deployment deployment
        [GIN] 2025/12/10 - 19:34:27 | 200 |     638.948µs |       127.0.0.1 | GET      "/api/applications/argocd-metrics-server/groupkinds/deployment/rows/http_traffic/graphs/http_traffic?name=argocd-metrics-server.*&namespace=argocd&application_name=argocd-metrics-server&project=default&uid=28274042-5c9c-4a79-a390-8527e3ae67cb&duration=1h"
        [GIN] 2025/12/10 - 19:34:27 | 200 |     708.646µs |       127.0.0.1 | GET      "/api/applications/argocd-metrics-server/groupkinds/deployment/rows/http_error_rate/graphs/http_error_rate_400?name=argocd-metrics-server.*&namespace=argocd&application_name=argocd-metrics-server&project=default&uid=28274042-5c9c-4a79-a390-8527e3ae67cb&duration=1h"
        pod deployment
        deployment deployment
        pod deployment
        deployment deployment
        [GIN] 2025/12/10 - 19:34:31 | 200 |    1.073685ms |       127.0.0.1 | GET      "/api/applications/argocd-metrics-server/groupkinds/deployment/rows/deployment_memory/graphs/deployment_memory_line?name=argocd-metrics-server.*&namespace=argocd&application_name=argocd-metrics-server&project=default&uid=28274042-5c9c-4a79-a390-8527e3ae67cb&duration=1h"
        [GIN] 2025/12/10 - 19:34:31 | 200 |    1.045537ms |       127.0.0.1 | GET      "/api/applications/argocd-metrics-server/groupkinds/deployment/rows/deployment_cpu/graphs/deployment_cpu_line?name=argocd-metrics-server.*&namespace=argocd&application_name=argocd-metrics-server&project=default&uid=28274042-5c9c-4a79-a390-8527e3ae67cb&duration=1h"
        ```
        Appuyez sur `Ctrl+C` pour arrêter l'observation une fois que tous les pods sont en cours d'exécution.

    === "UI"

        1. Actualisez l'interface utilisateur d'Argo CD [https://localhost:8080](https://localhost:8080)
        2. Vous verrez l'application **podinfo**
        3. Cliquez dessus pour voir la progression du déploiement
        4. Attendez que l'état soit "Healthy" et "Synced"


## PodInfo
Déployons maintenant Podinfo via Argo CD.

### Créer le manifeste Application Podinfo
```yaml title="apps/podinfo.yaml" linenums="1"
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

??? info "CHECK"
    
    Vous pouvez suivre le déploiement de PodInfo de deux manières:

    === "CLI"

        ```bash hl_lines="1" title="Observer la synchronisation de l'application"
        kubectl get application podinfo -n argocd -w
        NAME                    SYNC STATUS   HEALTH STATUS
        podinfo                 Synced        Healthy
        ```

        ```bash hl_lines="1" title="Observer la création des pods dans le namespace podinfo"
        kubectl get pods -n podinfo -w
        NAME                       READY   STATUS    RESTARTS   AGE
        podinfo-86f68db776-68gc4   1/1     Running   0          14h
        podinfo-86f68db776-vwzjk   1/1     Running   0          14h
        ```
        Appuyez sur `Ctrl+C` pour arrêter l'observation une fois que tous les pods sont en cours d'exécution.

    === "UI"

        1. Actualisez l'interface utilisateur d'Argo CD [https://localhost:8080](https://localhost:8080)
        2. Vous verrez l'application **podinfo**
        3. Cliquez dessus pour voir la progression du déploiement
        4. Attendez que l'état soit "Healthy" et "Synced"

## Apply App-of-Apps

### 4. Deploy App of Apps (One Command!)

```bash
kubectl apply -f apps/app-of-apps.yaml
```

**That's it!** 🎉 Argo CD will now deploy everything:
- Prometheus
- Metrics Server
- Podinfo


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


### What We Accomplished

✅ **Single Bootstrap Step:** Only Argo CD was installed manually
✅ **Everything Else via GitOps:** Prometheus and Podinfo deployed through Argo CD
✅ **Declarative:** All configuration in YAML files
✅ **Observable:** Metrics visible directly in Argo CD UI
✅ **Self-Healing:** Argo CD auto-syncs and heals applications


✅ Centralized in Argo CD
✅ Visible in UI
✅ Auto-sync enabled
✅ Git as source of truth (if you commit these YAMLs)


### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Argo CD                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Prometheus  │  │    Metrics   │  │   Podinfo    │       │
│  │  Application │  │    Server    │  │  Application │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                 │              │
│         ▼                  │                 ▼              │
│  ┌──────────────┐          │         ┌──────────────┐       │
│  │  Prometheus  │◄─────────┘         │   Podinfo    │       │
│  │   (Helm)     │                    │     Pods     │       │
│  └──────────────┘                    └──────────────┘       │
│         │                                     │             │
│         │  (scrapes metrics)                  │             │
│         └─────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘

Argo CD UI Extension reads metrics from Metrics Server
Metrics Server queries Prometheus
Prometheus scrapes metrics from Podinfo pods


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


### Step 1: Create Your Git Repository

```bash
# Create repository directory
mkdir argocd-gitops
cd argocd-gitops

# Initialize Git
git init

# Create directory structure
mkdir -p bootstrap apps manifests/metrics-server

# Initialize Git repository
git add .
git commit -m "Initial structure"

# Push to your Git hosting (GitHub, GitLab, etc.)
git remote add origin https://github.com/YOUR-USERNAME/argocd-gitops.git
git push -u origin main
```


---

## How It Works

### The App of Apps Pattern

```
┌─────────────────────────────────────────────────────┐
│                   Root App                          │
│            (apps/app-of-apps.yaml)                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ├─── Manages ───► Prometheus App
                 │                 (apps/prometheus.yaml)
                 │
                 ├─── Manages ───► Metrics Server App
                 │                 (apps/metrics-server.yaml)
                 │
                 └─── Manages ───► Podinfo App
                                   (apps/podinfo.yaml)
```

**One application (root-app) manages all other applications!**

### Benefits

✅ **Single Source of Truth:** Everything in your Git repo
✅ **Version Control:** All changes tracked
✅ **Rollback:** Easy to revert via Git
✅ **No External Dependencies:** Won't break if external repos change
✅ **One Command Deployment:** `kubectl apply -f apps/app-of-apps.yaml`
✅ **GitOps Native:** Argo CD watches your repo for changes

---

## Making Changes

### Update Prometheus Configuration

1. Edit `apps/prometheus.yaml`
2. Commit and push:
   ```bash
   git add apps/prometheus.yaml
   git commit -m "Increase Prometheus retention to 24h"
   git push
   ```
3. Argo CD automatically syncs the changes!

### Add New Application

1. Create `apps/my-new-app.yaml`
2. Commit and push
3. The root-app will automatically deploy it!

### Update Metrics Configuration

1. Edit `manifests/metrics-server/configmap.yaml`
2. Commit and push
3. Argo CD syncs automatically

---

## Monitoring the Deployment

### Watch All Applications

```bash
# List all applications
kubectl get applications -n argocd

# Watch sync status
watch kubectl get applications -n argocd
```

### Check Specific Application

```bash
# View application details
kubectl describe application kube-prometheus-stack -n argocd

# View sync status in UI
# Click on the application in https://localhost:8080
```

### View Logs

```bash
# Root app logs
kubectl logs -n argocd deployment/argocd-application-controller -f

# Metrics server logs
kubectl logs -n argocd -l app=argocd-metrics-server -f
```

---

## Clean Up

### Remove Everything

```bash
# Delete root app (will delete all child apps)
kubectl delete application root-app -n argocd

# Delete Argo CD
helm uninstall argocd -n argocd

# Delete Kind cluster
kind delete cluster --name argocd-demo
```

---

## Advanced: Multi-Environment

You can extend this structure for multiple environments:

```
argocd-gitops/
├── apps/
│   ├── dev/
│   │   ├── app-of-apps.yaml
│   │   ├── prometheus.yaml
│   │   └── podinfo.yaml
│   ├── staging/
│   │   └── ...
│   └── prod/
│       └── ...
└── manifests/
    ├── base/
    │   └── metrics-server/
    └── overlays/
        ├── dev/
        ├── staging/
        └── prod/
```

---

## Summary

You now have:
✅ **Pure GitOps:** Everything in your own Git repository
✅ **App of Apps:** One command deploys everything
✅ **Official Sources:** Using official images and charts
✅ **Version Control:** All changes tracked
✅ **No Manual kubectl apply:** Argo CD handles everything
✅ **Production Ready:** Structure suitable for real deployments

**Next Steps:**
1. Customize the configurations for your needs
2. Add more applications
3. Set up CI/CD to update your repo
4. Add monitoring and alerting
5. Implement multi-environment support


## Deployment Steps

### 1. Create Your Git Repository

```bash
mkdir argocd-gitops
cd argocd-gitops
git init

# Create all directories
mkdir -p bootstrap apps manifests/metrics-server

# Create all files (copy content from above)
# Then commit and push
git add .
git commit -m "Initial GitOps structure"
git remote add origin https://github.com/YOUR-USERNAME/argocd-gitops.git
git push -u origin main
```


## Verification

### Check All Applications

```bash
# List all applications
kubectl get applications -n argocd

# Expected output:
# NAME                     SYNC STATUS   HEALTH STATUS
# root-app                 Synced        Healthy
# kube-prometheus-stack    Synced        Healthy
# argocd-metrics-server    Synced        Healthy
# podinfo                  Synced        Healthy
```

### View in Argo CD UI

In the UI, you should see 4 applications:
1. **root-app** - The App of Apps
2. **kube-prometheus-stack** - Monitoring stack
3. **argocd-metrics-server** - Metrics backend
4. **podinfo** - Demo application

### Test Metrics

1. Click on **podinfo** application
2. Click on the **podinfo Deployment**
3. Click on the **Metrics** tab
4. You should see CPU, Memory, and Network graphs

---

## Making Changes

### Update Prometheus Configuration

1. Edit `apps/prometheus.yaml` in your repo
2. Change retention or resources
3. Commit and push:
   ```bash
   git add apps/prometheus.yaml
   git commit -m "Update Prometheus retention to 24h"
   git push
   ```
4. Argo CD auto-syncs the changes!

### Add Custom Metrics

1. Edit `manifests/metrics-server/configmap.yaml`
2. Add your custom Prometheus queries
3. Commit and push
4. Metrics server automatically reloads

### Add New Application

1. Create `apps/my-app.yaml`
2. Commit and push
3. The root-app automatically deploys it!

## Troubleshooting

### Metrics Tab Not Showing

**Check extension is loaded:**
```bash
kubectl logs -n argocd deployment/argocd-server | grep extension
```

**Verify proxy extension enabled:**
```bash
kubectl get configmap argocd-cm -n argocd -o yaml | grep proxy
```

### Metrics Server Issues

**Check logs:**
```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-metrics-server
```

**Verify ConfigMap:**
```bash
kubectl get configmap argocd-metrics-server -n argocd -o yaml
```

**Test Prometheus connectivity:**
```bash
kubectl exec -n argocd deployment/argocd-metrics-server -- \
  wget -O- http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090/api/v1/query?query=up
```

### Application Not Syncing

**Check application status:**
```bash
kubectl describe application <app-name> -n argocd
```

**Force sync:**
```bash
kubectl patch application <app-name> -n argocd \
  --type merge -p '{"operation":{"sync":{}}}'
```


## Clean Up

### Delete Everything

```bash
# Delete root app (removes all child apps)
kubectl delete application root-app -n argocd

# Delete Argo CD
helm uninstall argocd -n argocd

# Delete Kind cluster
kind delete cluster --name argocd-demo
```

---

## Summary

You now have:
- ✅ **Pure GitOps:** Everything in your Git repository
- ✅ **App of Apps:** One command deploys everything
- ✅ **Official Sources:** Using official manifests and images
- ✅ **Metrics Integration:** Prometheus metrics in Argo CD UI
- ✅ **Production Ready:** Suitable for real deployments

**Key Benefits:**
- All changes tracked in Git
- Easy rollback via `git revert`
- No manual `kubectl apply` needed
- Argo CD handles everything automatically
- Complete audit trail

**Changes from official:**
- ✅ Added Service definition (needed for Argo CD to reach the server)
- ✅ Pinned image version to `v1.0.3` (instead of `:latest` for reproducibility)
- ✅ Added serviceAccountName: `argocd-server`
- ✅ Added security context (runAsUser: 999, readOnlyRootFilesystem, etc.)
- ✅ Added resource limits
- ✅ Added proper labels for Argo CD
- ✅ Kept the official volume mount: `/app/config.json` with `subPath`