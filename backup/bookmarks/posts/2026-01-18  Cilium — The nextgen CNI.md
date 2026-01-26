---
title: "Cilium — The nextgen CNI"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@ksushants/cilium-the-nextgen-cni-adbf4c2af24d"
author:
  - "[[sushant kode]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Cilium is an open source, cloud native solution for providing, securing, and observing network connectivity between workloads, based on kernel technology eBPF.

### what is eBPF?

eBPF (Extended Berkeley Packet Filter) programs hook into the Linux network datapath and can be used to take actions like dropping packets based on network policy rules, right as the packet enters the network socket. In simpler terms ‘W *hat javascript is to the browser, eBPF is to the linux kernel* ’. eBPF makes the Linux kernel programmable, so that applications like Cilium can hook into Linux kernel subsystems, bringing user space application context to kernel operations.

### What is Cilium?

Cilium is an open source CNI-compatible networking and security layer for Kubernetes, Mesos, and Docker that does just that. From inception, Cilium was designed for large-scale, highly-dynamic containerized environments. It natively understands container identity and parses API protocols like HTTP, gRPC, and Kafka, providing visibility and security that is both simpler and more powerful than a traditional firewall. And the power of BPF enables highly efficient in-kernel data forwarding, delivering huge performance wins for common microservices use cases like service-based load-balancing in Kubernetes or the insertion of local proxies for a “service mesh” like Istio.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QWkuYS359RCrAQZDR4KbMA.png)

### Cilium capabilities

1. **Networking**

Cilium implements a simple flat Layer 3 network, with the ability to span multiple clusters connecting all application containers.  
By default, Cilium supports an **overlay** networking model, where a virtual network spans all hosts. Traffic in an overlay network is encapsulated for transport between different hosts.  
Cilium also offers the option of a **native routing** networking model, using the regular routing table on each host to route traffic to pod (or external) IP addresses. This mode is for advanced users and requires some awareness of the underlying networking infrastructure

2\. **Identity-aware Network Policy Enforcement**

Cilium assigns an **identity to groups of application containers** based on relevant metadata such as Kubernetes labels. The identity is then associated with all network packets emitted by the application containers, allowing eBPF programs to efficiently validate the identity at the receiving node — without the use of any Linux firewall rules.  
While traditional firewalls operate at Layer 3 and 4, Cilium also has the ability to secure modern Layer 7 application protocols such as REST/HTTP, gRPC, and Kafka.

3\. **Transparent Encryption**

Cilium supports simple-to-configure transparent encryption, using IPSec or WireGuard, that when enabled secures traffic between nodes without requiring reconfiguring any workload.

4\. **Multi-cluster Networking**

Cilium’s Cluster Mesh capabilities make it easy for workloads to communicate with services hosted in different Kubernetes clusters

5\. **Load Balancing**

Cilium implements distributed load balancing for traffic between application containers and external services. Load balancing is implemented in eBPF using efficient hash tables allowing for almost unlimited scale.

6\. **Enhanced Network Observability**

Cilium includes a dedicated network observability component called Hubble.

Hubble provides:

1. Visibility into network traffic at Layer 3/4 (IP address and port) and Layer 7 (API Protocol)
2. Event monitoring with metadata: When a packet is dropped, the tool doesn’t just report the source and destination IP of the packet, it also provides the full label information of both the sender and receiver among a lot of other information
3. Configurable Prometheus metrics exports
4. A graphical UI to visualize the network traffic flowing through your clusters

## More from sushant kode

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--adbf4c2af24d---------------------------------------)