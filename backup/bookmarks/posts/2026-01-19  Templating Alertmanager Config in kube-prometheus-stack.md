---
title: "Templating Alertmanager Config in kube-prometheus-stack"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://tech.loveholidays.com/templating-alertmanager-config-in-kube-prometheus-stack-6901a50857ce"
author:
  - "[[Dan Williams]]"
---
<!-- more -->

[Sitemap](https://tech.loveholidays.com/sitemap/sitemap.xml)## [loveholidays tech](https://tech.loveholidays.com/?source=post_page---publication_nav-6ba41fdba790-6901a50857ce---------------------------------------)

[![loveholidays tech](https://miro.medium.com/v2/resize:fill:76:76/1*Tn8bGS0wfOJbm6wA5dhlqg.png)](https://tech.loveholidays.com/?source=post_page---post_publication_sidebar-6ba41fdba790-6901a50857ce---------------------------------------)

Stories in tech, product and design at loveholidays

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Or-4siwXokKMt0tu.png)

Here at loveholidays we run Alertmanager in our Kubernetes Clusters (GKE) to route alerts from Prometheus and Loki to Slack and PagerDuty. This is deployed via the [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) Helm Chart and is an industry-standard way of doing things.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*gBTCDy0GZNvBhrDZ)

Without Alertmanager, we would have no alerts or out of hours pages. We wouldn’t have any visibility into systems breaking. Alertmanager is the unsung hero of our infrastructure.

loveholidays’ “you build it, you run it” culture means that, although the infrastructure team is responsible for the uptime of Alertmanager, it is the dev teams themselves that are responsible for creating the configuration within Alertmanager to make sure alerts are routed to their team’s slack channel(s) correctly.

We previously blogged about “ [dynamic alert routing with Prometheus and Alertmanager](https://tech.loveholidays.com/dynamic-alert-routing-with-prometheus-and-alertmanager-f6a919edb5f8) ”, and the TL;DR still holds up 3 years later:

> *TL;DR Dynamically route alerts to relevant Slack team channels by labelling Kubernetes resources with team and extracting team label within alert rules.*

## A monster is born

Over the last 5 years of running Alertmanager, the configuration driving Alertmanager has grown to a whopping 1700 lines of YAML, with our 15 (and growing) engineering teams each requiring their own set of Routes and Receivers to make sure alerts get to their channels.

1700 lines might not sound *that* drastic, but the list of Routes within Alertmanager is an ordered list, meaning that a team inserting a Route in the wrong place can affect or even break the routing for every other team.

Let’s look at a very simple configuration for a single team, teamA. Our alerts have a team label on them which is used to route the alert to the correct place. Alerts that don’t have a team label may have a namespace label, so we create a route for each possibility.

```c
---
alertmanager:
  config:
    route:
      group_by: [alertname]
      group_interval: 60m
      group_wait: 30s
      repeat_interval: 12h
      routes:
        - receiver: slack_teamA_alerts_channel
          matchers:
            team="teamA"
        - receiver: slack_teamA_alerts_channel
          matchers:
            namespace="teamA"
    receivers:
     - name: slack_teamA_alerts_channel
       slack_configs:
         - api_url: https://hooks.slack.com/services/...
           channel: '#teamA-alerts'
           send_resolved: true
```

This doesn’t look too bad, right? We define a pair of Routes for teamA, which sends any alert with a `team=teamA` label or `namespace=teamA` to the matching Receiver, which will in turn route those alerts to the Slack channel for `#teamA-alerts`.

teamA runs an on-call rota, which means certain alerts need to be routed to PagerDuty to page them out of hours. For this, some alerts will have a `pagerduty: active` label on them. This means we need an additional Route and Receiver, so our config doubles in size:

```c
alertmanager:
  config:
    route:
      group_by: [alertname]
      group_interval: 60m
      group_wait: 30s
      repeat_interval: 12h
      routes:
        - receiver: pagerduty_teamA
          group_interval: 10s
          group_wait: 10s
          repeat_interval: 1h
          matchers:
            - team="teamA"
            - pagerduty="active"
        - receiver: slack_teamA_alerts_channel
          matchers:
            - team="teamA"
        - receiver: slack_teamA_alerts_channel
          matchers:
            namespace="teamA"
    receivers:
     - name: slack_teamA_alerts_channel
       slack_configs:
         - api_url: https://hooks.slack.com/services/...
           channel: '#teamA-alerts'
           send_resolved: true
     - name: pagerduty_teamA
       pagerduty_configs:
         - service_key: <teamA-pagerduty-service-key>
           description: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ end }}'
```

Remember, routes is an ordered list, so alerts with the correct team label and PagerDuty labels will be sent to PagerDuty, and alerts that don’t have the PagerDuty label go to Slack.

teamB needs to do the same thing, so our config doubles in size again:

```c
alertmanager:
  config:
    route:
      group_by: [alertname]
      group_interval: 60m
      group_wait: 30s
      repeat_interval: 12h
      routes:
        - receiver: pagerduty_teamA
          group_interval: 10s
          group_wait: 10s
          repeat_interval: 1h
          matchers:
            - team="teamA"
            - pagerduty="active"
        - receiver: slack_teamA_alerts_channel
          matchers:
            - team="teamA"
        - receiver: slack_teamA_alerts_channel
          matchers:
            namespace="teamA"
        - receiver: pagerduty_teamB
          group_interval: 10s
          group_wait: 10s
          repeat_interval: 1h
          matchers:
            - team="teamB"
            - pagerduty="active"
        - receiver: slack_teamB_alerts_channel
          matchers:
            - team="teamB"
        - receiver: slack_teamB_alerts_channel
          matchers:
            namespace="teamB"
    receivers:
     - name: slack_teamA_alerts_channel
       slack_configs:
         - api_url: https://hooks.slack.com/services/...
           channel: '#teamA-alerts'
           send_resolved: true
     - name: slack_teamB_alerts_channel
       slack_configs:
         - api_url: https://hooks.slack.com/services/...
           channel: '#teamB-alerts'
           send_resolved: true
     - name: pagerduty_teamA
       pagerduty_configs:
         - service_key: <teamA-pagerduty-service-key>
           description: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ end }}'
     - name: pagerduty_teamB
       pagerduty_configs:
         - service_key: <teamB-pagerduty-service-key>
           description: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ end }}'
```

Our config is already looking less welcoming, and this is just to add very basic functionality for two teams. Some of our teams set custom values for things like `group_interval`, `repeat_interval`, `group_wait`, and `group_by`. Some teams have additional Routes to route different severity alerts to different Slack channels, and Routes for other custom logic.

Scale this up to 15+ teams, each deploying their own configuration, each with their own set of requirements, custom routing rules and features. Eventually your infrastructure team will start getting questions like “ *Why did this alert go to the wrong channel?*” or “ *I made this routing change and accidentally paged every team in the company* ” (true story..).

Slowly, but surely, a 1700 line YAML monster was born.

## Is this really platform engineering?

Although this hard-coded approach has scaled with our growth, it is a constant source of misconfiguration and cognitive load on our dev teams. They want to receive alerts (well, as much as anyone *wants* to receive alerts..) and to be paged when things go wrong, but why should they have to learn and know the ins-and-outs of Alertmanager’s syntax?

Why should adding a new team become a huge task to find the right place in those 1700 lines of config to add the new Routes and Receivers?

The whole concept of platform engineering here at loveholidays is about making dev team’s lives easier, and offering tooling / platform solutions to common problems. Our monstrous config, as functional as it is, is not a platform engineering solution.

Alertmanager has made an effort to improve this situation with the [AlertmanagerConfig CRD](https://docs.okd.io/latest/rest_api/monitoring_apis/alertmanagerconfig-monitoring-coreos-com-v1beta1.html).

Multiple `AlertmanagerConfig` resources can be created (e.g. one per team), and Alertmanger is responsible for merging them all together into a single configuration.

There are limitations with this approach which stopped us using it:

- `AlertmanagerConfig` is a namespace-scoped resource — “ *the Alertmanager configuration only applies to alerts for which the namespace label is equal to the namespace of the AlertmanagerConfig resource.*” — [source](https://docs.okd.io/latest/rest_api/monitoring_apis/alertmanagerconfig-monitoring-coreos-com-v1beta1.html#spec)
- We lose all control over the ordering of the merge of multiple `AlertmanagerConfig` CRDs. The ordered list of Routes is critical for ensuring alerts go to the right place, and if each team maintains their own `AlertmanagerConfig` resource, we need to ensure the final configuration is still correct.
- It doesn’t reduce the burden on dev teams at all. It just moves it. They still need to understand what they’re building and the syntax of Alertmanager, except with this approach, it’s now spread out into multiple places.

Karuppiah Natarajan produced an article running through examples of using this CRD which is well worth a read: [Trying out Prometheus Operator’s Alertmanager and Alertmanager Config Custom Resources](https://karuppiah.dev/trying-out-prometheus-operators-alertmanager-and-alertmanager-config-custom-resources)

## Fighting fire with fire

The [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) Helm Chart takes the Alertmanager configuration as part of a Values file, so our configuration lives in a values.yaml file under `.Values.alertmanager.config`.

The Chart renders this as such:

```c
alertmanager.yaml: {{ toYaml .Values.alertmanager.config | b64enc | quote }}
```

At the time of writing (Feb 2025), this is done in [secret.yaml](https://github.com/prometheus-community/helm-charts/blob/52124643c41e76176deda42ac0fd36d9b2e23123/charts/kube-prometheus-stack/templates/alertmanager/secret.yaml) and the file has not changed since Feb 2023.

That file, secret.yaml, holds some secrets of its own. I discovered this purely by accident when I was searching for something unrelated in the Helm Chart templates:

```c
data:
{{- if .Values.alertmanager.tplConfig }}
{{- if .Values.alertmanager.stringConfig }}
  alertmanager.yaml: {{ tpl (.Values.alertmanager.stringConfig) . | b64enc | quote }}
```

`tplConfig` and `stringConfig ` — anything passed to a `tpl` function in Helm can essentially render a Helm Template within the Values file. This means we could write a template to generate our Alertmanager config *within* the kube-prometheus-stack values file, and just expose a simple interface to our dev teams?

Let’s go through a practical example, recreating the examples we used in the first half of this post. Our goal is to render the template for teamA and teamB with their team, namespace and PagerDuty Routes.

First, we extend the Helm Values syntax, by adding our own set of team definitions in-line in the kube-prometheus-stack Values file:

```c
alertmanager:
  loveholidays:
    teams:
      teamA:
        slack_channel: teamA-alerts
        namespaces: [teamA]
        pagerduty_service_key: <pagerduty-service-key>

      teamB:
        slack_channel: teamB-alerts
        namespaces: [teamB]
        pagerduty_service_key: <pagerduty-service-key>
```

We then create a template in-line, to iterate over our teams dict and render the desired config:

```c
alertmanager:
  tplConfig: true
  stringConfig: |
    global:
      resolve_timeout: 5m
      slack_api_url: https://hooks.slack.com/services/<slack-webhook-url>
    templates:
      - '/etc/alertmanager/config/*.tmpl'
    route:
      group_by: [alertname]
      group_interval: 60m
      group_wait: 30s
      repeat_interval: 12h 
      receiver: slack_alertmanager
      routes:
      {{- range $k, $v := .Values.alertmanager.loveholidays.teams }}
      {{- $slackReceiver := printf "team_%s_slack" $k }}
      {{- $pagerdutyReceiver := printf "team_%s_pagerduty" $k }}
      {{- $team := $k }}
         
      {{- if $v.pagerduty_service_key }}
      ## PagerDuty rules for team: {{ $k }}
        - receiver: {{ $pagerdutyReceiver }}
          group_wait: 10s
          group_interval: 10m
          repeat_interval: 1h
          continue: true
          matchers:
            - pagerduty="active"
            - team=~"{{ $team }}"
      {{- end }}

      ## label team route for team: {{ $k }}
        - receiver: {{ $slackReceiver }}
          matchers:
            - team=~"{{ $team }}"

      ## label namespace route for team: {{ $k }}
        - receiver: {{ $slackReceiver }}
          matchers:
            - namespace=~"{{ join "|" $v.namespaces }}"
      {{- end }}

    receivers:
    {{- range $k, $v := .Values.alertmanager.loveholidays.teams }}
    {{- $slackReceiver := printf "team_%s_slack" $k }}
    {{- $pagerdutyReceiver := printf "team_%s_pagerduty" $k }}
    {{- $team := $k }}
      - name: {{ $slackReceiver }}
        slack_configs:
          - channel: '{{ printf "#%s" $v.slack_channel }}'
            send_resolved: true
            icon_emoji: '{{ "{{ template \"slack.loveholidays.iconemoji\" . }}" }}'
            title: '{{ "{{ template \"slack.loveholidays.title\" . }}" }}'
            text: '{{ "{{ template \"slack.loveholidays.text\" . }}" }}'
            username: '{{ "{{ template \"slack.loveholidays.username\" }}" }}'

    {{- if $v.pagerduty_service_key }}
      - name: {{ $pagerdutyReceiver }}
        pagerduty_configs:
          - service_key: {{ $v.pagerduty_service_key }}
            description: '{{ "{{ range .Alerts }}{{ .Annotations.summary }}\n{{ end }}" }}'
      {{- end }}
    {{- end }}

      ## Default catch all route for alerts with no matching team/namespace
      - name: slack_alertmanager
        slack_configs:
          - channel: '#alertmanager'
```

Objectively, this is far worse than having plain-text configuration, right?

Sure, Helm/Go Templating isn’t all that user friendly, but it shifts the ownership of the template to the infrastructure team and makes things much easier for the dev teams by providing them a simple interface to interact with. We are introducing an even more complex system to provide simplicity to our end users. Fighting fire with fire.

Rendering the above template + values file gives the following template:

```c
global:
  resolve_timeout: 5m
  slack_api_url: https://hooks.slack.com/services/<slack-webhook-url>
templates:
  - '/etc/alertmanager/config/*.tmpl'
route:
  group_by: [alertname]
  group_interval: 60m
  group_wait: 30s
  repeat_interval: 12h
  receiver: slack_alertmanager
  routes:
    ## PagerDuty rules for team: teamA
    - receiver: team_teamA_pagerduty
      group_wait: 10s
      group_interval: 10m
      repeat_interval: 1h
      continue: true
      matchers:
        - pagerduty="active"
        - team=~"teamA"

    ## label team route for team: teamA
    - receiver: team_teamA_slack
      matchers:
        - team=~"teamA"

    ## label namespace route for team: teamA
    - receiver: team_teamA_slack
      matchers:
        - namespace=~"teamA"
    ## PagerDuty rules for team: teamB
    - receiver: team_teamB_pagerduty
      group_wait: 10s
      group_interval: 10m
      repeat_interval: 1h
      continue: true
      matchers:
        - pagerduty="active"
        - team=~"teamB"

    ## label team route for team: teamB
    - receiver: team_teamB_slack
      matchers:
        - team=~"teamB"

    ## label namespace route for team: teamB
    - receiver: team_teamB_slack
      matchers:
        - namespace=~"teamB"

receivers:
  - name: team_teamA_slack
    slack_configs:
      - channel: '#teamA-alerts'
        send_resolved: true
        icon_emoji: '{{ template "slack.loveholidays.iconemoji" }}'
        title: '{{ template "slack.loveholidays.title" . }}'
        text: '{{ template "slack.loveholidays.text" . }}'
        username: '{{ template "slack.loveholidays.username" }}'
  - name: team_teamA_pagerduty
    pagerduty_configs:
      - service_key: <pagerduty-service-key>
        description: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
  - name: team_teamB_slack
    slack_configs:
      - channel: '#teamB-alerts'
        send_resolved: true
        icon_emoji: '{{ template "slack.loveholidays.iconemoji" }}'
        title: '{{ template "slack.loveholidays.title" . }}'
        text: '{{ template "slack.loveholidays.text" . }}'
        username: '{{ template "slack.loveholidays.username" }}'
  - name: team_teamB_pagerduty
    pagerduty_configs:
      - service_key: <pagerduty-service-key>
        description: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
  
  ## Default catch all route for alerts with no matching team/namespace
  - name: slack_alertmanager
    slack_configs:
      - channel: '#alertmanager'
```

A functionally identical template to our first example, but instead of the dev teams having to build the Routes and Receivers themselves, their exposure to this becomes 4 lines to define their team name, slack channel, namespaces and a PagerDuty key.

## Testing the template with amtool

The migration to the new configuration is big-bang, which is pretty scary given the importance of receiving PagerDuty and Slack alerts to maintain the uptime of loveholidays.

There is a tool, [amtool](https://github.com/prometheus/alertmanager?tab=readme-ov-file#amtool), packaged within the Alertmanager repo. With `amtool`, you can run `config routes test` to simulate alerts, showing which Route(s) a particular set of labels will match to.

Render your Alertmanager template (the method to do this will change depending on how you are using Helm Charts), and store it in a local file. You can then pass it to `amtool` to run tests:

```c
>amtool config routes test --config.file=alertmanager-config.yaml --tree "team=teamA"  

Matching routes:
└── default-route
    └── {team=~"teamA"}  receiver: team_teamA_slack

>amtool config routes test --config.file=alertmanager-config.yaml --tree "team=teamA" "pagerduty=active" 

Matching routes:
└── default-route
    ├── {pagerduty="active",team=~"teamA"}  receiver: team_teamA_pagerduty
    └── {team=~"teamA"}  receiver: team_teamA_slack

>amtool config routes test --config.file=alertmanager-config.yaml --tree "namespace=teamB" 

Matching routes:
└── default-route
    └── {namespace=~"teamB"}  receiver: team_teamB_slack
```

With this, we were able to confirm different sets of team labels and the Routes they would match before deploying to Production. Neat!

## Reducing our Configuration from 1700 lines to.. 6500?!

We’ve now finished the migration from our old static config to the new template-generated config, with a whole bunch of “Quality of Life” features baked in. We generate approximately 50(!) Routes per team, each with different sets of configuration and features.

Our full team interface with a single required attribute looks like:

```c
teams:
  team:
    slack_channel: ""  # Required
    namespaces: [] # Optional list of team namespaces
    pagerduty_service_key: "" # Optional PagerDuty key
    team_aliases: [] # Optional list of previous team names
    group_interval: ""  # Overrides our default setting
    group_wait: "" # Overrides our default setting
    repeat_interval: "" # Overrides our default setting
    send_resolved: ""  # Sets whether to receive resolved notifications
    mute_time_intervals: []  # Apply mute_time_intervals to your team Routes
    customRoutes: []  # For custom features not supported by our template.
    customReceivers: [] # For custom features not supported by our template.
```

The Alertmanager Config we generate looks roughly like the following:

```c
global:
  resolve_timeout: 5m
  slack_api_url: <>
mute_time_intervals: []
inhibit_rules: []

routes:
{{- range $k, $v := .Values.alertmanager.loveholidays.teams }}
  - Generate Pagerduty routes
  - Insert customRoutes
{{- end }}

{{- range $k, $v := .Values.alertmanager.loveholidays.teams }}
  - Generate Canary Alert routes
  - Generate routes for slack_channel=~".+"
  - Generate group_by routes
  - Generate group_interval routes
  - Generate alerting_policies routes
  - Generate catch-all team label route
{{- end }}

{{- range $k, $v := .Values.alertmanager.loveholidays.teams }}
  - Generate namespace routes
{{- end }}

  - catch-all pagerduty route for pagerduty alerts with no team or namespace
  - catch-all alert to route anything else to #alertmanager

receivers:
{{- range $k, $v := .Values.alertmanager.loveholidays.teams }}
  - Generate Pagerduty Receivers
  - Generate Slack Receivers
{{- end }}
```

The complete Alertmanager configuration when rendered is approximately 6500 lines currently, supporting 15 teams. Teams have full flexibility to add custom Routes and Receivers if they require functionality that we don’t support.

An example “Quality of Life” feature baked in is `team_aliases`; our cloud-infrastructure team has previously been called devops and platform-infrastructure, and alerts may still have a team label of any of our previous names too! With `team_aliases`, we can build a RegEx match e.g. `team=~"cloud-infrastructure|devops|platform-infrastructure”` to catch alerts we haven’t updated, and this also makes future team transitions much easier.

An example of why we end up creating so many Routes per team — `group_by`. By default, alerts will be grouped by `Alertname`, which generally works fine but isn’t granular enough to be efficient for some alerts. Take a generic alert provided as part of kube-prometheus-stack, [KubeJobFailed](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubejobfailed/). This alert fires when a Kubernetes Job fails:

```c
- alert: KubeJobFailed
  annotations:
    description: Job {{ $labels.namespace }}/{{ $labels.job_name }} failed to complete. Removing failed job after investigation should clear this alert.
    summary: Job failed to complete.
  expr: |
    kube_job_failed{job="kube-state-metrics"} > 0
  for: 15m
  labels:
    severity: warning
```

We want these failed job alerts to go to the responsible team, so we wrap the expression with some logic to retrieve the team label from the job:

```c
expr: |
    label_replace(
      kube_job_labels * on(job_name, namespace) group_right(label_team) (kube_job_failed{job="kube-state-metrics"}  > 0),
            "team", "$0","label_team", ".*")
```

This will route an alert to the correct team channel, but this will generate one alert per hour with all of the failed jobs grouped together. We want to receive an alert *per* failed job, as each failed job should be investigated individually.

Grouping within Alertmanager is configured by setting `group_by` e.g. `group_by: [Alertname, job_name]` on an Alertmanager route.

We attach a `group_by` label to alerts that should be grouped by a particular attribute, and generate Routes for these for each team within the Alertmanager template. Our fully customised alert for `KubeJobFailed` looks like:

```c
- alert: KubeJobFailed
  annotations:
    description: Job {{ $labels.namespace }}/{{ $labels.job_name }} failed to complete. Removing failed job after investigation should clear this alert.
    summary: Job failed to complete.
    loki_query: |
      {pod=~"{{ $labels.job_name }}-.*"}
  expr: |
    label_replace(
      kube_job_labels * on(job_name, namespace) group_right(label_team) (kube_job_failed{job="kube-state-metrics"}  > 0),
            "team", "$0","label_team", ".*")
  for: 15m
  labels:
    severity: warning
    group_by: job_name
```

and this will match the following generated Alertmanager route per team:

```c
- receiver: slack_teamA_alerts_channel
  group_by: [alertname, job_name]
  matchers:
    - team="teamA"
    - group_by="job_name"
```

We maintain a list of `group_by` attributes and generate a Route for each, so expanding this in the future is as trivial as adding a new item in a list.

Bonus points for those of you that spotted the `loki_query` annotation in our customised alert above — we dynamically insert buttons based on Alert annotations like `loki_query`, `runbook_url`, `dashboard_url` and others:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*7J-_5XeZnse4h7lBkfizNg.png)

Real KubeJobFailed Alert using our custom template

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*NBRk0CfklYXcjV68Nbi1wQ.png)

Example Alert with loki\_query, runbook\_url and dashboard\_url annotations

So by having a `loki_query` annotation on the alert, users will be able to click a button to view their logs within Grafana, timestamped to +/- 1 hour of when the alert fired. A big timesaver!

## Conclusion

Invest in Simplicity is one of [The 5 principles that helped scale loveholidays](https://tech.loveholidays.com/the-5-principles-that-helped-scale-loveholidays-7ea0b0fd3df9), and massively simplifying the Alertmanager experience for our dev teams at the cost of operational complexity for the infra team is a well-justified trade-off.

Since the migration we have had **zero** questions or alerts about misconfigurations, and our internal documentation on this makes it a fully self-serve platform. Teams have quickly adopted features like `loki_query` to make their alerting experience way more effective than before.

A tl;dr wouldn’t do this project justice, but we can summarise a few nice points:

- Teams can configure Alertmanager with a minimum of just **3** lines.
- Adding or renaming teams is now trivial.
- All teams get a whole bunch of nice Quality of Life features as part of the template.
- From our original 1700 line config, the total team configuration for Production (excluding customRoutes and customReceivers) is just **92** lines, an average of **6** lines per team and a reduction of ~ **94.59%**. If we include customRoutes and customReceivers, that number is still only **242** / an **85.76%** reduction.

Overall, this has been a very successful migration and is well worth assessing if it would be effective for your own platform and teams. We’d love to hear from you about how you are managing Alertmanager, so please do drop a comment!

Excited by org-wide challenges like this? We currently have an opportunity for a Platform Engineer — L1 in Cloud Infrastructure, and we’re hiring across multiple other teams as well. [Join us!](https://careers.loveholidays.com/#jobs)

[![loveholidays tech](https://miro.medium.com/v2/resize:fill:96:96/1*Tn8bGS0wfOJbm6wA5dhlqg.png)](https://tech.loveholidays.com/?source=post_page---post_publication_info--6901a50857ce---------------------------------------)

[![loveholidays tech](https://miro.medium.com/v2/resize:fill:128:128/1*Tn8bGS0wfOJbm6wA5dhlqg.png)](https://tech.loveholidays.com/?source=post_page---post_publication_info--6901a50857ce---------------------------------------)

[Last published Jan 6, 2026](https://tech.loveholidays.com/collaboration-patterns-for-cross-team-work-60bc4d40c4fe?source=post_page---post_publication_info--6901a50857ce---------------------------------------)

Stories in tech, product and design at loveholidays

## More from Dan Williams and loveholidays tech

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--6901a50857ce---------------------------------------)