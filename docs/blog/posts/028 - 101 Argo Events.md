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

<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 320" width="920" height="320"><!-- svg-source:excalidraw --><metadata><!-- payload-type:application/vnd.excalidraw+json --><!-- payload-version:2 --><!-- payload-start -->eyJ2ZXJzaW9uIjoiMSIsImVuY29kaW5nIjoiYnN0cmluZyIsImNvbXByZXNzZWQiOnRydWUsImVuY29kZWQiOiJ4nOWUW2/aMFx1MDAxNIDf+Vx1MDAxNVH22tJcXJyQ8NZRqqKVqWpardI0TW5yXGJcdTAwMWXGjmKHQlx1MDAxMf99dqA4XHUwMDAxqnXS3pZIkXzuPuc7WXcsy5arXHUwMDAy7L5lwzLFlGQlfrHPtHxcdTAwMDGlIJwplVefXHUwMDA1r8q0tpxKWYj+xYXx6KZ8vvVcdTAwMDJcbnNgUii77+psWev6qzQk077kjlxy5Vx1MDAxZEJJkP0kOVx1MDAxMtFlzmjtWlx1MDAxYr1cdTAwMTVTQioxyylcdTAwMTjVUsn9nuPsXHUwMDA1KyWIXHUwMDFh51x1MDAxN5LJqZbFcTduPNHeYlxuJJ9KXHUwMDFkp+G2TdO3jETIks9gwCkvdS2fXFzQr6nkXHUwMDE5p7O85Fx1MDAxNctcdTAwMWE2WL/GZkIoTeSqjqxap9pkXHUwMDFmxP+2K9c9kL/npVx1MDAxMuZTXHUwMDA2QrRq5Vx1MDAwNU6J1K1wXHUwMDFid9LVXHUwMDE1o6yewlx1MDAwZlNTiecw0mNgXHUwMDE1pXsxYVx1MDAxOejm2s9cIm2lY9kuXctcXFx1MDAwMOhcdTAwMTBcYvmB43hesFdcdTAwMThgwiPhV85qdlDgoDB2XHUwMDFk32RcdTAwMTdXilx1MDAxOVnHnGAqwLRZVzA0PLWqqIpcZm+d3F5cdTAwMTj1vCBy41x1MDAxOJm8lLDZoVx1MDAwZuXpzOSppZuzU5Bef3GffpXJ1dPEOz/nVbp4neXjY0glLOUhn16bT9dBx4BcIt/v9lx1MDAxNJdx6CHH81x1MDAxMTpcdTAwMDa0cZM/8zmpn/+Bz+zjfIZR6Fx1MDAwNj1cdTAwMWad4jNw3+MzREFcdTAwMWN5Tvjv+Vxm48CL/b/g0+CmMVPXXHUwMDFmjG5Hj2NrcPuYPFxm763xMLlpzJMzmZBXfVx1MDAwNz9sSa/xnFA9gKBcdTAwMTXxkpJcXPfCpjBpUKz6IYn6re/Vklx1MDAxN0abqniYMCiPp8RLklx1MDAxM4bpw0eqxZXk9yC29cqygmZf4OZtXHUwMDBi3K5cdTAwMTds11R9a05sXFxcdTAwMTSJVJ1V2u3S2lx1MDAwYlx1MDAwMi+fT1x1MDAxML/bis5uyTXxoMe03nQ2v1x1MDAwMZDDyEoifQ==<!-- payload-end --></metadata><defs><style class="style-fonts">
      @font-face { font-family: Excalifont; src: url(data:font/woff2;base64,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); }</style></defs><g stroke-linecap="round" transform="translate(10 10) rotate(0 450 150)"><path d="M0 0 L900 0 L900 300 L0 300" stroke="none" stroke-width="0" fill="#1a1a1a"></path><path d="M0 0 C354.54 0, 709.08 0, 900 0 M0 0 C351.97 0, 703.93 0, 900 0 M900 0 C900 113.09, 900 226.17, 900 300 M900 0 C900 66.59, 900 133.18, 900 300 M900 300 C641.88 300, 383.76 300, 0 300 M900 300 C622.06 300, 344.12 300, 0 300 M0 300 C0 184.67, 0 69.34, 0 0 M0 300 C0 181.73, 0 63.45, 0 0" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(30 250) rotate(0 216.8999481201172 22.5)"><text x="0" y="31.716" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="36px" fill="#ffffff" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">ARGO ROLLOUTS 101</text></g></svg>

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