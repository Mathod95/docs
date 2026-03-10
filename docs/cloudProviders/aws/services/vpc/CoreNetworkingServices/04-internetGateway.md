---
title: Internet Gateway
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Internet-Gateways-VPC/page
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Internet-Gateway-Demo/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/7258034f-e429-445f-ba36-5bc0bb772004
---

> This article explains how Internet Gateways provide internet access for subnets in an AWS VPC, converting private subnets into public ones.

In this lesson, we'll explore how Internet Gateways enable internet access for subnets in an Amazon Virtual Private Cloud (VPC), effectively converting private subnets into public ones.

By default, all newly created subnets are private: instances cannot reach the internet, nor can external clients initiate connections to them. Attaching an Internet Gateway to your VPC and updating route tables provides the necessary ingress and egress paths for internet communication.

## Key Characteristics of Internet Gateways

| Feature           | Description                                                        |
| ----------------- | ------------------------------------------------------------------ |
| Attachment Limit  | One Internet Gateway per VPC                                       |
| VPC Association   | An Internet Gateway can only be attached to a single VPC at a time |
| High Availability | Region-resilient across all Availability Zones                     |

<Callout icon="lightbulb" color="#1CB2FE">
  Internet Gateways are highly available within an AWS region and handle both ingress and egress traffic for your VPC.
</Callout>

## Steps to Make a Subnet Public

1. **Create an Internet Gateway**
   ```bash  theme={null}
   aws ec2 create-internet-gateway
   ```
2. **Attach the Internet Gateway to Your VPC**
   ```bash  theme={null}
   aws ec2 attach-internet-gateway \
     --internet-gateway-id igw-0123456789abcdef0 \
     --vpc-id vpc-0abcdef1234567890
   ```
3. **Create a Custom Route Table**
   ```bash  theme={null}
   aws ec2 create-route-table --vpc-id vpc-0abcdef1234567890
   ```
4. **Add a Default Route (`0.0.0.0/0`)**\
   Point to the Internet Gateway:
   ```bash  theme={null}
   aws ec2 create-route \
     --route-table-id rtb-0abcdef1234567890 \
     --destination-cidr-block 0.0.0.0/0 \
     --gateway-id igw-0123456789abcdef0
   ```
5. **Associate the Public Subnet with the Custom Route Table**
   ```bash  theme={null}
   aws ec2 associate-route-table \
     --subnet-id subnet-01234abcde5678fgh \
     --route-table-id rtb-0abcdef1234567890
   ```

<Frame>
  ![The image illustrates the setup of an Internet Gateway within a VPC, showing steps like creating the gateway, attaching it to the VPC, creating a custom route table, and configuring the default route. It includes a diagram of a region with a VPC, availability zone, public subnet, and route table.](https://kodekloud.com/kk-media/image/upload/v1752863236/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateways-VPC/internet-gateway-vpc-setup-diagram.jpg)
</Frame>

The default route (`0.0.0.0/0 → igw-xxxxxxxx`) ensures that any traffic not matching more specific routes is forwarded to the Internet Gateway. Associating your subnet with this route table makes it a **public subnet**, enabling instances to send and receive internet traffic.

## Public IP Assignment

Instances in a public subnet only receive a private IP address (e.g., `192.168.1.1`) by default. To allow access from the internet, enable **Auto-assign Public IPv4 address** on the subnet or assign a public IP when launching the instance. This allocates a public IP (e.g., `1.1.1.1`) and automatically maps it to the private IP.

From the instance’s perspective:

* Incoming requests target the **public IP**.
* AWS Network Address Translation (NAT) translates the public IP to the instance’s **private IP**.
* The instance processes traffic using its private IP, unaware of the public endpoint.

<Frame>
  ![The image illustrates a network diagram of an AWS Cloud setup, showing a public subnet with a resource that has both a private IP (192.163.1.1) and a public IP (1.1.1.1), accessible by a user.](https://kodekloud.com/kk-media/image/upload/v1752863237/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateways-VPC/aws-cloud-network-diagram-public-subnet.jpg)
</Frame>

If an instance has multiple Elastic Network Interfaces (ENIs), each interface can have its own public IP address mapped to a private IP. AWS uses these mappings to direct internet traffic to the correct interface.

## Summary

| Summary Point                        | Details                                                                   |
| ------------------------------------ | ------------------------------------------------------------------------- |
| Purpose of Internet Gateway          | Provides a path for internet traffic into and out of your VPC             |
| Attachment Rules                     | One Internet Gateway per VPC; one VPC per Internet Gateway                |
| Public Subnet Requirement            | Route table must include a default route pointing to the Internet Gateway |
| Public IP for External Accessibility | Instances need a public IPv4 address (auto-assigned or manually added)    |

<Frame>
  ![The image is a summary slide with three key points about internet gateways and VPCs, highlighting connectivity, attachment, and limitations.](https://kodekloud.com/kk-media/image/upload/v1752863239/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateways-VPC/internet-gateways-vpcs-summary-slide.jpg)
</Frame>

## References

* [AWS Internet Gateways](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)
* [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
* [Amazon EC2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/)

---

Quand on créer un subnet par défault il est private (Ce qui est créer dans le subnet n'as pas accès à internet)
Il faut créer une internetGateway attach to vpc couvre toutes les AZ
public associate to the private ip of the instances/object

- Enable resources to connect to internet
- Internet Gateways attach to a VPC and are region resilient
- VPC can only have max 1 internet gateway, and an internet gateway can only be attached to max 1 VPC
- A subnet is made public once a default route points to the internet gateway in the VPC


---

> This tutorial explains how to convert a private subnet into a public subnet by attaching an Internet Gateway and updating the route table.

In this tutorial, you’ll convert a private subnet into a public subnet by attaching an Internet Gateway and updating the route table. After completing these steps, any EC2 instance launched in your public subnet will have Internet access.

## Overview

| Step | Description                                   |
| ---- | --------------------------------------------- |
| 1    | Create a VPC & Subnet                         |
| 2    | Launch an EC2 instance in the public subnet   |
| 3    | Verify default connectivity (should fail)     |
| 4    | Create & attach an Internet Gateway           |
| 5    | Configure the route table for Internet access |
| 6    | Test Internet connectivity (should succeed)   |

## Prerequisites

* An AWS account with permissions to manage VPCs and EC2.
* A generated SSH key pair (for example, `aws-demo.pem`).

<Callout icon="lightbulb" color="#1CB2FE">
  You can refer to the [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/) for more details on VPC components.
</Callout>

***

## 1. Create a VPC and Public Subnet

1. In the AWS Console, go to **VPC > Your VPCs** and click **Create VPC**.
2. Set the IPv4 CIDR block to `10.0.0.0/16`. Optionally add an IPv6 block.
3. Click **Create VPC**.

<Frame>
  ![The image shows an AWS Management Console screen displaying details of a Virtual Private Cloud (VPC) named "vpcdemo," including its ID, state, and network configurations. The left sidebar lists various VPC-related options like subnets and route tables.](https://kodekloud.com/kk-media/image/upload/v1752863224/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-management-console-vpcdemo-details.jpg)
</Frame>

4. Navigate to **Subnets > Create subnet**:
   * **Name tag**: `public-subnet`
   * **VPC**: your newly created VPC
   * **IPv4 CIDR block**: `10.0.1.0/24`
5. Click **Create subnet**.

***

## 2. Launch an EC2 Instance in the Public Subnet

1. Open **EC2 Console** > **Instances > Launch instances**.
2. For **Name**, enter `my-public-server`.
3. Choose **Amazon Linux 2023** under **Application and OS Images (AMI)**.

<Frame>
  ![The image shows an AWS EC2 instance setup page, where a user is configuring a new instance with Amazon Linux 2023 AMI and a t2.micro instance type.](https://kodekloud.com/kk-media/image/upload/v1752863225/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-ec2-instance-setup-amazon-linux.jpg)
</Frame>

4. Select the **t2.micro** instance type (free tier).
5. Under **Key pair**, choose `aws-demo.pem`.
6. Expand **Network settings > Edit** and configure:
   * **VPC**: your new VPC
   * **Subnet**: `public-subnet`
   * **Auto-assign public IP**: **Enable**

<Frame>
  ![The image shows an AWS EC2 instance launch configuration screen, detailing instance type, key pair, network settings, and a summary of the selected options.](https://kodekloud.com/kk-media/image/upload/v1752863226/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-ec2-instance-launch-configuration.jpg)
</Frame>

7. Under **Security group**, allow SSH (port 22) from `0.0.0.0/0`. Optionally add ICMP for ping.

<Frame>
  ![The image shows an AWS EC2 instance launch configuration screen, detailing security group settings and a summary of the instance specifications, including the instance type and storage volume.](https://kodekloud.com/kk-media/image/upload/v1752863228/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-ec2-instance-launch-configuration-2.jpg)
</Frame>

8. Click **Launch instance** and wait for it to switch to **running**.

***

## 3. Verify Default Connectivity (Should Fail)

After your instance is running, copy its public IP (example: `54.159.89.36`) and test connectivity:

<Frame>
  ![The image shows an AWS EC2 Management Console with details of two instances, one terminated and one running, including instance IDs, states, and public IP addresses.](https://kodekloud.com/kk-media/image/upload/v1752863229/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-ec2-management-console-instances.jpg)
</Frame>

```bash  theme={null}
ping 54.159.89.36
ssh -i aws-demo.pem ec2-user@54.159.89.36
# Connection hangs.
```

By default, there’s no Internet route, so the instance remains unreachable despite having a public IP.

***

## 4. Create and Attach an Internet Gateway

1. In the **VPC Console**, select **Internet Gateways** and click **Create internet gateway**.
   * **Name tag**: `my-internet-gateway`
2. Click **Create internet gateway**.
3. Select the newly created gateway, choose **Actions > Attach to VPC**, and select your VPC.

<Frame>
  ![The image shows an AWS Management Console screen displaying details of a newly created subnet within a Virtual Private Cloud (VPC). The subnet is listed as available with its associated VPC and IPv4 CIDR block.](https://kodekloud.com/kk-media/image/upload/v1752863231/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-management-console-subnet-details-vpc.jpg)
</Frame>

<Frame>
  ![The image shows an AWS Management Console screen displaying details of an internet gateway that is successfully attached to a VPC. It includes information such as the gateway ID, state, VPC ID, and tags.](https://kodekloud.com/kk-media/image/upload/v1752863232/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-management-console-internet-gateway-vpc.jpg)
</Frame>

> Pinging still fails because the route table isn’t updated yet.

***

## 5. Configure the Route Table for Internet Access

1. Go to **VPC > Route Tables** and click **Create route table**.
   * **Name tag**: `public-route-table`
   * **VPC**: your demo VPC
2. Click **Create route table**.
3. Select the new route table, open **Subnet associations**, click **Edit subnet associations**, check `public-subnet`, and save.

<Frame>
  ![The image shows an AWS VPC management console displaying a list of subnets and details of a selected subnet's route table. The interface includes subnet names, IDs, states, and associated VPCs.](https://kodekloud.com/kk-media/image/upload/v1752863233/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-vpc-management-console-subnets.jpg)
</Frame>

4. In the **Routes** tab, click **Edit routes** > **Add route**:
   * **Destination**: `0.0.0.0/0`
   * **Target**: `my-internet-gateway`
5. Save the route.

<Frame>
  ![The image shows an AWS Management Console screen displaying details of a route table within a Virtual Private Cloud (VPC). It includes route information and subnet associations.](https://kodekloud.com/kk-media/image/upload/v1752863235/notes-assets/images/AWS-Networking-Fundamentals-Internet-Gateway-Demo/aws-management-console-route-table-vpc.jpg)
</Frame>

***

## 6. Test Internet Connectivity (Should Succeed)

Now retry ping and SSH using the public IP:

```bash  theme={null}
ping 54.159.89.36
ssh -i aws-demo.pem ec2-user@54.159.89.36
# Welcome to your public EC2 instance!
```

Congratulations! Your `public-subnet` is now internet-enabled, and any EC2 instances launched into it can be accessed from the Internet.

## Additional Resources

* [AWS VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/)
* [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)