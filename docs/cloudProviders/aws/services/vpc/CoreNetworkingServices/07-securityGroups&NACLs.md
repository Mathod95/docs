---
title: Security Groups
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Security-Groups-NACLs/page
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Security-Groups-Demo/page
sourcesVIdeos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/751f0228-5579-4601-a711-7d0be0b25117?autoplay=true
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/8c2cb5f8-5808-46ec-898a-b9563712623f
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/2bde7f3d-33aa-440a-969f-48a5cbb571e4
---

# 

> This article explains the differences between AWS Security Groups and Network ACLs, including their configurations, behaviors, and best practices for securing a VPC.

In this lesson, we’ll cover how firewalls work, then explore AWS implementations: Network ACLs (NACLs) and Security Groups. You’ll learn the differences between stateless and stateful filtering, how to configure rules, and best practices for securing your VPC.

## Firewalls: Inbound and Outbound Traffic

A firewall monitors traffic flows and only allows connections matching predefined rules. Each rule controls:

* **Inbound**: Connections *to* your resource
* **Outbound**: Connections *from* your resource

## Stateless Firewalls

Stateless firewalls treat inbound and outbound traffic independently. You must explicitly allow both directions for every connection.

For example, a web server listening on HTTPS (port 443) needs:

1. **Ingress**: Allow TCP 443
2. **Egress**: Allow TCP 1024–65535 (ephemeral ports)

If the server also fetches updates over HTTP (port 80):

* **Egress**: Allow TCP 80
* **Ingress**: Allow TCP 1024–65535

<Callout icon="triangle-alert" color="#FF6B6B">
  Stateless firewalls *do not* track connection state. If you forget to permit the reply path, your traffic will be dropped.
</Callout>

<Frame>
  ![The image illustrates stateless firewalls, showing inbound and outbound rules with specific IP/Port actions, and a server listening on port 443.](https://kodekloud.com/kk-media/image/upload/v1752863343/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/stateless-firewalls-inbound-outbound-rules.jpg)
</Frame>

<Frame>
  ![The image illustrates the concept of stateless firewalls, showing how firewall rules are divided into inbound and outbound rules, with specific ports and actions for each. It emphasizes the need for configuration to allow both inbound and outbound traffic.](https://kodekloud.com/kk-media/image/upload/v1752863344/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/stateless-firewalls-inbound-outbound-rules-2.jpg)
</Frame>

## Stateful Firewalls

Stateful firewalls track connection state. Once you allow an incoming request, the outbound response is automatically permitted (and vice versa).

Using the same web server example:

* **Ingress**: Allow TCP 443
* **Egress**: *No rule needed* for ephemeral ports
* **Egress**: Allow TCP 80
* **Ingress**: *No rule needed* for ephemeral ports

<Callout icon="lightbulb" color="#1CB2FE">
  Stateful filtering simplifies rules management by automatically permitting return traffic.
</Callout>

<Frame>
  ![The image explains how stateful firewalls work, showing how they manage inbound and outbound requests and responses by allowing specific IP/port actions.](https://kodekloud.com/kk-media/image/upload/v1752863345/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/stateful-firewalls-inbound-outbound-requests.jpg)
</Frame>

## AWS Network ACLs (NACLs)

A Network ACL filters traffic *entering* and *leaving* subnets. Key points:

* Every subnet **must** be associated with exactly one NACL.
* A NACL can apply to multiple subnets.
* NACLs are **stateless**: separate ingress/egress rules.
* They do **not** filter intra-subnet traffic.

<Frame>
  ![The image explains Network Access Control Lists (NACLs) in a Virtual Private Cloud (VPC), showing how they filter traffic entering and leaving subnets but not within them. It includes a diagram with public and private subnets.](https://kodekloud.com/kk-media/image/upload/v1752863347/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/nacl-vpc-traffic-filtering-diagram.jpg)
</Frame>

### Comparing NACLs vs. Security Groups

| Feature               | Network ACL (Stateless)           | Security Group (Stateful)                        |
| --------------------- | --------------------------------- | ------------------------------------------------ |
| Scope                 | Subnet-level                      | Instance/ENI-level                               |
| Direction             | Ingress & Egress rules (explicit) | Ingress rules only (egress auto for responses)   |
| Default Behavior      | Default rule: *Deny all*          | Default egress: *Allow all*; ingress: *Deny all* |
| Rule Actions          | Allow or Deny                     | Allow only (implicit deny)                       |
| Rule Evaluation Order | By rule number (lowest first)     | All rules are evaluated; no priority             |
| Stateful Tracking     | No                                | Yes                                              |

## AWS Security Groups

Security Groups act as **stateful** firewalls for individual resources (EC2, RDS, ENIs, etc.):

* Only the initiating direction is needed; return traffic is auto-allowed.
* Rules apply per resource, not per subnet.

<Frame>
  ![The image compares NACLs and Security Groups, explaining that NACLs are stateless firewalls monitoring traffic for subnets, while Security Groups are stateful and act as personal firewalls for individual resources. It includes a diagram of a Virtual Private Cloud (VPC) with public and private subnets.](https://kodekloud.com/kk-media/image/upload/v1752863348/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/nacls-security-groups-vpc-diagram.jpg)
</Frame>

### Configuring Security Group Rules

In the AWS Console, you define **Inbound** and **Outbound** rules separately. The fields are identical but apply in opposite directions.

```plaintext  theme={null}
Inbound rules
┌─────────┬─────────┬───────────┬──────────────┬────────────┐
│ Type    │ Protocol│ Port Range│ Source       │ Description│
├─────────┼─────────┼───────────┼──────────────┼────────────┤
│ HTTP    │ TCP     │ 80        │ 0.0.0.0/0    │ (optional) │
└─────────┴─────────┴───────────┴──────────────┴────────────┘
```

<Frame>
  ![The image shows a screenshot of inbound rules for a security group, allowing HTTP traffic on port 80 from any source (0.0.0.0/0).](https://kodekloud.com/kk-media/image/upload/v1752863350/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/inbound-rules-security-group-http-port-80.jpg)
</Frame>

Fields you’ll configure:

* **Type**: Predefined (HTTP, SSH) or *Custom*
* **Protocol**: TCP, UDP, ICMP, or *All*
* **Port Range**: Single port or port range
* **Source/Destination**: CIDR block or security group ID
* **Description**: Free-form text

Outbound rules follow the same format:

<Frame>
  ![The image shows a table of outbound rules for a security group, allowing all traffic to all destinations (0.0.0.0/0) with IPv4.](https://kodekloud.com/kk-media/image/upload/v1752863351/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/outbound-rules-security-group-ipv4.jpg)
</Frame>

<Callout icon="lightbulb" color="#1CB2FE">
  If no outbound rules exist, *all* traffic is blocked by default. Security Groups can only **allow** traffic; there’s no explicit deny.
</Callout>

<Frame>
  ![The image contains text explaining that security groups block all traffic when no rules are set, and that rules only allow traffic without a deny option.](https://kodekloud.com/kk-media/image/upload/v1752863352/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/security-groups-traffic-rules-explanation.jpg)
</Frame>

## NACL Rules Example

Every NACL rule includes a rule number (priority), type, protocol, port range, CIDR, and an Allow/Deny action. Rules are processed in ascending order.

<Frame>
  ![The image shows a table of network ACL (NACL) inbound rules, detailing rule numbers, types, protocols, port ranges, sources, and whether the traffic is allowed or denied.](https://kodekloud.com/kk-media/image/upload/v1752863353/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/network-acl-inbound-rules-table.jpg)
</Frame>

## Multiple Security Groups per Resource

You can attach multiple Security Groups to a single resource. AWS merges all allow rules into one effective policy.

<Frame>
  ![The image explains the concept of multiple security groups, showing how they can be assigned to a single resource with merged rules, and includes a table of ports and IP ranges for a combined "web + mgmt" security group.](https://kodekloud.com/kk-media/image/upload/v1752863354/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/multiple-security-groups-resource-rules.jpg)
</Frame>

## Default Behaviors and Associations

<Frame>
  ![The image contains three colored text boxes with information about security groups, subnets, and network ACLs in a VPC. Each box provides a specific detail about default outbound rules, subnet associations, and network ACL limitations.](https://kodekloud.com/kk-media/image/upload/v1752863355/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/vpc-security-groups-subnets-acls.jpg)
</Frame>

* **Security Groups**: Default egress allows all traffic.
* **NACLs**: Each subnet needs one NACL; one-to-many relationship.
* **Associations**: Subnet ↔ one NACL; NACL ↔ many subnets.

## Traffic Exempt from NACL Filtering

Certain AWS control-plane and metadata endpoints bypass NACLs:

<Frame>
  ![The image lists services and endpoints that are not filtered by Network ACLs, including Amazon DNS, DHCP, EC2 instance metadata, ECS task metadata, Windows license activation, Amazon Time Sync Service, and reserved IP addresses for the default VPC router.](https://kodekloud.com/kk-media/image/upload/v1752863356/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/unfiltered-services-endpoints-network-acls.jpg)
</Frame>

* Amazon DNS
* DHCP
* EC2 Instance Metadata
* ECS Task Metadata
* Windows License Activation
* Amazon Time Sync Service
* Reserved VPC Router IPs

## Summary

<Frame>
  ![The image is a summary slide describing different types of firewalls and network ACLs, highlighting their characteristics and functions. It includes four points about stateless and stateful firewalls and network ACLs.](https://kodekloud.com/kk-media/image/upload/v1752863357/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/firewalls-network-acls-summary-slide.jpg)
</Frame>

* **Stateless Firewalls**: Require explicit ingress *and* egress rules.
* **Stateful Firewalls**: Automatically permit response traffic.
* **NACLs**: Stateless, subnet-level, Allow/Deny capabilities.
* **Security Groups**: Stateful, resource-level, Allow-only rules.

<Frame>
  ![The image is a summary slide about security groups, highlighting their role as firewalls, their stateful nature, and how their rules are applied and merged.](https://kodekloud.com/kk-media/image/upload/v1752863359/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/security-groups-firewalls-stateful-rules.jpg)
</Frame>

* Applied per ENI/instance; rules are merged across groups.
* Outbound is wide-open by default.

<Frame>
  ![The image is a summary slide discussing network ACLs in a VPC, highlighting that every subnet must be associated with a network ACL and that a subnet can only be associated with one network ACL at a time.](https://kodekloud.com/kk-media/image/upload/v1752863360/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-NACLs/vpc-network-acls-subnet-summary.jpg)
</Frame>

* Each subnet requires exactly one NACL.
* Rules evaluated in numeric order, ending with a catch-all rule.

***

## Links and References

* [AWS Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
* [AWS Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
* [AWS VPC Overview](https://docs.aws.amazon.com/vpc/latest/userguide/)
* [AWS CLI EC2 Reference](https://docs.aws.amazon.com/cli/latest/reference/ec2/index.html)


---


> This lesson explores securing AWS resources using Security Groups and Network ACLs, covering EC2 instance launch, traffic control, and best practices for network security.

In this lesson, we’ll explore how to secure AWS resources using Security Groups and Network ACLs (NACLs). You’ll learn to:

* Launch an EC2 instance
* Configure Security Groups to control inbound/outbound traffic
* Demonstrate stateful behavior
* Split and reuse groups for modular access control
* Reference Security Groups in other rules

By the end, you’ll have hands-on experience with AWS best practices for network security.

## Launching the EC2 Instance

Start by launching an EC2 instance named **server-one** with the default Amazon Linux 2 AMI.

<Frame>
  ![The image shows the AWS EC2 Management Console interface for launching an instance. It includes options for naming the instance, selecting an Amazon Machine Image (AMI), and configuring instance details like type and storage.](https://kodekloud.com/kk-media/image/upload/v1752863325/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-launch-instance.jpg)
</Frame>

On the **Networking** page, choose your VPC. AWS automatically creates a default Security Group allowing inbound SSH (TCP 22) from `0.0.0.0/0`. You can restrict this later.

<Frame>
  ![The image shows the AWS EC2 Management Console interface, where a user is configuring settings for launching an EC2 instance, including key pair, network settings, and instance details.](https://kodekloud.com/kk-media/image/upload/v1752863326/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-instance-setup.jpg)
</Frame>

Review your settings and click **Launch**.

<Frame>
  ![The image shows an AWS EC2 instance launch configuration screen, detailing security group settings, storage configuration, and a summary of the instance details. The "Launch instance" button is highlighted at the bottom.](https://kodekloud.com/kk-media/image/upload/v1752863327/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-instance-launch-configuration.jpg)
</Frame>

## Verifying Initial Connectivity

Once **server-one** is in the **running** state, select it and open the **Security** tab. You should see:

* Inbound: SSH (TCP 22) from `0.0.0.0/0`
* Outbound: All traffic to `0.0.0.0/0`

<Frame>
  ![The image shows an AWS EC2 Management Console with two instances listed, both in the "Running" state, and details of one instance, including security group rules.](https://kodekloud.com/kk-media/image/upload/v1752863329/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-instances-running.jpg)
</Frame>

Connect via SSH to confirm:

```bash  theme={null}
ssh -i main.pem ec2-user@<Public-IP>
```

If you see the EC2 prompt, SSH is working.

## Blocking All Inbound Traffic

To illustrate rule enforcement, remove SSH access:

1. Go to **Security Groups** → select the default group.
2. Click **Edit inbound rules**.
3. Delete the SSH (22) rule and **Save**.

<Frame>
  ![The image shows the AWS EC2 Management Console, specifically the "Edit inbound rules" section for a security group, with an SSH rule allowing traffic from any IP address.](https://kodekloud.com/kk-media/image/upload/v1752863330/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-inbound-rules.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  By removing all inbound rules, you will lose SSH access to your instance. Be prepared to re-attach a group that allows SSH.
</Callout>

Now SSH attempts will time out:

```bash  theme={null}
ssh -i main.pem ec2-user@<Public-IP>
# (connection times out)
```

## Creating a Web Server Security Group

Next, create **web-server-sg** in the same VPC (Description: “Security group for web applications”):

* Inbound:\
  • SSH (TCP 22) from `0.0.0.0/0`
* Outbound: All traffic to `0.0.0.0/0`

<Frame>
  ![The image shows an AWS EC2 Management Console screen displaying details of a security group named "launch-wizard-20," with no inbound rules and one outbound rule.](https://kodekloud.com/kk-media/image/upload/v1752863331/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-security-group.jpg)
</Frame>

<Frame>
  ![The image shows an AWS EC2 security group configuration screen with inbound and outbound rules. The inbound rule allows SSH traffic from any IP, and the outbound rule allows all traffic to any destination.](https://kodekloud.com/kk-media/image/upload/v1752863332/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-security-group-configuration.jpg)
</Frame>

## Attaching the Security Group

Attach **web-server-sg** to **server-one**:

1. Select the instance.
2. **Actions → Security → Change security groups**.
3. Remove the old group and add **web-server-sg**.
4. Save.

<Frame>
  ![The image shows an AWS EC2 Management Console screen displaying details of a security group named "webserver-sg," including its inbound rules for SSH access.](https://kodekloud.com/kk-media/image/upload/v1752863333/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-webserver-sg.jpg)
</Frame>

<Frame>
  ![The image shows an AWS Management Console screen for changing security groups of an EC2 instance, displaying instance details and associated security groups.](https://kodekloud.com/kk-media/image/upload/v1752863334/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-management-console-ec2-security-groups.jpg)
</Frame>

Now SSH will succeed again.

## Installing and Testing Nginx

SSH into **server-one** and run:

```bash  theme={null}
sudo yum install nginx -y
sudo systemctl start nginx
```

Verify locally:

```bash  theme={null}
curl localhost
```

You should see the Nginx welcome page HTML.

## Allowing HTTP and HTTPS Access

By default, HTTP (80) and HTTPS (443) are blocked. Update **web-server-sg**:

1. Edit inbound rules.
2. Add:\
   • HTTP (TCP 80) from `0.0.0.0/0`\
   • HTTPS (TCP 443) from `0.0.0.0/0`
3. Save.

<Frame>
  ![The image shows an AWS EC2 security group settings page where inbound rules for SSH, HTTP, and HTTPS are being edited. Each rule specifies the protocol, port range, and source IP address.](https://kodekloud.com/kk-media/image/upload/v1752863335/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-security-group-inbound-rules.jpg)
</Frame>

Visiting the instance’s public IP in a browser now displays the Nginx welcome page.

## Demonstrating Stateful Behavior

Security Groups are stateful: return traffic is automatically allowed, even if outbound rules are removed.

<Frame>
  ![The image shows the AWS EC2 Management Console, specifically the "Edit outbound rules" section for a security group, with settings for allowing all traffic to a custom destination.](https://kodekloud.com/kk-media/image/upload/v1752863336/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-outbound-rules.jpg)
</Frame>

1. Remove all outbound rules.
2. Refresh the Nginx page in your browser—it still loads.
3. From the instance, try an outbound ping:

```bash  theme={null}
ping 8.8.8.8
# 100% packet loss
```

4. Re-add “All traffic” outbound rule and retry:

```bash  theme={null}
ping 8.8.8.8
64 bytes from 8.8.8.8: icmp_seq=1 ttl=53 time=1.58 ms
```

<Frame>
  ![The image shows an AWS EC2 Management Console screen displaying the details of a security group named "webserver-sg," including its inbound rules for SSH, HTTP, and HTTPS protocols.](https://kodekloud.com/kk-media/image/upload/v1752863337/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-security-group-webserver-sg.jpg)
</Frame>

## Splitting Rules into Multiple Security Groups

For modularity, create two groups:

* **allow-ssh-sg**\
  • Inbound: SSH (TCP 22) from `0.0.0.0/0`
* **allow-http-sg**\
  • Inbound: HTTP (TCP 80) from `0.0.0.0/0`

<Frame>
  ![The image shows the AWS Management Console interface for creating a security group, with fields for entering the security group name, description, and VPC, along with sections for inbound and outbound rules.](https://kodekloud.com/kk-media/image/upload/v1752863338/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-management-console-security-group-creation.jpg)
</Frame>

Detach **web-server-sg** and attach both **allow-ssh-sg** and **allow-http-sg** to **server-one**. You now have combined SSH + HTTP access.

<Frame>
  ![The image shows an AWS EC2 Management Console with details of running instances, including security settings for a specific instance. It displays security group rules for HTTP and SSH access.](https://kodekloud.com/kk-media/image/upload/v1752863339/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-security-settings.jpg)
</Frame>

## Reusing Security Groups Across Instances

Apply **allow-ssh-sg** and **allow-http-sg** to **server-two** to grant identical access controls.

<Frame>
  ![The image shows an AWS EC2 Management Console with details of two running instances, both of type t2.micro, including their instance IDs, public IP addresses, and status checks.](https://kodekloud.com/kk-media/image/upload/v1752863340/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-t2-micro.jpg)
</Frame>

## Referencing Security Groups as Rule Sources

For database connectivity, create **db-sg**:

* Inbound: PostgreSQL (TCP 5432)\
  • Source: **allow-http-sg**

This ensures any instance with **allow-http-sg** can connect on port 5432.

<Frame>
  ![The image shows an AWS EC2 Management Console screen with security group settings, including inbound and outbound rules for network traffic. The inbound rule specifies a custom TCP protocol on port 5432, and the outbound rule allows all traffic.](https://kodekloud.com/kk-media/image/upload/v1752863342/notes-assets/images/AWS-Networking-Fundamentals-Security-Groups-Demo/aws-ec2-management-console-security-groups.jpg)
</Frame>

By referencing another group, new web servers automatically gain DB access as soon as they attach **allow-http-sg**.

Subnet-level filtering with NACLs provides an additional control layer for stateless, rule-based traffic filtering.

## Summary of Security Groups

| Security Group | Description                      | Inbound Rules                            | Outbound Rules |
| -------------- | -------------------------------- | ---------------------------------------- | -------------- |
| web-server-sg  | Web application servers          | SSH (22), HTTP (80), HTTPS (443)         | All traffic    |
| allow-ssh-sg   | Modular SSH access               | SSH (22)                                 | All traffic    |
| allow-http-sg  | Modular HTTP access              | HTTP (80)                                | All traffic    |
| db-sg          | Database access from web servers | PostgreSQL (5432) from **allow-http-sg** | All traffic    |

## Links and References

* [AWS Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
* [AWS Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
* [Amazon EC2 Documentation](https://docs.aws.amazon.com/ec2/)
* [Nginx Official Site](https://nginx.org/)