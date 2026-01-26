---
title: "Mon été avec Cilium et EKS (Partie 2)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-2-ea8ba7a9dcae"
author:
  - "[[Joseph Ligier]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## Introduction

D ans la [première partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-1-99a66ed6671f), nous avons vu ce qu’était EKS et Cilium, et comment les déployer rapidement. Dans cette partie, nous allons voir comment installer Cilium avec helm. Nous verrons ensuite ce que ça a réellement installé.

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

L’installation avec helm est un peu plus compliqué qu’avec la cli cilium. Il faut lui dire quoi faire alors qu’avec la cli cilium, il faisait l’installation en préjugeant ce qu’on voulait.

Il faut déjà désactiver le plugin réseau d’aws car il ferait doublon avec cilium:

```c
kubectl -n kube-system patch daemonset aws-node --type='strategic' -p='{"spec":{"template":{"spec":{"nodeSelector":{"io.cilium/aws-node-enabled":"true"}}}}}'
```

Au lieu de le supprimer complètement, on le désactive au cas où on voudrait finalement l’utiliser à la place de Cilium.

Ensuite on va lancer l’installation de Cilium:

```c
helm repo add cilium https://helm.cilium.io/
helm repo update
helm install cilium cilium/cilium --version 1.13.4 \
  --namespace kube-system \
  --set eni.enabled=true \
  --set ipam.mode=eni \
  --set egressMasqueradeInterfaces=eth0 \
  --set tunnel=disabled
```

Première et deuxième ligne de commande: on rajoute le repo helm et on le met à jour.

Dernière ligne de commande: on installe cilium avec la version 1.13.4 dans le namespace kube-system, en activant le eni mode d’aws. La sortie est masquée sur l’interface des nœuds eth0 et on désactive le tunneling entre les nœuds.

Vous voyez déjà que sans la documentation, il est difficile de lancer cette ligne de commande par cœur.

Vous pouvez maintenant attendre que cilium soit complètement installé en utilisant la commande suivante:

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
Image versions    cilium             quay.io/cilium/cilium:v1.13.4@sha256:bde8800d61aaad8b8451b10e247ac7bdeb7af187bb698f83d40ad75a38c1ee6b: 2
                  cilium-operator    quay.io/cilium/operator-aws:v1.13.4@sha256:c6bde19bbfe1483577f9ef375ff6de19402ac20277c451fe05729fcb9bc02a84: 2
```

Avec cette ligne de commande, on voit qu’on a installé:

- Le daemonset cilium (un pod par nœud): ce sont ces pods qui vont communiquer avec l’eBPF pour chaque nœud, par exemple la modification d’une règle network policy.
- Le deployment cilium-operator (avec 2 réplicas): ce sont ces pods qui vont discuter avec AWS. Par exemple, ils vont demander à AWS une eni. Ils travaillent de façon actif-passif (l’un travaille pendant que l’autre se repose).

On a trois éléments qui ne sont pas activés:

- Le daemonset envoy qui permet de filtrer les cilium network policy de la couche 7 du modèle OSI
- Hubble relay qui permet d’observer le réseau
- Cluster Mesh qui permet de relier des cluster kubernetes entre eux.

Cette installation est résumée ici: [https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-helm.md](https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-helm.md)

Nous allons maintenant regarder un peu plus précisément ce qui a été installé.

## La face cachée de Cilium

La configuration qui est créée pendant l’installation se trouve ici:

```c
kubectl get cm -n kube-system cilium-config
NAME            DATA   AGE
cilium-config   85     96m
```

La configmap qui contient les différentes configurations de l’installation de cilium.

L’installation de Cilium va également installer des CRDs:

```c
kubectl get crd | grep cilium
ciliumclusterwidenetworkpolicies.cilium.io   2023-07-04T14:20:41Z
ciliumendpoints.cilium.io                    2023-07-04T14:20:41Z
ciliumexternalworkloads.cilium.io            2023-07-04T14:20:41Z
ciliumidentities.cilium.io                   2023-07-04T14:20:41Z
ciliumloadbalancerippools.cilium.io          2023-07-04T14:20:41Z
ciliumnetworkpolicies.cilium.io              2023-07-04T14:20:41Z
ciliumnodeconfigs.cilium.io                  2023-07-04T14:20:41Z
ciliumnodes.cilium.io                        2023-07-04T14:20:41Z
```

Nous allons installer quelques ressources de test de connectivité pour voir un peu plus au clair:

```c
kubectl create ns cilium-test
kubectl apply -n cilium-test -f https://raw.githubusercontent.com/cilium/cilium/v1.13/examples/kubernetes/connectivity-check/connectivity-check.yaml
```

On va commencer par simple, à quoi correspond le crd ciliumnodes:

```c
kubectl get ciliumnodes
NAME                             CILIUMINTERNALIP   INTERNALIP       AGE
ip-192-168-25-188.ec2.internal   192.168.19.239     192.168.25.188   6m22s
ip-192-168-39-205.ec2.internal   192.168.33.93      192.168.39.205   6m21s
```

On voit ainsi que Cilium va créer à but interne une IP pour chaque nœud (CILIUMINTERNALIP).

Si on fait un describe d’un des deux nœuds, on voit beaucoup de choses intéressantes:

```c
kubectl describe ciliumnodes ip-192-168-25-188.ec2.internal
Name:         ip-192-168-25-188.ec2.internal
Namespace:
Labels:       alpha.eksctl.io/cluster-name=basic-cilium
              alpha.eksctl.io/nodegroup-name=ng-1
              beta.kubernetes.io/arch=amd64
              beta.kubernetes.io/instance-type=t3.medium
              beta.kubernetes.io/os=linux
              eks.amazonaws.com/capacityType=ON_DEMAND
              eks.amazonaws.com/nodegroup=ng-1
              eks.amazonaws.com/nodegroup-image=ami-0fe06c902df3a937b
              eks.amazonaws.com/sourceLaunchTemplateId=lt-05c638d1708472b9f
              eks.amazonaws.com/sourceLaunchTemplateVersion=1
              failure-domain.beta.kubernetes.io/region=us-east-1
              failure-domain.beta.kubernetes.io/zone=us-east-1f
              k8s.io/cloud-provider-aws=adc9b7ebbe741f22290eef4d44b6387c
              kubernetes.io/arch=amd64
              kubernetes.io/hostname=ip-192-168-25-188.ec2.internal
              kubernetes.io/os=linux
              node.kubernetes.io/instance-type=t3.medium
              topology.kubernetes.io/region=us-east-1
              topology.kubernetes.io/zone=us-east-1f
Annotations:  <none>
API Version:  cilium.io/v2
Kind:         CiliumNode
Metadata:
  Creation Timestamp:  2023-07-04T14:20:53Z
  Generation:          7
  Owner References:
    API Version:     v1
    Kind:            Node
    Name:            ip-192-168-25-188.ec2.internal
    UID:             7f8a20a7-dc14-4891-95c1-da742d1b7411
  Resource Version:  6517
  UID:               a0bcbaec-3ca5-466a-bb96-ac3b50bf72dc
Spec:
  Addresses:
    Ip:    192.168.25.188
    Type:  InternalIP
    Ip:    44.211.236.70
    Type:  ExternalIP
    Ip:    192.168.19.239
    Type:  CiliumInternalIP
  Alibaba - Cloud:
  Azure:
  Encryption:
  Eni:
    Availability - Zone:            us-east-1f
    Disable - Prefix - Delegation:  false
    First - Interface - Index:      0
    Instance - Type:                t3.medium
    Node - Subnet - Id:             subnet-04a17f8467a496ee2
    Use - Primary - Address:        false
    Vpc - Id:                       vpc-0f1002e7ce852867b
  Health:
    ipv4:  192.168.21.163
  Ingress:
  Instance - Id:  i-01663a75bbcdb9131
  Ipam:
    Pod CIDRs:
      10.188.0.0/16
    Pool:
      192.168.13.38:
        Resource:  eni-0282382b4c257f03c
      192.168.14.69:
        Resource:  eni-0282382b4c257f03c
      192.168.16.229:
        Resource:  eni-0d43f5417fe806d4f
      192.168.17.136:
        Resource:  eni-0d43f5417fe806d4f
      192.168.19.239:
        Resource:  eni-0282382b4c257f03c
      192.168.2.175:
        Resource:  eni-0282382b4c257f03c
      192.168.21.163:
        Resource:  eni-0edda6362c2010c5f
      192.168.22.40:
        Resource:  eni-0edda6362c2010c5f
      192.168.24.8:
        Resource:  eni-0edda6362c2010c5f
      192.168.26.11:
        Resource:  eni-0edda6362c2010c5f
      192.168.30.102:
        Resource:  eni-0d43f5417fe806d4f
      192.168.6.177:
        Resource:  eni-0d43f5417fe806d4f
      192.168.8.153:
        Resource:  eni-0282382b4c257f03c
      192.168.8.202:
        Resource:  eni-0edda6362c2010c5f
      192.168.9.157:
        Resource:    eni-0d43f5417fe806d4f
    Pre - Allocate:  8
Status:
  Alibaba - Cloud:
  Azure:
  Eni:
    Enis:
      eni-0282382b4c257f03c:
        Addresses:
          192.168.8.153
          192.168.19.239
          192.168.14.69
          192.168.2.175
          192.168.13.38
        Description:  Cilium-CNI (i-01663a75bbcdb9131)
        Id:           eni-0282382b4c257f03c
        Ip:           192.168.19.121
        Mac:          16:5e:b0:f2:fc:65
        Number:       1
        Security - Groups:
          sg-03f8b578c6c28007b
        Subnet:
          Cidr:  192.168.0.0/19
          Id:    subnet-04a17f8467a496ee2
        Tags:
          io.cilium/cilium-managed:  true
          io.cilium/cluster-name:    basic-cilium
        Vpc:
          Id:              vpc-0f1002e7ce852867b
          Primary - Cidr:  192.168.0.0/16
      eni-0d43f5417fe806d4f:
        Addresses:
          192.168.9.157
          192.168.30.102
          192.168.6.177
          192.168.16.229
          192.168.17.136
        Description:  Cilium-CNI (i-01663a75bbcdb9131)
        Id:           eni-0d43f5417fe806d4f
        Ip:           192.168.24.26
        Mac:          16:b3:8e:67:d4:33
        Number:       2
        Security - Groups:
          sg-03f8b578c6c28007b
        Subnet:
          Cidr:  192.168.0.0/19
          Id:    subnet-04a17f8467a496ee2
        Tags:
          io.cilium/cilium-managed:  true
          io.cilium/cluster-name:    basic-cilium
        Vpc:
          Id:              vpc-0f1002e7ce852867b
          Primary - Cidr:  192.168.0.0/16
      eni-0edda6362c2010c5f:
        Addresses:
          192.168.22.40
          192.168.24.8
          192.168.8.202
          192.168.26.11
          192.168.21.163
        Id:   eni-0edda6362c2010c5f
        Ip:   192.168.25.188
        Mac:  16:ae:a1:4e:37:73
        Security - Groups:
          sg-03f8b578c6c28007b
        Subnet:
          Cidr:  192.168.0.0/19
          Id:    subnet-04a17f8467a496ee2
        Tags:
          node.k8s.amazonaws.com/instance_id:  i-01663a75bbcdb9131
        Vpc:
          Id:              vpc-0f1002e7ce852867b
          Primary - Cidr:  192.168.0.0/16
  Ipam:
    Operator - Status:
    Used:
      192.168.14.69:
        Owner:     cilium-test/pod-to-a-allowed-cnp-57fd79848c-dj57g
        Resource:  eni-0282382b4c257f03c
      192.168.16.229:
        Owner:     cilium-test/pod-to-b-multi-node-nodeport-64757f6d5f-wfxsh
        Resource:  eni-0d43f5417fe806d4f
      192.168.19.239:
        Owner:     router
        Resource:  eni-0282382b4c257f03c
      192.168.2.175:
        Owner:     kube-system/coredns-79df7fff65-kmqrz
        Resource:  eni-0282382b4c257f03c
      192.168.21.163:
        Owner:     health
        Resource:  eni-0edda6362c2010c5f
      192.168.22.40:
        Owner:     kube-system/coredns-79df7fff65-hklh2
        Resource:  eni-0edda6362c2010c5f
      192.168.26.11:
        Owner:     cilium-test/pod-to-a-6578dd7fbf-47vkk
        Resource:  eni-0edda6362c2010c5f
      192.168.30.102:
        Owner:     cilium-test/pod-to-external-1111-76c448d975-766t8
        Resource:  eni-0d43f5417fe806d4f
      192.168.8.153:
        Owner:     cilium-test/pod-to-b-multi-node-clusterip-54847b87b9-xw4lb
        Resource:  eni-0282382b4c257f03c
      192.168.9.157:
        Owner:     cilium-test/pod-to-b-multi-node-headless-64b4d78855-qvdzc
        Resource:  eni-0d43f5417fe806d4f
Events:            <none>
```

On voit par exemple toutes les ENIs (les cartes réseaux virtuelles) que contiennent ce nœud. Faites un test: kubectl describe node sur le même nœud, vous verrez beaucoup moins de choses au niveau réseau.

Comment est généré ce fichier? Le cilium agent va regarder dans les metadata de l’instance (`http://169.254.169.254/latest/meta-data/)` ) pour initialiser le fichier (spec.eni). Cilium operator écoute dans l’API AWS pour informer les IPs déjà prises (spec.ipam). Quand un pod est créé sur un nœud dont cilium agent s’occupe, cilium agent va choisir une IP de libre et le rajouter dans le fichier (status.eni).

Comme autre CRD, il y a les ciliumnetworkpolicies qui sont des network policies propre à Cilium:

```c
kubectl get cnp -n cilium-test
NAME                                    AGE
pod-to-a-allowed-cnp                    29m
pod-to-a-denied-cnp                     29m
pod-to-external-fqdn-allow-google-cnp   29m
```

Le nom de la CRD est tellement long qu’il y a un petit alias cnp pour les avoir.

En voici un exemple:

```c
kubectl get cnp -n cilium-test pod-to-external-fqdn-allow-google-cnp -o yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  labels:
    name: pod-to-external-fqdn-allow-google-cnp
  name: pod-to-external-fqdn-allow-google-cnp
  namespace: cilium-test
spec:
  egress:
  - toFQDNs:
    - matchPattern: '*.google.com'
  - toEndpoints:
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s:k8s-app: kube-dns
    - matchLabels:
        k8s:io.kubernetes.pod.namespace: kube-system
        k8s:k8s-app: node-local-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: ANY
      rules:
        dns:
        - matchPattern: '*'
  - toEndpoints:
    - matchLabels:
        k8s:dns.operator.openshift.io/daemonset-dns: default
        k8s:io.kubernetes.pod.namespace: openshift-dns
    toPorts:
    - ports:
      - port: "5353"
        protocol: UDP
      rules:
        dns:
        - matchPattern: '*'
  endpointSelector:
    matchLabels:
      name: pod-to-external-fqdn-allow-google-cnp
```

Les cilium network policies permettent d’avoir des règles beaucoup plus fines qu’avec les traditionnelles network policies kubernetes. Nous nous n’étendrons pas trop sur le sujet, il y a de quoi pour en parler des heures. Je vous conseille de faire le lab [Getting started with Cilium](https://isovalent.com/labs/getting-started-with-cilium/) pour en savoir plus.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*WDhyvvrfZmEHNrhAcSJG2w.png)

un éditeur de network policy bien pratique

Cependant un petit détail intéressant c’est le mot *endpoint*, c’est ce terme qui va permettre de sélectionner les pods dans les règles.

Transition toute trouvée, on a un moyen de trouver les cilium endpoints:

```c
kubectl get ciliumendpoints -A
NAMESPACE     NAME                                                     ENDPOINT ID   IDENTITY ID   INGRESS ENFORCEMENT   EGRESS ENFORCEMENT   VISIBILITY POLICY   ENDPOINT STATE   IPV4             IPV6
cilium-test   echo-a-6575c98b7d-z2x5k                                  1821          27668         <status disabled>     <status disabled>    <status disabled>   ready            192.168.52.136
cilium-test   echo-b-54b86d8976-qrgl4                                  1306          23881         <status disabled>     <status disabled>    <status disabled>   ready            192.168.36.74
cilium-test   pod-to-a-6578dd7fbf-47vkk                                1808          49453         <status disabled>     <status disabled>    <status disabled>   ready            192.168.26.11
cilium-test   pod-to-a-allowed-cnp-57fd79848c-dj57g                    465           9808          <status disabled>     <status disabled>    <status disabled>   ready            192.168.14.69
cilium-test   pod-to-a-denied-cnp-d984d7757-x4fr5                      2965          33428         <status disabled>     <status disabled>    <status disabled>   ready            192.168.41.123
cilium-test   pod-to-b-intra-node-nodeport-6654886dc9-bzkgr            1201          44618         <status disabled>     <status disabled>    <status disabled>   ready            192.168.33.36
cilium-test   pod-to-b-multi-node-clusterip-54847b87b9-xw4lb           3956          37273         <status disabled>     <status disabled>    <status disabled>   ready            192.168.8.153
cilium-test   pod-to-b-multi-node-headless-64b4d78855-qvdzc            673           8631          <status disabled>     <status disabled>    <status disabled>   ready            192.168.9.157
cilium-test   pod-to-b-multi-node-nodeport-64757f6d5f-wfxsh            2044          46317         <status disabled>     <status disabled>    <status disabled>   ready            192.168.16.229
cilium-test   pod-to-external-1111-76c448d975-766t8                    2132          36696         <status disabled>     <status disabled>    <status disabled>   ready            192.168.30.102
cilium-test   pod-to-external-fqdn-allow-google-cnp-56c545c6b9-95zxg   3654          2171          <status disabled>     <status disabled>    <status disabled>   ready            192.168.47.185
kube-system   coredns-79df7fff65-hklh2                                 2522          18012         <status disabled>     <status disabled>    <status disabled>   ready            192.168.22.40
kube-system   coredns-79df7fff65-kmqrz                                 263           18012         <status disabled>     <status disabled>    <status disabled>   ready            192.168.2.175
```

Ça rappelle aussi les endpoints kubernetes:

```c
kubectl get ep -A
NAMESPACE     NAME                   ENDPOINTS                                                        AGE
cilium-test   echo-a                 192.168.52.136:8080                                              6m1s
cilium-test   echo-b                 192.168.36.74:8080                                               6m
cilium-test   echo-b-headless        192.168.36.74:8080                                               6m
cilium-test   echo-b-host-headless   192.168.39.205                                                   6m
default       kubernetes             192.168.18.36:443,192.168.42.251:443                             38m
kube-system   hubble-peer            192.168.25.188:4244,192.168.39.205:4244                          27m
kube-system   kube-dns               192.168.2.175:53,192.168.22.40:53,192.168.2.175:53 + 1 more...   38m
```

La partie “intéressante” pour les cilium endpoints c’est les *endpoint ids* et *identity ids*. Chaque pod a son propre *endpoint id* alors qu’un pod peut avoir le même *identity id* qu’un autre. Il suffit qu’ils aient les mêmes labels.

Par exemple les pods coredns générés par le deployment ont les mêmes labels et donc le même *identity id* (18012) mais pas le même *endpoint id* (2522 et 263). Si un pod meurt dans un deployment, le pod recréé aura un autre *endpoint id* mais le même *identity id* car il aura les mêmes labels que le pod mort.

Plutôt que d’utiliser les IPs qui sont très temporaires dans le monde de kubernetes, Cilium va utiliser les *identity ids* pour identifier les sources et les destinations des flux réseaux. Il peut être intéressant de faire un describe sur un cilium endpoints. On verra les labels qui ont été pris en compte pour créer l’identity id, les ports utilisés, etc.

Dernier CRD à voir et qui est en rapport avec ce qui précède: les ciliumidentities.

```c
kubectl get ciliumidentities
NAME    NAMESPACE     AGE
18012   kube-system   22m
2171    cilium-test   111s
23881   cilium-test   112s
27668   cilium-test   112s
33428   cilium-test   111s
36696   cilium-test   112s
37273   cilium-test   111s
44618   cilium-test   109s
46317   cilium-test   110s
49453   cilium-test   112s
8631    cilium-test   110s
9808    cilium-test   111s
```

On a ainsi la liste de tous les cilium identities du cluster.

Il y a certainement d’autres choses permettant de debugger comme regarder les logs des agents Cilium ou Cilium operator mais ça sera tout pour aujourd’hui. On voit bien que Cilium installé sur EKS et sur un autre cluster ne seront pas tout à fait le même, il s’adapte au réseau sur lequel il s’installe.

La [prochaine partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-3-2e3d6882e643) sera sur un point qu’on a partiellement abordé aujourd’hui: les ENIs. On va voir ce que c’est et on va parler d’un mode particulier qui va permettre d’améliorer une de ses principales contraintes: le nombre de pods par instance ec2.

## More from Joseph Ligier

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--ea8ba7a9dcae---------------------------------------)