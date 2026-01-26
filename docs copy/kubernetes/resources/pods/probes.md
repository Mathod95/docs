---
title: Probes
categories: Kubernetes
tags:
  - Kubernetes
status:
sources:
  - Probes: https://towardsdev.com/liveness-readiness-and-startup-probes-in-kubernetes-b33a7c11d481
---

Liveness, Readiness, and Startup Probes stand out as essential mechanisms for maintaining application health and optimizing service performance. This article delves into these probes, elucidating their functionalities, differences, and best practices for their implementation.

Liveness, Readiness, and Startup Probes

### The Importance of Probes in Kubernetes

In a Kubernetes environment, applications are deployed in containers across multiple pods and nodes. This distributed nature can complicate monitoring and managing the health of applications. Probes are Kubernetes’ solution to this challenge, providing a way to automatically check the health of an application and take necessary actions to maintain its reliability.

### Liveness Probes: Keeping Containers Alive

Liveness probes determine if a container is running as expected. Kubernetes uses these probes to decide when to restart a container. For instance, if a liveness probe fails, indicating that an application is unresponsive or deadlocked, Kubernetes will restart the container, attempting to restore its normal operation. This automated intervention helps maintain service availability even in the face of software faults.

**Example:** Consider a web server running inside a container, serving traffic on port 8080. A liveness probe could be configured to perform an HTTP GET request to `/healthz`, an endpoint that returns a 200 OK status code if the server is healthy. If this endpoint fails to respond correctly, the liveness probe fails, signaling Kubernetes to restart the container.

```yaml linenums="1"
livenessProbe:
 httpGet:
 path: /healthz
 port: 8080
 initialDelaySeconds: 15
 periodSeconds: 10
```

### Readiness Probes: Managing Traffic Flow

Readiness probes assess whether a container is ready to serve traffic. Unlike liveness probes, if a readiness probe fails, Kubernetes will not kill the container; instead, it removes the pod from the list of service endpoints, preventing it from receiving traffic. This is particularly useful during startup or when an application is temporarily unable to serve traffic due to loading large data sets or performing other initialization tasks.

**Example:** Imagine an application that needs to load a large configuration file or establish a database connection before it can start serving traffic. A readiness probe can be configured to check an endpoint, such as `/ready`, which only returns a 200 OK status code once the initialization process is complete.

```yaml linenums="1"
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Startup Probes: The Initial Health Check

Startup probes are designed to check the health of a container that might take a long time to start. They provide a way to delay liveness and readiness checks, giving an application sufficient time to initialize without being restarted by Kubernetes due to slow startup times. Once a startup probe succeeds for the first time, it is disabled, and liveness and/or readiness probes take over.

**Example:** For an application that requires a significant amount of time to start, such as initializing a large dataset or waiting for external services, a startup probe can ensure that Kubernetes does not prematurely restart the container. This probe might execute a command inside the container that checks for the existence of a file indicating readiness.

```yaml linenums="1"
startupProbe:
 exec:
 command:
 — cat
 — /app/is_ready
 initialDelaySeconds: 10
 periodSeconds: 20
```

### Best Practices for Implementing Probes

1. Customize Probe Parameters: Adjust the `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `successThreshold`, and `failureThreshold` according to the specific needs of your application to avoid unnecessary restarts or downtime.
2. Use Probes Judiciously: Not every container needs a liveness or startup probe. Use them when containers are prone to deadlocks or have lengthy startup times.
3. Optimize Probe Effectiveness: Ensure that the checks performed by probes are reliable indicators of application health and readiness. Avoid heavy operations that could impact performance.
4. Monitor and Adjust: Continuously monitor the effectiveness of your probes and adjust their configurations as needed. This is especially important as your application evolves.
5. Leverage Probe Specifics: Each type of probe (HTTP, TCP, Exec) has its own benefits. Choose the one that best fits the health indicators of your application.