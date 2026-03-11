---
title: Cross Account Access
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/IAM-Cross-Account-Access/page
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/Demo-Cross-Account-Access/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/e72b296f-b510-4465-84b8-134098f91397?autoplay=true
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/5ef16daf-a5e1-49f8-9ccf-86fd97474311
---

> This guide configures cross-account access between AWS accounts for secure log retrieval from an S3 bucket without sharing long-term credentials.

In this guide, we'll configure cross-account access between a **Production** AWS account (owns an S3 log bucket) and a **Development** AWS account (hosts a Log Analysts group). This setup enables secure, temporary access to logs without sharing long-term credentials.

## Scenario

| AWS Account         | Resource                   | Purpose                                     |
| ------------------- | -------------------------- | ------------------------------------------- |
| Production Account  | S3 bucket (`log-bucket`)   | Stores application log files                |
| Development Account | IAM Group (`Log Analysts`) | Needs permission to list and read log files |

Our objective is to let the `Log Analysts` group assume a role in the Production account to retrieve logs.

## High-Level Architecture

1. Create an IAM Role in the **Production Account**
2. Attach an inline S3 policy to that role
3. Update the **S3 Bucket Policy** to trust the role
4. Assume the role from the **Development Account** and verify access

<Frame>
  ![The image is a diagram showing a request to provide log access to a Log Analysts group, involving a production account with an S3 bucket and a dev account with a log access role.](https://kodekloud.com/kk-media/image/upload/v1752862970/notes-assets/images/AWS-IAM-IAM-Cross-Account-Access/log-access-request-diagram-s3-dev.jpg)
</Frame>

## Cross-Account Access Components

| Component            | Description                                                                       |
| -------------------- | --------------------------------------------------------------------------------- |
| Trust Relationship   | IAM Role trust policy in the Production account allowing Dev account to assume it |
| Role Assumption      | `sts:AssumeRole` call from Dev account for temporary credentials                  |
| Permissions Boundary | Inline policy (or managed) on the role controls S3 access                         |
| Resource Policy      | S3 Bucket policy grants the role `s3:ListBucket` and `s3:GetObject`               |

<Frame>
  ![The image explains IAM Cross Account Access Capability, highlighting the implementation of cross-account access, the need for a trust relationship, role assumption by users, and the security benefits of resource isolation.](https://kodekloud.com/kk-media/image/upload/v1752862971/notes-assets/images/AWS-IAM-IAM-Cross-Account-Access/iam-cross-account-access-diagram.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  Be explicit in your trust policy to avoid granting unintended access. Restrict `Principal` to specific IAM roles or account IDs.
</Callout>

## Demo Walkthrough

Follow these steps to implement and test cross-account S3 access.

### 1. Create the IAM Role in Production

Create a trust policy (`trust-policy.json`):

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::DEV_ACCOUNT_ID:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Use the AWS CLI to create the role:

```bash  theme={null}
aws iam create-role \
  --role-name DevLogAccessRole \
  --assume-role-policy-document file://trust-policy.json \
  --description "Allows Dev account to access logs" \
  --profile prod-account
```

### 2. Attach an Inline S3 Access Policy

Define `s3-access-policy.json`:

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::log-bucket",
        "arn:aws:s3:::log-bucket/*"
      ]
    }
  ]
}
```

Attach it to the role:

```bash  theme={null}
aws iam put-role-policy \
  --role-name DevLogAccessRole \
  --policy-name S3LogAccess \
  --policy-document file://s3-access-policy.json \
  --profile prod-account
```

### 3. Update the S3 Bucket Policy

Create or edit your bucket policy (`bucket-policy.json`):

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDevRoleAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::PROD_ACCOUNT_ID:role/DevLogAccessRole"
      },
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::log-bucket",
        "arn:aws:s3:::log-bucket/*"
      ]
    }
  ]
}
```

Apply it:

```bash  theme={null}
aws s3api put-bucket-policy \
  --bucket log-bucket \
  --policy file://bucket-policy.json \
  --profile prod-account
```

<Callout icon="triangle-alert" color="#FF6B6B">
  Ensure the bucket policy’s `Principal` matches the exact ARN of the role. Using wildcards may expose your bucket to unintended access.
</Callout>

### 4. Assume the Role and Verify Access

From the Development account, assume the role:

```bash  theme={null}
aws sts assume-role \
  --role-arn arn:aws:iam::PROD_ACCOUNT_ID:role/DevLogAccessRole \
  --role-session-name LogAnalysisSession \
  --profile dev-account > assume-role-output.json
```

Export temporary credentials:

```bash  theme={null}
export AWS_ACCESS_KEY_ID=$(jq -r '.Credentials.AccessKeyId' assume-role-output.json)
export AWS_SECRET_ACCESS_KEY=$(jq -r '.Credentials.SecretAccessKey' assume-role-output.json)
export AWS_SESSION_TOKEN=$(jq -r '.Credentials.SessionToken' assume-role-output.json)
```

List and retrieve logs:

```bash  theme={null}
aws s3 ls s3://log-bucket
aws s3 cp s3://log-bucket/example.log .
```

## References

* [AWS IAM Roles](https://docs.aws.amazon.com/iam/latest/UserGuide/id_roles.html)
* [AWS STS AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html)
* [Amazon S3 Bucket Policies](https://docs.aws.amazon.com/AmazonS3/latest/dev/using-iam-policies.html)

---

> Enable cross-account S3 access by configuring bucket policies, creating IAM roles, and testing access via AWS CloudShell.

Enable a role in your **source account** (ID: 672261773768) to read objects from an S3 bucket in your **target account** (ID: …2021). This walkthrough covers:

* Configuring the bucket policy
* Creating and trusting an IAM role
* Testing access via AWS CloudShell

| Step | Description                                 |
| ---- | ------------------------------------------- |
| 1    | Add a bucket policy in the target account   |
| 2    | Create IAM policy & role with trust policy  |
| 3    | Assume role and verify access in CloudShell |

***

## 1. Configure the Bucket Policy in the Target Account

In the target account, go to **S3 > company1-logs > Permissions > Bucket policy** and paste:

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::6294702402021:role/LogAnalystsRole"
      },
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": [
        "arn:aws:s3:::company1-logs",
        "arn:aws:s3:::company1-logs/*"
      ]
    }
  ]
}
```

<Frame>
  ![The image shows an Amazon S3 bucket interface named "company1-logs" with two text files, "Logs1.txt" and "Logs2.txt," each 18 bytes in size. The interface displays options for managing the files, such as copying URLs, downloading, and deleting.](https://kodekloud.com/kk-media/image/upload/v1752862964/notes-assets/images/AWS-IAM-Demo-Cross-Account-Access/amazon-s3-bucket-company1-logs.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  Ensure the bucket ARN and role ARN exactly match your resources. Typos in ARNs will prevent access.
</Callout>

***

## 2. Create the IAM Role in the Target Account

### 2.1 Define a Read-Only Policy

Create an IAM policy named **company1-logs-read-policy**:

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": [
        "arn:aws:s3:::company1-logs",
        "arn:aws:s3:::company1-logs/*"
      ]
    }
  ]
}
```

### 2.2 Create the Role and Configure Trust

1. In IAM, create a role called **LogAnalystsRole**.
2. Attach **company1-logs-read-policy**.
3. Edit **Trust relationships** to allow the source account user (`amin`) to assume this role:

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::672261773768:user/amin"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

<Frame>
  ![The image shows an AWS Identity and Access Management (IAM) console displaying details of a role named "LogAnalystsRole," including its creation date, ARN, and other related information.](https://kodekloud.com/kk-media/image/upload/v1752862965/notes-assets/images/AWS-IAM-Demo-Cross-Account-Access/aws-iam-console-loganalystsrole-details.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Grant only the minimum privileges needed. Review your trust policy to prevent unauthorized access.
</Callout>

***

## 3. Test Cross-Account Access via CloudShell

1. Confirm your caller identity in the **source account**:
   ```bash  theme={null}
   aws sts get-caller-identity
   ```
2. Assume the cross-account role:
   ```bash  theme={null}
   aws sts assume-role \
     --role-arn arn:aws:iam::6294702402021:role/LogAnalystsRole \
     --role-session-name CrossAccountSession
   ```
3. Export the temporary credentials:
   ```bash  theme={null}
   export AWS_DEFAULT_REGION=us-east-2
   export AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY_ID>
   export AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_ACCESS_KEY>
   export AWS_SESSION_TOKEN=<YOUR_SESSION_TOKEN>
   ```
4. Verify you’re now the assumed role:
   ```bash  theme={null}
   aws sts get-caller-identity
   ```
   You should see an ARN with `assumed-role/LogAnalystsRole`.
5. List bucket contents:
   ```bash  theme={null}
   aws s3 ls s3://company1-logs
   ```
   Expected output:
   ```text  theme={null}
   2023-01-01 12:00:00        18 Logs1.txt
   2023-01-01 12:00:00        18 Logs2.txt
   ```

If you see the log files listed, your cross-account S3 access is working!

***

## Links and References

* [Amazon S3 Bucket Policies](https://docs.aws.amazon.com/AmazonS3/latest/dev/using-iam-policies.html)
* [IAM Trust Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html)
* [AWS STS AssumeRole](https://docs.aws.amazon.com/cli/latest/reference/sts/assume-role.html)
