---
title: Roles
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-IAM/Introduction-to-AWS-Identity-and-Access-Management/IAM-Roles/page
  - https://notes.kodekloud.com/docs/AWS-IAM/Introduction-to-AWS-Identity-and-Access-Management/Demo-Creating-IAM-Role/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-iam/module/84a65700-7455-4ad8-aeb5-27dfaf07b8cc/lesson/9f7a8d66-7718-45f8-af35-8daf997b42f5
  - https://learn.kodekloud.com/user/courses/aws-iam/module/84a65700-7455-4ad8-aeb5-27dfaf07b8cc/lesson/7fab0038-fbf9-404f-934e-901c9a532c7a
---

> AWS IAM roles provide secure, temporary access to resources, enabling fine-grained permissions and trust relationships while minimizing exposure risk.

AWS Identity and Access Management (IAM) roles enable secure, temporary access to AWS resources without embedding long-term credentials. By defining fine-grained permissions and trust relationships, you can enforce the principle of least privilege and reduce exposure risk.

| Component          | Description                                                                 | Example                                          |
| ------------------ | --------------------------------------------------------------------------- | ------------------------------------------------ |
| Role               | An identity with attached permissions and a trust policy                    | `S3AccessRole`                                   |
| Permissions Policy | A JSON document specifying allowed or denied actions                        | `AmazonS3ReadOnlyAccess`                         |
| Trust Policy       | Defines which principals (services, users, or accounts) can assume the role | EC2 service: `ec2.amazonaws.com`                 |
| Temporary Tokens   | Short-lived credentials issued by AWS STS                                   | `AccessKeyId`, `SecretAccessKey`, `SessionToken` |

<Frame>
  ![The image explains IAM roles, highlighting their use for access control, adherence to the principle of least privilege, creation of temporary credentials, and establishment of trust relationships.](https://kodekloud.com/kk-media/image/upload/v1752863063/notes-assets/images/AWS-IAM-IAM-Roles/iam-roles-access-control-diagram.jpg)
</Frame>

## How IAM Roles Enhance Security

Instead of hard-coding long-term AWS keys:

1. A principal (user or service) calls `sts:AssumeRole`.
2. AWS returns temporary credentials.
3. The principal uses these credentials to access resources.
4. Credentials expire automatically, minimizing the blast radius.

<Callout icon="lightbulb" color="#1CB2FE">
  Always follow the [principle of least privilege](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege). Grant only the permissions required for the task.
</Callout>

### Role Assumption Flow

<Frame>
  ![The image illustrates a process for increasing security using IAM roles, showing the flow from an IAM user assuming a role, applying a policy, accessing an S3 role, and obtaining temporary keys.](https://kodekloud.com/kk-media/image/upload/v1752863064/notes-assets/images/AWS-IAM-IAM-Roles/iam-roles-security-process-diagram.jpg)
</Frame>

Roles can be assumed not only by IAM users but also by AWS services such as EC2, Lambda, and ECS. The permissions come from attached policies, while the trust policy specifies who can assume the role.

### AWS Components Interaction

<Frame>
  ![The image is a diagram illustrating the relationship between AWS components: EC2 Service, S3 Bucket, IAM Role, IAM Policy, and IAM User. It shows how these components interact with each other in an AWS IAM Role setup.](https://kodekloud.com/kk-media/image/upload/v1752863065/notes-assets/images/AWS-IAM-IAM-Roles/aws-ec2-s3-iam-relationship-diagram.jpg)
</Frame>

***

## Demo: Create an IAM Role for EC2 to Access S3

Follow these steps in the AWS Management Console or use the AWS CLI commands shown.

### Console Steps

1. **Open the IAM console**\
   [https://console.aws.amazon.com/iam](https://console.aws.amazon.com/iam)

2. **Create a new role**
   * In the navigation pane, choose **Roles** → **Create role**.
   * Under **Select trusted entity**, choose **AWS service**, then **EC2**, and click **Next**.

3. **Attach permissions**
   * Search for **AmazonS3ReadOnlyAccess** (or attach your custom policy).
   * Select it and click **Next**.

4. **Name and create**
   * Enter **Role name**: `S3AccessRole`
   * Review settings and click **Create role**.

5. **Attach the role to an existing EC2 instance**
   * Open the EC2 console, select your instance.
   * Choose **Actions** → **Security** → **Modify IAM role**.
   * Select **S3AccessRole** and click **Save**.

### AWS CLI Alternative

First, create a trust policy file (`trust-policy.json`):

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "ec2.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Then run:

```bash  theme={null}
# Create the role
aws iam create-role \
  --role-name S3AccessRole \
  --assume-role-policy-document file://trust-policy.json

# Attach the AmazonS3ReadOnlyAccess policy
aws iam attach-role-policy \
  --role-name S3AccessRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

***

## Verify from the EC2 Instance

SSH into your EC2 instance and confirm the role is in effect:

```bash  theme={null}
# Check the caller identity (should show the assumed role ARN)
aws sts get-caller-identity

# List S3 buckets or contents to verify permissions
aws s3 ls s3://your-bucket-name
```

If you see the bucket contents, the role is correctly configured—no long-term keys required.

***

## References

* [AWS IAM Roles Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
* [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
* [AWS STS AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html)

---

> This guide explains how to create an IAM role for EC2 instances to access an S3 bucket securely.

In this step-by-step guide, you'll learn how to create an AWS Identity and Access Management (IAM) role that grants an Amazon EC2 instance permission to read objects from an S3 bucket named `company1-logs`. By leveraging IAM roles, you avoid hardcoding credentials on your server and follow AWS best practices for secure access management.

## Prerequisites

* An AWS account with administrative privileges
* A running EC2 instance
* An existing S3 bucket named `company1-logs`

## Step 1: Create the IAM Role

1. Open the [IAM console](https://console.aws.amazon.com/iam/), select **Roles**, then click **Create role**.
2. On **Select trusted entity**, choose **AWS service**.

<Frame>
  ![The image shows an AWS IAM console screen for creating a role, specifically the step to select a trusted entity type, with options like AWS service, AWS account, Web identity, SAML 2.0 federation, and custom trust policy.](https://kodekloud.com/kk-media/image/upload/v1752863020/notes-assets/images/AWS-IAM-Demo-Creating-IAM-Role/aws-iam-console-create-role-trusted-entity.jpg)
</Frame>

3. Under **Use cases for other AWS services**, select **EC2**.

<Frame>
  ![The image shows an AWS IAM console screen where a user is selecting a use case for creating a role, with options related to EC2 services.](https://kodekloud.com/kk-media/image/upload/v1752863021/notes-assets/images/AWS-IAM-Demo-Creating-IAM-Role/aws-iam-console-ec2-role-selection.jpg)
</Frame>

4. Click **Next** to move to the permissions page.
5. In **Permissions**, search for **company1** and select the **Company1 logs policy** which grants `s3:GetObject` access to the `company1-logs` bucket.

<Frame>
  ![The image shows an AWS IAM console screen where permissions are being added to a role. Two customer-managed policies are listed, with one selected.](https://kodekloud.com/kk-media/image/upload/v1752863023/notes-assets/images/AWS-IAM-Demo-Creating-IAM-Role/aws-iam-console-role-permissions-policies.jpg)
</Frame>

6. Click **Next**, then enter a **Role name** (e.g., `Company1-Logs-Role`) and an optional description.

<Frame>
  ![The image shows an AWS IAM console screen where a role is being created, with fields for role name and description filled in. The role name is "Company1-Logs-Role," and the description mentions allowing EC2 instances to call AWS services.](https://kodekloud.com/kk-media/image/upload/v1752863024/notes-assets/images/AWS-IAM-Demo-Creating-IAM-Role/aws-iam-console-role-creation.jpg)
</Frame>

7. Review the **Trust relationship** to ensure EC2 can assume this role. It should resemble:

   ```json  theme={null}
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["sts:AssumeRole"],
         "Principal": {"Service": ["ec2.amazonaws.com"]}
       }
     ]
   }
   ```
8. (Optional) Add tags to categorize your role, then click **Create role**.

<Callout icon="lightbulb" color="#1CB2FE">
  You’ve successfully created an IAM role that EC2 instances can assume to access S3 resources securely.
</Callout>

## Step 2: Attach the IAM Role to Your EC2 Instance

1. Go to the [EC2 console](https://console.aws.amazon.com/ec2/), select **Instances**, and choose your running instance.
2. From the **Actions** menu, select **Security > Modify IAM role**.
3. In the **IAM role** dropdown, pick **Company1-Logs-Role**.

<Frame>
  ![The image shows an AWS console interface for modifying an IAM role attached to an EC2 instance. It includes a dropdown to select an IAM role and a warning about removing existing roles.](https://kodekloud.com/kk-media/image/upload/v1752863025/notes-assets/images/AWS-IAM-Demo-Creating-IAM-Role/aws-console-iam-role-ec2-instance.jpg)
</Frame>

4. Click **Update IAM role** to apply the change.

<Callout icon="triangle-alert" color="#FF6B6B">
  If your EC2 instance already has an IAM role attached, updating it will replace the existing role and associated permissions. Ensure this change aligns with your security policies.
</Callout>

Your EC2 instance now inherits the permissions defined in `Company1-Logs-Role`, allowing it to securely read log files from the `company1-logs` bucket without embedded credentials.

## References

* [AWS IAM Roles Documentation](https://docs.aws.amazon.com/iam/latest/UserGuide/id_roles.html)
* [Amazon EC2 IAM Roles](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
* [Managing Access to S3 Buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-iam-policies.html)