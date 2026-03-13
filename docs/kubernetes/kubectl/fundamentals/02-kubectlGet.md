---
title: kubectl get
status: draft
sources:
  - https://notes.kodekloud.com/docs/Kubernetes-Troubleshooting-for-Application-Developers/Prerequisites/kubectl-get/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/kubernetes-troubleshooting-for-application-developers/module/09c2c8a6-ba29-4d55-bea1-cd8584be9107/lesson/03d75733-68c9-4385-878c-d4462fb8d59f?autoplay=true
---

> This article explains how to use the kubectl get command to inspect Kubernetes cluster resources effectively.

In this article, we explore how to use the `kubectl get` command to inspect your Kubernetes cluster resources. For convenience, an alias (`k`) for `kubectl` is used in the examples below. If you haven't already, [enable shell autocompletion](https://kubernetes.io/docs/tasks/tools/install-kubectl/#enabling-shell-autocompletion) for a smoother workflow.

Below you'll find a detailed walkthrough of various commands and options to inspect your cluster effectively.

──────────────────────────────────────────────

## Listing Cluster Resources

If your Kubernetes cluster has multiple resources deployed, simply running:

```bash hl_lines="1"
kubectl get
You must specify the type of resource to get. Use "kubectl api-resources" for a complete list of supported resources.
error: Required resource not specified.
Use "kubectl explain <resource>" for a detailed description of that resource (e.g. kubectl explain pods).
See 'kubectl get -h' for help and examples
```

will list the available resources. Using the alias, you can list all resources with:

```bash hl_lines="1"
kubectl get all
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   14s
```

To list resources across all namespaces, add the `-A`(`--all-namespaces`) flag.  
This command displays pods, services, daemon sets, deployments, replica sets, jobs, and more:  

```bash hl_lines="1"
kubectl get all -A
NAMESPACE            NAME                                             READY   STATUS    RESTARTS   AGE
kube-system          pod/coredns-7d764666f9-9wpvn                     1/1     Running   0          31s
kube-system          pod/coredns-7d764666f9-w9zq4                     1/1     Running   0          31s
kube-system          pod/etcd-kind-control-plane                      1/1     Running   0          39s
kube-system          pod/kindnet-xvsgr                                1/1     Running   0          31s
kube-system          pod/kube-apiserver-kind-control-plane            1/1     Running   0          39s
kube-system          pod/kube-controller-manager-kind-control-plane   1/1     Running   0          39s
kube-system          pod/kube-proxy-jjjmr                             1/1     Running   0          31s
kube-system          pod/kube-scheduler-kind-control-plane            1/1     Running   0          39s
local-path-storage   pod/local-path-provisioner-67b8995b4b-qzgvq      1/1     Running   0          31s

NAMESPACE     NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
default       service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  39s
kube-system   service/kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   38s

NAMESPACE     NAME                        DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
kube-system   daemonset.apps/kindnet      1         1         1       1            1           kubernetes.io/os=linux   36s
kube-system   daemonset.apps/kube-proxy   1         1         1       1            1           kubernetes.io/os=linux   38s

NAMESPACE            NAME                                     READY   UP-TO-DATE   AVAILABLE   AGE
kube-system          deployment.apps/coredns                  2/2     2            2           38s
local-path-storage   deployment.apps/local-path-provisioner   1/1     1            1           36s

NAMESPACE            NAME                                                DESIRED   CURRENT   READY   AGE
kube-system          replicaset.apps/coredns-7d764666f9                  2         2         2       31s
local-path-storage   replicaset.apps/local-path-provisioner-67b8995b4b   1         1         1       31s
```

---

## Exploring Namespaces and Deployments

First, list all namespaces in your cluster with:

```bash hl_lines="1"
kubectl get namespace
NAME                 STATUS   AGE
default              Active   5m15s
kube-node-lease      Active   5m15s
kube-public          Active   5m15s
kube-system          Active   5m15s
local-path-storage   Active   5m11s
```

To inspect the deployments in the User Acceptance Testing (uat) namespace, run:

```bash
controlplane ~ ➜ k get -n uat deployments.apps
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
notes-app-deployment    2/2     2            2           41m
```

---

## Inspecting a Deployment Manifest

To review a detailed deployment configuration (for example, "notes-app-deployment"), output the full manifest in YAML format. This manifest mirrors the original configuration file that created the Deployment:

```yaml 
creationTimestamp: "2024-10-20T18:46:54Z"
generation: 1
labels:
  app: notes-app
name: notes-app-deployment
namespace: uat
resourceVersion: "8757"
uid: 7e486af6-f24e-4136-b259-f5e1513dac5f
spec:
  progressDeadlineSeconds: 600
  replicas: 2
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: notes-app
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: notes-app
    spec:
      containers:
        - image: pavnasa/notes-app
          imagePullPolicy: IfNotPresent
          name: notes-app-deployment
          ports:
            - containerPort: 3000
              protocol: TCP
          resources:
            requests:
              cpu: 100m
```

This YAML output includes all key details such as metadata, specifications, and container configurations.

!!! tip
    The manifest output closely resembles the original file used for deployment creation, making it an excellent reference for understanding the resource structure.

---

## Filtering Specific Information

Sometimes you only need to extract specific information from the manifest, such as the number of replicas. You have two options:

1. **Using grep:**\
   This method filters the YAML output for occurrences of the `replicas` field.

   ```bash
   controlplane ~ ➜ k get -n uat deployments.apps notes-app-deployment -o yaml | grep replicas
     replicas: 2
     replicas: 2
   ```

2. **Using JSONPath:**\
   For a cleaner output, use the JSONPath flag to extract just the value of replicas.

   ```bash
   controlplane ~ ➜ k get -n uat deployments.apps notes-app-deployment -o jsonpath="{.spec.replicas}"
   2
   ```

---

## Extracting Container Specifications

To delve deeper into a deployment’s container specifications (such as image, ports, and resource requests), use JSONPath. Since the container configurations are nested under `spec.template.spec.containers`, running the command below will provide the necessary details:

```bash
controlplane ~ ➜ k get -n uat deployments.apps notes-app-deployment -o jsonpath="{.spec.template.spec.containers}"
[{"image": "pavnasa/notes-app", "imagePullPolicy": "IfNotPresent", "name": "notes-app-deployment", "ports": [{"containerPort":3000, "protocol": "TCP"}], "resources": {"requests": {"cpu": "100m"}}}]
```

This output displays all container configuration details defined in the Deployment.

---

## Summary

In summary, this article covered:

* How to list cluster resources using `kubectl get` with or without namespaces.
* Exploring namespaces and specific deployments in the cluster.
* Inspecting detailed deployment manifests in YAML format.
* Extracting specific information (like the number of replicas) using grep or JSONPath.
* Retrieving container specifications directly from the deployment definition.

<Callout icon="lightbulb" color="#1CB2FE">
  For more detailed information and advanced use cases, make sure to visit the [official Kubernetes documentation](https://kubernetes.io/docs/).
</Callout>