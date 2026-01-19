---
title: "How do we manage k8s applications deployed in multiple k8s clusters using argoCD & Helm?"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.stackademic.com/how-do-we-manage-k8s-applications-deployed-in-multiple-k8s-clusters-using-argocd-helm-d1de7b1d36e6"
author:
  - "[[Dhruvin Soni]]"
---
<!-- more -->

[Sitemap](https://blog.stackademic.com/sitemap/sitemap.xml)## [Stackademic](https://blog.stackademic.com/?source=post_page---publication_nav-d1baaa8417a4-d1de7b1d36e6---------------------------------------)

[![Stackademic](https://miro.medium.com/v2/resize:fill:76:76/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_sidebar-d1baaa8417a4-d1de7b1d36e6---------------------------------------)

Stackademic is a learning hub for programmers, devs, coders, and engineers. Our goal is to democratize free coding education for the world.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*qlqmdXvQ9eLpow17.png)

argoCD

### What is ArgoCD?

Argo CD is a Kubernetes-native continuous deployment (CD) tool. Unlike external CD tools that only enable push-based deployments, Argo CD can pull updated code from Git repositories and deploy it directly to Kubernetes resources.

### What is GitOps?

GitOps is a way of implementing Continuous Deployment for cloud-native applications. It focuses on a developer-centric experience when operating infrastructure using tools developers are already familiar with, including Git and Continuous Deployment tools.

The core idea of GitOps is to have a Git repository that always contains declarative descriptions of the infrastructure currently desired in the production environment and an automated process to make the production environment match the described state in the repository. If you want to deploy a new or existing application, you only need to update the repository — the automated process handles everything else. It’s like having cruise control for managing your applications in production.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*tYjokgWsZVKH3V1w.png)

GitOps with CI/CD

If you want to learn more about argoCD and GitOps then click [**here**](https://blog.stackademic.com/a-complete-overview-of-argocd-with-a-practical-example-0cf7edb00cb1).

In this tutorial, we will see how do we manage k8s application deployed in multiple k8s clusters using argoCD & Helm. I will use my portfolio application’s image to demonstrate this tutorial. I will create the application in 3 different k8s clusters i.e. prod, dev & stg.

### Prerequisites:

- 3 running k8s clusters (for prod, dev & stg environment)
- argoCD installed in one of the k8s clusters.
- eksctl installed
- Git repository

Click [**here**](https://blog.stackademic.com/a-complete-overview-of-argocd-with-a-practical-example-0cf7edb00cb1) to learn how to install argoCD in the k8s cluster.

Now, let’s start configuring the project.

### Step 1: Register the k8s cluster with argoCD

- Run the below command to log in to argoCD
```c
argocd login 127.0.0.1:<argocd_port>
```
- The above command will ask for the `username` and `password`. username will be `admin` and you can fetch the password by running the below command.
```c
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```
- After login, run the below command to register the k8s cluster with argoCD.
```c
argocd cluster add your_k8s_context_name
```
- You will see the cluster under the `Settings -> Clusters` in argoCD UI.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QZcuTkvu_T78cDRHmsCDuQ.png)

Clusters

### Step 2: Create the Helm chart for the application

- We need to create the helm chart for our application with different values for each environment.
```c
[dhruvinsoni@Dhruvins-MacBook-Pro charts (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$ tree
.
└── portfolio-app
    ├── Chart.yaml
    ├── templates
    │   ├── deployment.yaml
    │   └── service.yaml
    └── values
        ├── development
        │   └── values.yaml
        ├── production
        │   └── values.yaml
        └── staging
            └── values.yaml

7 directories, 6 files
[dhruvinsoni@Dhruvins-MacBook-Pro charts (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$
```
- Above is the structure of the helm chart. Create the same structure in your machine.
- Add the below code to the `Chart.yaml` file.
```c
apiVersion: v1
name: my-web-app
description: A Helm chart for my portfolio website
type: application
version: 1.0.0
appVersion: 1.0.0
maintainers:
  - name: Dhruvin Soni
    email: dksoni4530@gmail.com
```

> Note: You can replace the values as per yours.

### Step 3: Create the deployment & service for the application

- Create the `deployment.yaml` & `service.yaml` file in the `templates` folder.
- Add the below code to `deployment.yaml` file.
```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}
  namespace: {{ .Values.service.nameSpace }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
```
- Add the below code to `service.yaml` file.
```c
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.service.name }}
  namespace: {{ .Values.service.nameSpace }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    protocol: TCP
  selector:
    app: {{ .Chart.Name }}
```
- The values will be rendered from the values file which we will create later in the tutorial.

### Step 4: Store the code in the Git repository

- Now, for argoCD to apply the changes we need to store the code to the Git repository.
- Create a Git repository and store the code in it.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*6uwmXLajqSe_PMarjhFhAQ.png)

Code

### Step 5: Create the values file

- Create the `production`, `development` & `staging` directory in the `values` directory and create `values.yaml` file in each directory.
- Add the below code to development values.yaml file.
```c
replicaCount: 1
image:
  repository: dhruvin30/dhsoniweb
  tag: v1
  pullPolicy: IfNotPresent
service:
  name: my-web-app-dev
  type: LoadBalancer
  port: 80
  nameSpace: mywebapp
```
- For the development environment, I have set the `replicaCount` to 1.
- Add the below code to staging values.yaml file.
```c
replicaCount: 1
image:
  repository: dhruvin30/dhsoniweb
  tag: v1
  pullPolicy: IfNotPresent
service:
  name: my-web-app-stg
  type: LoadBalancer
  port: 80
  nameSpace: mywebapp
```
- For the development environment, I have set the `replicaCount` to 1.
- Add the below code to production values.yaml file.
```c
replicaCount: 3
image:
  repository: dhruvin30/dhsoniweb
  tag: v1
  pullPolicy: IfNotPresent
service:
  name: my-web-app-prod
  type: LoadBalancer
  port: 80
  nameSpace: mywebapp
```
- For the production environment, I have set the `replicaCount` to 3.
- Commit all the code to the git repository

### Step 6: Create the applications in argoCD

- Now, we need to create the 3 different applications in argoCD for each environment.
```c
[dhruvinsoni@Dhruvins-MacBook-Pro applications (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$ tree
.
├── pre-prod
│   ├── portfolio-app-dev.yaml
│   └── portfolio-app-stg.yaml
└── prod
    └── portfolio-app-prod.yaml

3 directories, 3 files
[dhruvinsoni@Dhruvins-MacBook-Pro applications (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$
```
- The above is the structure of the argoCD applications.
- `pre-prod` folder contains the dev & stg application code and `prod` folder contains the prod application code.
- Add the below code to `portfolio-app-dev.yaml`
```c
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: portfolio-app-dev-set
  namespace: argocd
spec:
  generators:
  - list:
      elements:
        - cluster_url: 'https://E1AD8AA23D533C4F7577F7E5490B77F3.gr7.us-east-2.eks.amazonaws.com'
          environment: development
          target_revision: HEAD
          namespace: mywebapp
          region: us-east-1
  template:
    metadata:
      name: portfolio-app-{{environment}}-{{region}}
    spec:
      destination:
        namespace: '{{namespace}}'
        server: '{{cluster_url}}'
      source:
        path: 'charts/portfolio-app'
        repoURL: 'https://github.com/Dhruvin4530/argoCD-Helm'
        targetRevision: '{{target_revision}}'
        helm:
          releaseName: portfolio-app
          valueFiles:
            - ./values/{{environment}}/values.yaml
      project: default
      syncPolicy:
        syncOptions:
        - CreateNamespace=true
```

> Note: You need to change the cluster\_url, repoURL, path, namespace & region as per yours

- The above code will create the application in the `argocd` namespace because all the resources of argoCD are deployed in the same namespace.
- `mywebapp` is the namespace where argoCD will create the deployment and service for our applications.
- For argoCD to create the namespace automatically we need to define `CreateNamespace=true`
- Add the below code to `portfolio-app-stg.yaml`
```c
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: portfolio-app-stg-set
  namespace: argocd
spec:
  generators:
  - list:
      elements:
        - cluster_url: 'https://C97142F25F1C99374E82B9D29D8F83A7.gr7.us-east-2.eks.amazonaws.com'
          environment: staging
          target_revision: HEAD
          namespace: mywebapp
          region: us-east-1
  template:
    metadata:
      name: portfolio-app-{{environment}}-{{region}}
    spec:
      destination:
        namespace: '{{namespace}}'
        server: '{{cluster_url}}'
      source:
        path: 'charts/portfolio-app'
        repoURL: 'https://github.com/Dhruvin4530/argoCD-Helm'
        targetRevision: '{{target_revision}}'
        helm:
          releaseName: portfolio-app
          valueFiles:
            - ./values/{{environment}}/values.yaml
      project: default
      syncPolicy:
        syncOptions:
        - CreateNamespace=true
```

> Note: You need to change the cluster\_url, repoURL, path, namespace & region as per yours

- Add the below code to `portfolio-app-prod.yaml`
```c
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: portfolio-app-prod-set
  namespace: argocd
spec:
  generators:
  - list:
      elements:
        - cluster_url: 'https://4C0CD6FC11D6F8998E30C3E96E55B8F1.gr7.us-east-2.eks.amazonaws.com'
          environment: production
          target_revision: HEAD
          namespace: mywebapp
          region: us-east-1
  template:
    metadata:
      name: portfolio-app-{{environment}}-{{region}}
    spec:
      destination:
        namespace: '{{namespace}}'
        server: '{{cluster_url}}'
      source:
        path: 'charts/portfolio-app'
        repoURL: 'https://github.com/Dhruvin4530/argoCD-Helm'
        targetRevision: '{{target_revision}}'
        helm:
          releaseName: portfolio-app
          valueFiles:
            - ./values/{{environment}}/values.yaml
      project: default
      syncPolicy:
        syncOptions:
        - CreateNamespace=true
```

> Note: You need to change the cluster\_url, repoURL, path, namespace & region as per yours

Now, our application code is ready. Now run the below commands to deploy the application.

```c
kubectl apply -f portfolio-app-prod.yaml
kubectl apply -f portfolio-app-dev.yaml
kubectl apply -f portfolio-app-stg.yaml
```
- You can see all the applications in the argoCD UI. We have not enabled the auto sync so you need to sync all the applications manually.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*DS7FCOZAQh25aLXu86BD_w.png)

Applications

- You can verify the resources from the backend as well.
```c
[dhruvinsoni@Dhruvins-MacBook-Pro applications (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$ kubectl get all -n mywebapp
NAME                              READY   STATUS    RESTARTS   AGE
pod/my-web-app-56d98fbf46-67rlm   1/1     Running   0          49m
pod/my-web-app-56d98fbf46-fr99w   1/1     Running   0          49m
pod/my-web-app-56d98fbf46-whthf   1/1     Running   0          49m

NAME                      TYPE           CLUSTER-IP     EXTERNAL-IP                                                              PORT(S)        AGE
service/my-web-app-prod   LoadBalancer   10.100.210.5   af90ce8fb84f44d1aba678ae8bf70ea9-479334478.us-east-2.elb.amazonaws.com   80:30412/TCP   49m

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-web-app   3/3     3            3           49m

NAME                                    DESIRED   CURRENT   READY   AGE
replicaset.apps/my-web-app-56d98fbf46   3         3         3       49m
[dhruvinsoni@Dhruvins-MacBook-Pro applications (⎈|dhsoni@prod-cluster.us-east-2.eksctl.io:N/A)]$
```
- The above are the resources for the production environment.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*RM2ahjCSBkbhy4pz15fE9g.png)

Production

- You can see 3 pods are running from the above snippet.

### Step 8: Change the target revision

- Now, we can also set the different target revision for each environment.
- We can create a branch or a tag in the git repository and apply the changes to them and we can define them in the argoCD application file so that it will fetch the update from them.
- Now, let’s say we want 2 replicas for our application in the development environment, So instead of making changes to `HEAD`, we can create a branch or a tag & change the replica count in the values file.
- I’ve created a branch called `dev-application-v0.1` and applied the changes to that branch.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GNL47ZvhPEPFG3B5vjWrJQ.png)

Branch

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5191d3DseyZIkc2qj2tFCw.png)

Changes

- Now, update the target revision in the argoCD application.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*nFPULv9bCKvwJAJkVPqaMQ.png)

Changes

- Now, Click on sync, add the branch name that you’ve created, and click on synchronize.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*e79H00CpQrloFHk7BGpJsg.png)

Sync to a different branch

- Now, you can see that 2 pods are running in the cluster.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ghb6dsCaB1VfRo-_fYqgxg.png)

Changes

- The best practice is to set the target revision to a different branch or a tag in the production environment so if we accidentally made some false changes to that branch then we can always revert the changes to the HEAD branch.
- Now you can perform different changes as per your need and argoCD will take care of the further action.
- You can find the entire code [**here**](https://github.com/Dhruvin4530/argoCD-Helm).
- Feel free to check out my other repositories as well.

Follow me on [**LinkedIn**](https://www.linkedin.com/in/dhruvinksoni/)

Follow for more stories like this 😁

## Stackademic 🎓

Thank you for reading until the end. Before you go:

- Please consider **clapping** and **following** the writer! 👏
- Follow us [**X**](https://twitter.com/stackademichq) **|** [**LinkedIn**](https://www.linkedin.com/company/stackademic) **|** [**YouTube**](https://www.youtube.com/c/stackademic) **|** [**Discord**](https://discord.gg/in-plain-english-709094664682340443)
- Visit our other platforms: [**In Plain English**](https://plainenglish.io/) **|** [**CoFeed**](https://cofeed.app/) **|** [**Venture**](https://venturemagazine.net/) **|** [**Cubed**](https://blog.cubed.run/)
- More content at [**Stackademic.com**](https://stackademic.com/)

[![Stackademic](https://miro.medium.com/v2/resize:fill:96:96/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_info--d1de7b1d36e6---------------------------------------)

[![Stackademic](https://miro.medium.com/v2/resize:fill:128:128/1*U-kjsW7IZUobnoy1gAp1UQ.png)](https://blog.stackademic.com/?source=post_page---post_publication_info--d1de7b1d36e6---------------------------------------)

[Last published 3 hours ago](https://blog.stackademic.com/building-a-high-throughput-payment-gateway-in-golang-348792191c63?source=post_page---post_publication_info--d1de7b1d36e6---------------------------------------)

Stackademic is a learning hub for programmers, devs, coders, and engineers. Our goal is to democratize free coding education for the world.

Senior Cloud Infrastructure Engineer | AWS | Automation | 2x AWS | CKA | Terraform Certified | k8s | Docker | CI/CD | [http://dhsoni.info/](http://dhsoni.info/)

## More from Dhruvin Soni and Stackademic

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d1de7b1d36e6---------------------------------------)