---
title: "Part 2: eBPF Map Metrics Prometheus Exporter"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/all-things-ebpf/part-2-ebpf-map-metrics-prometheus-exporter-fd2e3f12239a"
author:
  - "[[TJ. Podobnik]]"
  - "[[@dorkamotorka]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)## [eBPFChirp Blog](https://medium.com/all-things-ebpf?source=post_page---publication_nav-8b7b84adce05-fd2e3f12239a---------------------------------------)

[![eBPFChirp Blog](https://miro.medium.com/v2/resize:fill:76:76/1*Nw7KgVn0o4za9sPfZcRcJQ.png)](https://medium.com/all-things-ebpf?source=post_page---post_publication_sidebar-8b7b84adce05-fd2e3f12239a---------------------------------------)

Explore the cutting-edge world of eBPF in our Medium publication, where we dive deep into its capabilities, advancements, and practical applications. From kernel innovations to complex network monitoring, discover how eBPF is transforming the tech landscape.

This post follows up on my previous attempt to develop a standalone eBPF Map Metrics exporter, which initially failed.## [eBPF Map Metrics Prometheus Exporter](https://cloudchirp.medium.com/ebpf-map-metrics-prometheus-exporter-3e9be5f3f568?source=post_page-----fd2e3f12239a---------------------------------------)

Observability of eBPF Maps and Prometheus

cloudchirp.medium.com

[View original](https://cloudchirp.medium.com/ebpf-map-metrics-prometheus-exporter-3e9be5f3f568?source=post_page-----fd2e3f12239a---------------------------------------)

Fortunately, after sharing my struggles, Anton from Isovalent reached out to me with a recent patch to the Linux Kernel that addressed my issues.

In this blog post, we’ll discuss eBPF Iterators and the solution for exporting eBPF Map metrics without altering your application stack.

## eBPF Iterators

The advice Anton gave me revolved around using eBPF Iterators. To be quite honest with you, I had seen this feature in the past but didn’t have time to delve deeper into it, so it was just another thing that ended up on my (already long) TODO list.

> **So, what is an eBPF Iterator?**

An eBPF Iterator is a type of eBPF program that allows users to iterate over specific types of kernel data structures by defining callback functions that are executed for every entry in various kernel structures.

For instance, users can create a BPF iterator to traverse all tasks on the system and report the total CPU runtime used by each task. Alternatively, another BPF iterator could be configured to provide cgroup information for each task.

> **Wait, what?**

You can think of it as an eBPF function triggered from user space, whose return value is crafted in the kernel context and retrieved into user space. This is obviously a big abstraction, but it’s meant to illustrate my point.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rCMk-bm3qZNwnb2YxfSkyA.png)

At the moment, there aren’t many resources about eBPF iterators, but if you are a developer and want to get hands-on experience, I think [Linux documentation](https://docs.kernel.org/bpf/bpf_iterators.html#) and [kernel selftests](https://github.com/torvalds/linux/tree/master/tools/testing/selftests/bpf/progs) are great places to learn how to use the BPF iterator.

## eBPF Map Metrics Exporter

With knowledge of eBPF Iterators, the solution becomes straightforward. Here’s the implementation with added comments for clarity.

- Kernel Space program:
```rb
//go:build ignore
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>

// kfunc Function to sum up the element count in an eBPF map, marked as a kernel symbol.
__s64 bpf_map_sum_elem_count(struct bpf_map *map) __ksym;

// Section definition for the eBPF iterator.
SEC("iter/bpf_map")
int dump_bpf_map(struct bpf_iter__bpf_map *ctx) {
    // Get the sequence file and sequence number from the context.
    struct seq_file *seq = ctx->meta->seq;
    __u64 seq_num = ctx->meta->seq_num;
    struct bpf_map *map = ctx->map;

    // If the map is null, return 0 to indicate no processing.
    if (!map) {
        return 0;
    }

    // Print the map's ID, name, maximum entries, and current element count to the sequence file.
    BPF_SEQ_PRINTF(seq, "%4u %-16s %10d %10lld\n",
                   map->id, map->name, map->max_entries,
                   bpf_map_sum_elem_count(map));

    // Return 0 to indicate successful execution.
    return 0;
}

// Define the license for the eBPF program as GPL.
char _license[] SEC("license") = "GPL";
```
- User Space Program:
```rb
package main

//go:generate go run github.com/cilium/ebpf/cmd/bpf2go count count.c

import (
 "bufio"
 "fmt"
 "log"
 "net/http"
 "time"

 "github.com/cilium/ebpf/link"
 "github.com/cilium/ebpf/rlimit"
 "github.com/prometheus/client_golang/prometheus"
 "github.com/prometheus/client_golang/prometheus/promhttp"
)

const (
 UPDATE_INTERVAL = 1 // sec
)

var (
 // Gauge metric to track the current number of elements in eBPF maps
 mapElemCountGauge = prometheus.NewGaugeVec(
  prometheus.GaugeOpts{
   Name: "ebpf_map_curr_elem_count",
   Help: "Current number of elements in eBPF maps, labeled by map ID and name",
  },
  []string{"id", "name"},
 )

 // Gauge metric to track the pressure of eBPF maps (current elements / max elements)
 mapPressureGauge = prometheus.NewGaugeVec(
  prometheus.GaugeOpts{
   Name: "ebpf_map_pressure",
   Help: "Current pressure of eBPF maps (currElements / maxElements), labeled by map ID and name",
  },
  []string{"id", "name"},
 )
)

func main() {
 // Create a new Prometheus registry and register the metrics
 reg := prometheus.NewRegistry()
 reg.MustRegister(mapElemCountGauge)
 reg.MustRegister(mapPressureGauge)

 // Remove the memlock limit to allow eBPF to allocate memory
 if err := rlimit.RemoveMemlock(); err != nil {
  log.Fatalf("Failed to remove memlock limit: %v", err)
 }

 // Load eBPF objects from the generated count.c code
 objs := countObjects{}
 if err := loadCountObjects(&objs, nil); err != nil {
  log.Fatalf("Failed to load objects: %v", err)
 }
 defer objs.Close()

 // Attach the eBPF program to the Iterator hook
 iterLink, err := link.AttachIter(link.IterOptions{
  Program: objs.DumpBpfMap,
 })
 if err != nil {
  log.Fatalf("Failed to attach eBPF program: %v", err)
 }
 defer iterLink.Close()
 log.Println("eBPF program attached successfully.")

 // Start HTTP server for Prometheus metrics
 handler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
 http.Handle("/metrics", handler)
 go func() {
  log.Fatal(http.ListenAndServe(":2112", nil))
 }()
 log.Println("Prometheus HTTP server started on :2112")

 // Keep the program running indefinitely, updating metrics at intervals
 for {
  time.Sleep(UPDATE_INTERVAL * time.Second)
  reader, err := iterLink.Open()
  if err != nil {
   log.Fatalf("Failed to open BPF iterator: %v", err)
  }
  defer reader.Close()

  scanner := bufio.NewScanner(reader)
  for scanner.Scan() {
   // Variables to store the parsed values
   var id int
   var name string
   var maxElements int
   var currElements int64

   // Parse the line from the BPF iterator
   line := scanner.Text()
   length, err := fmt.Sscanf(line, "%4d %s %10d %10d", &id, &name, &maxElements, &currElements)
   if err != nil || length != 4 {
    log.Fatal(err)
   }

   // Update the metrics
   idStr := fmt.Sprintf("%d", id)
   mapElemCountGauge.WithLabelValues(idStr, name).Set(float64(currElements))
   mapPressureGauge.WithLabelValues(idStr, name).Set(float64(currElements) / float64(maxElements))
  }

  // Check for scanner errors
  if err := scanner.Err(); err != nil {
   log.Fatal(err)
  }
 }
}
```

In traditional tracing programs, a user space application activates the program by obtaining a `**bpf_link**` through `**bpf_program__attach()**`. Once activated, the program's callback is triggered whenever the associated tracepoint is hit in the kernel. In contrast, for BPF iterator programs, you obtain a `**bpf_link**` using `**bpf_link_create()**`, and the program’s callback is triggered by issuing system calls from user space.

In the case of [ebpf-go](https://ebpf-go.dev/), this is the `iterLink.Open()` abstracted call you see above in the code.

One important thing I’ll leave out for the next time. In the kernel space code, there’s a definition `**__s64 bpf_map_sum_elem_count(struct bpf_map *map) __ksym;**`. [This kfunc](https://ebpf-docs.dylanreimerink.nl/linux/kfuncs/bpf_map_sum_elem_count/) allows us to count the elements in the provided map (independent of its type) and significantly simplifying the coding process.

Complete source code is available on my GitHub Repository:## [GitHub - dorkamotorka/ebpf-map-metrics: eBPF Map Prometheus Exporter](https://github.com/dorkamotorka/ebpf-map-metrics?source=post_page-----fd2e3f12239a---------------------------------------)

eBPF Map Prometheus Exporter. Contribute to dorkamotorka/ebpf-map-metrics development by creating an account on GitHub.

github.com

[View original](https://github.com/dorkamotorka/ebpf-map-metrics?source=post_page-----fd2e3f12239a---------------------------------------)

## Conclusion

There’s a lot more potential for eBPF iterators beyond this use case, including CLI tools and enhanced observability platforms. We’ll explore these possibilities in future discussions, so stay tuned!

> To stay up-to-date with the latest cloud technologies, make sure to subscribe to my newsletter, [Cloud Chirp](https://cloudchirp.substack.com/). 🚀

[![eBPFChirp Blog](https://miro.medium.com/v2/resize:fill:96:96/1*Nw7KgVn0o4za9sPfZcRcJQ.png)](https://medium.com/all-things-ebpf?source=post_page---post_publication_info--fd2e3f12239a---------------------------------------)

[![eBPFChirp Blog](https://miro.medium.com/v2/resize:fill:128:128/1*Nw7KgVn0o4za9sPfZcRcJQ.png)](https://medium.com/all-things-ebpf?source=post_page---post_publication_info--fd2e3f12239a---------------------------------------)

[Last published Aug 8, 2024](https://medium.com/all-things-ebpf/part-2-ebpf-map-metrics-prometheus-exporter-fd2e3f12239a?source=post_page---post_publication_info--fd2e3f12239a---------------------------------------)

Explore the cutting-edge world of eBPF in our Medium publication, where we dive deep into its capabilities, advancements, and practical applications. From kernel innovations to complex network monitoring, discover how eBPF is transforming the tech landscape.

SRE at Prewave | Technical Writer-Editor | eBPF Researcher | Linkedin: [https://www.linkedin.com/in/teodor-janez-podobnik/](https://www.linkedin.com/in/teodor-janez-podobnik/)

## More from TJ. Podobnik, @dorkamotorka and eBPFChirp Blog

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--fd2e3f12239a---------------------------------------)