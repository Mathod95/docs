---
title: Working with Helm basics
source:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Helm-Basics/Working-with-Helm-basics/page
---

# Working with Helm basics

> This guide highlights key operations and commands available with Helm for managing deployments on Kubernetes efficiently.

With Helm installed, you can easily manage deployments on Kubernetes using the Helm command-line interface (CLI). This guide highlights key operations and commands available with Helm, ensuring you get started quickly and efficiently.

When you run the Helm command without parameters, it displays a comprehensive help menu that provides a quick reference for common actions. For example:

```bash
$ helm --help

The Kubernetes package manager

Common actions for Helm:
- helm search:     search for charts
- helm pull:       download a chart to your local directory to view
- helm install:    upload the chart to Kubernetes
- helm list:       list releases of charts

Usage:
  helm [command]

Available Commands:
  completion    generate autocompletion scripts for the specified shell
  create        create a new chart with the given name
  dependency    manage a chart's dependencies
  env           helm client environment information
  get           download extended information of a named release
  help          help about any command
  history       fetch release history
```

This help output serves as a handy reference; for instance, if you're considering rolling a release back to a previous version, you might initially search for a `helm restore` command. The help text quickly clarifies that the correct command for this operation is `helm rollback`.

## Exploring Subcommands

Helm provides a variety of subcommands to manage tasks, including repository-related functions. To see all commands related to chart repositories—such as adding, listing, or removing repositories—execute:

```bash
$ helm repo --help

This command consists of multiple subcommands to interact with chart repositories.
It can be used to add, remove, list, and index chart repositories.

Usage:
  helm repo [command]

Available Commands:
  add     add a chart repository
  index   generate an index file given a directory containing packaged charts
  list    list chart repositories
  remove  remove one or more chart repositories
  update  update information of available charts locally from chart repositories
```

For more detailed information on a specific operation, such as updating your local cache of chart repository data, you can view its help instructions:

```bash
$ helm repo update --help
Update gets the latest information about charts from the respective chart repositories.
Information is cached locally and used by commands like 'helm search'.

Usage:
  helm repo update [flags]

Aliases:
  update, up
```

<Callout icon="lightbulb" color="#1CB2FE">
  By frequently updating your local repository information, you ensure that you always have access to the latest charts available.


## Deploying a Real-World Application: WordPress

Helm simplifies the deployment of applications on Kubernetes. As a practical example, let's deploy a WordPress website using a prepackaged chart from the Bitnami repository. Follow these steps:

1. Add the Bitnami repository to your Helm configuration.
2. Deploy the WordPress application using the `helm install` command.

Here are the commands to execute:

```bash
$ helm repo add bitnami https://charts.bitnami.com/bitnami
"bitnami" has been added to your repositories

$ helm install my-release bitnami/wordpress
NAME: my-release
LAST DEPLOYED: Wed Nov 10 18:03:50 2021
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: wordpress
CHART VERSION: 12.1.27
APP VERSION: 5.8.1

** Please be patient while the chart is being deployed **
Your WordPress site can be accessed through the following DNS name from within your cluster:
my-release-wordpress.default.svc.cluster.local (port 80)
```

This streamlined process clearly demonstrates how Helm facilitates application deployments on Kubernetes. Typically, the chart’s README includes additional configuration details, allowing further customization of your deployment.

Once the chart is deployed, you can always confirm your active releases by listing them:

```bash
$ helm list
NAME        NAMESPACE   REVISION    UPDATED                                 STATUS      CHART                APP VERSION
my-release  default     1           2021-11-10 18:03:50.414174217 +0000 UTC    deployed    wordpress-12.1.27    5.8.1
```

To completely remove the deployed WordPress website and its associated Kubernetes objects, use the uninstall command:

```bash
$ helm uninstall my-release
release "my-release" uninstalled
```

## Managing Helm Repositories

Managing chart repositories with Helm is intuitive. You can add, list, remove, or update repositories using the `helm repo` commands. For example, to view your current repositories and update their information, run:

```bash
$ helm repo list
NAME      URL
bitnami   https://charts.bitnami.com/bitnami

$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "bitnami" chart repository
Update Complete. Happy Helming!
```

This process is akin to updating package manager repositories on Linux systems, ensuring that your local cache of available charts is always up-to-date.

<Callout icon="lightbulb" color="#1CB2FE">
  Explore our labs to experiment with these Helm CLI operations in your Kubernetes environment. This hands-on experience will help solidify your understanding.


That’s all for now. Happy Helming, and see you in the next article!