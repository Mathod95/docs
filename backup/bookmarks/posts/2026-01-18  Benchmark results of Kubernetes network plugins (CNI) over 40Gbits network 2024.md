---
title: "Benchmark results of Kubernetes network plugins (CNI) over 40Gbit/s network [2024]"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/benchmark-results-of-kubernetes-network-plugins-cni-over-40gbit-s-network-2024-156f085a5e4e"
author:
  - "[[Alexis Ducastel]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-156f085a5e4e---------------------------------------)

This article is a new run of my previous benchmark ([2020](https://itnext.io/benchmark-results-of-kubernetes-network-plugins-cni-over-10gbit-s-network-updated-august-2020-6e1b757b9e49), [2019](https://itnext.io/benchmark-results-of-kubernetes-network-plugins-cni-over-10gbit-s-network-updated-april-2019-4a9886efe9c4) and [2018](https://itnext.io/benchmark-results-of-kubernetes-network-plugins-cni-over-10gbit-s-network-36475925a560)), now running Kubernetes 1.26 and Ubuntu 22.04 with CNI version up-to-date in January 2024.

## Summary

**1) Benchmark Context**  
1.1) Selecting the CNIs  
1.2) Benchmark Protocol  
1.3) The Leap from 10Gbit to 40Gbit Networking  
1.4) Monitoring with statexec by BlackSwift  
**2) Benchmark results**  
2.1) Raw results exhaustivity and self-service exploration  
2.2) Example of raw data for test DTM (Direct TCP Multistream)  
2.3) Extracting Insights from Raw Data  
2.4) Stop talking, show me results  
**3) Interpretations**  
3.1) Reliability of tests  
3.2) Global performance  
3.3) Impact of eBPF  
3.4) Pursuing Efficiency, the path to Sustainable Computing?  
3.5) UDP drawback and concerns about HTTPv3  
3.6) The Case of Calico VPP  
3.7) Choosing the Right Network Encryption Protocol  
**4) Conclusion / TL;DR: Which CNI to choose?**

## 1) Benchmark Context

### 1.1) Selecting the CNIs

In the vast sea of 33 Container Network Interfaces *(CNIs)* available for Kubernetes, we narrowed our focus down to just seven. The criteria for inclusion in this year’s benchmark were stringent, aiming to ensure relevance and applicability across a wide range of environments.

To qualify, a CNI:  
\- must be actively maintained, evidenced by at least one commit in the past 12 months.  
\- must be independent of cloud-specific or hardware-specific *(Azure CNI, Cisco ACI, …)*  
\- must not be a meta-CNIs *(Ex: Multus, Spiderpool, …)*  
\- must support network policies *(While optional for use, it’s essential to have the capability available in 2024)*  
\- must be straightforward to install using standard Kubernetes commands

We decided to include the Flannel CNI in our benchmark despite it not meeting all of our prerequisites, particularly regarding Network Policies. This inclusion is strictly for comparative purposes, offering a clear reference point to gauge how other, more feature-rich CNIs stack up against a straightforward, connectivity-focused option like Flannel.

For each selected CNI *(*[*selection tab on benchmark spreadsheet*](https://docs.google.com/spreadsheets/d/1ohJL-HElbGvMnL1meAB9a_0EsrXbAulvn-13kv208J8/edit#gid=0)*)*, we delved into various configurations as outlined in their respective documentation. These configurations included enabling traffic encryption with WireGuard, or replacing kube-proxy with eBPF, among others. Altogether, we tested 21 different CNI variants in our benchmark. *(*[*variants tab on benchmark spreadsheet*](https://docs.google.com/spreadsheets/d/1ohJL-HElbGvMnL1meAB9a_0EsrXbAulvn-13kv208J8/edit#gid=1792314631)*)*

Here are the 7 selected CNIs along with their variants, totaling 21 configurations:

- **Antrea v1.15.0**  
	Variants: Default / No encapsulation / IPsec / Wireguard
- **Calico v3.27.2**  
	Variants: Default / eBPF / Wireguard / eBPF+Wireguard / VPP / VPP IPsec / VPP Wireguard
- **Canal v3.27.2**  
	Variants: Default
- **Cilium v1.15.2**  
	Variants: Default / with Hubble / No hubble / No kubeproxy / IPsec / Wireguard
- **Kube-OVN v1.12.8  
	**Variants: Default
- **Kube-router v2.1.0  
	**Variants: Default / All features

### 1.2) Benchmark Protocol

Our testing ground was a setup of three Supermicro bare-metal servers interconnected through a Supermicro 40Gbit switch. The servers were linked to the switch using passive DAC SFP+ cables and configured within the same VLAN, with jumbo frames enabled aka MTU 9000. *(More details on hardware and software version in* [*context tab of benchmark spreadsheet*](https://docs.google.com/spreadsheets/d/1ohJL-HElbGvMnL1meAB9a_0EsrXbAulvn-13kv208J8/edit#gid=1057550285)*)*

To closely mimic real-world conditions in our CNI evaluation, we consciously decided against extensive system tuning. The only modifications we made were the installation of WireGuard — to ensure the module was available for CNIs that might leverage it — and the activation of Jumbo Frames on the network interfaces. Beyond these adjustments, the servers ran with the default Ubuntu 22.04 kernel and were essentially “out-of-the-box.”

This approach was taken to ensure that our benchmark results would be as relevant and applicable as possible to a wide range of Kubernetes users. By avoiding specialized system optimizations, we aimed to present a clear picture of how each CNI performs under typical conditions, providing valuable insights to users who may not have the resources or expertise to engage in extensive system tuning.

We deployed Kubernetes version 1.26.12 via the [RKE2](https://docs.rke2.io/) distribution on Ubuntu 22.04. To enhance reproducibility, we adopted a consistent setup: the Kubernetes control plane was always situated on the first node (a1), the benchmark server component on the second server (a2), and the client part on the third (a3). Pods were statically assigned to nodes using the “nodeName” attribute.

![](https://miro.medium.com/v2/resize:fit:640/1*y8HFT3UipwNkwLx3zseJhQ.png)

Benchmark architecture

Each CNI variant underwent three test runs, with servers being reinstalled and the cluster redeployed for each run. A single run, lasting about 30 minutes, encompassed 12 steps with 9 distinct tests:

- \[prepare\] Deployment of nodes, installation of Kubernetes, and CNI setup
- \[info\] Information gathering, such as collecting MTU data of interfaces
- \[idle\] Idle performance measurement to gauge the CPU and memory overhead post-CNI installation
- \[dts\] **D** irect pod-to-pod **T** CP bandwidth with a **S** ingle stream
- \[dtm\] **D** irect pod-to-pod **T** CP bandwidth with **M** ultiple streams (8)
- \[dus\] **D** irect pod-to-pod **U** DP bandwidth with a **S** ingle stream
- \[dum\] **D** irect pod-to-pod **U** DP bandwidth with **M** ultiple streams (8)
- \[sts\] Pod to **S** ervice **T** CP bandwidth with a **S** ingle stream
- \[stm\] Pod to **S** ervice **T** CP bandwidth with **M** ultiple streams (8)
- \[sus\] Pod to **S** ervice **U** DP bandwidth with a **S** ingle stream
- \[sum\] Pod to **S** ervice **U** DP bandwidth with **M** ultiple streams (8)
- \[teardown\] Deinstallation of all nodes and Kubernetes cluster

This protocol was designed to provide a comprehensive view of each CNI’s performance, reliability, and resource consumption, setting the stage for insightful comparisons and conclusions.

### 1.3) The Leap from 10Gbit to 40Gbit Networking

Our journey through CNI benchmarking has seen a significant evolution, moving from older 10Gbit equipment and single-processor servers (Intel Xeon CPU E5–1630 v3) to a more modern setup capable of 40Gbit testing. This upgrade included transitioning to newer processors (AMD EPYC 7262), NVMe storage, and other enhancements, fundamentally changing the landscape of our benchmarks.

In the realm of network performance, a single-threaded process can manage a 10Gbit/s throughput without breaking a sweat. However, the challenge intensifies at 40Gbit/s. Our tool of choice for measuring performance, “iperf3,” is inherently single-threaded and, on a CPU with a clock speed over 3.5Ghz, it reaches its limits at around 20Gbits to 30Gbits in a single stream scenario. This limitation meant that the measurement tool itself became a bottleneck in our benchmarks. Thankfully, with the release of in December 2023, which supports multi-stream measurements, we were able to overcome this hurdle by utilizing this specific version instead of the one available in the official Ubuntu repositories.

Another notable impact of our hardware upgrade is the introduction of dual-CPU servers. With the network card connected via PCI-Express to one of the two CPUs, processes running on the other CPU face a disadvantage when generating high network traffic. While it’s possible to bind processes to the correct NUMA node (effectively tying them to the right processor), ensuring that the entire processing chain — iperf3, CNI-related processes, NIC drivers, etc. — resides on the same node would require system tuning. Again, to mirror real-world production workloads as closely as possible, we opted not to perform such tuning, allowing processes to be scheduled freely across processors.

By running iperf3 with 8 parallel streams, we effectively circumvent the bandwidth limitations of a single CPU core (though just 2 streams would suffice for this purpose) and increase the likelihood that at least two iperf3 processes are executed on the optimal NUMA node (the one connected to the network card). This setup enabled us to push the network card to its limit, achieving a cumulative bandwidth of ~40Gbit/s.

This strategic approach not only highlights the capabilities of our upgraded lab but also ensures that our benchmarks accurately reflect the performance users can expect in real-world, production environments without extensive system optimizations.

### 1.4) Monitoring with statexec by BlackSwift

Monitoring a Kubernetes cluster has become commonplace, but the unique nature of our benchmark introduces several implications for monitoring:

- Given that tests last about one minute, it is crucial to achieve second-level granularity in metric collection.
- The high network loads generated by the benchmark can significantly disrupt metric collection processes that rely on network transmissions, such as Prometheus scraping node-exporters on cluster nodes.
- It is essential to minimize the resource overhead of monitoring (CPU, memory, disk usage, etc.) to avoid influencing the benchmark results.

BlackSwift, a french company specializing in Kubernetes and providing Kubernetes namespaces as a service, faces similar challenges in their R&D as they evaluate lots of technologies for their products. Together, we have developed a utility called “ [statexec](https://github.com/blackswifthosting/statexec) ” that captures system metrics during the execution of a specified command and exports these metrics in the OpenMetrics format for integration into systems like Victoria Metrics, Prometheus, or similar. This tool, written in Go, is standalone with no external dependencies, consumes minimal resources, and includes features such as second-level granularity, full in-memory system metrics gathering, and command synchronization which is particularly useful for network tests requiring sequential server and client starts. The utility comes with a containerized stack based on Docker-compose featuring Grafana and a Victoria Metrics database, to facilitate the exploration of the collected metrics.

![](https://miro.medium.com/v2/resize:fit:640/0*tFxBe8VPSeuBWynk.png)

Example of statexec dashboard for a “wget” command

For more information, see [https://github.com/blackswifthosting/statexec](https://github.com/blackswifthosting/statexec)

## 2) Benchmark results

### 2.1) Raw results exhaustivity and self-service exploration

The volume of data generated during this benchmark is substantial, and to aid understanding and interpretation without overwhelming readers, we have chosen to present the graphs in a streamlined manner. Including every chart in full within this article would be counterproductive. To give an example, we will showcase the results from the “DTM” test (Direct pod-to-pod TCP bandwidth with multiple streams (8)) for illustrative purposes, and we invite the curious reader to independently explore the complete raw data through our Git repository. All the data and dashboards used in this article are published open-source and are accessible to anyone. The only prerequisites are having Docker and Docker-compose installed on your machine, along with a minimum of 10GB of free space.

To access the data, follow these instructions:

```c
# Clone the repo to retrieve all benchmark data (~8GB)
git clone https://github.com/InfraBuilder/benchmark-k8s-cni-2024-01.git
cd benchmark-k8s-cni-2024-01

# start docker-compose stack and import data in victoria metrics
# then open grafana UI on default dashboard
make results
```

You can then use the following dashboards to delve into the data:

- All CNI Summary: [http://localhost:3000/d/benchmark-results/benchmark-results](http://localhost:3000/d/benchmark-results/benchmark-results)
- Side-to-Side Comparison: [http://localhost:3000/d/benchmark-results/benchmark](http://localhost:3000/d/benchmark-results/benchmark)

These resources provide a comprehensive view of the performance landscape across different CNIs, allowing for detailed analysis and comparisons.

### 2.2) Example of raw data for test DTM (Direct TCP Multistream)

Here is a screenshot of the dashboard with raw data for each CNI:

![](https://miro.medium.com/v2/resize:fit:640/1*IBICGHAOdInwh2g2zHsxaQ.png)

Dashboard screenshot of raw results for test DTM

### 2.3) Extracting Insights from Raw Data

During the initial phases of exploring the data generated by the benchmark, we started by comparing the absolute values of each metric: bandwidth, CPU usage, and memory consumption, among others. Surprisingly, we observed that CNIs implementing encryption often consumed less CPU than their non-encrypted, bare-metal counterparts, a finding that is counterintuitive. While one might speculate that advancements in cryptographic hardware offloading could explain the reduced CPU impact, this was not the case. Encrypted CNIs showed significantly lower performance and achieved reduced bandwidths, which in turn required less CPU capacity to manage the decreased data flow. To better interpret CPU consumption relative to bandwidth performance, we introduced a “CPU efficiency” metric, defined as the amount of CPU used (in mCPU) divided by the bandwidth achieved (in Gbit/s). This provides a proportional representation of a CNI’s efficiency relative to its performance output.

Regarding memory usage, we noted that the amount of RAM consumed by a CNI did not correlate with the bandwidth it handled. Memory usage curves were flat across different loads, indicating no need to adjust memory usage relative to bandwidth as we did with CPU. Instead, we calculated the memory overhead compared to bare-metal, which allowed for a more accurate comparison of the impact CNIs have on system resources.

Here is an example graph illustrating the resource efficiency of CNIs, with memory overhead relative to bare-metal on the x-axis and “CPU efficiency” on the y-axis. The closer a CNI is to the origin, the more “lightweight” and efficient it is; conversely, higher values indicate greater CPU or memory consumption for equivalent bandwidth.

![](https://miro.medium.com/v2/resize:fit:640/1*qnmqpVZogFvGzhe5WQjcSQ.png)

Resource efficiency per CNI for test DTM

### 2.4) Stop talking, show me results

2.4.1) \[dts\] **D** irect pod-to-pod **T** CP bandwidth with a **S** ingle stream

![](https://miro.medium.com/v2/resize:fit:640/1*M5454WcyIFgmHZ6yX0ISRA.png)

Result for test \[dts\] D irect pod-to-pod T CP bandwidth with a S ingle stream

2.4.2) \[dtm\] **D** irect pod-to-pod **T** CP bandwidth with **M** ultiple streams (8)

![](https://miro.medium.com/v2/resize:fit:640/1*P8OqLMFs8pTGn0SOCYOYUg.png)

Result for test \[dtm\] D irect pod-to-pod T CP bandwidth with M ultiple streams (8)

2.4.3) \[dus\] **D** irect pod-to-pod **U** DP bandwidth with a **S** ingle stream

*Note: Yes, kube-router and antrea did better than baremetal, it was not expected, but, see section “3.1” for more information.*

![](https://miro.medium.com/v2/resize:fit:640/1*s7ois_RXnqZTZLYHH1LJpQ.png)

Result for test \[dus\] D irect pod-to-pod U DP bandwidth with a S ingle stream

2.4.4) \[dum\] **D** irect pod-to-pod **U** DP bandwidth with **M** ultiple streams (8)

![](https://miro.medium.com/v2/resize:fit:640/1*3XiPEGRDm-RWOMX3AMqkPg.png)

Result for test \[dum\] D irect pod-to-pod U DP bandwidth with M ultiple streams (8)

2.4.5) \[sts\] Pod to **S** ervice **T** CP bandwidth with a **S** ingle stream

![](https://miro.medium.com/v2/resize:fit:640/1*fpxQVnqj9HwQ8pTwPk189w.png)

Result for test \[sts\] Pod to S ervice T CP bandwidth with a ingle stream

2.4.6) \[stm\] Pod to **S** ervice **T** CP bandwidth with **M** ultiple streams (8)

![](https://miro.medium.com/v2/resize:fit:640/1*Q7OYeUkGhMfYiXpeJY0zxw.png)

Results for test \[stm\] Pod to S ervice T CP bandwidth with M ultiple streams (8)

2.4.7) \[sus\] Pod to **S** ervice **U** DP bandwidth with a **S** ingle stream

*Note: Yes, again kube-router and antrea did better than baremetal, it was not expected, but, see section “3.1” for more information.*

![](https://miro.medium.com/v2/resize:fit:640/1*JTmEK_TTtEMwph7KR5mMxA.png)

Results for test \[sus\] Pod to S ervice U DP bandwidth with a ingle stream

2.4.8) \[sum\] Pod to **S** ervice **U** DP bandwidth with **M** ultiple streams (8)

![](https://miro.medium.com/v2/resize:fit:640/1*djhAjzp31QEQCauve9vP_Q.png)

Results for test \[sum\] Pod to S ervice U DP bandwidth with M ultiple streams (8)

## 3) Interpretations

*Disclaimer: This section is subjective and represents our interpretation of the results. We encourage you to explore the raw results for yourself (refer to section “2.1”) and form your own conclusions.*

### 3.1) Reliability of tests

The reliability of single stream tests like “dts” (direct TCP single stream), “dus” (direct UDP single stream), “sts” (service-to-pod TCP single stream), and “sus” (service-to-pod UDP single stream) is somewhat compromised. The performance of single-threaded iperf3 heavily relies on the luck of being scheduled on the appropriate NUMA node, similar to the network drivers. In contrast, tests “dtm” (direct TCP multiple streams), “dum” (direct UDP multiple streams), “stm” (service-to-pod TCP multiple streams), and “sum” (service-to-pod UDP multiple streams) provide more reliable insights due to their use of eight processes, which increases the likelihood of optimal CPU core scheduling (see section 1.3).

### 3.2) Global performance

In our comprehensive benchmark analysis, it’s evident that the overall performance of Container Network Interfaces (CNIs) has reached a level where the distinctions in raw performance metrics between different implementations are minimal. This high level of efficiency across the board indicates that, as of now, performance alone is no longer a critical differentiating factor when selecting a CNI.

### 3.3) Impact of eBPF

eBPF has shown slightly better performance in TCP multi-stream scenarios, which may more closely represent the majority of real-world workloads — characterized by numerous containers simultaneously processing traffic across multiple processes and cores.

Remind that this benchmark is focus on a single workload, eBPF benefits will come more with lots of workloads and with increasing number of services in the cluster.

### 3.4) Pursuing Efficiency, the path to Sustainable Computing?

In the TCP multi-stream tests, all CNIs showed strong performance, and their developers deserve congratulations for their robust work.

Nevertheless, there is ample room for improvement in efficiency, specifically regarding resource consumption per unit of bandwidth. As Green IT and decarbonized data centers become increasingly important, enhancing efficiency not only supports environmental sustainability but also reduces the need for servers and the overall energy consumption.

Below, we present a clustering of CNIs based on their efficiency as illustrated in the accompanying chart:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*JoN-fag4InHrYL2mR6pX-g.png)

### 3.5) UDP drawbacks and concerns about HTTPv3

UDP performance across the board was disappointing. UDP scenarios typically showed lower bandwidth and more variable results, mainly due to the absence of hardware offloading for UDP at the NIC level, unlike TCP. This raises significant concerns about the adoption of HTTP/3 (HTTP over QUIC, an UDP-based protocol). As HTTP/3 gains traction, potentially extending to ingress controllers, it could pose serious performance and reliability issues, especially given the high drop rates of UDP at elevated bandwidths.

### 3.6) The Case of Calico VPP

During this benchmark, Calico VPP displayed performances that were below expectations. This shortfall is largely due to its need for meticulous tuning of both software and hardware configurations, which was beyond the scope of this benchmark. Calico VPP (Vector Packet Processor, a high-performance user-space dataplane) was almost excluded from the benchmark due to the complexity of its setup. However, it should be noted that since the last benchmark in 2020, there have been significant improvements in simplifying the installation process. Unfortunately, while installation has become easier, it alone is insufficient to fully leverage the capabilities of the hardware at your disposal. If you are considering deploying Calico VPP, it is advisable to consult closely with the teams responsible for its development to achieve optimal results.

### 3.7) Choosing the Right Network Encryption Protocol

The benchmark results indicate that WireGuard can outperform IPsec in terms of efficiency. While WireGuard offers superior performance, it’s important to note that unlike IPsec — where encryption key rotations can be easily managed (as seen with solutions like Cilium) — WireGuard does not support this feature. The choice between these protocols should therefore be guided by your specific security policies and performance requirements. If key rotation is critical for your security strategy, IPsec might be the more appropriate choice despite its slight performance disadvantage.

## 4) Conclusion / TL;DR: Which CNI to choose?

Disclaimer: This section is highly subjective and reflects our personal recommendations. Please consider these suggestions as friendly advice rather than universal truths.

- For **Low-Resource Clusters** (e.g., Edge Environments):  
	**Kube-router** is our top recommendation! It’s exceptionally lightweight, efficient, and performs well across all tested scenarios. Importantly, it offers Network Policies out-of-the-box and supports a wide range of architectures (amd64, arm64, riscv64, etc.), which are crucial for edge computing. Kube-router can be likened to Flannel but with Network Policies, or Canal but more efficient. While it lacks numerous advanced features, its design philosophy emphasizes “operational simplicity and high performance.” One concern is its need for more maintainers, although the current team is responsive. If this issue is a significant concern, consider Flannel or Canal as alternatives.
- For **Standard Clusters**:  
	**Cilium** stands out as the primary choice, followed by Calico or Antrea. Currently, all CNIs offer respectable performance and handle MTU discovery effectively, which means raw performance need not be the primary decision factor. We recommend focusing on CNIs that provide valuable features such as a CLI for troubleshooting and configuration, eBPF-based kube-proxy replacement, observability tools, comprehensive documentation, and Layer 7 policies. Cilium impresses with its feature-rich open-source version and significantly reduced resource footprint since our last benchmark four years ago. Calico, while robust, lacks certain features in its open-source variant that are only available in its enterprise version (Tigera). Antrea is rapidly evolving, incorporating many appealing features and is definitely one to watch.
- For **Fine-Tuned Clusters**:  
	If you require a highly optimized CNI, you likely have the expertise to make an informed choice without this guide. Based on our readings and discussions with CNI maintainers at events like KubeCon, Calico VPP could be a compelling option if you can extensively fine-tune both hardware (NICs, network fabric, motherboards, processors, etc.) and software (operating systems, drivers, etc.). Collaborating with the Calico VPP team might yield a high-performance network capable of managing substantial volumes of encrypted traffic efficiently. Here is an [Intel-led benchmark](https://networkbuilders.intel.com/solutionslibrary/intel-data-streaming-accelerator-intel-dsa-calico-vpp-multinet-with-intel-dsa-on-4th-gen-intel-xeon-scalable-processor-technology-guide) showcasing VPP’s capability to handle 100Gbits. *Again, you may see that not everyone is having such fine-tuned system, with servers as big as having nodes with 2 X Intel® Xeon® Platinum 8480C (56 cores, 112 thread, 350W TDP per CPU), over 100Gbit/s fabric.*

This summary provides a snapshot of suitable CNIs based on different use cases and requirements. Your final choice should align with your specific needs and the technical capabilities of your environment.

Repo: [https://github.com/InfraBuilder/benchmark-k8s-cni-2024-01/](https://github.com/InfraBuilder/benchmark-k8s-cni-2024-01/)

X: [twitter.com/BlackSwiftFR](https://twitter.com/BlackSwiftFR) — [twitter.com/infraBuilder](https://twitter.com/infraBuilder)

Web: [www.BlackSwift.fr](https://www.blackswift.fr/) — [www.infraBuilder.com](https://www.infrabuilder.com/)

*P.S: We extend our sincere thanks to the developers and community members behind the CNIs, included or not in our benchmark, for their invaluable collaboration and insights. Special thanks go to:*

- ***Antrea:*** *Antonin Bas, Quan Tian, Wenying Dong*
- ***Calico:*** *Lance Robson, Matt Dupre, Reza Ramezanpour, Tomas Hruby, Shaun Crampton*
- ***Calico VPP:*** *Jerome Tollet, Onong Tayeng, Hedi Bouattour, Nathan Skrzypczak*
- ***Cilium:*** *Daniel Borkmann, Marcel Zięba, Ryan Drew*
- ***Kube-router:*** *Aaron U’Ren*
- ***Spiderpool:*** *Cyclinder Kuo*

*Your interactions, assistance in understanding the results, and feedback have been crucial to the success of this benchmarking effort. Thank you all for your dedication and support!*

infraBuilder founder, BlackSwift founder, Kubernetes CKA and CKAD, devops meetup organizer, member of Build-and-Run group.

## More from Alexis Ducastel and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--156f085a5e4e---------------------------------------)