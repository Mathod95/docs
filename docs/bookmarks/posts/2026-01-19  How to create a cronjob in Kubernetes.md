---
title: "How to create a cronjob in Kubernetes?"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://overcast.blog/how-to-create-a-cronjob-in-kubernetes-60f6e76b477a"
author:
  - "[[Dhruvin Soni]]"
---
<!-- more -->

[Sitemap](https://overcast.blog/sitemap/sitemap.xml)## [overcast blog](https://overcast.blog/?source=post_page---publication_nav-9bad45fbe16d-60f6e76b477a---------------------------------------)

[![overcast blog](https://miro.medium.com/v2/resize:fill:76:76/1*fud-MZ0mXQKBVpkDiXRegQ.png)](https://overcast.blog/?source=post_page---post_publication_sidebar-9bad45fbe16d-60f6e76b477a---------------------------------------)

Cloud-Native Engineering: Kubernetes, Docker, Micro-services, AWS, Azure, GCP & more.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Cl_ccoa4TVqZV8wD.png)

Cronjob

### What is a Cronjob?

A cron job is a scheduled task in Unix-like operating systems, used to automate the execution of scripts or commands at specified intervals. The cron daemon runs in the background and executes these tasks according to the schedule defined in the crontab (cron table) files.

### Key Concepts:

- Cron Daemon: A background process that continuously checks the crontab files to see if any scheduled jobs need to be executed.
- Crontab File: A configuration file that specifies the schedule for running particular commands or scripts. Each user on a system can have their crontab file.
- Cron Job Syntax: Each line in a crontab file represents a cron job and follows this syntax:
```c
* * * * * command_to_execute
| | | | |
| | | | +----- Day of the week (0 - 7) (Sunday is both 0 and 7)
| | | +------- Month (1 - 12)
| | +--------- Day of the month (1 - 31)
| +----------- Hour (0 - 23)
+------------- Minute (0 - 59)
```

### Examples:

- Run a script every day at 2 AM
```c
0 2 * * * /path/to/script.sh
```
- Run a command every 15 minutes
```c
*/15 * * * * /path/to/command
```
- Run a job every Monday at 5 PM
```c
0 17 * * 1 /path/to/job
```

### How to create a cronjob in k8s?

Creating a cron job in Kubernetes involves defining a `CronJob` resource in a YAML file and apply it to your Kubernetes cluster. Here's a step-by-step guide

### Prerequisites:

- A Kubernetes cluster
- kubectl installed

### Step 1: Create a CronJob YAML file

- Create a YAML file, for example,`cronjob.yaml,` with the following content. This example runs a job every minute that prints “Hello, Kubernetes!” to the logs.
```c
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello-k8s
spec:
  schedule: "*/1 * * * *" # Run every minute
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            args:
            - /bin/sh
            - -c
            - echo "Hello, Kubernetes!"
          restartPolicy: OnFailure
```

Let’s understand the above code.

- `apiVersion` specifies the Kubernetes API version to be used for this resource. Here, it is `batch/v1` which is the API version for batch jobs.
- `kind` specifies the type of the Kubernetes resource. Here, it is `CronJob`.
- `metadata` contains information about the CronJob, such as its name.
- `spec` specifies the desired state of the CronJob.
- `schedule` is a string in the cron format that specifies when the job should be run. In this example, it will run every minute.
- `jobTemplate` specifies the template for the Job that will be created and run according to the schedule.
- `template` specifies the pod template for the Job.
- `containers` specifies the container specification for the pod.
- `name` is the name of the container.
- `image` is the container image to use.
- `args` specifies the command to be executed in the container. Here, a shell command makes an HTTP GET request to a URL with a date parameter.
- `restartPolicy` specifies the restart policy for the pod. Here, it is set to `OnFailure`.

### Step 2: Apply the CronJob to your cluster

Use `kubectl apply` to create the cron job in your cluster.

```c
kubectl apply -f cronjob.yaml
```

### Step 3: Verify the CronJob

Check that your CronJob has been created and is running correctly.

```c
kubectl get cronjob
```

You should see something like this.

```c
NAME         SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
hello-k8s    */1 * * * *   False     0        <none>          1m
```

### Step 4: Check the logs

To check the logs of the jobs created by your CronJob, first get the list of jobs.

```c
kubectl get jobs
```

Then, get the pods created by a specific job and check their logs.

```c
kubectl get pods --selector=job-name=<job-name>
kubectl logs <pod-name>
```

### Conclusion:

Creating a cron job in Kubernetes involves defining a `CronJob` resource in a YAML file and apply it to your cluster using `kubectl`. By specifying the schedule and job template, you can automate repetitive tasks at defined intervals, such as running scripts or performing maintenance. This approach ensures that tasks are executed in a reliable and scalable manner within your Kubernetes environment.

With the provided example, you should now have a basic understanding of how to set up and manage cron jobs in Kubernetes. This setup can be extended and customized further to suit your specific requirements, leveraging the powerful scheduling and orchestration capabilities of Kubernetes. For more detailed information and advanced configurations, refer to the official Kubernetes documentation on CronJobs.

Follow me on [**LinkedIn**](https://www.linkedin.com/in/dhruvinksoni/)

Follow for more stories like this 😁

[![overcast blog](https://miro.medium.com/v2/resize:fill:96:96/1*fud-MZ0mXQKBVpkDiXRegQ.png)](https://overcast.blog/?source=post_page---post_publication_info--60f6e76b477a---------------------------------------)

[![overcast blog](https://miro.medium.com/v2/resize:fill:128:128/1*fud-MZ0mXQKBVpkDiXRegQ.png)](https://overcast.blog/?source=post_page---post_publication_info--60f6e76b477a---------------------------------------)

[Last published 18 hours ago](https://overcast.blog/11-iceberg-performance-optimizations-you-should-know-d9aef7aab235?source=post_page---post_publication_info--60f6e76b477a---------------------------------------)

Cloud-Native Engineering: Kubernetes, Docker, Micro-services, AWS, Azure, GCP & more.

Senior Cloud Infrastructure Engineer | AWS | Automation | 2x AWS | CKA | Terraform Certified | k8s | Docker | CI/CD | [http://dhsoni.info/](http://dhsoni.info/)

## More from Dhruvin Soni and overcast blog

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--60f6e76b477a---------------------------------------)