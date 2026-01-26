---
title: "Monitoring Kubernetes Cronjobs with Prometheus"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://tjtharrison.medium.com/monitoring-kubernetes-cronjobs-with-prometheus-4c2ce272c5de"
author:
  - "[[tjtharrison]]"
---
<!-- more -->

[Sitemap](https://tjtharrison.medium.com/sitemap/sitemap.xml)

A Kubernetes job is a resource that will spin up a pod with a defined configuration and run it until completion (unlike a deployment pod which is designed to run until stopped).

Kubernetes Cronjobs are used to schedule jobs to run on a set interval, for example a script to backup a server that will exit with exit code 0/1 depending on whether it was successful or failed as appropriate.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*2MFV59GLtZDGM69h)

Photo by Eric Rothermel on Unsplash

## Writing a CronJob

Here is an example of a CronJob manifest file for deploying onto a Kubernetes cluster.

```c
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ws-backup
  namespace: ws
spec:
  schedule: "0 4 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: ws-backup
              image: my.registry.com/ws-backup:1.0.0
              imagePullPolicy: IfNotPresent
          imagePullSecrets:
            - name: registry
          restartPolicy: OnFailure
```

I won’t dive into the specifics of the job as it’s not overly relevant to the topic of observability, other than to note that it’s a backup script that is scheduled to run once a day at 04:00 to backup a web server.

## Observability on CronJobs in Prometheus

So, when it comes to observability around scheduled tasks, we want to make sure that we cover all of the bases.

For example we could simply monitor for the count of failed tasks increasing, however, this wouldn’t cover the use case of the task not launching at all or a task not completing over the period.

### Prerequisites

The metrics that we are going to be using to generate these alerts are provided by [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics) so you’ll need to have this deployed and configured as a scrape job in Prometheus (eg below) or as a service monitor, before proceeding:

```c
- job_name: 'kube-state-metrics'
    static_configs:
      - targets: [ 'kube-state-metrics.observabilityr.svc.cluster.local:8080' ]
```

### Deciding what to monitor

We’ll want to use Kubernetes metrics around jobs to monitor the following in Prometheus. The period of time that we are going to be writing our PromQL queries over, will be dependent on the interval at which your cronjob runs.

For example if your task is scheduled to run once a day, we will be monitoring for metric changes over 1 day (as we do not expect the value to change more frequently than that).

Given the above, we’re going to be generating Alerts in Prometheus for the following:

- There are no completed cronjob jobs in the past 25 hours (this is better than monitoring for failed tasks as it will also catch uncompleted jobs)
- A lack of presence of a task (eg if the Cronjob is deleted and the metrics are no longer reported).

### Configuring the alerts

The below PromQL expression will return if the last successfully completed job was more than 25 hours ago.

Although the job is scheduled to run every 24 hours, the job can take ~20 minutes to complete and we’ll give a bit of headroom to limit the false positives:

```c
(time() - kube_cronjob_status_last_successful_time{cronjob="ws-backup"}) > 25*60*60
```

If your job has completed successfully over the period of time, there should be no results from the query. If the job last completed more than 25 hours ago, this will return a result of the outdated job.

Now lets convert this into a Prometheus rule:

```c
- alert: WS Backup failed
  expr: (time() - kube_cronjob_status_last_successful_time{cronjob="ws-backup"}) > 25*60*60
  for: 10m
  labels:
    severity: high
  annotations:
    summary: No WS Backup in the last 25 hours
    description: The last successful WS Backup was more than 25 hours ago.
```

Next we’ll want to handle the case that the Cronjob does not exist at all.

To do this, we’ll use the `absent` prometheus function returns as a failure if there are no results (eg the opposite of a normal query).

We’ll use the below to alert if there are no reported successful jobs completed for our Cronjob at all (indicating an issue with the cronjob or that it has been deleted from the cluster).

```c
absent(kube_cronjob_status_last_successful_time{cronjob="ws-backup"})
```

Again lets convert this to a Prometheus rule:

```c
- alert: WS Backup job is not present
  expr: absent(kube_cronjob_status_last_successful_time{cronjob="ws-backup"})
  for: 10m
  labels:
    severity: high
  annotations:
    summary: Backup job is not present
    description: There are no reported backup jobs.
```

Finally, for good measure — Lets set up a monitor for a cronjob that has been deployed as “suspended” (K [ubernetes docs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#schedule-suspension)).

A suspended cronjob will never fire — Although this will eventually be picked up by the lack of a successful backup over 25 hours, it’s probably not something you want to leave for a day to find out if you can help it!

```c
kube_cronjob_spec_suspend{cronjob="ws-backup"} == 1
```

And as a prometheus rule:

```c
- alert: WS Backup cronjob suspended
  expr: kube_cronjob_spec_suspend{cronjob="ws-backup"} == 1
  for: 10m
  labels:
    severity: high
  annotations:
    summary: WS Backup cronjob is suspended
    description: The backup cronjob has been marked as suspended so will not run on schedule.
```

Once you’ve deployed these rules up to your Prometheus instance, you should see new alerts in your UI (hopefully) showing a green OK status:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*6rSSwFh9ueeRLxRrupIMdg.png)

## Testing

To verify that the alerting is working correctly, we should do three things:

The first test we’ll do will be to temporarily set the alert to trigger if not successful for a shorter period (eg 1 hour). Eg our expression would become:

```c
(time() - kube_cronjob_status_last_successful_time{cronjob="ws-backup"}) > 1*60*60
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*XapQCgYbbLUuUytzf7gVMw.png)

The second test will be to delete the cronjob and confirm that the “Backup job is not present” alert goes to warning status:

```c
kubectl delete cronjob -n ws ws-backup
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*TEurqNdukE4idpwTO2bZ9Q.png)

And finally we should deploy the cronjob as suspended to ensure that this triggers the alert correctly.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2zg-W8r4pNI-xsLHVtbWfw.png)

## Grafana dashboard

There are some other interesting metrics provided by kube-state-metrics when it comes to Cronjobs — Most of which we probably won’t want to receive notifications for.

However, there is a good G [rafana dashboard](https://grafana.com/grafana/dashboards/14279-cronjobs/) (albeit with a few typos!) which you can import to get some good visibility of other details of your cronjob (eg max/min/average duration)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*epneHHk0yYt6O32FSPjjjQ.png)

**Dashboard ID: 14279**

## Wrap up

I hope you’ve found this article helpful on how to get some observability about the completion state of your Cronjobs in Kubernetes!

Please follow for more of the same 🙇

## More from tjtharrison

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--4c2ce272c5de---------------------------------------)

Close sidebar