---
title: Customizing chart parameters
source:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Helm-Basics/Customizing-chart-parameters/page
---

# Customizing chart parameters

> Learn how to customize chart parameters during WordPress installation using Helm, including command line overrides, custom values files, and modifying built-in configurations.

In this guide, you’ll learn how to customize chart parameters during installation with Helm. By default, when installing WordPress using the Bitnami Helm chart, the deployment leverages the default settings provided in its values.yaml file. For example, executing the command below:

```bash
$ helm install my-release bitnami/wordpress
```

will deploy WordPress with the blog name set to "User's Blog!" since that is the value defined in the values.yaml file. The chart automatically configures these defaults as environment variables for the application.

## Using the Command Line to Override Defaults

Sometimes you may want to change specific default settings like the blog name or email address. Rather than modifying the values.yaml file directly, you can use the `--set` option on the command line to override these values. For instance, to change the blog name, run:

```bash
$ helm install --set wordpressBlogName="Helm Tut" my-release bitnami/wordpress
```

You can chain multiple `--set` options to override any parameter from the default configuration. Below is an excerpt from the default values for reference:

```yaml
image:
  registry: docker.io
  repository: bitnami/wordpress
  tag: 5.8.2-debian-10-r0
wordpressUsername: user
wordpressPassword: ""
existingSecret: ""
wordpressEmail: user@example.com
wordpressFirstName: WordPress user first name
wordpressBlogName: User's Blog!
```

The parameters passed on the command line will take precedence over the default values specified in the file.

## Using a Custom Values File

For scenarios where multiple settings need to be overridden, it may be more efficient to create your own custom values file. Follow these steps:

1. Create a file named `custom-values.yaml` with your desired configuration:

   ```yaml
   wordpressBlogName: Helm Tutorials
   wordpressEmail: john@example.com
   ```

2. Install the chart with your custom values file using the following command:

   ```bash
   $ helm install --values custom-values.yaml my-release bitnami/wordpress
   ```

This approach directs Helm to load your custom settings, thereby overriding those defined in the default values.yaml file.

## Modifying the Built-in values.yaml Directly

For a more permanent configuration change, you might choose to modify the chart's built-in values.yaml file. To do this, you first need to pull the chart locally. Begin by downloading the chart archive:

```bash
$ helm pull bitnami/wordpress
```

You can then extract the files using one of two methods:

* Unarchive the file manually
* Use the `--untar` option:

  ```bash
  $ helm pull --untar bitnami/wordpress
  ```

After extracting, you will find a directory (named `wordpress`) containing all chart files, including `values.yaml`. Here is a sample view of its contents:

```yaml
image:
  registry: docker.io
  repository: bitnami/wordpress
  tag: 5.8.2-debian-10-r0
##
## @param wordpressUsername WordPress username
##
wordpressUsername: user
## @param wordpressPassword WordPress user password
## Defaults to a random 10-character alphanumeric string if not set
wordpressPassword: ""
## @param existingSecret
##
existingSecret: ""
## @param wordpressEmail WordPress user email
##
wordpressEmail: user@example.com
## @param wordpressFirstName WordPress user first name
##
## @param wordpressBlogName Blog name
##
wordpressBlogName: User's Blog!
```

Modify the file using any text editor to adjust the desired values. When ready, install the modified chart locally by specifying the chart directory:

```bash
$ helm install my-release ./wordpress
```

Below is an example of how your customized local `values.yaml` file might appear:

```yaml
image:
  registry: docker.io
  repository: bitnami/wordpress
  tag: 5.8.2-debian-10-r0
  ## @param wordpressUsername WordPress username
  ##
  wordpressUsername: user
  ## @param wordpressPassword WordPress user password
  ## Defaults to a random 10-character alphanumeric string if not set
  wordpressPassword: ""
  ## @param existingSecret
  existingSecret: ""
  ## @param wordpressEmail WordPress user email
  wordpressEmail: user@example.com
  ## @param wordpressFirstName WordPress user first name
  ## @param wordpressBlogName Blog name
  wordpressBlogName: User's Blog!
```

<Callout icon="lightbulb" color="#1CB2FE">
  When installing from a local chart directory, the Helm installation command accepts both a repository chart name or a file path.


## Summary

In this article, we explored three effective methods to customize your WordPress deployment using Helm:

1. Overriding default values with command line parameters using the `--set` option.
2. Employing a custom values file via the `--values` option.
3. Modifying the built-in `values.yaml` file by pulling and editing the chart locally.

Each method is designed to tailor the deployment to meet your specific configuration requirements, ensuring that the installation aligns perfectly with your environment.

For more detailed information and additional practices, refer to the official [Helm Documentation](https://helm.sh/docs/).