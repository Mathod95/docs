---
title: "The Observability Stack Part2"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@aryalireza/the-observability-stack-part2-857fd883cc3d"
author:
  - "[[Alireza Yavari]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*BSKipkFd1Y3Uhm2qAjV5fw.jpeg)

An AI-Generated Image

In the previous part of “ [The Observability Stack Part 1](https://medium.com/@aryalireza/the-observability-stack-part1-17929769c0df) ”, we talked about how to build a data flow with multiple tools for gathering, sending to an observability backend, and visualizing logs on Grafana.

In this part, I want to discuss Metrics and their data flow.

Observability data is crucial for new tools and microservices, and metrics play a vital role in this regard. They enable us to track and analyze the performance of our ecosystem and identify any issues that may arise. For instance, when working with a K8S cluster, it is important to monitor the activity of various K8S objects such as namespaces, statefulsets, deployments, and pvcs. By doing so, we can gain valuable insights into our system's behavior and pinpoint areas that require attention.  
Or a Spring Boot application with Actuator metrics?

The traditional way like script monitoring is obsoleted and it’s out of a DevOps mindset league.

Many infrastructure and operating system monitoring tools, such as Zabbix, are not the ideal way to manage metrics. While these systems may have added metric management features, they are not natively and naturally supported. As a result, this could be problematic for managing large-scale metrics.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5lR1lQbdiesQTlA4U_9g5w.jpeg)

AI-Generated image of Prometheus

> When we talk about metrics, usually people think about Prometheus!  
> But my mean is a standard of metrics, the open-metric standard.  
> This is an active project on CNCF that is developed by Prometheus itself.  
> Prometheus has been the default for cloud-native observability since 2015.

For some small environments, Prometheus may be a suitable choice, but for my specific case, I require a centralized system for gathering metrics, a well-defined separation of data access with multi-tenancy support, a highly available backend for storing metrics, and a single telemetry shipper for multiple environments.

I am familiar with Grafana Loki and its components, which is why I prefer working with Grafana Mimir.  
The deployment methods for both are very similar, including the **distributed** deployment mode we discussed earlier, its components, and the storage backend. All the necessary infrastructure is available because of Loki’s requirements, such as the K8S and Minio cluster. So, why should I opt for any other metric backend when everything I need is already available?

![](https://miro.medium.com/v2/resize:fit:640/1*eVtjIqNfkvMTKSqz-ePLFA.jpeg)

An AI-Generated image

> According to Grafana documents:  
> Mimir lets you scale metrics to 1 billion active series and beyond, with high availability, multi-tenancy, durable storage, and blazing-fast query performance over long periods of time.  
> Mimir was started at Grafana Labs and [announced in 2022](https://grafana.com/blog/2022/03/30/announcing-grafana-mimir/). The mission for the project is to make it the most scalable, most performant open source time series database for metrics, by incorporating what Grafana Labs engineers have learned running Grafana Enterprise Metrics and Grafana Cloud Metrics at a massive scale. Mimir is released under the AGPLv3 license.

For the first step, I deployed Mimir HelmChart in distributed mode on K8S and used Minio for the s3 storage backend.

Since I used Fluent-bit for logging, I used it again for metrics.  
Here is my complete Fluent-bit data pipeline for collecting logs and metrics, and sending them to different destinations:

```c
service:
  log_level: info
  log_file: /opt/fluent-bit/fluent-bit.log
  parsers_file: /etc/fluent-bit/parsers.conf
  http_server: on
  http_listen: 0.0.0.0
  http_port: 2021
  flush: 1
  Health_Check: On
pipeline:
  inputs:
    - name: "forward"
      listen: 0.0.0.0
      port: 24224
      buffer_chunk_size: "100M"
      buffer_max_size: "200M"
      tag: "logs_tag"

    - name: "prometheus_scrape"
      host: "host_ip"
      port: "endpoint_port"
      metrics_path: /path/to/metrics/endpoint
      tag: "metrics_tag"
      scrape_interval: 10s
     
  outputs:
    - name: "kafka"
      match: "log_tag"
      brokers: kafka_broker1:9092,kafka_broker2:9092,kafka_broker3:9092
      topics: "Your_Kafka_Topic"

    - name: "prometheus_remote_write"
      match: "metrics_tag"
      host: "destinations_ip"
      port: "destinations_port"
      uri: "/api/v1/push" #Mimir Remote Write Address.
      log_response_payload: true
      add_label: a_label mylabel
      header: X-Scope-OrgID mytenant
```

With this Flunet-bit’s configurations, I used the “prometheus\_remote\_write” output plugin for sending scraped metrics via the “prometheus\_scrape” input plugin to my destination which is Grafana Mimir.

By default Mimir is supported and enabled the multi-tenancy feature, just need to send the “ **X-Scope-OrgID** ” header with your **remote\_write** configuration.

Now we can configure our data source in Grafana.  
Add a new **Prometheus** data source with Mimir’s Nginx gateway address.  
Add your HTTP header, “ **X-Scope-OrgID** ” as the header and the value you set in the Fluent-bit.  
Save and go to the Explore section.

By following this data flow, you will be able to view the label that you set in the Fluent-bit on the Explore page of Grafana. With the multi-tenancy feature, you no longer need to worry about the performance impact of a simple query or about the privacy of your company's observability data for your teams.

You can use any other metric scarper tools that support the remote\_write protocol.

> One big issue would be the **Cardinality** and i suggest everyone who wants to work with the labeling system, should know about it.

Happy observability!

A Devops Engineer that enthusiastic to IT world

## More from Alireza Yavari

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--857fd883cc3d---------------------------------------)