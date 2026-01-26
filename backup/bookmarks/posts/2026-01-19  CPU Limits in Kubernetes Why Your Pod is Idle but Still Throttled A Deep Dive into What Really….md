---
title: "CPU Limits in Kubernetes: Why Your Pod is Idle but Still Throttled: A Deep Dive into What Really…"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@alexandru.lazarev/cpu-limits-in-kubernetes-why-your-pod-is-idle-but-still-throttled-a-deep-dive-into-what-really-136c0cdd62ff"
author:
  - "[[Alexandru Lazarev]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

***Intro to intro — spoiler:*** *Some time ago I did a big research on this topic and prepared 100+ slides presentation to share knowledge with my teams, below article is a short summary of it but presentation itself I’ve decided making it available publicly, if You are interested in topic — feel free to explore it — it is full of interesting info and references on material. Presentation Link:* [*https://docs.google.com/presentation/d/1WDBbum09LetXHY0krdB5pBd1mCKOU6Tp*](https://docs.google.com/presentation/d/1WDBbum09LetXHY0krdB5pBd1mCKOU6Tp)

**Introduction**

In Kubernetes, setting CPU requests and limits is often considered routine. But beneath this simple-looking configuration lies a complex interaction between Kubernetes, the Linux Kernel, and container runtimes (docker, containerd, or others) — one that can significantly impact application performance, especially under load.

***NOTE****: I guess You already know that your application running in K8s Pods and containers, are ultimately Linux processes running on your underlying Linux Host (K8s Node), isolated and managed by two Kernel features: namespaces and cgroups.*

This article aims to demystify the mechanics of **CPU limits and throttling**, focusing on **cgroups v2 and the Completely Fair Scheduler (CFS)** in modern Linux kernels (*yeah, there are lots of other great articles, but most of them rely on older cgroupsv1*). It also outlines why setting CPU limits — a widely accepted practice — can sometimes do more harm than good, particularly in latency-sensitive systems.

**CPU Requests vs. CPU Limits: Not Just Resource Hints**

· **CPU Requests** are used by the Kubernetes scheduler to place pods on nodes. They act like a **minimum guarantee** and influence **proportional fairness** during CPU contention.

· **CPU Limits**, on the other hand, are enforced by the **Linux Kernel CFS Bandwidth Control** mechanism. They cap the maximum CPU time a container can use within a **100ms quota window** by default (CFS Period).

If a container exceeds its quota within that period, it’s **throttled** — prevented from running until the next window.

**Understanding Throttling in Practice**

Throttling is not a hypothetical concern. It’s very real — and observable.

Take this scenario: a container with cpu.limit = 0.4 tries to run a CPU-bound task requiring 200ms of processing time. This section compares how it will behave with and without CPU Limits:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GG8d7Y1QmYrEG2g3lzBigQ.png)

Figure 1. Example#1 — No CPU Limits. Example Credits to Dave Chiluk (src: https://youtu.be/UE7QX98-kO0 or https://static.sched.com/hosted\_files/kccncna19/dd/Kubecon\_ Throttling.pdf )

Due to the limit, it’s only allowed 40ms every 100ms, resulting in four throttled periods. The task finishes in 440ms instead of 200ms — nearly 2.2x longer.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*jUj3K6Pn8F9sc7ibYngPUQ.png)

Figure 2. Example#1 — With CPU Limits. Example Credits to Dave Chiluk

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*aYg-39QA1wauKxSL3TFN1g.png)

Figure 3. Example#1 — other view and details

This kind of delay can have severe side effects:

· Failed **liveness probes**

· JVM or.NET **garbage collector stalls**, and this may lead to Out-Of-Memory (OOM) case

· Missed heartbeat events

· Accumulated processing queues

==And yet, dashboards may show low average CPU usage, making the root cause elusive.==

**The Linux Side: CFS and Cgroups v2**

The Linux Kernel **Completely Fair Scheduler (CFS)** is responsible for distributing CPU time. When Kubernetes assigns a container to a node:

· Its **CPU Request** is translated into a **CPU weight** (via cpu.weight or cpu.weight.nice in cgroup v2).

· Its **CPU Limit**, if defined, is enforced via cgroupv2 cpu.max, which implements **CFS Bandwidth Control (BWC)**.

Cgroups v2 gives Kubernetes stronger control and hierarchical enforcement of these rules, but also exposes subtleties, especially for **multithreaded applications** or **bursty workloads**.

***Tip***: cgroupsv2 runtime files system resides usually in path /sys/fs/cgroup/ (cgroupv2 root path). To get cgroup name and based on it the full path to its configuration and runtime stats files, you can run “cat /proc/<PID>/cgroup” and get the group name without root part “0::/” and if append it to “/sys/fs/cgroup/” you’ll get the path to all cgroup configurations and runtime stats files, where <PID> is the Process ID from the host machine (not from within the container) of your workload running in Pod and container (can be identified on host with ps or pgrep).

**Example#2: Multithreaded Workload with a Low CPU Limit**

Let’s say you have 10 CPU-bound threads running on 10 cores. Each needs 50ms to finish its job. If you set a **CPU Limit = 2**, the total quota for the container is 200ms per 100ms period.

· In the first 20ms, all threads run and consume 200ms total CPU time.

· Then they are throttled for 80ms — even if the node has many idle CPUs.

· They resume in the next period.

**Result:** Task finishes in 210ms instead of 50ms. Effective CPU usage drops by over 75% since reported CPU Usage may looks misleading. Throughput suffers. Latency increases.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2Owy2dqQ7Ud6IzT_i4avLg.png)

Figure 4. Example#2: 10 parallel tasks, each requiring 50ms CPU Time, each one running on different CPU. No CPU Limits.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*dcK_x1jtpk2_yUjXhaxnmw.png)

Figure 5. 10 parallel tasks, each requiring 50ms CPU Time, each one running on different CPU. CPU Limits = 2.

**Why Throttling May Still Occur Below Requests**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*LzgM1j785gvl30dFaJYPFA.png)

Figure 6. Low CPU Usage but High Throttling

One of the most misunderstood phenomena is seeing **high CPU throttling while CPU usage remains low** — sometimes well below the container’s CPU request.

This is especially common in:

· Applications with **short, periodic bursts** (e.g., every 10–20 seconds or, even, more often — even few spikes within one second, which is relatively long interval vs 100ms — the default CFS Quota period).

· Workloads with **multi-threaded spikes**, such as API gateways or garbage collectors.

· Monitoring windows averaged over long intervals (e.g., 1 minute), which smooth out bursts and hide transient throttling events.

In such cases, your app may be throttled for 25–50% of the time, yet still report CPU usage under 10%.

**Community View: Should You Use CPU Limits?**

This topic remains heavily debated. Here’s a distilled view from real-world experience and industry leaders:

**Viewpoint: Recommendation**

· **Tim Hockin (K8s Maintainer):** In most cases, **don’t set CPU limits**. Use Requests + Autoscaler.

\- [https://x.com/thockin/status/1134193838841401345](https://x.com/thockin/status/1134193838841401345)

\- [https://news.ycombinator.com/item?id=24381813](https://news.ycombinator.com/item?id=24381813)

· **Grafana, Buffer, NetData, SlimStack:** Recommend removing CPU limits, especially for critical workloads.

\- [https://grafana.com/docs/grafana-cloud/monitor-infrastructure/kubernetes-monitoring/optimize-resource-usage/container-requests-limits-cpu/#cpu-limits](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/kubernetes-monitoring/optimize-resource-usage/container-requests-limits-cpu/#cpu-limits)

*And Lots of others links I put in The Presentation.*

**When to Set CPU Limits (and When Not To)**

**When to Set CPU Limits:**

· In **staging environments** for regression and performance tests.

· In **multi-tenant clusters** with strict ResourceQuotas.

· When targeting **Guaranteed QoS class** for eviction protection or CPU pinning.

**When to Avoid CPU Limits *or settling them very carefully and high enough*:**

· For **latency-sensitive apps** (e.g., API gateways, GC-heavy runtimes).

· When workloads are **bursty** or **multi-threaded**.

· If your observability stack doesn’t track time-based throttling properly.

**Observability: Beyond Default Dashboards**

To detect and explain throttling properly, rely on:

- container\_cpu\_cfs\_throttled\_periods\_total / container\_cpu\_cfs\_periods\_total (percentage of throttled periods) — widely adopted period-based throttling KPI, which show frequency of throttling, but not severity.
- container\_cpu\_cfs\_throttled\_seconds\_total — time-based throttling. Focusing more on throttling severity.
- Custom **Grafana dashboards** with 100ms resolution (aligned to CFS Period)?

Also consider using tools like:

- **KEDA** for event-based scaling
- **VPA** and **HPA** for resource tuning and autoscaling
- **Karpenter** (on AWS) for dynamic node provisioning

**Final Thoughts: Limits Shouldn’t Limit You**

Kubernetes provides powerful tools to manage CPU allocation. But misusing them — especially CPU limits — can severely degrade performance, even if the container looks idle in metrics.

Treat CPU limits as **safety valves**, not defaults. Use them **only when necessary** and always base them on **measured behavior**, not guesswork. And if you remove them, **test thoroughly** under real-world traffic and load.

**What’s Next?**

An eventual follow-up article will explore specific cases where **CPU usage is low, but throttling is high**, and what to do about it. Expect visualizations, PromQL patterns, and tuning techniques for better observability and performance.

***P.S.*** *It is my first (more) serios publication, so any comments, feedback and criticism are welcome.*

*cross-posted on:* [*https://www.linkedin.com/pulse/cpu-limits-kubernetes-why-your-pod-idle-still-deep-dive-lazarev-k3m7f*](https://www.linkedin.com/pulse/cpu-limits-kubernetes-why-your-pod-idle-still-deep-dive-lazarev-k3m7f)

Java Dev I like PostgreSQL, and started liking K8s and Linux Kernel:)

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--136c0cdd62ff---------------------------------------)