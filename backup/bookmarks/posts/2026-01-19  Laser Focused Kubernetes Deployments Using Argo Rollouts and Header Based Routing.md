---
title: "Laser Focused Kubernetes Deployments Using Argo Rollouts and Header Based Routing"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/containers-101/laser-focused-kubernetes-deployments-using-argo-rollouts-and-header-based-routing-b2fac95c8479"
author:
  - "[[Kostis Kapelonis]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)## [Container Hub](https://medium.com/containers-101?source=post_page---publication_nav-2f4a04e0f5fe-b2fac95c8479---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*xJzAG3HlNJuiWvkMd8EG_w.jpeg)

A Kubernetes cluster with default configuration has access to only two deployment strategies:

- [Recreate](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#recreate-deployment) (causes downtime)
- [Rolling Update](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment) (avoids downtime but you cannot preview or validate the next version in advance)

To get access to [more advanced deployment strategies](https://codefresh.io/learn/kubernetes-deployment/top-6-kubernetes-deployment-strategies-and-how-to-choose/) such as blue/green and canaries you need to use a dedicated [Progressive Delivery](https://codefresh.io/learn/software-deployment/understanding-progressive-delivery-concepts-and-best-practices/) controller such as [Argo Rollouts](https://codefresh.io/learn/argo-rollouts/).

We have previously covered several [basic](https://codefresh.io/blog/minimize-failed-deployments-argo-rollouts-smoke-tests/) and [advanced scenarios](https://codefresh.io/blog/multi-service-progressive-delivery-with-argo-rollouts/) for Argo Rollouts in our blog. Today we answer another common question which is how you can select which of all live users will have access to the canary deployment.

As a reminder, with a canary deployment, you gradually shift traffic to your live users for the new version’s pods. The canary is finished when 100% of live users see the new pods or when something goes wrong and you revert all of them to the previous/stable version.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*nO1KEYdHmXV39Kg2.png)

In the example above, we start the canary by shifting 20% of network requests to the v2 container, then 50%, and finally 100%. The key point here is that unless you do something special, the network traffic requests that go to the new version are random. Some users might even see both application versions if you are not careful.

In the real world you almost always want specific groups of people to be part of the canary process. Some examples are:

- “Only our internal users should see this new version”
- “Only French users must be part of the canary”
- “Asia should stay in the old version, the US will see the canary only”
- “Only users who have checked the ‘preview checkbox’ must see the canary”
- “The payment gateway should stay in the old version. The intranet should see the new version”

So can we still use Argo Rollouts to cover these use cases? The answer is yes, and in this guide we explain two approaches, one basic and one advanced and also compare the advantages and disadvantages.

The methods we are going to use to decide which users see the canary are

1. Static Routing with extra URLs (limited but simple to implement)
2. Header based Routing (more powerful but also more complex to implement)

If you want to try the examples on your own, all resources are available at [https://github.com/kostis-codefresh/rollouts-header-routing-example](https://github.com/kostis-codefresh/rollouts-header-routing-example)

## Understanding the blast radius of your deployments

The central promise of Argo Rollouts is automatic rollbacks. You deploy a new version and then within 1–2 hours (ideally 15 minutes) either the new version is promoted as stable or it is automatically reverted.

This sounds great in theory, but in practice, you need to understand who will be affected if a deployment fails. Let’s say you are doing canary deployments and need 1 hour to get good metrics to decide about the new version’s health. If the metrics fail, some users will have issues for 1 hour. Is this acceptable? Could you control which users face the disruption and who never participate in the canary?

If you read the official Argo Rollouts documentation, the assumption is that the Rollout controller only focuses on a single application.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*1tIgTupLRsxW_ltq.png)

In a big organization most services have dependencies. This is especially true for companies that have adopted microservices. So instead of looking at a single service independently, you need to understand how the application works inside the whole cluster.

A more realistic example would be the following:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*unww4_e4OqjbpNXA.png)

Here we have an e-shop application with different kinds of users

- External partners can interact with the inventory of the application
- Internal/Intranet users provide customer support and handle the store management
- The general public accesses the public website to order/buy items.

If we choose Progressive Delivery for the “auth” service shown in the middle, we see that even though it is a single service, it is a runtime requirement for 3 other services (portal, admin, store). So even if we apply a canary approach, a failed deployment will affect all users of our application.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*kiCRYwfnJ4frqXij.png)

Therefore if you need 2 hours for a canary deployment, and you have a failure then ALL your users will be affected for 2 hours. Wouldn’t it be nice if you could control which user groups are affected and which are not?

## Isolating specific users instead of random network requests

Making a decision about which users see the canary process and which do not is only one aspect of the deployment process. The other aspect is verifying whether a user is part of the canary. Then, all network requests should always be directed to the preview/canary version of the application.

A widespread misconception about Argo Rollouts is that integrating with [a traffic provider](https://argo-rollouts.readthedocs.io/en/stable/features/traffic-management/) allows you to send specific users to the canary version. Unfortunately, this is **not** true in the default configuration.

Even if you use a traffic provider, the percentage of requests that go to the canary application is completely RANDOM. If you set up Argo Rollouts with a canary step of 30%, Argo Rollouts will only guarantee that 30% of all network requests will go to the canary process. But there is no guarantee that these are from the *same* users.

This leads to a very common problem for several organizations: Multiple requests from the same user result in different application versions (both old/stable and preview/canary).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*2_CRC6anvRIzJKJ1.png)

In the example of 30%, Argo Rollouts will indeed send 30% of the total network requests to the canary version, but if you look at the network requests for a single user, you might have the case where the first request is not part of the 30%, the next one is, the next is not and so on. This limitation can be catastrophic for applications with a Graphical Interface, as the user might see different components on screen with each subsequent network request (if the canary version also affects the application’s UI).

In the real world, companies don’t want a random percentage of requests to go to the canary version. You want to apply the percentage to individual users.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*J3m8T5yI4Nn4-P9d.png)

The expectation is that if you set up a canary of 30%, you expect 30% of *users* to see the canary and 70% of them are still on the old/stable version. If you log the network requests of a single user however, you want all of them to go to **EITHER** the canary version **OR** the stable version and never both.

So can Argo Rollout support this use case of user segmentation instead of network request segmentation?

## Example application — Visualize your canary

Our example Rollout can be found at [https://github.com/kostis-codefresh/rollouts-header-routing-example/](https://github.com/kostis-codefresh/rollouts-header-routing-example/)

This repository includes

- The source code of the example application
- A setup for the [Traefik proxy](https://traefik.io/traefik/)
- Example [Rollout definitions](https://argo-rollouts.readthedocs.io/en/stable/features/specification/)
- Examples of HTTP routes from the [Gateway API](https://gateway-api.sigs.k8s.io/)

The highlight of the example application is that you can see visually which requests hit one version or the other.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*TtU_0EZy56nme-ix.png)

In the screenshot above, a canary is in progress between the application’s v1 and v2. The dashboard performs multiple requests (one for each box shown), allowing you to examine your canary networking in a very simple way.

## Approach 1 — Static URL routing

Let’s start with the first use case — reducing the blast radius from a failed deployment. The solution is to create a different URL for each group of users who participate in the deployment process.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*GMvbObf_jHpqA43l.png)

We have 3 URLs:

1. The canary/default URL where requests are routed to the canary. Users of this URL will follow the canary traffic as it increases
2. A URL that ALWAYS sends requests to the canary/preview version regardless of the defined percentage
3. A URL that ALWAYS sends requests to the stable/old version regardless of the defined percentage.

Instead of having a single URL for the canary, we can give each user group a different URL according to their risk acceptance.

In the previous example of the e-shop application we can easily accommodate the following imaginary requirements:

1. We want our external partner never to see the canary at all. They will be shown the stable version until the last possible moment
2. We want our public users to be part of the canary process as normal
3. We want our own employees to “see” the new version right away so that they can detect problems as early as possible
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*ikYZtKlvrCzKa-wa.png)

In this example we use different URL paths, but we could do the same thing with hostnames (e.g. [canary.auth.com](http://canary.auth.com/), [preview.auth.com](http://preview.auth.com/), [stable.auth.com](http://stable.auth.com/)).

Now when a canary process is started

- Users who follow the /stable endpoint will always see the old/stable application version
- Users who follow the /preview endpoint go to the new version straight away
- Users who follow the /canary endpoint participate in the canary as usual.

Here is a timeline for each user group. Blue indicates that network requests go to the old/stable version, and green indicates that they go to the new canary version.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Mmdh9gxUd0LCkOgi.png)

The end result for all groups is precisely the same. They see the new version of the application. The big difference is in failed deployments. If a deployment fails and the canary reverts, users that follow /stable (external partners in our example above) have no impact at all.

Instead of affecting everybody, we have completely isolated our external patterns and also have a different risk acceptance between the general public and our own internal users.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*3tyH7iobcdeXWZci.png)

Implementing this approach with Argo Rollouts is straightforward. Instead of using just one network endpoint (for the canary), you [create an additional one pointing at the stable service and one more for the preview service.](https://github.com/kostis-codefresh/rollouts-header-routing-example/blob/main/static-routing/httproutes.yml)

If you run our example, you can now access 3 URLS (/canary, /stable, /preview). If you start a canary process only the /canary will gradually move to the new version.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*aH3A_7YeZOAO9Kpo.png)

Users who visit /preview will see the new version right away:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*UO6BmvB4HJI22GhN.png)

Users who visit /stable will always view the stable version regardless of the state of the canary process:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*t_Q8A5dba-tfwWIZ.png)

This approach needs no source code changes and can be implemented quickly. It has however three significant limitations:

- It is static in the sense that you need to decide in advance which user groups will visit which URL
- You need to notify all dependent services about the new URLs if they don’t want to follow the default behaviour
- It still works at the level of network requests instead of actual users

## Approach 2 — Dynamic URL routing

The main limitation of static routing is that you need to identify which user group will use which service in advance. Once you make this selection, you cannot change it after the canary has started.

We still haven’t addressed the problem of users versus requests. In the case of the canary endpoint a random number of *requests* can see the canary instead of real users.

Using HTTP headers instead of simple endpoints can improve network isolation. Argo Rollouts can detect optional HTTP headers and make decisions accordingly.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*74DUQTDPW3bJTxHF.png)

In the example above Argo Rollouts will send to the canary all requests that have an HTTP header “X-Canary:true”.

Now we have the capability to have canaries for users instead of just networks. We can modify our application source code to enable this header on the fly.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Kb_rI9l5PtEbb66H.png)

All requests for users with this header present will be redirected to the canary user. This user group will always see the canary, so this approach works great even for Graphic applications.

HTTP headers are fully dynamic. You can change them on the fly. There are several networking products such as load balancers, api gateways, service meshes that allow you to inject headers or modify headers in a network request.  
We can activate this pattern by creating a standard [HTTP route](https://github.com/kostis-codefresh/rollouts-header-routing-example/blob/main/dynamic-routing/smart-route.yml) and then instructing [the canary](https://github.com/kostis-codefresh/rollouts-header-routing-example/blob/main/dynamic-routing/rollout.yml) to create a second one on the fly only if a specific header exists.

```c
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: smart-rollouts-demo
spec:
  replicas: 5
  strategy:
    canary:
      canaryService: smart-canary-service
      stableService: smart-stable-service
      trafficRouting:
        managedRoutes:
        - name: always-preview
        plugins:
          argoproj-labs/gatewayAPI:
            httpRoutes:
              - name: my-smart-route
                useHeaderRoutes: true
            namespace: default
      steps:
        - setHeaderRoute:
            name: always-preview
            match:
              - headerName: X-Canary
                headerValue:
                  exact: "yes"  
        - setWeight: 25                        
        - pause: {}
        - setWeight: 100
```

If you launch the application and this HTTP header is not present, you will see a standard canary with both versions.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*eW3b8RYtjUziRnt-.png)

If you activate the header then all requests of this user go to the canary!

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*bUB-1suEv5lBREtq.png)

This setting is now per user. If you open another browser (to simulate a different user), you will see the standard canary behavior again.

In this simple example, the application itself controls the HTTP header. In a real application, a networking component might do this for you (for example, adding this header only to French users).

## Conclusion

In this guide we have seen two additional approaches to decide which users can look at the new version during a canary instead of a random percentage of requests (default behavior for Argo Rollouts)

With these approaches

- We have complete control over the impact of a failed deployment. We can choose user groups that will always be redirected to the stable version even when a canary is in progress
- Splitting user groups according to their risk acceptance can be decided in advance or updated on the fly
- Canary behavior is now per user instead of per network request

In both cases, you might need to make source code changes to use a different endpoint or enable/disable a specific HTTP header.

Kostis is a developer advocate at Codefresh/Octopus Deploy. He lives and breathes automation, good testing practices and stress-free deployments with GitOps.

## More from Kostis Kapelonis and Container Hub

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--b2fac95c8479---------------------------------------)