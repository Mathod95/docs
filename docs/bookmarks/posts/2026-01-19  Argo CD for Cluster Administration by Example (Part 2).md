---
title: "Argo CD for Cluster Administration by Example (Part 2)"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://john-tucker.medium.com/argo-cd-for-cluster-administration-by-example-part-2-3743c0cfe127"
author:
  - "[[John Tucker]]"
---
<!-- more -->

[Sitemap](https://john-tucker.medium.com/sitemap/sitemap.xml)

In a multi cluster environment, learning how to use Argo CD to deploy workloads to targeted clusters.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PQ5PJOSKq0tb7Dc6n8d0ww.png)

[Part 1](https://medium.com/@john-tucker/argo-cd-for-cluster-administration-by-example-part-1-861aea4b1ac4) of this series of articles focused on Argo CD in a single cluster environment; introducing the core concepts: approject, application, and applicationset.

In this article, we switch to Argo CD in a multi cluster environment; learning how to use applicationsets to deploy workloads to targeted clusters.

We will use a hypothetical setup diagramed below where we simulate four clusters, *a*, *b*, *c*, and *d*, distributed across two regions and two environments. They are further differentiated as having GPU node pools or not.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*wjevzURBwR4dVVdh8gSMjQ.png)

In this set up, we will explore using Argo CD to target a workload to clusters that are:

- In *region-1*
- In the *testing* environment
- Have a GPU node pool

Looking at the diagram, the workload should only be targeted to cluster *c.*

## Prerequisites

If you wish to follow along, you will need access to five Kubernetes clusters (*v1.25+*); we will refer to them as *a, b, c, d* (from the diagram) and *hub*.

This series of articles was written using identical [kind](https://kind.sigs.k8s.io/) clusters (*v1.30*); each with a control plane and two worker nodes.

You will also need to have installed the [*kubeclt*](https://kubernetes.io/docs/tasks/tools/) CLI.

While we will exclusively interact with Argo CD via its CRDs throughout this series, we can still use the [*argocd*](https://argo-cd.readthedocs.io/en/stable/cli_installation/) CLI to visualize our work.

**note**: The examples in this article assume that the Kubernetes contexts are named, *kind-hub*, *kind-a*, etc. Likewise it is assumed that the Kubernetes API urls are, *https://hub-control-plane:6443*, *https://hub-control-plane:6443*, etc.

## Multi Cluster Installation

As in the the previous article, we install Argo CD core onto the *hub* cluster.

```c
$ kubectl create namespace argocd \
--context=kind-hub
$ kubectl apply \
--namespace=argocd \
-f https://raw.githubusercontent.com/argoproj/argo-cd/v2.13.3/manifests/core-install.yaml \
--context=kind-hub
```

## Adding Managed Clusters

Starting with cluster *a*, we will add it as an Argo CD managed (by the *hub* cluster) cluster.

As in the previous article, we will avoid using the *argocd* CLI (with its magic) and rather perform this operation by applying Kubernetes manifests.

**note**: The steps here are inspired by the article [*How to Configure Multiple Kubernetes Clusters on Argo CD*](https://devopscube.com/configure-multiple-kubernetes-clusters-argo-cd/).

Managed clusters are represented on the Argo CD cluster (*hub*) as a particular [type of secret](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#clusters) in the same namespace as the Argo CD workloads, here *argocd.*

> Cluster credentials are stored in secrets same as repositories or repository credentials. Each secret must have label argocd.argoproj.io/secret-type: cluster.

Here we work through creating that secret.

**note**: The steps here are for adding generic Kubernetes clusters; the Argo CD documentation provides specific instructions on adding AWS EKS, GCP GKE, and Azure AKS clusters.

We first create a service account, RBAC configuration, and a secret automatically populated with the service account’s token (credentials) on the *a* cluster by applying the following manifest named *argocd-manager.yaml*

```c
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: argocd-manager
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: argocd-manager-role
rules:
- apiGroups:
  - '*'
  resources:
  - '*'
  verbs:
  - '*'
- nonResourceURLs:
  - '*'
  verbs:
  - '*'
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: argocd-manager-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: argocd-manager-role
subjects:
- kind: ServiceAccount
  name: argocd-manager
  namespace: kube-system
---
apiVersion: v1
kind: Secret
metadata:
  name: argocd-manager-token
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: argocd-manager
type: kubernetes.io/service-account-token
```

with the command

```c
$ kubectl apply \
-f argocd-manager.yaml \
--context=kind-a
```

We then temporarily populate the *CA* and *TOKEN* environment variables on our workstation with the *a* cluster certificate authority certificate and the service account’s token.

```c
$ CA=$(kubectl get -n kube-system secret/argocd-manager-token --context=kind-a -o jsonpath='{.data.ca\.crt}')
$ TOKEN=$(kubectl get -n kube-system secret/argocd-manager-token --context=kind-a -o jsonpath='{.data.token}' | base64 --decode)
```

Using these environment variables, we create the desired secret on the Argo CD cluster (*hub*).

```c
cat <<EOF | kubectl apply --context=kind-hub -f -
apiVersion: v1
kind: Secret
metadata:
  labels:
    argocd.argoproj.io/secret-type: cluster
  name: cluster-a
  namespace: argocd
type: Opaque
stringData:
  config: |
    {
      "bearerToken": "${TOKEN}",
      "tlsClientConfig": {
        "serverName": "a-control-plane",
        "caData": "${CA}"
      }
    }
  name: a
  server: https://a-control-plane:6443
EOF
```

We can bring up the web UI to visualize the managed clusters.

```c
$ kubectl config use-context kind-hub
$ kubectl config set-context \
--current \
--namespace=argocd
$ argocd login --core
$ argocd admin dashboard -n argocd
```

From the the menu *Settings > Clusters*, we indeed can now see cluster *a*.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Mye2bMOJ38IYS3nKI3Lsvw.png)

Until an application is deployed to a cluster, the connection status will show *Unknown* (after which it will show *Successful*).

We repeat adding clusters *b*, *c*, and *d* as Argo CD managed (by the *hub* cluster) clusters.

## ApplicationSet

In Part 1, we were introduced to applicationsets, generators, and, in particular, the Git directory generator (generates parameters using the directory structure of a specified Git repository). We used them to deploy multiple applications to a single cluster as a unit.

In this article, we be using an applicationset with a [cluster generator](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Cluster/).

> In Argo CD, managed clusters are stored within Secrets in the Argo CD namespace. The ApplicationSet controller uses those same Secrets to generate parameters to identify and target available clusters.
> 
> For each cluster registered with Argo CD, the Cluster generator produces parameters based on the list of items found within the cluster secret.

Here we will be using a label selector.

> A label selector may be used to narrow the scope of targeted clusters to only those matching a specific label:

Here we execute the commands to label the secrets that represent clusters *a, b, c*, and *d* with the labels (from the diagram): *region*, *environment*, and *gpu*.

```c
$ kubectl label secret cluster-a region=region-1 \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-b region=region-1 \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-c region=region-1 \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-d region=region-2 \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-a environment=production \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-b environment=testing \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-c environment=testing \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-d environment=testing \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluster-c gpu=true \
--namespace=argocd \
--context=kind-hub
$ kubectl label secret cluser-d gpu=true \
--namespace=argocd \
--context=kind-hub
```

**note**: It takes some getting used to thinking of these secrets as representing managed clusters. The key is that these secrets are labeled with  
*argocd.argoproj.io/secret-type: cluster.*

Using the web UI, we indeed can see these labels when inspecting a cluster.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*dYFobFCvSsVC5gtHDcyRhw.png)

Now we create the applicationset manifest; *simple-applicationset.yaml.* The syntax of the cluster generator is fairly self-explanatory. Here we see the template parameters:

- *name*: The name of the cluster from the *name* value in the secret
- *server*: The URL of the cluster’s Kubernetes API from the *server* value in the secret
```c
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: simple
  namespace: argocd
spec:
  goTemplate: true
  goTemplateOptions: ["missingkey=error"]
  generators:
  - clusters:
      selector:
        matchLabels:
          environment: "testing"
          gpu: "true"
          region: "region-1"
  template:
    metadata:
      name: "{{.name}}-simple"
    spec:
      project: default
      source:
        path: simple
        repoURL: https://github.com/larkintuckerllc/argocd-examples
        targetRevision: HEAD
      destination:
        server: "{{.server}}"
        namespace: default
      syncPolicy:
        automated: {}
```

We apply this manifest to the *hub* cluster.

```c
$ kubectl apply \
-f simple-applicationset.yaml \
--context=kind-hub
```

We can now indeed see that the applicationset created the targeted application on cluster *c*.

```c
$ kubectl get applications \
--namespace=argocd \
--context=kind-hub
NAME       SYNC STATUS   HEALTH STATUS
c-simple   Synced        Healthy
```

We could describe the applicationset to get all the details.

```c
% kubectl describe application c-simple --namespace=argocd --context=kind-hub
Name:         c-simple
Namespace:    argocd
...
  Sync:
    Compared To:
      Destination:
        Namespace:  default
        Server:     https://c-control-plane:6443
      Source:
        Path:             simple
        Repo URL:         https://github.com/larkintuckerllc/argocd-examples
        Target Revision:  HEAD
    Revision:             84b7b0eede6592407749a0f4478993a5c9c56705
    Status:               Synced
Events:
  Type    Reason              Age    From                           Message
  ----    ------              ----   ----                           -------
  Normal  OperationStarted    7h27m  argocd-application-controller  Initiated automated sync to '84b7b0eede6592407749a0f4478993a5c9c56705'
  Normal  ResourceUpdated     7h27m  argocd-application-controller  Updated sync status:  -> OutOfSync
  Normal  ResourceUpdated     7h27m  argocd-application-controller  Updated health status:  -> Healthy
  Normal  ResourceUpdated     7h27m  argocd-application-controller  Updated sync status: OutOfSync -> Synced
  Normal  OperationCompleted  7h27m  argocd-application-controller  Sync operation to 84b7b0eede6592407749a0f4478993a5c9c56705 succeeded
```

or use the web UI which is easier to interpret.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*EJI5avJ42olmF00_zLX5yw.png)

## Wrap Up

In this series we just touched upon the power of applicationsets with their generators and templating. Looking at the documentation on [generators](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators/) we see that there are currently nine generators (we explored only two of them in this series).

There is even a [plugin generator](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Plugin/) that can make HTTP requests to provide the parameters. This provides a quick and powerful mechanism to customize Argo CD using familiar technology. Wow.

Broad infrastructure, development, and soft-skill background

## More from John Tucker

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--3743c0cfe127---------------------------------------)