---
title: Overview du chart
status: draft
sources:
  - https://notes.kodekloud.com/docs/Prep-Course-Prometheus-Certified-Associate-PCA-Certification/Monitoring-Kubernetes/Prometheus-Chart-Overview/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/prometheus-certified-associate-pca/module/bb958f66-38c3-41ed-ae2f-7a4ee96c4d66/lesson/cabca690-195e-4e68-8785-938fd09a887b
---

> Cette page explique l'organisation des ressources Kubernetes après l'installation du chart Helm Prometheus, en détaillant les StatefulSets, Deployments, DaemonSets et Services.

Vous découvrirez pour chaque composant une explication détaillée, accompagnée de commandes et d'extraits de configuration pour mieux comprendre leur rôle.

## Lister toutes les ressources

Commencez par exécuter la commande suivante pour lister toutes les ressources créées par le chart Helm:

```bash hl_lines="1"
kubectl get all
NAME                                                         READY   STATUS    RESTARTS   AGE
pod/alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          9h
pod/prometheus-grafana-64b4d64c54-2hjj8                      3/3     Running   0          9h
pod/prometheus-kube-prometheus-operator-84d5cd6bfd-lpnxb     1/1     Running   0          9h
pod/prometheus-kube-state-metrics-67cf98b59f-6nrv7           1/1     Running   0          9h
pod/prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          9h
pod/prometheus-prometheus-node-exporter-6b5mn                1/1     Running   0          9h

NAME                                              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
service/alertmanager-operated                     ClusterIP   None            <none>        9093/TCP,9094/TCP,9094/UDP   9h
service/kubernetes                                ClusterIP   10.96.0.1       <none>        443/TCP                      9h
service/prometheus-grafana                        ClusterIP   10.96.83.197    <none>        80/TCP                       9h
service/prometheus-kube-prometheus-alertmanager   ClusterIP   10.96.183.143   <none>        9093/TCP,8080/TCP            9h
service/prometheus-kube-prometheus-operator       ClusterIP   10.96.55.122    <none>        443/TCP                      9h
service/prometheus-kube-prometheus-prometheus     ClusterIP   10.96.37.225    <none>        9090/TCP,8080/TCP            9h
service/prometheus-kube-state-metrics             ClusterIP   10.96.107.10    <none>        8080/TCP                     9h
service/prometheus-operated                       ClusterIP   None            <none>        9090/TCP                     9h
service/prometheus-prometheus-node-exporter       ClusterIP   10.96.104.136   <none>        9100/TCP                     9h

NAME                                                 DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
daemonset.apps/prometheus-prometheus-node-exporter   1         1         1       1            1           kubernetes.io/os=linux   9h

NAME                                                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/prometheus-grafana                    1/1     1            1           9h
deployment.apps/prometheus-kube-prometheus-operator   1/1     1            1           9h
deployment.apps/prometheus-kube-state-metrics         1/1     1            1           9h

NAME                                                             DESIRED   CURRENT   READY   AGE
replicaset.apps/prometheus-grafana-64b4d64c54                    1         1         1       9h
replicaset.apps/prometheus-kube-prometheus-operator-84d5cd6bfd   1         1         1       9h
replicaset.apps/prometheus-kube-state-metrics-67cf98b59f         1         1         1       9h

NAME                                                                    READY   AGE
statefulset.apps/alertmanager-prometheus-kube-prometheus-alertmanager   1/1     9h
statefulset.apps/prometheus-prometheus-kube-prometheus-prometheus       1/1     9h
```

### StatefulSets

- **StatefulSet Prometheus** : Ce StatefulSet crée l'instance du serveur Prometheus. Bien que le nom soit long, il représente l'instance Prometheus elle-même. Se connecter à Prometheus revient à se connecter au conteneur s'exécutant dans ce StatefulSet.
- **StatefulSet Alertmanager** : Ce StatefulSet est responsable de l'exécution d'Alertmanager, qui gère les notifications d'alertes.

### Deployments

- **Deployment Prometheus Grafana:** Grafana est l'outil d'interface graphique permettant de visualiser les données issues de Prometheus. Il est automatiquement déployé et configuré via le chart Helm.
- **Deployment Kube Prometheus Operator:** L'opérateur Prometheus gère le cycle de vie de l'instance Prometheus, notamment les mises à jour de configuration et les redémarrages si nécessaire.
- **Deployment Kube-state-metrics:** Ce déploiement exécute un conteneur qui collecte des métriques sur les objets Kubernetes (par exemple les deployments, services et pods).

Les ReplicaSets correspondant à ces deployments sont également présents et garantissent que le bon nombre de réplicas de pods est maintenu.

### DaemonSet

- **Node Exporter:** Cette ressource déploie un pod Node Exporter sur chaque nœud du cluster, y compris les nœuds ajoutés ultérieurement. Le Node Exporter collecte des métriques au niveau de l'hôte telles que l'utilisation du CPU, la consommation mémoire et les informations sur le système de fichiers. Par exemple, si votre cluster comporte deux nœuds (vérifiable avec `kubectl get nodes`), vous verrez deux pods Node Exporter prêts.

### Pods and Services

La section Pods liste tous les pods déployés, notamment:

- Le pod du serveur Prometheus
- Le pod Alertmanager
- Le pod Grafana
- Le pod Prometheus Operator
- Le pod kube-state-metrics
- Le pods Node Exporter

!!! note "Services"
    La section Services expose ces pods en tant que services ClusterIP, ce qui signifie qu'ils sont accessibles uniquement à l'intérieur du cluster. Pour exposer le serveur Prometheus ou Grafana en dehors du cluster, il faudrait configurer un ingress, un load balancer ou un proxy.

## Inspecter la configuration du serveur Prometheus

Pour afficher la configuration du StatefulSet du serveur Prometheus, exécutez:

```bash hl_lines="1"
kubectl describe statefulset prometheus-prometheus-kube-prometheus-prometheus
Name:               prometheus-prometheus-kube-prometheus-prometheus
Namespace:          default
CreationTimestamp:  Tue, 17 Mar 2026 07:28:53 +0100
Selector:           app.kubernetes.io/instance=prometheus-kube-prometheus-prometheus,app.kubernetes.io/managed-by=prometheus-operator,app.kubernetes.io/name=prometheus,operator.prometheus.io/name=prometheus-kube-prometheus-prometheus,operator.prometheus.io/shard=0,prometheus=prometheus-kube-prometheus-prometheus
Labels:             app=kube-prometheus-stack-prometheus
                    app.kubernetes.io/instance=prometheus-kube-prometheus-prometheus
                    app.kubernetes.io/managed-by=prometheus-operator
                    app.kubernetes.io/name=prometheus
                    app.kubernetes.io/part-of=kube-prometheus-stack
                    app.kubernetes.io/version=82.10.5
                    chart=kube-prometheus-stack-82.10.5
                    heritage=Helm
                    managed-by=prometheus-operator
                    operator.prometheus.io/mode=server
                    operator.prometheus.io/name=prometheus-kube-prometheus-prometheus
                    operator.prometheus.io/shard=0
                    prometheus=prometheus-kube-prometheus-prometheus
                    release=prometheus
Annotations:        meta.helm.sh/release-name: prometheus
                    meta.helm.sh/release-namespace: default
                    prometheus-operator-input-hash: 11260676124905552650
Replicas:           1 desired | 1 total
Update Strategy:    RollingUpdate
Pods Status:        1 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:           app.kubernetes.io/instance=prometheus-kube-prometheus-prometheus
                    app.kubernetes.io/managed-by=prometheus-operator
                    app.kubernetes.io/name=prometheus
                    app.kubernetes.io/version=3.10.0
                    operator.prometheus.io/name=prometheus-kube-prometheus-prometheus
                    operator.prometheus.io/shard=0
                    prometheus=prometheus-kube-prometheus-prometheus
  Annotations:      kubectl.kubernetes.io/default-container: prometheus
  Service Account:  prometheus-kube-prometheus-prometheus
  Init Containers:
   init-config-reloader:
    Image:      quay.io/prometheus-operator/prometheus-config-reloader:v0.89.0
    Port:       8081/TCP (reloader-init)
    Host Port:  0/TCP (reloader-init)
    Command:
      /bin/prometheus-config-reloader
    Args:
      --watch-interval=0
      --listen-address=:8081
      --config-file=/etc/prometheus/config/prometheus.yaml.gz
      --config-envsubst-file=/etc/prometheus/config_out/prometheus.env.yaml
      --watched-dir=/etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0
      --watched-dir=/etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1
      --watched-dir=/etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2
    Environment:
      POD_NAME:   (v1:metadata.name)
      SHARD:     0
    Mounts:
      /etc/prometheus/config from config (rw)
      /etc/prometheus/config_out from config-out (rw)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0 (rw)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1 (rw)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2 (rw)
  Containers:
   prometheus:
    Image:      quay.io/prometheus/prometheus:v3.10.0
    Port:       9090/TCP (http-web)
    Host Port:  0/TCP (http-web)
    Args:
      --config.file=/etc/prometheus/config_out/prometheus.env.yaml
      --web.enable-lifecycle
      --web.external-url=http://prometheus-kube-prometheus-prometheus.default:9090
      --web.route-prefix=/
      --storage.tsdb.retention.time=10d
      --storage.tsdb.path=/prometheus
      --storage.tsdb.wal-compression
      --web.config.file=/etc/prometheus/web_config/web-config.yaml
    Liveness:     http-get http://:http-web/-/healthy delay=0s timeout=3s period=5s #success=1 #failure=6
    Readiness:    http-get http://:http-web/-/ready delay=0s timeout=3s period=5s #success=1 #failure=3
    Startup:      http-get http://:http-web/-/ready delay=0s timeout=3s period=15s #success=1 #failure=60
    Environment:  <none>
    Mounts:
      /etc/prometheus/certs from tls-assets (ro)
      /etc/prometheus/config_out from config-out (ro)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0 (ro)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1 (ro)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2 (ro)
      /etc/prometheus/web_config/web-config.yaml from web-config (ro,path="web-config.yaml")
      /prometheus from prometheus-prometheus-kube-prometheus-prometheus-db (rw)
   config-reloader:
    Image:      quay.io/prometheus-operator/prometheus-config-reloader:v0.89.0
    Port:       8080/TCP (reloader-web)
    Host Port:  0/TCP (reloader-web)
    Command:
      /bin/prometheus-config-reloader
    Args:
      --listen-address=:8080
      --reload-url=http://127.0.0.1:9090/-/reload
      --config-file=/etc/prometheus/config/prometheus.yaml.gz
      --config-envsubst-file=/etc/prometheus/config_out/prometheus.env.yaml
      --watched-dir=/etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0
      --watched-dir=/etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1
      --watched-dir=/etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2
    Environment:
      POD_NAME:   (v1:metadata.name)
      SHARD:     0
    Mounts:
      /etc/prometheus/config from config (rw)
      /etc/prometheus/config_out from config-out (rw)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0 (rw)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1 (rw)
      /etc/prometheus/rules/prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2 from prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2 (rw)
  Volumes:
   config:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  prometheus-prometheus-kube-prometheus-prometheus
    Optional:    false
   tls-assets:
    Type:        Projected (a volume that contains injected data from multiple sources)
    SecretName:  prometheus-prometheus-kube-prometheus-prometheus-tls-assets-0
    Optional:    false
   config-out:
    Type:       EmptyDir (a temporary directory that shares a pod's lifetime)
    Medium:     Memory
    SizeLimit:  <unset>
   prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0:
    Type:      ConfigMap (a volume populated by a ConfigMap)
    Name:      prometheus-prometheus-kube-prometheus-prometheus-rulefiles-0
    Optional:  true
   prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1:
    Type:      ConfigMap (a volume populated by a ConfigMap)
    Name:      prometheus-prometheus-kube-prometheus-prometheus-rulefiles-1
    Optional:  true
   prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2:
    Type:      ConfigMap (a volume populated by a ConfigMap)
    Name:      prometheus-prometheus-kube-prometheus-prometheus-rulefiles-2
    Optional:  true
   web-config:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  prometheus-prometheus-kube-prometheus-prometheus-web-config
    Optional:    false
   prometheus-prometheus-kube-prometheus-prometheus-db:
    Type:          EmptyDir (a temporary directory that shares a pod's lifetime)
    Medium:
    SizeLimit:     <unset>
  Node-Selectors:  <none>
  Tolerations:     <none>
Volume Claims:     <none>
Events:            <none>
```

La sortie contient des informations détaillées, notamment les arguments du conteneur, les variables d'environnement, les montages et les probes.

### Key Sections in the Prometheus Container Configuration

- **Container Arguments:**

    - `--web.console.templates` and `--web.console.libraries` paths
    - Retention time using `--storage.tsdb.retention.time=10d`
    - Path to configuration files and storage directories
    - Liveness, readiness, and startup endpoints

- **Volume Mounts:**

    - `/etc/prometheus/certs`: Mounted from a secret for TLS assets.
    - `/etc/prometheus/config_out`: Mounted as read-only for configuration output.
    - `/prometheus`: Mounted for Prometheus TSDB (Time Series Database) storage.

!!! tip 
    To capture the complete configuration, pipe the output to a file:

    ```bash hl_lines="1"
    kubectl describe statefulset prometheus-prometheus-kube-prometheus-prometheus > prometheus.yaml
    ```

## Configuring the Init Container

Within the `prometheus.yaml` file, locate the configuration for the init container named `init-config-reloader`. This container uses the Prometheus config reloader image and is responsible for generating the initial Prometheus configuration before the main container starts. A snippet of its configuration is as follows:

```yaml
init-config-reloader:
  Image: quay.io/prometheus-operator/prometheus-config-reloader:v0.60.1
  Port: 8080/TCP
  Host Port: 0/TCP
  Command:
    - /bin/prometheus-config-reloader
  Args:
    - --watch-interval=0
    - --listen-address=:8080
    - --config-file=/etc/prometheus/config/prometheus.yaml.gz
    - --config-envsubst-file=/etc/prometheus/config_out/prometheus.env.yaml
    - --watched-dir=/etc/prometheus/rules/
    - prometheus-prometheus-kube-prometheus-rulefiles-0
  Limits:
    cpu: 200m
    memory: 50Mi
  Requests:
    cpu: 200m
```

Below this section, you will find the main Prometheus container configuration.

## The Main Prometheus Container

The main container is configured with the following snippet:

```yaml
prometheus:
  Image: quay.io/prometheus/prometheus:v2.39.1
  Port: 9090/TCP
  Host Port: 0/TCP
  Args:
    - --web.console.templates=/etc/prometheus/consoles
    - --web.console.libraries=/etc/prometheus/console_libraries
    - --storage.tsdb.retention.time=10d
    - --config.file=/etc/prometheus/config_out/prometheus.env.yaml
    - --storage.tsdb.path=/prometheus
    - --web.enable-lifecycle
    - --web.external-url=http://prometheus-kube-prometheus-prometheus.default:9090
    - --web.route-prefix=/
    - --storage.tsdb.wal-compression
```

These arguments define paths for console templates, configuration files, and the data storage directory.

Additional mounted volumes in the Prometheus container include:

* A volume named `config`, containing the Prometheus configuration from a Secret.
* A volume for rules retrieved from a ConfigMap.
* Volumes such as `tls-assets` (for TLS certificates) and `config-out`.

## Inspecting the Prometheus Secret

To examine the secret that holds the Prometheus configuration, execute:

```bash hl_lines="1"
kubectl describe secret prometheus-prometheus-kube-prometheus-prometheus
Name:         prometheus-prometheus-kube-prometheus-prometheus
Namespace:    default
Labels:       app.kubernetes.io/managed-by=prometheus-operator
              managed-by=prometheus-operator
Annotations:  <none>

Type:  Opaque

Data
====
prometheus.yaml.gz:  2159 bytes
```

A sample output shows that the secret contains a compressed configuration file (`prometheus.yaml.gz`):

## Examining the ConfigMap for Prometheus Rule Files

You can also inspect the ConfigMap that stores Prometheus rule files. After retrieving the ConfigMap details, you might find a rule file snippet defining recording rules and alert expressions. For example:

```yaml
record: namespace_cpu:kube_pod_container_resource_limits:sum
expr: |
  max by (cluster, namespace, workload, pod) (
    label_replace(
      label_replace(
        kube_pod_owner(job="kube-state-metrics", owner_kind="ReplicaSet*"),
        "replicaset", "$1", "owner_name", "(.*)"
      ) on(replicaset, namespace) group_left(owner_name) topk by(replicaset, namespace) (
        kube_replicaset_owner(job="kube-state-metrics")
      )
    )
  )
labels:
  workload_type: deployment
```

The Prometheus Operator simplifies the management of these configurations by using Kubernetes manifests instead of directly modifying YAML files.

## Reviewing the Prometheus Operator Configuration

To inspect the Prometheus Operator Deployment, run:

```bash hl_lines="1"
kubectl get deployment
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
prometheus-grafana                    1/1     1            1           10h
prometheus-kube-prometheus-operator   1/1     1            1           10h
prometheus-kube-state-metrics         1/1     1            1           10h
```

You will see entries for Prometheus Grafana, the Prometheus Operator, and kube-state-metrics. Then, describe the operator deployment:

```bash hl_lines="1 41-67" linenums="1"
kubectl get deployment
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
prometheus-grafana                    1/1     1            1           10h
prometheus-kube-prometheus-operator   1/1     1            1           10h
prometheus-kube-state-metrics         1/1     1            1           10h
❯ kubectl describe deployment prometheus-kube-prometheus-operator
Name:                   prometheus-kube-prometheus-operator
Namespace:              default
CreationTimestamp:      Tue, 17 Mar 2026 07:28:47 +0100
Labels:                 app=kube-prometheus-stack-operator
                        app.kubernetes.io/component=prometheus-operator
                        app.kubernetes.io/instance=prometheus
                        app.kubernetes.io/managed-by=Helm
                        app.kubernetes.io/name=kube-prometheus-stack-prometheus-operator
                        app.kubernetes.io/part-of=kube-prometheus-stack
                        app.kubernetes.io/version=82.10.5
                        chart=kube-prometheus-stack-82.10.5
                        heritage=Helm
                        release=prometheus
Annotations:            deployment.kubernetes.io/revision: 1
                        meta.helm.sh/release-name: prometheus
                        meta.helm.sh/release-namespace: default
Selector:               app=kube-prometheus-stack-operator,release=prometheus
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:           app=kube-prometheus-stack-operator
                    app.kubernetes.io/component=prometheus-operator
                    app.kubernetes.io/instance=prometheus
                    app.kubernetes.io/managed-by=Helm
                    app.kubernetes.io/name=kube-prometheus-stack-prometheus-operator
                    app.kubernetes.io/part-of=kube-prometheus-stack
                    app.kubernetes.io/version=82.10.5
                    chart=kube-prometheus-stack-82.10.5
                    heritage=Helm
                    release=prometheus
  Service Account:  prometheus-kube-prometheus-operator
  Containers:
   kube-prometheus-stack:
    Image:      quay.io/prometheus-operator/prometheus-operator:v0.89.0
    Port:       10250/TCP (https)
    Host Port:  0/TCP (https)
    Args:
      --kubelet-service=kube-system/prometheus-kube-prometheus-kubelet
      --kubelet-endpoints=true
      --kubelet-endpointslice=false
      --localhost=127.0.0.1
      --prometheus-config-reloader=quay.io/prometheus-operator/prometheus-config-reloader:v0.89.0
      --config-reloader-cpu-request=0
      --config-reloader-cpu-limit=0
      --config-reloader-memory-request=0
      --config-reloader-memory-limit=0
      --thanos-default-base-image=quay.io/thanos/thanos:v0.41.0
      --secret-field-selector=type!=kubernetes.io/dockercfg,type!=kubernetes.io/service-account-token,type!=helm.sh/release.v1
      --web.enable-tls=true
      --web.cert-file=/cert/cert
      --web.key-file=/cert/key
      --web.listen-address=:10250
      --web.tls-min-version=VersionTLS13
    Liveness:   http-get https://:https/healthz delay=0s timeout=1s period=10s #success=1 #failure=3
    Readiness:  http-get https://:https/healthz delay=0s timeout=1s period=10s #success=1 #failure=3
    Environment:
      GOGC:  30
    Mounts:
      /cert from tls-secret (ro)
  Volumes:
   tls-secret:
    Type:          Secret (a volume populated by a Secret)
    SecretName:    prometheus-kube-prometheus-admission
    Optional:      false
  Node-Selectors:  <none>
  Tolerations:     <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  <none>
NewReplicaSet:   prometheus-kube-prometheus-operator-84d5cd6bfd (1/1 replicas created)
Events:          <none>
```

Ce déploiement est principalement responsable de la gestion des configurations Prometheus et s'assure que toutes les ressources associées (Secrets, ConfigMaps, StatefulSets) sont correctement mises en place. Seules les ressources essentielles, comme le secret du certificat TLS, sont montées.


!!! note
    Cette vue d'ensemble décrit la structure et les composants importants installés avec le chart Helm. Dans les sections suivantes, vous apprendrez à modifier ces configurations à l'aide de manifests Kubernetes standard, sans altérer directement les fichiers YAML générés.