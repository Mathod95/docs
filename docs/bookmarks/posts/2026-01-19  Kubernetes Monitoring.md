---
title: "Kubernetes Monitoring"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/cloud-native-daily/kubernetes-monitoring-d0ab5563f10f"
author:
  - "[[Lahiru Hewawasam]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)## [Cloud Native Daily](https://medium.com/cloud-native-daily?source=post_page---publication_nav-dd347d5c5a2b-d0ab5563f10f---------------------------------------)

[![Cloud Native Daily](https://miro.medium.com/v2/resize:fill:76:76/1*MoZ3voEYDtTTwoQ3azpccg.png)](https://medium.com/cloud-native-daily?source=post_page---post_publication_sidebar-dd347d5c5a2b-d0ab5563f10f---------------------------------------)

A blog for Devs and DevOps covering tips, tools, and developer stories about all things cloud-native

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*EjzR7qrxWK2EYaPq.jpg)

As developers increasingly embrace containerization and microservices architecture, the need for effective [monitoring and observability](https://medium.com/cloud-native-daily/kubernetes-monitoring-tools-584d82c94185) becomes paramount. Monitoring distributed applications and microservices presents unique challenges that traditional monitoring approaches struggle to address. Hence, it is essential to have a comprehensive understanding of modern monitoring techniques and tools like [Helios](https://gethelios.dev/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&utm_content=kubernetes+monitoring), [Grafana](https://grafana.com/) and [Prometheus](https://prometheus.io/) to tackle these challenges.

This article explores the significance of Kubernetes monitoring and why it is crucial for developers leveraging container orchestration tools like K8s. We will delve into the challenges posed by monitoring distributed applications and microservices and discuss best practices and tools for effective Kubernetes monitoring.

## Challenges in Monitoring Kubernetes

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*0vBODHr9mz6wyLrq.jpg)

Monitoring Kubernetes (K8s) is challenging due to its complex and dynamic nature. Organizations adopting Kubernetes face obstacles in effectively monitoring and maintaining cluster health and performance. [OpenTelemetry](https://gethelios.dev/blog/opentelemetry-otel-is-opening-new-possibilities-for-developers/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&utm_content=Kubernetes+monitoring) provides a solution to address these challenges.

Kubernetes environments are complex and difficult to monitor due to their scale. OpenTelemetry collects telemetry data, including metrics, traces, and logs, providing comprehensive visibility into Kubernetes deployments for effective monitoring and analysis.

Kubernetes’ dynamic nature adds complexity to monitoring efforts. OpenTelemetry’s automatic instrumentation adapts to Kubernetes’ dynamism, [tracing](https://gethelios.dev/distributed-tracing/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&utm_content=Kubernetes+monitoring) requests across microservices and collecting telemetry data in highly dynamic environments.

## The Significance of Monitoring K8s with OpenTelemetry

[Monitoring Kubernetes with OpenTelemetry](https://gethelios.dev/blog/kubernetes-monitoring-opentelemetry/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&utm_content=Kubernetes+monitoring) offers significant benefits, including faster issue detection and resolution, as well as issue mitigation.

OpenTelemetry collects telemetry data to quickly detect and diagnose issues within the Kubernetes cluster, enabling prompt identification and resolution of bottlenecks, errors, and anomalies.

Without proper monitoring, Kubernetes environments are vulnerable to performance issues and failures. Lack of monitoring makes it difficult to identify resource constraints and troubleshoot communication failures or [bottlenecks](https://dzone.com/articles/fixing-bottlenecks-in-your-microservices-app-flows).

Monitoring Kubernetes with OpenTelemetry provides end-to-end visibility by capturing telemetry data across different layers of the Kubernetes stack. This enhances understanding of the system, facilitates troubleshooting, optimization, and ensures smooth application operation.

## Monitoring Kubernetes: Recommended Best Practices

While monitoring Kubernetes depends on various factors specific to each application and organization, these are some general best practices that can help organizations maximize the effectiveness of their monitoring efforts.

1. **Comprehensive Data Collection**: Implement a robust monitoring strategy that captures a wide range of data, including metrics, traces and logs. This holistic approach provides a comprehensive view of your Kubernetes cluster’s performance, resource utilization, and application behavior.
2. **Instrumentation**: Properly instrument your applications, containers, and infrastructure components with monitoring agents or libraries. This allows for the collection of granular data and enables deep insights into the behavior of your Kubernetes ecosystem.
3. **Distributed Tracing**: Implement [distributed tracing](https://medium.com/cloud-native-daily/distributed-tracing-a-guide-for-2023-a40a1ee218b5) to gain visibility into the flow of requests and identify performance bottlenecks or issues across microservices. Distributed tracing helps trace requests as they traverse through various components and provides valuable insights into latency and dependencies.
4. **Alerting and Thresholds**: Set up proactive alerting mechanisms based on key metrics and thresholds. Define meaningful alerts to notify you of potential issues or deviations from normal behavior. Fine-tune alerting rules to reduce false positives and focus on critical events.
5. **Scalability and Performance**: Monitor the scalability and performance of your Kubernetes infrastructure by tracking metrics such as CPU and memory usage, network throughput, and response times. This helps ensure that your cluster can handle increasing workloads and provides insights for optimizing resource allocation.
6. **Visualization and Dashboards**: Utilize visualization tools and create custom dashboards to present monitoring data in a visually intuitive manner. Dashboards help you quickly assess the health and performance of your Kubernetes cluster, identify trends, and spot anomalies.

## Crucial Metrics to Monitor in Kubernetes

When monitoring Kubernetes, there are several critical metrics that you should keep a close eye on to ensure the health and optimal performance of your cluster. These key metrics provide valuable insights into different aspects of your Kubernetes environment and help you identify potential issues or bottlenecks. Here are some essential metrics to monitor in Kubernetes:

1. **CPU Utilization**: Monitor CPU usage at the Pod level to ensure efficient resource allocation and identify potential bottlenecks or resource contention.
2. **Memory Utilization**: Track memory usage within Pods to detect excessive memory consumption, potential memory leaks, or insufficient memory allocation.
3. **Network Throughput**: Monitor network throughput between Pods to identify any network congestion or performance issues impacting communication between containers.
4. **Disk I/O**: Keep an eye on disk input/output (I/O) metrics at the Pod level to identify potential disk-related bottlenecks or performance degradation.
5. **Pod Health**: Monitor the health status of individual Pods, including the number of restarts, to identify any persistent issues or failures affecting specific Pods.
6. **Node Health**: Track metrics related to the health and performance of Kubernetes nodes, such as CPU and memory utilization, to ensure the overall stability and capacity of the cluster.
7. **Etcd Metrics**: These metrics, which include disk usage, response time, and error rate, give details about the operation and condition of the etcd cluster.

## Implementing OpenTelemetry in Kubernetes

Implementing OpenTelemetry in your Kubernetes monitoring strategy can greatly enhance your observability capabilities and provide deeper insights into your application’s behavior. It will allow you to collect, instrument, and export telemetry data from your Kubernetes cluster.

To implement OpenTelemetry effectively, follow these steps:

1. Install the OpenTelemetry agent
2. Configure the OpenTelemetry agent
3. Enable OpenTelemetry instrumentation in your Kubernetes applications
4. Send data to your preferred backend

### 1\. Install the OpenTelemetry agent

To ensure the OTel agent is running on every node in your Kubernetes cluster, you can set it up as a DaemonSet. Follow these steps to install the agent:

Use the following command to install the OTel agent in your Kubernetes cluster. It will initiate the installation process of the OTel agent.

```rb
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```

### 2\. Configure the OpenTelemetry agent

To gather telemetry data from your Kubernetes cluster using the OTel collector, you need to [configure](https://opentelemetry.io/docs/k8s-operator/) it following the below steps:

1. **Create a YAML configuration file**: Generate a configuration file in YAML format that includes the desired exporters, receivers, and processors. This file will be used to define the behavior of the OTel collector.
2. **Mount the configuration file**: Mount the configuration file as a volume within the OTel agent pod. This ensures that the agent uses the specified configuration when collecting telemetry data.
3. **Specify exporters, receivers, and processors**: Within the configuration file, list the exporters, receivers, and processors that you intend to use. This determines how the telemetry data will be gathered and where it will be sent. Make sure to include the necessary details for each component.
4. **Consult the** [**OTel documentation**](https://opentelemetry.io/docs/k8s-operator/): For more detailed guidance on configuring the OTel agent, refer to the official OTel documentation. It provides comprehensive information and specific instructions to help you fine-tune the configuration based on your requirements.

Once the OTel agent is set up and the [OTel SDK](https://opentelemetry.io/docs/k8s-operator/) is incorporated into your application code, you can start sending the gathered telemetry data to your preferred backend.

OTel supports a range of backends, such as [Prometheus](https://prometheus.io/), [Jaeger](https://www.jaegertracing.io/), [Helios](https://gethelios.dev/), and [Zipkin](https://zipkin.io/), among others. These backends are compatible with OTel and provide options for storing, analyzing, and visualizing the collected telemetry data.

```rb
receivers:
  otlp:
    protocols:
      grpc:
exporters:
  prometheus:
    endpoint: "localhost:8888"
  jaeger:
    endpoint: "http://jaeger:14268/api/traces"
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: []
      exporters: [jaeger, prometheus]
```

### 3\. Enable OpenTelemetry instrumentation in your Kubernetes applications

To collect telemetry data from your Kubernetes applications, it is necessary to integrate the OTel SDK into your application code. This integration allows for instrumentation and the gathering of telemetry data. You can utilize language-specific operators provided by OTel, such as Java, Python, or.Net, to instrument your application. It’s important to note that for certain languages, [auto-instrumentation](https://docs.gethelios.dev/docs/deploying-the-helios-sdk-in-a-kubernetes-k8s-cluster?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&utm_content=Kubernetes+monitoring) can also be enabled, simplifying the process of instrumenting your application.

### 4\. Using OpenTelemetry to Monitor Kubernetes

Once you have successfully completed the setup of the OTel agent and integrated the OTel SDK into your application code, the next step is to transmit the collected telemetry data to your preferred backend. OpenTelemetry provides support for various backends, including popular options such as Prometheus, Jaeger, and Zipkin, among others. This flexibility allows you to choose the backend that best suits your monitoring and analysis requirements.

The [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator) simplifies the process of deploying OpenTelemetry in a Kubernetes environment. It offers a streamlined approach to deploying and managing OpenTelemetry components, allowing you to effortlessly deploy and manage the OTel collector within your Kubernetes cluster.

In addition, OpenTelemetry Operator is responsible for gathering the telemetry data from your Kubernetes applications and exporting it to your chosen backend. Whether you opt for a deployment or a daemon set, the OpenTelemetry Operator ensures a smooth and efficient setup process for the OTel collector, enabling seamless telemetry data collection and analysis in your Kubernetes environment.

***Learn more:***## [OpenTelemetry: A full guide](https://gethelios.dev/opentelemetry-a-full-guide/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

Learn all about OpenTelemetry OpenSource and how it transforms microservices observability and troubleshooting

gethelios.dev

[View original](https://gethelios.dev/opentelemetry-a-full-guide/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

## Tools to Use to Monitor K8s

OpenTelemetry serves as a powerful tool for monitoring Kubernetes, providing valuable insights into the performance and behavior of your Kubernetes applications. However, several additional tools can be employed alongside OpenTelemetry to further enhance its benefits and optimize Kubernetes monitoring.

Consider the following selection of commonly utilized tools for monitoring Kubernetes environments:

1. [Helios](https://gethelios.dev/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&utm_content=Kubernetes+monitoring)
2. [Prometheus](https://prometheus.io/)
3. [Grafana](https://grafana.com/)
4. [Jaeger](https://www.jaegertracing.io/)

### Monitoring Kubernetes with Helios

[Helios](https://gethelios.dev/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&utm_content=Kubernetes+monitoring) is a powerful development platform specifically explicitly for observability and monitoring purposes, making it an ideal choice for monitoring Kubernetes environments. One of its notable advantages is its seamless integration with OpenTelemetry, allowing for smooth data collection and analysis. What sets Helios apart from other tools is its unique set of features that include critical elements not found in other solutions.

Helios offers real-time visibility into your Kubernetes cluster, enabling you to monitor its performance and health in real-time. It also provides rich visualizations that enhance your understanding of the monitored data. Helios goes beyond Kubernetes monitoring by offering comprehensive monitoring capabilities for the underlying infrastructure and applications running on the Kubernetes platform. This holistic approach makes Helios a comprehensive and versatile [monitoring tool](https://medium.com/cloud-native-daily/kubernetes-monitoring-tools-584d82c94185) specifically designed for Kubernetes environments.

***Check out the official Helios documentation for more details:***## [☸️ Deploying the Helios OpenTelemetry SDK in a Kubernetes (K8s) cluster](https://docs.gethelios.dev/docs/deploying-the-helios-sdk-in-a-kubernetes-k8s-cluster?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

Follow the instructions below to install and update the Helios OpenTelemetry SDK in a centralized manner when running…

docs.gethelios.dev

[View original](https://docs.gethelios.dev/docs/deploying-the-helios-sdk-in-a-kubernetes-k8s-cluster?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

### Monitoring Kubernetes with Prometheus

[Prometheus](https://prometheus.io/) stands out as a highly popular monitoring tool extensively utilized in Kubernetes environments. It simplifies the monitoring and troubleshooting process for your Kubernetes cluster by providing a powerful query language and a wide range of visualization options.

Take a look at the following configuration example, which demonstrates how to deploy Prometheus in your Kubernetes cluster:

```rb
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
spec:
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      app: sample-app
  resources:
    requests:
      memory: 400Mi
  ruleSelector:
    matchLabels:
      prometheus: k8s
  alerting:
    alertmanagers:
    - static_configs:
      - targets:
        - alertmanager:9093
```

### Monitoring Kubernetes with Grafana

[Grafana](https://grafana.com/) is a widely adopted visualization tool, that seamlessly integrates with Prometheus. With Grafana, you gain access to a diverse range of visualization options and create customized dashboards that provide comprehensive insights into the performance and operation of your Kubernetes cluster.

```rb
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
  labels:
    app: grafana
spec:
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
  selector:
    app: grafana
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        volumeMounts:
        - name: grafana-data
          mountPath: /var/lib/grafana
      volumes:
      - name: grafana-data
        persistentVolumeClaim:
          claimName: grafana-data
```

### Monitoring Kubernetes with Jaeger

[Jaeger](https://www.jaegertracing.io/) is an open-source tracing tool, that shares similarities with OTel in terms of its [distributed tracing](https://gethelios.dev/blog/opentelemetry-dotnet-distributed-tracing/) capabilities. With Jaeger, you can effectively trace the flow of requests across your Kubernetes cluster, gaining valuable insights into the interactions between services. It provides a range of visualization options that simplify the understanding of request flows and supports multiple tracing formats, including OTel.

```rb
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: simple-prod
spec:
  strategy: allInOne
  allInOne:
    image: jaegertracing/all-in-one:latest
    options:
      log-level: debug
```

### Conclusion

In summary, monitoring your Kubernetes environment is paramount to guarantee your applications’ optimal performance, reliability, and availability. OpenTelemetry serves as a powerful framework for monitoring Kubernetes, offering comprehensive capabilities through distributed tracing, metrics, and logging.

By adhering to best practices and leveraging appropriate tools like OpenTelemetry and Helios, you can significantly enhance the performance of your applications. Real-time visibility into your Kubernetes clusters enables you to proactively identify and address potential issues, ensuring smooth operations.

As Kubernetes continues to gain popularity, a robust monitoring strategy becomes increasingly vital. By implementing OpenTelemetry and other monitoring tools, you can mitigate potential problems and maintain the seamless functioning of your Kubernetes environment.

### Further Reading:## [OpenTelemetry Tracing: Everything you need to know](https://gethelios.dev/blog/opentelemetry-tracing/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

OpenTelemetry tracing is filling the gaps of traditional observability methods in microservices apps. Here's how it's…

gethelios.dev

[View original](https://gethelios.dev/blog/opentelemetry-tracing/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)## [Serverless observability, monitoring, and debugging explained](https://gethelios.dev/blog/serverless-observability/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

Serverless troubleshooting requires E2E observability, through collecting trace data on top of logs and metrics- Here's…

gethelios.dev

[View original](https://gethelios.dev/blog/serverless-observability/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)## [OpenTelemetry: A full guide](https://gethelios.dev/opentelemetry-a-full-guide/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

Learn all about OpenTelemetry OpenSource and how it transforms microservices observability and troubleshooting

gethelios.dev

[View original](https://gethelios.dev/opentelemetry-a-full-guide/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)## [Kubernetes Monitoring with OpenTelemetry](https://gethelios.dev/blog/kubernetes-monitoring-opentelemetry/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

Learn how to monitor Kubernetes using OpenTelemetry with real-time visibility and granular error data - Reduce MTTR by…

gethelios.dev

[View original](https://gethelios.dev/blog/kubernetes-monitoring-opentelemetry/?utm_source=medium&utm_medium=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)## [Combining OTel and Prometheus metrics for alerting machine](https://gethelios.dev/blog/combinining-opentelemetry-traces-with-prometheus-metrics-to-build-a-powerful-alerting-mechanism/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

Using both OpenTelemetry and Prometheus, we delivered a trace-based alerting mechanism quickly and efficiently - here's…

gethelios.dev

[View original](https://gethelios.dev/blog/combinining-opentelemetry-traces-with-prometheus-metrics-to-build-a-powerful-alerting-mechanism/?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)## [Microservices Monitoring: Cutting Engineering Costs and Saving Time](https://gethelios.dev/blog/cut-engineering-costs-save-time-helios?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

A few ways fort leveraging Helios to save on engineering costs and dev time for a more resource-efficient organization…

gethelios.dev

[View original](https://gethelios.dev/blog/cut-engineering-costs-save-time-helios?utm_source=medium&utm_medium=referral&utm_campaign=cloud+native+daily&source=post_page-----d0ab5563f10f---------------------------------------)

[![Cloud Native Daily](https://miro.medium.com/v2/resize:fill:96:96/1*MoZ3voEYDtTTwoQ3azpccg.png)](https://medium.com/cloud-native-daily?source=post_page---post_publication_info--d0ab5563f10f---------------------------------------)

[![Cloud Native Daily](https://miro.medium.com/v2/resize:fill:128:128/1*MoZ3voEYDtTTwoQ3azpccg.png)](https://medium.com/cloud-native-daily?source=post_page---post_publication_info--d0ab5563f10f---------------------------------------)

[Last published Apr 4, 2025](https://medium.com/cloud-native-daily/serverless-video-transcoding-on-aws-using-lambda-mediaconvert-and-cloudfront-b4103ec16d49?source=post_page---post_publication_info--d0ab5563f10f---------------------------------------)

A blog for Devs and DevOps covering tips, tools, and developer stories about all things cloud-native

Cybersecurity Specialist | For more details find me on LinkedIn [https://www.linkedin.com/in/lahiru962/](https://www.linkedin.com/in/lahiru962/)

## More from Lahiru Hewawasam and Cloud Native Daily

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d0ab5563f10f---------------------------------------)