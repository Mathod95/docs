---
title: "When to Use Median vs. Average in DevOps Metrics: Lessons from a Karpenter EKS Review"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@talavital/when-to-use-median-vs-average-in-devops-metrics-lessons-from-a-karpenter-eks-review-2d466e819480"
author:
  - "[[Tal Avital]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Hey there! Recently, I was reviewing a monitoring plan for [Karpenter](https://karpenter.sh/) on EKS that one of my team members put together, and I noticed something interesting about the metrics: all of them used averages. For those not familiar with it, Karpenter is an open-source node autoscaling tool for Kubernetes that helps optimize cluster resources by automatically adjusting the number of nodes based on workload demands. This got me thinking about when we should use **median instead of average** in our monitoring systems.

As a **DevOps Team Lead at** [**CyberArk**](https://www.cyberark.com/), my team and I are maintaining infrastructure for an internal development platform that serves more than **1,500 developers**. With this scale, the accuracy of our metrics becomes especially critical for making the right decisions.

> *Full disclosure: I’m not a statistics expert by any means! But sometimes the most useful insights come from practical experience rather than advanced theory.*

## 💡 The Lightbulb Moment

During my review of our Karpenter metrics dashboard, I spotted metrics like **“Node Provisioning Latency”** and **“Pod Scheduling Latency”** that were being calculated as **averages**. Something didn’t feel right about that.

Here’s why this matters: in a large-scale Kubernetes environment, a single **outlier** can completely throw off your understanding of system performance if you’re only looking at averages.

## 🔄 A Quick Refresher: Average vs. Median

For those who (like me) didn’t pay close attention in statistics class:

- **Average (mean):** Sum up all values and divide by the number of values
- **Median:** The middle value when all data points are sorted

That’s it! But this small difference can have a huge impact on how we interpret our metrics.

## 🧭 When to Use Median in DevOps Metrics

After some digging and hands-on experience, here are the main cases where I found **median** to be more useful:

## 1\. When Measuring Response Times or Latency

In our Karpenter review, metrics like **“Node Provisioning Latency”** and **“Pod Scheduling Latency”** are perfect candidates for using **median**.

Why? Because in a distributed system, you’ll always have some outliers — that one pod that takes forever to schedule due to specific node requirements, or a node that takes longer to provision because of AWS API throttling.

> *That’s why for* ***time-based metrics****,* ***median and percentiles (like p95 or p99)*** *work best — they give a better sense of both typical and worst-case performance.*

## 2\. When Your Data Might Have Outliers

In production environments, outliers happen all the time. Maybe your system gets hit with an unusual request, a node runs out of resources, or a network hiccup causes unusual behavior.

**Median values give you a clearer picture of “normal” operation by ignoring these extremes.**

> *That said, outliers can still signal real problems. It’s worth tracking higher percentiles (like* ***p95/p99****) or setting alerts so you don’t miss rare but critical issues — even if you don’t want those outliers to skew your baseline metrics.*

## 3\. When You Want to Understand the Typical User Experience

If you’re trying to understand what **most users** experience, **median is your friend**.

An average could be pulled up by a few users having terrible experiences — even if most users are actually doing fine.

## ✅ When to Stick with Average

Averages still have their place! Here’s when I find them useful:

## 1\. When Measuring Resource Utilization

For metrics like **CPU Utilization** or **Memory Usage**, averages make more sense because you’re trying to understand the **overall load** on the system — not just the typical case.

## 2\. When You Need to Account for All Data Points

If **every single value matters** to your calculation — like **total cost** or **cumulative resource usage** — then average is appropriate.

## 3\. When Your Data Is Fairly Consistent

If your data tends to be **stable** and doesn’t show extreme spikes, average works well.

This is often true for metrics in **well-tuned environments**, like long-lived CPU/memory graphs on mature workloads.

## ✍️ My Practical Rule of Thumb

Over time, I’ve developed a simple rule I go by:

> ***\- For time-based metrics*** *(how long something takes), use* ***median and percentiles****.  
> \-* ***For quantity-based metrics*** *(how much of something), use* ***average****.*

## 📊 The Best of Both Worlds

Sometimes, you want **both**!

In our Karpenter monitoring, I suggested tracking **average, median, and 95th percentile** for key metrics. Together, they give a **complete picture**:

- **The median** shows us the *typical* experience
- **The average** shows us the *overall* system behavior
- **95th percentile** shows us the *worst experiences* (excluding true one-off outliers)

## 🔚 Wrapping Up

This small insight from a routine code review changed how I think about our monitoring systems.

It’s these little tweaks that can make the difference between a monitoring setup that gives you useful insights — and one that sends you chasing phantom problems.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*NsmNRmqGYXv2sD92)

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--2d466e819480---------------------------------------)