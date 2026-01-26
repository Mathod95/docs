---
title: "Tips and tricks for passing the CKAD exam — Notes #1 of 4"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@shamre/notes-for-passing-the-ckad-exam-and-understanding-the-concepts-of-kubernetes-8de04720279b"
author:
  - "[[Shambhu Kumar Sinha]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@shambhu)

> My motivation for writing these articles inspired by quote
> 
> **“You teach best what you most need to learn -Richard Bach”**

![](https://miro.medium.com/v2/resize:fit:640/1*RDWEongNPCCiiJU_1yqlvQ.png)

The Kubernetes CKAD exam is not all about knowledge and concepts but also about the efficiency of solving problems quickly.

I am covering a series of four articles from my CKAD exam notes as well as tips and tricks for clearing the CKAD exam. Starting here with the syllabus (the Domains & Competencies) for CKAD and what to focus on, I will subsequently cover other important tips and tricks in the rest of the articles.

> Probably you need to know about the imperative way of working before reading further. Imperative ways of working with Kubernetes mean creating or configuring Kubernetes objects by using the kubectl command. The declarative way involves configuring Kubernetes objects in YAML files and using the kubectl apply or replace command. l will discuss both in the later part of this series.

## CKAD Domains & Competencies (Syllabus) # What to practice.

Each Domains & Competencies got some weightage marked in percentage.

### A. Application Design and Build (20%)

1. Define, build and modify container images. — Practice imperative commands for creating Pods, Deployments, and their different settings. Also, one question is generally comes from Docker or Podman, so we need good practice on creating Dockerfiles and their different instructions. A question was also asked for extracting image containers in OCI format, etc.
2. Understand Jobs and CronJobs- Practice imperative commands but memorize settings for Job as well as for CronJob for solving problems fast, I will discuss those later in the next article.
3. Understand multi-container Pod design patterns (e.g. sidecar, init, and others) — Practice adding multiple image containers in Pod and practice using the vim editor to copy, paste, and modify Pod configurations correctly and quickly.
4. Utilize persistent and ephemeral volumes — Practice searching Kubernetes documentation for different examples of PV, PVC, and storage classes, as well as usages of PVC in Pod.

### B. Application Deployment (20%)

1. Use Kubernetes primitives to implement common deployment strategies (e.g. blue/green or canary) — Practice applying all four deployment strategies by editing or deploying Deployments. This requires Vim editor practice. There is no imperative command for strategy change except for cannery, where there may be a need to create different Deployments.
2. Understand Deployments and how to perform rolling updates — Learn the imperative command for rolling updates as well as the scale command.
3. Use the Helm package manager to deploy existing packages — Practice Helm commands and have a mental map of repo, hub, release, and local repository, as well as Kubernetes deployment.

### C. Application Observability and Maintenance (15%)

1. Understand API deprecations — Practice on the Kubectl convert tool for migration and try to practice on api-resource and their version using proxy; generally, one question is based on this, and it’s very easy.
2. Implement probes and health checks — Practice configuring the liveness and readiness probes in the main container and NOT in the init container. Mug up all configurations of liveness and readiness probes and their structures.
3. Use the tools provided to monitor Kubernetes applications — Practice command for determining the maximum CPU or memory consumed by a pod or node is also asked to identify the pod with the maximum resource usage.
4. Utilize container logs — Practice checking pod logs for different containers as well as different types of issues; simulate issues; and practice seeing output in logs.
5. Debugging in Kubernetes — there are 5–6 ways of debugging the pod or Kubernetes objects issues, describe, logs, and events. Practice issues by simulating them, and check if those are able to be discovered by these different methods.

### D. Application Environment, Configuration and Security (25%)

1. Discover and use resources that extend Kubernetes (CRD) — Practice creating CRD, and memorising their attributes and structure, as well as important configurations. Practice on debugging for issues.
2. Understand authentication, authorization and admission control — This requires concept understanding as well as the use of imperative commands and practices for access by defining roles and binding them to the user or service account.
3. Understanding and defining resource requirements, limits and quotas — use the imperative command for setting quotas, but LimitRange can only be done by declaration.
4. Understand ConfigMaps — you must be well versed in imperative commands for CM and Secret. There are a few different ways to use CM and Secret. Many times, chaining Kubectl commands is very useful. See the Kubectl command reference in the documentation.
5. Create & consume Secrets — must be well versed in using imperative commands for CM and secret.
6. Understand ServiceAccounts — must be clear on the concept and practice of SA and role-binding and learn how to debug issues related to SA. How to configure SA using the imperative set command.
7. Understand security contexts — memorize a few frequently used security capabilities and practice these with different configurations. Mostly, referring to Kubernetes documentation is helpful or sufficient.

### E. Services anu Networking (20%)

1. Demonstrate basic understanding of NetworkPolicies — They are very easy but always tricky, so they require good practice of configuration with various scenarios. No imperative command is available for NetPol.
2. Provide and troubleshoot access to applications via services — This part is hard, but the only thing to do is learn the concept and practice all previous questions.
3. Use Ingress rules to expose applications — Learn the imperative way to create Ingress.

## A glimpse of the summary of 16 questions is generally asked and must be practiced accordingly

1. Create a pod and set up env, or questions can be around setting up with some other configurations.
2. Create a CornJob that runs every 2 minutes, with a timeout of 20 seconds; success: 3; failure: 4. Test this Cronjib by creating a job.
3. Build a local Dockerfile file and copy the container in OCI format to a specified location as a tar file.
4. There was a pod configured with the wrong service account as default and required a fix with another service account, but it must have the right permission.
5. Ingress for one url accessing many services or questions can be to fix issue of ingress configuration.
6. NetPol for pods accessing only two ports and a pod, or NetPol for pods accessing only two pods
7. One Deployment configuration can be given and had to update surge, etc., and some other easy stuff.
8. One Deployment had to update the ENV, CM, and image, then rollback to previous
9. Migrate Deployment from version 1.15 YAML to 1.26 and deploy it
10. One deployment was updated with a liveness probe, but the deployment had an intiContainer, so it was unclear which container should be probed.
11. A configuration file was given for deployment, and we had to implement a canary deployment strategy.
12. Pod creation with env from secret and create secret.
13. Apply memory limit of a crashing Pod and value of memory limit should be half of range limit defined for namespace.
14. Helm chart deployment from repo
15. One Deployment with a couple of PV and PVC as well as a storage class
16. Question on NodePort with some other changes by expose

## The CKAD Exam preperation

### A. Developing CKAD Concepts

1. Kubernetes Concept: You must be very good with all Kubernetes concepts as per the CKAD exam syllabus. It may require a little more reading than the syllabus, but try to stick with it. Building concepts and initial practices may require 4–5 months, depending on your speed. I recommend reading Kubernetes in Action: [https://www.manning.com/books/kubernetes-in-action](https://www.manning.com/books/kubernetes-in-action)
2. I recommend the following course and additional suggestions:
- The Udemy course by Mumshad Mannambeth — [Kubernetes Certified Application Developer (CKAD) with Tests](https://www.udemy.com/course/certified-kubernetes-application-developer/)
- If you just want to prepare for the CKAD exam, then there is no need to spend time setting up Minikube, subscribing to VMs, setting up nodes, etc., as you will get a full-fledged Kubernetes practice environment in KodeKloud once you subscribe to the Udemy course.
- Go through the Kubernetes documentation multiple times and focus on the below topics.
```c
1. Concepts
2. Tasks
3. Tutorials
4. Reference 
       - focus on command line tool (kubectl) 
       - all four sections 
           # for understanding imperative commands and docker commands
```

### B. Strategy for solving problems faster

1. Create a mental map of examples in the Kubernetes documentation, as it is permissible to use documentation during exams. Some examples can be directly copied from the documentation and slightly modified for the solution. Practice Kubectl’s Set command chaining for Deployment as well as for Pod.
2. You must be very good with the VIM editor, so learn to use various shortcut keys and commands. Being efficient in the editor saves lots of time.
3. Develop your strategy to solve a problem in 4 to 5 minutes; with 4–5 minutes, understand the problem, work on a solution, as well as test the solution. The following was my strategy to increase the speed of the solution:
- Creating an alias or function (yes, function; I will share details later) to solve problems quickly, like listing all pods and services and deployment together with showing labels as well as detailed output (-o wide)
- Use aliases or functions to test, as well as aliases for running a temporary pod and accessing a newly created pod and behaviour.

### C. Right exam Practice

1. Must have an exam-like simulation for practice and must practice at least one month daily before the exam. One test, and also brushing up and practicing the problems on concept. I would suggest **KodeKloud — Ultimate CKAD mock exam series** as well as killer.sh that comes with the CKAD exam for two free practices, but both tests will have the same questions. Try to attempt the killer.sh exam 2–3 weeks before the exam, so that will help in building the exam strategy and test efficiency. Also, [Kubernetes 1.29 | Playgrounds | Killercoda](https://killercoda.com/playgrounds/scenario/kubernetes) can be used for most of practice.
2. Configuring the VIM editor for fast editing
3. Once you solve the problem, testing is very important immediately, so have testing strategy practice while solving the problem during practice.
4. Should be good with some Linux commands like ssh, file copy, sudo, etc.

### D. Strategy to track solved and unloved problems with weightage during exam.

1. Generally, a grid with five columns and each grid with points seems like a better strategy.
2. Also, generally, there will be 16 questions, and the question weights will be 8 or 6 or 4. So, the maximum number of questions will have a weight of 8.
3. I used a mouse-pad app from Accessories to note the question marks and track them; see below in the screen below the right corner for my question tracker strategy. I used a mark for defining position as well as an \* for problem solved, and I tested an otherwise short note on question type.
![](https://miro.medium.com/v2/resize:fit:640/1*aw4HvtZv4nSTFwg13q2RJQ.png)

Check here: [GitHub — piouson/kubernetes-bootcamp: A modern All-In-One guide to become proficient with Kubernetes core concept and pass the Certified Kubernetes Application Developer (CKAD) exam](https://github.com/piouson/kubernetes-bootcamp#exam-questions-approach)

### E. Planning and precautions for appearing for exam

1. Please refrain from taking the CKAD test on your company’s laptop as most company’s laptop prohibit unknown exe installations on computer and PSI browser may be not authorized software. It will take around ten to fifteen minutes to download and install the PSI browser ([see screenshot](https://lh5.googleusercontent.com/X0gMiwExkdRGqdGpJ2pxuyWLoWFSbdjtyN7o6jKwo_YqyCviuHaGjzCQNJWcu_-hSW0jwg1jLLBNKShLQLRQHn09cmalc8ynWQ-zctq6E_u7LlRX8TkfF78EcKPeUoTm2Gw3XSnlfcuSFUbq_ck)), which is required for the exam’s remote connection. Installation requires administrative access on the computer on which you will be taking the test.
2. Due to the nature of the test and the limitations of the remote access computer, you will not be permitted to access your local desktop or system during the exam. While you won’t have access to the internet, you will have access to the documentation for Kubernetes and Helm. Downloads of any kind, including installers, are restricted to Kubernetes-only sites, such as the Convert tool.
3. Use a big monitor and a desktop system. A laptop is not suitable at all for the CKAD exam due to its small screen and a lot of restrictions on scrolling and searching documentation in Firefox. As well, we need to work with many nested windows, and it would be a very pathetic situation to use small screens. If possible, I would suggest using a 24+ inch monitor with a external webcam on the desktop system. Also, use a better mouse and keyboard. Using the touchpad caused a lot of issues.
4. Every problem has its own context, and a command is given to switch the context. So every time, you must run the set context command. Along with changing the namespace as well. Using the function (nnc ns, mentioned in the next topic) would be useful as well. You will find your solution disappearing because you are not setting the right context.
5. Try to copy everything from the questions rather than typing.
6. Do not worry about setting up vim for tabstop, etc. These are available, but you must set some variables for the other aliases discussed in the next topic.
7. You must be good with using “explain” commands and use it with grep with A5, B2, etc. This is an easier way to search for documentation than to go to HTML documentation. I will explain this in detail in a later topic.
8. Memories and practice Kubernetes important object attributes and structures in YAML. There will be almost a list of 15–20 attributes that you must have by heart.
9. Kubectl-convert is not available, so you need to install it and practice with the document location so that you can do it quickly. The conversion was 1.15 to 1.28.
10. The killer.sh session pretty much matches the exam, so you must practice. But the live exam is 10 times more restricted for appearance than for the level of problems. The explanation of the test report for killer.sh is also good and really gives a detailed solution.
11. You must go through [https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-user-interface/examui-performance-based-exams](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/exam-user-interface/examui-performance-based-exams)
12. If comfortable, use tmux for breaking the screen into multiple sessions for working on multiple things, like opening a document or other template and copying. I never required this during the exam, but many have suggested it. There are many issues with the copy.
13. When the exam session begins, a mandatory guide will appear on the screen. Go through the details and do all the setup, like minimise the top bar and act quickly to set up all aliases, exports, etc. Keep max 3–4 minutes for these settings and arranging windows.
14. Read the note about namespace, context, and description of the problem at the top. And for each
15. Firefox browser will not be showing page search at the bottom by default, so you need to do a little drag-down window from the top and bring the browser a little up to show in the left bottom corner.

### E. Some useful bookmark allowed during exam

- [**https://kubernetes.io/docs/reference/kubectl/overview/**](https://kubernetes.io/docs/reference/kubectl/overview/)
- [**https://kubernetes.io/docs/reference/kubectl/cheatsheet/**](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#-strong-getting-started-strong](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#-strong-getting-started-strong)

### C. Some reference

1. [https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad](https://docs.linuxfoundation.org/tc-docs/certification/tips-cka-and-ckad)
2. [https://jamesdefabia.github.io/docs/user-guide/kubectl/kubectl\_describe/](https://jamesdefabia.github.io/docs/user-guide/kubectl/kubectl_describe/)
3. [https://www.youtube.com/watch?v=hKVz-Mwo9DM](https://www.youtube.com/watch?v=hKVz-Mwo9DM)
4. Helpful [https://youtu.be/4yhdTz1NFU0](https://youtu.be/4yhdTz1NFU0)

### D. Practice reference

1. [https://github.com/dgkanatsios/CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises)
2. [https://github.com/lucassha/CKAD-resources](https://github.com/lucassha/CKAD-resources)
3. [https://medium.com/bb-tutorials-and-thoughts/practice-enough-with-these-questions-for-the-ckad-exam-2f42d1228552](https://medium.com/bb-tutorials-and-thoughts/practice-enough-with-these-questions-for-the-ckad-exam-2f42d1228552)
4. [https://github.com/piouson/kubernetes-bootcamp](https://github.com/piouson/kubernetes-bootcamp)

### Must go through below documents and understand exam environment as well as does and don’t

1. Certified Kubernetes Application Developer: [https://www.cncf.io/certification/ckad/](https://www.cncf.io/certification/ckad/)

2\. Candidate Handbook: [https://www.cncf.io/certification/candidate-handbook](https://www.cncf.io/certification/candidate-handbook)

Gathering the information necessary to succeed on the CKAD exam is the goal of this blog. Consider yourself prepared for the test; you should be aware of all the material and know where to put your emphasis. By reading this, you may get the correct information and save a lot of time compared to doing your own research. Please do your best on the exam and let me know what you think by leaving a comment on this blog.

### Summary of this series

1. Part 1 — [About CKAD Test, CKAD Domains & Competencies (Syllabus) # What to practice](https://medium.com/@shamre/notes-for-passing-the-ckad-exam-and-understanding-the-concepts-of-kubernetes-8de04720279b)
2. Part 2 — [Working with Linux commands, usage of JSON, YAML etc. for CKAD exam](https://medium.com/@shamre/notes-for-passing-the-ckad-exam-and-understanding-the-concepts-of-kubernetes-part-2-dd67db2146f1)
3. Part 3 — [How to improve efficiency and some details on non Kubernetes object practice](https://medium.com/@shamre/notes-for-passing-the-ckad-exam-and-understanding-the-concepts-of-kubernetes-part-3-6115b500abbf)
4. Part 4 — [All about Kubernetes objects](https://medium.com/@shamre/notes-and-some-important-concepts-required-for-passing-the-ckad-exam-note-4-f7b03553c9f4)