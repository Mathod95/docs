---
title: VPC Peering
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Transit-Networks/VPC-Peering/page
sourcesVideos:
  -
---

> VPC Peering establishes a private network connection between two VPCs, enabling communication as if on the same network.

In AWS, each Virtual Private Cloud (VPC) is an isolated network boundary. By default, resources in one VPC cannot reach resources in another VPC without an explicit link.

<Frame>
  ![The image illustrates the behavior of Virtual Private Clouds (VPCs) acting as network boundaries, showing two VPCs with a boundary between them.](https://kodekloud.com/kk-media/image/upload/v1752863431/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering/vpc-network-boundaries-illustration.jpg)
</Frame>

## What Is VPC Peering?

VPC Peering establishes a private network connection between two VPCs, allowing instances to communicate as if they were on the same network. You can peer:

* VPCs within the same AWS Region
* VPCs across different regions (Inter-Region Peering)
* VPCs in separate AWS accounts

<Frame>
  ![The image illustrates VPC Peering between two AWS accounts, each containing a Virtual Private Cloud (VPC).](https://kodekloud.com/kk-media/image/upload/v1752863432/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering/vpc-peering-aws-accounts-diagram.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  Once peered, you must update route tables; peering alone doesn’t modify routing.
</Callout>

## Pricing Overview

| Charge Type            | Details                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| Peering Connection     | No setup fee or hourly rate                                        |
| Intra-AZ Data Transfer | Free (within the same Availability Zone over a peering connection) |
| Inter-AZ Data Transfer | Standard cross-AZ rates apply                                      |

## Establishing a VPC Peering Connection

Assume two VPCs with non-overlapping CIDR blocks:

* **VPC1**: `10.1.0.0/16`
* **VPC2**: `10.2.0.0/16`

Steps to create the peering link:

1. **Request Peering**
   * AWS Console: VPC dashboard → Peering Connections → Create Peering Connection
   * AWS CLI:
     ```bash  theme={null}
     aws ec2 create-vpc-peering-connection \
       --vpc-id vpc-01234567 --peer-vpc-id vpc-089abcdef
     ```
2. **Accept Peering**
   * Console or CLI (`accept-vpc-peering-connection`) by the peer VPC owner.
3. **Verify Connection**
   * Status changes to `active` in the Peering Connections list—but routing is still pending.

<Frame>
  ![The image illustrates a VPC peering process between two virtual private clouds (VPC 1 and VPC 2) with IP ranges 10.1.0.0/16 and 10.2.0.0/16, showing the sending and accepting of a peering request.](https://kodekloud.com/kk-media/image/upload/v1752863433/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering/vpc-peering-process-ip-ranges-diagram.jpg)
</Frame>

## Configuring Route Tables

After peering is active, add routes in each VPC’s route table:

VPC1 route table

```text  theme={null}
Destination     Target
10.2.0.0/16     pcx-0a1b2c3d4e5f6g7h
```

VPC2 route table

```text  theme={null}
Destination     Target
10.1.0.0/16     pcx-0a1b2c3d4e5f6g7h
```

This ensures traffic flows over the peering link instead of the internet gateway.

<Frame>
  ![The image illustrates a VPC peering connection between two virtual private clouds (VPC 1 and VPC 2) with their respective IP ranges and routing tables.](https://kodekloud.com/kk-media/image/upload/v1752863434/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering/vpc-peering-connection-ip-ranges-routing.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  VPC Peering is non-transitive. If VPC1 peers with VPC2, and VPC2 peers with VPC3, VPC1 cannot reach VPC3 through VPC2. Each pair requires its own peering connection.
</Callout>

## Transitive Peering Is Not Supported

* VPC1 ↔ VPC2
* VPC2 ↔ VPC3
* **No** indirect VPC1 ↔ VPC3 communication

## Summary

<Frame>
  ![The image is a summary slide about VPC Peering, highlighting three points: network connection between VPCs, connection across regions and AWS accounts, and cost details regarding data transfer.](https://kodekloud.com/kk-media/image/upload/v1752863435/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering/vpc-peering-summary-network-connection.jpg)
</Frame>

* VPC Peering connects two VPCs privately.
* Peerings can span regions and AWS accounts.
* No cost for the connection itself; data transfer pricing applies.
* Each VPC pair requires its own peering link—no transit routing.

## Links and References

* [AWS VPC Peering Guide](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html)
* [AWS Networking Fundamentals](https://aws.amazon.com/architecture/networking-and-content-delivery/)
* [AWS CLI Reference: create-vpc-peering-connection](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-vpc-peering-connection.html)

---

> This tutorial explains how to establish a VPC peering connection between two AWS VPCs for EC2 instance communication.

In this tutorial, you’ll learn how to establish a VPC peering connection between two AWS VPCs so that their EC2 instances can communicate over the private AWS network:

| VPC Identifier | CIDR Block  | EC2 Instance | Private IP |
| -------------- | ----------- | ------------ | ---------- |
| VPC-A          | 10.1.0.0/16 | server1      | 10.1.1.13  |
| VPC-B          | 10.2.0.0/16 | server2      | 10.2.1.139 |

<Callout icon="lightbulb" color="#1CB2FE">
  Make sure both VPCs have security groups and network ACLs allowing ICMP traffic. You also need IAM permissions to manage VPC peering and route tables.
</Callout>

Since VPCs are isolated by default, pinging from **server1** to **server2** will initially fail:

```bash  theme={null}
[ec2-user@ip-10-1-1-13 ~]$ ping 10.2.1.139
PING 10.2.1.139 (10.2.1.139) 56(84) bytes of data.
^C
--- 10.2.1.139 ping statistics ---
195 packets transmitted, 0 received, 100% packet loss
```

## 1. Create the VPC Peering Connection

1. Open the AWS VPC console and select **Peering Connections** → **Create Peering Connection**.
2. Name the connection `VPC-A-to-VPC-B`.
3. Under **Requester**, choose **VPC-A**.
4. Under **Accepter**, select your account and region, then choose **VPC-B**.
5. Click **Create Peering Connection**.

<Frame>
  ![The image shows the AWS VPC Management Console interface for creating a peering connection, with options to select a local VPC and specify regions.](https://kodekloud.com/kk-media/image/upload/v1752863426/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering-Demo/aws-vpc-management-console-peering-connection.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  You can also provision VPC peering using Infrastructure as Code tools like Terraform or AWS CloudFormation.
</Callout>

## 2. Accept the Peering Request

1. In **Peering Connections**, locate the new connection in **Pending Acceptance**.
2. Select it, then choose **Actions** → **Accept Request**.

<Frame>
  ![The image shows an AWS Management Console screen displaying details of a VPC peering connection request, which is pending acceptance. It includes information such as requester and accepter IDs, VPCs, and regions.](https://kodekloud.com/kk-media/image/upload/v1752863427/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering-Demo/aws-management-console-vpc-peering-request.jpg)
</Frame>

Once accepted, its status changes to **Active**:

<Frame>
  ![The image shows an AWS VPC dashboard with a peering connection established between two VPCs, indicated by a green status bar and details about the connection.](https://kodekloud.com/kk-media/image/upload/v1752863428/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering-Demo/aws-vpc-dashboard-peering-connection.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Even after peering is active, traffic won’t flow until you update each VPC’s route tables.
</Callout>

## 3. Update Route Tables

Each VPC needs a route pointing to the other VPC’s CIDR block through the peering connection:

1. In the VPC console, go to **Route Tables**.
2. Select the route table for **VPC-A**.

<Frame>
  ![The image shows the AWS management console displaying the route tables for a Virtual Private Cloud (VPC). It lists several route tables with details such as route table ID, subnet associations, and routes with their destinations and targets.](https://kodekloud.com/kk-media/image/upload/v1752863429/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering-Demo/aws-management-console-vpc-route-tables.jpg)
</Frame>

3. Under **Routes**, click **Edit routes** → **Add route**:
   * Destination: `10.2.0.0/16`
   * Target: the peering connection (`VPC-A-to-VPC-B`)
4. Save changes.

<Frame>
  ![The image shows the AWS Management Console with a VPC route table being edited, displaying routes with their destinations, targets, and statuses.](https://kodekloud.com/kk-media/image/upload/v1752863430/notes-assets/images/AWS-Networking-Fundamentals-VPC-Peering-Demo/aws-management-console-vpc-route-table.jpg)
</Frame>

5. Repeat these steps on **VPC-B**’s route table, adding a route to `10.1.0.0/16` via the same peering connection.

## 4. Verify Connectivity

Return to **server1** and ping **server2**:

```bash  theme={null}
[ec2-user@ip-10-1-1-13 ~]$ ping 10.2.1.139
PING 10.2.1.139 (10.2.1.139) 56(84) bytes of data.
64 bytes from 10.2.1.139: icmp_seq=1 ttl=127 time=1.88 ms
64 bytes from 10.2.1.139: icmp_seq=2 ttl=127 time=1.43 ms
64 bytes from 10.2.1.139: icmp_seq=3 ttl=127 time=1.38 ms
^C
--- 10.2.1.139 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 1.382/1.563/1.882/0.187 ms
```

Your EC2 instances can now communicate across VPCs using the private AWS backbone.

## Links and References

* [AWS VPC Peering Documentation](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html)
* [AWS Route Tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
* [Terraform AWS VPC Peering Module](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest)