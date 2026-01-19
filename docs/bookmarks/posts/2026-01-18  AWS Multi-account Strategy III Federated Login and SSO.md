---
title: "AWS Multi-account Strategy III: Federated Login and SSO"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://towardsaws.com/aws-multi-account-strategy-iii-federated-login-and-sso-cc49b8be164f"
author:
  - "[[Sarah Chen]]"
---
<!-- more -->

[Sitemap](https://towardsaws.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@SarahChen)## [Towards AWS](https://towardsaws.com/?source=post_page---publication_nav-5da0267791b1-cc49b8be164f---------------------------------------)

To centrally manage user access and simplify the registration process, we’ll set up a federated single sign-on (SSO) solution.

After establishing our AWS multi-account environment with AWS Organization and OUs, secured by SCPs and IAM identities, we continue with our company’s landing zone plan.

Now, let’s switch roles from CTO to IT manager who wants to add employees to our AWS environment to access resources and applications efficiently.

To centrally manage user access and simplify the registration process, we’ll set up a federated single sign-on (SSO) solution allowing our employees to access resources across our AWS multi-account environment with a single login.

## Services and Core Concepts

### Federated Login

Federated Login allows users to log in to multiple systems or applications using a single set of credentials from a trusted third party.

**Identity Provider (IdP)**

An Identity Provider (IdP) is a trusted entity that provides authentication services, such as Google, or enterprise systems like Active Directory.

**Service Provider (SP)**

A Service Provider (SP) is an application or system that requires authentication, such as AWS, Google Workspace, or any SaaS application.

When a user tries to access a service, they are redirected to the IdP for authentication. Once authenticated, the IdP sends an authentication token back to the SP, granting the user access.

This process eliminates the need for separate login credentials for each system, enhancing security by centralizing authentication and reducing the burden of remembering multiple passwords.

### Single Sign-On (SSO)

Single Sign-On (SSO) is a user authentication process that allows a user to enter one set of credentials (such as a username and password) to access multiple applications. SSO is often used with federated login to extend the benefits across different domains and platforms.

### AWS IAM Identity Center (AWS SSO)

AWS IAM Identity Center is a service for managing human user access to AWS resources. It allows you to assign workforce users consistent access to multiple AWS accounts and applications at no additional charge.

With multi-account permissions, you can centrally implement permissions across multiple AWS accounts simultaneously without manually configuring each account.

By default, AWS IAM Identity Center provides a directory to create users, organize them into groups, and set permissions across those groups to grant users access to AWS resources and applications.

### SAML 2.0

SAML (Security Assertion Markup Language) 2.0 is an open standard for exchanging authentication and authorization data between parties, specifically between an IdP and an SP.

## Solution

To add users registered in our IdP to AWS IAM Identity Center, we’ll grant Marc and Sarah, our developers, specific permissions.

### Set Up and Configuration

Marc and Sarah need full access to EC2 and S3 in the developer account (DevAccount) and read-only access to EC2 and S3 in the production account (PrdAccount).

**Step 1: Set Up AWS IAM Identity Center**

1. **Enable AWS IAM Identity Center**
- Enable AWS IAM Identity Center and select the identity source (e.g., AWS SSO, external SAML IdP, Active Directory).
- For this example, we’ll use the built-in directory.

**Step 2: Integrate AWS SSO with Your Identity Provider (IdP)**

We’ll use our own IdP service with SAML 2.0.

1. **Configure IdP:**
- Obtain the SAML metadata document from our IdP (e.g., Google Workspace, Okta).
- This document contains information about the IdP’s SAML configuration.

**2\. Set Up SAML 2.0 Federation in AWS IAM Identity Center:**

- Upload the SAML metadata document obtained from our IdP.
- Follow the instructions to complete the integration.

**Step 3: Create Permission Sets in AWS IAM Identity Center**

Create two permission sets:

- `FullAccessDev`: Full access to EC2 and S3
- `ReadOnlyPrd`: Read-only access to EC2 and S3

**Step 4: Assign Users to Accounts and Permission Sets**

1. **Add Users and Groups in AWS IAM Identity Center:**
- Add users Marc and Sarah by configuring their names and emails.

**2\. Assign Permissions:**

- Assign Marc and Sarah to the developer account (DevAccount) with the `FullAccessDev` permission set.
- Assign Marc and Sarah to the production account (PrdAccount) with the `ReadOnlyPrd` permission set.

**Step 5: Configure SAML 2.0 for Federated Login**

1. **Upload AWS Metadata File to IdP**
- Download the AWS metadata file from AWS IAM Identity Center.
- Upload it to your IdP.

**2\. Configure SAML Settings in IdP**

- Entity ID: Use the AWS IAM Identity Center entity ID.
- ACS URL: Use the AWS IAM Identity Center ACS URL.
- Attribute Mapping: Map email addresses and any other necessary attributes from your IdP to the AWS IAM Identity Center.

By following these steps, Marc and Sarah will be able to access the AWS resources as required, using federated login with SAML 2.0.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*dEYB4WeVvCPp9_JqkwK7pQ.jpeg)

Federated Login with AWS IAM Identity Center

Now let’s ask Sarah to help us test the configuration:

1. **Navigate to AWS Sign-In URL**: Sarah navigates to the AWS sign-in URL provided by the company.
2. **Redirect to IdP Login Page**: She is redirected to our company’s IdP login page.
3. **Login with IdP Credentials**: Sarah enters her credentials and successfully logs in.
4. **Generate SAML Assertion**: Our IdP service generates a SAML assertion containing Sarah’s identity and other attributes.
5. **Send SAML Assertion to AWS IAM Identity Center**: The IdP sends the SAML assertion back to AWS IAM Identity Center via a browser redirect.
6. **Validate SAML Assertion**: AWS IAM Identity Center validates the SAML assertion and checks Sarah’s group memberships.
7. **Present Access List**: After successful authentication, Sarah is presented with a list of accounts that she has access to.
8. **Access DevAccount**: When Sarah clicks on `DevAccount`, AWS IAM Identity Center issues temporary credentials with `FullAccessDev` permissions using AWS STS.
9. **Access Resources**: Sarah can now access DevAccount resources with the temporary credentials.

Problem Solver | AWS Solution Architect | Software Engineer | Home-trained Chef | Wine Lover

## More from Sarah Chen and Towards AWS

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--cc49b8be164f---------------------------------------)