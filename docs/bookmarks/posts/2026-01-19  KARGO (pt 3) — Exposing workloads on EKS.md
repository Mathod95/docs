---
title: "KARGO (pt 3) — Exposing workloads on EKS"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/tech-p7s1/exposing-workloads-on-eks-0ec39acd5fa9"
author:
  - "[[Tech@ProSiebenSat.1]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)## [ProSiebenSat.1 Tech Blog](https://medium.com/tech-p7s1?source=post_page---publication_nav-944d035f7e8e-0ec39acd5fa9---------------------------------------)

[![ProSiebenSat.1 Tech Blog](https://miro.medium.com/v2/resize:fill:76:76/1*PfjiDGFK9P_4KFFmqZzIww.png)](https://medium.com/tech-p7s1?source=post_page---post_publication_sidebar-944d035f7e8e-0ec39acd5fa9---------------------------------------)

We make digital entertainment happen! Reaching millions of viewers and users each day is the basis of our success. Creating real emotions among our viewers and users, we develop first-class products and take our technology to the next level every single day. 🎬

by Sebastian Spanner

This blog post is part of a series about the development of KARGO — A Container focused Developer Platform at ProSiebenSat.1 Tech & Services. For more information on the decision-making process or the overall architecture, please see our [previous blog posts](https://medium.com/tech-p7s1/moving-up-the-stack-c680cebe234c) on this topic.

Exposing workloads running on EKS to the internet, while ensuring security and ease of access, can be challenging. In this blog post, we will guide you through the process of exposing workloads in AWS using [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller), Traefik, ExternalDNS, and cert-manager. Following the constraints outlined [in our previous posts](https://medium.com/tech-p7s1/kargo-a-container-focused-developer-platform-on-aws-0bdc5262fa46), we aim to closely follow the on-premises design to facilitate an easier migration.

### What do we need?

Let’s explore the three key elements that are essential for making workloads accessible outside an [EKS](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html) cluster.

**Network Connectivity**

Manually creating load balancers for each service can be prone to errors and repetitive. To simplify this process, we will use [Traefik](https://traefik.io/traefik/), an open-source edge router, in conjunction with the [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.7/) (AWS LBC). Based on specific service labels, AWS LBC will automatically create and configure an AWS Network Load Balancer for us. This load balancer will serve as the entry point for Traefik. Traefik acts as a reverse proxy and routes requests to the required services. By creating a single load balancer, we can avoid the manual creation of multiple load balancers, thus reducing the chance of errors and unnecessary costs.

**DNS**

For human-readable URLs for our services, we need to set up DNS. ExternalDNS can be used to synchronize exposed Kubernetes Services and Ingresses with DNS providers. By adding the appropriate labels and annotations to our Services and Ingress Objects, ExternalDNS automatically creates DNS entries pointing to the load balancer of the service. This allows us to have easily accessible services with user-friendly URLs.

**Certificates**

Secure communication is crucial when making workloads accessible, especially over the Internet. To ensure this, we need valid certificates. This is where [cert-manager](https://cert-manager.io/) comes into play, a certificate controller for Kubernetes. Cert-manager automates the creation, validation, and renewal of certificates. By requesting certificates from Let’s Encrypt and leveraging DNS challenges for verification, cert-manager provides free, proper certificates for both internal and external services. This ensures that our workloads are always secured with valid certificates, SSL errors are avoided, and a secure communication path is provided.

### A closer look

Let’s take a closer look at these three pillars, starting with network connectivity.

**AWS Load Balancer Controller**

[AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller) helps to manage AWS Elastic Load Balancers within a Kubernetes cluster. It works for both Ingress (which creates ALBs) and Service (which creates NLBs) objects. Once installed, we can create load balancers (in this case NLBs) by simply adding two annotations to our service objects:

- service.beta.kubernetes.io/aws-load-balancer-subnets and a comma-separated list of subnets where the load balancer should be placed in
- service.beta.kubernetes.io/aws-load-balancer-nlb-target-type set to IP

Since we will only use load-balancing on Layer 3, we only need to concern ourselves with NetworkLoadBalancers and service objects. Layer 7 is handled by Traefik.

**Traefik**

[Traefik](https://traefik.io/traefik/) serves as an ingress controller, a component that manages external access to the services within the cluster, typically through HTTP. It manages the routing of incoming traffic to the appropriate services, based on the rules defined within Ingress resources. Ingress objects in a Kubernetes cluster define how traffic should be routed to the various applications and services. These objects hold rules that define which URI paths should be directed to which services. When we apply these Ingress objects to our cluster, both Traefik and the AWS Load Balancer Controller will respond to them.

The AWS Load Balancer Controller will ensure that a Network Load Balancer is set up and configured to forward traffic to the entry points of Traefik. Traefik then receives this traffic and, based on the rules defined in the ingress objects, routes the requests to the right backend services within the Kubernetes cluster. The network load balancer acts as an entry door, directing external traffic into the cluster to Traefik, which then acts as an internal traffic distributor, ensuring requests are routed to their intended services. This allows us to benefit from the scalability and integration of AWS infrastructure with the dynamic and flexible routing capabilities of Traefik.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9ILE00iGE__FfqcIkFBiKw.jpeg)

Figure 1 — Traefik and NLB setup (Picture by the authors drawn with draw.io)

**External DNS**

Moving on to DNS, we aim for service URLs that are easy to remember and type. For this purpose, we will use [ExternalDNS](https://github.com/kubernetes-sigs/external-dns). It automates the updating of DNS records in response to changes within the Kubernetes cluster. When we deploy services or Ingresses that should be accessible via a public domain name, ExternalDNS interfaces with our DNS provider — such as AWS Route 53 — to create or update the DNS records accordingly. As we create Ingress resources for our applications, annotating them for management by Traefik, ExternalDNS monitors these resources. It detects the hostnames we’ve specified and automatically creates or updates the DNS records in our DNS provider, pointing them to the LoadBalancer Service IP Address or Traefik’s exposed IP address.

The result is a seamless integration, whit Traefik handling the internal routing of requests based on hostnames and paths in our Ingress resources, while ExternalDNS ensures these hostnames are resolvable by external clients through its automatic DNS record management.

**Cert-manager**

With human-readable URLs in place, let’s tackle the last part of our three-step plan: Certificates. To address this aspect, we will use a tool called cert-manager and [Let’s Encrypt](https://letsencrypt.org/).Once we’ve set up a cert-manager on our cluster, it interacts with Let’s Encrypt to request certificates and validate domain ownership through various challenges, with the DNS challenge being our choice.

The DNS challenge is a verification process where Let’s Encrypt requests the creation of a DNS record with a specific value to verify domain control. Cert-manager automates this process by interfacing with our DNS provider to create the necessary records. We must give the cert-manager the appropriate IAM permissions to modify our DNS settings. Then we define a ClusterIssuer or an Issuer within our EKS cluster, which tells cert-manager to use Let’s Encrypt as the certificate source and to employ the DNS challenge for domain verification.

When we request a certificate through a Certificate resource that specifies our Issuer, cert-manager communicates with Let’s Encrypt to start the DNS challenge. It then automatically creates the necessary DNS records. Once Let’s Encrypt has verified the challenge, it issues the certificate, and cert-manager stores it in a Kubernetes Secret.

This secret is then used by our Ingress controllers, such as Traefik, to secure our services with TLS encryption. Cert-manager continuously monitors the certificates it manages and ensures that they are renewed well ahead of their expiration, thus maintaining an uninterrupted HTTPS service.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*h8E7ti9Yoay3gCIf9-9U4g.jpeg)

Figure 2 — Cert-workflow (Picture by the authors drawn with draw.io)

### So, let’s sum this up

- AWS Load Balancer Controller creates LoadBalancers based on annotations on service objects.
- Traefik receives requests on behalf of our system and routes them to the appropriate services, acting as a reverse proxy.
- ExternalDNS detects the labels and annotations on Services and Ingress

Objects and creates DNS entries accordingly. These DNS entries point to the LoadBalancer of the service, ensuring proper routing of requests. Cert-manager requests new certificates from Let’s Encrypt and verifies them using the DNS challenge. This automated process ensures that our certificates are always valid and up to date, providing a secure environment for our workloads.

By using proven open-source tools and integrating them with AWS, we’ve created a user-friendly solution for exposing workloads. Even though some tools were chosen based on personal preference and experience, this solution still meets all the expectations that we had defined at the beginning of our project. The system abstracts the underlying infrastructure to such an extent that developers can focus on adding value instead of dealing with infrastructure. Stay tuned for our next blog post where we’ll talk about the Cluster API and how it helps us to deploy thousands of EKS clusters in a simple and repeatable way.

## More about KARGO

- [KARGO (pt 1) — Moving up the stack](https://medium.com/tech-p7s1/moving-up-the-stack-c680cebe234c)
- [KARGO (pt 2) — A container focused developer platform on AWS](https://medium.com/tech-p7s1/kargo-a-container-focused-developer-platform-on-aws-0bdc5262fa46)
- **KARGO (pt 3) — Exposing workloads on EKS**
- [KARGO (pt 4) — Create Kubernetes cluster at scale with ClusterAPI](https://medium.com/tech-p7s1/kargo-series-part-3-create-kubernetes-clusters-at-scale-with-cluster-api-eff259d06874)
- [KARGO (pt 5) — Managing custom EKS cluster addons with Flux CD](https://medium.com/tech-p7s1/kargo-pt-5-managing-custom-eks-cluster-addons-with-flux-cd-0a9b6a706088)

[![ProSiebenSat.1 Tech Blog](https://miro.medium.com/v2/resize:fill:96:96/1*PfjiDGFK9P_4KFFmqZzIww.png)](https://medium.com/tech-p7s1?source=post_page---post_publication_info--0ec39acd5fa9---------------------------------------)

[![ProSiebenSat.1 Tech Blog](https://miro.medium.com/v2/resize:fill:128:128/1*PfjiDGFK9P_4KFFmqZzIww.png)](https://medium.com/tech-p7s1?source=post_page---post_publication_info--0ec39acd5fa9---------------------------------------)

[Last published Dec 17, 2025](https://medium.com/tech-p7s1/from-keywords-to-vectors-how-glomex-built-a-contextual-video-matching-engine-at-scale-a9cfa54ee85e?source=post_page---post_publication_info--0ec39acd5fa9---------------------------------------)

We make digital entertainment happen! Reaching millions of viewers and users each day is the basis of our success. Creating real emotions among our viewers and users, we develop first-class products and take our technology to the next level every single day. 🎬

Turn code into experience @P7S1 and join us 👉 [https://pro7.de/3bh](https://pro7.de/3bh)

## More from Tech@ProSiebenSat.1 and ProSiebenSat.1 Tech Blog

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--0ec39acd5fa9---------------------------------------)