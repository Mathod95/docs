---
title: VPC Overview
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/VPC-Overview/page
  - https://notes.kodekloud.com/docs/AWS-Solutions-Architect-Associate-Certification/Services-Networking/VPC-Overview/page#regional-isolation-and-vpc-deployment
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/19a57528-02b5-4093-8418-feb2b8cb3dfd
  - https://learn.kodekloud.com/user/courses/aws-solutions-architect-associate-certification/module/e03ffb87-3345-4fbb-9576-cb53d21d7a6a/lesson/a734115c-7980-4ff4-a86c-bda9435d7f2e
todo: 
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Custom-VPC-Demo/page
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Default-VPC-Demo/page
---

> Cette page présente un aperçu de AWS Virtual Private Cloud (VPC) et explique ses fonctionnalités, ses configurations et ses différents types pour sécuriser le cloud networking.

Dans cette page, nous explorons en détail le concept de AWS Virtual Private Cloud (VPC), une pierre angulaire du networking sécurisé et isolé dans le cloud. Comprendre les VPCs est essentiel pour quiconque souhaite maîtriser le networking sur AWS, que ce soit pour préparer l’examen Solutions Architect ou gérer des services cloud en production.

## Qu'est-ce qu'un VPC ?
Un VPC est une section isolée et sécurisée d'AWS qui vous permet de lancer des ressources (instances EC2, bases de données, etc.) dans un réseau virtuel entièrement défini par vos soins. Il garantit que les données d'un compte restent séparées des autres, même au sein d'une même infrastructure AWS, et permet de segmenter efficacement différentes applications.
Au sein d'un VPC, vous contrôlez intégralement votre environnement réseau.

**Vous pouvez configurer:**

- Les plages d'adresses IP via des blocs CIDR
- Les subnets pour regrouper vos ressources à travers plusieurs Availability Zones
- Les route tables pour maîtriser le flux du trafic entre vos ressources
- Les Security Groups — stateful firewalls appliqués au niveau des instances
- Les Network ACLs — stateless firewalls appliqués au niveau des subnets
- Les Gateways — pour les connexions Internet, les communications inter-VPC ou les connexions vers des infrastructures on-premises

![The image explains what a Virtual Private Cloud (VPC) is, highlighting components like subnetting, routing, and firewalls. It includes a network diagram and a list of features related to VPCs.](../../../../../assets/images/vpc/vpcOverview01.svg){ width="1000" }

!!! note
    La gestion de votre VPC dans AWS est similaire à celle d’un data center traditionnel avec des routers et des switches, mais la Console AWS simplifie et rationalise le processus.

---

## Isolation régionale

Chaque VPC est limité à une seule AWS Region et ne peut pas s’étendre sur plusieurs régions. Par défaut, les ressources de `vpc-1` (us-east-1) sont isolées de celles de `vpc-2` (eu-west-1), sauf si une connectivité explicite est configurée. Lors de la création d’un VPC, il faut spécifier sa AWS region, ce qui empêche toute communication inter-régions sans configuration spécifique.

![The image illustrates AWS Cloud regions "us-east-1" and "eu-west-1" each containing a separate VPC (Virtual Private Cloud). It highlights that a VPC is specific to a single region.](../../../../../assets/images/vpc/vpcOverview02.svg){ width="1000" }

---
<!--
## VPC as a Network Boundary

Out of the box, VPCs are completely isolated:

- No Internet access until you attach an **Internet Gateway**
- No communication between VPCs until you configure **VPC Peering** or a **Transit Gateway**
- No on-premises connectivity until you set up **VPN** or **AWS Direct Connect**

<Callout icon="lightbulb" color="#1CB2FE">
  You can attach an Internet Gateway to multiple public subnets, but each VPC supports only one Internet Gateway.
</Callout>

---
-->
## CIDR Blocks

Chaque VPC se voit attribuer une plage d’adresses IP via son CIDR block. Par exemple, un VPC avec un CIDR block 10.0.0.0/16 peut assigner n’importe quelle adresse IP de cette plage à ses ressources. Les tailles de bloc autorisées varient de /16 à /28.

En plus du primary CIDR block, vous pouvez activer un secondary IPv4 CIDR blocks ou ajouter jusqu’à cinq IPv6 CIDR blocks par VPC (chacun offrant un bloc /56), ce qui augmente la flexibilité et la scalabilité de votre configuration réseau.

![The image is a diagram explaining a Virtual Private Cloud (VPC) with a CIDR block of 10.0.0.0/16, including options for secondary IPv4 and IPv6 CIDR blocks.](../../../../../assets/images/vpc/vpcOverview03.svg){ width="1000" }

!!! warning
    Planifiez vos CIDR ranges avec soin pour éviter tout overlapping avec d’autres VPCs ou les réseaux on-premises.

---

## Types de VPC

Lorsque vous travaillez avec des VPCs, vous rencontrez généralement deux types:

- Default VPC
- Custom VPC

### Default VPC

Un default VPC est automatiquement créé par AWS lors de la création d’un nouveau compte. Chaque région dispose d’un default VPC, préconfiguré pour permettre une connectivité Internet immédiate pour vos instances. Cette configuration prête à l’emploi vous permet de déployer des serveurs sans avoir à gérer des configurations réseau complexes.

### Custom VPC

Les Custom VPCs sont créés et entièrement configurés par vous. Lors de leur mise en place, vous définissez:

- le CIDR block
- les subnets et leur adressage IP
- les configurations de routing
- les règles d’accès réseau via les security groups et les NACLs

![The image is a diagram showing two types of Virtual Private Clouds (VPCs) within a region: a default VPC and a custom VPC, both represented in separate boxes.](../../../../../assets/images/vpc/vpcOverview04.svg){ width="1000" }

---

## Default vs. Custom VPCs

AWS offers two VPC types:

| Feature               | Default VPC                                      | Custom VPC                             | Description                                                              |
|-----------------------| ------------------------------------------------ | -------------------------------------- | ------------------------------------------------------------------------ |
| **Creation**          | Automatically created in every region            | Manually created by you                |                                                                          |
| **CIDR block**        | `172.31.0.0/16`                                  | You choose (`/16`–`/28` for IPv4)      | Provides 65,536 IP addresses                                             |
| **Subnets**           | One public subnet `/20` subnet per AZ            | Public/private subnets per your design | For example, one zone may have 172.31.16.0/20 and another 172.31.32.0/20 |
| **Internet Gateway**  | Attached with a 0.0.0.0/0 route by default       | Requires manual attachment & routing   | Enables internet connectivity for instances                              |
| **Security Groups**   | Configured to allow outbound traffic             | Configure SGs from scratch             | Protects instances by default                                            |
| **NACL**              | Allows both inbound and outbound traffic         | Configure NACLs from scratch           | Provides an additional layer of security                                 |

!!! info
    AWS configure un default VPC dans chaque région. Cette configuration est conçue pour vous permettre de démarrer rapidement, mais pour des environnements de production, il est recommandé de créer des custom VPCs adaptés à vos besoins spécifiques en matière de sécurité et de performance.

![The image illustrates a default VPC setup, showing an internet gateway attached to the VPC, routes directing all traffic to the gateway, and public subnets in two availability zones accessible from the internet.](../../../../../assets/images/vpc/vpcOverview05.svg){ width="1000" }

---

## Résumé

- Les **VPCs** sont un élément fondamental du **networking** sur AWS, offrant des environnements isolés pour déployer vos ressources dans une seule **AWS Region**, ce qui renforce la sécurité et la segmentation réseau.
- Chaque **VPC** est défini par son **CIDR block**, qui délimite la plage d’adresses IP assignables (IPv4 `/16–/28`, IPv6 optionnel `/56`).
- AWS fournit un **default VPC** par région, préconfiguré avec des **subnets**, un **Internet Gateway**, un **Security Group** et des **NACLs**, permettant un déploiement rapide.
- Pour des besoins spécifiques de production, vous pouvez créer des **custom VPCs**, qui offrent un contrôle total sur le **CIDR block**, les **subnets**, le **routing** et les règles d’accès via **Security Groups** et **NACLs**.

---

## Points clés

- Les **VPCs** isolent vos ressources de calcul des autres ressources disponibles dans le cloud.
- Chaque **VPC** est limité à une seule **AWS Region**.
- Le **CIDR block** d’un VPC définit les adresses IP qu’il peut utiliser.
- Un VPC peut avoir :
    - un **CIDR block IPv4 secondaire**
    - jusqu’à cinq **CIDR blocks IPv6**
- Chaque région dispose d’un **default VPC** préconfiguré :
    - **CIDR block** : `172.31.0.0/16`
    - **Subnets** : un `/20` par **Availability Zone**
    - **Accès Internet** : activé par défaut pour le VPC et ses subnets
    - **Security Groups** : trafic sortant autorisé
    - **NACLs** : ouvertes pour le trafic entrant et sortant
- Les **Security Groups** et **NACLs** permettent de contrôler le trafic aux niveaux des instances et des subnets.
- Les **default VPCs** sont prêts à l’emploi pour un déploiement rapide, tandis que les **custom VPCs** offrent un contrôle total sur la configuration réseau.

---

!!! abstract ""

    ## Links and References

    - [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
    - [AWS Networking Services](https://aws.amazon.com/products/networking/)