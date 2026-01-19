---
title: "Argo Events — Event Bus and Webhook"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.chuklee.com/argo-events-event-bus-and-webhook-ac34e5714209"
author:
  - "[[Chuk Lee]]"
---
<!-- more -->

[Sitemap](https://medium.chuklee.com/sitemap/sitemap.xml)

[Argo Event](https://argoproj.github.io/argo-events/) is a Kubernetes based event automation engine. It is part of the [Argo project](https://github.com/argoproj). Argo Events can be used with or independent of other projects in Argo.

I will be writing a series of articles on Argo Events; in these articles I will be looking at how we can use Argo Event to automate process within and without a Kubernetes cluster.

For this first article in this series, we will examine Argo Events core concepts, installation and provisioning different event buses which Argo Event uses to forward events to their sink. Finally we will look at setting up a webhook event flow to verify our setup.

## Core Concepts

- Events are activities that we are interested in; for example every 12 AM on the the first of each month, a file has just been uploaded to a S3 bucket, a messages has just arrived on a queue, etc. We are interested in these events because we would like to perform some task when the event occurs.
- [Event sources](https://argoproj.github.io/argo-events/concepts/event_source/) is the way by which external real-world events are captured and routed into Argo Events engine; they are created by CRDs called `EventSource`. Argo support many common event sources like HTTP request, S3, Slack, etc; you can find the list of the supported events [here](https://argoproj.github.io/argo-events/concepts/event_source/).
- [Triggers](https://argoproj.github.io/argo-events/concepts/trigger/) are processes that are executed in response to an event. The is the action that you want to take when an event happens. Examples of triggers include sending an email message, rolling out a new application release, forwarding the event to a Kafka queue, invoking a serverless operation, etc. You can find a list of supported triggers [here](https://argoproj.github.io/argo-events/concepts/trigger/).
- [Sensor](https://argoproj.github.io/argo-events/concepts/sensor/), created by the CRD `Sensor`, determines which trigger to execute based on the events from event sources; for example a sensor can trigger a serverless operation from an upload event on a S3 bucket or perform a deployment of an application to the testing environment in response to a pull request event. The event sources are inputs, also known as dependencies, into sensors; triggers are the outputs from sensors.

Argo Events uses a message queue, called an [event bus](https://argoproj.github.io/argo-events/eventbus/eventbus/), to reliably transfer events from event sources to sensors.

The following diagram shows the relationship between the described components

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QxJdXQhNrlJ2DHEJqkiIJw.png)

Argo Event conceptual architecture

## Installation Workflow

The following are the required steps to setup and deploy Argo Event

1. Install Argo Events. Create a namespace call `argo-events` and install the event controller and a validating webhook. You can find the instructions [here](https://argoproj.github.io/argo-events/installation/).
2. Deploy one or more event buses. Since `EventBus`, `EventSource` and `Sensor` are are namespace scoped resource, event buses must be deployed into the same namespace as the `EventSource` and `Sensor`; event source and sensor can only use event buses in their namespace for communication. You may also need to manually create topics/queues if your event bus do not support auto topic creation. More on this later in this article
3. Deploy one or more event sources into the same namespace as the event bus.
4. Deploy one or more sensors into the same namespace as the event bus, specifying the deployed event sources as dependencies (inputs) and the corresponding triggers that will be called if the dependencies are resolved. Sensors must use the same event bus as the event source if a sensor is to receive events from that event source.
5. Install Argo Workflow if you are planning to trigger Argo Workflows. You can also use Argo Workflow’s web interface to view and manage event flow graphically; Argo Event do not come with any graphical interface.

## Event Bus

Event bus is a message broker; data is enqueued by producers is transmitted to its destination where they are dequeued and consumed as shown in the following diagram

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*kqG2vXLzDWM1aexr.png)

Image from https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview

In the context of Argo Events, event sources are the producers. They capture real world events like a push to GitHub, uploading a file to a S3 bucket, data from a MQTT topic, Stripe transaction, etc and enqueued these events as [cloudevents](https://github.com/cloudevents/spec) objects into an event bus. These events are then consumed by sensors which can be transformed and/or forwarded to triggers.

Argo Events uses existing messaging systems rather than implementing its own message broker. Message brokers can be deployed in-cluster or leverage existing external message brokers. Argo supports the following event bus: NATS (deprecated), [Jetstream](https://docs.nats.io/nats-concepts/jetstream) or [Kafka](https://kafka.apache.org/).

In the next section, we will create 2 event bus: the first is in-cluster and the second uses an existing Kafka cluster.

### Jetstream Event Bus

We will create an in-cluster `EventBus` based on Jetstream.

The `EventBus` is called `jetstream-eb` and it is created in the `playground` namespace. The Jetstream message broker consists of 3 nodes (`jetstream-eventbus.yaml` line 10). You can pass additional parameters to the broker with the `streamConfig` parameter; in the above example, messages are duplicated to 2 nodes for resiliency, and messages are retained for 5 minutes (`jetstream-eventbys.yaml` lines 12,13). You can see a list of other Jetstream options [here](https://docs.nats.io/nats-concepts/jetstream/streams).

Verify that the event bus have been created with the following command

```c
kubectl get all,sts,eventbus -nplayground
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*3Ulg7Cr-xsjsbGhNh3EnkA.png)

`eb` is the shortname for `eventbus` resource.

### Kafka Event Bus

In the second event bus example, we will use an existing Kafka cluster as an event bus. I have a Kafka cluster deployed on [Upstash](https://upstash.com/) with the following properties:

The following `EventBus` CRD deploys an event bus that uses the above Kafka cluster for event delivery.

We start by configuring the cluster’s [bootstrap server](https://jaceklaskowski.gitbooks.io/apache-kafka/content/kafka-properties-bootstrap-servers.html) and the topic that the event bus will be using to queue events (`kafka-eventbus.yaml` lines 21, 22).

The Kafka topic can be created automatically by Argo Events if the property `[auto.create.topics.enabled](https://kafka.apache.org/documentation/#brokerconfigs_auto.create.topics.enable)` is enabled.

Since my Kafka cluster has disabled auto topic creation, I have manually created the topic, `argo-kafka-eventbus`, and include the topic name in the `topic` attribute (`kafka-eventbus.yaml` line 22) of the `EventBus` resource. Note that for every sensor, you will need an additional 2 topics; more details on this later.

The next major configuration block is the credentials used by Argo Events to login to the cluster. Examining the above configuration file, `kafka.properties`, we have the following:

- [Client authentication is performed over SSL](https://en.wikipedia.org/wiki/Simple_Authentication_and_Security_Layer) — SASL\_SSL (`kafka.properties` line 3)
- Authentication mechanism — [SCRAM-SHA-256](https://en.wikipedia.org/wiki/Salted_Challenge_Response_Authentication_Mechanism) (`kafka.properties` line 2)
- Username and password (`kafka.properties` lines 5, 6)

We will need to create a `Secret` to hold the username and password (`kafka-eventbus.yaml lines` 2 — 10). The `EventBus` will source the username and password from this `Secret` (`kafka-eventbus.yaml` lines 27–32).

Finally we configure the event bus to use SASL\_SSL and SCRAM-SHA-256 for authentication (`kafka-eventbus.yaml lines` 25, 26). I could not find Upstash’s CA certificate so I am skipping the certificate verification with `tls.insecureSkipVerify` set to `true` (`kakfa-eventbus.yaml` lines 23, 24). If you have the cluster’s CA certificate, then you can configure the CA with `tls.caCertSecret` attribute (see [this](https://argoproj.github.io/argo-events/eventbus/kafka/#tls)).

## Producing Events with EventSource

An `EventSource` resources queue real world events into an event bus. You will have to start your event workflow by sourcing from one or more of the supported [event sources](https://argoproj.github.io/argo-events/concepts/event_source/).

For this article, we will look at one of the most common type of event: the [webhook](https://github.com/argoproj/argo-events/blob/master/api/event-source.md#webhookeventsource) event.

### Webhook Event Source

A webhook is a communication endpoint, typically over HTTP, that allows one application to send notification to another using the endpoint. Whereas ‘traditional’ API endpoint is request-response viz. the application that makes the request will also expect a response, e.g. what is the weather in Singapore?

A webhook on the other hand is a one-way exchange; when you invoke a webhook, you will typically not expect a response except an acknowledgement eg. with a [202](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202) status code in the case of a HTTP. An common example of webhook is receiving a transaction details in your email when you use your phone for payment.

The following `EventSource` resource creates a webhook for receiving notifications.

- The `webhook` attribute (`webhook-es.yaml` line 10) creates a HTTP endpoint on port 12000; events are sent with the `POST` method to `/notify` resource (`webhook-es.yaml` lines 12–14).
- The event’s name is called `simple` (`webhook-es.yaml` line 11). You can have multiple events under `webhook`; however the event names must be unique. You can also configure multiple types of events in a single `EventSource` resource. See the `EventSource` [documentation](https://github.com/argoproj/argo-events/blob/master/api/event-source.md#eventsourcespec) for the complete list. In future articles, we will look at other event sources.
- Events received by the webhook event source are queue to the `kafka-eb` event bus (`webhook-es.yaml` line 9).

When the above webhook `EventSource` is deployed, Argo Event provisions a `Deployment` with 1 pod; the pod listens on port 12000. To expose webhook outside world, you have to deploy an additional `Service` and an `Ingress` resource. The webhook event source pod has the following labels: `eventsource-name` and `owner-name`. These values default to the name of the event source: `webhook-es` (`webhook-es.yaml` line 5). Create a Service to forward traffic to these pods and expose the service with an `Ingress` as shown in the following YAML.

The following shows the output listing of `EventSource` and the resulting `Deployment` and `Pod` along with the `Service` and `Ingress` resource to expose the event.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*T1H4kYDNOKw-0dFULK-Q8g.png)

According to Argo Event documentation, [several event sources](https://argoproj.github.io/argo-events/eventsources/services/#eventsource-services) starts a HTTP service to receive incoming events. For these event sources, deploy an `Ingress` if these event sources need to be accessible from outside of the cluster or a ClusterIP `Service` only if it is for the cluster only.

## Consuming Events with Sensor

A sensor consumes events, called dependencies, on the same event bus as the event source from which the sensor is receiving its events. When the event fires, a `Sensor` will dequeue the event from the bus, extract the event object and use it to invoke one or more defined triggers.

### HTTP Trigger

One of the most common trigger is the HTTP trigger. Think of a HTTP trigger like a `curl`; which you can use to invoke any REST endpoint including serverless, web application, trigger other callbacks, etc.

In the following example, we create a `Sensor` to ingest events from `webhook-es` `EventSource` (`webhook-es.yaml`). The `Sensor` then selects some of the (arbitrary) fields from the event payload and forwards it to a deployed application, a simple web application that logs the contents of a `POST` request (see this [gist](https://gist.github.com/chukmunnlee/b6ce1491e4785e5747bb7c9a0afea271)).

- `eventBusName` (`webhook-sn.yaml` line 8) specifies which bus to subscribe to for event delivery.
- The `dependencies` define what are the events the `Sensor` is interested in (`webhook-es.yaml` lines 9–12).
- A dependency consist of 3 attributes: the event source’s name (`webhook-es`, `webhook-es.yaml` line 11) and the event name (`simple`, `webhook-es.yaml` line 12) from the event source and name (`message`, `webhook-es.yaml` line 10) to associated the event source, event name pair locally. This name, `message`, can be used as a reference when we are extracting values from the event.
- `triggers` define the action to take when the there is a event match from the event source. Each trigger is defined within a trigger template (`webhook-sn.yaml` lines 14–37). A template consist of a unique trigger name (`webhook-sn.yaml` line 15) and the [type of trigger](https://github.com/argoproj/argo-events/blob/master/api/sensor.md#argoproj.io/v1alpha1.TriggerTemplate) (`webhook-sn.yaml` line 16).
- In the above example, we use the [HTTP trigger](https://github.com/argoproj/argo-events/blob/master/api/sensor.md#httptrigger) (`webhook-sn.yaml` lines 16–37) to invoke the `shttpbin-svc` service (`webhook-sn.yaml` line 17) with a `POST` method. The payload of the `POST` method is extracted (`webhook-sn.yaml` lines 21 — 37) from the event object in the `payload` (`webhook-sn.yaml` line 21) attribute. The extracted values are passed as `application/json` to `shttpbin-svc` service.
- Each of the `payload` has a source, which uses JSON path to extract the value (`webhook-sn.yaml` lines 22–25, 26–29, 30–33) from the event object, and a destination (`webhook-sn.yaml` line 25, 29, 33), the name to bind the extracted value to.
- The JSON path address an attribute in the playload of the webhook. You can find out about the paybload by examining the cloudevent that the event source has queued. The following diagram shows the cloudevent object in the `argo-kafka-eventbus`.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*gqvWsGqAElyRMPQYjwPuUQ.png)

cloudevent object queued by webhook-es event source on kafka-eb event bus

- The webhook event is encoded as base64 in the `data_base64` attribute. If you decode the `data_base64`, you will get the following JSON structure.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*iZvXnobM20Ua6Txx)

Decoded base64 string from data\_base64

- To extract the email value, the JSON path would be `body.message.email`. Argo Events undecode `data_base64` before extracting the values. The JSON path is based on [tidwall/sjson](https://github.com/tidwall/sjson) implementation. Refer to the [documentation](https://github.com/tidwall/sjson#path-syntax) for more path expressions..
- cloudevent metadata can be extracted with the `contextKey` (`webhook-sn.yaml` line 37) instead of `dataKey` attribute.
- You can also include headers with the `headers` attribute (`webhook-sn.yaml` lines 19, 20) and optionally define a success criteria of the HTTP trigger invocation with `policy.status.allow` (`webhook-sn.yaml` lines 38–41). If `shttpbin-svc` returns a 200 status, then the invocation is successful.

The following figure summarizes the dependencies between `EventSource` and `Sensor`.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*lzXHdEodUA7XqGZyjD36WA.png)

If you have Argo Workflow installed you can view the event flow in Argo Workflow’s web console. Port forward to the `argo-server` service with the following command

```c
kubectl port-forward svc/argo-server 2746:2746 -nargo
```

The events can be found under the Event Flow tab.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*SY5UP8d7hTeHwBo6)

Event flow

### Kafka Topics for Sensors

According to Argo Event documentation, for every `Sensor`, we need to create [2 additional topic](https://argoproj.github.io/argo-events/eventbus/kafka/#topics), one for triggers and the other for actions. The topics are created according a strict naming convention.

For our example, the `EventSource` `webhook-es` and `Sensor` `webhook-sn`, publish to and subscribe from the topic `argo-kafka-eventbus` from the `kafka-eb` event bus.

For the `webhook-sn` sensor, to receive events from `webhook-es`, we will need to create 2 additional topics in our Kafka cluster using the following naming convention `<event bus topic name>-<sensor name>-action` and `<event bus topic name>-<sensor name>-action`; see the following figure for the 2 additional topics created to support `webhook-sn` `Sensor`. You do not have to manually create these topics if your Kafka cluster supports creating topics automatically.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*jX8JnsbuNpXZEVEY)

2 additional topics for every sensor

## Testing the Event Flow

Test the webhook by sending a `POST` request to `/notify` at the `webhook-es` `Ingress` endpoint; the following example uses `curl` to `POST` JSON payload to the webhook endpoint at `webhook-192.168.39.85.nip.io`.

```c
curl -v -X POST webhook-192.168.39.85.nip.io/notify \
   -H 'Content-Type: application/json' \
   -d '{ "message": { "id": "abc123", "name": "fred", "email": "fred@gmail.com" } }'
```

If you are not able to see the event arriving at `shttpbin-deploy`, then you can trace the event from the source to its sink by examining the following:

- Logging the `EventSource` deployment
- Viewing the contents of `argo-kafka-eventbus` topic from your Kafka console or with the `kafka-topics.sh` command
- Logging the `EventSensor` deployment
- Viewing the contents of `argo-kafka-eventbus-webhook-sn-trigger` topic
- Your application logs which in this case is `shttpbin-deploy`

We will explore other event sources and and triggers in future articles.

Till next time…

## More from Chuk Lee

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--ac34e5714209---------------------------------------)