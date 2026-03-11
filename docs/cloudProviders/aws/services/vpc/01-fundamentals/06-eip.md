---
title: EIP
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Elastic-IP/page
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Elastic-IP-Demo/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/a5dfb38f-8233-4f66-a59b-d7dfe1c37e14
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/352c84b3-410d-4463-be74-29ec189ce4c7?autoplay=true
---

> This article explains AWS Elastic IP addresses, their benefits, management, pricing, and how they ensure consistent connectivity for applications.

Understanding how AWS handles public IPs and leveraging Elastic IPs can help you maintain consistent connectivity for your applications.

## Why Dynamic Public IPs Can Be Problematic

When you launch an EC2 instance in a public subnet, AWS automatically assigns a **public IPv4 address** (for example, `1.1.1.1`). However, this IP is drawn from AWS’s shared pool and is **not** reserved for your account. Stopping or restarting the instance may result in a new IP, causing:

* Downtime if clients have hardcoded the old address
* Configuration drift in DNS records or security groups
* Operational overhead to track changing IPs
 
## Introducing Elastic IPs

**Elastic IP addresses** are static IPv4 addresses that you allocate and control within a specific AWS Region. Key benefits include:

* Static mapping: The IP stays yours until you explicitly release it
* Flexibility: Associate or disassociate the address from EC2 instances or ENIs at any time
* High availability: Instantly remap to a standby instance during maintenance or failure

### Example: Failover with Elastic IPs

If **Server A** goes down, simply disassociate its Elastic IP and reassign it to **Server B**. Clients continue to reach your application at the same address (`1.1.1.1`), eliminating DNS propagation delays.

<Frame>
  ![The image illustrates an AWS Cloud setup with two servers, Server A and Server B. Server A has an error, while Server B is associated with the IP address 1.1.1.1.](https://kodekloud.com/kk-media/image/upload/v1752863220/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP/aws-cloud-setup-servers-error-ip.jpg)
</Frame>

## Allocating and Managing Elastic IPs

You can manage Elastic IPs via the AWS Management Console or AWS CLI. Below is a sample CLI workflow.

```bash
# Allocate a new Elastic IP in your default VPC
aws ec2 allocate-address --domain vpc

# Associate the Elastic IP with an EC2 instance
aws ec2 associate-address \
  --instance-id i-0123456789abcdef0 \
  --allocation-id eipalloc-12345678

# Disassociate the Elastic IP when needed
aws ec2 disassociate-address --association-id eipassoc-87654321
```

<Callout icon="lightbulb" color="#1CB2FE">
  You can also manage Elastic IPs using AWS SDKs, CloudFormation, or Terraform. Refer to the [AWS Elastic IP Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html) for more details.
</Callout>

## Elastic IP Pricing

| Scenario                                            | Cost             |
| --------------------------------------------------- | ---------------- |
| First Elastic IP associated with a running instance | Free             |
| Additional Elastic IPs on the same instance         | Charged per hour |
| Allocated but unattached Elastic IPs                | Small hourly fee |

<Callout icon="triangle-alert" color="#FF6B6B">
  Unattached Elastic IPs incur charges. Always release unused addresses to avoid unexpected costs.
</Callout>

<Frame>
  ![The image illustrates "Elastic IP Pricing," showing a diagram of a microchip with multiple IPs, where additional IPs are charged per hour.](https://kodekloud.com/kk-media/image/upload/v1752863221/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP/elastic-ip-pricing-microchip-diagram.jpg)
</Frame>

## Key Considerations

* Elastic IPs are **region-specific** and cannot be moved across regions.
* You can associate them only with **EC2 instances** or **network interfaces (ENIs)** in the same region.
* Choose between AWS’s public IPv4 pool or bring your own custom IPv4 address block.

## Summary

* AWS **public IPv4 addresses** are dynamic and may change on instance stop/start.
* **Elastic IP addresses** provide a static, portable IPv4 address under your control.
* Workflow to use an Elastic IP:
  1. Allocate it to your AWS account.
  2. Associate it with an EC2 instance or ENI.
  3. Reassociate as needed during failover or maintenance.

<Frame>
  ![The image is a summary slide explaining the differences between public IPs and Elastic IPs, highlighting that public IPs are not static, while Elastic IPs are static IPv4 addresses. It also describes the process of allocating and associating an Elastic IP with an instance or network interface.](https://kodekloud.com/kk-media/image/upload/v1752863222/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP/public-vs-elastic-ips-summary.jpg)
</Frame>

## Links and References

* [Elastic IP Addresses – AWS EC2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)
* [AWS CLI Command Reference – allocate-address](https://docs.aws.amazon.com/cli/latest/reference/ec2/allocate-address.html)
* [AWS CLI Command Reference – associate-address](https://docs.aws.amazon.com/cli/latest/reference/ec2/associate-address.html)

---

- Public IPs are not static and, if an EC2 instance goes down, then it will get a new public IP
- Elastic IPs are static IPv4 addresses that do not change
- To use an Elastic IP address, you first allocate one to your account, and then associate it with your instance or a network interface

---

> This lesson demonstrates how to allocate, associate, and manage Elastic IPs in AWS for reliable access to EC2 workloads.

In this lesson, we’ll demonstrate how to allocate, associate, and manage Elastic IPs in AWS. Elastic IPs provide a static, public IPv4 address that remains constant across instance stop/start cycles, ensuring reliable access to your EC2 workloads.

## Why Use Elastic IPs?

By default, EC2 instances in a public subnet receive a **dynamic** public IP that changes whenever you stop and start the instance. This can disrupt services or remote connections.

1. Launch an EC2 instance named **myserver** in your VPC’s public subnet (with an Internet Gateway attached).
2. Note its current public IP (e.g., `52.90.159.117`).
3. Stop and then restart **myserver** via **Instance state > Stop instance** and **Start instance**.
4. Observe that its public IP has changed:

<Frame>
  ![The image shows an AWS EC2 management console with details of a running instance named "myserver." It displays information such as the instance ID, public and private IP addresses, instance type, and status.](https://kodekloud.com/kk-media/image/upload/v1752863211/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP-Demo/aws-ec2-management-console-myserver.jpg)
</Frame>

<Frame>
  ![The image shows an AWS EC2 Management Console with a list of instances, highlighting one named "myserver" that is currently running. The details of the selected instance, including its public and private IP addresses, are displayed below.](https://kodekloud.com/kk-media/image/upload/v1752863212/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP-Demo/aws-ec2-management-console-myserver-instance.jpg)
</Frame>

| Public IP Type    | Persistence            | Cost                    | Use Case                       |
| ----------------- | ---------------------- | ----------------------- | ------------------------------ |
| Dynamic Public IP | Changes on stop/start  | Free                    | Short-lived, test instances    |
| Elastic IP (EIP)  | Remains until released | Charged when unattached | Static endpoint for production |

<Callout icon="lightbulb" color="#1CB2FE">
  Elastic IPs are free when associated with a running instance. AWS charges apply if you reserve an Elastic IP without attaching it.
</Callout>

## 1. Allocating an Elastic IP

1. In the EC2 console, select **Elastic IPs**.
2. Click **Allocate Elastic IP address**.
3. Accept the default settings (Amazon’s IPv4 pool) and click **Allocate**.

<Frame>
  ![The image shows an AWS console page for allocating an Elastic IP address, with options for selecting a network border group and public IPv4 address pool. There are also sections for global static IP addresses and optional tags.](https://kodekloud.com/kk-media/image/upload/v1752863214/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP-Demo/aws-console-elastic-ip-allocation.jpg)
</Frame>

After allocation, you’ll see your new Elastic IP (e.g., `35.173.92.86`):

<Frame>
  ![The image shows an AWS Management Console screen where an Elastic IP address has been successfully allocated. The allocated public IPv4 address is 35.173.92.86.](https://kodekloud.com/kk-media/image/upload/v1752863216/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP-Demo/aws-management-console-elastic-ip-allocated.jpg)
</Frame>

## 2. Associating the Elastic IP

1. Select the allocated Elastic IP.
2. Choose **Actions > Associate Elastic IP address**.
3. For **Resource type**, pick **Instance** and select **myserver**.
4. If applicable, choose the correct private IP, then click **Associate**.

<Frame>
  ![The image shows an AWS console interface for associating an Elastic IP address with an EC2 instance. It includes options to select the resource type and instance, with a warning about reassociation.](https://kodekloud.com/kk-media/image/upload/v1752863218/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP-Demo/aws-console-elastic-ip-ec2-instance.jpg)
</Frame>

Once associated, **myserver** will display the Elastic IP as its public address:

<Frame>
  ![The image shows an AWS Management Console screen where an Elastic IP address has been successfully associated with an EC2 instance. The interface displays details like the public IPv4 address and associated instance ID.](https://kodekloud.com/kk-media/image/upload/v1752863219/notes-assets/images/AWS-Networking-Fundamentals-Elastic-IP-Demo/aws-management-console-elastic-ip-ec2.jpg)
</Frame>

## 3. Verifying Reachability

Run a simple ping test from your local machine or CloudShell:

```powershell  theme={null}
PS C:\> ping 35.173.92.86

Pinging 35.173.92.86 with 32 bytes of data:
Reply from 35.173.92.86: bytes=32 time=22ms TTL=112
Reply from 35.173.92.86: bytes=32 time=21ms TTL=112
Reply from 35.173.92.86: bytes=32 time=15ms TTL=112
Reply from 35.173.92.86: bytes=32 time=19ms TTL=112

Ping statistics for 35.173.92.86:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 15ms, Maximum = 22ms, Average = 19ms
```

Stop and start **myserver** again. Notice that `35.173.92.86` remains unchanged—your Elastic IP stays attached throughout.

## 4. Cleaning Up (Optional)

To prevent unnecessary charges, release the Elastic IP when you’re done:

1. Select the Elastic IP, then **Actions > Disassociate Elastic IP address**.
2. After it’s disassociated, choose **Actions > Release Elastic IP address**.
3. Confirm to remove the reservation from your account.

<Callout icon="triangle-alert" color="#FF6B6B">
  Releasing an Elastic IP makes it available to other AWS customers. You cannot reclaim the same address once released.
</Callout>

***

## Links and References

* [AWS Elastic IP Addresses Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)
* [EC2 User Guide: Managing Elastic IPs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)
* [AWS EC2 Service Home](https://aws.amazon.com/ec2/)