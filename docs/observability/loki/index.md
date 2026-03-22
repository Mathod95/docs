---
title: Loki
#status: draft
hide:
  - toc
---

<p align="center">
  <a href="https://github.com/grafana/loki">
    <img src="https://opengraph.githubassets.com/Mathod/grafana/loki" />
  </a>
</p>

---

> This course covers Loki, a log aggregation tool, focusing on its architecture, installation, configuration, integration with Grafana, and deployment in Kubernetes.

Welcome to this in-depth course on Loki, the innovative log aggregation tool by Grafana Labs. In this lesson, we will explore how Loki efficiently stores and queries logs, offering a streamlined alternative to traditional ELK stacks. If you’re already familiar with other Grafana tools like Prometheus, you’ll find Loki’s approach refreshingly similar yet uniquely optimized for log management.

Our session will cover the following key topics:

* An overview of what Loki is and the problems it solves.
* How Loki differentiates itself from legacy logging solutions.
* A high-level explanation of Loki's architecture.
* Step-by-step instructions to install your own Loki instance.
* Exploration of Loki's configuration options.
* How to integrate Loki seamlessly with Grafana.
* A practical guide to deploying Loki in a Kubernetes environment to effectively collect logs from both the cluster and running applications.

We'll wrap up the lesson with a hands-on demonstration that deploys the necessary resources to a Kubernetes cluster and shows you how to collect logs from a sample application.

<Callout icon="lightbulb" color="#1CB2FE">
  Familiarity with Kubernetes and Grafana will help you get the most out of this course.
</Callout>

---

Welcome to the byte-size course Grafana Loki! In this course, we’ll take you through everything you need to know about Grafana, the Loki architecture, step-by-step installation instructions, configuration tips, and a quick demo on integrating Grafana with Loki. Loki is a powerful logging backend, designed to be cost-effective and easy to operate. Whether you’re new to Loki or looking to enhance your monitoring stack, this course is for you!
Discover how to effortlessly set up Loki instances and promtail containers within your Kubernetes cluster, allowing you to gather logs from both the cluster itself and the applications running on it. With step-by-step guidance and expert insights, you’ll learn how to streamline the process using Helm charts, ensuring a seamless and efficient log management system. Don’t miss out on unlocking the power of Loki for enhanced monitoring and troubleshooting in your Kubernetes environment.

---
!!! abstract "Links and References"
    - https://github.com/grafana/loki


### Grafana Loki Essentials - Part 1
  - [ ] What is Loki
  - [ ] Architecture of Loki
  - [ ] Loki Installation
  - [ ] Promtail installation
  - [ ] Querying Logs
  - [ ] Collecting App logs
### Grafana Loki Essentials - Part 2
  - [ ] Loki in Kubernetes
  - [ ] Deploying Loki in Kubernetes
  - [ ] Connecting to Grafana
  - [ ] Viewing Kubernetes logs
  - [ ] Deploying view app logs
  - [ ] Promtail pipelines
  - [ ] Conclusion