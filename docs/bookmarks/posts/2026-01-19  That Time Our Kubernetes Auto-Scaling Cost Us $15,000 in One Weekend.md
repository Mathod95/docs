---
title: "That Time Our Kubernetes Auto-Scaling Cost Us $15,000 in One Weekend"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://aws.plainenglish.io/that-time-our-kubernetes-auto-scaling-cost-us-15-000-in-one-weekend-d6ede12d30bd"
author:
  - "[[Dev engineer]]"
---
<!-- more -->

[Sitemap](https://aws.plainenglish.io/sitemap/sitemap.xml)## [AWS in Plain English](https://aws.plainenglish.io/?source=post_page---publication_nav-35e7a49c6df5-d6ede12d30bd---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:76:76/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_sidebar-35e7a49c6df5-d6ede12d30bd---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.

*(And how we stopped it from happening again)*

## The Panic Sets In

I was brushing my teeth on a Sunday morning when my phone started blowing up:

> *Slack Alert from AWS: “Your monthly spend has exceeded 80% of budget”  
> Finance Team: “Why is there a $5,000 charge from AWS this morning?!”*

Turns out, our “smart” Kubernetes auto-scaling had gone completely rogue. What we thought was a minor config tweak on Friday afternoon had spun up 87 copies of a service that normally runs 3 pods — burning cash faster than a crypto startup at a Vegas conference.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*6QX0GgugDIXIEw-Y.jpeg)

Here’s what happened (with screenshots from our actual incident report), and how we fixed it.

## The Perfect Storm of Bad Decisions

We were running a Java service that processes background jobs. It worked fine for months… until we tried to “optimize” it.

## Mistake #1: The Overconfident HPA Config

Our `HorizontalPodAutoscaler` looked reasonable at first glance:

```c
# What we HOPED would happen:
# "Gently scale between 2-20 pods based on CPU"
```
```rb
# What ACTUALLY happened:
# "SCALE ALL THE THINGS!!"  
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  maxReplicas: 100  # 🤦 WHY did we think this was okay?!
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 50  # Aggressive AF
```

## Mistake #2: No Safeguards

- No PodDisruptionBudget: When scaling down, Kubernetes murdered pods like Game of Thrones characters
- No AWS billing alerts: We found out from Finance, not our monitoring
- Bad metric: CPU was a terrible scaling signal for this workload

## How We Debugged The Madness

## 1\. The “Oh Sh\*t” Moment

Ran `kubectl top pods` and saw:

```c
NAME                          CPU(cores)  
worker-service-abc123         5m          # Basically idle  
worker-service-def456         7m  
... (87 more lines of this nonsense)
```

## 2\. The Root Cause

- Our Java app had brief CPU spikes during GC
- HPA saw this as “OMG WE NEED MORE PODS”
- Each new pod caused more GC spikes, creating a feedback loop

*(Here’s an actual screenshot from our Prometheus dashboard showing the insanity:)*  
\[INSERT IMAGE: CPU % spiking like a heartbeat gone wrong\]

## How We Fixed It (For Real This Time)

## 1\. We Stopped Using CPU for Scaling

Switched to Kafka queue depth metrics (since this was a queue worker):

```c
metrics:
- type: External  # Now scales based on actual work
  external:
    metric:
      name: kafka_messages_behind  
    target:
      averageValue: 1000
```

## 2\. Added Scaling Friction

```c
maxReplicas: 10  # Hard ceiling  
minReplicas: 1   # Let it breathe
```

## 3\. Cost Controls That Actually Work

- AWS Budget Alert: Now emails AND Slack at $500 increments
- Cluster Autoscaler Settings:
- bash
- Copy
- Download
- — scale-down-unneeded-time=15m # Don’t react too fast — skip-nodes-with-local-storage=true # Protect stateful stuff

## Lessons Learned (The Hard Way)

1. Auto-scaling isn’t “set and forget” — It’s more like a pet than cattle
2. Test scaling changes on Friday? Bad idea. Deploy scaling tweaks on Tuesday mornings
3. Finance teams make great alert systems (but they won’t be happy about it)

Pro Tip: Run `kubectl get hpa -w` in a terminal before deploying HPA changes. Seeing numbers jump in real-time is terrifying… but less terrifying than an AWS bill.

## Your Turn

Ever had Kubernetes auto-scaling backfire? Reply with your disaster story — I’ll buy you a coffee if yours was more expensive than ours.

## Thank you for being a part of the community

*Before you go:*

- Be sure to **clap** and **follow** the writer ️👏️ **️**
- Follow us: [**X**](https://x.com/inPlainEngHQ) | [**LinkedIn**](https://www.linkedin.com/company/inplainenglish/) | [**YouTube**](https://www.youtube.com/@InPlainEnglish) | [**Newsletter**](https://newsletter.plainenglish.io/) | [**Podcast**](https://open.spotify.com/show/7qxylRWKhvZwMz2WuEoua0) | [**Twitch**](https://twitch.tv/inplainenglish)
- [**Start your own free AI-powered blog on Differ**](https://differ.blog/) 🚀
- [**Join our content creators community on Discord**](https://discord.gg/in-plain-english-709094664682340443) 🧑🏻💻
- For more content, visit [**plainenglish.io**](https://plainenglish.io/) + [**stackademic.com**](https://stackademic.com/)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:96:96/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--d6ede12d30bd---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:128:128/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--d6ede12d30bd---------------------------------------)

[Last published 4 hours ago](https://aws.plainenglish.io/how-to-run-a-web-application-in-aws-on-a-tight-budget-c659e5bdc3ce?source=post_page---post_publication_info--d6ede12d30bd---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.

CI/CD, AWS & K8s expert. Cut costs by 90%, sped up deploys. Passionate about scalable systems & ending over-engineering. Let’s build smarter. 🚀