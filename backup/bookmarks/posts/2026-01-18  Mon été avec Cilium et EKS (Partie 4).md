---
title: "Mon été avec Cilium et EKS (Partie 4)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-4-d45f3829ca82"
author:
  - "[[Joseph Ligier]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## Introduction

D ans la [partie précédente](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-3-2e3d6882e643), nous avons vu comment utiliser une fonctionnalité intéressante des ENIs qui permet d’avoir plus de pods par instance. Dans cette partie, nous allons voir le *chaining mode* et la gestion de la bande passante avec Cilium.

## Qu’est-ce donc le chaining mode?

Le *chaining mode* (le mode d’enchaînement?) permet de garder le aws vpc cni et d’utiliser les fonctionnalités de Cilium. Si vous utilisez déjà par exemple les security groups via l’aws vpc cni, vous pourrez également utiliser la gestion de la bande passante.

Autre intérêt: si vous avez déjà un cluster eks et aws vpc cni, la migration sera plus facile à effectuer, notamment si vous avez besoin que votre plateforme ne s’arrête pas pendant quelques temps. Ça peut être aussi un premier pas dans le monde de Cilium.

Notez bien qu’on parle ici dans un contexte AWS. Si vous utilisez déjà, par exemple, le plugin Calico, on peut ajouter Cilium à Calico pour avoir certaines fonctionnalités que n’a pas Calico.

## Que va faire Cilium dans cette galère?

Cilium va déléguer certaines de ses fonctionnalités à aws vpc cni, notamment l’IPAM (IP Address Management, c’est à dire la gestion des IPs), la création de l’IP sur le serveur, le routage, les interfaces etc. Mais Cilium fera le reste principalement via eBPF: network policy, load balancing, gestion de la bande passante, etc. J’ai l’impression que l’opérateur Cilium va moins travailler par contre.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ixMMF-yWIiZe5KWxkqViSA.png)

Cilium va discuter avec l’eBPF via l’eBPF map pour s’interfacer avec le vpc cni qui fait le reste

Nous allons maintenant voir comment on fait.

## Pré-requis

- un compte AWS avec des access keys
- un peu d’argent (0.1 $ / heure pour le cluster eks, environ 0.08 $ / heure pour deux t3.medium). Durée minimale: environ 30 minutes
- eksctl: outil pour déployer des clusters eks
- aws iam authenticator: outil pour s’authentifier auprès du cluster eks
- aws cli: outil pour communiquer avec l’API d’AWS
- kubectl: outil pour controler le cluster kubernetes
- cilium cli: outil pour gérer cilium
- helm: outil pour installer des applications kubernetes

Comme AWS EKS est un service payant, il est conseillé d’avoir bien installé les outils avant de créer le cluster.

## Déploiement d’un cluster AWS EKS

Le déploiement du cluster EKS est le même que pour [la partie 1](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-1-99a66ed6671f), je laisse vous y reporter.

## Installation de Cilium

Un pré-requis si vous utilisez un cluster déjà existant est d’avoir une version minimum du vpc cni de 1.11.2. Sur mon cluster on a la version 1.12.6:

```c
kubectl -n kube-system get ds/aws-node -o json | jq -r '.spec.template.spec.containers[0].image'
XXXXXXXXXXX.dkr.ecr.us-east-1.amazonaws.com/amazon-k8s-cni:v1.12.6-eksbuild.2
```

Pour l’installer, il suffit de taper:

```c
helm repo add cilium https://helm.cilium.io/
helm repo update
helm install cilium cilium/cilium --version 1.13.4 \
                                  --namespace kube-system \
                                  --set cni.chainingMode=aws-cni \
                                  --set cni.exclusive=false \
                                  --set enableIPv4Masquerade=false \
                                  --set tunnel=disabled \
                                  --set endpointRoutes.enabled=true
```

Ensuite on peut vérifier que tout fonctionne bien:

```c
cilium status --wait
    /¯¯\
 /¯¯\__/¯¯\    Cilium:             OK
 \__/¯¯\__/    Operator:           OK
 /¯¯\__/¯¯\    Envoy DaemonSet:    disabled (using embedded mode)
 \__/¯¯\__/    Hubble Relay:       disabled
    \__/       ClusterMesh:        disabled

Deployment        cilium-operator    Desired: 2, Ready: 2/2, Available: 2/2
DaemonSet         cilium             Desired: 2, Ready: 2/2, Available: 2/2
Containers:       cilium             Running: 2
                  cilium-operator    Running: 2
Cluster Pods:     2/2 managed by Cilium
Image versions    cilium-operator    quay.io/cilium/operator-generic:v1.13.4@sha256:09ab77d324ef4d31f7d341f97ec5a2a4860910076046d57a2d61494d426c6301: 2
                  cilium             quay.io/cilium/cilium:v1.13.4@sha256:bde8800d61aaad8b8451b10e247ac7bdeb7af187bb698f83d40ad75a38c1ee6b:
```

On voit ainsi que Cilium ne gère plus du tout les ENIs:

```c
kubectl describe ciliumnodes.cilium.io ip-192-168-29-49.ec2.internal
Name:         ip-192-168-29-49.ec2.internal
Namespace:
Labels:       alpha.eksctl.io/cluster-name=basic-cilium
              alpha.eksctl.io/nodegroup-name=ng-1
              beta.kubernetes.io/arch=amd64
              beta.kubernetes.io/instance-type=t3.medium
              beta.kubernetes.io/os=linux
              eks.amazonaws.com/capacityType=ON_DEMAND
              eks.amazonaws.com/nodegroup=ng-1
              eks.amazonaws.com/nodegroup-image=ami-061112afff4339a5f
              eks.amazonaws.com/sourceLaunchTemplateId=lt-02712f3f06910720b
              eks.amazonaws.com/sourceLaunchTemplateVersion=1
              failure-domain.beta.kubernetes.io/region=us-east-1
              failure-domain.beta.kubernetes.io/zone=us-east-1f
              k8s.io/cloud-provider-aws=adc9b7ebbe741f22290eef4d44b6387c
              kubernetes.io/arch=amd64
              kubernetes.io/hostname=ip-192-168-29-49.ec2.internal
              kubernetes.io/os=linux
              node.kubernetes.io/instance-type=t3.medium
              topology.kubernetes.io/region=us-east-1
              topology.kubernetes.io/zone=us-east-1f
Annotations:  <none>
API Version:  cilium.io/v2
Kind:         CiliumNode
Metadata:
  Creation Timestamp:  2023-07-10T10:08:18Z
  Generation:          3
  Owner References:
    API Version:     v1
    Kind:            Node
    Name:            ip-192-168-29-49.ec2.internal
    UID:             dc00e15b-01e3-43f8-9761-baf512030cf0
  Resource Version:  2037
  UID:               e95c656e-60d2-46a6-870b-84db61c25457
Spec:
  Addresses:
    Ip:    192.168.29.49
    Type:  InternalIP
    Ip:    3.236.87.89
    Type:  ExternalIP
    Ip:    10.0.0.121
    Type:  CiliumInternalIP
  Alibaba - Cloud:
  Azure:
  Encryption:
  Eni:
  Health:
  Ingress:
  Ipam:
    Pod CID Rs:
      10.0.0.0/24
Status:
  Alibaba - Cloud:
  Azure:
  Eni:
  Ipam:
    Operator - Status:
Events:  <none>
```

On peut aussi voir que les IPs internes de cilium ne sont pas utilisés par des ENIs vu qu’ils ne sont pas dans le même réseau que le VPC:

```c
kubectl get ciliumnode
NAME                             CILIUMINTERNALIP   INTERNALIP       AGE
ip-192-168-29-49.ec2.internal    10.0.0.121         192.168.29.49    53m
ip-192-168-50-201.ec2.internal   10.0.1.54          192.168.50.201   53m
```

Voici une commande pour savoir si on est en chaining mode:

```c
kubectl exec -it ds/cilium -n kube-system -c cilium-agent -- cilium status | grep Chaining
CNI Chaining:            aws-cni
```

Pour en savoir plus sur le chaining mode:## [AWS VPC CNI plugin — Cilium 1.15.0-dev documentation](https://docs.cilium.io/en/latest/installation/cni-chaining-aws-cni/?source=post_page-----d45f3829ca82---------------------------------------)

This guide explains how to set up Cilium in combination with the AWS VPC CNI plugin. In this hybrid mode, the AWS VPC…

docs.cilium.io

[View original](https://docs.cilium.io/en/latest/installation/cni-chaining-aws-cni/?source=post_page-----d45f3829ca82---------------------------------------)

L’installation est résumé [ici](https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-chaining.md).

## Gestion de la bande passante

Il y a une vidéo récente (à l’heure où je l’écris) sur le sujet:

Vous verrez que ce n’est pas possible dans kind

Kubernetes permet par défaut de limiter le CPU et la RAM les containers via les cgroups du kernel linux.

L’eBPF permet également de limiter la bande passante. Ainsi l’agent Cilium peut discuter avec l’eBPF via sa map pour limiter la bande passante **sortante** (**egress**) des pods. La limitation des flux entrants (**ingress**) n’est pas possible.

Notez bien que cette fonctionnalité n’est pas exclusive au *chaining mode*. On peut l’activer pour tout autre type d’installation.

Comment activer cette fonctionnalité? Rien de plus simple:

```c
helm upgrade cilium cilium/cilium --version 1.13.4 \
  --reuse-values \
  --namespace kube-system \
  --set bandwidthManager.enabled=true
```

Et redémarrer les agents Cilium de chaque nœud:

```c
kubectl -n kube-system rollout restart ds/cilium
```

Pour vérifier que ça a bien fonctionné:

```c
kubectl -n kube-system exec ds/cilium -- cilium status | grep BandwidthManager
BandwidthManager:        EDT with BPF [CUBIC] [eth0, eth1]
```
- EDT: Earliest Departure Time, c’est la méthode pour limiter le réseau. On envoie les paquets réseaux en fonction du temps de départ prévu selon la limitation de la bande passante (pour plus d’explication, voir [ici](https://isovalent.com/blog/post/addressing-bandwidth-exhaustion-with-cilium-bandwidth-manager/#ciliums-bandwidth-manager-implementation-ce74af4e-acf5-4d89-b564-ee6fbaa02fe0)).
- CUBIC: c’est un algorithme pour éviter la congestion du réseau. Il est également possible d’utiliser un autre algorithme BBR qui est bien meilleur en cas de trafic important. Mais il faut que le noyau linux des nœuds soit assez récent (au moins 5.18).

Maintenant qu’on a activé l’option dans Cilium, il ne reste plus qu’à tester la fonctionnalité.

Il suffit de rajouter une annotation au pod cible, par exemple:

```c
kubernetes.io/egress-bandwidth: "10M"
```

On limite ici à 10 Mbit/s:

```c
---
apiVersion: v1
kind: Pod
metadata:
  annotations:
    # Limits egress bandwidth to 10Mbit/s.
    kubernetes.io/egress-bandwidth: "10M"
  labels:
    # This pod will act as server.
    app.kubernetes.io/name: netperf-server
  name: netperf-server
spec:
  containers:
  - name: netperf
    image: cilium/netperf
    ports:
    - containerPort: 12865
---
apiVersion: v1
kind: Pod
metadata:
  # This Pod will act as client.
  name: netperf-client
spec:
  affinity:
    # Prevents the client from being scheduled to the
    # same node as the server.
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - netperf-server
        topologyKey: kubernetes.io/hostname
  containers:
  - name: netperf
    args:
    - sleep
    - infinity
    image: cilium/netperf
```
```c
kubectl apply -f bandwidth-test.yaml
```

On crée deux pods:

- netperf-client: là où on peut lancer les commandes netperf
- netperf-server: là où est exécuté réellement netperf

On va récupérer l’ip du pod netperf-server:

```c
NETPERF_SERVER_IP=$(kubectl get pod netperf-server -o jsonpath='{.status.podIP}')
```

Puis on va tester le flux sortant de netperf-server vers netperf-client

```c
kubectl exec netperf-client --netperf -t TCP_MAERTS -H "${NETPERF_SERVER_IP}"
```
- TCP\_MAERTS permet de faire cela. On aurait voulu tester le flux sortant de netperf-client, il suffisait de mettre à la place TCP\_STREAM (les lettres sont inversés)

Le résultat est le suivant:

```c
MIGRATED TCP MAERTS TEST from 0.0.0.0 (0.0.0.0) port 0 AF_INET to 192.168.62.98 (192.168) port 0 AF_INET
Recv   Send    Send
Socket Socket  Message  Elapsed
Size   Size    Size     Time     Throughput
bytes  bytes   bytes    secs.    10^6bits/sec

131072  20480  20480    10.01       9.91
```
- 9,91 < 10 Mbits/s on est bon!

Comment faire pour voir la liste des limitations de bande passante sur un nœud?

Il suffit de lancer la commande “ *cilium bpf bandwidth list* ” sur l’agent cilium du nœud cible:

```c
kubectl exec -it -n kube-system cilium-mfqkg -c cilium-agent -- cilium bpf bandwidth list
IDENTITY   EGRESS BANDWIDTH (BitsPerSec)
124        10M
```

On voit ainsi que les pods qui ont comme id 124 sont limités à 10 Mbit/s.

```c
kubectl get ciliumendpoint
NAME             ENDPOINT ID   IDENTITY ID   INGRESS ENFORCEMENT   EGRESS ENFORCEMENT   VISIBILITY POLICY   ENDPOINT STATE   IPV4            IPV6
netperf-client   2011          40890         <status disabled>     <status disabled>    <status disabled>   ready            192.168.27.99   fe80::5868:7aff:fe93:28c6
netperf-server   124           11371         <status disabled>     <status disabled>    <status disabled>   ready            192.168.62.98   fe80::6c2e:40ff:fe2f:f
```

C’est bien le netperf-server qu’on a limité.

Pour plus de renseignements vous pouvez vous reportez à la [documentation](https://docs.cilium.io/en/stable/network/kubernetes/bandwidth-manager/).

Ainsi on voit dans cette partie que:

- le chaining de cni n’empêche pas d’avoir cette fonctionnalité.
- l’eBPF n’a pas que pour fonctionnalité le filtrage du réseau mais aussi sa gestion.

Dans la [prochaine partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-5-118814fd100c), nous allons voir un mode complètement indépendant des ENIs: le mode overlay.

## More from Joseph Ligier

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d45f3829ca82---------------------------------------)