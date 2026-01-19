---
title: "The Observability Stack Part1"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@aryalireza/the-observability-stack-part1-17929769c0df"
author:
  - "[[Alireza Yavari]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*93dy6NNdFUq_LQL6Cc2D9g.jpeg)

An AI-Generated Image

In the DevOps world when we talk about observability, we mean to generate, collect, and gather, perform some manipulation on it, centralize it somewhere, make it queriable, and visualize.

You should do many things to make these stacks work fine, handle many challenges, so much R & D, and solve these problems especially when you have a big enterprise environment.

This is the beauty of DevOps is that we can integrate separate elements.

### So let’s dive into technical situations

In this article, I’ll try to explain my observability stack in several steps.

The mission is to collect observability data containing **Logs**, **Metrics,** and **Traces**.  
In My situation this collection, aggregation, centralizing, and visualizing required an enterprise environment because the throughput is on a high level.

> So what do I mean by the Enterprise Environment?  
> Including infrastructure, high-end and high-throughput tools, integration of these tools with each other, and of course the capability of using this environment!

![The Enterprise Environment Of Poseidon Stack](https://miro.medium.com/v2/resize:fit:640/format:webp/1*A0G0iMHN2xfM0abtADDecQ.jpeg)

The Enterprise Environment

According to this diagram, I have multiple tools to manage this stack.  
These observability pieces should be sent via a Log Shipper in a message queue for multiple use cases.  
The first use case is because we are sending too much data, with a message queue like Kafka, we can have a backpressure mechanism to avoid overwhelming our destinations.  
The second user case is when we have multiple destinations, for example for Data Engineering or other purposes, one for Grafana Loki, one for ElasticSearch, and another for MongoDB. When we have data on a topic, we can consume them to these destinations.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*G_gFExVdsBwKiZ9p4UKCcA.jpeg)

On the other side, we have to consume this data. I used Promtail as a Kafka consumer and configured it to send to Loki.

In a K8S cluster, I deployed the LGTM stack (Loki, Grafana, Tempo, Mimir) via Helm chart to manage logs, metrics, and distributed trace workflow including fetch, label, making these queryable, and storing on storage.

The LGTM stack can be deployed in multiple ways.  
stand-alone, simple scaleable, and distributed(Microservice) mode.

The recommendation of Grafana for hight-load is distributed-mode.  
The distributed mode of the LGTM stack required S3-compatible object storage for this deployment.  
Because of this, I implemented a Minio cluster for this environment.

> Based on my experience, the Object-Store is important for this stack, you should have some well-tuned configurations and setup for your object-storage, like high-speed disks, xfs-like file system, and the best configurations according to your environment.  
> If you can use a cloud provider S3, like AWS, just use it.

Some of the microservices in the LGTM stack need a cache server so I deployed an independent Redis Sentinel Cluster for them.

![](https://miro.medium.com/v2/resize:fit:640/1*5dlWq6zuCs1EvxCJ-rehQQ.png)

The first one is Logs, which was a real challenge!  
Consider an environment with 2000 or more microservices that we want to centralize their logs and each microservice has its logging system, log levels, and patterns!  
In any case, we have to unify these logs.  
One way using regex to make something with them.  
Another way is making the logs structured to process all of them, something like JSON format.  
So we decided to change every microservice we have, to generate only JSON format logs with only some small changes.

For example in java/spring-boot applications that use sle4j and logback.xml files for their log framework, we can use our format and encodings.

With this change, we are not to deal with multi-line logs that is a real headache!

It’s a trade-off between dealing with multi-line logs like Java stack traces, unifying the logging layer, and some application changes. It’s up to the situation.

![](https://miro.medium.com/v2/resize:fit:640/1*AbuS5UNh29b7qbh5diEqgA.png)

Deploying Loki  
I don't want to explain why I choose Grafana Loki as a Log Management system, because many documentation and benchmarks are available over the internet.  
But I will explain how I installed Loki.  
Based on the official document, the best way to handle production environments and high volumes of data is by using **distributed mode** on a K8S, which can be deployed in multiple ways. However, the most efficient deployment method is through Helm Chart.  
In this mode, Loki’s microservices will installed on a K8S cluster and will be ready for log management!

Each microservice is responsible for specific actions, allowing us to scale the specific components in different scenarios, for example, high traffic.

Configurations will vary based on the use case, including log format, amount, and retention.  
Here are some important configurations I want to point out. They concerned me, so it would be helpful to share.

In Loki, we should know every component, how it’s working, and which tuning is suitable for our environment.

The most important configuration is about how Loki saves events in a Datastore.  
There are multiple ways to handle this, but recently Loki introduced **Single Store** and **tsdb** which is now the recommended way.  
Loki needs an object store I used the Minio and the configuration section would be like this:

```c
schemaConfig:
    configs:
    - from: "2023-11-25"
      store: tsdb
      object_store: aws
      schema: v12
      index:
        prefix: tsdb_index_
        period: 24h
  storageConfig:
    boltdb_shipper:
      shared_store: aws
      active_index_directory: /var/loki/boltdb-shipper-active
      cache_location: /var/loki/boltdb-shipper-cache
      cache_ttl: 24h
    tsdb_shipper:
      active_index_directory: /var/loki/tsdb-index
      cache_location: /var/loki/tsdb-cache
      index_gateway_client:
        server_address: "loki-distributed-index-gateway.loki.svc.cluster.local:9095"
      query_ready_num_days: 7
      shared_store: aws
    aws:
      s3: http://username:password@ip:port/your_bucket
      s3forcepathstyle: true
```

One of the important components is the Querier responsible for accepting log queries from end-users and fetching that data.  
For example, we can scale and configure just this component or the others.  
So for performance improvement, in my experience, the most important component that we should tune, is Querier.

One of the good features of Loki is Multi-tenancy.  
This feature allows us to separate our data for multiple use cases.

In an environment with Multi-tenancy enabled in Loki and you as an Admin need to access over of data, the line of the below configuration is mandatory:

```c
querier:
    multi_tenant_queries_enabled: true
```

With this configuration, you can query logs with multiple tenant names like:

```c
tenantName1 | tenantName2
```

For removing old logs data, Loki has a component named **Compactor.  
**With this component configuration, we can control our retention**.  
**For example:

```c
limits_config:
  retention_period: 24h
compactor:
  shared_store: your_store_name
  working_directory: /var/loki/retention
```

We should collect logs with a log collector (log shipper) with features like low resource footprints, compatibility with multiple environments, ease of use, and a good community.  
After some R&D I found the ***fluent-bit*** and ***Vector*** is a good choice.

Vector is written by Rust and fluent-bit by C.

Both of them have a low resource footprint. But I chose fluent-bit because of its ready-to-use parsers, active community, and of course it’s a CNCF graduated project.

![](https://miro.medium.com/v2/resize:fit:640/1*D8wyv0aSvO39n3g53CSR4w.png)

Fluentbit

we can deploy fluent-bit everywhere including k8s clusters, containers, linux, and Windows.

The example below is a fluent-bit configuration that I installed on a Ubuntu Linux server:

```c
service:
  log_level: debug
  log_file: /opt/fluent-bit/fluent-bit.log
  parsers_file: /etc/fluent-bit/parsers.conf
  http_server: on
  http_listen: 0.0.0.0
  http_port: 2021
  flush: 1
  Health_Check: On
pipeline:
  inputs:
    - name: "tail"
      path: "/var/lib/docker/containers/*/*.log"
      parser: "json"
      docker_mode: "true"
      Skip_Empty_Lines: "true"
      tag: "my.logs"
  filters:
    - name: "record_modifier"
      match: "my.logs"
      record: application_name microserivce_a10
      record: tenant_name instrucation_team
      record: custom_record custom_value
    - name: "parser"
      Match: "my.logs"
      Key_Name: "log"
      Parser: "json"
      Preserve_Key: "Off"
      Reserve_Data: "On"
  outputs:
    - name: "kafka"
      match: "*"
      brokers: kafka1-broker-ip:9092,kafka2-broker-ip:9092,kafka3-broker-ip:9092
      topics: "Your_Topic_Name"
```

In the example above I configured fluent-bit to use a pipeline that includes three sections:  
**Input:** the **tail** plugin to read our container log path.  
**Filters:** using **record\_modifier** to add some records to every event.**Outputs:** sendall events that are collected to Apache Kafka with the **Kafka** output plugin.

This input pipeline can collect every log that persists on var lib containers, and we can’t easily control container metadata, especially when we have multiple containers running.

Another useful input plugin is **forward** which listens on a specific port on the host and waits for accepting log event.

Now we configure the docker log driver in deamon.json or a docker compose file.

It is more efficient than the **tail** plugin for this case.

The fluent-bit **forward** input config:

```c
pipeline:
  inputs:
    - name: "forward"
      listen: 0.0.0.0
      port: 24224
      buffer_chunk_size: "Custom_size"
      buffer_max_size: "Custom_size"
      tag: "my.logs"
```

The docker-compose file with fluent log driver:

```c
version: '3.3'
services:
  example-service:
    container_name: example-container-name
    image: exmaple-image
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        max-file: custom-number
        max-size: custom-size
        tag: my.logs
```

Now we have some log events manipulated and shaped in our **Kafka topics.**

All we need to do is consume them in our log manager, here I use **Promtail.**

Promtail is a log shipper for Loki, reads logs, and sends them to Loki with a specific Label.

here is my Promtail configuration section that consumes logs from Kafka Topics.

```c
scrapeConfigs:
      - job_name: kafka_job_name
        kafka:
          brokers:
            - broker1:9092
            - broker2:9092
            - broker3:9092
          topics:
            - "Specefic_Topic"
          use_incoming_timestamp: true
          labels:
            team: a_label
        pipeline_stages:
          - json:
              expressions:
                filed01: filed01
                filed02: filed02
                filed03: filed03
          - labels:
              filed01:
              filed02:
          - tenant:
              source: filed03
```

In the above configuration section, I described a job kind of Kafka with broker's addresses and the specific topic.  
Also, I want to extract JSON fields from logs and use them as labels in Loki, and one of the fields as Tenant.

> Understanding tenants and multi-tenancy can be complex and outside the scope of our subject.  
> But we should know that in Grafana Loki we can enable multi-tenancy if needed, and when it is enabled, Loki won't accept any event until they have an HTTP header that contains the specific tenant name.  
> For more information look at the official documents of Loki.

Now with this echo system, every event of logs generated by our applications will be sent or forwarded by fluent-bit to Kafka topics, and Promtail will get these streams and insert them into Loki. after some process between Loki’s microservices, Loki will store these data in the Minio.  
You can see these data in the **Minio dashboard** or using **mcli** withthe specific bucket and path.

As I said earlier, I deployed a cluster of Redis.  
The Redis here is responsible for multiple caching levels of Loki.  
In different levels in Loki’s configuration, Redis can be configured  
You can also see these data on Redis with “redis-cli” to ensure that Loki is using Redis.

![](https://miro.medium.com/v2/resize:fit:640/1*8ED4uBQZJRnjCFgK0YCWyw.png)

**Visualize & Query via Grafana**

To see what you gathered, you should use Grafana.

You can use any kind of deployment of Grafana, but I used a Grafana helm chart on K8S which can be easily scaled.

After installation and configuration, you must see it on your browser.

The first thing to do is add the Loki Datasource.

In Loki’s data source section, you should enter 3 important things.

**Name**, **URL,** and **HTTP headers**.

Choose a custom name for your data source.

For the Loki address, because we deployed Loki in distributed mode, you should enter Loki’s Gateway.

And because we enabled Multi-tenancy in Loki, we need to enter that tenant name on the HTTP headers section like this:

**Header**: X-Scope-OrgID

**Value**: tenant name

And now save the Datasource.

By these configurations, your data source can query Loki and can only access the specified tenant.

You can see your log data from the Explore menu choose your data source and select labels.

If you see your labels, then everything works fine.

This part of my topic is finished, I will publish the next part in the future.

Happy observability!

A Devops Engineer that enthusiastic to IT world

## More from Alireza Yavari

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--17929769c0df---------------------------------------)