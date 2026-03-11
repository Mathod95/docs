---
title: DNS
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/DNS-VPC/page
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/DNS-VPC-Demo/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/9ea8c487-18ef-46f4-bb02-d420a7f898ed
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/dfa079f3-73e5-4c65-bb7b-15a73836f0e7?autoplay=true
---

> This article explains DNS resolution in AWS VPCs and how to configure DNS settings for EC2 instances.

Discover how DNS resolution operates within AWS Virtual Private Clouds (VPCs) and how to configure DNS settings for your EC2 instances for reliable name resolution.

## Domain Names for Private IP Addresses

When you launch an EC2 instance into a public or private subnet, AWS automatically assigns it a private IPv4 address (for example, 10.0.100.10). AWS also generates a DNS hostname that embeds this IP address. Clients can connect using either the private IP or the assigned DNS name.

<Frame>
  ![The image is a diagram showing DNS in VPCs within an AWS Cloud, featuring four VPCs with different IP address ranges. Each VPC is labeled with its CIDR block and a specific IP address.](https://kodekloud.com/kk-media/image/upload/v1752863199/notes-assets/images/AWS-Networking-Fundamentals-DNS-VPC/dns-vpcs-aws-diagram-ip-addresses.jpg)
</Frame>

## AWS-Provided DNS Servers

EC2 instances resolve these hostnames by querying the Amazon-provided DNS servers. AWS exposes two endpoints for DNS resolution within a VPC:

* Link-local address: 169.254.169.253 (accessible from all instances)
* VPC CIDR second IP: e.g., 10.10.0.2 in a 10.10.0.0/16 VPC or 10.20.0.2 in a 10.20.0.0/16 VPC

Instances can send queries to either endpoint interchangeably.

<Callout icon="lightbulb" color="#1CB2FE">
  In the default VPC, both DNS support and hostnames are enabled out of the box. Custom VPCs default to DNS support on and hostnames off.
</Callout>

## VPC DNS Configuration Options

AWS provides two VPC attributes that control DNS behavior:

| Option             | Description                                                  | Default Value                                |
| ------------------ | ------------------------------------------------------------ | -------------------------------------------- |
| enableDnsSupport   | Enables DNS resolution via Amazon-provided DNS servers.      | true (all VPCs)                              |
| enableDnsHostnames | Assigns DNS hostnames to instances with public IP addresses. | false for custom VPCs, true for default VPCs |

You can modify these settings through the AWS Management Console, AWS CLI, or AWS SDKs.

<Frame>
  ![The image shows two DNS options: "enableDnsHostnames" and "enableDnsSupport," each in a colored square.](https://kodekloud.com/kk-media/image/upload/v1752863200/notes-assets/images/AWS-Networking-Fundamentals-DNS-VPC/dns-options-enable-dns-hostnames-support.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Disabling `enableDnsSupport` prevents any DNS resolution within the VPC, which can break applications that rely on domain names.
</Callout>

## Summary

* Private IPv4 addresses are automatically mapped to DNS hostnames.
* Amazon-provided DNS endpoints are available at 169.254.169.253 and the VPC CIDR’s second IP.
* Use `enableDnsHostnames` to toggle DNS hostname assignment for instances with public IPs.
* Use `enableDnsSupport` to enable or disable DNS resolution within the VPC.

<Frame>
  ![The image is a summary slide with four points about DNS settings in AWS VPCs, including private IP assignments, DNS server access, and DNS support options.](https://kodekloud.com/kk-media/image/upload/v1752863202/notes-assets/images/AWS-Networking-Fundamentals-DNS-VPC/dns-settings-aws-vpcs-summary-slide.jpg)
</Frame>

## Links and References

* [AWS VPC DNS Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-dns.html)
* [Amazon EC2 User Guide](https://docs.aws.amazon.com/ec2/latest/userguide/)

---

> This guide explores DNS settings in an AWS VPC and their effects on EC2 instances.

In this guide, we’ll explore the two DNS settings available on an AWS Virtual Private Cloud (VPC)—**Enable DNS resolution** and **Enable DNS hostnames**—and demonstrate their effects on EC2 instances.

## Overview of VPC DNS Settings

When you create a custom VPC without modifying defaults, the VPC DNS settings look like this (an Internet Gateway is also attached by default):

<Frame>
  ![The image shows an AWS VPC management console with details of a VPC named "vpcdemo," including its state, CIDR blocks, and associated resources.](https://kodekloud.com/kk-media/image/upload/v1752863194/notes-assets/images/AWS-Networking-Fundamentals-DNS-VPC-Demo/aws-vpc-management-console-vpcdemo.jpg)
</Frame>

| Setting               | Description                                                                                | Default | Use Case                                                   |
| --------------------- | ------------------------------------------------------------------------------------------ | ------- | ---------------------------------------------------------- |
| Enable DNS resolution | Allows instances to forward hostname lookups to the Amazon‐provided DNS server (10.0.0.2). | true    | Required for any DNS-based name resolution inside the VPC. |
| Enable DNS hostnames  | Assigns a public DNS hostname to instances that have a public IPv4 address.                | false   | Useful for mapping public IPs to friendly DNS names.       |

<Callout icon="lightbulb" color="#1CB2FE">
  The Amazon‐provided DNS server is always at the second IP address in the VPC CIDR block (for example, 10.0.0.2 in a 10.0.0.0/16 VPC).
</Callout>

***

## 1. Enable DNS Hostnames

By default, **Enable DNS hostnames** is disabled. Launch an EC2 instance in this VPC with these settings:

* **AMI**: Amazon Linux 2
* **Instance type**: t2.micro
* **Key pair**: your existing key
* **Network**: vpcdemo
* **Auto-assign Public IP**: Enabled
* **Security group**: allow SSH (port 22) and ICMP (All ICMP) from 0.0.0.0/0

Once it’s running, you’ll see only the private DNS name:

<Frame>
  ![The image shows an AWS EC2 management console with a list of instances, highlighting one instance named "dnsdemo" that is currently running. The details of the selected instance, including its public IPv4 address and instance type, are displayed below.](https://kodekloud.com/kk-media/image/upload/v1752863196/notes-assets/images/AWS-Networking-Fundamentals-DNS-VPC-Demo/aws-ec2-console-dnsdemo-instance-details.jpg)
</Frame>

1. Go to **Actions → Edit VPC settings**.
2. Check **Enable DNS hostnames** and click **Save**.
3. Refresh the EC2 Instances view.

The **Public DNS (IPv4)** column is now populated:

```bash  theme={null}
$ ping ec2-35-173-226-213.compute-1.amazonaws.com
PING ec2-35-173-226-213.compute-1.amazonaws.com (35.173.226.213): 56 data bytes
64 bytes from 35.173.226.213: icmp_seq=0 ttl=54 time=35.1 ms
```

***

## 2. Enable DNS Resolution

Next, verify **Enable DNS resolution**. SSH into your instance:

```bash  theme={null}
$ ssh -i path/to/key.pem ec2-user@35.173.226.213
```

Return to the VPC console to confirm the CIDR block:

<Frame>
  ![The image shows an AWS EC2 management console displaying details of a Virtual Private Cloud (VPC) named "vpcdemo," including its ID, state, and CIDR information. The interface includes options for managing subnets, route tables, and other network settings.](https://kodekloud.com/kk-media/image/upload/v1752863197/notes-assets/images/AWS-Networking-Fundamentals-DNS-VPC-Demo/aws-ec2-vpcdemo-management-console.jpg)
</Frame>

On the instance, inspect `/etc/resolv.conf`:

```bash  theme={null}
[ec2-user@ip-10-0-1-144 ~]$ cat /etc/resolv.conf
nameserver 10.0.0.2
search ec2.internal
```

Perform a DNS lookup:

```bash  theme={null}
[ec2-user@ip-10-0-1-144 ~]$ nslookup google.com
Server:         10.0.0.2
Address:        10.0.0.2#53

Non-authoritative answer:
Name:   google.com
Address: 142.251.163.100
```

Because **Enable DNS resolution** is turned on, lookups succeed. To see what happens when you disable it:

1. In the VPC console, choose **Actions → Edit VPC settings**.
2. Uncheck **Enable DNS resolution** and click **Save**.
3. Back on your instance, try:

```bash  theme={null}
[ec2-user@ip-10-0-1-144 ~]$ nslookup youtube.com
;; connection timed out; no servers could be reached
```

<Frame>
  ![The image shows the AWS Management Console with the "Edit VPC settings" page open, displaying options for VPC details, DHCP settings, DNS settings, and network address usage metrics settings.](https://kodekloud.com/kk-media/image/upload/v1752863198/notes-assets/images/AWS-Networking-Fundamentals-DNS-VPC-Demo/aws-management-console-edit-vpc-settings.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  With DNS resolution disabled, instances cannot use the Amazon‐provided DNS server. You must configure an alternate DNS server (for example, 8.8.8.8) in your DHCP options or run your own DNS service within the VPC.
</Callout>

***

## References

* [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
* [Amazon EC2 User Guide – Networking](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html)
* [Route 53 Resolver – Amazon VPC DNS](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html)