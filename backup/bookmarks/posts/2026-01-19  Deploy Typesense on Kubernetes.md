---
title: "Deploy Typesense on Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/deploy-typesense-on-kubernetes-893fe452c36a"
author:
  - "[[Akriotis Kyriakos]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-893fe452c36a---------------------------------------)

Deploy a highly available, self-healing Typesense cluster on Kubernetes.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ZSJnPu8ZXG46GPpHv_8OWA.png)

## What is Typesense?

[Typesense](https://typesense.org/) is an open-source search engine designed for speed and simplicity. Its core purpose is to provide instant, relevant search results for applications and websites, making it a popular choice for developers who want powerful search functionality without the complexity of traditional search engines like [Elasticsearch](https://www.elastic.co/elasticsearch).

It supports features such as **full-text search**, **real-time indexing**, **faceted filtering**, and **dynamic sorting**. Typesense also includes advanced capabilities like **vector and semantic search**, allowing it to go beyond simple keyword matching and understand the intent behind queries.

## What are the deployment options?

Typesense offers two main deployment options: the so-called **Typesense Cloud** and **self-hosting**. Typesense Cloud is a fully managed service where the infrastructure, scaling, high availability, and updates are handled for you by Typesense Inc., provided you’re willing to invest a not negligible sum per month for infrastructure and network traffic costs. On the self-hosting frontier, there is official support for Docker, Docker Compose, and native binaries for Linux and macOS — but **not** for Kubernetes.

Deploying Typesense on Kubernetes clusters presents several notable challenges, primarily due to the way Typesense manages cluster membership and consensus using [braft](https://github.com/baidu/braft), an implementation of the [Raft](https://raft.github.io/raft.pdf) algorithm. One of the most persistent issues is **quorum management**. In Kubernetes, pods are ephemeral and their IP addresses can change, which conflicts with Raft’s expectation of stable node identities. This, if not done correct, can lead to situations where the cluster loses quorum or retains outdated information about nodes, **resulting in downtime or the need for manual intervention to restore the cluster**.

**All** the community hacks and workaround so far, for installing Typesense on Kubernetes — such as using plain StatefulSets, Helm charts, custom scripts, sidecars or they just deploy a single node cluster that is not eventually free of the problems mentioned above — fall short as they cannot tackle the actual core problem: that Typesense relies on a stable and consistently updated quorum configuration for its Raft consensus.

## How is Raft working?

[Raft](https://raft.github.io/raft.pdf) nodes operate in one of three possible states: *follower*, *candidate*, or *leader*. Every new node always joins the quorum as a follower. Followers can receive log entries from the leader and participate in voting for electing a leader. If no log entries are received for a specified period of time, a follower transitions to the candidate state. As a candidate, the node can accept votes from its peers nodes. Upon receiving a majority of votes, the candidate is becoming the leader of the quorum. The leader’s responsibilities include handling new log entries and replicating them to other nodes.

Another thing to consider is what happens when the node set changes, when nodes join or leave the cluster. If a quorum of nodes is available, raft can dynamically modify the node set without any issue (this happens every 30sec). But if the cluster cannot form a quorum, then problems start to appear or better to pile up. A cluster with `N` nodes can tolerate a failure of at most `(N-1)/2` nodes without losing its quorum. If the available nodes go below this threshold then two events are taking place:

- **Raft declares the whole cluster as unavailable!** (no leader can be elected, no more log entries can be processed)
- **the remaining nodes are restarted in bootstrap mode!**

In a Kubernetes environment, the nodes are actually `Pods` which are rather **volatile by nature and their lifetime is quite ephemeral** and subject to potential restarts, and that puts the whole concept of raft protocol consensus under a tough spot. As we can read in the official documentation of Typesense when it comes to [recovering a cluster that has lost quorum](https://typesense.org/docs/guide/high-availability.html#recovering-a-cluster-that-has-lost-quorum), it is explicitly stated:

*“If a Typesense cluster loses more than* `*(N-1)/2*` *nodes at the same time, the cluster becomes unstable because it loses quorum and the remaining node(s) cannot safely build consensus on which node is the leader. To avoid a potential split brain issue, Typesense then stops accepting writes and reads* ***until some manual verification and intervention is done****.”*

In production environments, manual intervention is sometimes impossible or undesirable, and downtime for a service like Typesense may be unacceptable. So what is the solution?

## Meet Typesense Kubernetes Operator (TyKO)

[Typesense Kubernetes Operator](https://akyriako.github.io/typesense-operator-docs/) (TyKO) simplifies deploying, scaling, and managing Typesense clusters in Kubernetes by fulfilling the following objectives:

- Provides a Kubernetes-native interface to define and manage Typesense cluster configurations using a CRD named `TypesenseCluster`.
- Simplifies the life-cycle automation of a HA Typesense cluster by handling aspects like: bootstrapping admin API Keys as `Secret`, deploying Typesense as a `StatefulSet`, provisioning Typesense services (headless, discovery and health-check `Services`), actively discovering and updating Typesense’s nodes list and mounting it in a `ConfigMap`, managing the underlying storage with `PersistentVolumeClaims`, exposing Typesense API endpoint via an `Ingress`, exposing Typesense metrics as Prometheus targets and finally provisioning [DocSearch Scrapers](https://github.com/typesense/typesense-docsearch-scraper) instances for content-crawling as `CronJobs`.
- Actively re-discovers the quorum configuration reacting to changes in `ReplicaSet` **without the need of an additional sidecar container.**
- Recovers automatically a cluster that has lost quorum **without the need of manual intervention**,as long as the encountered error is not hardware related.

## Talking is cheap, show me some code

The operator’s installation is done with a simple Helm Chart:

```c
helm repo add typesense-operator https://akyriako.github.io/typesense-operator/
helm repo update

helm upgrade --install typesense-operator typesense-operator/typesense-operator -n typesense-system --create-namespace
```

No complicated wiring, no complex tuning, batteries included — ready to go!

Let’s deploy a cluster now.

The cluster provisioning, as we mentioned before, relies on a new Custom Resource Definition that comes with the operator, called `TypesenseCluster`. The [configuration options of the CRD](https://akyriako.github.io/typesense-operator-docs/docs/crds/) are plenty, but you can start here with a very simple manifest before delving more in it.

```c
apiVersion: ts.opentelekomcloud.com/v1alpha1
kind: TypesenseCluster
metadata:
  name: demo-cluster
spec:
  image: typesense/typesense:29.0
  replicas: 3
  storage:
    size: 100Mi
    storageClassName: <STORAGE_CLASS_NAME>
```

Make sure you replace `<STORAGE_CLASS_NAME>` with the respective value supported from your underlying Kubernetes distribution and within minutes you will get a 3-nodes, high-available, self-healing cluster regardless if you are running on a local development machine with KiND, on bare-metal, on a cloud offered managed Kubernetes service or even on OpenShift.

Of course the cluster can be upgraded to a newer or downgraded to an earlier version of Typesense simply by changing the `spec.image` property. Same counts for `storage.size` as long as your CSI Provider permits to do so.

For more information concerning the internals of the controller and its configuration you can refer to the [documentation](https://akyriako.github.io/typesense-operator-docs/). Make sure, to leave a ⭐️ in the [GitHub repository](https://github.com/akyriako/typesense-operator), and if you are already using TyKO in your organisation would really make a difference if you would consider the option to enlist yourselves as [Adopters](https://akyriako.github.io/typesense-operator-docs/docs/adopters).

talking about: kubernetes, golang, open telekom cloud, aws, openstack, cloudstack, proxmox, sustainability and software carbon emissions.

## More from Akriotis Kyriakos and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--893fe452c36a---------------------------------------)