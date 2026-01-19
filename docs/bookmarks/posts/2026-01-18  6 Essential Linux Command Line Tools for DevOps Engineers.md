---
title: "6 Essential Linux Command Line Tools for DevOps Engineers"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/6-essential-linux-command-line-tools-for-devops-engineers-5cd23b578c50"
author:
  - "[[Piotr]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)

[Mastodon](https://fosstodon.org/@piotr1215)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-5cd23b578c50---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*4Zo3esuXAkz4RPzm)

Photo by Albert Dera on Unsplash

## Introduction

Practicing DevOps means juggling lots of various command line tools, `kubectl, helm and other *.ctls` from different `cloud native` projects. A good working knowledge of those command line tools is essential, but even more important are the command line tools used to \_glue\_ together the DevOps workflow.

Whether you’re managing deployments, automating tasks, or troubleshooting issues, a strong command of Linux tools is indispensable. As engineers, we constantly strive for efficiency and reliability, and the right set of tools can be a game-changer.

Linux commands are the backbone of many DevOps tasks. From configuration management to monitoring system performance, these commands streamline processes and enhance productivity. In this blog, we’ll explore six essential Linux commands that every DevOps engineer should know. These commands will not only simplify your day-to-day tasks but also empower you to handle complex scenarios with ease.

Let’s dive into these 6 essential Linux commands that will become your go-to tools in your DevOps toolkit.

## 1\. yq — Parsing and Modifying YAML

Yq is a lightweight and portable command-line YAML processor. More information: [yq](https://mikefarah.gitbook.io/yq/).

YAML files are ubiquitous in DevOps, especially for configuration management. The `yq` command is a powerful tool for parsing and modifying these files. Let’s inspect a deployment configuration file using `yq`.

```c
cat deploy-config.yaml
```
```c
app:
  name: mywebapp
  version: 1.0.0
  image: nginx:latest
  replicas: 3
database:
  image: postgres:13
  password: secretpassword
```

Now, let’s extract the image used by our app:

```c
yq '.app.image' deploy-config.yaml
```

This command will output:

```c
nginx:latest
```

## 2\. sed and grep — Updating Configuration

`Sed` allows to edit text in a scriptable manner. See also: `awk`, `ed`. More information: [sed](https://manned.org/man/sed.1posix).

When it’s time for a new release, updating configuration files is a routine task. The combination of `sed` and `grep` makes this process seamless. Here’s how you can update the version in our YAML file:

```c
sed -i 's/version: 1.0.0/version: 1.1.0/' deploy-config.yaml
```
```c
grep version deploy-config.yaml
```

Find patterns in files using regular expressions. More information: [GNU Grep Manual](https://www.gnu.org/software/grep/manual/grep.html).

`Sed` will update the version, we can quickly `grep` to confirm the change.

## 3\. curl — Checking Deployment Status

Transfers data from or to a server. Supports most protocols, including HTTP, FTP, and POP3. More information: [curl manpage](https://curl.se/docs/manpage.html).

Monitoring the status of your deployment APIs is crucial. The `curl` command allows you to check API statuses and parse the responses. For example, to check the latest release of Kubernetes:

```c
curl -s 'https://api.github.com/repos/kubernetes/kubernetes/releases/latest' | yq '.tag_name'
```

This will give us the tag name of the latest `Kubernets` release.

## 4\. tee — Logging Deployment Steps

Keeping logs of your deployment steps ensures you have a trail of what was executed. The `tee` command is perfect for this:

```c
echo 'Starting deployment process' | tee deployment.log
echo 'App version: 1.1.0' | tee -a deployment.log
cat deployment.log
```

## 5\. watch — Monitoring Deployment Progress

`Watch` executes a program periodically, showing output. More information: [watch](https://manned.org/watch).

The `watch` command is excellent for real-time monitoring. For example, by continuously watching the status of Kubernetes pods, you can stay updated on the deployment progress:

```c
watch kubectl get pods
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*DAMnzA5TSGnc1DLLyZtgpA.png)

> `kubectl` has its own `— watch` flag which we could use in this specific case:
> 
> `kubectl get pods — watch`

## 6\. journalctl — Viewing System Logs

Since most of the time you will work with Linux based virtual machines, `journald` can query the `systemd` journal. More information: [journalctl](https://manned.org/journalctl).

System logs are invaluable for troubleshooting. The `journalctl` command helps you view and filter these logs. For instance, to view logs for a specific service:

```c
journalctl -u nginx.service | tail
```

## Conclusion

Having those commands in your toolbelt and knowing when and how to use them can often mean a difference between spending 2 hours vs 30 min on a task. This is of course not an exhaustive list, but I find myself using those specific commands more often than others.

Do you agree with the list? Are there any other commands you find essential in your workflow?

## More from Piotr and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--5cd23b578c50---------------------------------------)