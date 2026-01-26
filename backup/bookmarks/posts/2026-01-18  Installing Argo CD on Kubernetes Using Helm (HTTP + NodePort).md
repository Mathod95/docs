---
title: Installing Argo CD on Kubernetes Using Helm (HTTP + NodePort)
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://medium.com/@tradingcontentdrive/installing-argo-cd-on-kubernetes-using-helm-http-nodeport-0fde03eec450
author:
  - "[[Manohar Shetty]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

GitOps has become a standard approach for deploying and managing applications in Kubernetes, and **Argo CD** is one of the most widely used tools to implement it. Instead of pushing changes directly to a cluster, GitOps treats Git as the single source of truth, allowing Kubernetes to continuously reconcile the desired state defined in version control.

In this blog, we walk through setting up a complete **local GitOps environment** using **Docker, kind, Helm, and Argo CD**. We start by installing the required tools, create a multi-node kind cluster with NodePort access, and then install Argo CD using Helm in HTTP mode. This setup is ideal for learning, testing, and experimenting with GitOps workflows before moving to production-grade clusters.

This blog walks through each command and explains **what it does and why it is needed**.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Y3ZncgGlo_3svwp78jplzw.png)

## Install Docker and Helm

Before creating a kind cluster or installing Argo CD, Docker and Helm must be installed on the system.

## Step 1: Install Docker

```c
apt update
apt install docker.io -y
```

Start and enable Docker:

```c
systemctl start docker
systemctl enable docker
```

(Optional) Allow non-root usage:

```c
usermod -aG docker $USER
```

(Log out and log back in if you run this.)

Verify Docker installation:

```c
docker --version
docker ps
```

## Step 2: Install Helm

```c
snap install helm --classic
```

Verify Helm installation:

```c
helm version
```

## Create a kind Kubernetes Cluster

We will create a **multi-node kind cluster** and expose **NodePorts (30000–30010)** so services like Argo CD can be accessed from the host.

## Step 1: Install kind

```c
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-amd64
chmod +x kind
sudo mv kind /usr/local/bin/kind
```

Verify:

```c
kind version
```

## Step 2: Create kind cluster configuration

```c
cat <<EOF > kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: multi-node-cluster
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
  - containerPort: 30001
    hostPort: 30001
  - containerPort: 30002
    hostPort: 30002
  - containerPort: 30003
    hostPort: 30003
  - containerPort: 30004
    hostPort: 30004
  - containerPort: 30005
    hostPort: 30005
  - containerPort: 30006
    hostPort: 30006
  - containerPort: 30007
    hostPort: 30007
  - containerPort: 30008
    hostPort: 30008
  - containerPort: 30009
    hostPort: 30009
  - containerPort: 30010
    hostPort: 30010
- role: worker
- role: worker
EOF
```

This configuration:

- Creates **1 control-plane + 2 worker nodes**
- Exposes NodePorts **30000–30010** to the host
- Works perfectly with Argo CD NodePort access

## Step 3: Create the kind cluster

```c
kind create cluster --config kind-config.yaml
```

## Step 4: Verify the cluster

```c
kubectl get nodes
```

Expected output:

```c
multi-node-cluster-control-plane   Ready
multi-node-cluster-worker          Ready
multi-node-cluster-worker2         Ready
```

Verify Docker containers:

```c
docker ps
```

You should see:

```c
multi-node-cluster-control-plane
multi-node-cluster-worker
multi-node-cluster-worker2
```

## Step 5: Confirm NodePort mapping

```c
docker inspect multi-node-cluster-control-plane | grep 30004
```

This confirms host-to-container port mapping is active.

## Step 1: Add the Argo CD Helm Repository

```c
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

**What this does:**

- Adds the official Argo project Helm repository to your local Helm configuration
- Updates Helm’s repository index so it can fetch the latest Argo CD charts

This step is mandatory before installing Argo CD via Helm.

## Step 2: Create the Argo CD Namespace

```c
kubectl create namespace argocd
```

**What this does:**

- Creates a dedicated Kubernetes namespace called `argocd`
- Keeps all Argo CD components isolated from other workloads

Argo CD installs multiple components (server, repo-server, controller, Redis, etc.), so using a namespace is a best practice.

## Step 3: Create Helm Values File (HTTP + NodePort)

```c
cat <<EOF > argocd-values.yaml
server:
  insecure: true
  service:
    type: NodePort
    nodePortHttp: 30004
    nodePortHttps: null
EOF
```

**What this does:**

- Creates a Helm values file using `EOF` redirection
- Configures Argo CD to:
- Run in **HTTP mode** (`insecure: true`)
- Disable HTTPS entirely
- Expose the UI via **NodePort 30004**

**Why this is important:**

- kind clusters and simple setups often don’t need HTTPS
- Disabling HTTPS avoids redirect issues
- NodePort allows direct access without ingress

This file ends exactly at `EOF` — no extra lines.

## Step 4: Install Argo CD Using Helm

```c
helm install argocd argo/argo-cd -n argocd -f argocd-values.yaml
```

**What this does:**

- Installs Argo CD using the official Helm chart
- Uses the custom values file you created
- Deploys all Argo CD components into the `argocd` namespace

At this point, Helm takes care of:

- Deployments
- Services
- ConfigMaps
- Secrets
- RBAC

## Step 5: Verify Argo CD Pods

```c
kubectl get pods -n argocd
```

**What to check:**

- All pods should be in `Running` state
- Typical pods include:
- `argocd-server`
- `argocd-repo-server`
- `argocd-application-controller`
- `argocd-dex-server`
- `argocd-redis`

If pods are running, Argo CD is successfully installed.

## Step 6: Verify Services

```c
kubectl get svc -n argocd
```

This shows all services created by the Helm chart.

Then specifically check the Argo CD server service:

```c
kubectl get svc argocd-server -n argocd
```

**Expected output (important):**

- Service type: `NodePort`
- Port mapping should include:
```c
80:30004/TCP
```

This confirms

- Argo CD UI is exposed on port **30004**
- HTTP is enabled
- No HTTPS port is required

## Step 7: Access Argo CD UI

Once the service is confirmed, access Argo CD in your browser:

```c
http://<NODE-IP>:30004
```

For example:

```c
http://13.108.227.150:30004
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Njpp62MCZK84EmH7gWZVEQ.png)

## Get Argo CD Admin Password

After Argo CD is installed, the initial admin password is stored in a Kubernetes secret.

Run the following command:

```c
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d
```

**Login details:**

- **Username:**`admin`
- **Password:** output of the command above

This password is generated automatically during installation and can be changed later from the Argo CD UI or CLI.

## Summary

In this setup, you have:

- Installed Argo CD **via Helm**
- Configured it to run in **HTTP-only mode**
- Exposed it using **NodePort 30004**
- Verified pods and services cleanly

This approach is:

- Simple
- Repeatable
- Suitable for kind clusters and learning environments
- Easy to tear down and reinstall

## Conclusion

By the end of this guide, you have a fully functional **Kubernetes GitOps setup** running on a kind cluster. Docker provides the container runtime, kind enables a lightweight multi-node Kubernetes environment, Helm simplifies application installation, and Argo CD continuously deploys and synchronizes applications from Git.

This approach mirrors real-world GitOps practices while remaining simple and easy to manage. It allows you to focus on understanding deployment workflows, Helm-based applications, and Argo CD operations without the overhead of managing a complex production cluster. With this foundation in place, you can confidently extend the setup to include multiple applications, environments, and eventually transition to managed or on-prem Kubernetes clusters.

DevOps Engineer | AWS Community Builder | CI/CD & Cloud Enthusiast | Automating Workflows & Scaling Systems

## More from Manohar Shetty

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--0fde03eec450---------------------------------------)