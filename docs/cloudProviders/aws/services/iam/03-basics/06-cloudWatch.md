---
title: CloudWatch
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/CloudWatch/page
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/Demo-CloudWatch/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/e74caf44-a8b0-405b-9bfa-af91f5e11214
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/c708e4e3-ae56-4c23-9f79-981aa6a018fe
---

> This article explains how to use AWS CloudWatch for monitoring, setting alarms, and creating dashboards for AWS resources and applications.

AWS CloudWatch is the central observability service for collecting metrics, logs, and events from your AWS resources and applications. In this guide, you’ll learn how to set up a CPU utilization alarm for an EC2 instance, ensuring you receive notifications whenever usage crosses a critical threshold.

<Frame>
  ![The image shows a CPU utilization graph with a red alarm threshold line at 75%, indicating that the CPU usage has exceeded this threshold multiple times, triggering an alarm.](https://kodekloud.com/kk-media/image/upload/v1752862939/notes-assets/images/AWS-IAM-CloudWatch/cpu-utilization-graph-alarm-threshold.jpg)
</Frame>

## Why Use CloudWatch?

With CloudWatch, you can:

* Collect and visualize metrics (CPU, memory, disk I/O, network) from AWS services and custom applications
* Aggregate, search, and analyze logs in real time
* Trigger automated actions or notifications when specified events or thresholds are met
* Build dashboards for a consolidated, at-a-glance view of your infrastructure health

<Callout icon="lightbulb" color="#1CB2FE">
  Be aware that custom metrics and detailed monitoring (1-minute resolution) may incur additional charges.
</Callout>

## Key CloudWatch Components

| Component    | Purpose                                                              |
| ------------ | -------------------------------------------------------------------- |
| Metrics      | Time-series data for resource performance (e.g., `CPUUtilization`).  |
| Logs         | Centralized aggregation and querying of application and system logs. |
| Alarms       | Threshold-based triggers to send notifications or invoke actions.    |
| Dashboards   | Customizable visualizations combining metrics and logs in one view.  |
| Events/Rules | Automated reactions to state changes or scheduled tasks across AWS.  |

<Frame>
  ![The image explains AWS Cloudwatch, highlighting its use for monitoring and observability, setting up alarms for issues, and analyzing data through dashboards.](https://kodekloud.com/kk-media/image/upload/v1752862940/notes-assets/images/AWS-IAM-CloudWatch/aws-cloudwatch-monitoring-alarms-dashboards.jpg)
</Frame>

## Demo: Configure a High-CPU Alarm

Follow these steps in the AWS Management Console to create an alarm that notifies you when CPU utilization exceeds 75% for 5 minutes:

1. Navigate to **CloudWatch** in the AWS Console.
2. In the sidebar, choose **Alarms** → **All alarms** → **Create alarm**.
3. Under **Select metric**, pick the **EC2** namespace and then **Per-Instance Metrics** → **CPUUtilization**.
4. Click **Select metric** for your target instance.
5. On the **Specify metric and conditions** page:
   * **Threshold type**: Static
   * **Whenever CPUUtilization is**: `>` 75
   * **For**: 5 consecutive periods of 1 minute each
6. Under **Configure actions**, choose an SNS topic or create a new one to send email notifications.
7. (Optional) Add tags to organize billing and access management.
8. Review settings and click **Create alarm**.

Once activated, CloudWatch will continuously evaluate the metric and send an email via SNS whenever CPU usage remains above 75% for 5 minutes.

<Callout icon="triangle-alert" color="#FF6B6B">
  Ensure your SNS subscription is confirmed; otherwise, you won’t receive alarm notifications.
</Callout>

## Further Reading & References

* [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/latest/monitoring/WhatIsCloudWatch.html)
* [Managing Amazon SNS Topics](https://docs.aws.amazon.com/sns/latest/dg/sns-create-topic.html)
* [AWS Well-Architected Monitoring and Observability](https://docs.aws.amazon.com/wellarchitected/latest/mon-in-op/overview.html)

---

> This guide explains how to configure an Amazon CloudWatch alarm for EC2 CPU utilization exceeding 70% and set up email notifications.

In this guide, you’ll configure an Amazon CloudWatch alarm that notifies you via email whenever an EC2 instance’s average CPU usage exceeds 70% over a five-minute period. This is essential for maintaining optimal performance and responding swiftly to resource bottlenecks.

## Prerequisites

| Requirement                         | Description                                           |
| ----------------------------------- | ----------------------------------------------------- |
| AWS account with CloudWatch access  | Permissions to view metrics and create alarms         |
| Running EC2 instance                | The instance you intend to monitor                    |
| Verified email subscription for SNS | Confirmed subscription to receive alarm notifications |

<Callout icon="triangle-alert" color="#FF6B6B">
  Make sure your IAM user or role has the following managed policies:

  * `CloudWatchFullAccess`
  * `AmazonSNSFullAccess`

  Without these permissions, you won’t be able to create alarms or SNS topics.
</Callout>

## 1. Open the Alarms Dashboard

1. Sign in to the [AWS Management Console](https://aws.amazon.com/console/) and open **CloudWatch**.
2. In the left navigation pane, choose **Alarms**, then click **Create alarm**.

<Frame>
  ![The image shows the AWS CloudWatch Alarms dashboard with no alarms currently displayed. There is an option to create a new alarm.](https://kodekloud.com/kk-media/image/upload/v1752862957/notes-assets/images/AWS-IAM-Demo-CloudWatch/aws-cloudwatch-alarms-dashboard-no-alarms.jpg)
</Frame>

## 2. Select the EC2 CPUUtilization Metric

1. On **Select metric**, pick **EC2**.
2. Under **Per-Instance Metrics**, locate and select your instance’s **CPUUtilization** metric.
3. Click **Select metric**.

<Frame>
  ![The image shows an AWS CloudWatch interface where metrics for an EC2 instance are being selected. It lists various metrics like CPUUtilization and EBSIOBalance% for a specific instance.](https://kodekloud.com/kk-media/image/upload/v1752862958/notes-assets/images/AWS-IAM-Demo-CloudWatch/aws-cloudwatch-ec2-metrics-interface.jpg)
</Frame>

## 3. Define the Alarm Threshold

Configure the alarm conditions on the **Configure metric** page:

| Setting          | Value                |
| ---------------- | -------------------- |
| Statistic period | 5 minutes            |
| Threshold type   | Static               |
| Condition        | GreaterThanThreshold |
| Threshold value  | 70                   |

This setup tells CloudWatch to evaluate the average CPU utilization over each 5-minute interval and fire the alarm if it exceeds 70%.

<Frame>
  ![The image shows an AWS CloudWatch interface for creating a metric alarm, specifically monitoring CPU utilization for an EC2 instance. It includes a graph and configuration details like namespace, metric name, instance ID, and statistic period.](https://kodekloud.com/kk-media/image/upload/v1752862959/notes-assets/images/AWS-IAM-Demo-CloudWatch/aws-cloudwatch-cpu-utilization-alarm.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  Custom metrics and long-term storage can incur additional charges. Review [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/) before enabling high-frequency monitoring.
</Callout>

## 4. Configure Notifications via SNS

Under **Notification**, choose **Create new topic** and enter:

* **Topic name**: Send\_email\_to\_Admin
* **Endpoint**: [admin@test.com](mailto:admin@test.com)

Click **Create topic** to confirm. You can also attach automated actions for Auto Scaling, EC2, or Systems Manager.

<Frame>
  ![The image shows an AWS CloudWatch console screen where an alarm state trigger is being configured. It includes options for sending notifications via SNS, with a new topic being created named "Send\_email\_to\_Admin."](https://kodekloud.com/kk-media/image/upload/v1752862960/notes-assets/images/AWS-IAM-Demo-CloudWatch/aws-cloudwatch-alarm-sns-configuration.jpg)
</Frame>

<Frame>
  ![The image shows an AWS CloudWatch interface with options to add actions for Auto Scaling, EC2, and Systems Manager. There are buttons for "Add Auto Scaling action," "Add EC2 action," and "Add Systems Manager action."](https://kodekloud.com/kk-media/image/upload/v1752862962/notes-assets/images/AWS-IAM-Demo-CloudWatch/aws-cloudwatch-auto-scaling-ec2-actions.jpg)
</Frame>

Click **Next** to proceed.

## 5. Name, Review, and Create

1. Provide a name such as `CPUUtilizationAbove70` and an optional description.
2. Review all settings:
   * Metric: **CPUUtilization** for your EC2 instance
   * Period and statistic
   * Threshold: **GreaterThan 70**
   * Notification: **SNS email to [admin@test.com](mailto:admin@test.com)**
3. Click **Create alarm**.

Upon successful creation, you’ll see a confirmation message in the Alarms dashboard.

<Frame>
  ![The image shows an AWS CloudWatch dashboard with a notification indicating a successfully created alarm for CPU utilization above 70 percent. The alarms section currently displays no active alarms.](https://kodekloud.com/kk-media/image/upload/v1752862963/notes-assets/images/AWS-IAM-Demo-CloudWatch/aws-cloudwatch-dashboard-cpu-alarm.jpg)
</Frame>

***

Your CloudWatch alarm is now active. When the average CPU utilization exceeds 70% over a five-minute span, an email is sent to the administrator. Monitor and adjust thresholds as needed to align with your application’s performance requirements.

## References

* [AWS CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
* [Amazon EC2 Monitoring](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-cloudwatch.html)
* [Amazon SNS Developer Guide](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)