---
title: "Automation using Control planes vs. Command-line tools"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/automation-using-control-planes-vs-command-line-tools-66f818ff8278"
author:
  - "[[Brian Grant]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-66f818ff8278---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*RfP6NfiECPe380Z7Iaj4_Q.png)

In my [post about GitOps](https://medium.com/@briankgrant/is-gitops-actually-useful-a1c851ba99d8), I mentioned evolving the client-side “kubectl rolling-update” to the server-side Kubernetes [Deployment controller](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) /API. Different projects have made different choices whether to implement a command-line-based tool or control-plane-based automation, and projects have changed their decisions over time.

For example, Docker Swarm started as a libswarm library, then a CLI-based feature IIRC, then a control plane, whereas Kubernetes was always control-plane-based, but had features that moved from the CLI to the control plane. [Helm](https://helm.sh/) v1 was a command-line tool, Helm v2 introduced the Tiller server, and Helm v3 [removed Tiller](https://helm.sh/docs/faq/changes_since_helm2/), but GitOps [Operators](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) like [FluxCD](https://fluxcd.io/) and [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) add back control-plane functionality. Terraform is a command-line tool, but a number of services, such as those with [catalogs](https://medium.com/@briankgrant/what-is-it-with-template-catalogs-7637c24d5200), wrap control planes around it. Other projects that provision infrastructure, like [Crossplane](https://www.crossplane.io/why-control-planes) and [Radius](https://docs.radapp.io/concepts/technical/architecture/#ucp-a-general-resource-management-api), put control planes at their cores.

This got me thinking about the tradeoffs between client-side and server-side implementations and the criteria regarding which to choose. Maybe it seems obvious, but evidently it isn’t always.

Back around 2018 when Crossplane and Google Cloud’s [Config Connector](https://cloud.google.com/config-connector/docs/overview) got started, [Custom Resource Definitions](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) were fairly [new](https://pwittrock.github.io/docs/tasks/access-kubernetes-api/migrate-third-party-resource/) and the [Operator pattern](https://www.redhat.com/en/blog/introducing-operators-putting-operational-knowledge-into-software) was building momentum. By 2020–2021, there was a fair bit of discussion about using Kubernetes as a universal control plane ([1](https://thenewstack.io/kubernetes-is-the-new-control-plane-for-infrastructure/), [2](https://thenewstack.io/how-kubernetes-is-becoming-the-universal-control-plane-for-distributed-applications/), [3](https://blog.cedriccharly.com/post/20200426-kubernetes-the-universal-control-plane/), [4](https://containerjournal.com/kubeconcnc/kubernetes-true-superpower-is-its-control-plane/), [5](https://thenewstack.io/how-google-turned-kubernetes-into-a-control-plane-to-manage-gcp-resources/), [6](https://labs.sogeti.com/kubernetes-the-new-cloud-control-plane/), [7](https://medium.com/@allingeek/kubernetes-as-a-common-ops-data-plane-f8f2cf40cd59), [8](https://blog.yugabyte.com/recap-kubernetes-as-a-universal-control-plane-joe-beda-vmware/), [9](https://containerjournal.com/features/treating-kubernetes-as-a-source-of-truth/)). Some people are using Kubernetes that way for some things, but [not everyone](https://www.reddit.com/r/kubernetes/comments/vtt1vx/are_kubernetes_operators_not_that_popular_yet/) is doing all automation using [Operators](https://digitalis.io/blog/kubernetes/kubernetes-operators-pros-and-cons/).

The main advantage of client-side tools is fairly obvious: they’re simple. ==They are relatively simple to write, install, authenticate, run, individually upgrade, extend via plugins, and embed into CI/CD pipelines==. Server-side implementations are more difficult in all of those areas.

So when is it worth bothering with a control-plane-based implementation for automation?

1. You want/need continuous operation, or really long-running operations, like hours, days, or longer. Command-line tools have to be invoked. Servers run continuously. It’s possible to run command-line tools in an infinite loop, but they aren’t designed for that.
2. If you need fault tolerance, resilience, and/or decently high availability while operations run, that suggests a server-side implementation is what you need.
3. If the automation needs to react to spontaneous changes in the resources under management, such as in the case of autoscaling, that suggests you need a service.
4. The automation needs to orchestrate operations on large numbers of entities. This is a case that probably includes all of the previous needs, and also may need to be parallelized and adaptive, as in the [retail edge case I mentioned in the GitOps post](https://medium.com/@briankgrant/is-gitops-actually-useful-a1c851ba99d8).
5. You want/need an API. It’s easier to build robust, observable higher-level automation controllers on top of APIs than on scripts, pipelines, and log files. [Pulumi’s Automation API](https://www.pulumi.com/automation/) is a good example. It’s possible to create local APIs in client-side components, but it makes access through multiple programming languages and from some environments (e.g., web browsers, serverless functions) harder.
6. You want/need to access the functionality through multiple user-interface surfaces, such as GUIs and LLM chat bots, in addition to a CLI. Continuously updated status dashboards and multi-player experiences are enabled by services. Accessing the functionality through multiple Infrastructure as Code tools, such as Terraform, Pulumi, and Crossplane, also becomes more straightforward. The [Terraform provider plugin API](https://developer.hashicorp.com/terraform/plugin/framework/providers) is kind of a de facto standard now, but it’s not a fully open standard, it’s harder to integrate with programming languages other than Go, and it wasn’t designed to be consumed by a variety of clients, which creates integration friction.
7. You want/need more control over what users can and can’t do. Client tools use end-user credentials or service accounts accessible to those users, so effectively those users would have to be directly granted permissions to do what they need to do. Services can proxy operations by [running with elevated privileges](https://medium.com/@briankgrant/what-is-it-with-template-catalogs-7637c24d5200) relative to end users and then impose role-based access control, state-based constraints, quotas, and other controls to constrain what users can do with their power.
8. You want to encapsulate the implementation, such as to not directly expose backend systems, for security, privacy, reliability, or ease of evolution. Similar to the previous point, but a slightly different motivation.
9. You want to shift the operational burden from users to service operators: telemetry, upgrades, troubleshooting, etc. This can be challenging when lots of users are individually running instances of command-line tools of different versions in their own environments.

There may be some other motivations also, but those are some common ones I see.

Given the complexity, it makes sense to start with a command-line implementation and only graduate to a control-plane-based implementation when truly warranted.

Do you prefer to use automation tools that are just CLIs or that require control planes? Does it make a difference if the control plane is a SaaS rather than a system you have to run and manage yourself? Do you view control planes differently than per-node agents?

Feel free to reply here, or send me a message on [LinkedIn](https://www.linkedin.com/in/bgrant0607/) or [X/Twitter](https://x.com/bgrant0607), where I plan to crosspost this.

You may be interested in other posts in my [Infrastructure as Code](https://medium.com/@bgrant0607/list/infrastructure-as-code-and-declarative-configuration-8c441ae74836) or [Kubernetes](https://medium.com/@bgrant0607/list/kubernetes-8b0b8930195b) series.

CTO of ConfigHub. Original lead architect of Kubernetes and its declarative model. Former Tech Lead of Google Cloud's API standards, SDK, CLI, and IaC.

## More from Brian Grant and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--66f818ff8278---------------------------------------)