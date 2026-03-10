---
title: NAT Gateway
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/NAT-Gateways-VPC/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/456455aa-064a-4edc-830e-8702935929cd?autoplay=true
---

> This guide explains NAT Gateways, their importance for private subnet internet access, and how to deploy and manage them in AWS.

In this guide, you’ll learn what NAT Gateways are, why they’re essential for private subnet internet access, and how to deploy and manage them in AWS.

## Overview

When you run instances in private subnets, you often still need outbound internet connectivity—for OS updates, package downloads, and API calls—without exposing those instances to inbound traffic. NAT Gateways solve this by enabling secure, outbound-only internet access while keeping your servers hidden from unsolicited inbound connections.

## The Challenge

You have an EC2 instance in a private subnet that needs to pull updates from the internet.

* Attaching an Internet Gateway (IGW) and routing traffic through it turns your subnet public.
* A public subnet exposes instances to inbound internet traffic, increasing security risk.

<Callout icon="triangle-alert" color="#FF6B6B">
  Avoid routing private instance traffic directly through an Internet Gateway, as this exposes them to inbound connections.
</Callout>

## Introducing NAT Gateways

A NAT Gateway is a fully managed AWS service that allows instances in private subnets to send outbound traffic to the internet while blocking inbound traffic initiated from the internet. Key features include:

* Outbound-only traffic with automatic source IP translation
* Requires an Internet Gateway on the VPC for upstream connectivity
* Elastic IP–backed for consistent public IPs

<Frame>
  ![The image is a diagram illustrating a NAT Gateway setup within a VPC, showing four availability zones, each with a connection to the internet.](https://kodekloud.com/kk-media/image/upload/v1752863293/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC/nat-gateway-vpc-setup-diagram.jpg)
</Frame>

## Deployment Steps

1. **Create or Attach an Internet Gateway**
   * In the AWS Console under **VPC → Internet Gateways**, attach the IGW to your VPC.
2. **Configure a Public Subnet**
   * Create a subnet and tag it as public.
   * Update its route table:
     * Destination: `0.0.0.0/0`
     * Target: your Internet Gateway
3. **Launch a NAT Gateway**
   * Go to **VPC → NAT Gateways**.
   * Select the public subnet and assign an Elastic IP.
4. **Update Private Subnet Routes**
   * For each private subnet, modify its route table:
     * Destination: `0.0.0.0/0`
     * Target: the NAT Gateway

<Callout icon="lightbulb" color="#1CB2FE">
  Each NAT Gateway requires an Elastic IP. Ensure you have available Elastic IPs or allocate new ones before deployment.
</Callout>

## IGW vs NAT Gateway Comparison

| Feature                | Internet Gateway (IGW)          | NAT Gateway                      |
| ---------------------- | ------------------------------- | -------------------------------- |
| Inbound Connections    | Allowed                         | Blocked (outbound-only)          |
| Source IP Preservation | Yes                             | No (performs source NAT)         |
| Managed Service        | Yes                             | Yes                              |
| Public IP Requirement  | No (automatic public IP on ENI) | Elastic IP must be assigned      |
| Use Case               | Public subnet internet access   | Private subnet outbound internet |

## Traffic Flow

1. **Private Instance → NAT Gateway**
2. **NAT Gateway → Internet Gateway → Internet**
3. **Return Traffic → Internet Gateway → NAT Gateway → Private Instance**

## Key Characteristics

* **Fully Managed**: AWS handles provisioning, scaling, and health monitoring.
* **Automatic Scaling**: Starts at 5 Gbps and can scale up to 100 Gbps.
* **AZ Isolation**: Deploy one per Availability Zone (AZ) for high availability.
* **Billing**: Hourly NAT Gateway charge + per GB data processed.

<Frame>
  ![The image is a summary of NAT Gateways, highlighting their function, deployment on public subnets, use of Elastic IPs, and AZ-reliant service requirements.](https://kodekloud.com/kk-media/image/upload/v1752863294/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC/nat-gateways-summary-elastic-ips.jpg)
</Frame>

## Cost Considerations

<Callout icon="triangle-alert" color="#FF6B6B">
  NAT Gateways incur hourly charges per gateway and data processing fees. Monitor usage in AWS Cost Explorer to avoid unexpected costs.
</Callout>

## High Availability

* Deploy a NAT Gateway in each AZ where you have private subnets.
* Update each private subnet’s route table to point to the AZ-specific NAT Gateway.
* Consider combining with AWS Transit Gateway for multi-VPC designs.

## Summary

* **Purpose**: Enable outbound internet access for private subnets without inbound exposure.
* **Requirements**: Internet Gateway, Elastic IP, public subnet for the NAT Gateway.
* **High Availability**: One NAT Gateway per AZ.
* **Management & Billing**: AWS-managed; pay hourly + per GB.

<Frame>
  ![The image is a summary slide with points about NAT Gateway, including routing for private subnets, AWS management, and charging details.](https://kodekloud.com/kk-media/image/upload/v1752863295/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC/nat-gateway-summary-routing-aws.jpg)
</Frame>

## Links and References

* [AWS NAT Gateway Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
* [AWS VPC Internet Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)
* [Terraform AWS NAT Gateway Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/nat_gateway)

---


- NAT Gateways allow subnets to talk to the internet but connections must be initiatied from within the VPC
- Nat Gateways are deployed onto public subnets so that they have a public IP and internet access
- Uses Elastic IPs
- AZ-reliant services; need 1 NAT Gateway in each AZ
- Route table for private subnets should point to NAT gateway
- Managed by AWS
- Charged for each hour that NAT gateawy is available and for each Gigabyte of data that it processes
- A NAT gateway supports 5 Gbps of bandwidth and automatically scales up to 100 Gbps

---

> This walkthrough explains how to configure an AWS NAT Gateway for internet access in a private subnet while blocking unsolicited inbound connections.

In this walkthrough, you’ll learn how to configure an AWS NAT Gateway to enable internet access for EC2 instances in a private subnet—while preventing unsolicited inbound connections from the internet. By the end, only instances that initiate outbound requests will receive responses.

## 1. Create a New VPC

1. Open the **VPC** console and select **Create VPC**.
2. Enter a **Name tag** (e.g., `demo-vpc`) and set the **IPv4 CIDR block** to `10.0.0.0/16`.
3. Leave IPv6 settings disabled and click **Create**.

<Frame>
  ![The image shows the AWS Management Console interface for creating a VPC, with options for setting the name tag, IPv4 CIDR block, and other configurations.](https://kodekloud.com/kk-media/image/upload/v1752863282/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-management-console-create-vpc.jpg)
</Frame>

## 2. Create a Private Subnet

This subnet will host your EC2 instance without a public IP.

* **Name**: `private-subnet`
* **Availability Zone**: e.g., `us-east-1b`
* **IPv4 CIDR block**: `10.0.1.0/24`

<Frame>
  ![The image shows the AWS Management Console interface for creating a subnet within a VPC. It includes fields for VPC ID, subnet name, availability zone, and IPv4 CIDR block.](https://kodekloud.com/kk-media/image/upload/v1752863283/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-management-console-create-subnet-vpc.jpg)
</Frame>

## 3. Launch an EC2 Instance in the Private Subnet

1. Navigate to the **EC2** console → **Launch Instance**.
2. Select the **Amazon Linux 2 AMI** (or your preferred AMI).
3. Under **Network settings**:
   * Choose your **demo-vpc** and the **private-subnet**.
   * Disable **Auto-assign Public IP**.
4. Configure or select a security group (default settings are fine).
5. Review and **Launch**. Name it `private-server`.

Because there’s no public IP, the instance cannot be reached directly from the internet.

<Frame>
  ![The image shows an AWS EC2 instance launch configuration screen, detailing network settings, security group options, and a summary of the instance specifications.](https://kodekloud.com/kk-media/image/upload/v1752863284/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-ec2-instance-launch-configuration.jpg)
</Frame>

## 4. Create and Attach an Internet Gateway

An Internet Gateway (IGW) is required to give public subnets internet access.

1. In the VPC console, go to **Internet Gateways** → **Create Internet Gateway**.
2. Name it `my-igw` and click **Create**.
3. Select the new IGW → **Actions** → **Attach to VPC** → choose `demo-vpc`.

<Frame>
  ![The image shows an AWS Management Console screen displaying the "Internet gateways" section, with one internet gateway listed as attached to a VPC.](https://kodekloud.com/kk-media/image/upload/v1752863286/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-management-console-internet-gateways-vpc.jpg)
</Frame>

## 5. Create a Public Subnet

This subnet will host the NAT Gateway and must have a route to the IGW.

* **Name**: `public-subnet`
* **Availability Zone**: same or different (e.g., `us-east-1b`)
* **IPv4 CIDR block**: `10.0.2.0/24`

<Frame>
  ![The image shows an AWS VPC dashboard with a notification indicating the successful creation of a subnet. The subnet details, including its ID and availability, are displayed.](https://kodekloud.com/kk-media/image/upload/v1752863288/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-vpc-dashboard-subnet-creation.jpg)
</Frame>

## 6. Configure Route Tables

You need two route tables: one public and one private.

<Callout icon="lightbulb" color="#1CB2FE">
  Separate route tables help isolate internet-facing and internal traffic.
</Callout>

| Route Table Name    | Associated Subnet | Default Route Target        |
| ------------------- | ----------------- | --------------------------- |
| public-route-table  | public-subnet     | Internet Gateway (`my-igw`) |
| private-route-table | private-subnet    | (added after NAT creation)  |

### Steps

1. **Create** `public-route-table` → select `demo-vpc` → **Create**.
2. **Edit routes** → **Add route** `0.0.0.0/0` → Target: **Internet Gateway** → choose `my-igw` → **Save**.
3. **Associate** with `public-subnet`.
4. **Create** `private-route-table` → select `demo-vpc` → **Create**.
5. **Associate** with `private-subnet` (no default route yet).

<Frame>
  ![The image shows an AWS Management Console screen displaying details of a VPC route table, including route entries and their statuses. The route table has two routes, one for internet gateway access and another for local network access, both marked as active.](https://kodekloud.com/kk-media/image/upload/v1752863289/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-vpc-route-table-details.jpg)
</Frame>

## 7. Deploy a NAT Gateway

In a public subnet, NAT Gateways allow private instances to access the internet securely.

1. Go to **NAT Gateways** → **Create NAT Gateway**.
2. Name it `my-nat-gateway`.
3. Subnet: **public-subnet**.
4. Allocate a new **Elastic IP**.
5. Click **Create NAT Gateway**.

<Frame>
  ![The image shows an AWS Management Console screen displaying details of a newly created NAT gateway, which is currently in a pending state.](https://kodekloud.com/kk-media/image/upload/v1752863290/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-management-console-nat-gateway-pending.jpg)
</Frame>

You can also use the AWS CLI:

```bash  theme={null}
aws ec2 create-nat-gateway \
  --subnet-id <public-subnet-id> \
  --allocation-id <eip-allocation-id>
```

## 8. Update the Private Route Table

After the NAT Gateway becomes **available**:

1. Open `private-route-table` → **Edit routes**.
2. **Add route** `0.0.0.0/0` → Target: **NAT Gateway** → select `my-nat-gateway`.
3. **Save**.

Now, instances in `private-subnet` will send outbound traffic through the NAT Gateway while remaining inaccessible from the internet.

## 9. Plan for High Availability

NAT Gateways are zonal resources. To avoid a single point of failure:

* Deploy one NAT Gateway per Availability Zone.
* Update each private route table to point to the NAT Gateway in its own AZ.

<Callout icon="triangle-alert" color="#FF6B6B">
  If the AZ with your NAT Gateway goes down, all instances using it lose internet access.
</Callout>

<Frame>
  ![The image shows an AWS Management Console screen displaying details of a public subnet within a Virtual Private Cloud (VPC). It includes information such as the subnet ID, state, IPv4 CIDR, and availability zone.](https://kodekloud.com/kk-media/image/upload/v1752863292/notes-assets/images/AWS-Networking-Fundamentals-NAT-Gateways-VPC-Demo/aws-management-console-public-subnet-vpc.jpg)
</Frame>

## Links and References

* [Amazon VPC Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
* [AWS NAT Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
* [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/index.html)