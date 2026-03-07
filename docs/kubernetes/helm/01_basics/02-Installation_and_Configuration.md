---
title: Installation and configuration
source:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Helm-Basics/Installation-and-configuration/page
---

# Installation and configuration

> This article provides an overview of installing Helm, the package manager for Kubernetes, specifically on Linux systems.

In this lesson, we provide an overview of installing Helm, the package manager for Kubernetes. Helm simplifies the deployment and management of applications on Kubernetes. Before you begin, ensure that you have a fully functional Kubernetes cluster and that the kubectl command-line tool is properly configured on your local machine. Also, verify that your kubeconfig file contains the correct credentials to interact with your Kubernetes cluster.

Helm is compatible with Linux, Windows, and macOS. This guide focuses on installing Helm on Linux systems.

<Callout icon="lightbulb" color="#1CB2FE">
  Ensure your Kubernetes cluster is up and running, and that you have installed and properly configured kubectl on your system.


## Installing Helm on Linux

### Using Snap

If your Linux system supports Snap, you can install Helm using the following command:

```bash
sudo snap install helm --classic
```

The `--classic` flag allows Helm to access necessary files (like your kubeconfig) by relaxing sandbox restrictions.

### For apt-based Systems (Debian/Ubuntu)

Follow these steps to add the Helm repository and install Helm on systems that use apt:

1. Add the Helm GPG key:

   ```bash
   curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
   ```

2. Install HTTPS support for apt:

   ```bash
   sudo apt-get install apt-transport-https --yes
   ```

3. Add the Helm repository:

   ```bash
   echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
   ```

4. Update the package index:

   ```bash
   sudo apt-get update
   ```

5. Install Helm:

   ```bash
   sudo apt-get install helm
   ```

### For PKG-Supported Systems

If your system uses the PKG package manager, install Helm with this command:

```bash
pkg install helm
```

<Callout icon="triangle-alert" color="#FF6B6B">
  Always refer to the official Helm documentation for the most up-to-date installation instructions.


Now it's time to practice installing Helm in your lab environment. For additional details, visit the [Helm documentation](https://helm.sh/docs/).