---
title: "Mon été avec Cilium et EKS (Partie 3)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-3-2e3d6882e643"
author:
  - "[[Joseph Ligier]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## Introduction

Dans la [deuxième partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-2-ea8ba7a9dcae), nous avons vu, en détail, les ressources que créait Cilium lors de son installation comme des ENIs. Dans cette partie, nous allons voir un peu plus en détail les ENIs et une fonctionnalité qui peut s’avérer intéressante qui s’appelle la délégation de préfixe. Cela va permettre d’étendre le nombre de pods par nœud. Cette fonctionnalité est disponible depuis la version 1.12 de Cilium.

## Les ENIs, qu’est-ce que c’est?

Quand on parle réseau dans AWS, difficile d’échapper aux ENIs (Elastic Network Interface). C’est tout simplement une carte réseau virtuelle. Les instances EC2s en ont particulièrement besoin mais pas seulement. Par exemple les NAT Gateways en ont besoin d’une également.

Voici comment fonctionne avec Cilium la communication via les ENIs entre pods dans deux EC2 différentes:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PMmtp8w6WP1w9j0OYJJGHw.png)

Si vous voulez en savoir plus

## Combien de pods par EC2?

Les instances EC2s peuvent avoir un certain nombre d’ENIs. Cela va dépendre du type et de la puissance de l’instance. La règle est relativement simple et logique: plus c’est puissant plus elle peut en accueillir.

Une ENI peut avoir plusieurs IPs privés. Il y a une seule IP primaire qui est rattachée à l’EC2 et un nombre défini d’IPs secondaires selon le type d’instance.

Par exemple, pour t3.medium, on peut avoir 3 ENIs et chacune peut avoir une IP primaire et 5 IPs secondaires. On peut donc avoir au maximum 15 pods qui utilisent des IPs secondaires car un pod a une unique IP. On rajoute 2 pods (kube-proxy et vpc-cni) qui utilisent l’IP primaire du nœud). D’où le calcul de 17 pods si on a déjà lu d’autres sites sur le sujet. Le calcul est à peu près le même si on installe Cilium car l’agent Cilium et le Cilium Operator utilisent l’IP primaire du nœud.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*wkRFD8PiLJlk4waaMsGUPA.png)

Exemple pour t3.small

On a la liste des résultats de ce calcul pour chaque instance:## [amazon-eks-ami/files/eni-max-pods.txt at master · awslabs/amazon-eks-ami](https://github.com/awslabs/amazon-eks-ami/blob/master/files/eni-max-pods.txt?source=post_page-----2e3d6882e643---------------------------------------)

Packer configuration for building a custom EKS AMI - amazon-eks-ami/files/eni-max-pods.txt at master ·…

github.com

[View original](https://github.com/awslabs/amazon-eks-ami/blob/master/files/eni-max-pods.txt?source=post_page-----2e3d6882e643---------------------------------------)

Cette limitation peut être un peu embêtante, notamment si on a beaucoup de pods qui ne demandent que peu de ressources, c’est bête d’avoir besoin des nœuds supplémentaires pour cela.

## ENI en mode délégation de préfixe

Le mode de délégation de préfixe des ENIs permet d’avoir plus de pods par nœuds.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*vSy2jtjKxO4G9pb571b2Rg.png)

Paramétrages avancés lors de la création d’ENI

Au lieu d’IPs secondaires, l’ENI aura des CIDR /28 donc 16 IPs par slot disponible. Ainsi pour t3.medium on aura une IP primaire et 5 CIDR / 28 par ENI. Donc 81 IPs au total / par eni soit 243 IPs au total ce qui est largement suffisant a priori. Bien évidemment on n’est pas obligé d’utiliser les 3 ENIs.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PJcM-tq4y1Yu5-ur3cCGDw.png)

exemple pour t3.small

On voit bien qu’avec ce mode, on consomme moins d’ENIs mais on risque de consommer plus d’IPs car si par exemple on n’a que 17 pods dans un t3.small, on gaspillera 15 IPs. On ne peut pas tout avoir!

Après la théorie, voici la pratique! Cilium permet de créer des ENIs avec ce mode. Il y a une petite subtilité dans l’installation: une fois l’installation de Cilium faite avec les bonnes options, il faut créer de nouveaux les EC2 pour que ce mode soit effectif. Les anciens garderont toujours les ENIs traditionnels.

## Pré-requis

- un compte AWS avec des access keys
- un peu d’argent (0.1 $ / heure pour le cluster eks, environ 0.08 $ / heure pour deux t3.medium). Durée minimale: environ 30 minutes
- eksctl: outil pour déployer des clusters eks
- aws iam authenticator: outil pour s’authentifier auprès du cluster eks
- aws cli: outil pour communiquer avec l’API d’AWS
- kubectl: outil pour controler le cluster kubernetes
- cilium cli: outil pour gérer cilium
- utilisation d’ [instance Nitro](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html#ec2-nitro-instances) (t3.small est possible pour le test)

Comme AWS EKS est un service payant, il est conseillé d’avoir bien installé les outils avant de créer le cluster.

## Déploiement d’un cluster AWS EKS

Le déploiement du cluster EKS est le même que pour [la partie 1](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-1-99a66ed6671f), je laisse vous y reporter.

## Installation de Cilium

Nous allons utiliser la cilium cli pour effectuer l’installation. C’est encore assez simple, il suffit de rajouter une petite option:

```c
cilium install --helm-set "eni.awsEnablePrefixDelegation=true"
🔮 Auto-detected Kubernetes kind: EKS
ℹ️  Using Cilium version 1.13.3
🔮 Auto-detected cluster name: basic-cilium-us-east-1-eksctl-io
🔮 Auto-detected datapath mode: aws-eni
🔮 Auto-detected kube-proxy has been installed
🔥 Patching the "aws-node" DaemonSet to evict its pods...
ℹ️  helm template --namespace kube-system cilium cilium/cilium --version 1.13.3 --set cluster.id=0,cluster.name=basic-cilium-us-east-1-eksctl-io,egressMasqueradeInterfaces=eth0,encryption.nodeEncryption=false,eni.awsEnablePrefixDelegation=true,eni.enabled=true,ipam.mode=eni,kubeProxyReplacement=disabled,operator.replicas=1,serviceAccounts.cilium.name=cilium,serviceAccounts.operator.name=cilium-operator,tunnel=disabled
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

Maintenant que Cilium est installé. On va devoir créer un nouveau nodegroup. Dans un fichier, copier/coller cela:

```c
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: basic-cilium
  region: us-east-1
  version: "1.27"

managedNodeGroups:
- name: ng-2
  instanceType: t3.medium
  taints:
   - key: "node.cilium.io/agent-not-ready"
     value: "true"
     effect: "NoExecute"
  maxPodsPerNode: 110
```
- On remarquera qu’on a rajouté une option maxPodsPerNode. Par défaut dans EKS, kubelet limite le nombre de pods car il suppose qu’on utilise les ENIs de façon traditionnelle.
- J’ai mis 110 de façon quasi-arbitraire, c’est tout de même ce qui est recommandé par AWS de mettre au maximum.

Pour appliquer la modification:

```c
eksctl create nodegroup -f files/eks-cilium-prefix.yaml
```

Puis vous allez supprimer l’ancien node group:

```c
eksctl delete nodegroup --cluster basic-cilium --name ng-1
```

## Test

On va créer un déploiement de 100 pods nginx:

```c
kubectl create deployment nginx --image nginx --replicas 100
```

Cela prend forcément un peu de temps. Au bout d’une quarantaine de secondes:

```c
kubectl get deployment
NAME    READY     UP-TO-DATE   AVAILABLE   AGE
nginx   100/100   100          100         46s
```

Avec le mode traditionnel des ENIs, on devrait avoir au maximum 34 pods (17x2 en t3.medium). On est bien au delà!

On peut aussi voir cela au niveau des nœuds:

```c
kubectl describe ciliumnodes ip-192-168-18-39.ec2.internal
...
        Id:   eni-0364f1386a3a9a192
        Ip:   192.168.18.39
        Mac:  16:59:91:27:e2:a1
        Prefixes:
          192.168.11.32/28
          192.168.12.0/28
          192.168.8.160/28
          192.168.9.240/28
...
```

On a une seule ENI (eni-0364f1386a3a9a192). l’IP primaire est 192.168.18.39 et on voit les différents préfixes /28

On a créé plus de 100 pods pour 2 nœuds. Soit environ 50 pods par nœuds. Il y a 4 /28 => 64 IPs. 3 auraient été trop justes (48).

Vous pouvez retrouver ici un résumé de l’installation: [https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-prefix.md](https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-prefix.md)

Pour plus d’information sur cette fonctionnalité:

- [https://isovalent.com/blog/post/cilium-release-112/#eni-prefix-delegation](https://isovalent.com/blog/post/cilium-release-112/#eni-prefix-delegation)
- [https://aws.github.io/aws-eks-best-practices/networking/prefix-mode/index\_linux/](https://aws.github.io/aws-eks-best-practices/networking/prefix-mode/index_linux/)

La [prochaine partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-4-d45f3829ca82) sera sur le chaining mode et la limitation de la bande passante.

## More from Joseph Ligier

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--2e3d6882e643---------------------------------------)