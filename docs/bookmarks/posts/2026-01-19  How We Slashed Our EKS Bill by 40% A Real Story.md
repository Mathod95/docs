---
title: "How We Slashed Our EKS Bill by 40%: A Real Story"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://aws.plainenglish.io/how-we-slashed-our-eks-bill-by-40-a-real-story-96b93ef7d450"
author:
  - "[[Yash Thaker]]"
---
<!-- more -->

[Sitemap](https://aws.plainenglish.io/sitemap/sitemap.xml)## [AWS in Plain English](https://aws.plainenglish.io/?source=post_page---publication_nav-35e7a49c6df5-96b93ef7d450---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:76:76/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_sidebar-35e7a49c6df5-96b93ef7d450---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*pOBPbYRlJsT6_XwR)

Photo by Alexander Mils on Unsplash

Last year, we inherited a messy EKS infrastructure that was burning through cash like crazy. Around $25K a month, to be exact. Our CTO wasn’t happy, and we had to figure out how to cut costs without breaking things. After months of trial and error, we managed to save over $100K annually. Here’s what actually worked for us.

**The Wake-Up Call**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Bdymx2D4h8xlyCxV)

Photo by bruce mars on Unsplash

I still remember the day our CFO walked into our team meeting with a concerned look. Our AWS bills had been climbing steadily, and EKS was the biggest culprit. The funny thing? We had no idea where all that money was going.

The first thing we did was break down our costs:  
\- EC2 instances for worker nodes (this was bleeding us dry)  
\- Storage (those EBS volumes add up fast)  
\- Data transfer (cross-AZ traffic was killing us)  
\- Load balancers (we had way too many)

**Finding the Low-Hanging Fruit**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*hT9njTMaGKCXOR_q)

Photo by Eran Menashri on Unsplash

Our first win was embarrassingly simple. We had been running our dev and staging environments 24/7. Why? “Because we always did it that way.” A quick script to shut down non-prod clusters during off-hours instantly saved us $3K monthly.

Here’s what we used:

```c
# eks-scheduler.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cluster-scaler
spec:
  schedule: "0 20 * * 1-5"  # 8 PM weekdays
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cluster-ops
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - kubectl scale deployment --all --replicas=0
```

**The Worker Node Saga**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*-OS3p52aQXaqtzki)

Photo by Kate Ferguson on Unsplash

Next up was our worker node setup. We were running m5.2xlarge instances across the board because someone read it was “good for general use.” Classic.

After actually looking at our usage patterns (thank you, Prometheus), we realized something interesting: our Java services were memory hogs, but CPU usage was minimal. Meanwhile, our Go services were CPU-intensive but light on memory.

We split our workloads:

```c
# Before: One size fits none
nodeGroups:
  - name: workers
    instanceType: m5.2xlarge
    desiredCapacity: 30

# After: Mix and match
nodeGroups:
  - name: java-services
    instanceTypes: ["r5.xlarge", "r5a.xlarge"]
    desiredCapacity: 20
  - name: go-services
    instanceTypes: ["c5.large", "c5a.large"]
    desiredCapacity: 10
```

This simple change cut our EC2 costs by 35%. The team thought I was a genius. I didn’t tell them it was just common sense.

**The Spot Instance Adventure**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*agNO4vEJzr3KcR9e)

Photo by Howard Malone on Unsplash

Everyone talks about using spot instances, but let me tell you — our first attempt was a disaster. We tried to run everything on spot, and our services went down during peak hours when spot prices spiked.

Here’s what actually worked:

1\. Use spot instances for stateless workloads only  
2\. Set up a mixed instance policy  
3\. Implement proper pod disruption budgets

Here’s our battle-tested setup:

```c
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
nodeGroups:
  - name: spot-workers
    instanceTypes: ["m5.xlarge", "m5a.xlarge", "m5n.xlarge"]
    desiredCapacity: 5
    minSize: 3
    maxSize: 15
    spot: true
```

Pro tip: Always keep some on-demand instances for critical workloads. Trust me, your sleep schedule will thank you.

**Storage: The Silent Budget Killer**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*PaibCp_nu8MnWuXY)

Photo by Shane on Unsplash

Nobody paid attention to our storage costs until we noticed we were spending $3K monthly on mostly empty volumes. The culprit? Every developer was requesting 100GB volumes because “storage is cheap.”

We implemented storage quotas:

```c
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage-quota
spec:
  hard:
    requests.storage: 500Gi
    persistentvolumeclaims: "10"
```

And switched to gp3 volumes:

```c
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3-standard
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
```

**Real Talk About Results**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*sXd9tK7F7sq7QkD8)

Photo by National Cancer Institute on Unsplash

After six months of optimization:  
\- Monthly AWS bill: Down from $25K to $15K  
\- Application performance: Actually improved (funny how that works)  
\- Team happiness: Way up (fewer 3 AM calls)

**Lessons Learned the Hard Way**

1\. Start with monitoring. You can’t optimize what you can’t measure.  
2\. Don’t try to optimize everything at once. We broke our cluster three times by being too aggressive.  
3\. Get your developers involved. They know their applications better than anyone.

**What’s Next?**

We’re looking at Graviton2 instances now. Initial tests show another 20% potential savings. I’ll probably write another post about that adventure once we’ve finished testing.

That’s our story. Not glamorous, but it worked. What’s your experience with EKS costs? Any horror stories or wins to share? Drop a comment below — I’d love to hear them.

Found this helpful? Let’s connect!

🔗 Follow me on [LinkedIn](https://www.linkedin.com/in/yash-thaker-aws/) for more tech insights and best practices.

💡 Have thoughts or questions? Drop them in the comments below — I’d love to hear your perspective.

If this article added value to your day, consider giving it a 👏 to help others discover it too.

Until next time!

## Thank you for being a part of the community

*Before you go:*

- Be sure to **clap** and **follow** the writer ️👏 **️️**
- Follow us: [**X**](https://x.com/inPlainEngHQ) | [**LinkedIn**](https://www.linkedin.com/company/inplainenglish/) | [**YouTube**](https://www.youtube.com/channel/UCtipWUghju290NWcn8jhyAw) | [**Newsletter**](https://newsletter.plainenglish.io/) | [**Podcast**](https://open.spotify.com/show/7qxylRWKhvZwMz2WuEoua0)
- [**Check out CoFeed, the smart way to stay up-to-date with the latest in tech**](https://cofeed.app/) **🧪**
- [**Start your own free AI-powered blog on Differ**](https://differ.blog/) 🚀
- [**Join our content creators community on Discord**](https://discord.gg/in-plain-english-709094664682340443) 🧑🏻💻
- For more content, visit [**plainenglish.io**](https://plainenglish.io/) + [**stackademic.com**](https://stackademic.com/)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:96:96/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--96b93ef7d450---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:128:128/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--96b93ef7d450---------------------------------------)

[Last published just now](https://aws.plainenglish.io/how-to-run-a-web-application-in-aws-on-a-tight-budget-c659e5bdc3ce?source=post_page---post_publication_info--96b93ef7d450---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.

Senior DevOps Engineer & AWS Community Builder | Cloud Infrastructure Automation Enthusiast | Tech Writer Sharing AWS & DevOps Best Practices

## More from Yash Thaker and AWS in Plain English

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--96b93ef7d450---------------------------------------)