---
title: "[Nov 2025] Local Kubernetes Using Kind and cloud-provider-kind"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@standardloop/nov-2025-local-kubernetes-using-kind-and-cloud-provider-kind-dda75e19c926"
author:
  - "[[Josh]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![Kind Logo which does kubernetes in a bottle.](https://miro.medium.com/v2/resize:fit:640/format:webp/1*nzCO38pyKTeYN2Z-Ydh29A.png)

[kind logo](https://github.com/kubernetes-sigs/kind/blob/main/logo/logo.png)

## My GitHub Repo for this Article

- [https://github.com/standardloop/knowledge-transfer/tree/main/01-kind](https://github.com/standardloop/knowledge-transfer/tree/main/01-kind)

## Table of Contents

· [My GitHub Repo for this Article](https://medium.com/@standardloop/#ff32)  
· [Table of Contents](https://medium.com/@standardloop/#3fe6)  
· [Background](https://medium.com/@standardloop/#2387)  
· [Prerequisites](https://medium.com/@standardloop/#821d)  
∘ [Docker](https://medium.com/@standardloop/#fbcf)  
∘ [Kind](https://medium.com/@standardloop/#d65b)  
· [Creating a Cluster with a Config File](https://medium.com/@standardloop/#359f)  
∘ [Config](https://medium.com/@standardloop/#f606)  
∘ [Check to see the Nodes are Running](https://medium.com/@standardloop/#0786)  
· [Updating the Cluster](https://medium.com/@standardloop/#2207)  
· [Setting up and Running cloud-provider-kind](https://medium.com/@standardloop/#76f1)  
∘ [Install](https://medium.com/@standardloop/#dc7c)  
∘ [Run](https://medium.com/@standardloop/#b333)  
· [Deploying ingress-nginx as our Load Balancer](https://medium.com/@standardloop/#d6cf)  
∘ [Creating a values file](https://medium.com/@standardloop/#c3de)  
∘ [Deploying the Chart](https://medium.com/@standardloop/#6710)  
∘ [Confirm Installation](https://medium.com/@standardloop/#7b5a)  
· [Configure /etc/hosts](https://medium.com/@standardloop/#d255)  
· [Deploy a Sample App](https://medium.com/@standardloop/#332c)  
· [Cleaning Up](https://medium.com/@standardloop/#2aa5)  
· [TLDR](https://medium.com/@standardloop/#4d03)

## Background

> kind is a tool for running local Kubernetes clusters using Docker container “nodes”. kind was primarily designed for testing Kubernetes itself, but may be used for local development or CI.

Kind is part of the Kubernetes Special Interest Groups (SIGS)

Special Interest Groups in Kubernetes provide places for the community to focus development and discussion on a particular part of the project.

You can find the Kind source code here:

- [https://github.com/kubernetes-sigs/kind](https://github.com/kubernetes-sigs/kind)

and the documentation here:

- [https://kind.sigs.k8s.io/](https://kind.sigs.k8s.io/)

## Prerequisites

For this article, I will be using [homebrew (brew)](https://github.com/Homebrew/brew) on macOS, but you can use your package manager of your choice.

### Docker

Have docker installed and have a docker engine running.

For this article, I will be using [Rancher Desktop](https://github.com/rancher-sandbox/rancher-desktop).

You can install with Rancher Desktop with brew like this:

```c
$ brew install --cask rancher
```

Make sure your docker engine is running.

You can check if it is with the following command:

```c
$ docker info > /dev/null 2>&1
```

### Kind

You can install with the following command:

```c
$ brew install kind
$ which kind
/opt/homebrew/bin/kind
$ kind --version
kind version 0.30.0
```

## Creating a Cluster with a Config File

You can create clusters without config files, but I always recommend getting in the habit of using them for repeatable behavior.

There are two kinds of node types, **control-plane** and **worker**.

A single **control-plane** node is always required.

### Config

Make sure to check the newest version, you can find the images [here](https://hub.docker.com/r/kindest/node/).

I will create a file named **kind-config.yaml** and place the following contents in it:

```c
---
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: slke-1
nodes:
  - role: control-plane
    image: kindest/node:v1.34.0
  - role: worker
    image: kindest/node:v1.34.0
```

I will naming my cluster slke-1 (standardloop kubernetes engine 1).

Here we are creating two nodes, one for the control-plane and one worker.

```c
$ kind create cluster --config=./kind-config.yaml
```

You can use a tool such as [**kubectx**](https://github.com/ahmetb/kubectx) to ensure your context is set.

```c
$ kubectx
kind-slke-1
```

Notice how the name is prefixed with *kind-.*

### Check to see the Nodes are Running

Using **docker ps**:

```c
$ docker ps
CONTAINER ID   IMAGE                  COMMAND                  CREATED         STATUS         PORTS                       NAMES
4b59fab194e5   kindest/node:v1.34.0   "/usr/local/bin/entr…"   2 minutes ago   Up 2 minutes   127.0.0.1:57499->6443/tcp   slke-1-control-plane
bdf56ba1fc15   kindest/node:v1.34.0   "/usr/local/bin/entr…"   2 minutes ago   Up 2 minutes                               slke-1-worker
```

Using **kubectl get nodes**:

```c
$ kubectl get nodes
NAME                   STATUS   ROLES           AGE   VERSION
slke-1-control-plane   Ready    control-plane   15m   v1.34.0
slke-1-worker          Ready    <none>          15m   v1.34.0
```

If it is bothering you that **ROLES** is empty for the **worker** node, you can run:

```c
$ kubectl label nodes slke-1-worker node-role.kubernetes.io/worker=""
node/slke-1-worker labeled
$ kubectl get nodes
NAME                   STATUS   ROLES           AGE   VERSION
slke-1-control-plane   Ready    control-plane   16m   v1.34.0
slke-1-worker          Ready    worker          16m   v1.34.0
```

## Updating the Cluster

You cannot update a cluster after creation, so you will need to delete it and then recreate it if you are changing any config.

## Setting up and Running cloud-provider-kind

**cloud-provider-kind** allows you to use a Kubernetes **Service** type [**LoadBalancer**](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer)**.**

The reason it is called **cloud-provider-kind** is because when you use a Kubernetes **Service** type **LoadBalancer** in a cloud environment, such as [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/service-load-balancer), the Cloud Provider will setup some infrastructure behind the scenes to allow routing.

Previously, you had to configure [MetalLB](https://github.com/metallb/metallb) (which was a more involved setup and had issues on macOS), or use [Extra Port Mappings](https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings) (which was a simple solution, but it felt more hacky and different from what would be used in a production environment).

### Install

```c
$ brew install cloud-provider-kind
$ which cloud-provider-kind
/opt/homebrew/bin/cloud-provider-kind
```

### Run

I recommend opening a separate terminal session for running this command to easily view the logs.

According to the [README of the repository](https://github.com/kubernetes-sigs/cloud-provider-kind/blob/main/README.md), you will need to run with **sudo**.

```c
$ sudo cloud-provider-kind
```

You can also view the docker container running that is part of cloud-provider-kind:

```c
$ docker ps
CONTAINER ID   IMAGE                      COMMAND                  CREATED          STATUS          PORTS                                                                                                                                     NAMES
a411bd911a94   envoyproxy/envoy:v1.33.2   "/docker-entrypoint.…"   4 seconds ago    Up 3 seconds    0.0.0.0:32774->80/tcp, [::]:32774->80/tcp, 0.0.0.0:32775->443/tcp, [::]:32775->443/tcp, 0.0.0.0:32776->10000/tcp, [::]:32776->10000/tcp   kindccm-f53170ec34f3
...
```

## Deploying ingress-nginx as our Load Balancer

### Creating a values file

I will create a file called **ingress-nginx.values.yaml** with the following contents:

```c
controller:
  service:
    type: "LoadBalancer"
```

You can pass values as command line arguments, but I prefer values files as it helps with upgrading the release if needed.

### Deploying the Chart

[Make sure to use the latest chart version](https://github.com/kubernetes/ingress-nginx/releases?q=helm-chart&expanded=true), for me it was **4.13.3.**

```c
$ helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
$ helm repo update
$ helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --create-namespace \
    -n ingress-nginx \
    --values ingress-nginx.values.yaml \
    --version 4.13.3 \
    --wait
```

### Confirm Installation

We will check the **namespace**, the **pods**, and see if the **LoadBalancer** service was assigned an **EXTERNAL-IP** by **cloud-provider-kind**

```c
$ kubectl get ns
NAME                 STATUS   AGE
default              Active   21m
ingress-nginx        Active   2m12s
kube-node-lease      Active   21m
kube-public          Active   21m
kube-system          Active   21m
local-path-storage   Active   21m
$ kubectl get pods -n ingress-nginx
NAME                                        READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-6f6c964579-csllp   1/1     Running   0          2m27s
$ kubectl get svc -n ingress-nginx
kubectl get svc -n ingress-nginx
NAME                                 TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx-controller             LoadBalancer   10.96.241.10   172.18.0.4    80:32725/TCP,443:30829/TCP   2m51s
ingress-nginx-controller-admission   ClusterIP      10.96.249.13   <none>        443/TCP                      2m51s
```

If your **EXTERNAL-IP** for the **ingress-nginx-controller** **svc** is showing **<pending>** make sure **cloud-provider-kind** is running and inspect the logs.

Here is an easy one-liner to print the IP Address:

```c
$ kubectl get svc/ingress-nginx-controller -n ingress-nginx -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'
172.18.0.4
```

Note: this IP address is not public on the internet. There is no networking in place for anyone outside your network to access this.

Now we can use curl to hit the LoadBalancer via IP Address:

```c
$ curl http://172.18.0.4
<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

Awesome!

## Configure /etc/hosts

Using the IP address we got from:

```c
$ kubectl get svc/ingress-nginx-controller -n ingress-nginx -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

We can update **/etc/hosts** to have a nice looking URL:

```c
$ sudo vim /etc/hosts
...
172.18.0.4      kind.local
```

Now you can go to [http://kind.local](http://kind.local/)

## Deploy a Sample App

I will be using the [**hashicorp http-echo server**](https://github.com/hashicorp/http-echo) has my example app.

Make sure to use the most up to date image, you can view the images [here](https://hub.docker.com/r/hashicorp/http-echo).

I will create a file called **app.yaml** and add the following manifests in it:

```c
---
apiVersion: v1
kind: Namespace
metadata:
  name: app
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: http-echo-deployment
  namespace: app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: http-echo
  template:
    metadata:
      labels:
        app: http-echo
    spec:
      containers:
        - name: http-echo
          image: hashicorp/http-echo:1.0.0
          args: ["-text", "Hello from Kubernetes!", "-listen", ":8080"]
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: http-echo-service
  namespace: app
spec:
  selector:
    app: http-echo
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: http-echo-service-ingress
  namespace: app
spec:
  ingressClassName: nginx
  rules:
    - host: kind.local
      http:
        paths:
          - path: /
            pathType: ImplementationSpecific
            backend:
              service:
                name: http-echo-service
                port:
                  number: 80
```

Apply the contents:

```c
$ kubectl apply -f app.yaml
namespace/app created
deployment.apps/http-echo-deployment created
service/http-echo-service created
ingress.networking.k8s.io/http-echo-service-ingress created
```

Go to [http://kind.local](http://kind.local/) and see the message!

![We opened or special URL add see “Hello from Kubernetes”](https://miro.medium.com/v2/resize:fit:640/format:webp/1*w1AND7bHW-bAqwj9Bg0-Vw.png)

The message from http://kind.local

## Cleaning Up

Stop your **cloud-provider-kind** by Ctrl+C’ing the terminal or by manually finding and stopping process:

```c
$ sudo pkill cloud-provider-kind
```

and then delete the cluster (deleting the cluster will also remove all the kubernetes resources we deployed):

```c
$ kind delete cluster --name slke-1
```

Also don’t forgot to remove your **/etc/hosts** entry!

If you really want to uninstall the kubernetes resources you can do the following:

```c
$ kubectl delete -f app.yaml
$ helm uninstall ingress-nginx -n ingress-nginx
```

## TLDR

- [https://github.com/standardloop/knowledge-transfer/blob/main/01-kind/Taskfile.yml](https://github.com/standardloop/knowledge-transfer/blob/main/01-kind/Taskfile.yml)

Use my provided **Taskfile.yml** and run it all yourself easily:

```c
---
version: '3'

vars:
  INGRESS_NGINX_NS: "ingress-nginx"
  INGRESS_NGINX_VERSION: 4.13.3
  CLUSTER_NAME: slke-1
  DEPENDENCIES:
    - docker
    - kind
    - helm
    - cloud-provider-kind
    - kubectl

check-docker-running: &check-docker-running |
  docker info > /dev/null 2>&1

check-cluster-running: &check-cluster-running |
  kind get clusters | grep {{.CLUSTER_NAME}}

check-cloud-provider-kind-running: &check-cloud-provider-kind-running |
  pgrep sudo cloud-provider-kind

tasks:
  default:
    aliases: [all, make]
    deps:
      - check-dependencies
      - create-cluster
      - run-cloud-provider-kind
      - deploy-ingress
      - deploy-app
      - update-etc-hosts
      - open-app

  check-dependencies:
    silent: true
    cmds:
      - |
        {{range .DEPENDENCIES}}
          if ! command -v {{.}} > /dev/null; then
            echo "{{.}} not found"
          fi
        {{end}}
        if ! helm plugin list | grep -q diff > /dev/null; then
            echo "helm diff plugin is missing"
        fi

  create-cluster:
    run: once
    preconditions:
      - *check-docker-running
    cmds:
      - kind create cluster --config=./kind-config.yaml
    status:
      - *check-cluster-running

  run-cloud-provider-kind:
    run: once
    deps:
      - create-cluster
    interactive: true
    cmds:
      - sudo -v
      - bash -c 'nohup sudo cloud-provider-kind >/dev/null 2>&1 &'
    status:
      - *check-cloud-provider-kind-running

  deploy-ingress:
    run: once
    deps:
      - run-cloud-provider-kind
    cmds:
      - |
        helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
        helm repo update
        helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
          --create-namespace \
          -n {{.INGRESS_NGINX_NS}} \
          --values ingress-nginx.values.yaml \
          --version {{.INGRESS_NGINX_VERSION}} \
          --wait
    status:
      - |
        helm diff upgrade ingress-nginx ingress-nginx/ingress-nginx \
          -n {{.INGRESS_NGINX_NS}} \
          --values ingress-nginx.values.yaml \
          --version {{.INGRESS_NGINX_VERSION}} \

  clean-ingress:
    cmds:
      - helm uninstall ingress-nginx -n {{.INGRESS_NGINX_NS}}

  deploy-app:
    run: once
    deps:
      - deploy-ingress
    cmds:
      - kubectl apply -f app.yaml
    status:
      - kubectl diff -f app.yaml

  clean-app:
    cmds:
      - kubectl delete -f app.yaml

  update-etc-hosts:
    run: once
    prompt: Do you want to update /etc/hosts ?
    deps:
      - deploy-app
    cmds:
      - echo {{.LOAD_BALANCER_IP}}
      - sudo -v
      - echo "{{.LOAD_BALANCER_IP}}      kind.local" | sudo tee -a /etc/hosts
    status:
      - cat /etc/hosts | grep {{.LOAD_BALANCER_IP}}
    vars:
      LOAD_BALANCER_IP:
        sh: kubectl get svc/ingress-nginx-controller -n {{.INGRESS_NGINX_NS}} -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'  # yamllint disable-line rule:line-length

  open-app:
    deps:
      - deploy-app
    cmds:
      - open http://kind.local

  clean-cloud-provider-kind:
    interactive: true
    cmds:
      - *check-cloud-provider-kind-running
      - sudo -v
      - sudo pkill cloud-provider-kind

  clean-cluster:
    cmds:
      - kind delete cluster --name {{.CLUSTER_NAME}}

  clean:
    aliases: [delete]
    ignore_error: true
    cmds:
      - task: clean-app
      - task: clean-ingress
      - task: clean-cluster
      - task: clean-cloud-provider-kind
      - echo "make sure to reset your etc/hosts!"
```
```c
$ task
```

Thanks for reading! I will be making more articles in the future so please following my account! If you have any tools or topics you want me to look into, please add a comment below.

If you are interested in using the Gateway API take a look at this article:## [\[Nov 2025\] Using K8s Gateway API with Kind and cloud-provider-kind](https://medium.com/@standardloop/nov-2025-using-k8s-gateway-api-with-kind-and-cloud-provider-kind-3a724b926780?source=post_page-----dda75e19c926---------------------------------------)

Let’s utilize the Kubernetes Gateway API with Kind and cloud-provider-kind

medium.com

[View original](https://medium.com/@standardloop/nov-2025-using-k8s-gateway-api-with-kind-and-cloud-provider-kind-3a724b926780?source=post_page-----dda75e19c926---------------------------------------)

Hi, I'm Josh! I'm a Site Reliability Engineer. I love learning and contributing.

## More from Josh

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--dda75e19c926---------------------------------------)