---
title: "Deploying Super Mario on Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@awsanuragkadu/deploying-super-mario-on-kubernetes-4fbe16f84e91"
author:
  - "[[Anurag Kadu]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*dO6wF59MVF3RWbwq)

`Hey folks, remember the thrill of 90's gaming? Let's step back in time and relive those exciting moments! With the game deployed on Kubernetes, it's time to dive into the nostalgic world of Mario. Grab your controllers, it's game time!`

Super Mario is a classic game loved by many. In this guide, we’ll explore how to deploy a Super Mario game on Amazon’s Elastic Kubernetes Service (EKS). Utilizing Kubernetes, we can orchestrate the game’s deployment on AWS EKS, allowing for scalability, reliability, and easy management.

1. An Ubuntu Instance
2. IAM role
3. Terraform should be installed on instance
4. AWS CLI and KUBECTL on Instance

## LET’S DEPLOY

## STEP 1: Launch Ubuntu instance

1. Sign in to AWS Console: Log in to your AWS Management Console.
2. Navigate to EC2 Dashboard: Go to the EC2 Dashboard by selecting “Services” in the top menu and then choosing “EC2” under the Compute section.
3. Launch Instance: Click on the “Launch Instance” button to start the instance creation process.
4. Choose an Amazon Machine Image (AMI): Select an appropriate AMI for your instance. For example, you can choose Ubuntu image.
5. Choose an Instance Type: In the “Choose Instance Type” step, select `t2.micro` as your instance type. Proceed by clicking "Next: Configure Instance Details."
6. Configure Instance Details:
- For “Number of Instances,” set it to 1 (unless you need multiple instances).
- Configure additional settings like network, subnets, IAM role, etc., if necessary.
- For “Storage,” click “Add New Volume” and set the size to 8GB (or modify the existing storage to 8GB).
- Click “Next: Add Tags” when you’re done.

7\. Add Tags (Optional): Add any desired tags to your instance. This step is optional, but it helps in organizing instances.

8\. Configure Security Group:

- Choose an existing security group or create a new one.
- Ensure the security group has the necessary inbound/outbound rules to allow access as required.

9\. Review and Launch: Review the configuration details. Ensure everything is set as desired.

10\. Select Key Pair:

- Select “Choose an existing key pair” and choose the key pair from the dropdown.
- Acknowledge that you have access to the selected private key file.
- Click “Launch Instances” to create the instance.

11\. Access the EC2 Instance: Once the instance is launched, you can access it using the key pair and the instance’s public IP or DNS.

Ensure you have necessary permissions and follow best practices while configuring security groups and key pairs to maintain security for your EC2 instance.

## STEP 2: Create IAM role

Search for IAM in the search bar of AWS and click on roles.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*YgettlbhpdjmIHio)

Click on Create Role

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*sykhALZp7vA3RwQP)

Select entity type as AWS service

Use case as EC2 and click on Next.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*tIgzX_GJyo338FyW)

For permission policy select Administrator Access (Just for learning purpose), click Next.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Cl3phknQdWRkz-5U)

Provide a Name for Role and click on Create role.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*8is0uvxzQTFjLB8p)

Role is created.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*SEglpnhK0PC9-xok)

Now Attach this role to Ec2 instance that we created earlier, so we can provision cluster from that instance.

Go to EC2 Dashboard and select the instance.

Click on Actions → Security → Modify IAM role.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Rri1YGqUVjAYAbhq)

Select the Role that created earlier and click on Update IAM role.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*RNEWZ6bO3pm7Aa52)

Connect the instance to Mobaxtreme or Putty

## STEP 3: Cluster provision

1. Now clone this Repo.  
	git clone [https://github.com/awsanuragkadu/k8s-mario.git](https://github.com/awsanuragkadu/k8s-mario.git)
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*bwqflfYRE3CxEK0c2BwtHw.png)

2\. change directory  
cd k8s-mario

3\. Provide the executable permission to [script.sh](http://script.sh/) file, and run it.  
sudo chmod +x script.sh  
./script.sh

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*61JRGoLffjKxfJi3)

This script will install `Terraform, AWS cli, Kubectl, Docker.`

4\. Check versions

```c
docker — — version
aws — —  version
kubectl version — client
terraform — version
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*UoY0O8i30tGqjhkw)

5\. Now change directory into the EKS-TF

6\. Run Terraform init  
`NOTE: Don’t forgot to change the s3 bucket name in the backend.tf file`

```c
cd EKS-TF
terraform init
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*9p6h1JnDK0UcTXor)

7\. Now run terraform validate and terraform plan

```c
terraform validate
terraform plan
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*5Aqi2nl8VbFLPBSW)

8\. Now Run terraform apply to provision cluster.

```c
terraform apply --auto-approve
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*WWkwaNV_pTvk2PJw)

Completed in 10mins

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Wn_CCx1uGkI9PLOL)

9\. Update the Kubernetes configuration

Make sure change your desired region

```c
aws eks update-kubeconfig --name EKS_CLOUD --region ap-south-1
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*yPHlAnMdwW-IQ9Tf)

10\. Now change directory back to k8s-mario

```c
cd ..
```

11\. Let’s apply the deployment and service

Deployment

```c
kubectl apply -f deployment.yaml
#to check the deployment 
kubectl get all
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*RrcuvRRcNoMA6R5W)

12\. Now let’s apply the service

Service

```c
kubectl apply -f service.yaml
kubectl get all
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*1VRAg-v7iHb_HrXe)

13\. Now let’s describe the service and copy the LoadBalancer Ingress

```c
kubectl describe service mario-service
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*FLaRespSqKnxFksd)

Paste the ingress link in a browser and you will see the Mario game.

Let’s Go back to 1985 and play the game like children.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*eCDOHOJC5YIyK9cC)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*DBzAZhX_wJYDXN2u)

## STEP 4: Cluster Destruction:

1. Let’s remove the service and deployment first
```c
kubectl get all
kubectl delete service mario-service
kubectl delete deployment mario-deployment
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*UsJ0E8xLkLzrUIALd18isw.png)

2\. Let’s Destroy the cluster

```c
terraform destroy --auto-approve
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*YcxiKajeV1IRP8Ew)

After 10mins Resources that are provisioned will be removed.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*svhNYc2g00SNYifS6eyvRQ.png)

Thank you for joining this nostalgic journey to the 90s! We hope you enjoyed rekindling your love for gaming with the deployment of the iconic Mario game on Kubernetes. Embracing the past while exploring new technologies is a true testament to the timeless allure of classic games. Until next time, keep gaming and reliving those fantastic memories! 👾🎮.

## More from Anurag Kadu

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--4fbe16f84e91---------------------------------------)