---
title: "NetworkPolicy Best Practices"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://pauldally.medium.com/networkpolicy-best-practices-9a388e41c7c9"
author:
  - "[[Paul Dally]]"
---
<!-- more -->

[Sitemap](https://pauldally.medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*oSE9r8O89v87EV-2pi01Tg.png)

### Create a default deny (and possibly additional default NetworkPolicies)

In a perfect world, your Pod will only allow the network traffic that you explicitly permit — “zero-trust”, or perhaps more accurately “least-privilege” principle. By default, however, Kubernetes imposes no restrictions on network traffic.

However, as soon as you implement your first [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/) that selects a Pod, Kubernetes will start restricting all traffic to/from that Pod that matches the type of that NetworkPolicy (Ingress, Egress). If you create a “default deny” NetworkPolicy, that selects **all Pods** and specifies **both Ingress and Egress** types, Kubernetes will start behaving in a least-privilege manner (at least for **your** Namespace).

Here is an example of a default deny NetworkPolicy:

```c
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: my-ns
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

With this policy in place, **any/all** network traffic will require explicit NetworkPolicies to be defined. This includes traffic that you might not initially anticipate, such as DNS lookups.

If you have other standard requirements (for example, access to DNS) that you want every pod in every Namespace to have, then create these NetworkPolicies in addition to your default deny at Namespace creation.

### Name your NetworkPolicies such that they describe what the NetworkPolicy actually does

This one is probably pretty self-explanatory, but a network-policy named “my-network-policy” probably doesn’t help anyone to understand the purpose of the network policy. Names like “default-deny-all” or “allow-allpods-to-dns” give a lot more clarity to what the NetworkPolicy is intended to do.

### Don’t combine disparate NetworkPolicies

Combining disparate NetworkPolicies into one may make naming the policy a bit of a challenge, but also may result in allowing more access to/from your Pods than desired, violating the least-privilege principle. Consider this NetworkPolicy:

```c
# This is bad because it grants access to more than it should
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: egress-network-policy
  namespace: my-ns
spec:
  policyTypes:
  - Egress
  podSelector: {} 
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    - ipBlock:         
        cidr: 93.184.216.34/32
    ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
    - port: 80
      protocol: TCP
```

It allows access from all Pods to the kube-dns pods in the kube-system Namespace on port 53, as well as to “example.com” on port 80. Unfortunately, it **also** allows access to DNS services on port 53 at “example.com” as well as (in-theory) access to anything running on port 80 in the kube-dns Pods as well. It would be better to have two discrete NetworkPolicies:

```c
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-allpods-to-dns
  namespace: my-ns
spec:
  policyTypes:
  - Egress
  podSelector: {} 
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
```

and (if we assume that only certain Pods need access to “example.com” on port 80):

```c
apiVersion: networking.k8s.io/v1 
kind: NetworkPolicy 
metadata:   
  name: allow-cronjob-to-examplecom
  namespace: my-ns
spec: 
  podSelector:     
    matchLabels:       
      app.kubernetes.io/component: cronjob
  policyTypes:   
  - Egress   
  egress:   
  - to:     
    - ipBlock:         
        cidr: 93.184.216.34/32
    ports:     
    - protocol: TCP       
      port: 80
```

### Except in rare cases, specify a podSelector in the spec and podSelectors and/or ipBlocks in to/from blocks

Usually, your Pods will not all have the same connectivity requirements. Specifying /spec/podSelector: {} is usually not a good idea, except for connections that are pretty ubiquitous (for example, DNS).

Similarly, when you don’t specify a to: block in an egress policy or a from: block in an ingress policy, you are effectively saying that ALL connections from/to **ALL** sources should be allowed on the ports specified. For example, the following NetworkPolicy will allow outbound connections on port 80 to **everywhere** (which, while perhaps better than nothing, is certainly much more than is required to allow access to “example.com”):

```c
# This is bad, because it allows connections to anything listening
# on port 80
apiVersion: networking.k8s.io/v1 
kind: NetworkPolicy 
metadata:   
  name: allow-cronjob-to-examplecom
  namespace: my-ns
spec: 
  podSelector:     
    matchLabels:       
      app.kubernetes.io/component: cronjob
  policyTypes:   
  - Egress   
  egress:   
  - ports:     
    - protocol: TCP       
      port: 80
```

Ensuring that your NetworkPolicies are specifying which Pods and/or ipBlocks they will permit traffic to/from (as demonstrated in previous examples) will go a long way to ensuring that your NetworkPolicies are actually providing the security you expect.

For additional information on debugging NetworkPolicies, see:## [Kubernetes — Debugging NetworkPolicy (Part 1)](https://faun.pub/debugging-networkpolicy-part-1-249921cdba37?source=post_page-----9a388e41c7c9---------------------------------------)

For something as important as NetworkPolicy, debugging is surprisingly painful. There’s even a section in the…

faun.pub

[View original](https://faun.pub/debugging-networkpolicy-part-1-249921cdba37?source=post_page-----9a388e41c7c9---------------------------------------)## [Kubernetes — Debugging NetworkPolicy (Part 2)](https://pauldally.medium.com/debugging-networkpolicy-part-2-2d5c42d8465c?source=post_page-----9a388e41c7c9---------------------------------------)

The first part of this series can be found here. It discusses features that are not available (at least yet) with…

pauldally.medium.com

[View original](https://pauldally.medium.com/debugging-networkpolicy-part-2-2d5c42d8465c?source=post_page-----9a388e41c7c9---------------------------------------)## [Kubernetes — Debugging NetworkPolicy (Part 3)](https://pauldally.medium.com/debugging-networkpolicy-part-3-83658d26747e?source=post_page-----9a388e41c7c9---------------------------------------)

The first part of this series can be found here. It discusses features that are not available (at least yet) with…

pauldally.medium.com

[View original](https://pauldally.medium.com/debugging-networkpolicy-part-3-83658d26747e?source=post_page-----9a388e41c7c9---------------------------------------)

AVP, IT Foundation Platforms Architecture at Sun Life Financial. Views & opinions expressed are my own, not necessarily those of Sun Life

## More from Paul Dally

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--9a388e41c7c9---------------------------------------)