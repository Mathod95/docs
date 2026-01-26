---
title: "Mon été avec Cilium et EKS (Partie 1)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-1-99a66ed6671f"
author:
  - "[[Joseph Ligier]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## Introduction

N ous allons voir Cilium sous toutes ces facettes avec EKS, comment il s’intègre à l’environnement d’AWS. Pour cette première partie, on va voir ce qu’est Cilium et EKS et comment installer rapidement Cilium sur un cluster EKS.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*NaWuw7RC617aWuGrxmcC_g.jpeg)

Un été studieux

## Qu’est-ce qu’AWS EKS et Cilium?

A WS EKS est un service géré par AWS. Il permet de créer des clusters Kubernetes. Kubernetes est un orchestrateur de containers. J’ai choisi ce service car je le connais bien et que ça permet de confronter cilium à un “vrai” cluster et non à des clusters de dev comme kind ou minikube.

Cilium est un plugin réseau (ou CNI: Container Network Interface) pour Kubernetes. Ce projet est géré par la société Isovalent. Contrairement à la plupart des autres CNI qui utilisent iptables/netfilter pour gérer les modifications réseaux, Cilium utilise l’eBPF. Pour faire simple, l’eBPF a beaucoup d’avantages sur iptables. Par exemple, la performance est meilleure, l’identification des trames réseaux est plus simple qui permet ainsi d’avoir une meilleure observabilité du réseau. Ainsi Isovalent a créé un outil qui s’appelle Hubble permettant de visualiser les flux réseaux dans le réseau cilium à l’instar de tcpdump dans un modèle traditionnel.

Par défaut, AWS EKS utilise un autre plugin réseau AWS VPC CNI. Pourquoi utiliser Cilium plutôt que le plugin par défaut? Nous allons le voir pendant tout cet été mais la première chose qui me vient en tête est l’absence de Network Policies, des règles qui permettent de dire je veux que tel pod accède à tel pod via tel port. Cela n’est pas possible par exemple avec le CNI par défaut. Nous allons aussi explorer des limitations au niveau de Cilium. Tout n’est pas rose non plus.

Pour ce premier épisode, nous allons faire (très) simple: on va déployer un cluster eks et installer cilium.

## Pré-requis

- un compte AWS avec des access keys
- un peu d’argent (Pour une heure: 0.1 $ pour le cluster eks, environ 0.08 $ pour deux t3.medium et 0.05 $ pour la nat gateway). Durée minimale: environ 30 minutes
- eksctl: outil pour déployer des clusters eks
- aws iam authenticator: outil pour s’authentifier auprès du cluster eks
- aws cli: outil pour communiquer avec l’API d’AWS
- kubectl: outil pour controler le cluster kubernetes
- cilium cli: outil pour installer cilium

Comme AWS EKS est un service payant, il est conseillé d’avoir bien installé les outils avant de créer le cluster.

## Déploiement d’un cluster AWS EKS

Nous allons voir comment déployer rapidement un cluster AWS EKS.

On va exporter les access keys:

```c
export AWS_DEFAULT_REGION=ch-ange-1
export AWS_ACCESS_KEY_ID="CHANGEME"
export AWS_SECRET_ACCESS_KEY="CHANGEME"
```

On va créer un fichier yaml pour eksctl:

```c
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: basic-cilium
  region: us-east-1
  version: "1.27"

managedNodeGroups:
- name: ng-1
  instanceType: t3.medium
  # taint nodes so that application pods are
  # not scheduled/executed until Cilium is deployed.
  # Alternatively, see the note above regarding taint effects.
  taints:
   - key: "node.cilium.io/agent-not-ready"
     value: "true"
     effect: "NoExecute"
```

Je déploie sur us-east-1 mais si vous préférez utilisez une autre région, n’hésitez pas à changer.

On va lancer la commande suivante:

```c
eksctl create cluster -f ./files/eks-cilium.yaml
```

Cela va prendre un temps important (de l’ordre de 15 minutes).

Voici ce que cette commande va créer:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*LvxOrlOsaNdSWvTJIXRGyw.png)

Un schéma pour vous faire patienter

Une fois que c’est fini, on va pouvoir lancer des commandes kubectl:

```c
kubectl get node
NAME STATUS ROLES AGE VERSION
ip-192–168–11–135.ec2.internal Ready <none> 4m18s v1.27.1-eks-2f008fe
ip-192–168–56–129.ec2.internal Ready <none> 4m22s v1.27.1-eks-2f008fe
```

## Installation de Cilium

Rien de plus simple avec la cli cilium:

```c
cilium install
🔮 Auto-detected Kubernetes kind: EKS
ℹ️  Using Cilium version 1.13.3
🔮 Auto-detected cluster name: basic-cilium-us-east-1-eksctl-io
🔮 Auto-detected datapath mode: aws-eni
🔮 Auto-detected kube-proxy has been installed
🔥 Patching the "aws-node" DaemonSet to evict its pods...
ℹ️  helm template --namespace kube-system cilium cilium/cilium --version 1.13.3 --set cluster.id=0,cluster.name=basic-cilium-us-east-1-eksctl-io,egressMasqueradeInterfaces=eth0,encryption.nodeEncryption=false,eni.enabled=true,ipam.mode=eni,kubeProxyReplacement=disabled,operator.replicas=1,serviceAccounts.cilium.name=cilium,serviceAccounts.operator.name=cilium-operator,tunnel=disabled
ℹ️  Storing helm values file in kube-system/cilium-cli-helm-values Secret
🔑 Created CA in secret cilium-ca
🔑 Generating certificates for Hubble...
🚀 Creating Service accounts...
🚀 Creating Cluster roles...
🚀 Creating ConfigMap for Cilium version 1.13.3...
🚀 Creating Agent DaemonSet...
🚀 Creating Operator Deployment...
⌛ Waiting for Cilium to be installed and ready...
✅ Cilium was successfully installed! Run 'cilium status' to view installation health
```

On voit que cilium détecte pas mal de chose automatiquement, par exemple qu’il va installer sur EKS. Il va installer la version 1.13.3. Il va donc supprimer les pods qui composent l’aws vpc cni. Il va ensuite générer toutes les dépendances permettant d’installer cilium sur le cluster.

La commande *cilium status* va permettre d’avoir un aperçu si cela a bien été installé:

```c
cilium status --wait
    /¯¯\
 /¯¯\__/¯¯\    Cilium:             OK
 \__/¯¯\__/    Operator:           OK
 /¯¯\__/¯¯\    Envoy DaemonSet:    disabled (using embedded mode)
 \__/¯¯\__/    Hubble Relay:       disabled
    \__/       ClusterMesh:        disabled

Deployment        cilium-operator    Desired: 1, Ready: 1/1, Available: 1/1
DaemonSet         cilium             Desired: 2, Ready: 2/2, Available: 2/2
Containers:       cilium-operator    Running: 1
                  cilium             Running: 2
Cluster Pods:     2/2 managed by Cilium
Image versions    cilium             quay.io/cilium/cilium:v1.13.3@sha256:77176464a1e11ea7e89e984ac7db365e7af39851507e94f137dcf56c87746314: 2
                  cilium-operator    quay.io/cilium/operator-aws:v1.13.3@sha256:394c40d156235d3c2004f77bb73402457092351cc6debdbc5727ba36fbd863ae: 1
```

On rajoute l’option wait pour attendre que l’installation soit bien finie.

Vérifions maintenant que l’installation s’est bien passée:

```c
cilium connectivity test
```

La commande va faire plein de tests réseaux. Cela va donc prendre un temps important.

En exclusivité voici le résumé final du test:

```c
📋 Test Report
❌ 4/42 tests failed (20/300 actions), 12 tests skipped, 1 scenarios skipped:
Test [no-policies]:
  ❌ no-policies/pod-to-host/ping-ipv4-1: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> 54.243.4.228 (54.243.4.228:0)
  ❌ no-policies/pod-to-host/ping-ipv4-3: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> 54.158.35.146 (54.158.35.146:0)
  ❌ no-policies/pod-to-host/ping-ipv4-5: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> 54.158.35.146 (54.158.35.146:0)
  ❌ no-policies/pod-to-host/ping-ipv4-7: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> 54.243.4.228 (54.243.4.228:0)
Test [no-policies-extra]:
  ❌ no-policies-extra/pod-to-remote-nodeport/curl-0: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> cilium-test/echo-same-node (echo-same-node:8080)
  ❌ no-policies-extra/pod-to-remote-nodeport/curl-1: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> cilium-test/echo-other-node (echo-other-node:8080)
  ❌ no-policies-extra/pod-to-remote-nodeport/curl-2: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> cilium-test/echo-other-node (echo-other-node:8080)
  ❌ no-policies-extra/pod-to-remote-nodeport/curl-3: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> cilium-test/echo-same-node (echo-same-node:8080)
  ❌ no-policies-extra/pod-to-local-nodeport/curl-0: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> cilium-test/echo-other-node (echo-other-node:8080)
  ❌ no-policies-extra/pod-to-local-nodeport/curl-1: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> cilium-test/echo-same-node (echo-same-node:8080)
  ❌ no-policies-extra/pod-to-local-nodeport/curl-2: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> cilium-test/echo-same-node (echo-same-node:8080)
  ❌ no-policies-extra/pod-to-local-nodeport/curl-3: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> cilium-test/echo-other-node (echo-other-node:8080)
Test [allow-all-except-world]:
  ❌ allow-all-except-world/pod-to-host/ping-ipv4-1: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> 54.158.35.146 (54.158.35.146:0)
  ❌ allow-all-except-world/pod-to-host/ping-ipv4-3: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> 54.243.4.228 (54.243.4.228:0)
  ❌ allow-all-except-world/pod-to-host/ping-ipv4-5: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> 54.158.35.146 (54.158.35.146:0)
  ❌ allow-all-except-world/pod-to-host/ping-ipv4-7: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> 54.243.4.228 (54.243.4.228:0)
Test [host-entity]:
  ❌ host-entity/pod-to-host/ping-ipv4-1: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> 54.158.35.146 (54.158.35.146:0)
  ❌ host-entity/pod-to-host/ping-ipv4-3: cilium-test/client-6965d549d5-hwmbt (192.168.61.62) -> 54.243.4.228 (54.243.4.228:0)
  ❌ host-entity/pod-to-host/ping-ipv4-5: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> 54.158.35.146 (54.158.35.146:0)
  ❌ host-entity/pod-to-host/ping-ipv4-7: cilium-test/client2-76f4d7c5bc-5h4xr (192.168.63.171) -> 54.243.4.228 (54.243.4.228:0)
```

On voit déjà que:

- le ping des pods vers les hosts ne fonctionne pas.
- le test des nodeports ne fonctionne pas

C’est déjà pas mal, on n’a pas forcément besoin du ping ni des nodeports.

Si on veut résoudre le problème, il suffit d’ouvrir le ping et les ports tcp des nodeports (30000–32767) au niveau du security group qui concernent les ec2. On aura alors:

```c
✅ All 42 tests (300 actions) successful, 12 tests skipped, 1 scenarios skipped.
```

La première partie est finie. Vous pouvez voir cette installation résumée ici: [https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks.md](https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks.md)

Dans la [prochaine partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-2-ea8ba7a9dcae), nous verrons ce qui est “caché” dans l’installation avec la cli cilium avec l’installation avec helm.

## More from Joseph Ligier

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--99a66ed6671f---------------------------------------)