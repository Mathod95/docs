---
title: The Kubernetes Gateway API
date: 2026-01-19
categories:
  - Kubernetes
tags:
  - Gateway API
source: https://medium.com/@GiantSwarm/the-kubernetes-gateway-api-a8c425bdd97b
author:
  - "[[Giant Swarm]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

by on Sep 14, 2022

![Gateway](https://miro.medium.com/v2/resize:fit:640/format:webp/0*xW6HoXp9GDVVbGfN.jpeg)

At Giant Swarm, Kubernetes is central to all that we do. That means that we care very much about the content, quality, and expressiveness of the multitude of APIs that Kubernetes offers to get things done. We have a vested interest, and so we actively participate in the community in order to help improve the core APIs. And, when we need to, we also extend Kubernetes with our own APIs.

One API that we and our customers use a lot is the [Ingress API](https://kubernetes.io/docs/concepts/services-networking/ingress/) . It facilitates the routing of external traffic to the services running in-cluster, according to rules defined in resource definitions. Unfortunately, whilst it’s one of the oldest APIs exposed by Kubernetes (extensions/v1beta1 first appeared in September 2015), it has been widely perceived by the community to be [limited in terms of its utility](https://github.com/bowei/k8s-ingress-survey-2018) .

## The problem with the Ingress API

The Ingress API was deliberately designed to be terse, so as to enable it to be easily implemented by third-party ingress controllers and public cloud providers. As a result, it’s changed little over the years and only graduated from its status in 2020. But, this simplicity comes with a cost; it has caused a lot of frustration for cluster administrators wanting to use the more advanced features of proxy engines, upon which Ingress controllers are built (e.g [NGINX](https://nginx.org/en/)). For example, there are no inherent means in the API for defining a rewrite of the path of an HTTP request, which is a fairly basic and common requirement.

In order to circumvent the lack of expression in the API, ingress controller implementors turned to [Kubernetes annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) as an informal mechanism for extending the API. For the popular, community-provided [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/) , the following annotation rewrites the request’s path to the root path, before the request is routed to a backend service in the cluster:

```c
apiVersion: networking.k8s.io/v1 
kind: Ingress 
metadata: 
annotations: 
nginx.ingress.kubernetes.io/rewrite-target: /
```

The use of a single annotation is all well and good in the simple scenario shown here. But, the effects of annotation usage can soon add up. There are over [100 different possible annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/) for the NGINX Ingress Controller, for example. This makes writing and maintaining Ingress resource definitions, unwieldy and prone to error. Then, other ingress controllers, such as the Contour Ingress Controller, use a completely different [set of annotations](https://projectcontour.io/docs/v1.21.1/config/annotations/) . This renders Ingress resource definitions non-portable between different Ingress controller types. Further, some ingress controllers even bypass the Ingress API altogether, preferring to use their own [custom resources types](https://doc.traefik.io/traefik/providers/kubernetes-crd/) as a means of providing access to the features of the underlying proxy software.

These issues, and others besides, render the whole Ingress experience in Kubernetes, less than optimal. It’s for this reason, that the [Kubernetes Network Special Interest Group](https://github.com/kubernetes/community/tree/master/sig-network) launched the Gateway API project in 2019, to engineer a richer alternative to the limited Ingress API.

## The Gateway API

Whilst the Ingress API may be limited in its expression, its use over a long period of time has enabled the Kubernetes community to coalesce on a set of use cases and requirements. This has informed the development of the Gateway API, and the project is much better placed to deliver an API that serves the needs of apps running atop Kubernetes.

## Features

The Gateway API has a number of noble aims that will significantly improve the task of shepherding external traffic to the backend services running in a Kubernetes cluster. Here are a few highlights.

Firstly, it lends itself to role-based delineation of administrative responsibilities. For example, it decouples the definition of traffic routes () from the abstract definition of the infrastructure or software () that handles the routing activity. Cluster administrators can create Gateway resources that define logical network endpoints bound to the Gateway’s IP address(es). These ‘listeners’, which comprise hostname, port number, and protocol, constrain the type of routes that can be associated with a Gateway. With these constraints in place, application developers can then define routes that are capable of being attached to a Gateway, for their specific application scenarios.

```c
apiVersion: gateway.networking.k8s.io/v1beta1
kind: Gateway
metadata:
  name: contour
  namespace: contour
spec:
  gatewayClassName: contour
  listeners:
  - allowedRoutes:
   namespaces:
       from: All
    name: http
    port: 80
    protocol: HTTP
```

In the definition of the Gateway above, a single listener has been defined, allowing route definitions from any namespace that references the Gateway. The listener handles HTTP traffic on port 80.

```c
apiVersion: gateway.networking.k8s.io/v1beta1
kind: HTTPRoute
metadata:
  name: giantswarm-myapp-route
  namespace: default
spec:
  hostnames:
  - "giantswarm.io"
  parentRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: contour
    namespace: contour
  rules:
  - backendRefs:
    - name: myapp-svc
   port: 80
```

The above HTTPRoute definition references the Gateway as its parent. HTTP traffic incoming on port 80, with a Host header equating to `giantswarm.io`, is routed by the Gateway to a Kubernetes backend service called myapp-svc. [Future enhancements](https://github.com/kubernetes-sigs/gateway-api/blob/eec1d10fb0f0cc87beefc6819883a240b47a5ce7/site-src/geps/gep-1058.md#gep-1058-route-inclusion-and-delegation) will help make this decoupling even more granular, by allowing the creation of parent/child route relationships, using `inclusion` to embed route configuration snippets from child into parent. This caters to delegation scenarios, and provides the opportunity for route composition from more than one source.

The Ingress API is limited to defining traffic at layer 7 only, specifically HTTP/S traffic. Whilst this may cater to the vast majority of use cases, there will always be a requirement for handling TCP streams, and even UDP streams, too. The proxy software solutions that define ingress controller variants are inherently capable of handling pure layer 4 traffic, but of course, this option is not directly exposed through the Ingress API. Whilst an experimental feature of the Gateway API at present, and resources will become first-class constituent components of the API in due course.

Other than through the kludge that is ingress annotation (over)use, extending the Ingress API beyond its vanilla expression, is not possible. Perhaps with this limitation in mind, the Gateway API has been designed to be extendable. For example, if the existing and planned route types (`HTTPRoute`, `TCPRoute`, UDPRoute, `GRPCRoute`) don’t satisfy a requirement, then custom routes can be implemented as required. As it’s early days with the Gateway API, the mechanics of the extension points aren’t overly mature.

These are just a few of the features that the API provides, but there are a whole lot more, including [TLS configuration for routes](https://gateway-api.sigs.k8s.io/guides/tls/) , [traffic splitting](https://gateway-api.sigs.k8s.io/guides/traffic-splitting/) by weight and/or HTTP headers, HTTP request [rewrites, and redirects](https://gateway-api.sigs.k8s.io/guides/http-redirect-rewrite/) , and route conflict resolution.

## API Maturity

The Gateway API has been in the works since November 2019, and on 12 July 2022, the project [released v0.5.0](https://kubernetes.io/blog/2022/07/13/gateway-api-graduates-to-beta/) . This release saw the graduation of some of the key APIs (`GatewayClass`, `Gateway,` and `HTTPRoute`) from alpha to beta status. It also saw the establishment of `standard` and `experimental` release channels, with the former containing only beta-level APIs.

Clearly, there’s still a long way to go before the Gateway API reaches a level of maturity and stability, that will allow organizations to rely on its use in production scenarios. That said, the Ingress API remained at beta-level for 5 years before graduation to ‘stable’, and was routinely used in production settings by organizations, large and small!

## Reference Implementation

Meanwhile, progress on the Gateway API is being keenly watched, and there are already a number of [early implementations](https://gateway-api.sigs.k8s.io/implementations/) of the API. But, what’s of particular interest to us at Giant Swarm, is a recent announcement by, the creator of the popular Envoy proxy. In a [blog article](https://blog.envoyproxy.io/introducing-envoy-gateway-ad385cc59532) , he introduces a new open-source project called the [Envoy Gateway](https://github.com/envoyproxy/gateway) , which aims “to become the de facto standard for Kubernetes ingress supporting the Gateway API”.

As you might expect, the Envoy Gateway will be based on the Envoy proxy, and will borrow ideas from the and ingress projects from VMWare and Ambassador Labs, respectively. The notion is that the community should benefit from a single Envoy-based implementation of the Gateway API, rather than having to choose between a number of competing solutions. It also aims to abstract away the complexities of the Envoy proxy, but leave open the possibility of exposing additional proxy features, as allowed by the extension capabilities of the Gateway API.

In conjunction with the Gateway API, the Envoy Gateway project is a compelling development in the Kubernetes ingress story, and one that Giant Swarm is following very closely.

## Conclusion

It has been an age since the introduction of the Ingress API, which sparked the extensive discussion that ensued concerning its perceived limitations. With the introduction of v0.5.0 of the Gateway API, it finally feels as if the community is moving towards a networking solution that is fit for purpose. It’s probably not a coincidence that the Envoy Gateway project has emerged at this juncture, too, but it’s not the only new initiative in town. The [Gateway API for Mesh Management and Administration (GAMMA)](https://gateway-api.sigs.k8s.io/contributing/gamma/) initiative has recently emerged as a Gateway API subproject, to represent the interests of the service mesh community. This means the Gateway API may eventually figure in the routing of east-west inter-service traffic in Kubernetes clusters, as well as the north-south traffic use case associated with ingress.

As the Gateway API continues to mature, Giant Swarm will be evaluating each of the solutions that seek to implement the API. We’ll be tracking their progress to see which of the solutions satisfies our needs, and the needs of our customers, whilst ensuring the long-term viability of the solution. We’d love to hear the thoughts of anyone in the community who is an early adopter of a Gateway API implementation. [**Let us know your thoughts!**](https://www.giantswarm.io/contact?utm_campaign=Medium+CTA+Conversion&utm_source=Medium&utm_medium=The+Kubernetes+Gateway+API)

*Originally published at* [*https://www.giantswarm.io*](https://www.giantswarm.io/blog/the-kubernetes-gateway-api)*.*

Giant Swarm is a leader in cloud native infrastructures and provides managed Kubernetes clusters to run containerized applications on-premises and in the cloud.

## More from Giant Swarm

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--a8c425bdd97b---------------------------------------)