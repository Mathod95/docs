---
title: CloudTrail
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/CloudTrail/page
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/Monitoring-Demo-CloudTrail/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/3f50db97-eef8-43a7-957a-8b1bf3e8fbb0?autoplay=true
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/459cb4fc-2717-4d4a-a80b-868b4c11ea21
---

> This guide explains how to use AWS CloudTrail to audit and trace EC2 instance shutdowns by identifying the IAM user responsible for the action.

CloudTrail provides a comprehensive audit trail of all API calls in your AWS account. In this guide, you’ll learn how to trace which IAM user issued the `StopInstances` command to shut down an EC2 instance.

## Table of Contents

* [Use Case: Investigating EC2 Shutdown](#use-case-investigating-ec2-shutdown)
* [How CloudTrail Works](#how-cloudtrail-works)
* [Key Features](#key-features)
* [Demo: Finding the StopInstances Event](#demo-finding-the-stopinstances-event)
* [Best Practices](#best-practices)
* [References](#references)

***

## Use Case: Investigating EC2 Shutdown

When an unexpected EC2 instance stops, you need to know who performed that action. CloudTrail captures every API call, making it straightforward to identify the culprit.

<Frame>
  ![The image is a diagram showing the process of investigating who shut down an EC2 instance using AWS CloudTrail. It involves an IAM user making an API call to stop the instance, which is logged by AWS CloudTrail.](https://kodekloud.com/kk-media/image/upload/v1752862936/notes-assets/images/AWS-IAM-CloudTrail/ec2-instance-shutdown-investigation-diagram.jpg)
</Frame>

## How CloudTrail Works

1. An IAM user or role issues an API request (e.g., `StopInstances`).
2. CloudTrail records the request details: caller identity, API action, resource ARNs, and timestamp.
3. Logs are delivered to an S3 bucket (or optionally to CloudWatch Logs) for storage and analysis.

<Callout icon="lightbulb" color="#1CB2FE">
  Make sure you have at least one active trail in the region where your EC2 instances run.\
  Configure multi-region logging for global coverage.
</Callout>

## Key Features

| Feature                 | Description                                                       |
| ----------------------- | ----------------------------------------------------------------- |
| Audit Trail             | Complete history of all API calls for compliance and forensic use |
| Visibility & Security   | Detect unusual behavior by monitoring account activity            |
| Centralized Log Storage | Store logs in Amazon S3 for long-term retention                   |
| Real-time Monitoring    | Integrate with CloudWatch Logs to trigger alerts instantly        |

<Frame>
  ![The image explains AWS CloudTrail, highlighting its functions: creating an audit trail, enhancing security through activity monitoring, and storing logs in S3 buckets for real-time analysis.](https://kodekloud.com/kk-media/image/upload/v1752862938/notes-assets/images/AWS-IAM-CloudTrail/aws-cloudtrail-audit-trail-security-logs.jpg)
</Frame>

## Demo: Finding the StopInstances Event

Follow these steps in the AWS Management Console or use the AWS CLI to locate the `StopInstances` event.

### AWS Management Console

1. Open the **CloudTrail** service.
2. Click **Event history**.
3. In the filter bar, select **Event name** and enter `StopInstances`.
4. Review each entry’s:
   * **Event time**
   * **Username** (IAM user or role)
   * **Resources** (affected EC2 instance ARNs)

### AWS CLI

```bash  theme={null}
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=StopInstances \
  --max-results 10
```

This returns a JSON list of matching events. Inspect the `Username`, `EventTime`, and `Resources` fields to pinpoint who stopped the instance.

<Callout icon="triangle-alert" color="#FF6B6B">
  If your trail isn’t configured to deliver logs to CloudWatch Logs, you won’t get real-time alerts.\
  Enable CloudWatch integration in the trail settings to receive immediate notifications.
</Callout>

## Best Practices

* Enable **multi-region trails** to capture global AWS API activity.
* Encrypt log files with SSE-KMS for data protection.
* Implement **log file validation** to ensure integrity.
* Configure **lifecycle policies** in S3 to archive or delete old logs.

## References

* [AWS CloudTrail User Guide](https://docs.aws.amazon.com/cloudtrail/latest/userguide/)
* [AWS CloudTrail API Reference](https://docs.aws.amazon.com/cloudtrail/latest/APIReference/)
* [Monitoring CloudTrail with CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
* [Managing S3 Lifecycle Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-configuration-examples.html)

---

> Learn to identify the IAM user who terminated an EC2 instance using AWS CloudTrail’s Event History for enhanced security visibility.

In this walkthrough, you’ll learn how to pinpoint the IAM user who terminated an EC2 instance (ID ends with `1D91`) using AWS CloudTrail’s Event History. This helps you audit critical API calls and enhance security visibility.

## 1. Access CloudTrail Event History

1. Sign in to the AWS Management Console and search for **CloudTrail**.
2. In the left-hand menu, select **Event history**.
3. Adjust the time range and apply filters as needed to narrow down results.

By default, Event history shows all recorded API calls, such as:

* `CreateBucket`
* `PutBucketEncryption`
* `ConsoleLogin`
* `TerminateInstances`

<Callout icon="lightbulb" color="#1CB2FE">
  Ensure your IAM user or role has the `cloudtrail:LookupEvents` permission to view event history.
</Callout>

## 2. Filter for TerminateInstances Events

1. In the **Event name** filter, type `TerminateInstances`.
2. (Optional) Under **Resource name**, enter the instance ID:
   ```text  theme={null}
   i-02287a6b78cc71d91
   ```

Now you should see the specific `TerminateInstances` event for the target instance. The summary row displays the IAM user, timestamp, and event name.

## 3. Inspect Event Details

Click the `TerminateInstances` entry to expand the details pane. You’ll find several sections:

### 3.1 User Identity & Metadata

```json  theme={null}
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAZZBPMTHEGGK6QLMU",
    "arn": "arn:aws:iam::672261773768:user/John",
    "accountId": "672261773768",
    "accessKeyId": "ASIAZZBPMTHEGOIBHXVW",
    "userName": "John",
    "sessionContext": {
      "attributes": {
        "creationDate": "2023-10-16T17:24:53Z",
        "mfaAuthenticated": "false"
      }
    }
  },
  "eventTime": "2023-10-16T17:25:20Z",
  "eventSource": "ec2.amazonaws.com"
}
```

This indicates:

* IAM user **John** (`principalId`: `AIDAZZBPMTHEGGK6QLMU`)
* Event timestamp: `2023-10-16T17:25:20Z`
* API source: `ec2.amazonaws.com`

### 3.2 Instance State Transition

Scroll down to **Response elements** to view the state change:

```json  theme={null}
{
  "responseElements": {
    "requestId": "77104859-e0f6-4465-a836-830c1cb8583e",
    "instancesSet": {
      "items": [
        {
          "instanceId": "i-02287a6b78cc71d91",
          "previousState": {
            "code": 16,
            "name": "running"
          },
          "currentState": {
            "code": 32,
            "name": "shutting-down"
          }
        }
      ]
    }
  }
}
```

| State         | Code | Meaning       |
| ------------- | ---- | ------------- |
| previousState | 16   | Running       |
| currentState  | 32   | Shutting-down |

This confirms the `TerminateInstances` call initiated a shutdown.

## 4. Summary of Event Record

At the bottom of the details pane, you’ll find additional metadata:

```json  theme={null}
{
  "eventID": "0ea6b2d5-51d5-4765-ad83-4db65d506d9c",
  "readOnly": false,
  "eventType": "AwsApiCall",
  "managementEvent": true,
  "recipientAccountId": "672261773768",
  "eventCategory": "Management"
}
```

| Field              | Sample Value                         | Description                            |
| ------------------ | ------------------------------------ | -------------------------------------- |
| eventID            | 0ea6b2d5-51d5-4765-ad83-4db65d506d9c | Unique ID for the CloudTrail event     |
| eventType          | AwsApiCall                           | Type of API call                       |
| managementEvent    | true                                 | Indicates a management-level operation |
| recipientAccountId | 672261773768                         | AWS account where the event occurred   |

From this audit trail, you’ve confirmed that **John** executed the `TerminateInstances` API call, changing the instance from **running** to **shutting-down**.

## 5. Automate Alerts with EventBridge

Integrate these CloudTrail logs with Amazon EventBridge (formerly CloudWatch Events) to trigger alerts or remediation workflows when critical actions occur:

```bash  theme={null}
aws events put-rule \
  --name EC2TerminationRule \
  --event-pattern '{
    "source": ["aws.ec2"],
    "detail-type": ["AWS API Call via CloudTrail"],
    "detail": {
      "eventName": ["TerminateInstances"]
    }
  }'
```

Attach a target (e.g., SNS topic, Lambda function) to notify your team or perform automated checks.

## References

* [AWS CloudTrail User Guide](https://docs.aws.amazon.com/cloudtrail/latest/userguide/)
* [Amazon EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/)
* [EC2 TerminateInstances API](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_TerminateInstances.html)