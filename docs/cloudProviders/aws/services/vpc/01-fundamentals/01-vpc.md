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

When creating a VPC, assign a primary IPv4 CIDR block between `/16` and `/28`:

- Example: `192.168.0.0/16` (65,536 addresses)
- Add secondary IPv4 CIDR blocks as needed
- Enable IPv6 using a `/56` block (up to five per VPC, adjustable on request)

<Frame>
  ![The image is a diagram explaining a Virtual Private Cloud (VPC) with a CIDR block of 192.168.0.0/16, including options for secondary IPv4 and IPv6 CIDR blocks.](https://kodekloud.com/kk-media/image/upload/v1752863379/notes-assets/images/AWS-Networking-Fundamentals-VPC-Overview/vpc-diagram-cidr-blocks-ipv4-ipv6.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Plan your CIDR ranges carefully to avoid overlap with other VPCs or on-premises networks.
</Callout>

## Default vs. Custom VPCs

AWS offers two VPC types:

| Feature           | Default VPC                                      | Custom VPC                             |
| ----------------- | ------------------------------------------------ | -------------------------------------- |
| Creation          | Automatically created in every region            | Manually created by you                |
| CIDR block        | `172.31.0.0/16`                                  | You choose (`/16`–`/28` for IPv4)      |
| Subnets           | One public `/20` subnet per AZ                   | Public/private subnets per your design |
| Internet Gateway  | Attached with a 0.0.0.0/0 route by default       | Requires manual attachment & routing   |
| Security Controls | Default SG and NACL allow all traffic by default | Configure SGs & NACLs from scratch     |

<Frame>
  ![The image is a diagram illustrating multiple regions, each containing a Virtual Private Cloud (VPC) labeled as "Default."](https://kodekloud.com/kk-media/image/upload/v1752863380/notes-assets/images/AWS-Networking-Fundamentals-VPC-Overview/vpc-default-regions-diagram.jpg)
</Frame>

<Frame>
  ![The image is a diagram showing two types of Virtual Private Clouds (VPCs) within a region: a default VPC and a custom VPC, both represented in separate boxes.](https://kodekloud.com/kk-media/image/upload/v1752863381/notes-assets/images/AWS-Networking-Fundamentals-VPC-Overview/vpc-diagram-default-custom-boxes.jpg)
</Frame>

<Frame>
  ![The image illustrates a comparison between a default and a custom Virtual Private Cloud (VPC) within a region, featuring icons and labels for each type.](https://kodekloud.com/kk-media/image/upload/v1752863383/notes-assets/images/AWS-Networking-Fundamentals-VPC-Overview/vpc-comparison-default-custom-illustration.jpg)
</Frame>

## Default VPC Configuration

Every AWS Region includes one Default VPC with these built-in settings:

* **CIDR block**: `172.31.0.0/16` (65,536 IPs)
* **Subnets**: One default `/20` subnet per AZ
  * e.g., `172.31.16.0/20`, `172.31.32.0/20`, etc.
* **Internet Gateway**: Attached by default with a `0.0.0.0/0` route
* **Security Group**: Default SG allowing all outbound traffic
* **Network ACL**: Default NACL allowing all inbound and outbound traffic

<Frame>
  ![The image illustrates a default VPC setup, showing an internet gateway attached to the VPC, routes directing all traffic to the gateway, and public subnets in two availability zones accessible from the internet.](https://kodekloud.com/kk-media/image/upload/v1752863384/notes-assets/images/AWS-Networking-Fundamentals-VPC-Overview/default-vpc-setup-internet-gateway.jpg)
</Frame>


## Summary

* VPCs isolate your AWS resources within a single Region.
* Define IP ranges with CIDR blocks (IPv4 `/16`–`/28`, optional IPv6 `/56`).
* Default VPCs are pre-configured for fast deployment; Custom VPCs give you full control.
* Default VPCs use `172.31.0.0/16`, provide one `/20` subnet per AZ, and include Internet access by default.
* Security Groups and NACLs enforce instance- and subnet-level traffic rules, respectively.

## Links and References

* [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
* [AWS Networking Services](https://aws.amazon.com/products/networking/)

---

## Key Takeaways

- VPC isolate computing resources from other computing resources available in the cloud.
- VPC are isolated to region.
- VPCs isolate your AWS resources within a single Region.
- VPC CIDR block defines the IP addresses a VPC can use. Define IP rangesN with CIDR blocks (IPv4 `/16`–`/28`, optional IPv6 `/56`).
- VPC can have optional secondary IPV4 CIDR block as well as IPV6 CIDR block.
- Every region has a Default VPC with default subnetsN, Security Group and NACLs
    - Default CIDR block is 172.31.0.0/16
    - VPC and its subnets have outbound access to the internet by default
    - 1 default subnet in each Availability Zone
    - The Security Groups in default VPC allow outbound traffic and the NACLs are open in both inbound and outbound direction
- Default VPCs are pre-configured for fast deployment; Custom VPCs give you full control.
- Default VPCs use `172.31.0.0/16`, provide one `/20` subnet per AZ, and include Internet access by default.
- Security Groups and NACLs enforce instance- and subnet-level traffic rules, respectively.