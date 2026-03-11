---
title: Identity Center
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/IAM-Identity-Center/page
  - https://notes.kodekloud.com/docs/AWS-IAM/Configure-AWS-IAM-at-Scale/Demo-IAM-Identity-Center/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/8ef1cadc-3cb3-44c5-b7fa-0d87b6a949af
  - https://learn.kodekloud.com/user/courses/aws-iam/module/586f5114-fd4d-45e3-88ba-6a691fde129c/lesson/c0ec95bf-93dc-47c2-98e0-7a2aa4b6e813
---

> AWS IAM Identity Center offers centralized identity management and single sign-on for AWS Organizations, enhancing access control across multiple accounts.

AWS IAM Identity Center provides a unified, organizational-level identity management solution for your AWS Organization. While AWS IAM manages users and groups within a single account, IAM Identity Center lets you centralize access, identities, and single sign-on (SSO) across multiple member accounts from your management account.

## Key Features

| Feature              | Description                                                                   | Benefit                                      |
| -------------------- | ----------------------------------------------------------------------------- | -------------------------------------------- |
| Centralized Access   | Assign and manage permissions across all member accounts in your Organization | Consistent, audit-ready permission model     |
| User Identities      | Create users in AWS or connect to external identity providers (Okta, AD)      | Flexible identity source, no separate sync   |
| Single Sign-On (SSO) | Integrate cloud apps and AWS accounts for seamless access                     | One-click access to all authorized resources |

<Frame>
  ![The image describes IAM Identity Center features, highlighting centralized access, user identities, and single sign-on capabilities.](https://kodekloud.com/kk-media/image/upload/v1752862973/notes-assets/images/AWS-IAM-IAM-Identity-Center/iam-identity-center-access-features.jpg)
</Frame>

***

## Demo: Enabling IAM Identity Center

Follow these steps to enable IAM Identity Center (formerly AWS SSO) in your Organization.

<Callout icon="lightbulb" color="#1CB2FE">
  Ensure your AWS Organization is active and you have Management Account privileges before proceeding.
</Callout>

### 1. Verify SSO Status in a Member Account

1. Sign in to a **member account**.
2. Go to **IAM Identity Center** in the AWS Console.
3. You’ll see a message indicating SSO isn’t enabled yet.

### 2. Enable in the Management Account

1. Switch to your **Management Account**.
2. Open the **IAM Identity Center** page.
3. Click **Enable IAM Identity Center** to activate SSO for all member accounts.

<Frame>
  ![The image is a slide titled "Demo: Enable IAM Identity Center," featuring an illustration of a person with a speech bubble labeled "Demo" and instructions for enabling the IAM Identity Center for single sign-on.](https://kodekloud.com/kk-media/image/upload/v1752862974/notes-assets/images/AWS-IAM-IAM-Identity-Center/enable-iam-identity-center-demo-slide.jpg)
</Frame>

### (Optional) CLI Alternative

You can also enable SSO programmatically using the AWS CLI:

```bash  theme={null}
aws sso-admin enable-sso \
  --region us-east-1 \
  --cli-input-json file://enable-sso-config.json
```

## Links and References

* [AWS IAM Identity Center Documentation](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
* [AWS Organizations Overview](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
* [AWS CLI SSO Admin Commands](https://docs.aws.amazon.com/cli/latest/reference/sso-admin/index.html)

---

> This guide explains how to enable and use AWS IAM Identity Center for managing user and group access across AWS accounts and applications.

In this guide, you’ll learn how to enable and use AWS IAM Identity Center to centrally manage user and group access across multiple AWS accounts and cloud applications.

## Prerequisites

* An AWS Organizations management account
* Permissions to manage IAM Identity Center and AWS Organizations

<Callout icon="lightbulb" color="#1CB2FE">
  IAM Identity Center can only be enabled from your organization’s management account. Member accounts cannot enable or configure it.
</Callout>

## Enabling IAM Identity Center

1. Sign in to the AWS Management Console with your **management account**.
2. In the top search bar, type **IAM Identity Center** and select it:

<Frame>
  ![The image shows the AWS Console Home with a search for "IAM Identity Center," displaying services like IAM Identity Center, IAM, Cloud9, and Amazon CodeWhisperer.](https://kodekloud.com/kk-media/image/upload/v1752862966/notes-assets/images/AWS-IAM-Demo-IAM-Identity-Center/aws-console-home-iam-identity-center.jpg)
</Frame>

3. Click **Enable**.
4. Choose your identity source:
   * Connect an existing directory (AWS Managed Microsoft AD, AD Connector, or external IdP)
   * Use the built-in Identity Center directory
5. After activation, create users and groups (if using the built-in directory), then assign permission sets to your AWS accounts or cloud applications.

## IAM vs. IAM Identity Center

When you go to the **IAM** console and click **Create user**, selecting **Provide console access** will direct you to specify an Identity Center user:

<Frame>
  ![The image shows a webpage from the AWS Management Console, specifically the "Specify user details" section for creating a new user in IAM. It includes fields for entering a username and options for providing console access.](https://kodekloud.com/kk-media/image/upload/v1752862968/notes-assets/images/AWS-IAM-Demo-IAM-Identity-Center/aws-iam-create-user-console-access.jpg)
</Frame>

Use the following table to decide between IAM users and IAM Identity Center:

| Capability                        | IAM User           | IAM Identity Center               |
| --------------------------------- | ------------------ | --------------------------------- |
| Console access across accounts    | Manual per account | Centralized via permission sets   |
| Programmatic access (access keys) | Yes                | No (create separate IAM users)    |
| Service-specific credentials      | Yes                | No                                |
| External identity federation      | Limited            | Built-in SAML and OIDC support    |
| Multi-account role assignments    | Manual             | Automated through a single portal |

<Callout icon="triangle-alert" color="#FF6B6B">
  Reserve IAM users for programmatic or service-specific credentials. For scalable, centralized console access across multiple accounts, adopt IAM Identity Center.
</Callout>

## References

* [AWS IAM Identity Center User Guide](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
* [AWS Organizations Documentation](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
* [AWS IAM User Guide](https://docs.aws.amazon.com/iam/latest/UserGuide/introduction.html)