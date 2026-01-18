---
title: "Stop Paying for Expensive Logging: Self-Hosted ClickHouse on Kubernetes"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://faun.pub/stop-paying-for-expensive-logging-self-hosted-clickhouse-on-kubernetes-c6c3d757b2c9
author:
  - "[[Vamsi Jakkula]]"
---
<!-- more -->

[Sitemap](https://faun.pub/sitemap/sitemap.xml)## [FAUN.dev() 🐾](https://faun.pub/?source=post_page---publication_nav-10d1a7495d39-c6c3d757b2c9---------------------------------------)

[![FAUN.dev() 🐾](https://miro.medium.com/v2/resize:fill:76:76/1*af3uHdSUsv_rXFEufcyTqA.png)](https://faun.pub/?source=post_page---post_publication_sidebar-10d1a7495d39-c6c3d757b2c9---------------------------------------)

We help developers learn and grow by keeping them up with what matters. 👉 [www.faun.dev](http://www.faun.dev/)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*HaDO2avqK5Xwvhn_1ihkxA.jpeg)

Image by Tumisu from Pixabay

C entralized logging is crucial for understanding application behavior in Kubernetes, but the cost of storing those logs can quickly spiral out of control. **ClickHouse** is changing that narrative. It provides a high-performance, cost-effective alternative to traditional logging stacks, delivering lightning-fast query speeds that significantly reduces your infrastructure overhead.

In this blog post, we’re going to build a high-performance logging pipeline from the ground up. Let’s look at how to:

- **Deploy ClickHouse on Minikube** for lightning-fast, cost-effective log storage
- Harness the power of **Fluent Bit**, the industry-standard, lightweight log processor designed to handle high-throughput Kubernetes telemetry with minimal CPU overhead
- **Integrate Grafana** to visualize your logs in real-time

## Why ClickHouse for Logs?

Before we dive in, let’s understand why ClickHouse is excellent for logging:

- **Speed**: Queries on billions of rows in seconds
- **Compression**: 10–100x compression ratios
- **Cost-Effective**: Lower storage and compute costs
- **SQL Interface**: No need to learn new query languages
- **Scalability**: Handles petabytes of data

Let’s dive into the setup of ClickHouse on Minikube

### Step-1: Setting up Minikube

```rb
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Step-2: Deploy ClickHouse

```rb
kubectl create namespace clickhouse

helm repo add clickhouse-operator https://docs.altinity.com/clickhouse-operator/
helm repo update

helm install clickhouse-operator clickhouse-operator/altinity-clickhouse-operator \
  --namespace clickhouse

<clickhouse-instance.yaml>

apiVersion: clickhouse.altinity.com/v1
kind: ClickHouseInstallation
metadata:
  name: clickhouse
  namespace: clickhouse
spec:
  configuration:
    users:
      default/password: "changeme"
      default/networks/ip:
        - "::/0"
    clusters:
      - name: default
        layout:
          shardsCount: 1
          replicasCount: 1
  defaults:
    templates:
      podTemplate: clickhouse-pod
      dataVolumeClaimTemplate: data-volume
  templates:
    podTemplates:
      - name: clickhouse-pod
        spec:
          containers:
            - name: clickhouse
              image: clickhouse/clickhouse-server:23.8
              ports:
                - name: http
                  containerPort: 8123
                - name: tcp
                  containerPort: 9000
    volumeClaimTemplates:
      - name: data-volume
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 10Gi

kubectl apply -f clickhouse-instance.yaml

qvamjak% kubectl get pods -n clickhouse

NAME                                                              READY   STATUS    RESTARTS   AGE
chi-clickhouse-default-0-0-0                                      2/2     Running   0          6h34m
clickhouse-operator-altinity-clickhouse-operator-6bcb844b765srr   2/2     Running   0          6h41m
```

### Step-3: Deploy Log Generator App

```rb
apiVersion: v1
kind: Namespace
metadata:
  name: demo-app
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: log-generator
  namespace: demo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: log-generator
  template:
    metadata:
      labels:
        app: log-generator
    spec:
      containers:
      - name: log-generator
        image: busybox
        command: ["/bin/sh"]
        args:
          - -c
          - |
            i=0
            while true; do
              i=$((i+1))
              # Generate structured JSON logs
              echo "{\"level\":\"info\",\"message\":\"Processing request $i\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",\"request_id\":\"req-$i\",\"duration_ms\":$((RANDOM % 1000))}"
              
              # Occasionally generate errors
              if [ $((i % 20)) -eq 0 ]; then
                echo "{\"level\":\"error\",\"message\":\"Failed to process request\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",\"request_id\":\"req-$i\",\"error\":\"Connection timeout\"}"
              fi
              
              sleep 3
            done
```

### Step-4: Deploy Fluentbit

```rb
apiVersion: v1
kind: Namespace
metadata:
  name: logging
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluent-bit
  namespace: logging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluent-bit
rules:
- apiGroups: [""]
  resources:
  - namespaces
  - pods
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fluent-bit
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: fluent-bit
subjects:
- kind: ServiceAccount
  name: fluent-bit
  namespace: logging
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: logging
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Daemon       Off
        Log_Level    info
        Parsers_File parsers.conf

    [INPUT]
        Name              tail
        Path              /var/log/containers/*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5
        Mem_Buf_Limit     5MB
        Skip_Long_Lines   On

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Kube_Tag_Prefix     kube.var.log.containers.
        Merge_Log           Off
        Keep_Log            On

    [FILTER]
        Name                nest
        Match               kube.*
        Operation           lift
        Nested_under        kubernetes
        Add_prefix          kubernetes_

    [FILTER]
        Name                modify
        Match               kube.*
        Rename              kubernetes_pod_name pod
        Rename              kubernetes_namespace_name namespace
        Rename              kubernetes_container_name container
        Rename              log log_message

    [OUTPUT]
        Name                 http
        Match                *
        Host                 clickhouse-clickhouse.clickhouse.svc.cluster.local
        Port                 8123
        URI                  /?query=INSERT%20INTO%20logs.application_logs%20FORMAT%20JSONEachRow
        Format               json_lines
        http_User            default
        http_Passwd          changeme
        Retry_Limit          2

  parsers.conf: |
    [PARSER]
        Name   docker
        Format json
        Time_Key time
        Time_Format %Y-%m-%dT%H:%M:%S.%L%z
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
  labels:
    app: fluent-bit
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      serviceAccountName: fluent-bit
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:2.1
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 100Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: fluent-bit-config
          mountPath: /fluent-bit/etc/
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: fluent-bit-config
        configMap:
          name: fluent-bit-config
```

### Step-5: Create Table in ClickHouse & Verify the logs

```rb
kubectl exec -n clickhouse chi-clickhouse-default-0-0-0 -- clickhouse-client --password changeme --query "
CREATE TABLE logs.application_logs
(
    timestamp DateTime DEFAULT now(),
    namespace String DEFAULT '',
    pod String DEFAULT '',
    container String DEFAULT '',
    log_message String DEFAULT '',
    stream String DEFAULT ''
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, namespace, pod)
"

Check Logs
++++++++++++++++

qvamjak% kubectl exec -n clickhouse chi-clickhouse-default-0-0-0 -- clickhouse-client --password changeme --query "
SELECT 
    timestamp,
    namespace,
    pod,
    log_message
FROM logs.application_logs 
ORDER BY timestamp DESC 
LIMIT 10
" --format=PrettyCompact
Defaulted container "clickhouse" out of: clickhouse, clickhouse-log
┌───────────timestamp─┬─namespace─┬─pod──────────────┬─log_message─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2025-12-24 16:07:04 │ logging   │ fluent-bit-58l57 │ [2025/12/24 16:06:59] [ info] [output:http:http.0] clickhouse-clickhouse.clickhouse.svc.cluster.local:8123, HTTP status=200
 │
│ 2025-12-24 16:07:04 │ logging   │ fluent-bit-58l57 │ [2025/12/24 16:06:59] [ info] [output:http:http.0] clickhouse-clickhouse.clickhouse.svc.cluster.local:8123, HTTP status=200
 │
│ 2025-12-24 16:07:04 │ logging   │ fluent-bit-58l57 │ [2025/12/24 16:06:59] [ info] [output:http:http.0] clickhouse-clickhouse.clickhouse.svc.cluster.local:8123, HTTP status=200
 │
│ 2025-12-24 16:07:04 │ logging   │ fluent-bit-58l57 │ [2025/12/24 16:06:59] [ info] [output:http:http.0] clickhouse-clickhouse.clickhouse.svc.cluster.local:8123, HTTP status=200
 │
│ 2025-12-24 16:07:04 │ logging   │ fluent-bit-58l57 │ [2025/12/24 16:06:59] [ info] [output:http:http.0] clickhouse-clickhouse.clickhouse.svc.cluster.local:8123, HTTP status=200
 │
│ 2025-12-24 16:07:04 │ logging   │ fluent-bit-58l57 │ [2025/12/24 16:06:59] [ info] [output:http:http.0] clickhouse-clickhouse.clickhouse.svc.cluster.local:8123, HTTP status=200
 │
└─────────────────────┴───────────┴──────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌───────────timestamp─┬─namespace───┬─pod─────────────────┬─log_message───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2025-12-24 16:07:04 │ kube-system │ storage-provisioner │ W1224 16:07:02.874294       1 warnings.go:70] v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
 │
│ 2025-12-24 16:07:04 │ kube-system │ storage-provisioner │ W1224 16:07:02.856919       1 warnings.go:70] v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
 │
│ 2025-12-24 16:07:04 │ kube-system │ storage-provisioner │ W1224 16:07:00.854029       1 warnings.go:70] v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
 │
│ 2025-12-24 16:07:04 │ kube-system │ storage-provisioner │ W1224 16:07:00.841958       1 warnings.go:70] v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
 │
└─────────────────────┴─────────────┴─────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
qvamjak%
```

### Step-6: Setup Grafana

```rb
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: GF_SECURITY_ADMIN_USER
          value: admin
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: admin
        - name: GF_INSTALL_PLUGINS
          value: grafana-clickhouse-datasource
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
      volumes:
      - name: grafana-storage
        persistentVolumeClaim:
          claimName: grafana-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  type: NodePort
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30300
  selector:
    app: grafana
```

### Step-7: Configure ClickHouse Datasource and Visualize with SQL

```rb
Configure ClickHouse Data Source

Click ☰ menu → Connections → Data sources
Click Add data source
Search for ClickHouse and select it
Configure:

Name: ClickHouse Logs
Server Address: clickhouse-clickhouse.clickhouse.svc.cluster.local
Server Port: 9000
Protocol: Native
Username: default
Password: xxxxxx
Default Database: logs

Click Save & Test

In Grafana Explorer use the following query 
+++++++++++++++++++++++++++++++++++++++++++

SELECT 
    timestamp as time,
    concat('[', pod, '] ', log_message) as line
FROM logs.application_logs
WHERE namespace = 'demo-app'
  AND timestamp > now() - INTERVAL 10 MINUTE
ORDER BY timestamp DESC
LIMIT 500
```

We can see real time logs in Grafana as shown in the screenshot

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*WEXI4MKjVzgVmHRrslTxlQ.png)

No more paying premium prices for third-party logging services. By self-hosting **ClickHouse on Kubernetes**, you take full control of your observability stack — achieving enterprise-grade performance on infrastructure you own and operate. From seamlessly collecting logs across your cluster with Fluent Bit to visualizing them in real-time through Grafana, high-performance logging has never been more accessible or affordable.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*QDkVCfJNmECTBq8g.png)

### 👋 If you find this helpful, please click the clap 👏 button below a few times to show your support for the author 👇

### 🚀Join FAUN.dev() & get similar stories in your inbox each week for free!

[![FAUN.dev() 🐾](https://miro.medium.com/v2/resize:fill:96:96/1*af3uHdSUsv_rXFEufcyTqA.png)](https://faun.pub/?source=post_page---post_publication_info--c6c3d757b2c9---------------------------------------)

[![FAUN.dev() 🐾](https://miro.medium.com/v2/resize:fill:128:128/1*af3uHdSUsv_rXFEufcyTqA.png)](https://faun.pub/?source=post_page---post_publication_info--c6c3d757b2c9---------------------------------------)

[Last published Dec 31, 2025](https://faun.pub/getting-started-with-amazon-bedrock-cli-api-simple-llm-inference-and-model-selection-1927b4826e2f?source=post_page---post_publication_info--c6c3d757b2c9---------------------------------------)

We help developers learn and grow by keeping them up with what matters. 👉 [www.faun.dev](http://www.faun.dev/)

## More from Vamsi Jakkula and FAUN.dev() 🐾

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--c6c3d757b2c9---------------------------------------)