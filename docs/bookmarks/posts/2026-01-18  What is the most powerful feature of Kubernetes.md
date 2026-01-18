---
title: What is the most powerful feature of Kubernetes ?
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://medium.com/@anishbista/what-is-the-most-powerful-feature-of-kubernetes-8ba071f280d1
author:
  - "[[Anish Bista]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*5tqNU82s8r8St5ke.jpg)

***Note: This is hand written blog. In this blog, we gonna discuss about that feature which become one of the main reason behind the success of Kubernetes.***

Let’s start with a bit of history. Before Docker and Kubernetes, Google had been running an containers and orchestration system called Borg internally for so many years. Docker changed the way software is built. So, Googlers definitely had the confidence that something called Kubernetes was going to create a lot of impact in the upcoming decade and I would say google was right.

Google created Kubernetes and open-sourced it, donated it to the CNCF. It gained a lot of attention from all the tech giants. People started contributing to it. Right now, it is the world’s largest open-source project after Linux. Almost all Organizations that run at scale are using Kubernetes in production.

You might be wondering what was the one important thing that enabled developers to build their solutions around Kubernetes, and how the number of projects in the CNCF is increasing. I would say, based on experience and knowledge, it is the ***“Extensive features of Kubernetes”***

Let’s elaborate it.

If you are working with Kubernetes, you might have created deployment thousand times.

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

If you apply this manifest, the API server will be able to recognize it, and the ReplicaSet controller will react based on it and create the target Pod based on the configuration, and always maintain the desired state. But if you try to put maybe a ***spec.anish.age***, the API server will reject it.

```c
spec:
  anish: 
    age: <> # This will be rejected by API Server
```

The hack is what if somebody has their own setup problem and they want to build their own resource and write the controller loop to handle that part and leave the rest of the things to Kubernetes.

Comes into the picture **Kubernetes Custom Operator.** Operator is the combination of CRD (Custom Resource Definition) that lets you extend your Kubernetes API and create your own resource based out of your business need and a controller to handle that Custom Resource within the cluster.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*aOmvQhnC2hUlVUcX.png)

[***CRD (Custom Resource Definition)***](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)***:***  
In simple words, it is the blueprint for your custom resource.

[***CR (Custom Resource):***  
](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)This is the actual resource, like a Deployment, which will be recognized by the API server.

[***Controller (Reconcile function):***  
](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#custom-controllers)The main important part in the controller is the reconcile function that always listens/watches for any changes to your custom resource / other resources. It is responsible for maintaining the desired state.

Now, I hope you might have basic understanding of Kubernetes custom operator. If you see [CNCF Landscape](https://landscape.cncf.io/) there are total 239 project (at the time while writing this blog). Majority of the project are built on the top of Kubernetes by extending Kubernetes API means they come up with thier own CRD and Reconcile loop.

In my previous [blog on Platform Engineering](https://medium.com/@anishbista/platform-engineering-how-to-build-green-kubernetes-platform-for-your-business-fde340cebaf8) , all the tools that I have mentioned are Operator based.

**Conclusion:**  
People have extended the Kubernetes API to the next level, and every day they are building new solutions, and there is no end to this, right? Let’s say you have some problem and you want to automate it. Just build an operator. But with great power comes great responsibility. You should be capable enough to manage these things at scale:)

> I strongly believe that the ***“Extensive features of Kubernetes”*** is the main reason behind the success of Kubernetes adoption. AI experts believe that Kubernetes is going to be the next Linux to run their AI workloads. I hope this will be continue in next decade.

**FAQs in the Kubernetes community:**

**1)Will the Kubernetes ecosystem be replaced by AI in the future?**

*Nothing is impossible, but what I can say is that it is very, very, very hard to automate. From a business perspective, just check the investment in the CNCF, which is almost around 400 billion dollars. Do you think investors will allow automation of the whole ecosystem?*

**2)Will there be something that replaces Kubernetes?**

*Solutions for the current problems with Kubernetes will define the next era of Kubernetes, which may be something more powerful than Kubernetes.*

## More from Anish Bista

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--8ba071f280d1---------------------------------------)