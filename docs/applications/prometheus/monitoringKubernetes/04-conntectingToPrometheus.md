---
title: Connecting To Prometheus
status: draft
sources:
  - https://notes.kodekloud.com/docs/Prep-Course-Prometheus-Certified-Associate-PCA-Certification/Monitoring-Kubernetes/Connecting-To-Prometheus/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/prometheus-certified-associate-pca/module/bb958f66-38c3-41ed-ae2f-7a4ee96c4d66/lesson/b88c394c-edce-4eb5-8fc4-c65759ecbf20
---

> This guide explains how to connect to a Prometheus server and access its web UI using various methods.

In this guide, you'll learn how to connect to a Prometheus server and access its web UI. We'll cover several methods, starting with inspecting the Prometheus service using kubectl.

## Listing Cluster Services

Begin by listing all services in your Kubernetes cluster to locate the Prometheus service:

```bash hl_lines="1"
kubectl get service
NAME                                      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
alertmanager-operated                     ClusterIP   None            <none>        9093/TCP,9094/TCP,9094/UDP   13h
kubernetes                                ClusterIP   10.96.0.1       <none>        443/TCP                      13h
prometheus-grafana                        ClusterIP   10.96.83.197    <none>        80/TCP                       13h
prometheus-kube-prometheus-alertmanager   ClusterIP   10.96.183.143   <none>        9093/TCP,8080/TCP            13h
prometheus-kube-prometheus-operator       ClusterIP   10.96.55.122    <none>        443/TCP                      13h
prometheus-kube-prometheus-prometheus     ClusterIP   10.96.37.225    <none>        9090/TCP,8080/TCP            13h
prometheus-kube-state-metrics             ClusterIP   10.96.107.10    <none>        8080/TCP                     13h
prometheus-operated                       ClusterIP   None            <none>        9090/TCP                     13h
prometheus-prometheus-node-exporter       ClusterIP   10.96.104.136   <none>        9100/TCP                     13h
```

This output confirms that the Prometheus service is running. Notice that the service is of type ClusterIP, meaning it is accessible only within the cluster.

## Inspecting the Prometheus Service Configuration

To investigate further, output the service configuration to a YAML file. For instance, execute:

```bash hl_lines="1"
kubectl get service prometheus-kube-prometheus-prometheus -o yaml
```

```yaml linenums="1" hl_lines="44"
apiVersion: v1
kind: Service
metadata:
  annotations:
    meta.helm.sh/release-name: prometheus
    meta.helm.sh/release-namespace: default
  creationTimestamp: "2026-03-17T06:28:47Z"
  labels:
    app: kube-prometheus-stack-prometheus
    app.kubernetes.io/instance: prometheus
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: kube-prometheus-stack
    app.kubernetes.io/version: 82.10.5
    chart: kube-prometheus-stack-82.10.5
    heritage: Helm
    release: prometheus
    self-monitor: "true"
  name: prometheus-kube-prometheus-prometheus
  namespace: default
  resourceVersion: "615"
  uid: 80ad2ef9-ac4e-4995-a8de-dea1d1989e0c
spec:
  clusterIP: 10.96.37.225
  clusterIPs:
  - 10.96.37.225
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - name: http-web
    port: 9090
    protocol: TCP
    targetPort: 9090
  - appProtocol: http
    name: reloader-web
    port: 8080
    protocol: TCP
    targetPort: reloader-web
  selector:
    app.kubernetes.io/name: prometheus
    operator.prometheus.io/name: prometheus-kube-prometheus-prometheus
  sessionAffinity: None
  type: ClusterIP
status:
  loadBalancer: {}
```

You will notice it is configured as a ClusterIP service.

!!! info
    Since the service uses ClusterIP, it is only accessible from within your Kubernetes cluster.

## Enabling External Access

To access Prometheus externally, consider the following options:

- Change the service type to NodePort or LoadBalancer.
- Set up an Ingress resource to route traffic from a specific URL or domain to the Prometheus service.

For demo purposes, we'll use port forwarding.

## Accessing Prometheus via Port Forwarding

First, check the running pods in your cluster:

```bash hl_lines="1"
kubectl get pods
NAME                                                     READY   STATUS    RESTARTS   AGE
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          13h
prometheus-grafana-64b4d64c54-2hjj8                      3/3     Running   0          13h
prometheus-kube-prometheus-operator-84d5cd6bfd-lpnxb     1/1     Running   0          13h
prometheus-kube-state-metrics-67cf98b59f-6nrv7           1/1     Running   0          13h
prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          13h
prometheus-prometheus-node-exporter-6b5mn                1/1     Running   0          13h
```

Once you have identified the correct Prometheus pod (for example, `prometheus-prometheus-kube-prometheus-0`), forward the pod’s port 9090 to your local machine:

```bash hl_lines="1"
kubectl port-forward prometheus-prometheus-kube-prometheus-prometheus-0 9090
```

With port forwarding active, open your browser and navigate to [http://localhost:9090](http://localhost:9090){target=_blank} to access the Prometheus web UI. This confirms that Prometheus is actively running.

!!! warning
    Port forwarding is ideal for demos and testing. For production environments, switch to NodePort, LoadBalancer, or configure an Ingress for secure and stable external access.