---
title: CloudFront
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Edge-Networks/CloudFront/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/d31cb856-303b-4a11-b280-b8729906670b/lesson/aeadb426-fcb0-433f-b1fa-75f0962e82b9?autoplay=true
---

> This article explains Amazon CloudFront, a CDN that enhances content delivery speed and reliability through edge caching and origin failover.

In this lesson, we dive into Amazon CloudFront—a powerful Content Delivery Network (CDN) that reduces latency and accelerates both static and dynamic content. Learn how edge caching, TTL management, and origin failover work together to deliver fast, reliable experiences for users worldwide.

## The Latency Challenge

When your web application resides in a single AWS Region (for example, us-east-1 in New York), users nearby see quick responses, but those thousands of miles away suffer high round-trip times. Slow page loads, video buffering, and large downloads frustrate end users.

<Frame>
  ![The image shows a world map illustrating global content delivery and edge locations, with a central web server connected to various points around the globe.](https://kodekloud.com/kk-media/image/upload/v1752863400/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/global-content-delivery-map-illustration.jpg)
</Frame>

By deploying dozens of **edge locations** around the globe, CloudFront brings content closer to your users, slashing latency and improving performance.

## What Is CloudFront?

Amazon CloudFront is AWS’s global CDN service. It delivers your web assets—HTML, CSS, JavaScript, images, videos, APIs, and dynamic content—via a worldwide network of edge caches. Instead of every user request going back to your origin server, CloudFront routes traffic to the nearest edge location.

<Frame>
  ![The image is a diagram showing Amazon CloudFront distributing content from an S3 Bucket for static content and Amazon Lightsail or an Application Load Balancer for dynamic content.](https://kodekloud.com/kk-media/image/upload/v1752863400/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/cloudfront-s3-bucket-lightsail-diagram.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  Using CloudFront for both static and dynamic assets improves load times, reduces origin load, and can lower data transfer costs.
</Callout>

## Core Components

| Component         | Description                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------- |
| **Origin**        | The source of your content: S3 bucket, EC2/On-Prem HTTP server, Elastic Load Balancer, etc. |
| **Distribution**  | Configuration that links one or more origins to CloudFront; provides a unique domain name.  |
| **Edge Location** | A global cache point where CloudFront stores and serves your objects.                       |

### Distribution Workflow

<Frame>
  ![The image illustrates the architecture of CloudFront, showing the flow of data from users to a distribution configuration, which is connected to an origin server and multiple edge locations.](https://kodekloud.com/kk-media/image/upload/v1752863402/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/cloudfront-architecture-data-flow-diagram.jpg)
</Frame>

1. User requests content from your `*.cloudfront.net` domain.
2. CloudFront routes to the nearest edge location.
3. **Cache Hit**: Edge returns the object immediately.
4. **Cache Miss**: Edge fetches from the origin, caches the response, then serves the user.

## Origin Interaction Examples

### S3 Bucket as Origin

<Frame>
  ![The image illustrates the process of CloudFront interacting with an S3 bucket, showing how requests are handled through edge locations, checking for cache, and fetching from the origin if needed.](https://kodekloud.com/kk-media/image/upload/v1752863403/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/cloudfront-s3-bucket-interaction-diagram.jpg)
</Frame>

* **User → CloudFront edge**
* **Edge: cache hit** → serve directly
* **Edge: cache miss** → fetch from S3 → cache → serve

### Custom HTTP Backend

<Frame>
  ![The image is a diagram illustrating the process of a request being sent to CloudFront, which then fetches a response from a custom HTTP backend.](https://kodekloud.com/kk-media/image/upload/v1752863404/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/cloudfront-request-response-diagram.jpg)
</Frame>

* **User → CloudFront edge**
* **Edge: cache hit** → serve content
* **Edge: cache miss** → fetch from your HTTP server → cache → serve

## Cache Expiration (TTL)

Each cached object at an edge location lives for its **Time To Live (TTL)**. Once TTL expires, the object is evicted and a new request triggers an origin fetch.

<Frame>
  ![The image is an informational slide about CloudFront Time to Live (TTL), explaining that cached content remains for a set time, with a default TTL of 24 hours, and can be set to expire at specific times.](https://kodekloud.com/kk-media/image/upload/v1752863405/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/cloudfront-ttl-cached-content-info.jpg)
</Frame>

* Default TTL: 24 hours
* Customize per object or set absolute expiration timestamps

<Callout icon="triangle-alert" color="#FF6B6B">
  Serving stale content is possible if TTL is too long. Tune your Cache-Control headers carefully to balance freshness and performance.
</Callout>

## Cache Invalidation

Updating assets before their TTL expires requires explicit **cache invalidation**. Otherwise, edge locations will continue to serve the old version.

<Frame>
  ![The image illustrates the concept of cache invalidation, showing how content cached at edge locations can be invalidated, with a TTL of 24 hours, and the potential issue of receiving outdated content.](https://kodekloud.com/kk-media/image/upload/v1752863406/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/cache-invalidation-edge-locations-ttl.jpg)
</Frame>

**Invalidation process**

1. Submit invalidation for the object path (e.g., `/images/logo.png`).
2. Edge caches remove the object.
3. Next request → origin fetch → cache updated → user gets the new version.

## Origin Groups for High Availability

CloudFront **origin groups** let you specify a primary and secondary origin. If the primary fails (for example, 5xx errors or timeouts), CloudFront automatically retries against the secondary, ensuring uninterrupted service.

## Logging and Monitoring

CloudFront can publish detailed logs to Amazon S3, Amazon CloudWatch Logs, or third-party analytics tools. Logs include:

* Request timestamp
* Client IP address
* Requested object and HTTP method
* Response status code

<Frame>
  ![The image illustrates the flow of CloudFront logs, showing interactions between users, CloudFront, and the origin, with logs being sent to CloudWatch. It also lists details captured in the logs, such as request time, IP address, and response status.](https://kodekloud.com/kk-media/image/upload/v1752863407/notes-assets/images/AWS-Networking-Fundamentals-CloudFront/cloudfront-logs-flow-diagram.jpg)
</Frame>

## Summary of CloudFront Features

* **Global CDN**: Edge caching for low-latency delivery
* **Flexible Origins**: S3, HTTP servers, load balancers
* **Distributions**: Custom configuration with domain name
* **TTL & Invalidation**: Fine-grained cache control
* **Origin Groups**: Automatic failover for high availability
* **Logging**: Insights into traffic patterns and errors

## Links and References

* [Amazon CloudFront Developer Guide](https://docs.aws.amazon.com/cloudfront/latest/DeveloperGuide/Introduction.html)
* [AWS CDN Solutions](https://aws.amazon.com/cloudfront/)
* [AWS CLI: create-distribution](https://docs.aws.amazon.com/cli/latest/reference/cloudfront/create-distribution.html)

---

> This tutorial explains how to host a static website on AWS using S3 and accelerate it with CloudFront.

In this tutorial, we’ll walk through how to serve a simple static website (HTML, CSS, images) from Amazon S3 and accelerate it globally with Amazon CloudFront. You’ll learn how to:

1. Set up an S3 bucket and upload your assets
2. Secure S3 with a bucket policy for CloudFront access
3. Create and configure a CloudFront distribution
4. Customize caching behavior and invalidate objects

## Prerequisites

* An AWS account with IAM permissions for S3 and CloudFront
* A local project folder containing:
  * `index.html`
  * `index.css`
  * `images/` (your asset directory)

## Project Structure

Here’s our local directory layout. It contains an HTML page, a CSS stylesheet, and an images folder:

<Frame>
  ![The image shows an AWS Console Home page with a file explorer window open, displaying a folder named "cloudfront" containing an HTML file, a CSS file, and an images folder.](https://kodekloud.com/kk-media/image/upload/v1752863385/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-console-file-explorer-cloudfront.jpg)
</Frame>

All assets will reside in an S3 bucket. CloudFront will then cache these files at edge locations to minimize latency for end users.

***

## 1. Create and Configure an S3 Bucket

1. Open the [Amazon S3 console](https://console.aws.amazon.com/s3/), then click **Create bucket**.
2. Enter a globally unique name (e.g., `kodekloud-cloudfront-demo`), leave other settings at their defaults, and click **Create bucket**.

<Frame>
  ![The image shows an AWS S3 interface for creating a new bucket, with options for general configuration, bucket type, and object ownership settings. The bucket name "kodekloud-cloudfront-demo" is entered in the text field.](https://kodekloud.com/kk-media/image/upload/v1752863386/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-s3-create-bucket-interface.jpg)
</Frame>

After creation, verify your bucket appears in the list:

<Frame>
  ![The image shows an AWS S3 management console with a list of general-purpose buckets, their regions, and creation dates. A green notification at the top indicates the successful creation of a bucket named "kodekloud-cloudfront-demo."](https://kodekloud.com/kk-media/image/upload/v1752863388/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-s3-management-console-buckets-list.jpg)
</Frame>

3. Click on your bucket name, then choose **Upload**. Add `index.html`, `index.css`, and the entire `images` folder.

***

## 2. Secure Bucket Access

By default, S3 blocks public access to buckets:

<Frame>
  ![The image shows an AWS S3 bucket permissions settings page, highlighting options for blocking public access and managing bucket policies.](https://kodekloud.com/kk-media/image/upload/v1752863389/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-s3-bucket-permissions-settings.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Do not disable **Block Public Access**. Instead, grant CloudFront permission via a bucket policy in Step 4.
</Callout>

***

## 3. Create a CloudFront Distribution

1. Navigate to the [CloudFront console](https://console.aws.amazon.com/cloudfront/), then click **Create distribution** → **Get started** under **Web**.
2. For **Origin domain**, select your S3 bucket (`kodekloud-cloudfront-demo`).
3. Leave **Origin path** blank unless you want to serve a subdirectory. Use the default Origin ID or customize it.

<Frame>
  ![The image shows a screenshot of the AWS CloudFront console, specifically the "Create distribution" page where the user is configuring the origin settings for a distribution.](https://kodekloud.com/kk-media/image/upload/v1752863390/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-cloudfront-create-distribution-screenshot.jpg)
</Frame>

Scroll to other settings—most can remain at their defaults:

* Web Application Firewall: **Disabled**
* Price Class: **Use all edge locations (Best Performance)**
* SSL Certificate: **Default CloudFront certificate (\*.cloudfront.net)**
* Default Root Object: **index.html**

<Frame>
  ![The image shows a configuration page for creating a CloudFront distribution on the AWS Management Console, with options for SSL certificates, HTTP versions, logging, and IPv6 settings.](https://kodekloud.com/kk-media/image/upload/v1752863391/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/cloudfront-distribution-configuration-aws.jpg)
</Frame>

### Why Set a Default Root Object?

When you request the root of a distribution (`/`), CloudFront needs to know which file to serve. By setting **Default Root Object** to `index.html`, you avoid typing the full filename in the URL.

<Frame>
  ![The image shows an Amazon S3 bucket interface with three objects: a folder named "images" and two files, "index.css" and "index.html," along with their details like type, last modified date, size, and storage class.](https://kodekloud.com/kk-media/image/upload/v1752863392/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/amazon-s3-bucket-interface-objects.jpg)
</Frame>

Ensure **Default Root Object** is `index.html`:

<Frame>
  ![The image shows a configuration page for creating a CloudFront distribution on AWS, with options for SSL certificates, HTTP versions, and logging settings.](https://kodekloud.com/kk-media/image/upload/v1752863393/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/cloudfront-distribution-configuration-aws-2.jpg)
</Frame>

4. Click **Create distribution**. Distribution creation can take several minutes.

<Frame>
  ![The image shows an AWS CloudFront distribution page with a notification about a successfully created distribution and a warning to update the S3 bucket policy. It includes details like the distribution domain name and settings.](https://kodekloud.com/kk-media/image/upload/v1752863394/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-cloudfront-distribution-notification.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  CloudFront distributions typically deploy within 10–20 minutes. You’ll know it’s ready when the status changes to **Enabled**.
</Callout>

***

## 4. Apply an S3 Bucket Policy for CloudFront

To allow CloudFront to fetch objects without making the bucket public:

1. In the CloudFront console, click the **Copy Policy** link from the warning banner.
2. Go back to your S3 bucket’s **Permissions** tab → **Bucket policy** → **Edit**.
3. Paste and save the following JSON (replace `kodekloud-cloudfront-demo` with your bucket name):

```json  theme={null}
{
  "Version": "2008-10-17",
  "Id": "PolicyForCloudFrontPrivateContent",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::kodekloud-cloudfront-demo/*"
    }
  ]
}
```

If you wish to lock it down to a specific distribution, add a `Condition` block with your Distribution ARN:

```json  theme={null}
"Condition": {
  "StringEquals": {
    "AWS:SourceArn": "arn:aws:cloudfront:841860927337:distribution/E2D1BKS7RKY1GR"
  }
}
```

***

## 5. Validate Your Distribution

Once the distribution status is **Enabled**, copy its **Domain Name** (e.g., `d111111abcdef8.cloudfront.net`) and open it in a browser with a trailing slash:

```text  theme={null}
https://d111111abcdef8.cloudfront.net/
```

* **First request:** CloudFront fetches content from S3.
* **Subsequent requests:** Content is served from the nearest edge location.

***

## 6. Review and Customize Cache Settings

By default, CloudFront applies the **Managed-CachingOptimized** policy with a 24 hour (86,400 s) TTL.

1. In your distribution, go to the **Behaviors** tab and click **Edit** on the default behavior.
2. Note the **Cache policy** in use (e.g., `Managed-CachingOptimized`).
3. Click **View policy** to inspect TTL values:

<Frame>
  ![The image shows the settings page of an AWS CloudFront distribution, displaying options for path patterns, origin groups, compression, viewer protocol policy, allowed HTTP methods, and cache key and origin requests.](https://kodekloud.com/kk-media/image/upload/v1752863395/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-cloudfront-settings-page-options.jpg)
</Frame>

<Frame>
  ![The image shows an AWS CloudFront settings page for a caching policy named "Managed-CachingOptimized," detailing TTL settings, cache key settings, and compression support options.](https://kodekloud.com/kk-media/image/upload/v1752863396/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-cloudfront-managed-caching-policy-settings.jpg)
</Frame>

| Setting             | Default                  | Description                                |
| ------------------- | ------------------------ | ------------------------------------------ |
| Price Class         | All edge locations       | Global performance vs. cost.               |
| Default Root Object | index.html               | Serves root URL without a filename.        |
| Cache Policy        | Managed-CachingOptimized | TTL: 86,400 s (min/max can be customized). |
| SSL Certificate     | Default CloudFront cert  | HTTPS support for `*.cloudfront.net`.      |

***

## 7. Invalidate Cached Objects

When you overwrite a file in S3 (e.g., update `images/car.jpg`), CloudFront may still serve the old version until its TTL expires:

<Frame>
  ![The image shows an AWS S3 bucket permissions page for "kodekloud-cloudfront-demo," highlighting settings for blocking public access and bucket policy options.](https://kodekloud.com/kk-media/image/upload/v1752863397/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-s3-bucket-permissions-kodekloud.jpg)
</Frame>

To force CloudFront to fetch the updated file:

1. In the CloudFront console, select your distribution and open **Invalidations**.
2. Click **Create invalidation**, then specify paths:

   ```text  theme={null}
   /images/car.jpg
   /images/*
   /*
   ```

   Use wildcards to cover multiple objects.

<Frame>
  ![The image shows an AWS CloudFront distribution settings page, specifically the "Behaviors" tab, displaying a default behavior configuration with options for creating and editing behaviors.](https://kodekloud.com/kk-media/image/upload/v1752863398/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-cloudfront-behaviors-settings-page.jpg)
</Frame>

<Frame>
  ![The image shows an AWS CloudFront interface where a user is creating an invalidation by adding object paths to remove from the CloudFront cache.](https://kodekloud.com/kk-media/image/upload/v1752863399/notes-assets/images/AWS-Networking-Fundamentals-CloudFront-Demo/aws-cloudfront-invalidation-object-paths.jpg)
</Frame>

3. Click **Create invalidation**. Once it completes, refresh your distribution URL to see the new image.

<Callout icon="triangle-alert" color="#FF6B6B">
  Invalidations may incur additional charges if you exceed the free tier (1,000 paths/month).
</Callout>

***

## Next Steps

You’ve successfully deployed a static website with S3 and CloudFront. In future lessons, we’ll cover:

* Custom cache-key and origin-request policies
* Geographic restrictions and geo-blocking
* Using Lambda\@Edge for dynamic content transformations

***

## References

* [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/index.html)
* [Amazon CloudFront Developer Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/)
* [How CloudFront Caching Works](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html)