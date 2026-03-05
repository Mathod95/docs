---
title: Lifecycle management with Helm
source:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Helm-Basics/Lifecycle-management-with-Helm/page
---


# Lifecycle management with Helm

> This article explores how Helm simplifies lifecycle management in Kubernetes by packaging objects into releases for easy installation, upgrades, and rollbacks.

In this article, we explore how Helm simplifies lifecycle management in Kubernetes. Helm packages Kubernetes objects into releases, allowing you to install, upgrade, and roll back configurations with ease. Every time you install a chart, Helm creates a release that tracks all associated Kubernetes objects. This tracking enables seamless upgrades, downgrades, or uninstallations without interfering with other releases—all even if multiple releases are based on the same chart.

For instance, you can deploy two independent releases from the same WordPress chart:

```bash
$ helm install my-site bitnami/wordpress
$ helm install my-SECOND-site bitnami/wordpress
```

## Creating a New Release

Let's walk through creating a new release. In this example, we install an older version of the NGINX chart using the `--version` option:

```bash
$ helm install nginx-release bitnami/nginx --version 7.1.0

$ kubectl get pods
NAME                                    READY   STATUS             RESTARTS   AGE
nginx-release-687cdd5c75-ztn2n         0/1     ContainerCreating  0          13s
```

After installation, you might see that the running NGINX pod uses version 1.19.2—a version that, at this point, is considered outdated. Later on, if security vulnerabilities emerge or improvements are required, Helm can update your application without manually modifying each object.

## Upgrading a Release

Before upgrading, you can verify the current version by describing the pod:

```bash
$ kubectl describe pod nginx-release-687cdd5c75-ztn2n
Containers:
  nginx:
    Container ID:   docker://81bb5ad6b5...
    Image:          docker.io/bitnami/nginx:1.19.2-debian-10-r28
    Image ID:       docker-pullable://bitnami/nginx@sha256:2fcaf026b8acb7a...
    Port:           8080/TCP
    Host Port:      0/TCP
    State:          Running
```

To upgrade the release, execute the following command. In doing so, Helm replaces the old pod with a new one running the updated version:

```bash
$ helm upgrade nginx-release bitnami/nginx
Release "nginx-release" has been upgraded. Happy Helming!
NAME: nginx-release
LAST DEPLOYED: Mon Nov 15 19:25:55 2021
NAMESPACE: default
STATUS: deployed
REVISION: 2
TEST SUITE: None
NOTES:
  CHART NAME: nginx
  CHART VERSION: 9.5.13
  APP VERSION: 1.21.4
```

You can confirm the upgrade by checking the pod details again—the new pod should be running NGINX version 1.21.4.

## Reviewing Release History

Helm provides commands to inspect a release’s lifecycle. The `helm list` command displays summary information, including the current revision, while `helm history` offers detailed revision insights:

```bash
$ helm list
NAME            NAMESPACE       REVISION        STATUS      CHART              APP VERSION
nginx-release   default         2               deployed    nginx-9.5.13       1.21.4

$ helm history nginx-release
REVISION        UPDATED                         STATUS        CHART            APP VERSION     DESCRIPTION
1               Mon Nov 15 19:20:51 2021       superseded    nginx-7.1.0      1.19.2         Install complete
2               Mon Nov 15 19:25:55 2021       deployed      nginx-9.5.13     1.21.4         Upgrade complete
```

This detailed output helps you understand the progression of changes and enables efficient troubleshooting or auditing of configurations.

## Rolling Back a Release

If an upgrade introduces an unexpected change, you can easily roll back to a previous configuration. Unlike a simple revert, Helm creates a new revision that mirrors the state of the earlier release:

```bash
$ helm rollback nginx-release 1
Rollback was a success! Happy Helming!
```

After the rollback, a new revision reflecting the configuration of revision one is recorded, while the revision number continues to increase.

## Handling Upgrade Dependencies in Kubernetes Packages

When upgrading certain Kubernetes packages, additional parameters are sometimes required. For example, if you attempt to upgrade a WordPress release without supplying the current administrative passwords, you might encounter an error like the following:

```bash
$ helm upgrade wordpress-release bitnami/wordpress
Error: UPGRADE FAILED: template: wordpress/templates/NOTES.txt:83:4: executing "wordpress/templates/NOTES.txt" at <include "common.errors.upgrade.passwords.empty" ...>: 
    PASSWORDS ERROR: You must provide your current passwords when upgrading the release.
    Note that even after reinstallation, old credentials may be needed as they may be kept in persistent volume claims.
    Further information can be obtained at https://docs.bitnami.com/general/how-to/troubleshoot-helm-chart-issues/#credential-errors-while-upgrading-chart-releases
    'wordpressPassword' must not be empty, please add '--set wordpressPassword=$WORDPRESS_PASSWORD' to the command. To get the current value:
        export WORDPRESS_PASSWORD=$(kubectl get secret --namespace "default" wordpress-release -o jsonpath="{.data.wordpress-password}" | base64 --decode)
    'mariadb.auth.rootPassword' must not be empty, please add '--set mariadb.auth.rootPassword=$MARIADB_ROOT_PASSWORD' to the command. To get the current value:
        export MARIADB_ROOT_PASSWORD=$(kubectl get secret --namespace "default" wordpress-release-mariadb -o jsonpath="{.data.mariadb-root-password}" | base64 --decode)
    'mariadb.auth.password' must not be empty, please add '--set mariadb.auth.password=$MARIADB_PASSWORD' to the command. To get the current value:
        export MARIADB_PASSWORD=$(kubectl get secret --namespace "default" wordpress-release-mariadb -o jsonpath="{.data.mariadb-password}" | base64 --decode)
```

<Callout icon="triangle-alert" color="#FF6B6B">
  Helm requires access to specific administrative passwords to upgrade certain configurations, particularly for external services like databases. If these credentials are not provided during an upgrade, you will encounter errors. Consider implementing dedicated backup and restore strategies (often via Chart Hooks) for persistent data stored on volumes or in external databases.


## Summary

Helm's lifecycle management empowers you to:

* Install releases that package and manage multiple Kubernetes objects.
* Upgrade releases seamlessly in one command with robust tracking of configuration changes.
* Roll back to previous states by creating new revisions that reflect past stable configurations.
* Inspect release history to monitor and audit configuration modifications over time.

Now that you understand lifecycle management with Helm, try applying these concepts in your hands-on practice environment. Happy Helming!

For further information, explore:

* [Kubernetes Basics](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)
* [Helm Documentation](https://helm.sh/docs/)
* [Bitnami Charts](https://artifacthub.io/)