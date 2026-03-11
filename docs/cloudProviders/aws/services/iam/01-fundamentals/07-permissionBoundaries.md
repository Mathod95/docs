---
title: Permission Boundaries
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-IAM/Introduction-to-AWS-Identity-and-Access-Management/IAM-Permission-Boundaries/page
  - https://notes.kodekloud.com/docs/AWS-IAM/Introduction-to-AWS-Identity-and-Access-Management/Demo-Permission-Boundaries/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-iam/module/84a65700-7455-4ad8-aeb5-27dfaf07b8cc/lesson/b39e535a-f5b7-4f71-b27e-ede3d528f0e1
---

> This guide explains how to use permission boundaries in IAM to enforce least privilege for new users like interns.

In this guide, you’ll learn how to enforce the principle of least privilege for new IAM users—such as interns—by using **permission boundaries**. This lets you assign them to existing groups (e.g., Accounting and Dev) without granting any permissions beyond what you intend.

<Frame>
  ![The image shows a diagram with two groups, "Accounting Group" and "Dev Group," each containing a red bucket icon linked to a checklist icon. The text at the top reads, "Manager Request: We are hiring interns."](https://kodekloud.com/kk-media/image/upload/v1752863053/notes-assets/images/AWS-IAM-IAM-Permission-Boundaries/manager-request-hiring-interns-diagram.jpg)
</Frame>

Currently, both the Accounting Group and the Dev Group have rights to specific S3 buckets. If you simply add interns to these groups:

* Accounting interns could view or modify confidential financial data.
* Dev interns could access or change log files in S3.

To prevent over-permissioning, apply a **permission boundary** that caps the maximum actions an intern can perform—even if their group policies allow more.

## What Is a Permission Boundary?

A permission boundary is an advanced IAM feature that specifies the upper limit of permissions an identity (user or role) can have. No matter how many permissions you attach via identity-based or group policies, the boundary ensures the principal cannot exceed its scope.

<Frame>
  ![The image explains the concept of a "Permission Boundary" in IAM, highlighting its role in setting maximum permissions, preventing unintended access, restricting IAM policies, and controlling permission scope for users and roles.](https://kodekloud.com/kk-media/image/upload/v1752863054/notes-assets/images/AWS-IAM-IAM-Permission-Boundaries/permission-boundary-iam-concept-explanation.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  Permission boundaries do **not** grant permissions by themselves. They only restrict the maximum permissions that an IAM principal can utilize.
</Callout>

## Step-by-Step: Create and Attach a Permission Boundary

Follow these steps in the AWS Management Console:

| Step | Console Navigation      | Action                                                                            |
| ---- | ----------------------- | --------------------------------------------------------------------------------- |
| 1    | IAM Dashboard           | Click **Policies** → **Create policy**                                            |
| 2    | **JSON** tab            | Paste the boundary policy definition (see below)                                  |
| 3    | Review policy           | Name it `InternBoundaryPolicy` and create                                         |
| 4    | **Users** → Select User | Under **Permissions** pick **Add permissions boundary** and attach the new policy |

```json  theme={null}
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::example-log-bucket"
      ]
    }
  ]
}
```

<Frame>
  ![The image is a tutorial slide titled "Create Permission Boundary," showing a stick figure labeled "Demo" and instructions for creating a permission boundary on AWS.](https://kodekloud.com/kk-media/image/upload/v1752863056/notes-assets/images/AWS-IAM-IAM-Permission-Boundaries/create-permission-boundary-tutorial-slide.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Even if an intern’s group policy grants broader access, they cannot exceed the actions allowed by their permission boundary.
</Callout>

## Assigning Interns to Groups

Once the boundary is in place:

1. Attach the `InternBoundaryPolicy` as a permissions boundary to each intern’s IAM user.
2. Add the intern to the relevant group (Accounting or Dev).
3. The intern inherits group permissions, but all actions are capped by the boundary.

## Benefits of Using Permission Boundaries

| Benefit                 | Description                                                     |
| ----------------------- | --------------------------------------------------------------- |
| Enforce Least Privilege | Limits every principal to only the actions you explicitly allow |
| Granular Control        | Applies max-permission caps even when multiple policies overlap |
| Risk Mitigation         | Prevents accidental or malicious privilege escalation           |

## References

* [Permission Boundaries in AWS IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html)
* [IAM JSON Policy Elements](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html#access_policies-json)
* [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

> This tutorial demonstrates enforcing least privilege in AWS IAM using permission boundaries to restrict a new users effective permissions.

In this tutorial, we’ll demonstrate how to enforce the principle of least privilege in AWS IAM by using permission boundaries. You’ll learn how to restrict a new user’s effective permissions so that they can only list S3 buckets without gaining full access.

## 1. Identify the Target S3 Bucket

First, open the Amazon S3 Management Console. Filter your buckets by the prefix “Company1” and locate **company1-logs**, which stores daily logs used by your development team.

<Frame>
  ![The image shows an AWS S3 Management Console with a list of buckets named "company1-hr," "company1-logs," and "company1-sales," all located in the US West (Oregon) region and marked as not public.](https://kodekloud.com/kk-media/image/upload/v1752863041/notes-assets/images/AWS-IAM-Demo-Permission-Boundaries/aws-s3-management-console-buckets.jpg)
</Frame>

## 2. Review Customer-Managed Policies

Next, navigate to the IAM console and filter customer-managed policies by “company1.” You should see:

<Frame>
  ![The image shows the AWS Identity and Access Management (IAM) console, displaying a list of customer-managed policies filtered by "company1," including "Company1-Logs-Policy" and "Company1\_List\_S3\_Buckets."](https://kodekloud.com/kk-media/image/upload/v1752863042/notes-assets/images/AWS-IAM-Demo-Permission-Boundaries/aws-iam-console-company1-policies.jpg)
</Frame>

| Policy Name                 | Purpose                             | Key Actions                                                        |
| --------------------------- | ----------------------------------- | ------------------------------------------------------------------ |
| Company1-Logs-Policy        | Full S3 access to `company1-logs`   | `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` |
| Company1\_List\_S3\_Buckets | Read-only listing of all S3 buckets | `s3:ListAllMyBuckets`, `s3:GetBucketLocation`                      |

## 3. Inspect the Full-Access Logs Policy

Click on **Company1-Logs-Policy** to view its JSON document. This policy grants any principal full control over the `company1-logs` bucket.

<Frame>
  ![The image shows an AWS Identity and Access Management (IAM) console screen, displaying a customer-managed policy with full access permissions for the S3 service.](https://kodekloud.com/kk-media/image/upload/v1752863044/notes-assets/images/AWS-IAM-Demo-Permission-Boundaries/aws-iam-console-s3-full-access-policy.jpg)
</Frame>

Currently, this policy is attached to the **Developers** group. All members—like John—inherit full S3 permissions on `company1-logs`.

***

## 4. Scenario: Hiring a New Intern

We’ve hired an intern, Sara, but we want to limit her permissions to bucket listing only. Without adjustments, adding her to the Developers group would grant full S3 access.

1. In the IAM console, click **Create User**.
2. Enter **Sara-intern** as the username.
3. Enable **AWS Management Console access**, generate a password, and require a reset on first login.
4. Add **Sara-intern** to the **Developers** group and complete the user creation.

<Frame>
  ![The image shows the AWS Management Console interface for creating a new IAM user, with a username "Sara-intern" being specified.](https://kodekloud.com/kk-media/image/upload/v1752863046/notes-assets/images/AWS-IAM-Demo-Permission-Boundaries/aws-management-console-iam-user-sara.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  By default, Sara inherits every permission granted to the Developers group. We need a permissions boundary to cap her maximum privileges.
</Callout>

***

## 5. Apply the Permissions Boundary

To restrict Sara’s permissions:

1. Open **Sara-intern**’s user summary and go to the **Permissions** tab.
2. Click **Set permissions boundary**.
3. Select **Company1\_List\_S3\_Buckets** and save.

<Frame>
  ![The image shows an AWS IAM Management Console screen where a user is setting a permissions boundary for "Sara-intern." Two customer-managed policies are listed: "Company1\_List\_S3\_Buckets" and "Company1-Logs-Policy."](https://kodekloud.com/kk-media/image/upload/v1752863047/notes-assets/images/AWS-IAM-Demo-Permission-Boundaries/aws-iam-console-permissions-sara-intern.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  A permissions boundary only defines the maximum rights a user can have. The user’s effective permissions are the intersection of their group policies and the boundary. Always validate by testing in a non-production account.
</Callout>

With **Company1\_List\_S3\_Buckets** as Sara’s boundary, she can list bucket names (`s3:ListAllMyBuckets`) but cannot read, write, or delete any objects. This enforces least privilege for new users.

***

## References

* [AWS IAM Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
* [Using Permissions Boundaries for IAM Identities](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html)
* [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/index.html)