---
title: "Kubernetes Networking: eBPF in Action —  Filtering Packets Like a Pro"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@hmquan08011996/kubernetes-networking-ebpf-in-action-filtering-packets-like-a-pro-b5f2d1c062b1"
author:
  - "[[Quan Huynh]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Welcome back to *eBPF in Action*. In Part 1, we learned how to use eBPF by counting system activity. Now, let’s put it to work on networking — specifically, filtering packets. We’ll use eBPF to block traffic from a specific IP address, showing how it can control your network like a pro. This sets the stage for Kubernetes networking later in the series. Ready? Let’s dive in.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Q8ix66nquOEPeuZ-VRTCig.png)

Series structure:

[Part 1 — What’s eBPF, and Why Should You Care?](https://medium.com/@hmquan08011996/kubernetes-networking-ebpf-in-action-f0df2592dade)

Part 2 — eBPF Meets Networking: Filtering Packets Like a Pro

[Part 3 — How does eBPF work?](https://medium.com/@hmquan08011996/kubernetes-networking-ebpf-in-action-how-it-works-1139ad08c465)

[Part 4 — eBPF in Kubernetes: Replacing the Old Ways](https://medium.com/@hmquan08011996/kubernetes-networking-ebpf-in-kubernetes-replacing-the-old-ways-e1da78bc3631)

[Part 5 — Cilium Up and Running](https://medium.com/@hmquan08011996/kubernetes-networking-cilium-up-and-running-928114530cdb)

[Part 6 — Cilium Gateway](https://medium.com/@hmquan08011996/kubernetes-networking-cilium-gateway-ebpf-meets-the-modern-kubernetes-ingress-ba50c6903c26)

Part 7 — Observability with Cilium: Seeing Inside Your Cluster

Part 8 — Load Balancing with Cilium

Part 9 — Securing Kubernetes with Cilium: Network Policies

Part 10 — Building Your eBPF Tool for Kubernetes

## Why eBPF for Networking?

Networks are the backbone of any system — data flows in and out constantly. Sometimes, you need to block an IP, redirect traffic, or just watch what’s happening. Old tools like iptables can do this, but they’re slow for big jobs. eBPF changes that.

With eBPF, you get:

- **Speed**: It runs right in the kernel.
- **Control**: You decide exactly what happens to each packet.
- **No Reboots**: Load your rules, and they start working instantly.

Today, we’ll write a simple eBPF program to drop packets from an IP we don’t like. It’s a small step, but it shows the power we’ll unleash in Kubernetes down the road.

## What We’re Building

Our goal: Block all packets coming from a specific IP (say, `192.168.1.100`). We’ll use:

- **XDP**: A fast eBPF hook that grabs packets as soon as they hit the network card.
- **A Simple Program**: Written in C, it checks the source IP and drops matches.
- **Tools**: `bpftool` and `clang` to compile and load it.

This runs on your network interface — like `eth0` — and acts like a bouncer at the door.

## What You Need

- A Linux system (Ubuntu 22.04 or similar, kernel 4.9+ — check with `uname -r`).
- Install these:
```c
sudo apt update && sudo apt install clang llvm libbpf-dev bpftool linux-tools-common linux-tools-$(uname -r)
```
- A network interface (e.g., `eth0` or `enp0s3` — find yours with `ip link`).

**Note for WSL2 Users**: WSL2’s kernel might not support XDP fully. Try this in a VM (like Ubuntu in VirtualBox) or on real hardware for best results.

## Step 1: Write the eBPF Program

Create a file called `block_ip.c`:

```c
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <bpf/bpf_helpers.h>

SEC("xdp")
int block_ip(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    // Check if packet has Ethernet and IP headers
    struct ethhdr *eth = data;
    if (data + sizeof(*eth) > data_end)
        return XDP_PASS;

    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;

    struct iphdr *ip = data + sizeof(*eth);
    if (data + sizeof(*eth) + sizeof(*ip) > data_end)
        return XDP_PASS;

    // Block this IP (in network byte order)
    __u32 blocked_ip = __constant_htonl(0xC0A80164); // 192.168.1.100
    if (ip->saddr == blocked_ip)
        return XDP_DROP;

    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
```
- `SEC(“xdp”)`: Tells the kernel this is an XDP program.
- `block_ip`: Checks each packet’s source IP.
- `XDP_DROP`: Blocks the packet if it matches `192.168.1.100`.
- `XDP_PASS`: Let everything else through.

## Step 2: Compile It

Run this in your terminal:

```c
clang -O2 -target bpf -c block_ip.c -o block_ip.o
```

This turns your C code into eBPF bytecode the kernel can use.

## Step 3: Load It

Attach it to your network interface (replace `eth0` with yours):

```c
sudo bpftool prog load block_ip.o /sys/fs/bpf/block_ip
sudo bpftool net attach xdp name block_ip dev eth0
```

## Step 4: Test It

- From another machine (or a VM), ping your Linux box from `192.168.1.100`. It should fail.
- Ping from a different IP (like `192.168.1.101`). It should work.
- Check if it’s running:
```c
sudo bpftool prog list
```

You’ll see your program listed with an ID.

## Step 5: Clean Up

When you’re done:

```c
sudo bpftool net detach xdp dev eth0
sudo rm /sys/fs/bpf/block_ip
```

## How It Works

Here’s the flow:

1. A packet hits your network card.
2. XDP grabs it before the kernel does much else.
3. Your eBPF program checks the IP.
4. If it’s `192.168.1.100`, it’s dropped. Otherwise, it moves on.

This happens crazy fast because XDP runs at the earliest point possible. Compare that to iptables, which processes packets later and slows down under load.

## Why This Matters for Kubernetes

This IP-blocking trick is simple, but it’s a building block. In Kubernetes, you’ve got tons of Pods talking over the network. Tools like Cilium use eBPF to:

- Filter traffic between Pods.
- Balance loads without old proxies.
- Watch everything in real time.

We’ll get there in future posts. For now, you’ve had a taste of eBPF’s networking power.

## Wrap-Up

- eBPF lets you control network traffic right in the kernel.
- You just built a program to block an IP with XDP — fast and precise.
- This is the foundation for bigger things, like Kubernetes networking.

## More from Quan Huynh

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--b5f2d1c062b1---------------------------------------)