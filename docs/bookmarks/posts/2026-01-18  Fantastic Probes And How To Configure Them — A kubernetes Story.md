---
title: "Fantastic Probes And How To Configure Them — A kubernetes Story"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/swlh/fantastic-probes-and-how-to-configure-them-fef7e030bd2f"
author:
  - "[[Ricardo A.]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)## [The Startup](https://medium.com/swlh?source=post_page---publication_nav-f5af2b715248-fef7e030bd2f---------------------------------------)

[![The Startup](https://miro.medium.com/v2/resize:fill:76:76/1*pKOfOAOvx-fWzfITATgGRg.jpeg)](https://medium.com/swlh?source=post_page---post_publication_sidebar-f5af2b715248-fef7e030bd2f---------------------------------------)

Get smarter at building your thing. Follow to join The Startup’s +8 million monthly readers & +772K followers.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Qz93alITsYBh5txFuAZ3zg.png)

Distributed systems are great, right? But manage them and monitor all components to be sure everything is up and running synchronized like musicians in an orchestra is not that great. At least, not that easy…

Fortunately, nowadays most platforms offer tools to help us to keep the house in order and ensure we won’t run into big surprises. And Kubernetes is not different in this aspect, providing a set of tools to monitor applications and to automatically take actions based upon their state.

In this article I’ll talk about one of these tools and probably the easiest to setup: **probes**. Despite the name resemble some sophisticated spacecraft/sci-fi artifact, they are nothing more than actions performed by the internal ***kubelet*** process to check which pods have their applications available and running properly.

Probes are defined inside container’s definition in the *.yaml* resource file used to create the pod:

```c
apiVersion: v1
kind: Pod
metadata:
   (...)
spec:
  containers:
  - name: my-awesome-container
    image: some-awesome-image
    (...)
    <probe-type>:
      <probe-action>: (...)
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 3
      successThreshold: 2
      failureThreshold: 4
```

==Kubernetes supports== ==***Readiness***== ==and== ==***Liveness***== ==probes. For clusters running version 1.16 or higher, there’s a third type as well called== ==***Startup***====. All of them are optional and, as you can see, each container running inside the pod may have it’s own set of probes.==

## Probe Mechanism

No matter what type of probe is executed, Kubernetes uses a common set of properties to control and decide when to execute it and the criteria to consider it successful or failed.

The first one is the initial delay (**initialDelaySeconds**) which defines the amount of time in seconds to wait before executing the probe for the first time. This interval is particularly good when we have applications with lots of dependencies and/or large loading time. If this property is not set, the probe will be executed as soon as the container is loaded.

After this initial delay, the probe is executed and *kubelet* waits for a certain amount of time for a result before assuming a fail for timeout (**timeoutSeconds**). Keep in mind that if you have a short timeout, you may have false results just because your application had no time enough to process the action. The default value is 1 second which is enough for most situations but I highly recommend to define a realistic value for each application.

If the probe fails, *kubelet* tries again how many times as set in the **failureThreshold** property, this way any temporary unavailability won’t cause the probe to put the container in a failed state. Only after the last consecutive failed attempt the container will be considered failed. If not set, the default number of attempts is 3.

In some situations a single successful result may not be enough to really ensure the health of our container. In this case, the **successThreshold** property sets how many consecutive times the action needs to be successful to change the state of a container from failed to successful.

We can also set the interval between one execution and another, in seconds, using the **periodSeconds** property. If not set, the probe will be executed every 10 seconds.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*hpuMx_1BvJ5BDqqxhJ18PA.png)

Kubernetes Probes — General flow

A quick observation: In my experience, I’ve seen more than once developers wrongly interpreting the fact that, except for the new *Startup*, all probes are periodically executed during the pod’s lifespan (yeah, I’m looking to you *Readiness* probe… we’ll talk about this later on).

## Probe Actions

Each application is different and so is the way to define their healthiness. Based upon this premise, probes can execute different **actions** to interact with applications running in a container.

### HTTP Request

As Kubernetes is usually used in micro-services architectures, the most common probe action you’ll see around and probably setup is the **HTTP request** ([*HTTPGetAction*](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.16/#httpgetaction-v1-core)).

```c
<probe-type>:
   httpGet:
     path: /my/healthcheck/endpoint?param=value
     port: 8080
     httpHeaders:
     - name: SomeHeaderName
       value: someHeaderValue
     - name: AnotherHeaderName
       value: "Another Header Value"
   initialDelaySeconds: 5
   periodSeconds: 10
   (...)
```

In this case, *kubelet* sends a GET request to the configured endpoint (*path*) and port (if not specified, port 80 is used) and check the response. Path needs to be accessible from inside the cluster and relative to the container’s address, allowing normal URL encoded parameters (as seen the previous exemple).

This action also can be configured to send custom HTTP headers, allowing for example to use authentication tokens.

The action is considered *failed* if there’s no response or if the response is **not** between 200 and 399.

***Note:*** *As you may have noticed, Kubernetes considers redirection codes as success, so keep this in mind when developing your application’s probe endpoint.*

### Shell Command

Another option is to configure the probe to run a **shell command** ([*ExecAction*](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.16/#execaction-v1-core)) which is executed in pod’s shell context and considered failed if the execution returns any result code different from 0 (zero).

```c
<probe-type>:
   exec:
     command:
     - /app/bin/myFantasticConsoleApp.exe
     - param1
     - "param 2"
   initialDelaySeconds: 5
   periodSeconds: 10
   (...)
```

An array of strings is passed through the *command* property and then executed inside pod’s context. The first element is the application path (relative or absolute) and each other element is passed as a command line argument.

***Note:*** *The command does not necessarily needs to call your application. It can simply check if a file has been created, for exemple, with* `*test -f "fileName"*`*.*

### TCP Port Check

The last action that can be performed by a probe is the **TCP port check** ([*TCPSocketAction*](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.16/#tcpsocketaction-v1-core)) which checks if a port in the pod is open. If *kubelet* is able to connect to a specific port, the action is considered successful. As simple as it sounds.

```c
<probe-type>:
   tcpSocket:
     port: 5677
   initialDelaySeconds: 5
   periodSeconds: 10
   (...)
```

In both TCPSocketAction and HttpGetAction we can use named ports instead of a number, but this is subject for another time.

## Probe Types

There are currently three different types of probes in a Kubernetes cluster: *Readiness, Liveness* and *Startup*. Although they have the same properties and behavior, each one is executed in a specific moment with slightly different outcome, and it’s crucial to clearly understand their purpose to optimize usage and avoid problems.

### Readiness Probe

When a new pod is created, its services are **not** immediately registered in cluster’s load balancer and so they’re not allowed to serve external traffic (services running inside the same cluster still can access them). This way Kubernetes can prevent an instance of a service to receive requests when it is still loading or too busy to process them properly. **Readiness probes** are used to check when the containers running in that pod are (guess what?) ready and able to receive external requests.

The most common use of this probe is to check if all dependencies of a pod are available. For example, if your application depends on a database, two other services and a message bus, you could implement a method to verify all these external components are ready. In case of failure, you can even provide different codes and responses for different kinds of fails to track down what component is failing.

However (and here comes a big however) some developers seems to ignore or forget the fact that this probe is not executed only during the startup of a container. It will be repeatedly executed and every time if fails the container will be removed from the list of available services for requests. Thus this probe should not execute long/heavy tasks to avoid overloading services. A busy service also my take longer to execute the probe and return false failures due to timeout.

***Note:*** *I am currently writing another article detailing a solution for this problem using a list of dependencies and it’s current state, distributing dependency checking along the code and making this probe light-speed fast (as soon as I finish it, I will publish the link here).*

### Liveness Probe

Application loaded, all dependencies checked, requests free to come in... but what if the application is dead-locked? The quickest solution would be to make its container to be restarted, which would return the application to it initial healthy state.

For that purpose, Kubernetes provides **Liveness probes**. They work exactly like *Readiness* probes but, in case of failure, it causes the container to be killed and restarted, creating an automatic mechanism for recover applications from an unresponsive state. Needless to say this probe should have an execution interval (*periodSeconds*) short enough to ensure highest availability and also not too short to the point of impacting service performance.

As you notice, in most applications (if not all) this probe is meant to be simple and quick. For a service, for example, an endpoint returning a HTTP OK would do the trick.

Also, avoid long checks for this probe as it may cause false fails due to timeout. This scenario is even worse here than in a Readiness probe because it may cause exactly the opposite of what is expected, as killing and restarting a container is a time consuming operation and doing that to a healthy container is everything we don’t want when speaking of high availability.

### Startup Probe

As from Kubernetes 1.16 a new type of probe is available, the **Startup probe**. From a logic and configuration point of view, Startups and Liveness probes are exactly the same. They have the same properties and in case of fail its container is restarted as well.

If a *Startup* probe is set, after container creation Kubernetes will execute it instead of *Liveness* probe, which will be in a “hold” state. If *Startup* probe succeeds, it is replaced by the *Liveness* probe which will then be executed normally as configured. If the *Startup* probe fails, the pod is restarted and the cycle repeated.

So, if the *Startup* probe has the same logic as *Liveness* and is executed only until it succeed and letting *Liveness* assumes afterwards, why do we need it in the first place? Can’t we just increase the initial delay (*initialDelaySeconds*) for a reasonable time?

Short answer: It depends.

Long answer: Sometimes a bigger initial delay for *Liveness* probe does the trick. Sometimes, to maximize availability, it doesn’t. If you know exactly how long your application needs to become available, go for it! However some applications have long loading periods which can’t be precisely estimated. For example, let’s suppose your application have a lot of tasks during initialization that depend on factors with unpredictable response time, like other applications that may or may not be starting and busy at that moment. How to figure it out the amount of time needed if sometimes it is less than a second and sometimes it may take a minute? If you have a short initial delay, you will cause your container to be wrongly restarted. If you set a large delay, you will have a period where you application may be having problems but there’s no probe to check it.

*Startup* probes sort this out providing a mechanism where you can have a kind of a special *Liveness* probe with different configurations only during the startup. Usually we configure Startup probes with the same values as *Liveness* but a higher tolerance to failure (*failureThreshold*). For example:

```c
startupProbe:
  httpGet:
    path: /probes/liveness
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 18
livenessProbe:
  httpGet:
    path: /probes/liveness
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 3
```

This configuration sets a *Startup* probe to be started 5 seconds after the container creation (*initialDelaySeconds*), and executed every 5 seconds (*periodSeconds*) with a tolerance to fail 18 times (*failureThreshold*). So only after the 18th failure, this probe will cause the container to be restarted.

On the other hand (and here is the trick) as we’re using the default success threshold, as soon as it succeeds this probe is deactivated and the *Liveness* probe starts to be executed, but the later with a more realistic failure threshold of only 3 times.

So packing everything up, now this container have up to 90 seconds to be available at startup but as soon as it becomes available, any problem can be detected in no more than 15 seconds.

### General Overview

For people that likes diagrams (as myself), here’s one to show the execution flow of probes in a Kubernetes cluster:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*B_wvCEbp_DobOXwMAaozjA.png)

Kubernetes probe logic

## Conclusion

Probes are an incredibly easy-to-set and useful native tool in Kubernetes clusters. However, as you brave reader who reached this point may have seen, some situations and caveats need to be taken in consideration when developing and setting up them.

I hope you have enjoyed the article, first one I make in a long time and the very first here in Medium. Any suggestion, corrections or comments, please feel free to shout any time.

[![The Startup](https://miro.medium.com/v2/resize:fill:96:96/1*pKOfOAOvx-fWzfITATgGRg.jpeg)](https://medium.com/swlh?source=post_page---post_publication_info--fef7e030bd2f---------------------------------------)

[![The Startup](https://miro.medium.com/v2/resize:fill:128:128/1*pKOfOAOvx-fWzfITATgGRg.jpeg)](https://medium.com/swlh?source=post_page---post_publication_info--fef7e030bd2f---------------------------------------)

[Last published just now](https://medium.com/swlh/the-more-one-person-ai-businesses-we-build-the-more-risk-we-create-b7d637af0734?source=post_page---post_publication_info--fef7e030bd2f---------------------------------------)

Get smarter at building your thing. Follow to join The Startup’s +8 million monthly readers & +772K followers.

Software engineer lead (currently base in London), book lover, movie maniac, professional TV show marathoner, writer wannabe, among other things…

## More from Ricardo A. and The Startup

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--fef7e030bd2f---------------------------------------)