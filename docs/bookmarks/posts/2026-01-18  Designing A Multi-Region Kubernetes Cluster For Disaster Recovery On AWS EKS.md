---
title: "Designing A Multi-Region Kubernetes Cluster For Disaster Recovery On AWS EKS"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://rahulbhatia1998.medium.com/designing-a-multi-region-kubernetes-cluster-for-disaster-recovery-on-aws-eks-0a0a98ad5854"
author:
  - "[[Rahulbhatia1998]]"
---
<!-- more -->

[Sitemap](https://rahulbhatia1998.medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*vbNbInAFIeQZnQhvREgoLw.png)

Multi-Region Disaster Recovery EKS Cluster

**Objective**: Design and implement a robust, multi-region disaster recovery (DR) solution for a critical application on Kubernetes, ensuring minimal downtime and data consistency during region-wide outages.

1. **Traffic Management and Failover**:

To make sure continuous traffic is coming into your environment, and there is no disruption for client side.  
Route 53 can be combined with Global accelerator can be used for better traffic management.  
  
**AWS Route 53**:  
DNS based Service on AWS.  
  
**AWS Global Accelerator:**

- **Accelerated and Optimized Global Network:  
	**Global Accelerator uses the AWS global network infrastructure to optimise the path for traffic from users to your applications, improving performance and reliability by reducing latency and providing higher availability.
- **Anycast IP Addresses:  
	**Global Accelerator allocates static anycast IP addresses that act as entry points to your applications hosted in one or multiple AWS regions. These IP addresses remain fixed and automatically route traffic to the closest healthy endpoints.

**Combining Route 53 with Global Accelerator:**

- **Enhanced Global Traffic Management:  
	**Route 53 can be used in combination with Global Accelerator to perform DNS-based traffic management.  
	Route 53 can direct traffic to Global Accelerator’s anycast IP addresses, which in turn route traffic to the closest healthy endpoints in multiple regions.
- **Traffic Steering and Failover:  
	**Route 53 can steer traffic using its routing policies, considering various factors such as latency, health checks, and weighted distribution to the Global Accelerator endpoints.  
	In the event of regional outages or endpoint unavailability, Route 53 can perform failover to direct traffic away from the affected regions or endpoints.
- **Performance and Scalability:  
	**Global Accelerator improves the performance of your applications by intelligently routing traffic through the AWS global network backbone, reducing the effect of internet congestion and optimising the path to your applications hosted in different regions.

The exact Routing policy will be **Failover Routing in Route 53** which we can use for our use-case.

**Why Failover Routing?**

Failover routing lets you route traffic to a resource when the resource is healthy or to a different resource when the first resource is unhealthy. The primary and secondary records can route traffic to anything from an Amazon S3 bucket that is configured as a website to a complex tree of records. For more information, see [Active-passive failover](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover-types.html#dns-failover-types-active-passive).

The Failover routing policy is particularly suitable for scenarios where you have primary and secondary resources in different regions and want to ensure high availability. It enables Route 53 to monitor the health of the primary resources and automatically fail over to the secondary resources if necessary.

When configuring the Failover routing policy, you’ll designate one resource set as the primary and another as the secondary, setting appropriate health checks to determine when a failover should occur.

The failover routing can have 2 entries for 2 anycast IP address from Global accelerator for ALB’s which would reverse proxy it to their respective Kubernetes cluster.

**The above solution is beneficial for client, as they will not face any disruption if as per any cutover happens between the regions, the client’s local dns cache will change once the call to domain is made,**  
**One catch can be the TTL for the subdomain, if the TTL is high the client might be redirecting to the old Load balancer.**  
**This can be made to 30 seconds.**

**2\. Application & Data Backend Setup**:

For the above solution, we can use a stateless application like Postgres pod on a Kubernetes cluster.  
**Design considerations**:

I have used EFS over EBS because of the ready availability of the resource for the 2nd region as and when disaster happens.  
For ebs you will have to restore from snapshot and some amount of downtime is required, whereas the RTO and RPO is way less for EFS.

**Steps:**

- **Deploy PostgreSQL on Kubernetes:  
	**Use a Kubernetes manifest or Helm chart to deploy PostgreSQL. Ensure you define the persistent volume claim (PVC) for storing PostgreSQL data.
- **Configure AWS EFS Volumes:  
	**Create an AWS EFS volume in Region A and attach it to the Kubernetes cluster.  
	Define the StorageClass in Kubernetes that references AWS EFS with the appropriate settings (e.g., volume type, size, etc.).
- **Kubernetes Cluster Setup (Region B):  
	**Set up another Kubernetes cluster in Region B if not already available.
- **Configure EFS Volumes:  
	**Create an AWS EFS volume in Region B and attach it to the Kubernetes cluster.  
	Define the StorageClass in Kubernetes that references AWS EFS with the appropriate settings (e.g., volume type, size, etc.).  
	Attach the replicated EFS volume to the Kubernetes cluster in Region B using the appropriate StorageClass and PVC.
- **Cross region Replication:**  
	For Cross region Replication, we can use a Service in AWS called AWS DataSync,  
	AWS DataSync is a service specifically designed for data transfer and synchronization between on-premises systems, AWS services, and AWS regions. You can use DataSync to replicate data between EFS file systems in different regions.
- **Configure PostgreSQL Pod in Region B:  
	**Update your PostgreSQL deployment to use the PVC associated with the EFS volume in Region B.

For better **Robustness** and **Repeatability**, you can use terraform or cloud formation, to set up infrastructure as fast as possible.

**3\. Disaster Recovery Drills**:

We can remove the ELB in Region A, to replicate a Disaster, now the Route 53 will come in action with the failover routing policy when it fails the health check and direct the traffic to the new load balancer placed in region B, once it has done that, the data present in EFS in region 2 will become active and pod will be serving traffic to clients. Route 53 will direct traffic onto the new load balancer which reverse proxies the data to the Kubernetes Postgres pod in region B.

Once **Region A** is “restored”:

AWS Data Sync needs to be configured since it’s uni-directional to transfer any incremental data between region B to region A. Once it’s done with that, the load balancer is back up and route 53 starts serving traffic to the old load balancer.

4\. **Monitoring and Alerting:**

- **Application Performance Monitoring:  
	**Use tools like Prometheus with Grafana or AWS CloudWatch to monitor application performance metrics such as response times, resource utilization, and latency within each Kubernetes cluster.  
	Implement custom metrics specific to your application’s performance and behaviour.
- **Data Replication Monitoring:  
	**Use AWS CloudWatch Metrics or DataSync monitoring capabilities to track replication status, latency, and throughput.  
	Implement custom checks or scripts to validate data consistency between databases or file systems in different regions.
- **CloudWatch Alarms:  
	**Configure alerts to trigger any inconsistencies detected between the data in **Region A** and **Region B**.  
	Set up alarms for replication failures, delays, or errors.  
	Establish thresholds for performance degradation or outages and trigger alerts accordingly.”

And hence a Multi-Region Disaster Recovery solution is created.

## More from Rahulbhatia1998

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--0a0a98ad5854---------------------------------------)