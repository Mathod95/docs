---
title: "State of Cloud‑Native 2026: CNCF CTO’s Insights and Predictions"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://horovits.medium.com/state-of-cloud-native-2026-cncf-ctos-insights-and-predictions-479e6bbf793c
author:
  - "[[Dotan Horovits (@horovits)]]"
---
<!-- more -->

[Sitemap](https://horovits.medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*q9FNw5DoLZZZ8xhVHSXOWA.png)

State of Cloud‑Native 2026: CNCF CTO’s Insights and Predictions | @horovits | Medium

We’ve just celebrated the [10th anniversary to the Cloud Native Computing Foundation](https://medium.com/@horovits/cncf-ambassadors-reflections-on-10-years-of-the-cloud-native-computing-foundation-a796646db552) (CNCF), the foundation behind Kubernetes and so many other successful open source projects we all rely on. That’s a good reason to sit down with the CTO and co-founder of the CNCF at the start of 2026, look at the state of cloud native, and discuss what’s coming next.

## The state of the CNCF

Ten years into CNCF’s journey, that sense of amazement is exactly how I feel. What began with Kubernetes and roughly twenty members has grown into an ecosystem of over 230 projects and more than 300,000 contributors across more than 190 countries around the world.

Over the decade the scope of CNCF has expanded well beyond container orchestration to include observability, service meshes, platform engineering, FinOps and now elements of the AI stack. Chris clarifies that it’s the result of an approach that keeps evolving based on user needs, not by clinging to one narrow definition of “cloud native.”

## Kubernetes: from orchestrator to de facto OS

Kubernetes has been the cornerstone of the CNCF. We discussed the evolution of Kubernetes from its original scope as an orchestrator into what I’d call the operating system for cloud native workloads. In fact, Kubernetes trails Linux (a 34 years old project, mind you) as the highest development velocity project, according to the current devstats dashboards.

Rather than swallowing every feature, Chris highlights, Kubernetes’ maintainers focused on avoiding bloat (moving storage to CSI, runtimes to CRI, etc.) and improving the UX with projects like K3s and Headlamp. That discipline helped Kubernetes scale beyond containers into supporting GPU/TPU inference and other edge, industrial and now AI-focused needs.

This took me back to my [fireside with Kelsey Hightower](https://horovits.medium.com/kubernetes-turns-10-a-fireside-chat-with-kelsey-hightower-on-its-impact-and-future-475bbc7137a4) back when we celebrated a decade to Kubernetes, and the insights he gave about the evolving role of Kubernetes

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*2SKtdHbNmTBEE7B2.png)

OpenObservability Talks: Kubernetes and Beyond: A fireside Chat with Kelsey Hightower

## Observability, security, and AI: a convergence

Chris gave an interesting observation about how observability and security are converging. He pointed to industry moves where traditional security vendors acquire observability companies — a sign that observability is essential to doing security well at scale. [As AI workloads ramp up, observability data will be the backbone](https://horovits.medium.com/observability-for-ai-workloads-a-new-paradigm-for-a-new-era-b8972ba1b6ba) for security, ops, and analytics. With consistent data collection (OpenTelemetry-style tooling) and better instrumentation, Chris believes the groundwork is there to unify analysis across these domains.## [Observability for AI Workloads: A New Paradigm for a New Era](https://horovits.medium.com/observability-for-ai-workloads-a-new-paradigm-for-a-new-era-b8972ba1b6ba?source=post_page-----479e6bbf793c---------------------------------------)

Lessons from 2025 and insights for building observable AI systems in productions

horovits.medium.com

[View original](https://horovits.medium.com/observability-for-ai-workloads-a-new-paradigm-for-a-new-era-b8972ba1b6ba?source=post_page-----479e6bbf793c---------------------------------------)

## FinOps for AI and the rise of niche clouds

AI isn’t just a technical challenge — it’s a cost one. Chris sees FinOps practices extending to AI workloads as teams wrestle with large inference and training bills. That cost pressure will drive experimentation: from hyperscalers to GPU-first micro-clouds and regional providers focused on data sovereignty. Kubernetes and CNCF projects will be crucial glue to enable portability and interoperability across these varied environments.

## A controversial prediction: AI as a top open source contributor

Chris shared a provocative prediction: by 2026 year-end, AI-powered systems will be among the top contributors to many open source projects — at least by volume. That will increase the review burden on maintainers and force communities to adapt review processes and tooling. It’s an important reminder that higher contribution volume doesn’t automatically mean higher quality; governance and review will matter more than ever. It gave me a flashback a few years back when Stack Overflow mods started getting flooded with AI-generated coding answers, many of which looked credible and knowledgable but contained major flaws or even plain wrong.

Want to learn more? Check out the OpenObservability Talks episode: A Decade of CNCF: Fireside Chat with the CTO.

Happy new year y’all!

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*ZIuc7OxBE4IpipdP.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*uz_v5y9GuMWAJyVt.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*M352tKh9KNWmDxJD.png)

## More from Dotan Horovits (@horovits)

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--479e6bbf793c---------------------------------------)