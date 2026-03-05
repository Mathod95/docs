---
title: A quick note about Helm2 vs Helm3
source:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/2025-Updates-Helm-Basics/A-quick-note-about-Helm2-vs-Helm3/page
---

# A quick note about Helm2 vs Helm3

> This article reviews the differences between Helm 2 and Helm 3, focusing on architectural changes and new features in Helm 3.

Helm has evolved significantly over the years. Understanding the differences between Helm 2 and Helm 3 is essential for anyone working with Kubernetes charts and infrastructure. In this guide, we review Helm’s evolution, detail the architectural changes between Helm 2 and Helm 3, and explain an important new feature introduced in Helm 3.

## A Brief History of Helm

Helm's journey began with the release of Helm 1.0 in February 2016. It was soon followed by Helm 2.0 in November 2016, and later by Helm 3.0 in November 2019. As Kubernetes matured, Helm evolved to take full advantage of new features and best practices within the ecosystem.

<Frame>
  ![The image shows a timeline of Helm's version history, with releases 1.0 in February 2016, 2.0 in November 2016, and 3.0 in November 2019.](https://kodekloud.com/kk-media/image/upload/v1752869631/notes-assets/images/CKA-Certification-Course-Certified-Kubernetes-Administrator-A-quick-note-about-Helm2-vs-Helm3/frame_30.jpg)
</Frame>

## Architectural Changes: Tiller vs. Direct Kubernetes Integration

Helm uses a CLI client installed on your local machine to manage applications on your Kubernetes cluster. In Helm 2, a component called Tiller was necessary because early Kubernetes versions lacked role-based access control (RBAC) and custom resource definitions (CRDs). The CLI communicated with Tiller, which then executed the required operations on the cluster.

<Frame>
  ![The image illustrates Helm 2 architecture, showing the interaction between Helm CLI and Tiller, with notes on Role-Based Access Control and Custom Resource Definitions.](https://kodekloud.com/kk-media/image/upload/v1752869632/notes-assets/images/CKA-Certification-Course-Certified-Kubernetes-Administrator-A-quick-note-about-Helm2-vs-Helm3/frame_100.jpg)
</Frame>

<Callout icon="triangle-alert" color="#FF6B6B">
  Tiller ran with high privileges ("God mode") by default. This increased the risk of unrestricted actions within the cluster from any user having access to Tiller.


With advancements in Kubernetes—especially the introduction of RBAC and improved CRDs—the extra layer provided by Tiller became unnecessary. Helm 3 eliminates Tiller entirely, enabling the CLI to interact directly with Kubernetes, simplifying the architecture and enhancing security through native RBAC controls.

<Frame>
  ![The image illustrates Helm 3 architecture, showing a Helm CLI interacting with Kubernetes, emphasizing role-based access control and custom resource definitions.](https://kodekloud.com/kk-media/image/upload/v1752869633/notes-assets/images/CKA-Certification-Course-Certified-Kubernetes-Administrator-A-quick-note-about-Helm2-vs-Helm3/frame_180.jpg)
</Frame>

## Three-Way Strategic Merge Patch in Helm 3

One of the most significant improvements in Helm 3 is the integration of a three-way strategic merge patch mechanism. Think of this as a snapshot feature for your deployments. When you install a chart—say, a full-blown WordPress website—Helm creates revision 1. Upgrading the release with a new chart version creates an additional revision.

For example, consider the following sequence:

```bash
$ helm install wordpress
$ helm upgrade wordpress
```

Suppose the initial installation specifies the container image as:

```yaml
containers:
  - image: wordpress:4.8-apache
```

After upgrading, the container image might be updated to:

```yaml
containers:
  - image: wordpress:5.8-apache
```

Each significant action (installation, upgrade, or rollback) creates a new revision. This revision acts as a snapshot of your deployment’s state. If a rollback is needed, Helm compares the live configuration with the targeted revision and reverts the changes:

```bash
$ helm rollback wordpress
```

During the rollback process, Helm 3 performs a three-way comparison between the live state, the current chart, and the previous revision. This ensures that any manual changes—like those made with `kubectl set image`—are detected and addressed accordingly.

Consider this scenario:

1. A WordPress deployment is installed with Helm, creating revision 1.

2. A user manually updates the application image using:

   ```bash
   kubectl set image wordpress wordpress=5.8-apache
   ```

3. Since this manual change wasn't made via Helm, no new revision is recorded.

4. When a rollback command is issued, Helm 3 compares the live state with the configuration from revision 1. Unlike Helm 2, which would ignore such manual modifications, Helm 3 detects the discrepancies and reverts the application to the previous configuration.

<Frame>
  ![The image compares Helm 2 and Helm 3, highlighting the presence of Tiller in Helm 2 and 3-Way Strategic Merge Patch in Helm 3.](https://kodekloud.com/kk-media/image/upload/v1752869634/notes-assets/images/CKA-Certification-Course-Certified-Kubernetes-Administrator-A-quick-note-about-Helm2-vs-Helm3/frame_230.jpg)
</Frame>

## Upgrades and Preserving Manual Changes

A notable advantage of Helm 3 is how it handles upgrades. In Helm 2, manual changes made directly to Kubernetes objects were often lost during upgrades because they were not reflected in the chart specifications. Helm 3, however, examines both the live state and the chart definitions. This dual-check approach ensures that any additions or modifications made outside of Helm commands are maintained during the upgrade process.

<Callout icon="lightbulb" color="#1CB2FE">
  Leveraging Kubernetes RBAC in Helm 3 not only simplifies the deployment process but also reinforces security by enforcing least-privilege access policies.


## Conclusion

Helm 3 brings several key improvements over Helm 2:

* Removal of Tiller simplifies the underlying architecture and improves security.
* The introduction of a three-way strategic merge patch mechanism creates reliable snapshots for each deployment revision.
* Enhanced upgrade and rollback processes ensure that both Helm-managed configurations and manual changes are preserved.

This concludes our discussion on the primary differences between Helm 2 and Helm 3. In the next lesson, we will explore additional Helm 3 features and detailed usage guidelines to help you harness its full potential in your Kubernetes environment.