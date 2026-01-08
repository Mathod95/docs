---
title: 101 Argo Rollouts
date: 2026-01-07
categories:
  - Argo Events
tags:
  - Argo Events
  - 101
---

![](../../assets/images/argo/argo.svg)

## Introduction

<!-- more -->

Getting Started
We are going to set up a sensor and event-source for a webhook. The goal is to trigger an Argo workflow upon an HTTP POST request.

Note: You will need to have Argo Workflows installed to make this work. The Argo Workflow controller will need to be configured to listen for Workflow objects created in the argo-events namespace. (See this link.) The Workflow Controller will need to be installed either in a cluster-scope configuration (i.e., no "--namespaced" argument) so that it has visibility to all namespaces, or with "--managed-namespace" set to define "argo-events" as a namespace it has visibility to. To deploy Argo Workflows with a cluster-scope configuration, you can use this installation YAML file, setting ARGO_WORKFLOWS_VERSION with your desired version. A list of versions can be found by viewing these project tags in the Argo Workflows GitHub repository.

``` bash
kubectl create namespace argo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.7.6/install.yaml
```

1. Install Argo Events
```
kubectl create namespace argo-events
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install.yaml
# Install with a validating admission controller
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install-validating-webhook.yaml
```

2. Make sure to have the EventBus pods running in the namespace. Run the following command to create the EventBus.
```
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/eventbus/native.yaml
```

3. Set up the event-source for the webhook as follows.
```
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/event-sources/webhook.yaml
```


The event-source above contains a single event configuration that runs an HTTP server on port `12000` with the endpoint example.

After running the above command, the event-source controller will create a pod and service.

1. Create a service account with RBAC settings to allow the sensor to trigger workflows, and allow workflows to function.
```
# sensor rbac
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/master/examples/rbac/sensor-rbac.yaml
# workflow rbac
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/master/examples/rbac/workflow-rbac.yaml
```

2. Create the webhook sensor.
```
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/sensors/webhook.yaml
```

Once the sensor object is created, the sensor controller will create a corresponding pod and service.

1. Expose the event-source pod via Ingress, OpenShift Route, or port forward to consume requests over HTTP.
```
kubectl -n argo-events port-forward svc/webhook-eventsource-svc 12000:12000
```

2. Use either Curl or Postman to send a POST request to http://localhost:12000/example.
```
curl -d '{"message":"this is my first webhook"}' -H "Content-Type: application/json" -X POST http://localhost:12000/example
```

3. Verify that an Argo workflow was triggered.
```bash
kubectl -n argo-events get workflows | grep "webhook"
```