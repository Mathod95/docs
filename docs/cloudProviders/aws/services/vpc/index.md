---
title: VPC
status: draft
sources: 
  - https://learn.kodekloud.com/user/courses/aws-networking-fundamentals
  - https://notes.kodekloud.com/docs/AWS-Networking-Fundamentals/Introduction/Course-Introduction/page
---

## Course Introduction

> This course covers essential AWS networking concepts through hands-on labs and real-world scenarios.

Step into the foundational world of cloud networking with our "AWS Networking Fundamentals" course. Designed for IT professionals and network enthusiasts who are just beginning their cloud journey, this course offers a thorough grounding in essential AWS networking concepts. Through clear, engaging lessons and practical demos, you'll gain the basic knowledge and confidence needed to design, implement, and manage AWS networking solutions effectively. Whether you're aiming to expand your skills or starting from scratch, this course is your gateway to mastering AWS networking.

**Core Networking Services:**

Learn how to create and configure Custom and Default VPCs with practical demos. Delve into subnets, routing, and route tables. Explore Internet Gateways and NAT Gateways, and differentiate between private/public subnets. Understand DNS within VPC and integrate Elastic IPs, Security Groups, and NACLs with hands-on demos. Gain expertise in Load Balancers and Route 53 DNS services.

**Transit Networks:**

Understand the setup of Virtual Private Networks (VPN) and Direct Connect for dedicated connections. Learn VPC Peering with practical demos and connect multiple VPCs both in-region and cross-region in a comprehensive lab. Centralize and simplify network architecture using Transit Gateway and securely connect to AWS services via PrivateLink.

**Edge Networks:**

Get introduced to AWS's Content Delivery Network, CloudFront, and extend its capabilities with CloudFront Functions and Lambda@Edge. Improve application availability and performance with Global Accelerator. Participate in labs to set up a global website using S3 and CloudFront.
Join us in this course to gain the knowledge and confidence in the fundamentals of AWS Networking.

---

## What You’ll Learn

This module covers the following core topics:

| Topic             | Key Concepts                                         | Hands-On Demonstrations                         |
| ----------------- | ---------------------------------------------------- | ----------------------------------------------- |
| VPC Fundamentals  | Default vs. Custom VPC                               | Create VPCs, configure CIDR blocks              |
| Subnets           | Public vs. Private Subnets                           | Launch EC2 instances in each subnet type        |
| Routing           | Route Tables, Route Propagation                      | Define custom routes, inspect routing behavior  |
| Gateways          | Internet Gateway, NAT Gateway                        | Attach IGWs, configure NAT Gateways for subnets |
| Elastic IPs       | Allocation, Association                              | Allocate EIPs, remap addresses                  |
| Security Controls | Security Groups (stateful), Network ACLs (stateless) | Compare SG vs. NACL rules in action             |
| VPC Peering       | Peering Architectures                                | Establish peering, test cross-VPC connectivity  |

---

## Course Outcome

By the end of this course, you will have:

* Mastered VPC design and configuration
* Built secure network architectures
* Connected multiple VPCs using peering
* Gained confidence to implement AWS networking in production

Let’s get started!

---

## Fundamentals
- [ ] VPC Overview
    - [ ] Custom VPC Demo
    - [ ] Default VPC Demo
    - [ ] DNS VPC
        - [ ] DNS VPC Demo
- [ ] Subnets
    - [ ] Subnets Demo
- [ ] Routing in VPC
    - [ ] Route Table Demo
- [ ] Internet Gateways VPC
    - [ ] Internet Gateway Demo
- [ ] NAT Gateways VPC
    - [ ] NAT Gateways VPC Demo
- [ ] Public vs Private Subnets

- [ ] Elastic IP
    - [ ] Elastic IP Demo
- [ ] Security Groups NACLs
    - [ ] Security Groups Demo
    - [ ] NACLs Demo
- [ ] Load Balancers
    - [ ] Load Balancers Demo
- [ ] Route 53
    - [ ] Route 53 Demo

## Transit Networks
- [ ] VPN
- [ ] Direct Connect
- [ ] VPC Peering
    - [ ] VPC Peering Demo
- [ ] Transit Gateway
- [ ] Privatelink

## Edge Networks
- [ ] CloudFront
    - [ ] CloudFront Demo
- [ ] Cloudfront and LambdaEdge
- [ ] Global Accelerator

---

!!! abstract ""

    ## Links and References

    * [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
    * [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/)
    * [AWS Networking Best Practices](https://aws.amazon.com/architecture/networking/)