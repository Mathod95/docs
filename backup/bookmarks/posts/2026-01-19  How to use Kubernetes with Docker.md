---
title: "How to use Kubernetes with Docker"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@muthanagavamsi/how-to-use-kubernetes-with-docker-89afb866c876"
author:
  - "[[Mutha Nagavamsi]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

There are only 8 things you need to install to use **Kubernetes cluster with Docker.**

For this setup I am using Ubuntu 20.04.06 LTS

Step 1: Install Docker. Save the following script as docker.sh

```c
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
newgrp docker
```

Step 2: Run Docker Script

```c
bash docker.sh
```

Step 3: Start docker.

```c
service docker start
```

Step 4: Download Kubectl. Save the following script as kubectl.sh

```c
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

Step 5: Run the script.

```c
bash kubectl.sh
```

Step 6: Download Kind. Save the following script as kind.sh

```c
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.27.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/
```

Step 7: Run kind cluster.

```c
kind create cluster
```

Step 8: Connect with Kubectl.

```c
kubectl get pods
```

I will try to put all these steps in a video and public once done. Hope you are running your Kubernetes with Docker with Kind.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*nzCO38pyKTeYN2Z-Ydh29A.png)

Kubernetes with Docker with Kind

## More from Mutha Nagavamsi

![125,000 Layoffs Later: DevOps Skills That Can Save Careers and Why](https://miro.medium.com/v2/resize:fit:679/format:webp/1*bWgWBs3452-HDSxDMCpNXA.png)

Jan 8

![Install Kubernetes on Windows 11 with Kind](https://miro.medium.com/v2/resize:fit:679/format:webp/319daec016b12da748373d51bd9d27c727580bba9947096fe89b8e2efb8e03a6)

Oct 21, 2023

![Setting Kubernetes Dashboard on Latest K8s 1.32 using Kind](https://miro.medium.com/v2/resize:fit:679/format:webp/1*LGiXcv2uSkJaSpLCyCA9KQ.png)

Feb 27, 2025

![Connection pooling in Kubernetes](https://miro.medium.com/v2/resize:fit:679/format:webp/1*SWHmysMNha2mhI5xJeZXDw.gif)

Jul 24, 2023

## Recommended from Medium

![Deploying WSO2 Identity Server on Kubernetes with Helm Chart: Part 1](https://miro.medium.com/v2/resize:fit:679/format:webp/1*Jl8fMjMucqb7ay-IIDVCRQ.png)[Ravindran Dharshan](https://medium.com/@ravindrandharshan?source=post_page---read_next_recirc--89afb866c876----0---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)## [Deploying WSO2 Identity Server on Kubernetes with Helm Chart: Part 1](https://medium.com/@ravindrandharshan/deploying-wso2-identity-server-on-kubernetes-with-helm-d49f8f6b9ebf?source=post_page---read_next_recirc--89afb866c876----0---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

### A practical guide to deploying WSO2 Identity Server on Kubernetes using Helm charts.

](https://medium.com/@ravindrandharshan/deploying-wso2-identity-server-on-kubernetes-with-helm-d49f8f6b9ebf?source=post_page---read_next_recirc--89afb866c876----0---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

Oct 3, 2025[203](https://medium.com/@ravindrandharshan/deploying-wso2-identity-server-on-kubernetes-with-helm-d49f8f6b9ebf?source=post_page---read_next_recirc--89afb866c876----0---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

![Exposing Applications with Kubernetes Services (NodePort, LoadBalancer, Ingress)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*XjrJ8gyKRnXb9kYMg5i6fg.png)[Engineer Palsu](https://medium.com/@engineerpalsu?source=post_page---read_next_recirc--89afb866c876----1---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)## [Exposing Applications with Kubernetes Services (NodePort, LoadBalancer, Ingress)](https://medium.com/@engineerpalsu/exposing-applications-with-kubernetes-services-nodeport-loadbalancer-ingress-b0f4cd500de3?source=post_page---read_next_recirc--89afb866c876----1---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

### Kubernetes Services are a fundamental concept in Kubernetes, enabling you to expose your applications running within pods to the network…

](https://medium.com/@engineerpalsu/exposing-applications-with-kubernetes-services-nodeport-loadbalancer-ingress-b0f4cd500de3?source=post_page---read_next_recirc--89afb866c876----1---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

Jan 1

![How to Optimize Docker Images for Faster Builds: A Practical Guide for Node.js Developers](https://miro.medium.com/v2/resize:fit:679/format:webp/1*r0pX8qXCMFjygVZUVkwR7A.png)## [How to Optimize Docker Images for Faster Builds: A Practical Guide for Node.js Developers](https://medium.com/aws-in-plain-english/how-to-optimize-docker-images-for-faster-builds-a-practical-guide-for-node-js-developers-cf5d31ec8e74?source=post_page---read_next_recirc--89afb866c876----0---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

### If you’ve ever sat there watching Docker build your image for the hundredth time, waiting for those familiar “RUN npm install” lines to…

](https://medium.com/aws-in-plain-english/how-to-optimize-docker-images-for-faster-builds-a-practical-guide-for-node-js-developers-cf5d31ec8e74?source=post_page---read_next_recirc--89afb866c876----0---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

Oct 13, 2025

![Day 2: Understanding Kubernetes Architecture](https://miro.medium.com/v2/resize:fit:679/format:webp/1*APHR0ckFXiMR1KxuIsJZ_Q.png)[Senthil](https://medium.com/@senthil262006?source=post_page---read_next_recirc--89afb866c876----1---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)## [Day 2: Understanding Kubernetes Architecture](https://medium.com/@senthil262006/day-2-understanding-kubernetes-architecture-f7609666e87b?source=post_page---read_next_recirc--89afb866c876----1---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

### — Inside the Cloud-Native Engine

](https://medium.com/@senthil262006/day-2-understanding-kubernetes-architecture-f7609666e87b?source=post_page---read_next_recirc--89afb866c876----1---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

Oct 5, 2025[11](https://medium.com/@senthil262006/day-2-understanding-kubernetes-architecture-f7609666e87b?source=post_page---read_next_recirc--89afb866c876----1---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

![MinIO, Redis, HashiCorp: A Sustainability Crisis Reaching Your Stack in 2026](https://miro.medium.com/v2/resize:fit:679/format:webp/1*JNe5yh8kYeubS34WAiPR1A.png)[Heinan Cabouly](https://medium.com/@heinancabouly?source=post_page---read_next_recirc--89afb866c876----2---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)## [MinIO, Redis, HashiCorp: A Sustainability Crisis Reaching Your Stack in 2026](https://medium.com/@heinancabouly/minio-redis-hashicorp-a-sustainability-crisis-reaching-your-stack-in-2026-78f9577699cb?source=post_page---read_next_recirc--89afb866c876----2---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

### Three major projects changed their open source model. Your dependencies are next. Here’s what September 2026’s compliance deadline means.

](https://medium.com/@heinancabouly/minio-redis-hashicorp-a-sustainability-crisis-reaching-your-stack-in-2026-78f9577699cb?source=post_page---read_next_recirc--89afb866c876----2---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

6d ago[45](https://medium.com/@heinancabouly/minio-redis-hashicorp-a-sustainability-crisis-reaching-your-stack-in-2026-78f9577699cb?source=post_page---read_next_recirc--89afb866c876----2---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

1

](https://medium.com/@heinancabouly/minio-redis-hashicorp-a-sustainability-crisis-reaching-your-stack-in-2026-78f9577699cb?source=post_page---read_next_recirc--89afb866c876----2---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

![Production-Ready Mocking: Docker, Kubernetes, and CI/CD](https://miro.medium.com/v2/resize:fit:679/format:webp/8e14c4381c6099d3ecf0f402666d596f5a6456be8a58343bf4d85acc567ba803)[Mohsen Zainalpour](https://medium.com/@zainalpour_79971?source=post_page---read_next_recirc--89afb866c876----3---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)## [Production-Ready Mocking: Docker, Kubernetes, and CI/CD](https://medium.com/@zainalpour_79971/production-ready-mocking-docker-kubernetes-and-ci-cd-f835db58e208?source=post_page---read_next_recirc--89afb866c876----3---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

### Deploy mock services like a pro

](https://medium.com/@zainalpour_79971/production-ready-mocking-docker-kubernetes-and-ci-cd-f835db58e208?source=post_page---read_next_recirc--89afb866c876----3---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

4d ago[5](https://medium.com/@zainalpour_79971/production-ready-mocking-docker-kubernetes-and-ci-cd-f835db58e208?source=post_page---read_next_recirc--89afb866c876----3---------------------f3b91f92_4425_409d_826d_97b57bab7163--------------)

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--89afb866c876---------------------------------------)