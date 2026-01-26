---
title: "Challenge 15: Down the rabbit hole"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@danielepolencic/challenge-15-down-the-rabbit-hole-d1d16121a835"
author:
  - "[[Daniele Polencic]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

In Kubernetes, you can expose your application to external traffic by using a Service of `type: NodePort`. When you create a NodePort service, Kubernetes assigns a port to each Node. When traffic reaches that port, a set of rules rewrites the traffic to have one of the Pods' IP addresses as the destination. To route the traffic to all the NodePort, it's usually a good idea to provision a load balancer and set the NodePort port as the receiver for the traffic. Since this is an ordinary operation, there's also a service of `type: LoadBalancer` that combines the NodePort with provisioning a cloud load balancer.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*38REyle8I2F9QlSD77hfcg.png)

Now consider having a cluster with 4 nodes. There’s a (red) app with a Service of `type: ClusterIP`. The cluster has an Ingress controller deployed with a single replica and exposed with a NodePort on port 32000. A cloud load balancer is manually provisioned to route traffic to the cluster, but only the last two are selected instead of having all four pods as the destination.

Assuming that there is an Ingress manifest that routes the traffic to the Red service, how many hops are necessary to reach the pod?

You should start counting starting from the load balancer:

1. Only one
2. Two
3. Three
4. None of the above

## Solution

The correct answer is 3: packets always incur in three hops to reach the pods.

The first hop is from the load balance to the NodePort.

At this point, the traffic is intercepted and rewritten to have the Ingress controller pod as the destination.

Depending on your CNI, this could be done with iptables rules, ipvs, eBPF, etc.

When the traffic reaches the Ingress controller, we count another hop.

At this point, the Ingress controller decides how and where to route the traffic based on the definition of the ingress manifest (YAML).

Here’s an example of such a definition:

```c
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
spec:
  rules:
  - http:
      paths:
      - path: /testpath
        pathType: Prefix
        backend:
          service:
            name: test
            port:
              number: 80
```

You might be tempted to conclude that two more hops are missing: one to the ClusterIP and one to the Pod.

However, the Ingress controller doesn’t route the traffic to the Service because Services don’t physically exist in Kubernetes.

Services are a list of endpoints (IP address:port pairs) stored in the control plane.

The Ingress controller knows this and keeps an updated version of the relevant services locally.

The load balances and forwards the traffic directly to the pods.

If you liked this, you might also like:

- The [Kubernetes courses that we run at Learnk8s.](https://learnk8s.io/training)
- I publish the [Learn Kubernetes Weekly newsletter](https://learnk8s.io/learn-kubernetes-weekly) every week.
- This series of [20 Kubernetes concepts that I published over 20 weeks.](https://twitter.com/danielepolencic/status/1666063542011977728)

## More from Daniele Polencic

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d1d16121a835---------------------------------------)