---
title: "How to create ArgoCD Applications Automatically using ApplicationSet? “Automation of the Gitops”"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://amralaayassen.medium.com/how-to-create-argocd-applications-automatically-using-applicationset-automation-of-the-gitops-59455eaf4f72"
author:
  - "[[AmrAlaaYassen]]"
---
<!-- more -->

[Sitemap](https://amralaayassen.medium.com/sitemap/sitemap.xml)

## What will we discuss today?

In this article we will discuss ArgoCD ApplicationSet and how to use ApplicationSet generators to automatically create ArgoCD Applications templates using the flexibility of the ApplicationSet controller to our own benefit, we will give examples for some of ApplicationSet generators and at the end of the article, we will implement a very specific use case and give final opinions and conclusions.

## Introduction

One of the very popular tools in the Kubernetes ecosystem is ArgoCD, so let’s briefly explain what ArgoCD has been built for, it applies the theoretical parts of the GitOps approach and brings it to the practical world through a tool built with a wonderful UI which makes everyone’s life easier, the tool simply watches over a GitHub Repository which defines the desired state to be deployed to our Kubernetes cluster and continuously compare this desired state with the actual state deployed on the cluster if there’s a difference between the stats, the tool has a set of well-defined actions to take (we define those actions) to handle those differences, as a result, we will have a defined state on GitHub Repository applied to our Kubernetes cluster, to know more about ArgoCD I highly recommend to take a look over the [documentation](https://argo-cd.readthedocs.io/en/stable/).

## The problem that ApplicationSet tries to solve.

ArgoCD will give you the opportunity to version control your cluster deployments, configurations and Kubernetes objects by monitoring a GitHub repository (the source of truth) and applying it to the cluster.

you can do this by defining an ArgoCD application manifest like the one below

Simple ArgoCD Application

Simple ArgoCD Application definition

This should create an ArgoCD Application like below:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*NfG8eu17ybGbbLSq8vOQPg.png)

ArgoCD Application UI

This is for a single application, let’s assume you are working in a microservice architecture, then you will have to create a new ArgoCD application for every microservice, even if you are using tools like kustomize or Helm for sure you will have different values for every deployment which will lead you to create a separate application for each, and as the applications number grows it becomes very hard and doesn’t make any sense to handle that very large number of ArgoCD Applications manifests.

**Here comes ApplicationSet in place, it makes it very easy to automatically create Application manifests using its generators.**

## What is ArgoCD ApplicationSet?

==ApplicationSet is a Kubernetes CRD (Custom Resource Definition) that helps us to automatically create ArgoCD Applications and adds more flexibility to manage those applications and provide a single place to make changes to all of your applications==, whether you have different destinations for those applications or different configuration values it will automatically handle setting those values for your Applications.

Alongside ApplicationSet CRD, comes the ApplicationSet controller that adds support to ApplicationSet CRD, the controller works side by side with an existing ArgoCD installation, you can consider ApplicationSet as a plugin or extension that makes handling Applications easier.

## How ApplicationSet controller solves the problem.

While an ArgoCD application holds a Git repository for the desired manifests and a Kubernetes cluster destination, An ApplicationSet definition holds the generators that will automatically create ArgoCD applications with different values for different sources and destinations, ApplicationSet creates an application using an application template defined in a YAML format and fills that template with the outputted values from the generators.

so it’s best to use ApplicationSet when you have too many applications to handle using ArgoCD and those applications are similar in a way to be able to use the generators in your favor.

The image below show a usecase where you have Kubernetes tools that you want to be deployed in all Kubernetes clusters that you work on, for example, a Prometheus operator that you want it to be deployed on all clusters, in a normal scenario you will have to create 7 different Application Manifests pointing to the same Git repository as the source and different clusters as the destination, but that could be handled using a Single ApplicationSet Manifests

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*xt98FAJrqxu5dQ3yhZ2ZRg.png)

Single app — multiple clusters

## ApplicationSet generators and use cases for every generator.

There are lots of ApplicationSet generators we will mention the most important ones and usecases for each but I advice to take a look at [the generators documentation](https://argocd-applicationset.readthedocs.io/en/stable/Generators/)

- **List Generator**

The list generator simply creates ArgoCD application templates given a list of elements that we define the values for, so let’s take an example that we have an application that we need to deploy to a list of namespaces (e.g dev, test, uat), the ApplicationSet manifest will be like:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*xcdCLa2MTPwi5Fi9CHjYVQ.png)

ApplicationSet List Generator

The above ArgoCD ApplicationSet manifest deploys 3 different ArgoCD apps `dev-color-app`,`test-color-app`, and `uat-color-app` to 3 different namespaces dev, test, and uat on ArgoCD UI you will see three applications created for you on the fly.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*hAzUpJlDmrYA7WP6gOEx3A.png)

Applications Created by ApplicationSet

here comes the magic of the ApplicationSet generators it has created all needed applications using a very simple ApplicationSet manifest file.

- **Git Generators**

The git generator has two types under the git generator tree:

1. **Git Directory Generator.**

It creates variables based on the directory structure in a specific Git repository and then uses different paths/subPaths as variables to use them in the ArgoCD Application template, this generator will help you to automatically create applications if you have a structure where you put every application manifests in a single directory in the same Git repository, or you have a common helm chart repository for all your applications or environments.

2\. **Git File Generator.**

It creates variables using the contents of a file (JSON or YAML format) from a defined Git repository, the contents of the file may include different destinations or clusters to deploy the application to.

In the example below we will use the Git-Dir generator to create deployments for some Argo projects like Argo workflows, Argo rollouts, and Argo image updater and we want each of these applications to be deployed on a different namespace on our cluster that has been created to manage only Argo projects on it, ApplicationSet definition will be something like below:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*w3rKX9kTC_tK1HqP2d88Tw.png)

ApplicationSet Git-Dir Generator

this ApplicationSet manifest will create 3 ArgoCD Applications using directories names and paths as variables to be used in the Application template in the ApplicationSet manifest.

in the generator section above we point to a Git repository to get the directories from and specify the path that includes those directories [the path](https://github.com/AmrAlaaYassen/ArgoCD-ApplicationSet-Demo/tree/main/git-dir-generator-example/argo-projects) specified above includes 3 sub-directories

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*FGCvrMmYNBfAdgJG4W9sWA.png)

Directory structure

this will create 3 variables for us to be used in the template section above and those 3 variables are `git-dir-generator-example/argo-projects/argo-image-updater`, `git-dir-generator-example/argo-projects/argo-rollouts`, and `git-dir-generator-example/argo-projects/argo-workflows` each one of these variables has a child value which we refer to as `path.basename` that has the value of `basename` of the path (the right-most pathname) in our case will be argo-image-updater or argo-rollouts or argo-workflows.

we will use names of directories to specify different destinations (different namespaces in our case) to deploy our applications, as a result, we will have 3 ArgoCD applications like below:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*sSCPZ1obdiFF4r5QVLm0Lw.png)

Git-Dir Applications

**Note different namespaces are specified.**

## Demo

In this demo we have advanced usage of the git-dir generator

**usecase:** let’s assume that we have a Git repository that contains our deployments using a common helm chart like below:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*_avHbXGL6npVncacV0eKlw.png)

Directory Structure (2)

as you see here we have a common helm chart that will be used to deploy all of our applications and for each application we have different environments directories that include different **values.yaml** file that specifies the needed values for each environment (prod, qa, stating), we want to name our application in the following naming convention `appname-environment` and we want to select different values files for each application based on the environment that we will make deployment for, in a normal case scenario using the above structure you will have to create 9 different ArgoCD Application manifests to specify different values files for helm to use and for each application and the application different environment, but using ApplicationSet Generator you will only create a single manifest file as below:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*g-H010vGGOxPb6BBRQLIiw.png)

Demo ApplicationSet

This ApplicationSet manifest will create the 9 applications manifests we mentioned above automatically using the git-dir generator with paths and sub-paths pattern

`demo/configs/*/*` here we use the directories under the configs folder and the subdirectories of the directories under the config folder so we will have 9 different values generated form the above generator

`demo/config/app-hulk/prod` `demo/config/app-hulk/qa` `demo/config/app-hulk/staging` and the same for `app-iron` and `app-spider` this will help us to specify different values files for those different apps, the diagram below explains more

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*SQmLFFqXMUx-xw1HiG-01w.png)

Demo Example Illustration

as a result, you will see in Argo UI the below

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*NR_PlZllZEZNoZ-_ZZgaJw.png)

ArgoCD Demo Example UI

This demo introduces a concept called “mono-repository” where you manage all of your ArgoCD Applications from a single Git Repository you can find more about that concept [here](https://argo-cd.readthedocs.io/en/stable/operator-manual/high_availability/#monorepo-scaling-considerations), if you face issues using this approach and want some way to work it around comment below in the comments this may be our next blog.

**Repository includes the examples and demos we discussed in this blog**## [GitHub - AmrAlaaYassen/ArgoCD-ApplicationSet-Demo](https://github.com/AmrAlaaYassen/ArgoCD-ApplicationSet-Demo?source=post_page-----59455eaf4f72---------------------------------------)

[

github.com

](https://github.com/AmrAlaaYassen/ArgoCD-ApplicationSet-Demo?source=post_page-----59455eaf4f72---------------------------------------)

## Conclusions and Opinions

ArgoCD ApplicationSet has other amazing generators like Matrix Generator a matrix generator combines the variables generated from 2 different ApplicationSet generators, it generates different ArgoCD Applications for every combination of the generated values, this generator gives us the flexibility to use different generators features and use the values generated from each generator.

ArgoCD is already a very powerful tool that makes it really easy to manage your deployments using the GitOps approach however it lacks some kind of automation here’s where ArgoCD ApplicationSet comes in place and introduces its way around creating ArgoCD Applications Manifest automatically if you are using ArgoCD ApplicationSet I’d like to hear more about your use case and what is the challenge that you have faced and how it’s been solved.

## More from AmrAlaaYassen

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--59455eaf4f72---------------------------------------)