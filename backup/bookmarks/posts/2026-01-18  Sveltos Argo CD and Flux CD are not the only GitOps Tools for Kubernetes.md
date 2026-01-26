---
title: "Sveltos: Argo CD and Flux CD are not the only GitOps Tools for Kubernetes"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/sveltos-argo-cd-and-flux-cd-are-not-the-only-gitops-tools-for-kubernetes-fa2b94b2ea48"
author:
  - "[[Artem Lajko]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@artem_lajko)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-fa2b94b2ea48---------------------------------------)

> **Note:** The purpose of this blog is not to showcase the many possibilities of Sveltos, as [Gianluca Mardente](https://www.linkedin.com/in/gianlucamardente/) and [Eleni Grosdouli](https://www.linkedin.com/in/eleni-grosdouli-85a1a5116/) has already explained this in the [documentation](https://projectsveltos.github.io/sveltos/) and many [blog posts on Medium](https://medium.com/@gianluca.mardente). I am focusing here from the perspective of a Platform Engineer and the challenges we face with Argo CD, which Sveltos combined with Flux CD has solved more elegantly.

![](https://miro.medium.com/v2/resize:fit:640/1*F5m8GepQrcKSalsGcP418Q.gif)

Figure-1: Argo CD vs Sveltos — Comparison of fleet cluster management solutions

As shown in Figure-1, we will only be looking at Argo CD and Sveltos, not Flux CD. The reason for this will be explained shortly. This blog assumes that you are familiar with the GitOps concept as well as [Cockpit and Fleet](https://medium.com/devops-dev/gitops-at-scale-69639c9a3dd7).

## Introduction

Sveltos is based on having one management cluster and several fleet clusters to manage applications (Add-ons) on them. An add-on such as an application like the Ingress controller. Argo CD can also be used with this approach. Comparing it to Flux CD wouldn’t be fair or meaningful, as in my opinion, Flux CD is designed for **managing his own cluster.**

Most people immediately think of Flux CD and Argo CD when they talk about GitOps, as if there were no other tools available. I was one of those people, by the way. Even though these are the prevalent tools on the market, we should open our minds to other options. Fortunately, this happened to me at KubeCon2024 in Paris, where I met Gianluca, a maintainer of Sveltos, and I find the solution quite elegant.

## Sveltos vs Argo CD

![](https://miro.medium.com/v2/resize:fit:640/1*4hYV5GLzUb9NMn2TsfNYDA.gif)

Figure-2: Let the games begin!

[Sveltos](https://github.com/projectsveltos) is a set of Kubernetes controllers that run in the management cluster. From the management cluster, Sveltos can manage add-ons and applications on a fleet of managed Kubernetes clusters. It is a declarative tool to ensure that the desired state of an application is always reflected in the actual state of the Kubernetes Management or Workload cluster.

[Argo CD](https://github.com/argoproj/argo-cd) is an open-source, continuous delivery (CD) tool for Kubernetes that automates the deployment, monitoring, and rollback of applications. It is a declarative tool that uses GitOps principles to ensure that the desired state of an application is always reflected in the actual state of the Kubernetes Management or Workload cluster.

Sounds similar at first, doesn’t it? Here comes the first similarity, but also the first major difference.

Although both tools can be used to roll out the necessary applications on the fleet ships (workload clusters), Argo CD has integrated the GitOps approach, while Sveltos has to rely on [Flux CD](https://github.com/fluxcd/flux2) as an integration at this point (like showing in Figure-3).

![](https://miro.medium.com/v2/resize:fit:640/1*DRT2TI_nq8Z_kzwCqqrPCg.png)

Figure-3: Sveltos and Flux Integration

In the following, we will take a look at various points in order to understand which approaches the two tools pursue and where the tools are limited.

### Architecture

Now, let’s look at this on the architectural level to understand how the Cockpit Cluster establishes connections to the Fleet-Ships (workload clusters) that are being managed. In the following section, we will technically and hands-on examine how the creation of these connections differs.

![](https://miro.medium.com/v2/resize:fit:640/1*zlnWNw691p2YWmRzH8l8YQ.gif)

Figure-4: Argo CD Architecture

Here, we can see the first difference. As previously mentioned, Argo CD accesses the repository and manages it through a controller (Repo Server). When establishing the connection, Argo creates ServiceAccounts, ClusterRole, and ClusterRoleBinding, and stores the bearer token in the management cluster as a secret in the namespace where the Argo instances are running. Then, Argo keeps the deployed applications in sync and checks the status between the repository and the deployed state in the clusters every 3 minutes by default. The synchronization and templating, for example when using Helm as a package manager, occur server-side at Argo.

Here we encounter the first challenges that our team has already faced. For example, managing 2000 applications via Argo requires significant resources for refreshing or syncing. Currently, we keep replicas fixed at 3 and allow horizontal scaling up to 5.

Because it consumes many resources, Akuity, for example, recommends [managing the rendering via CI and deploying only the final manifests](https://akuity.io/blog/the-rendered-manifests-pattern/). For this purpose, they have also developed a tool named Kargo to simplify these processes.

Now let’s take a look at the architecture of Sveltos:

![](https://miro.medium.com/v2/resize:fit:640/1*b_KuXMtniHDON4Hd_dbOhw.gif)

Figure-5: Sveltos Architecture

To ensure the GitOps approach, Sveltos relies on the integration of Flux CD. Flux retrieves what are called Profiles or ClusterProfiles as resources, which Sveltos then uses to roll out the add-ons on the fleet-ships. We will look at this more closely later. When establishing the connection, Sveltos creates a namespace for the fleet-ship in the management cluster, as well as ServiceAccounts, ClusterRole, and ClusterRoleBinding in the fleet-ship, and stores them as a secret in the created namespace of the management cluster. Additionally, Sveltos then deploys the agent on the fleet-ship.

This also makes a difference in the syncing process. Unlike Argo, Sveltos deploys agents on the fleet clusters, which notify the Sveltos instance on the management cluster depending on the sync mode, and this instance then performs the re-sync to restore the original state (manifest). This saves resources because the sync only occurs in case of a drift and the check is done via the agents, not through the cockpit instance like with Argo. This significantly conserves resources and simultaneously ensures stronger isolation based on namespaces. It also enables Sveltos to pursue a more rigorous multi-tenancy approach, as it was designed with this idea in mind from the start. Anyone who has dealt with multi-tenancy in Argo knows how challenging it is to implement true hard isolation.

In the next part, we will look at how to set up both solutions.

### Deployment of Argo CD vs Sveltos

The prerequisite here is that you are logged in against all Kubernetes clusters and have stored them in the kubeconfig. We use it to establish the connection between the cockpit and fleet ships for both Argo and Sveltos.

[**Argo CD**](https://argo-cd.readthedocs.io/en/stable/getting_started/)**:**

Deploy Argo CD to the Cockpit with:

```c
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Download and install Argo CD CLI:

```c
brew install argocd
```

There is now a special workflow of Argo, which can be seen in Figure 6.

![](https://miro.medium.com/v2/resize:fit:640/1*rMjKuxjEjBk_luHEob_Wmg.gif)

Figure-6: Establish Connection via argocd cli

In Figure-6 you can see that you have to be logged in against the clusters as well as against the Argo server in order to establish the connection. Of course, you can also set up the connection directly via manual steps and deploying the manifests, which saves you step 2.

```c
argocd cluster add aks-vengeance-development --label env=development --upsert --yes
```

You can see a secret in the cockpit and the connection can also be seen in the UI for example like:

![](https://miro.medium.com/v2/resize:fit:640/1*ihF4duF-Qvxt7rp098pdyw.png)

Figure-7: Established Connection to fleet ship

Here are two direct differences compared to Sveltos. Argo has a UI and Sveltos does not yet.  
You have to set the *— — label* flag for each label and with Sveltos you can specify a list.

What is the situation with Sveltos?

[**Sveltos**](https://projectsveltos.github.io/sveltos/getting_started/install/install/)**:**

Sveltos provides two modes for managing clusters: In Mode 1, an agent runs in each managed cluster, which is ideal for standard setups. Mode 2 introduces a different approach where, although each managed cluster still has its own agent, these agents operate within the management cluster itself.

This adaptation (Mode 2), inspired by the [Kamaji architecture](https://github.com/clastix/kamaji) where the managed cluster’s control planes function as pods within the management cluster, ensures that the agents, while centrally located, still exclusively monitor their designated managed cluster’s API server.

So in my own Terms, I will call it:

**Mode-1 (Local Agent Mode)**: For the mode where an agent runs in each managed cluster.

**Mode-2 (Centralized Agent Mode)**: For the mode where agents operate within the management cluster but still monitor each managed cluster.

We will use Mode 1.

```c
kubectl apply -f https://raw.githubusercontent.com/projectsveltos/sveltos/main/manifest/manifest.yaml
kubectl apply -f https://raw.githubusercontent.com/projectsveltos/sveltos/main/manifest/default-classifier.yaml
```

Download and install [sveltosctl CLI:](https://projectsveltos.github.io/sveltos/getting_started/sveltosctl/sveltosctl/)

```c
wget https://github.com/projectsveltos/sveltosctl/releases/download/v0.28.0/sveltosctl-darwin-arm64 -O /usr/local/bin/sveltosctl
chmod +x /usr/local/bin/sveltosctl
```

Now we register the fleet-ship cluster or the fleet ship cluster.

![](https://miro.medium.com/v2/resize:fit:640/1*Bm9U2fq0af1K0yJGUjwINg.gif)

Figure-8: Establish Connection via sveltosctl cli

At this point, Sveltos only requires access to the clusters (Figure 8) and no extra login via the server.

```c
kubectl create ns aks-vengeance-development
sveltosctl register cluster --namespace=aks-vengeance-development --cluster=aks-vengeance-development --fleet-cluster-context=aks-vengeance-development --labels=env=development
```

After the cluster is registered with the previous command, we can display it. Since there is no UI, we can see it with the following command:

```c
kubectl get sveltosclusters.lib.projectsveltos.io -A 

                     
NAMESPACE                   NAME                        READY   VERSION
aks-vengeance-development   aks-vengeance-development           v1.28.3
mgmt                        mgmt                                v1.27.1
```

Since sveltoscluster are *CustomResourceDefinitions*, we can easily retrieve them. With Argo, it is a secret and we can only see the token, server, etc. if we encrypt it.

Both tools offer an easy way to add the clusters to the cockpit. With Argo, it requires an extra step.

At this point, we have the basis to equip the fleet clusters accordingly.

### Let's Deploy

In this step, we want to roll out the Ingress controller to all clusters via a Helm chart with the corresponding label *env=development*.

In **Argo CD**, we create an *ApplicationSet* for this purpose like:

```c
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: nginx-ingress
  namespace: argocd
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            env: development
        values:
          branch: main

  template:
    metadata:
      name: "{{name}}-nginx-ingress"
      annotations:
        argocd.argoproj.io/manifest-generate-paths: ".;.."

    spec:
      project: default
      sources:
        - repoURL: https://github.com/Hamburg-Port-Authority/kubernetes-service-catalog.git
          targetRevision: "{{values.branch}}"
          path: "./networking/ingress-nginx"
          helm:
            releaseName: "ingress-nginx" # Release name override (defaults to application name)
            valueFiles:
              - "values.yaml"
      destination:
        name: "{{name}}"
        namespace: "nginx-ingress"
      syncPolicy:
        automated:
          prune: false
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
        retry:
          limit: 5
```

Here we use a [cluster generator](https://www.google.com/search?client=safari&rls=en&q=generators+argo+cd&ie=UTF-8&oe=UTF-8), which creates an application based on the registered clusters and the matching of the labels and patches it accordingly. This allows cluster-specific overwriting of the values.

This approach allows us at Argo CD to roll out an application across all clusters that match the labels. We can also filter by saying, for example, roll out the application only on the clusters that contain *env=development && networking=true && ingress-controller=nginx*.

The cockpit looks like this:

![](https://miro.medium.com/v2/resize:fit:640/1*QCnspheGLxL940DvHw1rNQ.png)

Figure-9: Deployed NGINX-Ingress into Fleet-Ship

The disadvantages of this are, for example, that you can only combine a maximum of two generators. In addition, **helm and kustomize cannot be combined** at this point. Argo then tries to render both manifests with Helm and once with Kustomize, but does not know which should be applied. It is also not possible to post-patch the manifests.

You then have to define complex solutions such as post-hooks in order to patch the resources afterwards. This was a particular challenge for us when we switched from pod security policies to pod security standards. Most third-party tools had not yet implemented the necessary security context.

In **Sveltos**, the *CustomResourceDefinitions* are called Profiles or *ClusterProfiles*. We create a *ClusterProfile* because, as admins, we want to match the profiles in all clusters.

These then look as follows:

```c
apiVersion: config.projectsveltos.io/v1alpha1
kind: ClusterProfile
metadata:
  name: kyverno
spec:
  clusterSelector: env=prod
  syncMode: Continuous
  helmCharts:
    - repositoryURL: https://kyverno.github.io/kyverno/
      repositoryName: kyverno
      chartName: kyverno/kyverno
      chartVersion: v3.1.4
      releaseName: kyverno-latest
      releaseNamespace: kyverno
      helmChartAction: Install
```

We have set the relationship via the labels and then specify a list of Helm Charts, which is processed in order from top to bottom. We are using kyverno as an example here, as we have already rolled out the ingress-nginx controller via Argo CD.

Then we can see the addon as follows:

```c
sveltosctl show addons
```

Possible Output:

```c
+-----------------------------------------------------+---------------+-----------+----------------+---------+--------------------------------+------------------------+
|                       CLUSTER                       | RESOURCE TYPE | NAMESPACE |      NAME      | VERSION |              TIME              |        PROFILES        |
+-----------------------------------------------------+---------------+-----------+----------------+---------+--------------------------------+------------------------+
| aks-vengeance-development/aks-vengeance-development | helm chart    | kyverno   | kyverno-latest | 3.1.4   | 2024-04-19 19:33:47 +0200 CEST | ClusterProfile/kyverno |
+-----------------------------------------------------+---------------+-----------+----------------+---------+--------------------------------+------------------------+
```

Sveltos has a strong focus on multi-tenancy by design, as can be seen in many places, e.g. in the administration via namespace-based profiles like you can see in the following Figure-10.

![](https://miro.medium.com/v2/resize:fit:640/1*dJfqPs0W3U6G58LkiAJMrw.png)

Figure-10: Profiles vs. ClusterProfiles

With Argo CD, only since version 2.10 has it been possible to create the application in other namespaces and not in a namespace.

### What else?

As you can see, a blog series is necessary to make a detailed comparison. But that is not the aim of the blog. I would like to share the experience we have had with Argo CD for around 2 years and the challenges we have faced.

That is why I have divided the rest into points and will share our experience in 2–3 sentences.

- **Observability (Notifications):** Argo CD is very simplified and can be controlled via a ConfigMap, so the alert rules are quite long. For this reason, we will dispense with the alert rules at this point and use an observability stack instead. Sveltos offers much more here and extends the part with CRDs, which make handling easier. There are also different endpoints provided by [Sveltos for notifications](https://projectsveltos.github.io/sveltos/observability/notifications/) such as Teams, Discord, Slack, etc.
- **UI:** at Argo CD is great, it makes getting started smooth, especially for developers starting out in the field. Contains all the necessary information and the login via an OIDC provider such as Azure also works perfectly for us. I’m currently missing that part of Sveltos, but it will probably come one day.
- **Templating/Patching Limitations:** I had already explained earlier that we had challenges with patching the rendered resources. Sveltos seems to offer a lot more at this point and provides helmet charts, kustomize, jsonet, ytt, etc. Sveltos also offers interfaces to patch resources e.g. via a ConfigMap. This makes it possible to fetch resources, e.g. to perform an operation in the target cluster when credentials have to be created and then pass them directly to the management cluster so that further operations can take place. This means that no intermediate steps or extra tools are required.
- **Multi-Tenancy:** Sveltos was created directly with a multi-tenancy concept, which can be seen, for example, in the profiles and cluster profiles for determining and managing tenants. Anyone who has tried to set up a [multi-tenancy setup with Argo CD](https://medium.com/devops-dev/gitops-multi-tenancy-with-argo-cd-74ce8ec3bbf5) knows how exhausting and time-consuming it is.
- **Events:** Both tools offer great events integration, although Argo CD offers a much [larger portfolio of triggers](https://argoproj.github.io/argo-events/). This is probably due to the fact that events are strongly integrated into the Argo workflow approach. [Sveltos events](https://projectsveltos.github.io/sveltos/events/addon_event_deployment/) are tailored to the essential to manage multi-cluster.

## Conclusion

In summary, Sveltos fully unveils its GitOps capabilities when combined with Flux CD, a vital combination for us as Platform Engineers to enable GitOps at scale. Initially, newcomers may find entering Sveltos challenging due to the absence of a user interface and the necessity to learn two tools simultaneously when integrated with GitOps. But it fulfills exactly the purpose for which it was built, namely to manage add-ons distributed across clusters securely and stably via a reconcilable loop.

I am optimistic that Sveltos will become more user-friendly in the coming months. Utilizing Sveltos over CI/CD should present no obstacles, in my opinion. Moreover, Sveltos inherently supports features like multi-tenancy, the agent based drift notification and sync, to saver resources, which are becoming increasingly crucial due to rising cloud and on-premise costs. We aim to avoid further driving up costs with engineering hours.

It’s important to remember that Argo has around 1,300 contributors and has been around since about 2018. Sveltos, on the other hand, has about five contributors, has been in existence since roughly 2022 and is fully Open Source. Even so, the Sveltos contributors have done commendable work and introduced a robust tool to the market.

I look forward to future developments and am grateful for the fresh perspectives and insights gained through Sveltos. [Gianluca](https://www.linkedin.com/in/gianlucamardente/) is very receptive to feedback, quickly implementing solutions, so feel free to contribute and share your input. Don’t forget to leave a [STAR 🌟](https://github.com/projectsveltos/addon-controller)!

## Contact Information

If you have some Questions, would like to have a friendly chat or just network to not miss any topics, then don’t use the comment function at medium, just feel free to add me to your [LinkedIn](https://www.linkedin.com/in/artem-lajko-%E2%98%81%EF%B8%8F-%E2%8E%88-82139918a/) network!

## References

- [https://github.com/projectsveltos](https://github.com/projectsveltos)
- [https://projectsveltos.github.io/sveltos/](https://projectsveltos.github.io/sveltos/)
- [https://github.com/projectsveltos/addon-controller](https://github.com/projectsveltos/addon-controller)
- [https://github.com/fluxcd/flux2](https://github.com/fluxcd/flux2)
- [https://projectsveltos.github.io/sveltos/blogs/](https://projectsveltos.github.io/sveltos/blogs/)

Do something with cloud, kubernetes, gitops and all the fancy stuff [https://www.linkedin.com/in/lajko](https://www.linkedin.com/in/lajko)

## More from Artem Lajko and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--fa2b94b2ea48---------------------------------------)