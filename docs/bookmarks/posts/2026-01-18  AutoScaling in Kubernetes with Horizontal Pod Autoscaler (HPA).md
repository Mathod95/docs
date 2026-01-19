---
title: "AutoScaling in Kubernetes with Horizontal Pod Autoscaler (HPA)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.stackademic.com/autoscaling-in-kubernetes-with-horizontal-pod-autoscaler-hpa-7ea780f87755"
author:
  - "[[Dhruvin Soni]]"
---
<!-- more -->

[Sitemap](https://blog.stackademic.com/sitemap/sitemap.xml)## [Stackademic](https://blog.stackademic.com/?source=post_page---publication_nav-d1baaa8417a4-7ea780f87755---------------------------------------)

[![Stackademic](https://miro.medium.com/v2/resize:fill:76:76/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_sidebar-d1baaa8417a4-7ea780f87755---------------------------------------)

Stackademic is a learning hub for programmers, devs, coders, and engineers. Our goal is to democratize free coding education for the world.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*6wr-gyxvIwLXwcdv.png)

HPA

### What is HPA in K8s?

Horizontal Pod Autoscaler (HPA), in Kubernetes, is a system that automatically adjusts the number of pods in a deployment or replica set based on observed CPU utilization or other select metrics provided by the user. The main goal of HPA is to scale out (add more pods) when the load increases and scale in (remove pods) when the load decreases, ensuring that applications maintain performance without wasting resources.

### How does HPA work?

1. **Metrics Monitoring:** HPA retrieves metrics that it uses to make scaling decisions. These metrics can be CPU utilization, memory usage, or custom metrics defined by the user.
2. **Decision Making:** HPA calculates the desired number of pods by comparing the current metrics against the targets specified. For instance, if the target CPU utilization is set to 50% and the current utilization is 100%, HPA will decide to increase the number of pods to try to halve the CPU usage per pod.
3. **Scaling:** Based on its calculations, HPA adjusts the number of pods. It interacts with the Kubernetes API to scale the number of pods up or down according to the need.

### Configuration Elements

- **Metrics to be monitored:** Users can define what metrics the HPA should monitor. By default, it’s usually CPU but can include memory or any other custom metric set up via the metrics server or provided by external sources like Prometheus.
- **Scaling targets:** These are the values that the HPA tries to maintain. For CPU or memory, it’s often a percentage. For custom metrics, it could be the number of requests per second.
- **Min and Max Number of Pods:** Defines the minimum and maximum number of pods that the HPA can scale to. This prevents the system from scaling beyond what the underlying infrastructure can support.
- **Cooldown/Delay:** After scaling, HPA has a cooldown period during which it doesn’t make further scaling decisions. This prevents rapid fluctuation in the number of pods which can be destabilizing.

### How to Use HPA Metrics?

Kubernetes HPA supports four kinds of metrics:

**Resource Metric**

Resource metrics refer to CPU and memory utilization of Kubernetes pods against the values provided in the limits and requests of the pod spec. These metrics are natively known to Kubernetes through the metrics server. The values are averaged together before comparing them with the target values. That is, if three replicas are running for your application, the utilization values will be averaged and compared against the CPU and memory requests defined in your deployment spec.

**Object Metric**

Object metrics describe the information available in a single Kubernetes resource. An example of this would be hits per second for an ingress object.

**Pod Metric**

Pod metrics (referred to as PodsMetricSource) reference pod-based metric information at runtime and can be collected in Kubernetes. An example would be transactions processed per second in a pod. If there are multiple pods for a given PodsMetricSource, the values will be collected and averaged together before being compared against the target threshold values.

**External Metrics**

External metrics are metrics gathered from sources running outside the scope of a Kubernetes cluster. For example, metrics from Prometheus can be queried for the length of a queue in a cloud messaging service, or QPS from a load balancer running outside of the cluster.

### Horizontal Pod Autoscaler API Versions

API version autoscaling/v1 is the stable and default version; this version of API only supports CPU utilization-based autoscaling.

autoscaling/v2 version of the API brings usage of multiple metrics, and custom and external metrics support.

You can verify which API versions are supported on your cluster by querying the API versions. This command lists, all the versions.

```c
# kubectl api-versions | grep autoscaling
autoscaling/v1
autoscaling/v2
autoscaling/v2beta1
autoscaling/v2beta2
```

### Requirements:

Horizontal Pod Autoscaler (and also Vertical Pod Autoscaler) requires a [Metrics Server](https://github.com/kubernetes-sigs/metrics-server) installed in the Kubernetes cluster. Metric Server is a container resource metrics (such as memory and CPU usage) source that is scalable, can be configured for high availability, and is efficient on resource usage when operating. Metrics Server gathers metrics -by default- every 15 seconds from Kubelets, this allows rapid autoscaling,

### Installation of Metrics Server:

Metrics Server offers two easy installation mechanisms.

1. Using `kubectl` that includes all the manifests.
```c
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

2\. The second option is using the Helm chart.

```c
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm upgrade --install metrics-server metrics-server/metrics-server
```

### Verify the Installation

As the installation is finished and we allow some time for the Metrics Server to get ready, run the below command to verify

```c
kubectl top pods
```
```c
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$ kubectl top pods
NAME                              CPU(cores)   MEMORY(bytes)   
metrics-server-5f47bb57f7-jcpzb   3m           18Mi            
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$
```
```c
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$ kubectl top nodes
NAME                                           CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%   
ip-192-168-70-238.us-east-2.compute.internal   39m          2%     509Mi           7%        
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$
```

You can also send queries directly to the Metric Server via `kubectl`

```c
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$ kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes | jq
{
  "kind": "NodeMetricsList",
  "apiVersion": "metrics.k8s.io/v1beta1",
  "metadata": {},
  "items": [
    {
      "metadata": {
        "name": "ip-192-168-70-238.us-east-2.compute.internal",
        "creationTimestamp": "2024-04-19T11:51:35Z",
        "labels": {
          "alpha.eksctl.io/cluster-name": "prod-cluster",
          "alpha.eksctl.io/nodegroup-name": "prod-workers",
          "beta.kubernetes.io/arch": "amd64",
          "beta.kubernetes.io/instance-type": "t2.large",
          "beta.kubernetes.io/os": "linux",
          "eks.amazonaws.com/capacityType": "ON_DEMAND",
          "eks.amazonaws.com/nodegroup": "prod-workers",
          "eks.amazonaws.com/nodegroup-image": "ami-06868002018b8d7a7",
          "eks.amazonaws.com/sourceLaunchTemplateId": "lt-09846d96d35ca8459",
          "eks.amazonaws.com/sourceLaunchTemplateVersion": "1",
          "failure-domain.beta.kubernetes.io/region": "us-east-2",
          "failure-domain.beta.kubernetes.io/zone": "us-east-2b",
          "k8s.io/cloud-provider-aws": "005adb6d0ecd78b27855fb14fff1bda9",
          "kubernetes.io/arch": "amd64",
          "kubernetes.io/hostname": "ip-192-168-70-238.us-east-2.compute.internal",
          "kubernetes.io/os": "linux",
          "node.kubernetes.io/instance-type": "t2.large",
          "topology.kubernetes.io/region": "us-east-2",
          "topology.kubernetes.io/zone": "us-east-2b"
        }
      },
      "timestamp": "2024-04-19T11:51:26Z",
      "window": "20.03s",
      "usage": {
        "cpu": "35811125n",
        "memory": "549124Ki"
      }
    }
  ]
}
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$
```

### Configure Horizontal Pod Autoscaling:

- Now, let’s configure the HPA
- Create the `deployment.yaml` file and add the below code to it.
```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  selector:
    matchLabels:
      app: myapp
  replicas: 2
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: dhruvin30/dhsoniweb
```
- Run the below command to apply the changes.
```c
kubectl apply -f deployment.yaml
```
- Verify the deployment.
```c
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$ kubectl get deploy 
NAME               READY   UP-TO-DATE  AVAILABLE   AGE
myapp-deployment   2/2     2           2         16s
[dhruvinsoni@Dhruvins-MacBook-Pro ~ (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$
```
- Create `service.yaml` file and add the below code to it.
```c
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
  - port: 80
```
- Run the below command to apply the changes.
```c
kubectl apply -f service.yaml
```
- Create `hpa.yaml` file and add the below code to it.
```c
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
 name: myapp-hpa
spec:
 scaleTargetRef:
   apiVersion: apps/v1
   kind: Deployment
   name: myapp-deployment
 minReplicas: 2
 maxReplicas: 10
 targetCPUUtilizationPercentage: 50
```
- Run the below command to apply the changes
```c
kubectl apply -f hpa.yaml
```
- So this HPA says that the deployment `myapp-deployment` should have a minimum replica count of 2 all the time, and whenever the CPU utilization of the Pods reaches 50 percent, the pods should scale up to 10 replicas.
- We will now send some load requests to the service that we created earlier. When the CPU utilization goes about 50% we should see the replicas scaling.
```c
$ external_ip=$(kubectl get svc myapp-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
$ while true; do curl $external_ip ; done
```
- Once the CPU crossed the threshold, we should now see the pods being scaled up in the events of the HPA.
- Once stop sending the load to service, you should see the replicas being scaled back.
- Don’t forget to clean up the resources.

### Conclusion:

In this article, I walked you through how to set up and configure the HPA to auto-scale the replicas of pods based on the metrics. You can now use different metrics to test the HPA and play with it.

If you found this guide helpful then do click on 👏 the button and also feel free to drop a comment.

Follow for more stories like this 😊

## Stackademic 🎓

Thank you for reading until the end. Before you go:

- Please consider **clapping** and **following** the writer! 👏
- Follow us [**X**](https://twitter.com/stackademichq) **|** [**LinkedIn**](https://www.linkedin.com/company/stackademic) **|** [**YouTube**](https://www.youtube.com/c/stackademic) **|** [**Discord**](https://discord.gg/in-plain-english-709094664682340443)
- Visit our other platforms: [**In Plain English**](https://plainenglish.io/) **|** [**CoFeed**](https://cofeed.app/) **|** [**Venture**](https://venturemagazine.net/) **|** [**Cubed**](https://blog.cubed.run/)
- More content at [**Stackademic.com**](https://stackademic.com/)

[![Stackademic](https://miro.medium.com/v2/resize:fill:96:96/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_info--7ea780f87755---------------------------------------)

[![Stackademic](https://miro.medium.com/v2/resize:fill:128:128/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_info--7ea780f87755---------------------------------------)

[Last published just now](https://blog.stackademic.com/the-future-of-coding-is-vibe-coding-but-fundamentals-still-matter-d34114b48689?source=post_page---post_publication_info--7ea780f87755---------------------------------------)

Stackademic is a learning hub for programmers, devs, coders, and engineers. Our goal is to democratize free coding education for the world.

Senior Cloud Infrastructure Engineer | AWS | Automation | 2x AWS | CKA | Terraform Certified | k8s | Docker | CI/CD | [http://dhsoni.info/](http://dhsoni.info/)

## More from Dhruvin Soni and Stackademic

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--7ea780f87755---------------------------------------)