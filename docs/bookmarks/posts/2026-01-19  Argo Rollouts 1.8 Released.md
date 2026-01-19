---
title: "Argo Rollouts 1.8 Released"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.argoproj.io/argo-rollouts-1-8-released-cf3183fae1af"
author:
  - "[[Zach Aller]]"
---
<!-- more -->

[Sitemap](https://blog.argoproj.io/sitemap/sitemap.xml)## [Argo Project](https://blog.argoproj.io/?source=post_page---publication_nav-21be29067291-cf3183fae1af---------------------------------------)

[![Argo Project](https://miro.medium.com/v2/resize:fill:76:76/1*ZJ10oT9u3uqJVT-Rkyb0bQ.png)](https://blog.argoproj.io/?source=post_page---post_publication_sidebar-21be29067291-cf3183fae1af---------------------------------------)

[https://github.com/argoproj/](https://github.com/argoproj/)

Welcome Argo Rollouts 1.8! This release had 53 contributors, of which 39 were first-timers, and includes 202 commits! Thank you all for your contributions! There are some really nice features in this release so let’s take a look.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*anQTvyi32Mpo6dIWszWrDg.png)

## Canary Step Plugins

This exciting new feature allows you to configure new steps in your Canary configured Rollout. With this plugin system, you are now able to [create a plugin and execute your own steps](https://argo-rollouts.readthedocs.io/en/stable/features/canary/plugins/) during the canary analysis. This extends Argo Rollouts capabilities and enriches the progressive delivery experience to accommodate a multitude of scenarios. It is a continuation of the previous work that was done to create a pluggable system for traffic routers and metric providers in the v1.5 release.

You can refer to the [documentation](https://argo-rollouts.readthedocs.io/en/latest/plugins/) to learn more about creating a plugin. Once implemented, it can be configure in the argo-rollouts-config ConfigMap:

```hs
apiVersion: v1
kind: ConfigMap
metadata:
  name: argo-rollouts-config
data:
  stepPlugins: |-
    - name: "argoproj-labs/step-exec" # name of the plugin
      location: "file://./my-custom-plugin" # supports http(s):// urls and file://Ya
```

Users can then configure this plugin as part of their canary steps:

```hs
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: example-plugin-ro
spec:
  strategy:
    canary:
      steps:
        - plugin:
            name: argoproj-labs/step-exec
            config:
              command: echo "hello world"
```

While these plugins do not require to be open-source, we are looking forward to what the community will implement in the upcoming months. If you are interested in contributing a canary step plugin to the community, simply open an issue under argo-rollouts requesting an argoproj-labs repository to host your plugin.

Contributed by: [Alexandre Gaudreault](https://github.com/agaudreault)

## Analysis Consecutive Success Limit

This provides the *inverse* of what an analysis currently does. The main use case for this is to allow users to wait on a condition (in a step analysis especially) to hold, before proceeding to the next step.

Here is an example analysis:

```hs
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result[0] <= 0.95
    consecutiveSuccessLimit: 3
    provider:
      prometheus:
        address: http://prometheus.example.com:9090
        query: |
          sum(irate(
            istio_requests_total{reporter="source",destination_service=~"{{args.service-name}}",response_code!~"5.*"}[1m]
          )) /
          sum(irate(
            istio_requests_total{reporter="source",destination_service=~"{{args.service-name}}"}[1m]
          ))
```

You can find more information in the documentation found [here](https://argo-rollouts.readthedocs.io/en/latest/features/analysis/#consecutivesuccesslimit-and-failurelimit).

Contributed by: [Youssef Rabie](https://github.com/y-rabie)

## Other Features

- New Prometheus metric: build\_info ([#3591](https://github.com/argoproj/argo-rollouts/issues/3591))
- Enable pprof profiling support ([#3769](https://github.com/argoproj/argo-rollouts/issues/3769))
- Allow specifying full annotations for Nginx canary ([#3671](https://github.com/argoproj/argo-rollouts/issues/3671))
- Credentials to download plugin ([#3905](https://github.com/argoproj/argo-rollouts/issues/3905))

## Bug fixes

We had 36 labeled bug fixes in this release some of the area’s of focus for bugs have been around Rollouts getting stuck progressing and better verification of not causing any outage during a rollout. So, if you have experienced any of these issue test this release out and let us know how it behaves.

## Summary

This releases big feature was around step plugins, I can’t wait to see what this feature empowers end users to create. Feel free to share in the CNCF Argo Rollouts Slack channel and open an issue if you would like a plugin repo on argoproj-labs. Additionally, delve into the complete change log [here](https://github.com/argoproj/argo-rollouts/blob/master/CHANGELOG.md), and don’t forget to try out the release, available . A heartfelt thank you goes out to all those who contributed to this release.

## More from Zach Aller and Argo Project

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--cf3183fae1af---------------------------------------)