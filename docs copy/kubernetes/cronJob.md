---
title: Kubernetes CronJob
date: 2026-01-22
status: draft
categories: Kubernetes
tags:
  - kubernetes
source: https://faun.pub/kubernetes-cron-jobs-60e1a2509d54
---

In our previous article, we explored the world of Kubernetes Jobs and how they enable us to run one-off tasks within our containerized applications. However, one critical aspect of managing containerized workloads that we intentionally skipped for a more in-depth discussion is Kubernetes CronJobs. In this article, we’ll delve deeper into CronJobs, the scheduling powerhouse of Kubernetes, and discover how they allow you to automate and orchestrate recurring tasks with precision and ease.

Kubernetes Cron jobs

### What Are Kubernetes CronJobs?

In the world of Kubernetes, a CronJob is a resource type that defines a time-based job. It enables you to run tasks periodically at specified intervals, just like the traditional cron utility on Linux systems. With CronJobs, you can automate various tasks within your containerized applications, such as database backups, log rotation, or data syncing.

### Enabling Scheduled Tasks

CronJobs offer several advantages for managing scheduled tasks in Kubernetes:

**Automation:** CronJobs automate repetitive tasks, reducing the need for manual intervention and human error.

**Scalability:** Kubernetes scales CronJobs according to your cluster’s capacity, ensuring tasks are executed efficiently.

**Flexibility:** You can define the schedule for tasks down to the minute, making it easy to customize when and how often jobs run.

### Jobs Vs Cron Jobs

Kubernetes Jobs are designed for running one-time, batch-style tasks. They execute a task to completion once and then terminate, making them suitable for operations that should occur only once, such as a database migration or a data import task. On the other hand, CronJobs excel at automating recurring tasks. They repeatedly run jobs based on a predefined schedule, ensuring that periodic operations, like regular data backups, log rotation, or daily reports, are executed consistently and on time.

Now, let’s dive into creating and managing CronJobs in Kubernetes.

### Creating a Kubernetes CronJob

Creating a CronJob in Kubernetes involves defining a manifest file, which is written in YAML format. Here’s a step-by-step guide to creating a basic CronJob:

**Define a YAML manifest**: Create a YAML file, e.g., my-cronjob.yaml, and specify the CronJob’s details, including the schedule and the container image to run. Here’s a minimal example:

```hs
apiVersion: batch/v1
kind: CronJob
metadata:
 name: my-cronjob
spec:
 schedule: “*/5 * * * *”
 jobTemplate:
 spec:
 template:
 spec:
 containers:
 — name: my-cronjob-container
 image: my-image:latest
```

In this example, the CronJob runs every 5 minutes, using the my-image:latest container.

Apply the manifest: Use the kubectl apply command to create the CronJob resource:

```hs
kubectl apply -f my-cronjob.yaml
```

Verify the CronJob: You can check the status and details of your CronJob with the following command:

```hs
kubectl get cronjob my-cronjob
```

### Managing Kubernetes CronJobs

Once you’ve created a CronJob, you can manage it using various Kubernetes commands.

Here are some common operations:

**List CronJobs:** To see all the CronJobs in your cluster, use the *kubectl get cronjobs* command.

**Inspect CronJob:** To view the details of a specific CronJob, use kubectl describe cronjob *<cronjob-name>*.

**Pause and Resume CronJobs:** You can temporarily stop a CronJob with *kubectl suspend cronjob <cronjob-name>* and resume it with kubectl resume cronjob *<cronjob-name>.*

**Manually Run CronJob:** To manually run a CronJob outside its schedule, use *kubectl create job — from=cronjob/<cronjob-name> <job-name>.*

### Conclusion

Kubernetes CronJobs are a powerful tool for automating and managing scheduled tasks within your containerized applications. By defining the schedule and job details in a simple YAML manifest, you can easily create, deploy, and manage CronJobs in your Kubernetes cluster. Whether it’s performing backups, generating reports, or cleaning up resources, CronJobs can streamline your workflow and enhance the reliability of your applications in a Kubernetes environment.