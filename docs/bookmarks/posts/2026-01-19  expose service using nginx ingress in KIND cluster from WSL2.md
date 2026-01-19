---
title: "expose service using nginx ingress in KIND cluster from WSL2"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://kk-shichao.medium.com/expose-service-using-nginx-ingress-in-kind-cluster-from-wsl2-14492e153e99"
author:
  - "[[Shi]]"
---
<!-- more -->

[Sitemap](https://kk-shichao.medium.com/sitemap/sitemap.xml)

To expose a service in a on prem k8s cluster, you just need to add a ingress controller and map out the service and port, however, things are little bit trickier with WSL2….

- first, WSL2 doesn’t allow port forwarding AFTER you have created the cluster.
- secondly, a minor but annoying detail, nginx only assign pod to node with `"ingress-ready=true"` label.

so we have to take note about this when we create the kind cluster.

let’s start to create a KIND config file,

```c
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
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
```

then let’s create a KIND cluster with the above configuration,

```c
kind create cluster --config kind.config --name kind-c1
```

*and, let’s confirm that the node has been properly labelelled.*

```c
k get node --show-labels
NAME                    STATUS   ROLES           AGE    VERSION   LABELS
kind-c1-control-plane   Ready    control-plane   163m   v1.25.2   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,ingress-ready=true,kubernetes.io/arch=amd64,kubernetes.io/hostname=kind-c1-control-plane,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=,node.kubernetes.io/exclude-from-external-load-balancers=
```

then, let’s create a simple deployment and service in namespace *hello-ns*

```c
k create ns hello-ns

k create deployment hello - image=k8s.gcr.io/echoserver:1.4 -n hello-ns

k expose deployment hello - type=LoadBalancer - port 80 - target-port=8080 -n hello-ns
```

and, let’s confirm that the pod and service are running,

```c
k get pod -n hello-ns -o wide
NAME                     READY   STATUS    RESTARTS   AGE   IP            NODE                    NOMINATED NODE   READINESS GATES
hello-56c75d54f7-qzpbb   1/1     Running   0          8h    10.244.0.13   kind-c1-control-plane   <none>           <none>

k get svc -n hello-ns
NAME    TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
hello   LoadBalancer   10.96.20.23   <pending>     80:32671/TCP   8h
```

then let’s deploy the nginx ingress controller

```c
k apply --filename https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/kind/deploy.yaml
k wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
```

now, we can define the nginx ingress mapping to service and port with a yaml,

```c
$ cat nginx-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: helloingress
  namespace: hello-ns
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello
            port:
              number: 80
```

then use it to initialize the ingress,

```c
k apply --filename nginx-ingress.yaml
```

then let’s confirm that the ingress is mapped correctly,

```c
k describe ingress helloingress -n hello-ns
Name:             helloingress
Labels:           <none>
Namespace:        hello-ns
Address:          localhost
Ingress Class:    <none>
Default backend:  <default>
Rules:
  Host        Path  Backends
  ----        ----  --------
  *
              /   hello:80 (10.244.0.5:8080)
Annotations:  nginx.ingress.kubernetes.io/rewrite-target: /
Events:
  Type    Reason  Age                 From                      Message
  ----    ------  ----                ----                      -------
  Normal  Sync    22m (x2 over 161m)  nginx-ingress-controller  Scheduled for sync
```

now, we should be able to visit the service from host,

```c
curl localhost
CLIENT VALUES:
client_address=10.244.0.8
command=GET
real path=/
query=nil
request_version=1.1
request_uri=http://localhost:8080/

SERVER VALUES:
server_version=nginx: 1.10.0 - lua: 10001

HEADERS RECEIVED:
accept=*/*
host=localhost
user-agent=curl/7.58.0
x-forwarded-for=172.18.0.1
x-forwarded-host=localhost
x-forwarded-port=80
x-forwarded-proto=http
x-forwarded-scheme=http
x-real-ip=172.18.0.1
x-request-id=4692c3149d7c0e961f5a55ca037b6ed7
x-scheme=http
BODY:
-no body in request-
```

\==== debugging tips ====

```c
# launch a new utility pod from within the cluster
$ kubectl run bbox --image=progrium/busybox -i --tty -- sh

# opkg-install curl

# curl 10.244.0.13:8080   // probe the pod
# curl 10.96.20.23:80     // probe the service
```

\=== the gist ===

I am a coder/engineer/application security specialist. I like to play around with language and tools; I have strong interest in efficiency improvement.

## More from Shi

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--14492e153e99---------------------------------------)