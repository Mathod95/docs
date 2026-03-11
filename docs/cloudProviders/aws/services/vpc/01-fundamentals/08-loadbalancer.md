---
title: Load Balancers
status: draft
sources:
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Core-Networking-Services/Load-Balancers/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals/module/406e4440-01a6-45f6-ab45-e14485d333c3/lesson/3ddb4c64-67ec-4e5a-bb59-e502555c91a8
---

> This lesson explores AWS Elastic Load Balancers and their configuration for high availability, auto-scaling, and fault tolerance in cloud environments.

In this lesson, you'll explore AWS Elastic Load Balancers (ELB) and learn how to configure them for high availability, auto-scaling, and fault tolerance in your cloud environments.

***

## Why Load Balancers?

Imagine hosting your web application on a single EC2 instance at public IP `1.1.1.1`. If that instance fails, your site goes offline. To add redundancy, you deploy instances across multiple Availability Zones:

* EC2 A: 1.1.1.1
* EC2 B: 2.2.2.2
* EC2 C: 3.3.3.3

Which IP address should your users access? Manually switching between IPs is cumbersome and exposes internal details. A load balancer provides a single, stable endpoint that intelligently distributes requests to healthy backends.

<Frame>
  ![The image illustrates an Elastic Load Balancer (ELB) in AWS, showing a user querying which IP to send data to, with three availability zones each having a different IP address.](https://kodekloud.com/kk-media/image/upload/v1752863260/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/elastic-load-balancer-aws-diagram.jpg)
</Frame>

Once deployed, the ELB abstracts individual instance IPs and automatically routes traffic:

<Frame>
  ![The image illustrates an Elastic Load Balancer (ELB) setup in AWS Cloud, showing how traffic is distributed from a single IP address to multiple availability zones with different IPs.](https://kodekloud.com/kk-media/image/upload/v1752863261/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/aws-elb-traffic-distribution-diagram.jpg)
</Frame>

***

## Types of AWS Load Balancers

AWS provides three managed load-balancing options to suit different workloads:

| Load Balancer Type              | OSI Layer | Protocols               | SSL Termination       | Use Case                         |
| ------------------------------- | --------- | ----------------------- | --------------------- | -------------------------------- |
| Classic Load Balancer (CLB)     | 4 & 7     | HTTP, HTTPS, TCP, SSL   | Yes (one certificate) | Legacy workloads                 |
| Application Load Balancer (ALB) | 7         | HTTP, HTTPS, WebSockets | Yes (multiple)        | URL/path-based routing           |
| Network Load Balancer (NLB)     | 4         | TCP, UDP                | No                    | Ultra-low latency transport load |

### 1. Classic Load Balancer (CLB)

The original AWS load balancer supports HTTP, HTTPS, TCP, and SSL but lacks modern features like multiple certificates and advanced routing.

<Callout icon="triangle-alert" color="#FF6B6B">
  Classic Load Balancer is considered legacy. AWS recommends using Application Load Balancer (ALB) or Network Load Balancer (NLB) for new deployments.
</Callout>

<Frame>
  ![The image is an illustration of the Classic Load Balancer (CLB) by AWS, noting it was the first load balancer introduced by AWS and is not recommended for use. It includes a simple diagram showing the CLB distributing traffic to two applications.](https://kodekloud.com/kk-media/image/upload/v1752863262/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/aws-classic-load-balancer-diagram.jpg)
</Frame>

### 2. Application Load Balancer (ALB)

ALBs operate at the application layer (Layer 7) and excel at HTTP, HTTPS, and WebSocket traffic. They provide content-based routing and host/path-based rules:

* URL path and host header conditions
* HTTP methods, headers, query strings, source IP
* HTTP redirects and custom responses
* Application-level health checks

<Frame>
  ![The image is an infographic about Application Load Balancer (ALB), highlighting its support for HTTP/HTTPS/WebSockets, functioning at the application layer (layer 7), and request forwarding based on URL path conditions, host domain, and HTTP fields.](https://kodekloud.com/kk-media/image/upload/v1752863263/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/alb-infographic-http-https-websockets.jpg)
</Frame>

<Frame>
  ![The image is an infographic about Application Load Balancer (ALB), highlighting its support for HTTP/HTTPS/WebSockets, functioning at the application layer, request forwarding based on specific conditions, and performing application-specific health checks.](https://kodekloud.com/kk-media/image/upload/v1752863264/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/alb-infographic-http-https-websockets-2.jpg)
</Frame>

#### ALB Traffic Flow and SSL Termination

Application Load Balancers terminate SSL/TLS connections, decrypting traffic at the edge. Your SSL certificates reside on the ALB, and you can choose to forward decrypted traffic to backends over HTTP or re-encrypt using HTTPS.

<Callout icon="lightbulb" color="#1CB2FE">
  Ensure your backend instances are configured to handle re-encrypted HTTPS if you require end-to-end encryption.
</Callout>

<Frame>
  ![The image illustrates the flow of data through an Application Load Balancer (ALB), showing SSL/TLS termination at the ALB and the transition from encrypted to unencrypted data.](https://kodekloud.com/kk-media/image/upload/v1752863265/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/alb-data-flow-ssl-termination.jpg)
</Frame>

### 3. Network Load Balancer (NLB)

Operating at the transport layer (Layer 4), NLBs handle millions of requests per second with ultra-low latency. They forward TCP/UDP connections directly to targets without TLS termination.

* High throughput and low latency
* Static IP support and Elastic IP attachment
* Basic transport-level health checks (TCP)

<Frame>
  ![The image is an informational graphic about Network Load Balancers (NLB), highlighting features such as load balancing traffic based on TCP/UDP, suitability for non-HTTP/HTTPS applications, speed, basic health checks, and TCP connection forwarding.](https://kodekloud.com/kk-media/image/upload/v1752863266/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/network-load-balancers-features-graphic.jpg)
</Frame>

***

## ELB Architecture in a VPC

When you create an ELB, AWS launches a load-balancer node in each selected subnet (one per AZ). Clients resolve the ELB’s DNS name, and AWS distributes traffic across all nodes, which in turn forward requests to registered targets.

<Frame>
  ![The image illustrates the architecture of Elastic Load Balancers within a Virtual Private Cloud (VPC), showing public and private subnets across two availability zones. It includes a DNS record creation for the ELB and load balancer nodes in each public subnet.](https://kodekloud.com/kk-media/image/upload/v1752863267/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/elastic-load-balancer-vpc-architecture.jpg)
</Frame>

***

## Cross-Zone Load Balancing

By default, each ELB node only routes traffic to targets in its own Availability Zone, which can cause uneven distribution if instance counts differ. Enabling **cross-zone load balancing** ensures each node spreads requests across all zones evenly.

<Callout icon="lightbulb" color="#1CB2FE">
  Cross-zone load balancing can improve utilization but may incur additional inter-AZ data transfer charges.
</Callout>

<Frame>
  ![The image illustrates a cross-zone load balancing setup within a Virtual Private Cloud (VPC), showing traffic distribution between two availability zones, each with load balancing nodes and instances.](https://kodekloud.com/kk-media/image/upload/v1752863268/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/cross-zone-load-balancing-vpc-setup.jpg)
</Frame>

***

## Public vs. Private Load Balancers

When deploying an ELB, you specify subnets:

* **Public Load Balancer**: Internet-facing on public subnets
* **Private Load Balancer**: Internal-only on private subnets

<Frame>
  ![The image compares public and private load balancers, highlighting that public load balancers are deployed on public subnets for internet access, while private load balancers are deployed on private subnets for access within an organization's AWS network.](https://kodekloud.com/kk-media/image/upload/v1752863269/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/public-private-load-balancers-comparison.jpg)
</Frame>

<Frame>
  ![The image illustrates the difference between private and public subnets in AWS Cloud, showing that a private load balancer is not accessible from the internet, while a public subnet is.](https://kodekloud.com/kk-media/image/upload/v1752863270/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/aws-private-public-subnets-difference.jpg)
</Frame>

***

## Example: Multi-Tier Application

Consider a two-tier application in a VPC across two Availability Zones:

1. **API Layer**
   * EC2 instances hosting your public API
   * Internet-facing **public ALB** distributes incoming user traffic

2. **Database Layer**
   * EC2 instances running database or business logic
   * Internal **private ALB** restricts access to only the API servers

This setup exposes your frontend securely while keeping your backend protected.

<Frame>
  ![The image illustrates an ELB (Elastic Load Balancer) architecture within a Virtual Private Cloud (VPC), showing how load balancers in public subnets forward requests to resources in private subnets.](https://kodekloud.com/kk-media/image/upload/v1752863270/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/elb-architecture-vpc-load-balancer.jpg)
</Frame>

***

## Listeners and Target Groups

Listeners and target groups define how ELBs receive and route traffic:

* **Listeners**: Check for incoming connections on a specific protocol and port. ALB listeners support content-based rules (host, path, headers).
* **Target Groups**: Logical groups of endpoints (EC2 instances, IPs, ECS tasks, Lambda functions). Each listener rule forwards traffic to one or more target groups, with configurable health checks.

<Frame>
  ![The image illustrates a network architecture with listeners and target groups, showing how load balancers forward requests to resources like ECS and Lambda functions.](https://kodekloud.com/kk-media/image/upload/v1752863271/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/network-architecture-load-balancers-ecs-lambda.jpg)
</Frame>

***

## Summary

* ELBs distribute traffic across multiple targets and AZs automatically.
* Supports EC2 instances, IP addresses, containers (ECS), and Lambda functions.
* **Classic (CLB)**: Legacy; limited features, one SSL cert.
* **Application (ALB)**: Layer 7 routing with advanced rules and TLS termination.
* **Network (NLB)**: Layer 4 transport load balancing with ultra-low latency.
* **Cross-zone load balancing** for even traffic distribution across AZs.
* **Listeners** parse connections; **target groups** manage backend health and routing.

<Frame>
  ![The image is a summary slide about Elastic Load Balancing (ELB), highlighting its traffic distribution capabilities, types, and a note on outdated CLBs.](https://kodekloud.com/kk-media/image/upload/v1752863272/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/elastic-load-balancing-summary-slide.jpg)
</Frame>

<Frame>
  ![The image is a summary slide comparing Application Load Balancers (ALBs) and Network Load Balancers (NLBs), highlighting their functions and differences in handling HTTP/HTTPS traffic.](https://kodekloud.com/kk-media/image/upload/v1752863273/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers/alb-nlb-comparison-summary-slide.jpg)
</Frame>

***

## References

* [AWS Elastic Load Balancing Documentation](https://docs.aws.amazon.com/elasticloadbalancing/)
* [AWS Networking Fundamentals](https://aws.amazon.com/elasticloadbalancing/)
* [Designing Highly Available Systems on AWS (Whitepaper)](https://docs.aws.amazon.com/whitepapers/latest/designing-high-availability-systems/)

--- 

- ELB auto-distributes incoming traffic accros multiple targets in multiple Availabitiliy Zones
- Distributes traffic to EC2 instances, IPs, and Lambda functions
- Three types of ELB: Classic, Application, Network
- CLBs are outdated and should be avoided
- ALB functions on application layer and forwards HTTP/HTTPS traffic
- NLB can forward non-HTTP/HTTPS traffic
- NLBs are faster than ALBs
- HTTP/HTTPS is always terminated on ALB and not NLB
- Cross-Zone Load Balancing equally distributes traffic across aall instances in all AZs
- A listener matches traffic based on rules and handles connection requests
- Target groups route requests to registered EC2 instances based on specified protocol and port

---

> This hands-on tutorial guides setting up an AWS Application Load Balancer to distribute HTTP requests across two EC2 web servers running Nginx.

In this hands-on tutorial, you’ll set up an AWS Application Load Balancer (ALB) to distribute HTTP requests across two EC2 web servers running Nginx, each in a different Availability Zone. By the end, you’ll have a resilient, internet-facing load balancer serving content from both servers.

## Prerequisites

<Callout icon="lightbulb" color="#1CB2FE">
  Make sure you already have:

  * Two t2.micro EC2 instances (**web-server-1**, **web-server-2**) with Nginx and distinct landing pages.
  * A VPC configured with an Internet Gateway.
  * Two public subnets in us-east-1a and us-east-1b.
</Callout>

| Resource       | Description           | Details                                                  |
| -------------- | --------------------- | -------------------------------------------------------- |
| EC2 Instances  | Web servers           | `web-server-1` (us-east-1a), `web-server-2` (us-east-1b) |
| VPC            | Virtual Private Cloud | Includes an Internet Gateway and public subnets          |
| Public Subnets | Hosts web servers     | 10.0.201.0/24 (AZ a), 10.0.202.0/24 (AZ b)               |

### EC2 Instances

Our EC2 console shows both instances running:

<Frame>
  ![The image shows an AWS EC2 Management Console with two running instances, "web-server1" and "web-server2," both of type t2.micro. The details of "web-server2" are displayed, including its instance ID, public IP address, and status checks.](https://kodekloud.com/kk-media/image/upload/v1752863240/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-ec2-management-console-instances.jpg)
</Frame>

Visiting **web-server-1** confirms Nginx is up:

<Frame>
  ![The image shows a web page with a message indicating that "server1" is running, confirming the successful installation of the Nginx web server. It includes links for online documentation and support.](https://kodekloud.com/kk-media/image/upload/v1752863242/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/nginx-server1-running-installation-confirmation.jpg)
</Frame>

And **web-server-2** is similarly healthy:

<Frame>
  ![The image shows an AWS EC2 Management Console with two running instances, "web-server1" and "web-server2," both of type t2.micro, with status checks passed and no alarms. Monitoring graphs for CPU utilization and network activity are displayed below.](https://kodekloud.com/kk-media/image/upload/v1752863243/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-ec2-management-console-instances-2.jpg)
</Frame>

### Network Layout

Your VPC’s public subnets:

<Frame>
  ![The image shows an AWS Management Console screen displaying the subnets section of a VPC dashboard, listing two subnets with their details such as VPC ID, IPv4 CIDR, and availability zones.](https://kodekloud.com/kk-media/image/upload/v1752863244/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-vpc-subnets-dashboard.jpg)
</Frame>

* **web-us-east-1a**: 10.0.201.0/24
* **web-us-east-1b**: 10.0.202.0/24

These subnets host your web servers and route traffic through the Internet Gateway.

***

## Step 1: Create Dedicated Subnets for the Load Balancer

Add two new public subnets—one in each AZ—for the ALB:

1. In the VPC console, click **Create Subnet**.
2. Configure:
   * **LB-us-east-1a**: us-east-1a, 10.0.101.0/24
   * **LB-us-east-1b**: us-east-1b, 10.0.102.0/24

<Frame>
  ![The image shows a screenshot of the AWS Management Console, specifically the VPC (Virtual Private Cloud) setup page, where subnet settings are being configured. It includes fields for VPC ID, associated CIDRs, subnet name, availability zone, and IPv4 CIDR block.](https://kodekloud.com/kk-media/image/upload/v1752863245/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-vpc-setup-screenshot-subnet-settings.jpg)
</Frame>

After creation, verify you have four public subnets:

<Frame>
  ![The image shows the AWS Management Console displaying the VPC dashboard with a list of subnets. A notification at the top indicates that a new subnet has been successfully created.](https://kodekloud.com/kk-media/image/upload/v1752863247/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-vpc-dashboard-subnets.jpg)
</Frame>

***

## Step 2: Verify Public Subnet Configuration

<Callout icon="lightbulb" color="#1CB2FE">
  Confirm each new subnet’s route table includes a default route (`0.0.0.0/0`) to the Internet Gateway—this makes the ALB internet-facing.
</Callout>

Select **LB-us-east-1a** (and **LB-us-east-1b**) to inspect its Route Table:

<Frame>
  ![The image shows an AWS VPC Management Console displaying a list of subnets, with details of a selected subnet including its ID, state, and availability zone.](https://kodekloud.com/kk-media/image/upload/v1752863248/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-vpc-management-console-subnets-details.jpg)
</Frame>

***

## Step 3: Create the Application Load Balancer

1. In the EC2 console, go to **Load Balancers** → **Create Load Balancer** → **Application Load Balancer**.
2. Set:
   * **Name**: web-lb
   * **Scheme**: Internet-facing
   * **IP address type**: IPv4
   * **VPC**: demo
3. Select subnets **LB-us-east-1a** and **LB-us-east-1b**.

<Frame>
  ![The image shows a comparison of three types of AWS load balancers: Application Load Balancer, Network Load Balancer, and Gateway Load Balancer, each with a brief description and a "Create" button.](https://kodekloud.com/kk-media/image/upload/v1752863249/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-load-balancer-comparison-diagram.jpg)
</Frame>

Configure the ALB network mapping:

<Frame>
  ![The image shows a configuration page for creating an application load balancer in the AWS Management Console, with options for naming, scheme selection, IP address type, and network mapping.](https://kodekloud.com/kk-media/image/upload/v1752863250/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-application-load-balancer-configuration.jpg)
</Frame>

Attach a security group allowing HTTP (80) and HTTPS (443):

<Frame>
  ![The image shows a screenshot of the AWS Management Console, specifically the section for configuring security groups for a load balancer. It includes options to select or create security groups and displays a dropdown list of available groups.](https://kodekloud.com/kk-media/image/upload/v1752863251/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-security-groups-load-balancer.jpg)
</Frame>

***

## Step 4: Configure Listener and Target Group

### Listener

Add an HTTP listener on port 80:

<Frame>
  ![The image shows an AWS Management Console interface for configuring a load balancer, including settings for security groups and listener routing with HTTP protocol on port 80.](https://kodekloud.com/kk-media/image/upload/v1752863252/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-load-balancer-configuration.jpg)
</Frame>

### Target Group

1. Create a new target group:
   * **Target type**: Instances
   * **Name**: web-targets
   * **Protocol**: HTTP
   * **Port**: 80
   * **VPC**: demo
   * **Health check path**: `/`

<Frame>
  ![The image shows a screenshot of the AWS Management Console, specifically the section for creating a target group for a load balancer. It includes options for setting the target group name, protocol, port, VPC, and protocol version.](https://kodekloud.com/kk-media/image/upload/v1752863253/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-target-group-creation.jpg)
</Frame>

2. Register **web-server-1** and **web-server-2** on port 80:

<Frame>
  ![The image shows an AWS Management Console interface, specifically the section for creating a target group for load balancing, with two instances listed as targets.](https://kodekloud.com/kk-media/image/upload/v1752863255/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-target-group-load-balancing.jpg)
</Frame>

3. Back in the ALB wizard, set **web-targets** as the default action for the HTTP listener:

<Frame>
  ![The image shows an AWS Management Console interface for configuring listeners and routing for a load balancer, with options for HTTP and HTTPS protocols. It includes settings for ports, default actions, and listener tags.](https://kodekloud.com/kk-media/image/upload/v1752863256/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-load-balancer-listeners.jpg)
</Frame>

4. Review and create the ALB:

<Frame>
  ![The image shows an AWS Management Console screen for configuring a load balancer, displaying sections for basic configuration, security groups, network mapping, and listeners and routing.](https://kodekloud.com/kk-media/image/upload/v1752863257/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-management-console-load-balancer-config.jpg)
</Frame>

***

## Step 5: Test the Load Balancer

Wait until the ALB status is **active**, then copy its DNS name:

<Frame>
  ![The image shows an AWS EC2 Management Console displaying details of a load balancer named "web-lb," which is active and internet-facing, with information about its VPC, availability zones, and other settings.](https://kodekloud.com/kk-media/image/upload/v1752863258/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-ec2-load-balancer-web-lb.jpg)
</Frame>

From your terminal or browser:

```bash  theme={null}
curl http://<load-balancer-dns-name>
```

Refreshing the request should alternate responses between **server1** and **server2**, confirming traffic distribution.

***

## Best Practice: Secure Your Web Servers

<Callout icon="triangle-alert" color="#FF6B6B">
  Currently, both web servers have public IPs:

  <Frame>
    ![The image shows an AWS EC2 Management Console with a list of instances, some running and some terminated. The user is searching for instances with the state "running."](https://kodekloud.com/kk-media/image/upload/v1752863259/notes-assets/images/AWS-Networking-Fundamentals-Load-Balancers-Demo/aws-ec2-management-console-running-instances.jpg)
  </Frame>

  To harden your architecture:

  1. Move web servers into private subnets.
  2. Keep the ALB in public subnets.
  3. Configure the web servers’ security group to accept traffic only from the ALB’s security group.
</Callout>

This ensures all external requests pass through the ALB, improving security and isolation.

***

## Links and References

* [AWS Documentation: Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
* [Nginx Official Documentation](https://nginx.org/en/docs/)
* [AWS VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/)