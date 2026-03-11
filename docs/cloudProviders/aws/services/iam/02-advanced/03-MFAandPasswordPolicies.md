---
title: MFA and Password Policies
status: draft
sources: 
  - https://notes.kodekloud.com/docs/AWS-IAM/IAM-Policies-Federation-STS-and-MFA/MFA-and-Password-Policies/page
  - https://notes.kodekloud.com/docs/AWS-IAM/IAM-Policies-Federation-STS-and-MFA/Demo-MFA-and-Password-Policies/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-iam/module/8ffebc04-c194-403a-ac2e-2a2f0a6221ce/lesson/0d0f7d82-9b0f-46d9-a426-7ae39b8a597c
  - https://learn.kodekloud.com/user/courses/aws-iam/module/8ffebc04-c194-403a-ac2e-2a2f0a6221ce/lesson/375879f4-c1ae-4165-837d-69d3892ce0cd
---

> This guide explains enabling MFA and strong password policies in AWS IAM to enhance account security.

Enhancing your AWS account’s security posture involves two critical measures:

1. Enabling Multi-Factor Authentication (MFA) for IAM users
2. Defining and enforcing a robust password policy

This guide explains why MFA and strong password rules matter, outlines the key policy settings, and provides step-by-step instructions to configure both in the AWS Management Console.

***

## Why Enforce Multi-Factor Authentication?

Multi-Factor Authentication adds an additional proof of identity beyond a username and password. After entering their credentials, users must supply a one-time code from a hardware token or a virtual MFA app like [Google Authenticator](https://support.google.com/accounts/answer/1066447). This secondary factor dramatically reduces the risk of unauthorized access, even if passwords are compromised.

<Callout icon="lightbulb" color="#1CB2FE">
  Virtual MFA apps (e.g., [Authy](https://authy.com/), [Google Authenticator](https://support.google.com/accounts/answer/1066447)) are free and easy to deploy across multiple devices.
</Callout>

***

## Understanding IAM Password Policies

By default, AWS IAM does not enforce any password policy. Creating a custom policy allows you to align password complexity, expiration, and reuse rules with your organization’s governance standards.

<Frame>
  ![The image outlines AWS password policies, highlighting account-level policies, default IAM policies, and the ability to configure custom policies based on governance requirements.](https://kodekloud.com/kk-media/image/upload/v1752862995/notes-assets/images/AWS-IAM-MFA-and-Password-Policies/aws-password-policies-account-iam-custom.jpg)
</Frame>

### Key Password Policy Settings

| Policy Setting                      | Description                                         | Example |
| ----------------------------------- | --------------------------------------------------- | ------- |
| Minimum password length             | Enforces a lower bound on characters                | 12      |
| Maximum password length             | (Optional) Caps password size to reduce system load | 128     |
| Require uppercase characters        | Ensures at least one `A–Z`                          | Enabled |
| Require lowercase characters        | Ensures at least one `a–z`                          | Enabled |
| Require numbers                     | Ensures at least one digit `0–9`                    | Enabled |
| Require non-alphanumeric characters | Ensures at least one symbol (e.g., `!@#$%^&*`)      | Enabled |
| Password expiration                 | Forces periodic password updates (in days)          | 90      |
| Prevent password reuse              | Blocks reuse of the last *N* passwords              | Last 5  |

<Callout icon="triangle-alert" color="#FF6B6B">
  Enabling password expiration **without** a notification process can lead to unexpected lockouts. Communicate expiration policies clearly to your team.
</Callout>

***

## Step-by-Step: Enable MFA and Configure a Password Policy

Follow these steps in the AWS Management Console:

### 1. Sign In to the AWS Management Console

* Navigate to [https://console.aws.amazon.com/](https://console.aws.amazon.com/) and open the **IAM** service.

### 2. Enable MFA for an IAM User

1. In the left sidebar, choose **Users**.
2. Select the target user name.
3. Open the **Security credentials** tab.
4. Under **Assigned MFA device**, click **Manage**.
5. Follow the prompts to activate a hardware or virtual MFA device.

### 3. Define Your Account Password Policy

1. From the IAM dashboard, click **Account settings**.
2. Under **Password policy**, select **Manage**.
3. Configure the policy using your organization’s minimums for length, complexity, expiration, and reuse.
4. Click **Save changes** to apply.

***

## References and Further Reading

* [AWS Identity and Access Management (IAM) Documentation](https://docs.aws.amazon.com/iam/latest/UserGuide/)
* [AWS MFA Best Practices](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_support-mfa.html)
* [Google Authenticator Overview](https://support.google.com/accounts/answer/1066447)

---

> This tutorial explains how to secure AWS environments by enabling Multi-Factor Authentication and enforcing custom password policies for IAM users.

In this tutorial, you’ll learn how to secure your AWS environment by enabling Multi-Factor Authentication (MFA) for IAM users and enforcing custom password policies in the AWS Identity and Access Management (IAM) console.

## Configuring MFA for an IAM User

1. Sign in to the AWS Management Console and open the **IAM** dashboard.
2. Select **Users** in the navigation pane to view all IAM accounts.

<Frame>
  ![The image shows an AWS Identity and Access Management (IAM) dashboard displaying a list of users with details such as username, path, groups, last activity, MFA, and password age.](https://kodekloud.com/kk-media/image/upload/v1752862979/notes-assets/images/AWS-IAM-Demo-MFA-and-Password-Policies/aws-iam-dashboard-users-list-details.jpg)
</Frame>

3. Click on the user **John**, then open the **Security credentials** tab.
4. Under **Multi-Factor Authentication (MFA)**, click **Assign MFA device**.

<Frame>
  ![The image shows an AWS Identity and Access Management (IAM) console screen, focusing on multi-factor authentication (MFA) settings for a user, with an option to assign an MFA device.](https://kodekloud.com/kk-media/image/upload/v1752862981/notes-assets/images/AWS-IAM-Demo-MFA-and-Password-Policies/aws-iam-console-mfa-settings.jpg)
</Frame>

5. Provide a **Device label** (for example, “MFA”) and choose your device type from the table below:

| Device Type         | Description                                                      |
| ------------------- | ---------------------------------------------------------------- |
| Virtual MFA device  | Software authenticator (Google Authenticator, Authy, Duo Mobile) |
| Security key        | FIDO2/WebAuthn hardware key                                      |
| Hardware TOTP token | Physical token generating time-based codes                       |

<Frame>
  ![The image shows an AWS IAM interface for selecting a multi-factor authentication (MFA) device, with options for an authenticator app, security key, and hardware TOTP token.](https://kodekloud.com/kk-media/image/upload/v1752862982/notes-assets/images/AWS-IAM-Demo-MFA-and-Password-Policies/aws-iam-mfa-device-selection-interface.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  Make sure your chosen authenticator app supports Time-based One-Time Passwords (TOTP).
</Callout>

6. To set up a **Virtual MFA device**:
   * Install and open a compatible authenticator app.
   * Scan the QR code displayed in the console.
   * Enter the two consecutive codes from your app (MFA Code 1 and MFA Code 2).
   * Click **Assign MFA** to finalize.

<Callout icon="triangle-alert" color="#FF6B6B">
  If you lose access to your MFA device and haven’t saved the seed key, you may need to contact your AWS account administrator or use your root credentials to regain access.
</Callout>

## Customizing Password Policies

1. In the IAM console, select **Account settings** to view the **Password policy** section.

2. Review the default requirements, which ensure basic password strength:

| Requirement               | Default Setting                                                  |
| ------------------------- | ---------------------------------------------------------------- |
| Minimum length            | 8 characters                                                     |
| Character categories      | At least 3 of: uppercase, lowercase, numbers, special characters |
| Exclusions                | Cannot match username or email address                           |
| Password expiration       | Disabled                                                         |
| Password reuse prevention | None                                                             |

<Frame>
  ![The image shows an AWS Identity and Access Management (IAM) account settings page, detailing the default password policy requirements, including minimum length and character types.](https://kodekloud.com/kk-media/image/upload/v1752862983/notes-assets/images/AWS-IAM-Demo-MFA-and-Password-Policies/aws-iam-account-settings-password-policy.jpg)
</Frame>

3. Click **Edit**, select **Custom**, and modify settings such as:
   * **Minimum password length**
   * **Maximum password age**
   * **Required character types**
   * **Prevent password reuse**

<Frame>
  ![The image shows an AWS IAM password policy settings page, where custom password requirements can be configured, including minimum length and strength criteria.](https://kodekloud.com/kk-media/image/upload/v1752862985/notes-assets/images/AWS-IAM-Demo-MFA-and-Password-Policies/aws-iam-password-policy-settings.jpg)
</Frame>

4. Once you've tailored the policy to your organizational standards, click **Save changes**. All IAM users will now be subject to the updated policy.

## Links and References

* [AWS IAM User Guide: Managing MFA Devices](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_manage.html)
* [AWS IAM: Password Policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html)
* [AWS Security Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-standards.html)