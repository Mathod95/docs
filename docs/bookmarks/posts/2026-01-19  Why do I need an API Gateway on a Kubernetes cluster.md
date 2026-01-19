---
title: "Why do I need an API Gateway on a Kubernetes cluster"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@martin.hodges/why-do-i-need-an-api-gateway-on-a-kubernetes-cluster-c70f15da836c"
author:
  - "[[Martin Hodges]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## In this article I introduce the concepts of an API Gateway and explain why you would need one in your Kubernetes cluster. In my next article I will show how to set one up using Kong.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*4MZkRWrqNvU_NFLmL7w6mw.png)

Connecting to your microservices

Unlike most of my articles, this one is about theory rather than practice. If you want to install an API Gateway, [read my article on Kong installation here](https://medium.com/@martin.hodges/using-kong-to-access-kubernetes-services-using-gateway-resource-no-loadbalancer-8a1bcd396be9).

If you are creating a scalable backend for your product, it is likely that you will be implementing a microservice architecture. In such an architecture you want your client to be able to connect to your microservices, regardless of whether it is a browser, mobile device or even Internet of Things (IoT) component.

For this article, I have assumed that you are familiar with Kubernetes.

In the picture above, you can see our microservices inside a Kubernetes cluster. The dotted lines represent the connection of the client to these microservices and it is these dotted lines that we need a solution for.

As well as Kubernetes, I also assume that you are familiar with the creation and use of Services to provide a consistent and persistent point of contact to the Pods that are running your microservices. If you are not familiar with Services, you can [read more about implementing Services in one of my other articles](https://medium.com/@martin.hodges/use-terraform-ansible-and-github-actions-to-automate-running-your-spring-boot-application-on-686b95c4e0f6).

Ok, as we have our Services providing a consistent point of contact for our microservices, we can access them without having to worry about the number of instances (or replicas) we have running, or even where they are running. In fact, if you follow my articles, you will realise this is exactly what I do when I am trying things out. I expose the Service as a NodePort Service and access it from outside the cluster.

Whilst you could do this in a production setting, it is not advised for reasons that will become clear when you see what an API Gateway can do.

## Introducing the API gateway

Let’s say we have a number of microservices, each with their own number of replicas and each set with their own Services. We can now step back and look at how our client connects to these Services.

We need a way whereby the client has a single, consistent and persistent point of contact. Effectively we need a service for our Services!

We call this an API Gateway.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*cf6QkzASaSE9BDA0WPmekg.png)

Introducing the API Gateway

You may have noticed I have flipped this picture around. This is so I can introduce the idea of North/South and East/West bound traffic.

These terms are frequently used when discussing Kubernetes traffic flow.

- Northbound refers to traffic going out to the Internet through a point of ***egress***
- Southbound refers to traffic coming in from the Internet through a point of ***ingress***
- ==East/West refers to traffic flowing== ==***between***== ==Pods and Services==

I do not intend to get into the large and complex world of Kubernetes networking in this article, however, it is useful to understand these terms when talking about an API Gateway.

From the picture, you can see that client connects to our services by way of the API Gateway. It provides an ingress point and provides a consistent and persistent connection point for our southbound traffic.

Our client no longer needs to know about how we have structured our microservices and Services, how many there are or where they are. The client simply connects to our API Gateway and requests our services via, say, a REST interface. Ok, so I am also assuming you know what a REST interface is too!

The API Gateway takes care of routing the request to the appropriate Service based on domain, path or a number of other factors. In some cases, the Services may not be REST APIs but may be other application-level protocols. The API Gateway should route these also.

Technically, routing of the East/West traffic is not carried out by the API Gateway but some suppliers include this in their solutions. There are other solutions, such as the Istio service mesh that can manage the East/West traffic.

## Other features of an API Gateway

Ok, so we have just seen how an API Gateway can route Southbound traffic to the required Service and microservice within our cluster but this is only one of the features of an API gateway. Others include:

- Routing based on host, path, headers and more
- Load balancing
- Security
- Enforcing authentication
- Service monitoring
- Request monitoring and tracing
- A/B testing
- API versioning
- Rating limiting / circuit breaking
- Request transformation

### Routing

Whilst we have talked about routing REST requests, you should also be aware that there may be other requests other than HTTP traffic. This may be streaming, web sockets, multi-casts etc. The API Gateway can handle all of these.

### Load Balancing

To ensure High Availability, the API Gateway can load balance across Services. This means that if a Service fails or is terminated, your client does not even realise as its requests will be handled by another Service.

There are a number of load balancing techniques, such as random, sticky, hash, round robin etc and the API Gateway should give you the option.

One thing we have not discussed is the need for an external load balancer but we will come back to that later.

### Security

The API Gateway can act as your TLS endpoint. You can give it the TLS certificates that the client will trust and, using these, clients can confidently and securely connect to your API Gateway.

As a TLS endpoint, the traffic then becomes unencrypted and is open to network eavesdropping. To prevent this, it is recommended that you configure your API Gateway to connect to your Services and microservices over secure connections also.

In some architectures, the API Gateway does not terminate the TLS connection but actually routes it all the way through the microservice.

### Authentication

When a client connects to your microservice, you want to know who they are. This is the process of authentication. Authentication should always take place at the ingress point to your network to ensure that no one gets in without being identified first.

Remember, authentication is knowing who you are, authorisation is allowing you to do something. Authorisation is left up to other parts of the network or the services themselves.

Whilst the API Gateway does not carry out authentication itself, it can ensure that it takes place. You can secure particular request routes such that, if the user is not authenticated, they are either asked to authenticate (through redirection to login) or their request is rejected (by returning a 401 HTTP status).

In some cases authentication and authorisation is possible within the API Gateway by using API keys.

### Service monitoring

As requests are passed southbound to your Services, the API Gateway soon understands if a Service is no longer available. It needs to know this as it needs to redirect the request.

For this reason, the API Gateway becomes a good source of information to monitor your services.

### Request Monitoring and tracing

We have just mentioned that the API Gateway is good for monitoring Services. As it handles requests, it can also provide monitoring of those requests, providing information on the number of requests, types of request, possible cyber-attacks and on the performance of the Services to service requests.

If you have ever worked with microservices and, in particular, a chain of microservices connected via an asynchronous queue, you will know it is very difficult to trace requests end-to-end.

The API Gateway solves this particular problem by injecting headers as it passes the request southbound. These headers can include unique identifiers for each request that can be added to logs for monitoring. You can then use tools to report on your requests across your microservices.

### A/B testing

In A/B testing you run two versions of a service. This is typically a frontend user interface but could be a backend service too. By running two versions and directing users to one or the other, you can compare the performance of the two different solutions and/or versions.

Selection of the A or B version may be blind (the user does not know which they are using), sticky (one is randomly selected and stuck to that user) or self-selection (the user decides which they want to use).

The API Gateway can assist with this type of testing by directing requests to the appropriate A or B version based on information in the request, including cookies, headers and paths.

### API Versioning

Closely related to A/B testing is API versioning. Your API Gateway can help manage API versions, directing requests to Services that support that version of the API.

This type of request routing makes it much easier to support the evolution of your APIs.

### Rating limiting and circuit breaking

You may decide to limit the rate that a particular client can access your services. It may be a monetisation option (higher rate limit for paid accounts) or it may simply be a security tool limiting the number of requests in a Denial of Service (DoS) attack.

As all your requests are coming in via a single ingress point, it stands to reason that your API Gateway is best placed to apply these types of limits.

Under extreme load (or under Service problems), you may actually want your API Gateway to stop passing requests to your microservice to avoid cascade failures (where one failure leads to another). This is known as a circuit breaker and, again, is best implemented in your API Gateway.

### Request Transformation

The path to your REST API in your microservice may not be the same as the path your client uses. If this is the case, your request must be transformed (known as rewriting the path) so that you can connect your client to your microservice.

This request transformation is something typically done by the API Gateway. These transformations are not limited to the path and can include others such as:

- Augmenting the request with additional information (eg: adding tracing or authentication information)
- Splitting a single request between two microservices (unmarshalling)
- Bringing together information from multiple microservices to form a response to a request (marshalling)
- Hiding the API Gateway by setting up proxy rules so the microservice thinks it is talking to the client and not the API Gateway

## Gateway Architecture

Hopefully, by now, you have been convinced you need an API Gateway in your cluster. I think it is important to also understand the high-level architecture of the API Gateway.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*S2ye5yJrC9dJqnJc2MeU1w.png)

API Gateway architecture

Typically, the API Gateway architecture within a Kubernetes cluster comprises of three parts:

- External Load Balancer
- Gateway Proxy
- Ingress Controller

### External Load Balancer

This component is the one that will provide the load balancing across your nodes. It allows you to have multiple instances of your Gateway Proxy and the load balancer will ensure that if any fail, that requests will continue to be serviced by directing them to another instance.

In the world of cloud computing, cloud providers (eg: AWS, Azure, Google Cloud) may provide the load balancer as a service offering. The Kubernetes cluster can then automatically request a load balancer be provided, externally to the cluster — hence its name.

In a non-cloud environment, the load balancer must be provided manually.

The load balancer may provide protection against cyber attacks, such as Distributed Denial of Service (DDoS) attacks.

Note that the load balancer is multi-homed in that it has an interface in the public domain (the Internet) and one in the Virtual Private Cloud (VPC). Typically, this is the only ingress point to the VPC from the Internet. As it is on the Internet, it will have a public IP address and it is likely that it will have a domain name associated with it in the public DNS network so that clients can find it by that name.

### Gateway Proxy

Requests come in from the load balancer into the Gateway Proxy. It is this component that provides the routing of the request (and any transformations) to the appropriate Service based on the rules supplied.

Typically, the Gateway Proxy is stateless but if any persistent session information is required, a distributed session management database will be required across instances of the proxy as requests may come into any instance. Session persistence can be provided by technology such as Redis.

Note that whilst I have referred to the Gateway Proxy as a proxy, it may actually be a router or alternative technology.

### Ingress Controller

The Gateway Proxy needs to be configured with the routing and transformation rules.

Within a Kubernetes cluster, these rules are governed by the cluster state and also the resources created within the cluster. It is the job of the Ingress Controller to carry out this translation of the cluster state and resources into rules that the Gateway Proxy understands.

After creating the rules, the Ingress Controller passes them to the Gateway Proxy so that they can be implemented. This is typically a real-time update without the need for any downtime.

Together the Ingress Controller, Gateway Proxy and the External Load Balancer provide the features of the API Gateway.

## Gateway classes and gateways

Whilst I have described an API Gateway both in general terms and within the context of a Kubernetes cluster, it is important to understand how Kubernetes manages an API Gateway resource.

> A point of confusion arises here. The structure of a Kubernetes Custom Resource Definition (CRD) or manifest file is referred to as an API. This is because it refers to the structure of the API in the Kubernetes control plane. Why does this matter? Because a new CRD has been defined for API Gateways. After much deliberation, it has been decided to refer to the Gateway CRD as the Gateway API. Not to be confused with the API Gateway (which is implemented via the Gateway API). Hopefully that clears that up!

In Kubernetes the API Gateway is defined by two resources, the `GatewayClass` and the `Gateway`. I’ll now attempt to describe the difference between them.

### GatewayClass

The purpose of the `GatewayClass` is to define a type of `Gateway` that can be instantiated and configured within the cluster. It effectively tells you what gateway technologies are available for you to use.

This is a cluster level resource which means that when it is created, it can be referenced from any namespace. You can find documentation [here](https://gateway-api.sigs.k8s.io/api-types/gatewayclass/).

The things that a `GatewayClass` resource defines are:

- The class name to act as a reference
- An optional description of the class
- A reference to the technology supported by this class
- An optional object that defines the type of parameters required by the `Gateway`

Each API Gateway technology supplier will have specific values for these fields. For example, if you decided to use the Hashicorp gateway, they define these values [here](https://developer.hashicorp.com/consul/docs/connect/gateways/api-gateway/configuration/gatewayclass). [If you want to use Kong, read my article here.](https://medium.com/@martin.hodges/using-kong-to-access-kubernetes-services-using-gateway-resource-no-loadbalancer-8a1bcd396be9) I will use the Kong example below. Resources are defined within a YAML file.

```c
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: kong-class
  annotations:
    konghq.com/gatewayclass-unmanaged: 'true'
spec:
  controllerName: konghq.com/kic-gateway-controller
```

There are a few things to note about this file:

1. There is no namespace as it is a cluster level resource
2. Annotations define solution specific options and for Kong these start with `konghq`
3. The unmanaged annotation is an example of an annotation and states that Kong is being manually set up rather than automatically through an operator
4. The Ingress Controller is the Kong Ingress Controller (KIC) and is configured in the `contollerName` field

The `GatewayClass` resource can be created with:

```c
kubectl apply -f kong-gw-class.yml
```

Once a `GatewayClass` has been created, it is now possible to create a `Gateway` that will use this class. Note that you can create many `Gateway` instances that refer to the same `GatewayClass`. You can also create multiple `GatewayClass` resource based on different technologies.

### Gateway

The `Gateway` resource represents the actual API Gateway installation.

Like the `GatewayClass`, suppliers of a particular technology will generally tell you what their technology expects from an associated `Gateway` resource.

In the case of a manually installed Kong Gateway (like the example above), you can define a `Gateway` as follows:

```c
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: kong-gateway
  namespace: kong
spec:
  gatewayClassName: kong-class
  listeners:
  - name: world-selector
    hostname: worlds.com
    port: 80
    protocol: HTTP
    allowedRoutes:
      namespaces:
        from: All
```

Again, there are some things you need to make note of in this file:

- It has a `name` (`kong-gateway`) that will allow it to be referenced later by routing resources, such as `HTTPRoute`
- The `GatewayClass` that defines the type of `Gateway` is matched using its `GatewayClassName`
- Each `Gateway` defines one or more listeners, which are the ingress points to the cluster (ie: just like any application that listens for connections)
- Each listener needs a unique `name` that is a URL compatible string
- The `hostname` is used as a matching field and is optional
- You can control which services can be connected to this listener (`allowedRoutes`) by way of their namespace — this defaults to the `same` namespace as the Gateway but there are other configuration options (such as `All` as shown in this example)

In this example, we can see that the `Gateway` specification expects the gateway to listen on a single port (80) over HTTP. It also tells Kubernetes that its class or type is defined by the `gatewayClassName` of `kong-class`, which we defined earlier.

Note that the `port` has been set to 80, which is the *internal cluster port* for the service, ***not*** any port-forwarded port or external port (eg: if using a NodePort).

Note that `Gateway` resources are specific to a namespace, which we would need to create before creating the resource. If the `Gateway` is in a namespace, it does not stop it accessing Services from other namespaces, as mentioned in the earlier note about `AllowedRoutes`.

### Configuring your gateway

Once you have an API Gateway up and running, you will need to configure it. Each supplier will have their own Customer Resource Definitions to configure features specific to their technology but, by defining a Kubernetes Gateway API, there are some that are standard. These are described [here](https://gateway-api.sigs.k8s.io/reference/spec/).

It should be noted that some route configurations (eg: `TCPRoute`, `TLSRoute` and `UDPRoute`) have no formal definition of rules and effectively act as direct proxies for their backend services. They can be viewed as a port forwarding from the client to the service.

### HTTPRoute

This is the most common form of routing. It routes HTTP and HTTPS requests (after TLS termination) to your backend service based on matching the request based on any combination of hostname, path, header values and query parameters.

Here is an example HTTPRoute:

```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: example-1
  namespace: default
  annotations:
    konghq.com/strip-path: 'true'
spec:
  parentRefs:
  - name: kong-gateway
    namespace: kong
  hostnames:
  - worlds.com
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /world1
    backendRefs:
      - name: hello-world-1-svc
        port: 80
        kind: Service
```

In this file, we have added a Kong specific annotation, `konghq.com/strip-path: ‘true’` which will strip the incoming, matched path from the request to the upstream service. Other lines include:

- The `namespace` of the `HTTPRoute`
- A definition of the `Gateway` to use (in `ParentRefs`), referenced by name and namespace
- An optional reference to the `hostname` to match to the appropriate listener in the `Gateway`
- The `rules` to match the incoming request to for this route
- The `backendRefs` defines the service and pprt to route any matched requests to (note that use of a name that is defined by Kubernetes and added automatically to the cluster DNS and that the port is the unmapped `clusterIP` port for the service)

In this route, the match is the prefix of `/world1`, which is then stripped off before being passed to the service.

It is likely that all your routing configurations will be made using this type of `HTTPRoute`.

## Summary

In this article I have introduced the concept of an API Gateway and shown why they are required and the benefits they can bring.

We have looked at how they are architected within a Kubernetes cluster and how they are split into 3 distinct components.

Finally we saw how Kubernetes has been extended to understand the concept of a `GatewayClass` and `Gateway` resource to allow you to install Kubernetes compatible API Gateways. Using a couple of examples, we could see how these are created and used.

Whilst this article has been mainly theoretically, you can find a practical example of implementing an API Gateway in a Kubernetes cluster in [my article here](https://medium.com/@martin.hodges/using-kong-to-access-kubernetes-services-using-gateway-resource-no-loadbalancer-8a1bcd396be9).

I hope you enjoyed this article and that you have extended your skills by learning something new, even if it is something small.

If you found this article of interest, please give me a clap as that helps me identify what people find useful and what future articles I should write. If you have any suggestions, please add them as notes or responses.

## More from Martin Hodges

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--c70f15da836c---------------------------------------)