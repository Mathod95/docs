---
title: Installing Helm Chart
status: draft
sources:
  - https://notes.kodekloud.com/docs/Prep-Course-Prometheus-Certified-Associate-PCA-Certification/Monitoring-Kubernetes/Installing-Helm-Chart/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/prometheus-certified-associate-pca/module/bb958f66-38c3-41ed-ae2f-7a4ee96c4d66/lesson/601c8a1d-c743-457e-85e5-a39ea757c476
todo:
  - Revoir les informations sur prometheus operator ligne 79
---

> Cette page fournit des instructions étape par étape pour installer Helm et déployer le Helm chart Prometheus sur un cluster Kubernetes.

Dans cette leçon, je vais vous guider étape par étape pour installer Helm et déployer le Helm chart Prometheus (`kube-prometheus-stack`) sur votre cluster Kubernetes. Suivez ces instructions pour mettre en place la supervision dans votre environnement.

## Installation de Helm

Avant d’installer le chart Prometheus, vous devez installer Helm sur votre système. Pour des instructions d’installation détaillées spécifiques à votre système d’exploitation, consultez la [documentation officielle](https://helm.sh/docs/intro/install/){target=_blank}. Pour une machine Linux standard, vous pouvez utiliser le script d’installation intégré.


1. Télécharger le script d’installation Helm:

    ```bash hl_lines="1"
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
    ```

2. Donner les permissions d’exécution et lancer l’installation:

    ```bash hl_lines="1 2"
    chmod 700 get_helm.sh
    ./get_helm.sh
    ```

3. Vérifier l’installation en vérifiant la version de Helm:

    ```bash hl_lines="1"
    helm version
    version.BuildInfo{Version:"v4.1.3", GitCommit:"c94d381b03be117e7e57908edbf642104e00eb8f", GitTreeState:"clean", GoVersion:"go1.26.1", KubeClientVersion:"v1.35"}
    ```

Vous pouvez également installer Helm via brew:

```bash hl_lines="1"
brew install helm
```

## Ajout du dépôt Prometheus et installation du chart

Une fois Helm installé, vous pouvez ajouter le dépôt Prometheus Community et déployer le chart kube-prometheus-stack.

1. Ajouter le dépôt Prometheus Community:

    ```bash hl_lines="1"
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    "prometheus-community" has been added to your repositories
    ```

2. Mettre à jour les dépôts Helm:

    ```bash hl_lines="1"
    helm repo update
    Hang tight while we grab the latest from your chart repositories...
    ...Successfully got an update from the "prometheus-community" chart repository
    Update Complete. ⎈Happy Helming!⎈
    ```

3. Installer le chart kube-prometheus-stack.  

    ```bash hl_lines="1"
    helm install prometheus prometheus-community/kube-prometheus-stack
    NAME: prometheus
    LAST DEPLOYED: Tue Mar 17 07:28:30 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1
    DESCRIPTION: Install complete
    TEST SUITE: None
    NOTES:
    kube-prometheus-stack has been installed. Check its status by running:
      kubectl --namespace default get pods -l "release=prometheus"

    Get Grafana 'admin' user password by running:

      kubectl --namespace default get secrets prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo

    Access Grafana local instance:

      export POD_NAME=$(kubectl --namespace default get pod -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=prometheus" -oname)
      kubectl --namespace default port-forward $POD_NAME 3000

    Get your grafana admin user password by running:

      kubectl get secret --namespace default -l app.kubernetes.io/component=admin-secret -o jsonpath="{.items[0].data.admin-password}" | base64 --decode ; echo


    Visit https://github.com/prometheus-operator/kube-prometheus for instructions on how to create & configure Alertmanager and Prometheus instances using the Operator.
    ```

!!! note "Configuration par défaut"
    La commande si dessus déploie le chart en utilisant les valeurs de configuration par défaut que vous pouvez retrouvez avec cette commande
    ```bash hl_lines="1"
    helm show values prometheus-community/kube-prometheus-stack
    ```

!!! info "kube-prometheus-stack"
    kube-prometheus-stack inclut Grafana, AlertManager, ... mais surtout l'operator Prometheus

    Prometheus Operator est un controller Kubernetes qui automatise la gestion de Prometheus.  
    Concrètement, il permet de gérer Prometheus avec des objets Kubernetes comme `ServiceMonitor` plutôt qu’avec des fichiers de config manuels.  

## Customizing the Chart Values

Each Helm chart allows you to override default configuration values. To explore configurable options for the kube-prometheus-stack chart, export the default configuration into a file:

```bash
$ helm show values prometheus-community/kube-prometheus-stack > values.yaml
```

Review the generated `values.yaml` file to see all the custom configuration options. Below is an excerpt that illustrates some of the configurable sections:

```yaml
containers: []

# Additional volumes on the output StatefulSet definition.
volumes: []

# Additional VolumeMounts on the output StatefulSet definition.
volumeMounts: []

## InitContainers allows injecting additional initContainers. This is meant to allow doing some changes
## (permissions, directory tree modifications) on mounted volumes before starting Prometheus.
initContainers: []

## Priority class assigned to the Pods.
priorityClassName: ""

## PortName to use for ThanosRuler.
portName: "web"

## ExtraSecret can be used to store various data in an extra secret (e.g., hashed basic auth credentials).
extraSecret:
  name: ""
  annotations: {}
  data: {}

## Setting to true produces cleaner resource names, but requires a data migration due to persistent volume name changes.
cleanPrometheusOperatorObjectNames: false
```

Another section might include:

```yaml
nameOverride: ""
namespaceOverride: ""
kubeTargetVersionOverride: ""
kubeVersionOverride: ""
fullnameOverride: ""
commonLabels: {}
  scmhash: abc123
```

And additional service-specific configurations:

```yaml
externalTrafficPolicy: Cluster
type: ClusterIP

servicePerReplica:
  enabled: false
  annotations: {}

port: 9093
targetPort: 9093
nodePort: 30904
```

Once you have customized the `values.yaml` file, deploy your configuration using the `-f` flag:

```bash
$ helm install prometheus prometheus-community/kube-prometheus-stack -f values.yaml
```

For this lesson, we will proceed with the default deployment settings.

## Summary

You have successfully learned how to install Helm, add the Prometheus Community repository, and deploy the kube-prometheus-stack chart on your Kubernetes cluster. In the upcoming lesson, we will dive deeper into the components deployed by this chart and explain the various Kubernetes resources created during the installation.

https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#configuration