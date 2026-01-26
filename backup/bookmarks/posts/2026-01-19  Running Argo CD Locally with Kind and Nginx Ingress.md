---
title: "Running Argo CD Locally with Kind and Nginx Ingress"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@chirayukapoor/running-argo-cd-locally-with-kind-and-nginx-ingress-26b31cece300"
author:
  - "[[Chirayu Kapoor]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Deploying Argo CD on a local Kubernetes cluster using Kind and Nginx Ingress

In this article, I will guide you through the process of setting up and running Argo CD locally. We will utilize Kind to create the local Kubernetes cluster and Nginx Ingress to enable access to the Argo CD instance.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9KFY1nM-sNQtxWx93Rg-hw.png)

ArgoCD

## Prerequisites

Before we begin, make sure you have the following prerequisites in place:

1. **Docker:** Install Docker on your machine to run the Kubernetes cluster with Kind. Refer to the official Docker documentation [here](https://docs.docker.com/get-docker/) for installation instructions specific to your operating system.
2. **Kind:** Install Kind, which is a tool for creating lightweight Kubernetes clusters locally. Kind is distributed as a single binary and can be easily installed. Follow the official Kind documentation [here](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) for installation instructions.
3. **kubectl:** Install the Kubernetes command-line tool, kubectl, to interact with the Kubernetes cluster. You can install kubectl by following the instructions provided in the official Kubernetes documentation [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

### Argo CD

Argo CD is a powerful tool for the continuous delivery and deployment of Kubernetes applications. It provides a declarative approach to manage and automate the deployment of applications and their configurations in Kubernetes clusters. You can learn more about Argo CD from the official documentation [here](https://argo-cd.readthedocs.io/en/stable/).

### Kind

Kind is a popular tool for creating lightweight Kubernetes clusters locally. It runs each Kubernetes node as a Docker container, making it easy to set up and manage local development clusters. To learn more about Kind, visit the official GitHub repository [here](https://github.com/kubernetes-sigs/kind).

## Let’s get started!

### Setting up the Cluster with Kind:

Once you have Docker, Kind, and kubectl installed, follow the steps below to create the local Kubernetes cluster using Kind:

- Create a file named `kind-argocd.yaml` with the following configuration:
```c
# kind-argocd.yaml
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
  - containerPort: 443
    hostPort: 443
    protocol: TCP
```
- Run the following command to create the Kind cluster:
```c
kind create cluster --config=kind-argocd.yaml
```

### Adding Ingress to the Cluster:

To add ingress support to our Kind cluster, we will install the Nginx Ingress controller. Execute the following command:

```c
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/kind/deploy.yaml
```

### Installing Argo CD:

Now, let’s install Argo CD on our Kubernetes cluster. Run the following commands:

```c
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Configuring Ingress for Argo CD:

To access Argo CD, we need to set up an ingress.

- Create a file named `ingress-argocd.yaml` with the following content:
```c
# ingress-argocd.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    alb.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "false"
spec:
  rules:
  - host: argocd-server.local
    http:
      paths:
      - pathType: Prefix
        path: /
        backend:
          service:
            name: argocd-server
            port:
              number: 443
```
- Apply the ingress using the following command:
```c
kubectl apply -f ingress-argocd.yaml
```

### Obtaining the Argo CD Admin Password

To log in to the Argo CD dashboard, you need the admin password. Run the following command to retrieve the password:

```c
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

### Modifying /etc/hosts:

To access Argo CD using the URL `argocd-server.local`, you need to modify the `/etc/hosts` file on your machine.

- Open the file `/etc/hosts` with your favorite editor and add the following line:
```c
127.0.0.1       argocd-server.local
```

Now you are ready to access Argo CD through [http://argocd-server.local/](http://argocd-server.local/) with the admin credentials obtained in previous step.

## Conclusion

In this article, we have covered the steps required to set up and run Argo CD locally using Kind and Nginx Ingress. By following these instructions, you can experiment with Argo CD and manage your Kubernetes applications in a declarative manner. Enjoy exploring the capabilities of Argo CD in your local environment, and hit the clap button if you find the article informative!

**Reference:**

- [https://argo-cd.readthedocs.io/en/stable/](https://argo-cd.readthedocs.io/en/stable/)
- [https://kubernetes.io/docs/tasks/tools/](https://kubernetes.io/docs/tasks/tools/)
- [https://kind.sigs.k8s.io/docs/user/quick-start/#installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
- [https://magmax.org/en/blog/argocd/](https://magmax.org/en/blog/argocd/)
- [https://github.com/kubernetes-sigs/kind](https://github.com/kubernetes-sigs/kind)

## More from Chirayu Kapoor

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--26b31cece300---------------------------------------)