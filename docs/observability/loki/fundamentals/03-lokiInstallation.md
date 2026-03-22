---
title: Loki Installation
status: draft
sources:
  - https://notes.kodekloud.com/docs/Grafana-Loki/Grafana-Loki-Essentials-Part-1/Loki-Installation/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/grafana-loki/module/99ea0065-ea43-4058-9fef-46fbe62292ee/lesson/689b850b-e392-491a-8654-a08ab31a2102?autoplay=true
---

> This guide explains how to install Loki locally and configure it with Promtail as a logging agent.

In this guide, you'll learn how to install Loki on your local machine and configure it to work with Promtail as your logging agent. For more detailed information, please refer to the [official Loki documentation](https://grafana.com/docs/loki/latest/).

## 1. Overview

Loki provides multiple deployment options including Helm charts for Kubernetes and Docker container installations. This guide focuses on installing Loki locally. Before you begin, visit the Loki documentation page and review the installation instructions.

## 2. Downloading Configuration Files for Loki and Promtail

Start by downloading the configuration files necessary for both Loki and Promtail. Open your terminal and execute the following commands:

```bash
wget https://raw.githubusercontent.com/grafana/loki/main/cmd/loki/loki-local-config.yaml
wget https://raw.githubusercontent.com/grafana/loki/main/clients/cmd/promtail/promtail-local
```

These commands download a basic configuration for a local setup. Feel free to modify these files later according to your specific logging requirements.

## 3. Downloading the Loki Binary

Select the appropriate release for your system architecture. Visit the Loki [release page](https://github.com/grafana/loki/releases) for the latest version. For example, to download and prepare the Loki binary, run the following commands:

```bash
curl -O "https://github.com/grafana/loki/releases/download/v2.7.2/loki-linux-amd64.zip"
# Extract the binary
unzip loki-linux-amd64.zip
# Make the binary executable
chmod a+x loki-linux-amd64
```

After these commands, confirm the presence of the Loki binary by listing your directory contents. If the zip file has not been extracted, you can run:

```bash
curl -O -L "https://github.com/grafana/loki/releases/download/v2.8.2/loki-linux-amd64.zip"
ls
unzip loki-linux-amd64.zip
```

You should now see the executable Loki binary in your working directory.

## 4. Reviewing the Loki Configuration File

If you haven't already obtained the configuration file, download it by running:

```bash
wget https://raw.githubusercontent.com/grafana/loki/main/cmd/loki/loki-local-config.yaml
wget https://raw.githubusercontent.com/grafana/loki/main/clients/cmd/promtail/promtail-local-config.yaml
```

You can open and inspect the configuration file using your preferred text editor. For example:

```bash
vi loki-local-config.yaml
```

A typical configuration file includes settings for the HTTP server (port 3100), the gRPC server (port 9096), and filesystem storage for log chunks and rules. Here is an example snippet:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 127.0.0.1
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
    replication_factor: 1
  ring:
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
```

<Callout icon="lightbulb" color="#1CB2FE">
  This configuration instructs Loki to use the local file system for storage. You can modify these settings or switch to another storage backend, such as S3, based on your needs. For more tailored configurations, consult the [Loki documentation](https://grafana.com/docs/loki/latest/).
</Callout>

## 5. Running Loki

Once the configuration file is ready, you can start Loki. Use the appropriate command for your operating system:

### For Windows

```bash
.\loki-windows-amd64.exe --config.file=loki-local-config.yaml
```

### For Linux

```bash
./loki-linux-amd64 -config.file=loki-local-config.yaml
```

When you run the executable, Loki will start up and display several log messages. Look for logs similar to the following to confirm that it has started correctly:

```plaintext
level=info ts=2023-07-18T05:54:14.795944069Z caller=compactor.go:346 msg="waiting until compactor is ACTIVE in the ring"
level=info ts=2023-07-18T05:54:14.796194848Z caller=ingester.go:432 msg="recovered WAL checkpoint recovery finished" elapsed=1.148398ms errors=false
...
level=info ts=2023-07-18T05:54:14.972723532 caller=worker.go:209 msg="adding connection" addr=127.0.0.1:9096
```

<Callout icon="lightbulb" color="#1CB2FE">
  These log messages indicate that Loki is initializing its internal processes and joining the cluster ring successfully.
</Callout>

## 6. Verifying the Installation

To ensure Loki is running as expected, open your web browser and navigate to:

http\://\[LOKI\_SERVER\_IP]:3100/metrics

Replace \[LOKI\_SERVER\_IP] with the actual IP address or DNS name of your Loki server. If everything is set up correctly, you will see the metrics output similar to what is shown in the logs.

<Callout icon="lightbulb" color="#1CB2FE">
  Now that Loki is successfully installed, consider exploring additional configuration options and integrations with Promtail for a comprehensive logging solution. Visit the [Loki documentation](https://grafana.com/docs/loki/latest/) for further details and advanced configurations.
</Callout>