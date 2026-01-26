---
title: "Mastering Cilium Network Policies: Zero-Trust Security for Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://yogender027mae.medium.com/mastering-cilium-network-policies-zero-trust-security-for-kubernetes-58cc00518602"
author:
  - "[[Yogender Pal]]"
---
<!-- more -->

[Sitemap](https://yogender027mae.medium.com/sitemap/sitemap.xml)

“Trust No One. Authenticate Everyone. Secure Everything!”

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*HNVk82jwjX2tItCCAdwo9Q.jpeg)

Photo by Sandra Seitamaa on Unsplash

Kubernetes provides a powerful platform for deploying and managing containerized applications, but securing network traffic between pods is a critical challenge. This is where [**Cilium**](https://docs.cilium.io/en/stable/index.html) **Network Policies** come into play.

Cilium is an **eBPF-powered networking solution** that enhances Kubernetes security by enforcing fine-grained network access control. Unlike traditional Kubernetes Network Policies, which operate at **Layer 3/4** (IP and port-based filtering), Cilium extends security controls to **Layer 7** (application-aware filtering for HTTP, gRPC, and Kafka). This means you can enforce policies based on **HTTP methods, paths, and even API calls**, providing deeper security for microservices communication.

With **Cilium Network Policies (CNPs)**, you can:  
✅ Restrict traffic between pods based on labels, protocols, or ports.  
✅ Apply **Layer 7 filtering** to allow or deny requests based on URLs, HTTP methods, and headers.  
✅ Secure applications without modifying them, using eBPF to enforce rules transparently.  
✅ Improve observability with detailed metrics and logs for network traffic.

The code in available in my [github repo](https://github.com/yogenderPalChandra/prometheus-grafana-flask-db/tree/cilium)

In this article, we’ll explore how to use **Cilium Network Policies** to secure Kubernetes workloads, enforce access control, and apply advanced traffic filtering with practical examples.

1. **Install** [**KIND**](https://kind.sigs.k8s.io/) **k8s:**
```c
#install kind
# For AMD64 / x86_64
$ [ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.27.0/kind-linux-amd64

$ chmod +x ./kind

$ sudo mv ./kind /usr/local/bin/kind

# Create test cluster and delete it:
$ sudo kind create cluster --name=test-prometheus-grafana

#get cluster
$ kind get clusters

#delete cluster:
$ kind delete cluster
```
- Create and configure the cluster (file name is cilium-cluster.yaml), Here defaultCNI is disabled as we will install cilium CNI.
```c
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: cilium
networking:
  disableDefaultCNI: true  # Ensures KIND does not use the default CNI, allowing Cilium installation
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=false"
  extraPortMappings:
  - containerPort: 80
    hostPort: 8080
    protocol: TCP
  - containerPort: 443
    hostPort: 44300
    protocol: TCP
```
```c
# kind cluster with port forwarding to host
$ kind create cluster --config cilium-cluster.yaml

$ kubectl cluster-info --context kind-cilium # output: 
Kubernetes control plane is running at https://127.0.0.1:39185
CoreDNS is running at https://127.0.0.1:39185/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

**2\. Install** [**Helm**](https://helm.sh/docs/intro/install/) **&** [**Cilium**](https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default/) (Debian/Ubuntu)

```c
# Install Helm
$ curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
$ sudo apt-get install apt-transport-https --yes
$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
$ sudo apt-get update
$ sudo apt-get install helm

# Install Cilium
$ helm install cilium cilium/cilium --version 1.10.1 \--namespace kube-system

$ cilium status #output:

cilium status
    /¯¯\
 /¯¯\__/¯¯\    Cilium:             OK
 \__/¯¯\__/    Operator:           OK
 /¯¯\__/¯¯\    Envoy DaemonSet:    OK
 \__/¯¯\__/    Hubble Relay:       disabled
    \__/       ClusterMesh:        disabled

DaemonSet              cilium                   Desired: 1, Ready: 1/1, Available: 1/1
DaemonSet              cilium-envoy             Desired: 1, Ready: 1/1, Available: 1/1
Deployment             cilium-operator          Desired: 1, Ready: 1/1, Available: 1/1
Containers:            cilium                   Running: 1
                       cilium-envoy             Running: 1
                       cilium-operator          Running: 1
                       clustermesh-apiserver    
                       hubble-relay             
Cluster Pods:          14/14 managed by Cilium
Helm chart version:    1.17.2
Image versions         cilium             quay.io/cilium/cilium:v1.17.2@sha256:3c4c9932b5d8368619cb922a497ff2ebc8def5f41c18e410bcc84025fcd385b1: 1
                       cilium-envoy       quay.io/cilium/cilium-envoy:v1.31.5-1741765102-efed3defcc70ab5b263a0fc44c93d316b846a211@sha256:377c78c13d2731f3720f931721ee309159e782d882251709cb0fac3b42c03f4b: 1
                       cilium-operator    quay.io/cilium/operator-generic:v1.17.2@sha256:81f2d7198366e8dec2903a3a8361e4c68d47d19c68a0d42f0b7b6e3f0523f249: 1
```

Cilium deploys several components in kube-system name space, lets check:

```c
$ kubectl get pods -n kube-system
NAME                                           READY   STATUS    RESTARTS      AGE
cilium-envoy-r2gf5                             1/1     Running   1 (26h ago)   46h
cilium-hfckl                                   1/1     Running   1 (26h ago)   46h
cilium-operator-59944f4b8f-9jgtg               1/1     Running   1 (26h ago)   46h
```

The `**cilium-hfckl**` pod is a **Cilium agent** running on a Kubernetes node, responsible for enforcing network policies, managing eBPF programs, and handling networking for pods. The `**cilium-operator-59944f4b8f-9jgtg**` pod is a control-plane component that performs higher-level tasks like managing Cilium resources, synchronizing network policies, and handling cluster-wide networking. The `**cilium-envoy-r2gf5**` pod runs **Envoy**, acting as a Layer 7 proxy to enforce HTTP-aware policies, provide observability, and enable service mesh capabilities. We will use layer 7 networking later in this article.

**3\. Deploy Microservices (see:** [**Python frontend + PostgreSQL Backend**](https://yogender027mae.medium.com/microservices-deployment-on-kubernetes-d0723bbffa67)**)**

```c
# Create secret used by flaks connection string 
$ kubectl -n db create secret generic postgresql \
  --from-literal POSTGRES_USER="postgres" \
  --from-literal POSTGRES_PASSWORD='postgres' \
  --from-literal POSTGRES_DB="mydb" \
  --from-literal REPLICATION_USER="postgres" \
  --from-literal REPLICATION_PASSWORD='postgres'

# Create namespace db and actiavte it
$ kubectl create namespace db

# deploy postgres db
$ kubectl apply -f https://raw.githubusercontent.com/yogenderPalChandra/prometheus-grafana-flask-db/main/flask-postgres/postgres-sts.yaml -n db

# deploy flask app and svc
$ kubectl apply -f https://raw.githubusercontent.com/yogenderPalChandra/prometheus-grafana-flask-db/main/flask-postgres/postgres-flask.yaml -n db

# deploy configmap for postgres db
$ kubectl apply -f https://raw.githubusercontent.com/yogenderPalChandra/prometheus-grafana-flask-db/main/flask-postgres/configmap.yaml -n db

#deploy postgres svc
$ kubectl apply -f https://raw.githubusercontent.com/yogenderPalChandra/prometheus-grafana-flask-db/main/flask-postgres/postgres-svs.yaml -n db

# deploy ingress:
$ kubectl apply -f https://raw.githubusercontent.com/yogenderPalChandra/prometheus-grafana-flask-db/main/flask-postgres/postgres-ingress.yaml -n db

# To make flask.postgres accessible from your local machine add this domain in your host file
$ sudo nano /etc/hosts

# Add this line at the end:
127.0.0.1 flask.postgres

# check what pods deployed in db namespace (should be running state):
 
$ kubectl get pods -n db
NAME                        READY   STATUS    RESTARTS      AGE
flask-app-fc5658747-9qr5g   1/1     Running   1 (26h ago)   4d
flask-app-fc5658747-gnn8n   1/1     Running   2 (26h ago)   4d
flask-app-fc5658747-wz9mb   1/1     Running   1 (26h ago)   4d
postgres-0                  1/1     Running   1 (26h ago)   4d
```

Get the node IP: `kubectl get node -o wide` and hit the browser with the address: http://<node IP>: 8080, and boom:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*qz4hvOdmdMwkGDlM6ujHWQ.png)

Python REST API mapped to localhost

**4\. Pod connectivity tests within the same namespace:**

### (No network policy in place — L3 Policy)

By default, any pod can connect to any other pod in any namespace in K8S. This is though undesirable makes K8S implimentaion simple. Lets check this:

- From Frontend python flask pod to Backend postgres pod.
```c
# Create pod
$ kubectl run debug -n db --image=curlimages/curl --restart=Never -- sleep infinity

# get name of the flask pod:
$ kubectl get pods -n db #fecth the name of the pod
# Output:
NAME                        READY   STATUS    RESTARTS      AGE
debug                       1/1     Running   0             19m
flask-app-fc5658747-9qr5g   1/1     Running   1 (27h ago)   4d
flask-app-fc5658747-gnn8n   1/1     Running   2 (27h ago)   4d
flask-app-fc5658747-wz9mb   1/1     Running   1 (27h ago)   4d
postgres-0                  1/1     Running   1 (27h ago)   4d

# get cluster IP of flask pod:
$ kubectl get pod flask-app-fc5658747-9qr5g -o wide -n db

# run shell in the pod
$ kubectl exec -it debug -n db -- sh

# run curl command inside the debug pod:
$ curl http://<Flask pod IP>:5000 # pod Ip looks like this: 10.244.0.193
# Output:<!doctype html><html> ...</html>
```

When you curl from the debug pod the clusterIP of flask it throws the html content which is equivalent to what you saw in the localhost in the first blue image.

- From/To Postgres pod directly:
```c
# get name of the Postgres pod:
$ kubectl get pods -n db #fetch the name of the pod

# get IP of Postgres pod:
$ kubectl get pod postgres-0 -n db -o wide

# in debug pod shell which you opened previosuly do:
$ nc -v -z -w 2 10.244.0.254 5432
10.244.0.254 (10.244.0.254:5432) open
```

We cant use curl command for postgres pod at 5432 port as only TCP traffic is allowed at this port. For this reason we would use the Netcat nc connectivity tool, The `nc` Netcat command checks if port **5432** (PostgreSQL) on **10.244.0.254** is open, confirming that the service is accessible within the namespace.

- From Flask servcie (flask-app-service) to postgres pod:
```c
$ kubectl get svc -n db #output:
NAME                               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
cilium-ingress-flask-app-ingress   ClusterIP   10.96.185.103   <none>        80/TCP,443/TCP   2d2h
flask-app-service                  NodePort    10.96.126.204   <none>        80:30008/TCP     4d
mydb-service                       ClusterIP   None            <none>        5432/TCP         4d1h

# Run again the curl command in the debug pod with the clusterIP of flask-app-service
$ curl http://10.96.126.204:80 # port 80 becasue ist a service exposed to 80 and mapped to localhost at 8080
#output: <!doctype html><html> ...</html>
```

The output is again the html doc eliment. This means there is also conectivity from flask service.

**5\. Pod connectivity test from/to different namespace:**

### (No network policy in place — L3 Policy)

```c
# create a new namespace and create a debug pod there:
$ kubectl create namespace dummy

#Create a pod called debug in dummy namespace and keep it alive and run TCP connectivit using nc to postgres pod running in db namepace:
kubectl run debug -n dummy --image=curlimages/curl --restart=Never -- sleep infinity

#run this pod
kubectl exec -it debug -n dummy -- sh

$ nc -v -z -w 2 10.244.0.254 5432 # output:
10.244.0.254 (10.244.0.254:5432) open
```

The output is printed as open. This means the TCP connection to postgres pod in db namespace is open from a yet different namepsace called dummy. This is security risk anyone can have access to our database.

Kubernetes allows **open communication** between pods because the default **CNI (Container Network Interface)** implementation does not enforce any restrictions. To **restrict pod-to-pod communication**, you need to create **NetworkPolicies** (standard Kubernetes NetworkPolicies or Cilium NetworkPolicies) to explicitly allow or deny traffic. Lets restirct the access uisng cilium network policies.

**6\. Pod connectivity tests from within same namespace**

### (Cilium network policy in place — L3 policy)

Let’s first restrict access to the database pod to only the web server. Apply the network policy that only allows traffic from the web server pod to the database (file name: postgres-networkPolicy.yaml):

```c
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "flask-app-to-db"
  namespace: db
spec:
  endpointSelector:
    matchLabels:
      app: postgres
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: flask-app
```
```c
# Apply this policy in db namespace:
$ kubectl apply -f postgres-networkPolicy.yaml -n db

# Chek if its succesfull:
$ k get cnp -n db # output: 
NAME              AGE   VALID
flask-app-to-db   2s    True
```

This **Cilium Network Policy** allows traffic from pods labeled `**app: flask-app**` to reach pods labeled `**app: postgres**` in the `**db**` **namespace**. It enforces **ingress restrictions** on PostgreSQL, ensuring that only Flask app pods can communicate with it while blocking all other traffic.

- From Frontend python flask pod Backend postgres pod:
```c
# Get Flask pods clusterIP as described in setp 4
# run curl command inside the debug pod in db namespace:
$ curl http://<Flask pod IP>:5000 # pod Ip looks like this: 10.244.0.193
# Output:<!doctype html><html> ...</html>
```

This means we have connectivity from flask pod in db namespace to the postgres pod in the same db namespace

- From/To Postgres pod directly
```c
# Get Postgres Pod clusterIP as described in step 4
# in debug pod shell in db namespace, which you opened previosuly do:
$ nc -v -z -w 2 10.244.0.254 5432 # output:
nc: 10.244.0.254 (10.244.0.254:5432): Operation timed out
```

With the network policy applied, the debug pod can no longer reach the postgres database pod; we can see this in the timeout, while the Flask pod is still connected to the Postgres database pod, thus making it more secure.

- From Flask servcie (flask-app-service) to postgres pod:
```c
# Run again the curl command in the debug pod with the clusterIP of flask-app-service
$ curl http://10.96.126.204:80 #port 80 becasue check this:github cilium
#output: <!doctype html><html> ...</html>
```

This means HTTP traffic from `flask-app-service` service is also allowed.

**7\. Pod connectivity test from/to different namespace:**

```c
kubectl exec -it debug -n dummy -- sh
~ $ nc -v -z -w 2 10.244.0.254 5432
nc: 10.244.0.254 (10.244.0.254:5432): Operation timed out
```

The ClusterIP typed above is the IP of of Postgres pod. The output is printed as `Operation timed out.` This means the TCP connection to postgres pod in db namespace is restricted from all other namspaces including dummy namespace and is allowed from only flask pod and service.

**8\. Pod connectivity tests — Namespace Agnostic**

### (No network policy— L7 policy)

Cilium is layer 7 aware so that we can block or allow a specific request on the HTTP URI paths. In our example policy, we allow HTTP GETs on `/ ` and `/plot/temp`, and also on `/metrics` let’s test that:

```c
# in debug pod in db OR dummy namespace:
$ curl http://<flask service clusterIP>:80/metrics # curl the flask-app-service cluster IP OR
$ curl http://<flask pod clusterIP>:5000/metrics # curl the flask-app pod cluster IP 

# ouputs:
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 927.0
python_gc_objects_collected_total{generation="1"} 332.0
python_gc_objects_collected_total{generation="2"} 95.0
# HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
# TYPE python_gc_objects_uncollectable_total counter
...
```

The command `**curl http://<Flask-app-service clusterIP>:80/metrics**` OR `**curl http://<Flask-app pod ClusterIP>:5000/metrics**` makes an HTTP request to the servcie (port 80) or pod (port 5000). The response contains **Prometheus-style metrics**, which are used for monitoring and observability. **These metrics must be visible to observability team and must be masked from dev team.** The ouput shows that the request is successfull thus breaching a security aspect. Now lets restrict this `/metrics` path: (filename: flask-cnp-l7.yaml)

**9\. Pod connectivity tests — Namespace Agnostic**

### (Cilium network policy in place— L7 policy)

```c
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "l7-rule"
spec:
  endpointSelector:
    matchLabels:
      app: flask-app
  ingress:
    - toPorts:
        - ports:
            - port: '5000'
              protocol: TCP
          rules:
            http:
              - method: GET
                path: "/"
```

`kubectl apply -f flask-cnp-l7.yaml -n db` commands applies this policy in db namespace. This **Cilium Network Policy** applies to pods labeled `**app: flask-app**` and restricts incoming traffic. It allows only **GET requests to the** `**/**` **path** on **port 5000**, while blocking all other request like on path `/metrics`. This ensures that unauthorized HTTP paths or methods cannot be accessed on the Flask application. Try it:

```c
# In debug pod in db or dummy namespace:
$ curl http://<Flask-app pod clusterIp>:5000/metrics # output: 
Access denied
$ curl http://<Flask-app-service clusterIP>:80/metrics # output:
Access denied
```

So we secured our Micoservice. That is the end of it. Cheers!

**If you want to understand how Microservices are working in k8s, try to code this:**## [Microservices deployment on Kubernetes](https://yogender027mae.medium.com/microservices-deployment-on-kubernetes-d0723bbffa67?source=post_page-----58cc00518602---------------------------------------)

Deploying Flask frontend, and PostgreSQL server as backend

yogender027mae.medium.com

[View original](https://yogender027mae.medium.com/microservices-deployment-on-kubernetes-d0723bbffa67?source=post_page-----58cc00518602---------------------------------------)

**If you want to understand the monitoring part of this microservices, try this:**## [Microservices Monitoring with Grafana & Prometheus in Kubernetes](https://yogender027mae.medium.com/microservices-monitoring-with-grafana-prometheus-in-kubernetes-33902fb0c872?source=post_page-----58cc00518602---------------------------------------)

Deploy K8S cluster, Deploy Prometheus & Grafana, Deploy Microservices, Monitor Microservices — Life is easy

yogender027mae.medium.com

[View original](https://yogender027mae.medium.com/microservices-monitoring-with-grafana-prometheus-in-kubernetes-33902fb0c872?source=post_page-----58cc00518602---------------------------------------)

**If you want to understand the config files and deployment of PostgreSQL server in K8S:**## [Deploying custom PostgreSQL server on OpenShift/Kubernetes](https://yogender027mae.medium.com/deploying-custom-postgresql-server-on-openshift-kuberenets-0cca37a1d9ca?source=post_page-----58cc00518602---------------------------------------)

Custom PostgreSQL server comes up with pre-initiallised database, tables, relations and more.

yogender027mae.medium.com

[View original](https://yogender027mae.medium.com/deploying-custom-postgresql-server-on-openshift-kuberenets-0cca37a1d9ca?source=post_page-----58cc00518602---------------------------------------)

Thank you

I talk about programing, AWS, and two hamsters in my room

## More from Yogender Pal

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--58cc00518602---------------------------------------)