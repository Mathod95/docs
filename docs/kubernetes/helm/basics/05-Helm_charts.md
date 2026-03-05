---
title: Helm charts
source:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Helm-Basics/Helm-charts/page
---

# Helm charts

> Helm Charts simplify application deployment on Kubernetes by managing complex configurations through reusable instruction manuals.

Helm is a command-line automation tool that simplifies the deployment, upgrade, and rollback of applications on Kubernetes. Instead of manually executing numerous individual operations, Helm accepts high-level commands like “install this application” and manages all the necessary steps behind the scenes. It achieves this by reading a set of instructions defined in Helm Charts.

Charts are essentially instruction manuals composed of multiple text files, each serving a specific purpose. One of the key files is the **values.yaml** file, which defines configuration parameters. These parameters are referenced within template files to generate the final Kubernetes manifest files used to create objects.

Below is an example of a simple Helm chart that deploys a basic "hello-world" application. This chart defines two Kubernetes objects: a Service and a Deployment. Notice how templating is used for values like the container image and replica count, which are later defined in the **values.yaml** file.

<Callout icon="lightbulb" color="#1CB2FE">
  This example demonstrates the power of using Helm Charts to abstract complex Kubernetes configurations into a reusable package.


## Hello-World Helm Chart Example

### Service Definition

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hello-world
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: hello-world
```

### Deployment Definition

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-world
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: hello-world
  template:
    metadata:
      labels:
        app: hello-world
    spec:
      containers:
        - name: hello-world
          image: "{{ .Values.image.repository }}"
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
```

### Default Configuration Values

```yaml
# values.yaml
replicaCount: 1
image:
  repository: nginx
```

Templating enables the same chart to be customized based on the configuration provided in **values.yaml**. When you run the following command, Helm uses the templates alongside the values file to generate the final Kubernetes manifest files:

```bash
$ helm install hello-world
```

## Chart Metadata with Chart.yaml

In addition to the **values.yaml** file, every Helm chart includes a **Chart.yaml** file. This file contains essential metadata such as the API version, app version, name, description, and chart type.

Consider the following **Chart.yaml** for the "hello-world" application:

```yaml
apiVersion: v2
appVersion: "1.16.0"
name: hello-world
description: A web application
type: application
```

The API version is particularly important. While Helm 2 did not include the API version field, Helm 3 introduced it along with other features like chart dependencies and type fields. Charts built for Helm 3 must have the API version set to v2. Using a Helm 3 chart with API version v2 in Helm 2 may lead to unexpected results. Therefore, always set the API version to v2 when developing a chart for Helm 3.

<Callout icon="triangle-alert" color="#FF6B6B">
  If you encounter a chart that lacks an API version field, it is likely built for Helm 2. Attempting to deploy such charts with Helm 3 might result in unexpected behavior. Always verify the chart version before installation.


## Comprehensive Example: Deploying WordPress

Consider another example where the Helm chart deploys WordPress. In this case, the **appVersion** field represents the version of the WordPress application, while the **version** field tracks the chart version. This distinction helps manage changes in the chart independently of the application version.

Below is the sample **Chart.yaml** for WordPress:

```yaml
apiVersion: v2
appVersion: 5.8.1
version: 12.1.27
name: wordpress
description: Web publishing platform for building blogs and websites.
type: application
dependencies:
  - condition: mariadb.enabled
    name: mariadb
    repository: https://charts.bitnami.com/bitnami
    version: 9.x.x
keywords:
  - application
  - blog
  - wordpress
maintainers:
  - email: containers@bitnami.com
    name: Bitnami
home: https://github.com/bitnami/charts/tree/master/bitnami/wordpress
icon: https://bitnami.com/assets/stacks/wordpress/img/wordpress-stack-220x234.png
```

## Chart Directory Structure

Helm charts are organized in a standard directory structure. At a minimum, a chart directory includes:

* **templates** directory: Contains all the template files (e.g., Service and Deployment manifests).
* **values.yaml** file: Provides the default configuration values.
* **Chart.yaml** file: Holds metadata about the chart.

Additional files such as a LICENSE or README, and directories like **charts** (for dependent charts) might also be included.

## Installing the WordPress Chart

To install the WordPress chart from the Bitnami repository, execute the following commands:

```bash
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm install my-release bitnami/wordpress
```

This completes the overview of Helm charts. We explored how Helm uses charts to automate Kubernetes deployments with templating and values files, and reviewed the structure and metadata defined in **Chart.yaml**.

In the next lesson, we will dive deeper into chart dependencies and provide additional details on customizing your Helm charts.

For further reading, consider visiting [Helm Documentation](https://helm.sh/docs/).