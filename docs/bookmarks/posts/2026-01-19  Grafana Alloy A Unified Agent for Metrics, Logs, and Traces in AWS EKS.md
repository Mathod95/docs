---
title: "Grafana Alloy: A Unified Agent for Metrics, Logs, and Traces in AWS EKS"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.obsium.io/grafana-alloy-a-unified-agent-for-metrics-logs-and-traces-in-aws-eks-c0ab2492f774"
author:
  - "[[Bibin Kuruvilla]]"
---
<!-- more -->

[Sitemap](https://blog.obsium.io/sitemap/sitemap.xml)

While enhancing an existing observability solution for a customer, the Grafana Agent was a requirement. However, since the Agent is reaching its end of life and Grafana introduced Alloy, I thought I would give it a try.

Things were not easy, as it’s a new tool and there aren’t many online articles or resources available except for the Grafana documentation, which always takes time to figure out. Even ChatGPT was out of ideas!

To begin with, I like the name ‘Alloy.’ Perhaps they chose this name because it reflects the concept of blending various elements to create something stronger and more versatile. Alloy offers native pipelines for ==OTel==, Prometheus, Loki, and many other metrics, logs, traces, and profiling tools.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*gqK8m86KvIBfScndrlAMWA.jpeg)

### Objective of this hands-on: To replace OpenTelemetry, Promtail, and the Prometheus agent in the existing cluster with Grafana Alloy

This post assumes you already have the following tools installed in your observability cluster in AWS EKS:

If you need assistance setting up these tools, feel free to check out my previous post [here](https://medium.com/@bibinkuruvilla/comprehensive-guide-in-setting-up-the-three-pillars-of-observability-in-kubernetes-cluster-within-4a7e01d3dec)

- Grafana
- Grafana Mimir
- Grafana Loki
- Grafana Tempo
- Promtail
- Prometheus

**Configure alloy for Metrics**

The trick is to convert the existing prometheus config to the alloy format. We will first get the config values from Prometheus config map and convert it using the alloy [convert command](https://grafana.com/docs/alloy/latest/reference/cli/convert/)

```c
kubectl -n prometheus get cm prometheus-server -o jsonpath='{.data.prometheus\.yml}' > prometheus.config
alloy convert --source-format=prometheus --output=alloy_prometheus.config prometheus.config
```

Conversion is not 100% guaranteed and is done on a best-effort basis, so you are likely to see errors at this point. Read the errors, modify the input file, and try again. A little patience is required.

After conversion you will generate an alloy values file with the converted values under the config map section. You may trim the config values or add sections as per your requirement.

*Note: As prometheus is already configured to send to mimir, you can see the mimir remote write endpoint in config*

```c
alloy:
  configMap:
    content: |-
      logging {
        level  = "info"
        format = "logfmt"
      }

      discovery.kubernetes "kubernetes_apiservers" {
              role = "endpoints"
      }

      discovery.kubernetes "kubernetes_nodes" {
              role = "node"
      }

      discovery.kubernetes "kubernetes_nodes_cadvisor" {
              role = "node"
      }

      discovery.kubernetes "kubernetes_service_endpoints" {
              role = "endpoints"
      }

      discovery.kubernetes "kubernetes_service_endpoints_slow" {
              role = "endpoints"
      }

      discovery.kubernetes "prometheus_pushgateway" {
              role = "service"
      }

      discovery.kubernetes "kubernetes_services" {
              role = "service"
      }

      discovery.kubernetes "kubernetes_pods" {
              role = "pod"
      }

      discovery.kubernetes "kubernetes_pods_slow" {
              role = "pod"
      }

      discovery.relabel "kubernetes_apiservers" {
              targets = discovery.kubernetes.kubernetes_apiservers.targets

              rule {
                      source_labels = ["__meta_kubernetes_namespace", "__meta_kubernetes_service_name", "__meta_kubernetes_endpoint_port_name"]
                      regex         = "default;kubernetes;https"
                      action        = "keep"
              }
      }

      discovery.relabel "kubernetes_nodes" {
              targets = discovery.kubernetes.kubernetes_nodes.targets

              rule {
                      regex  = "__meta_kubernetes_node_label_(.+)"
                      action = "labelmap"
              }

              rule {
                      target_label = "__address__"
                      replacement  = "kubernetes.default.svc:443"
              }

              rule {
                      source_labels = ["__meta_kubernetes_node_name"]
                      regex         = "(.+)"
                      target_label  = "__metrics_path__"
                      replacement   = "/api/v1/nodes/$1/proxy/metrics"
              }
      }

      discovery.relabel "kubernetes_nodes_cadvisor" {
              targets = discovery.kubernetes.kubernetes_nodes_cadvisor.targets

              rule {
                      regex  = "__meta_kubernetes_node_label_(.+)"
                      action = "labelmap"
              }

              rule {
                      target_label = "__address__"
                      replacement  = "kubernetes.default.svc:443"
              }

              rule {
                      source_labels = ["__meta_kubernetes_node_name"]
                      regex         = "(.+)"
                      target_label  = "__metrics_path__"
                      replacement   = "/api/v1/nodes/$1/proxy/metrics/cadvisor"
              }
      }

      discovery.relabel "kubernetes_service_endpoints" {
              targets = discovery.kubernetes.kubernetes_service_endpoints.targets

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_scrape"]
                      regex         = "true"
                      action        = "keep"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_scrape_slow"]
                      regex         = "true"
                      action        = "drop"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_scheme"]
                      regex         = "(https?)"
                      target_label  = "__scheme__"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_path"]
                      regex         = "(.+)"
                      target_label  = "__metrics_path__"
              }

              rule {
                      source_labels = ["__address__", "__meta_kubernetes_service_annotation_prometheus_io_port"]
                      regex         = "(.+?)(?::\\d+)?;(\\d+)"
                      target_label  = "__address__"
                      replacement   = "$1:$2"
              }

              rule {
                      regex       = "__meta_kubernetes_service_annotation_prometheus_io_param_(.+)"
                      replacement = "__param_$1"
                      action      = "labelmap"
              }

              rule {
                      regex  = "__meta_kubernetes_service_label_(.+)"
                      action = "labelmap"
              }

              rule {
                      source_labels = ["__meta_kubernetes_namespace"]
                      target_label  = "namespace"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_name"]
                      target_label  = "service"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_node_name"]
                      target_label  = "node"
              }
      }

      discovery.relabel "kubernetes_service_endpoints_slow" {
              targets = discovery.kubernetes.kubernetes_service_endpoints_slow.targets

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_scrape_slow"]
                      regex         = "true"
                      action        = "keep"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_scheme"]
                      regex         = "(https?)"
                      target_label  = "__scheme__"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_path"]
                      regex         = "(.+)"
                      target_label  = "__metrics_path__"
              }

              rule {
                      source_labels = ["__address__", "__meta_kubernetes_service_annotation_prometheus_io_port"]
                      regex         = "(.+?)(?::\\d+)?;(\\d+)"
                      target_label  = "__address__"
                      replacement   = "$1:$2"
              }

              rule {
                      regex       = "__meta_kubernetes_service_annotation_prometheus_io_param_(.+)"
                      replacement = "__param_$1"
                      action      = "labelmap"
              }

              rule {
                      regex  = "__meta_kubernetes_service_label_(.+)"
                      action = "labelmap"
              }

              rule {
                      source_labels = ["__meta_kubernetes_namespace"]
                      target_label  = "namespace"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_name"]
                      target_label  = "service"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_node_name"]
                      target_label  = "node"
              }
      }

      discovery.relabel "prometheus_pushgateway" {
              targets = discovery.kubernetes.prometheus_pushgateway.targets

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_probe"]
                      regex         = "pushgateway"
                      action        = "keep"
              }
      }

      discovery.relabel "kubernetes_services" {
              targets = discovery.kubernetes.kubernetes_services.targets

              rule {
                      source_labels = ["__meta_kubernetes_service_annotation_prometheus_io_probe"]
                      regex         = "true"
                      action        = "keep"
              }

              rule {
                      source_labels = ["__address__"]
                      target_label  = "__param_target"
              }

              rule {
                      target_label = "__address__"
                      replacement  = "blackbox"
              }

              rule {
                      source_labels = ["__param_target"]
                      target_label  = "instance"
              }

              rule {
                      regex  = "__meta_kubernetes_service_label_(.+)"
                      action = "labelmap"
              }

              rule {
                      source_labels = ["__meta_kubernetes_namespace"]
                      target_label  = "namespace"
              }

              rule {
                      source_labels = ["__meta_kubernetes_service_name"]
                      target_label  = "service"
              }
      }

      discovery.relabel "kubernetes_pods" {
              targets = discovery.kubernetes.kubernetes_pods.targets

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"]
                      regex         = "true"
                      action        = "keep"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_scrape_slow"]
                      regex         = "true"
                      action        = "drop"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_scheme"]
                      regex         = "(https?)"
                      target_label  = "__scheme__"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_path"]
                      regex         = "(.+)"
                      target_label  = "__metrics_path__"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_port", "__meta_kubernetes_pod_ip"]
                      regex         = "(\\d+);(([A-Fa-f0-9]{1,4}::?){1,7}[A-Fa-f0-9]{1,4})"
                      target_label  = "__address__"
                      replacement   = "[$2]:$1"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_port", "__meta_kubernetes_pod_ip"]
                      regex         = "(\\d+);((([0-9]+?)(\\.|$)){4})"
                      target_label  = "__address__"
                      replacement   = "$2:$1"
              }

              rule {
                      regex       = "__meta_kubernetes_pod_annotation_prometheus_io_param_(.+)"
                      replacement = "__param_$1"
                      action      = "labelmap"
              }

              rule {
                      regex  = "__meta_kubernetes_pod_label_(.+)"
                      action = "labelmap"
              }

              rule {
                      source_labels = ["__meta_kubernetes_namespace"]
                      target_label  = "namespace"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_name"]
                      target_label  = "pod"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_phase"]
                      regex         = "Pending|Succeeded|Failed|Completed"
                      action        = "drop"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_node_name"]
                      target_label  = "node"
              }
      }

      discovery.relabel "kubernetes_pods_slow" {
              targets = discovery.kubernetes.kubernetes_pods_slow.targets

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_scrape_slow"]
                      regex         = "true"
                      action        = "keep"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_scheme"]
                      regex         = "(https?)"
                      target_label  = "__scheme__"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_path"]
                      regex         = "(.+)"
                      target_label  = "__metrics_path__"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_port", "__meta_kubernetes_pod_ip"]
                      regex         = "(\\d+);(([A-Fa-f0-9]{1,4}::?){1,7}[A-Fa-f0-9]{1,4})"
                      target_label  = "__address__"
                      replacement   = "[$2]:$1"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_annotation_prometheus_io_port", "__meta_kubernetes_pod_ip"]
                      regex         = "(\\d+);((([0-9]+?)(\\.|$)){4})"
                      target_label  = "__address__"
                      replacement   = "$2:$1"
              }

              rule {
                      regex       = "__meta_kubernetes_pod_annotation_prometheus_io_param_(.+)"
                      replacement = "__param_$1"
                      action      = "labelmap"
              }

              rule {
                      regex  = "__meta_kubernetes_pod_label_(.+)"
                      action = "labelmap"
              }

              rule {
                      source_labels = ["__meta_kubernetes_namespace"]
                      target_label  = "namespace"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_name"]
                      target_label  = "pod"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_phase"]
                      regex         = "Pending|Succeeded|Failed|Completed"
                      action        = "drop"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_node_name"]
                      target_label  = "node"
              }
      }

      prometheus.scrape "prometheus" {
              targets = [{
                      __address__ = "localhost:9090",
              }]
              forward_to = [prometheus.remote_write.default.receiver]
              job_name   = "prometheus"
      }

      prometheus.scrape "kubernetes_apiservers" {
              targets    = discovery.relabel.kubernetes_apiservers.output
              forward_to = [prometheus.remote_write.default.receiver]
              job_name   = "kubernetes-apiservers"
              scheme     = "https"

              authorization {
                      type             = "Bearer"
                      credentials_file = "/var/run/secrets/kubernetes.io/serviceaccount/token"
              }

              tls_config {
                      ca_file              = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                      insecure_skip_verify = true
              }
      }

      prometheus.scrape "kubernetes_nodes" {
              targets    = discovery.relabel.kubernetes_nodes.output
              forward_to = [prometheus.remote_write.default.receiver]
              job_name   = "kubernetes-nodes"
              scheme     = "https"

              authorization {
                      type             = "Bearer"
                      credentials_file = "/var/run/secrets/kubernetes.io/serviceaccount/token"
              }

              tls_config {
                      ca_file              = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                      insecure_skip_verify = true
              }
      }

      prometheus.scrape "kubernetes_nodes_cadvisor" {
              targets    = discovery.relabel.kubernetes_nodes_cadvisor.output
              forward_to = [prometheus.remote_write.default.receiver]
              job_name   = "kubernetes-nodes-cadvisor"
              scheme     = "https"

              authorization {
                      type             = "Bearer"
                      credentials_file = "/var/run/secrets/kubernetes.io/serviceaccount/token"
              }

              tls_config {
                      ca_file              = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
                      insecure_skip_verify = true
              }
      }

      prometheus.scrape "kubernetes_service_endpoints" {
              targets      = discovery.relabel.kubernetes_service_endpoints.output
              forward_to   = [prometheus.remote_write.default.receiver]
              job_name     = "kubernetes-service-endpoints"
              honor_labels = true
      }

      prometheus.scrape "kubernetes_service_endpoints_slow" {
              targets         = discovery.relabel.kubernetes_service_endpoints_slow.output
              forward_to      = [prometheus.remote_write.default.receiver]
              job_name        = "kubernetes-service-endpoints-slow"
              honor_labels    = true
              scrape_interval = "5m0s"
              scrape_timeout  = "30s"
      }

      prometheus.scrape "prometheus_pushgateway" {
              targets      = discovery.relabel.prometheus_pushgateway.output
              forward_to   = [prometheus.remote_write.default.receiver]
              job_name     = "prometheus-pushgateway"
              honor_labels = true
      }

      prometheus.scrape "kubernetes_services" {
              targets      = discovery.relabel.kubernetes_services.output
              forward_to   = [prometheus.remote_write.default.receiver]
              job_name     = "kubernetes-services"
              honor_labels = true
              params       = {
                      module = ["http_2xx"],
              }
              metrics_path = "/probe"
      }

      prometheus.scrape "kubernetes_pods" {
              targets      = discovery.relabel.kubernetes_pods.output
              forward_to   = [prometheus.remote_write.default.receiver]
              job_name     = "kubernetes-pods"
              honor_labels = true
      }

      prometheus.scrape "kubernetes_pods_slow" {
              targets         = discovery.relabel.kubernetes_pods_slow.output
              forward_to      = [prometheus.remote_write.default.receiver]
              job_name        = "kubernetes-pods-slow"
              honor_labels    = true
              scrape_interval = "5m0s"
              scrape_timeout  = "30s"
      }

      prometheus.remote_write "default" {
              endpoint {
                      url     = "http://mimir-nginx.mimir.svc:80/api/v1/push"
                      queue_config { }

                      metadata_config { }
              }
      }
```

Now install Alloy using above values.yaml and helm

```c
helm -n alloy install alloy grafana/alloy  -f values/alloy.yaml
```

Check if the pods are up

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*tD-wDa_ic5ynG1X1tNdXqw.png)

Now check in Grafana and see if the metrics are showing up

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5FWgEwLYEr-_qcuwtQPWZQ.png)

**Configure Alloy for Loki**

I found it easier to convert existing promtail config to alloy config than to start from scratch

```c
kubectl -n promtail exec -it promtail-jcm2z -- cat /etc/promtail/promtail.yaml > promtail_values.yaml
alloy convert --source-format=promtail --output=alloy_promtail.config promtail-values.yaml
```

Fix the errors and create a working configuration similar to the one I used below (you may modify it as per your requirements).  
*Note: Promtail is configured to send logs to Loki, so the configuration will include the Loki endpoint.*

```c
alloy:
  configMap:
    content: |-
      logging {
        level  = "info"
        format = "logfmt"
      }

      discovery.kubernetes "kubernetes_pods" {
              role = "pod"
      }

      discovery.relabel "kubernetes_pods" {
              targets = discovery.kubernetes.kubernetes_pods.targets

              rule {
                      source_labels = ["__meta_kubernetes_pod_label_app_kubernetes_io_name", "__meta_kubernetes_pod_label_app", "__tmp_controller_name", "__meta_kubernetes_pod_name"]
                      regex         = "^;*([^;]+)(;.*)?$"
                      target_label  = "app"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_label_app_kubernetes_io_instance", "__meta_kubernetes_pod_label_instance"]
                      regex         = "^;*([^;]+)(;.*)?$"
                      target_label  = "instance"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_node_name"]
                      target_label  = "node_name"
              }

              rule {
                      source_labels = ["__meta_kubernetes_namespace"]
                      target_label  = "namespace"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_name"]
                      target_label  = "pod"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_container_name"]
                      target_label  = "container"
              }

              rule {
                      source_labels = ["__meta_kubernetes_pod_uid", "__meta_kubernetes_pod_container_name"]
                      separator     = "/"
                      target_label  = "__path__"
                      replacement   = "/var/log/pods/*$1/*.log"
              }

      }

      local.file_match "kubernetes_pods" {
              path_targets = discovery.relabel.kubernetes_pods.output
      }
      loki.source.kubernetes "kubernetes_pods" {
          targets    = discovery.relabel.kubernetes_pods.output
          forward_to = [loki.process.process.receiver]
      }

      loki.process "process" {
          forward_to = [loki.write.loki.receiver]
      }

      loki.write "loki" {
          endpoint {
              url = "http://loki-loki-distributed-distributor.loki.svc.cluster.local:3100/loki/api/v1/push"
          }
      }
```

Upgrade alloy installation using above values.yaml

```c
helm -n alloy upgrade alloy grafana/alloy  -f values/alloy_logs.yaml
```

Check in Grafana and see if the logs are exported correctly

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*jXi-TGMD_B63PMMqKr_2Dg.png)

**Configure alloy for Traces**

Convert the existing Otel collector to alloy config

```c
kubectl -n otel get configmap otel-collector-opentelemetry-collector -o yaml > otel-values-fromcm.yaml
alloy convert --source-format=otelcol --output=alloy_otel.config otel-values-fromcm.yaml
```

You will, of course, see errors during conversion, as shown below. Fix them and derive the configuration you require. Patience is key here

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*f8EPDaOMa-CGR-xewCfEqg.png)

Now upgrade alloy to use the new values file with the traces config in it.

```c
# File name values/alloy_traces.yaml
alloy:
  extraPorts:
  - name: "otlp"
    port: 4317
    targetPort: 4317
    protocol: "TCP"
  - name: "otlphttp"
    port: 4318
    targetPort: 4318
    protocol: "TCP"
  configMap:
    content: |-
      logging {
        level  = "info"
        format = "logfmt"
      }
      otelcol.receiver.otlp "default" {
        grpc {
          endpoint = "0.0.0.0:4317"
        }

        http {
          endpoint = "0.0.0.0:4318"
        }

        output {
          traces  = [otelcol.processor.batch.default.input]
        }
      }

      otelcol.exporter.otlp "default" {
        client {
          endpoint = "http://tempo.tempo.svc.cluster.local:4317"
          tls {
                 insecure = true
          }

        }
      }
```
```c
helm -n alloy upgrade alloy grafana/alloy  -f values/alloy_traces.yaml
```

Check for traces in Grafana and confirm all is good.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*obY-sMPwoYmLppzwsaz8sw.png)

I’d love to hear any comments or suggestions you might have! 😊

AWS | Kubernetes | Observability | Let's connect: [https://www.linkedin.com/in/bibin-kuruvilla/](https://www.linkedin.com/in/bibin-kuruvilla/) [https://obsium.io/](https://obsium.io/) bibin AT obsium dot io

## More from Bibin Kuruvilla

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--c0ab2492f774---------------------------------------)