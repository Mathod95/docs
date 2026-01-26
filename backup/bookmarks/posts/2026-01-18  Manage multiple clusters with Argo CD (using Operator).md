---
title: "Manage multiple clusters with Argo CD (using Operator)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://abhishekveeramalla-av.medium.com/manage-multiple-clusters-with-openshift-gitops-based-on-argo-cd-84e1fa761218"
author:
  - "[[Abhishek Veeramalla]]"
---
<!-- more -->

[Sitemap](https://abhishekveeramalla-av.medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Piz4z2fqRd00h0gX09Tebw.png)

Manage multiple clusters with OpenShift GitOps

Argo CD Instance can be used to manage deployment of manifests to the same cluster or multiple clusters.

The model where a single Argo CD Instance is used to manage multiple clusters is commonly referred to as hub and spoke model(as shown in the picture above).

This model is very popular for implementing GitOps with Argo CD as

1. Easy to setup.
2. Easy to onboard new clusters to the GitOps model.
3. Easy to add, remove or update Argo CD configuration(A single instance).
4. Disaster recovery is simple.
5. Administrators find it easy to manage RBAC as everything is at one place.

However this model also comes up with its own challenges such as “Single point of failure” as a single Argo CD instance is managing multiple clusters configuration. This situation can be improved by configuring Argo CD in HA mode.

In this blog post, we will learn

1. How to add remote clusters to Argo CD.
2. How to configure Argo CD in HA mode.
3. Recommendation for HA mode.

## How to add Clusters to Argo CD

Note: Adding clusters is not supported through UI at this point. This is only possible using the Argo CD CLI.

Step 1:  
Download the Argo CD CLI  
[https://argo-cd.readthedocs.io/en/stable/cli\_installation/](https://argo-cd.readthedocs.io/en/stable/cli_installation/)

Step 2:  
Add a cluster using the below command.

```c
$ argocd cluster add <CONTEXT> — server <Argo CD Server Route url>

WARNING: This will create a service account \`argocd-manager\` on the cluster referenced by context \`default/api-ci-<>:6443/kube:admin\` with full cluster level privileges. Do you want to continue [y/N]? y
INFO[0004] ServiceAccount "argocd-manager" created in namespace "kube-system" 
INFO[0004] ClusterRole "argocd-manager-role" created    
INFO[0004] ClusterRoleBinding "argocd-manager-role-binding" created 
INFO[0005] Created bearer token secret for ServiceAccount "argocd-manager" 
Cluster 'https://api.ci-<>.com:6443' added
```

In the above command CONTEXT refers to the context of cluster that you want to add. You can get the context by running

```c
kubectl config get-contexts
```

Step 3:  
Verify if the cluster is added successfully.

```c
argocd cluster list

SERVER                           NAME                                    VERSION  STATUS   MESSAGE    
https://api.ci-ln-<>.com:6443    default/api-ci-<>-com:6443/kube:admin            Active   
https://kubernetes.default.svc   in-cluster                                       Unknown
```

you can also get this information from the UI.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PQ4Mm2qhPL5XWlNjTDqUhw.png)

Clusters List

You can explore more about the argocd cluster add command reference with arguments [here](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_cluster_add/).

Step 4:  
Deploy manifests to the target cluster.

CLI:  
Apply the below manifest in the namespace your Argo CD is installed. In the below manifest, destination field refers to the target cluster where manifests are deployed.

```c
apiVersion: argoproj.io/v1beta1
kind: Application
metadata:
  name: test
  namespace: openshift-gitops
spec:
  destination:
    namespace: default
    server: 'https://api.ci-<>.com:6443'
  project: default
  source:
    path: guestbook
    repoURL: 'https://github.com/argoproj/argocd-example-apps'
```

UI:  
Login to the Argo CD UI, Click NEW APP, Provide details for sample guest-book application as shown below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*vro5WBfimOSrSgyAsWAXJQ.png)

Deploy application to a different cluster using Argo CD UI

Sync the Argo CD application to complete the deployment.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*m87cwnPS2f4kvKJSHRnIwA.png)

Sync successful

## How to run Argo CD in HA Mode

To upgrade an existing Argo CD instance to HA configuration mode.

- Go to **Administration** → **CustomResourceDefinitions**.
- Search for `argocds.argoproj.io` and click `ArgoCD` custom resource definition (CRD).
- On the **CustomResourceDefinition details** page, click the **Instances** tab, and then click **ArgoCD**.
- Update the YAML file of your Argo CD Instance with HA configuration as shown below.
```c
apiVersion: argoproj.io/v1beta1
kind: ArgoCD
metadata:
  name: argocd 
  namespace: openshift-gitops 
spec:
  ha:
    enabled: true 
  ...
  ...
```

## Recommendations for Argo CD HA Mode

**Sharding**

If the controller is managing too many clusters and uses too much memory then you can shard clusters across multiple controller replicas. This is useful to relieve memory pressure on the controller component.

To enable sharding, modify the Argo CD CR configuration to look like below.

```c
apiVersion: argoproj.io/v1beta1
kind: ArgoCD
metadata:
  name: example-argocd
  labels:
    example: controller
spec:
  controller:
    sharding:
      enabled: true
      replicas: 5
```

**Processors**

Each controller replica uses two separate queues to process application reconciliation (milliseconds) and app syncing (seconds). The number of queue processors for each queue is controlled by `--status-processors` (20 by default) and `--operation-processors` (10 by default) flags. Increase the number of processors if your Argo CD instance manages too many applications. For 1000 application we use 50 for `--status-processors` and 25 for `--operation-processors`

```c
apiVersion: argoproj.io/v1beta1
kind: ArgoCD
metadata:
  name: example-argocd
  labels:
    example: controller
spec:
  controller:
    processors:
      operation: 10
      status: 20
    resources: {}
```

**Repo Server Timeout**

The manifest generation typically takes the most time during reconciliation. The duration of manifest generation is limited to make sure the controller refresh queue does not overflow. The app reconciliation fails with `Context deadline exceeded` error if the manifest generation is taking too much time. As a workaround increase the repo-server timeout seconds.

```c
apiVersion: argoproj.io/v1alpha1
kind: ArgoCD
metadata:
  name: example-argocd
  labels:
    example: controller
spec:
  controller:
    env:
    - name: ARGOCD_APPLICATION_CONTROLLER_REPO_SERVER_TIMEOUT_SECONDS
      value: '120'
```

You can find more tuning options in the Argo CD official [docs](https://argo-cd.readthedocs.io/en/stable/operator-manual/high_availability/#argocd-application-controller).

Just another geek who believes in sharing:)

## More from Abhishek Veeramalla

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--84e1fa761218---------------------------------------)