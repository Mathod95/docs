---
title: Route 53
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Route-53/page
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Route-53-Demo/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/fd4709e4-52c9-4d2b-861d-164e42ff25de
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/7d84a13a-4cbf-4ecb-b577-e27f6209b96d?autoplay=true
---

> Amazon Route 53 is a scalable DNS web service and domain registrar for managing domains and routing internet traffic.

Amazon Route 53 is AWS’s scalable and highly available Domain Name System (DNS) web service and domain registrar. With Route 53, you can register new domains, manage DNS records for routing internet traffic, and leverage a global network of DNS servers.

## Key Features

* Domain registration and management as your registrar
* DNS record configuration for EC2, load balancers, S3 static websites, and more
* Highly available, low-latency global DNS resolution

## Domain Registration and DNS Management

When you register a domain (e.g., `example.com`) through Route 53, AWS serves as your domain registrar. You can then configure all DNS records directly in the AWS Management Console, AWS CLI, or through the API.

<Callout icon="lightbulb" color="#1CB2FE">
  If you register the domain with Route 53, name servers are automatically set. For external domains, update the NS records at your existing registrar to point to the Route 53 name servers.
</Callout>

## Hosted Zones

A **hosted zone** in Route 53 is a container for DNS records related to a specific domain or subdomain. AWS allocates four authoritative name servers for each hosted zone.

| Hosted Zone Type    | Scope                       | Use Case                            |
| ------------------- | --------------------------- | ----------------------------------- |
| Public Hosted Zone  | Global (Internet)           | Serve public DNS queries            |
| Private Hosted Zone | VPC (Virtual Private Cloud) | Internal DNS resolution within VPCs |

<Frame>
  ![The image illustrates the concept of hosted zones in Amazon Route 53, showing how DNS records are managed for different domains, each allocated four nameservers by AWS.](https://kodekloud.com/kk-media/image/upload/v1752863310/notes-assets/images/AWS-Networking-Fundamentals-Route-53/amazon-route53-hosted-zones-dns-records.jpg)
</Frame>

## How It Works: Step by Step

1. Create a hosted zone for your domain (e.g., `fastcars.com`).
2. AWS assigns four name servers to the hosted zone.
3. Define DNS records (A, AAAA, CNAME, MX, TXT, etc.) in the hosted zone.
4. Verify that your domain’s NS records at the registrar match the assigned name servers.

After these steps, Route 53’s global network of name servers will respond to DNS queries for your domain.

## Common DNS Record Types

| Record Type | Description                             | Example                                               |
| ----------- | --------------------------------------- | ----------------------------------------------------- |
| A           | Maps a domain to an IPv4 address        | `www -> 192.0.2.44`                                   |
| AAAA        | Maps a domain to an IPv6 address        | `www -> 2001:0db8:85a3:0000:0000:8a2e:0370:7334`      |
| CNAME       | Aliases one name to another             | `blog -> blog.example.com`                            |
| MX          | Mail exchange servers for email routing | `example.com MX 10 mail.example.com`                  |
| TXT         | Text records for verification/DNSSEC    | `example.com TXT "v=spf1 include:amazonses.com -all"` |

## Summary

Route 53 offers:

* Fully managed DNS service for end-user request routing
* Domain registration with AWS as the registrar
* Global DNS infrastructure for low-latency queries
* Hosted zones for organizing DNS records per domain

<Frame>
  ![The image is a summary slide highlighting three points about AWS Route 53: it's a managed DNS service, a global service, and hosted zones are a collection of DNS.](https://kodekloud.com/kk-media/image/upload/v1752863311/notes-assets/images/AWS-Networking-Fundamentals-Route-53/aws-route-53-dns-summary-slide.jpg)
</Frame>

## Links and References

* [Amazon Route 53 Documentation](https://docs.aws.amazon.com/Route53/)
* [Amazon Route 53 Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)
* [AWS DNS Concepts and FAQs](https://aws.amazon.com/route53/faqs/)

---

> Learn to register a domain with AWS Route 53, explore hosted zones, and create an A record for web server connection.

In this guide, you’ll learn how to register a domain name with AWS Route 53, explore your hosted zone, and create an A record to point your domain to a web server. By the end, you’ll understand how to leverage Route 53’s global DNS network for reliable name resolution.

## Prerequisites

* An active AWS account with Route 53 permissions
* A public IPv4 address for your web server
* Basic knowledge of DNS concepts

## 1. Register a Domain Name

1. Sign in to the AWS Management Console and navigate to **Route 53**.
2. In the left pane, select **Registered domains** and click **Register domains**.

<Frame>
  ![The image shows the AWS Route 53 console interface, specifically the "Registered domains" section, which currently displays no domains.](https://kodekloud.com/kk-media/image/upload/v1752863299/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/aws-route-53-registered-domains-console.jpg)
</Frame>

3. Enter your desired domain (e.g., `kodeklouddemo123.com`) and click **Check** to verify availability.

<Frame>
  ![The image shows a domain search page on AWS, displaying the availability and pricing of the domain "kodeklouddemo123.com" and suggesting alternative domain options.](https://kodekloud.com/kk-media/image/upload/v1752863300/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/aws-domain-search-kodeklouddemo123.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Make sure your chosen domain doesn’t infringe on trademarks or copyrights. Unauthorized use may result in legal issues.
</Callout>

4. Select the domain and choose **Proceed to checkout**.

<Frame>
  ![The image shows a domain registration page on AWS Route 53, displaying pricing options for the domain "kodeklouddemo123.com" with auto-renew enabled for one year at \$13.00 USD.](https://kodekloud.com/kk-media/image/upload/v1752863301/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/aws-route53-domain-registration-pricing.jpg)
</Frame>

5. Enable **Auto-renewal** (recommended) and confirm **Privacy protection** is on for all contacts.
6. Provide registrant, admin, and tech contact information, review the terms, and click **Submit**.

<Frame>
  ![The image shows a contact information form for domain registration on Amazon Route 53, including registrant, admin, and tech contact details, with a section for terms and conditions. There is a "Submit" button at the bottom.](https://kodekloud.com/kk-media/image/upload/v1752863302/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/amazon-route53-domain-registration-form.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  AWS automatically creates a hosted zone when you register a domain. A small hosted zone fee applies in addition to the registration cost. See [Route 53 Pricing](https://aws.amazon.com/route53/pricing/).
</Callout>

7. After AWS processes your request, you’ll receive a confirmation email. The new domain will appear under **Registered domains**.

## 2. View Domain Details

Click your domain in **Registered domains** to see:

* Registration and expiration dates
* Contact information
* Assigned name servers

<Frame>
  ![The image shows the AWS Route 53 console displaying details for the domain "kodekloudemo123.com," including registration and expiration dates, contact information, and name servers.](https://kodekloud.com/kk-media/image/upload/v1752863304/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/aws-route53-console-kodekloudemo123.jpg)
</Frame>

## 3. Explore the Hosted Zone

1. In the Route 53 dashboard, select **Hosted zones**.
2. Click the hosted zone named after your domain (e.g., `kodeklouddemo123.com`).

Inside, you’ll find:

* The four name servers assigned by AWS
* Default DNS records created automatically

<Frame>
  ![The image shows an AWS Route 53 console displaying details of a hosted zone for the domain "kodeklouddemo123.com," including name servers and DNS records.](https://kodekloud.com/kk-media/image/upload/v1752863305/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/aws-route53-hosted-zone-kodeklouddemo123.jpg)
</Frame>

## 4. Create an A Record

An A record maps your domain (or subdomain) to an IPv4 address.

1. In your hosted zone, click **Create records**.
2. Select **A – IPv4 address** as the record type.
3. For **Record name**, leave blank to map the root domain or enter a prefix (e.g., `www`).
4. Under **Value**, enter your server’s public IPv4 address.
5. Accept the default TTL and click **Create records**.

<Frame>
  ![The image shows an AWS Route 53 console screen where a user is creating a DNS record. The record type is set to "A" for routing traffic to an IPv4 address, with a specified IP address and TTL value.](https://kodekloud.com/kk-media/image/upload/v1752863307/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/aws-route53-dns-a-record-creation.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  DNS updates typically propagate within 60 seconds. Use **View status** to verify when your record is `INSYNC`.
</Callout>

<Frame>
  ![The image shows an AWS Route 53 dashboard displaying change info details for a hosted zone, with the status marked as "INSYNC."](https://kodekloud.com/kk-media/image/upload/v1752863308/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/aws-route53-dashboard-insync-change-info.jpg)
</Frame>

## 5. Validate Your Setup

Once your A record is `INSYNC`, open a browser and navigate to:

```text  theme={null}
https://kodeklouddemo123.com
```

You should see your web server’s default page.

<Frame>
  ![The image shows a simple webpage with the text "This is kodeklouddemo123.com" centered on a white background.](https://kodekloud.com/kk-media/image/upload/v1752863308/notes-assets/images/AWS-Networking-Fundamentals-Route-53-Demo/kodeklouddemo123-webpage-white-background.jpg)
</Frame>

## Common DNS Record Types

| Record Type | Description                      | Example                               |
| ----------- | -------------------------------- | ------------------------------------- |
| A           | Maps a domain to an IPv4 address | `example.com` → `192.0.2.44`          |
| CNAME       | Points a name to another domain  | `www.example.com` → `example.com`     |
| MX          | Specifies mail servers           | `10 mail.example.com`                 |
| TXT         | Holds text for SPF, DKIM, etc.   | `"v=spf1 include:amazonses.com ~all"` |

## Summary

* Register and manage domains in one place
* Configure DNS records (A, CNAME, MX, TXT)
* Benefit from AWS’s global DNS infrastructure

## Links & References

* [AWS Route 53 Documentation](https://docs.aws.amazon.com/route53/)
* [Domain Registration Guide](https://docs.aws.amazon.com/route53/latest/DeveloperGuide/domain-register.html)
* [Route 53 Pricing](https://aws.amazon.com/route53/pricing/)
* [AWS Certified Solutions Architect – Associate](https://aws.amazon.com/certification/certified-solutions-architect-associate/)