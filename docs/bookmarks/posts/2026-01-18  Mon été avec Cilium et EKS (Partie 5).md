---
title: "Mon été avec Cilium et EKS (Partie 5)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-5-118814fd100c"
author:
  - "[[Joseph Ligier]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## Introduction

D ans la [partie précédente](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-4-d45f3829ca82), nous avons vu comment installer Cilium sans désinstaller aws vpc cni. On va faire tout le contraire, pour cette partie. On va supprimer aws vpc cni et on ne va pas utiliser le réseau aws. Cilium va créer son propre réseau. Ceci s’appelle le mode overlay.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*axHyfC2LsgQRnIkltqlo0A.png)

Cilium a un peu plus de travail

Ici, le mode d’encapsulation VXLAN est utilisée, il est également possible d’utiliser le mode d’encapsulation GENEVE. Si vous voulez connaître la différence entre ces deux modes d’encapsulation, vous pouvez le voir [ici](https://ipwithease.com/vxlan-vs-geneve-understand-the-difference/).

## Pourquoi?

Quel est l’intérêt du mode overlay? Le principal intérêt que je vois est si on est à court d’IPs au niveau VPC. Créer un autre réseau permettra de créer un plus gros réseau que celui qu’on a pour AWS. Il est aussi possible de passer en IPv6 si on a vraiment besoin un nombre d’IPs très important. Notez qu’en mode ENI, cilium ne permet pas encore [la création de pod qui ont une IPv6](https://github.com/cilium/cilium/issues/18405).

## Y-a-t-il des limitations?

Les IPs des pods ne sont plus accessibles de l’extérieur du cluster. Cela n’est pas grave en soit. Mais au niveau réseau cela crée plus de couches pour la communication pod vers l’extérieur du cluster (services aws) qui est masqué (masqueraded) ce qui est donc moins performant. De plus, si le cluster communique avec d’autres ressources, il faut vérifier que les IPs de ses ressources ne peuvent pas être dans le CIDR du cluster.

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

On supprime donc aws vpc cni:

```c
kubectl -n kube-system patch daemonset aws-node --type='strategic' -p='{"spec":{"template":{"spec":{"nodeSelector":{"io.cilium/aws-node-enabled":"true"}}}}}'
```

Pour l’installer il suffit de taper:

```c
helm repo add cilium https://helm.cilium.io/
helm repo update
helm install cilium cilium/cilium --version 1.13.4 \
  --namespace kube-system \
  --set egressMasqueradeInterfaces=eth0
```

Les deux premières sont pour installer le repo helm cilium.

La dernière ligne est pour l’installation. Par défaut, le cidr est 10.0.0.0/8. Mais si on veut, on peut le changer avec:

```c
ipam:
  operator:
    clusterPoolIPv4PodCIDRList:
    - "172.31.0.0/16"
```
```c
helm install cilium cilium/cilium --version 1.13.4 \ 
                                  --set egressMasqueradeInterfaces=eth0 \
                                  --namespace kube-system \
                                  --values values.yaml # fichier contenant les lignes ci-dessus
```

On a:

```c
kubectl get pod -n kube-system -o wide
NAME                             READY   STATUS    RESTARTS   AGE    IP              NODE                            NOMINATED NODE   READINESS GATES
cilium-operator-d5f57588-mf5x9   1/1     Running   0          116m   192.168.43.78   ip-192-168-43-78.ec2.internal   <none>           <none>
cilium-operator-d5f57588-thgdw   1/1     Running   0          116m   192.168.17.24   ip-192-168-17-24.ec2.internal   <none>           <none>
cilium-vbntg                     1/1     Running   0          116m   192.168.17.24   ip-192-168-17-24.ec2.internal   <none>           <none>
cilium-xg2bx                     1/1     Running   0          116m   192.168.43.78   ip-192-168-43-78.ec2.internal   <none>           <none>
coredns-79df7fff65-22wxf         1/1     Running   0          127m   10.0.0.130      ip-192-168-43-78.ec2.internal   <none>           <none>
coredns-79df7fff65-wqljf         1/1     Running   0          127m   10.0.0.66       ip-192-168-43-78.ec2.internal   <none>           <none>
kube-proxy-8chh8                 1/1     Running   0          118m   192.168.43.78   ip-192-168-43-78.ec2.internal   <none>           <none>
kube-proxy-vcgbz                 1/1     Running   0          119m   192.168.17.24   ip-192-168-17-24.ec2.internal   <none>           <none>
```

On voit que cilium, cilium-operator et kube-proxy sont sur le cidr d’AWS et coredns est sur le cidr de cilium. C’est normal, cilium, cilium-operator et kube-proxy utilise le réseau de l’host.

Si on veut être totalement propre, il faut supprimer des règles iptables:

```c
iptables -t nat -F AWS-SNAT-CHAIN-0
iptables -t nat -F AWS-SNAT-CHAIN-1
iptables -t nat -F AWS-CONNMARK-CHAIN-0
iptables -t nat -F AWS-CONNMARK-CHAIN-1
```

Ou si on veut être plus “cloud”: on peut créer un autre node group et supprimer l’ancien node group. Ça permet également de vérifier qu’en rajoutant des instances au serveur, cela fonctionne toujours.

Pour un résumé de l’installation vous pouvez vous reporter à:

[https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-overlay.md](https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-overlay.md)

Regardons maintenant comment sont les IPs des cilium nodes:

```c
kubectl get ciliumnode
NAME                            CILIUMINTERNALIP   INTERNALIP      AGE
ip-192-168-17-24.ec2.internal   10.0.1.205         192.168.17.24   114m
ip-192-168-43-78.ec2.internal   10.0.0.45          192.168.43.78   114m
```
```c
kubectl describe ciliumnode ip-192-168-43-78.ec2.internal
Name:         ip-192-168-43-78.ec2.internal
Namespace:
Labels:       alpha.eksctl.io/cluster-name=basic-cilium
              alpha.eksctl.io/nodegroup-name=ng-1
              ...
Annotations:  <none>
API Version:  cilium.io/v2
Kind:         CiliumNode
Metadata:
  Creation Timestamp:  2023-07-18T13:42:31Z
  Generation:          3
  Owner References:
    API Version:     v1
    Kind:            Node
    Name:            ip-192-168-43-78.ec2.internal
    UID:             6e530976-18bf-46f9-8be4-e8f77d439e54
  Resource Version:  2132
  UID:               c2e15bbf-96ba-4001-89b0-f71f92a5e9cd
Spec:
  Addresses:
    Ip:    192.168.43.78
    Type:  InternalIP
    Ip:    184.72.213.151
    Type:  ExternalIP
    Ip:    10.0.0.45
    Type:  CiliumInternalIP
  Alibaba - Cloud:
  Azure:
  Encryption:
  Eni:
  Health:
    ipv4:  10.0.0.54
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

Tiens le CIDR est 10.0.0.0/24 et non 10.0.0.0/8 comme prévu initialement. Mais c’est bizarre l’autre nœud a une IP 10.0.1.205.

Si on regarde le deuxième nœuds:

```c
kubectl describe ciliumnode ip-192-168-17-24.ec2.internal
...
  Ipam:
    Pod CID Rs:
      10.0.1.0/24
...
```

Ah donc chaque nœud a un cidr de /24.

Ce qui correspond à ce schéma:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*z9_2HE-NORnBUXGk.png)

Schéma copié ici

Donc on ne peut pas créer plus de 256x255 nœuds (pas sûr totalement du calcul car je ne pense pas que j’en créerai autant) avec cette méthode.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Fd20kUVGi0B7fpAgGZfY2w.png)

extrait de value.yaml du helm chart… on comprend le /24;)

Si on veut modifier le /24 (je pense que /25 serait suffisant mais c’est plus compliqué à calculer pour un humain), il suffit de changer ipam.operator.clusterPoolIPv4MaskSize.

Dans la [prochaine partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-6-a393c9701c12), nous allons voir que Cilium peut aussi remplacer kube-proxy.

## More from Joseph Ligier

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--118814fd100c---------------------------------------)