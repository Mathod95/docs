# GitOps Introduction

## What is GitOps

GitOps is an operational framework that leverages Git as the single source of truth for managing both infrastructure and application code. It extends the principles of Infrastructure as Code, enabling automated deployments and rollbacks by controlling the entire code delivery pipeline through Git version control.

### GitOps Workflow
Developers begin by committing their changes to a centralized Git repository. Typically, they work in feature branches created as copies of the main codebase. These branches allow teams to develop new features in isolation until they are deemed ready. A Continuous Integration (CI) service automatically builds the application and runs unit tests on the new code. Once tests pass, the changes undergo a review and approval process by relevant team members before being merged into the central repository.

The final step in the pipeline is Continuous Deployment (CD), where changes from the repository are automatically released to Kubernetes clusters.

The image illustrates the GitOps workflow, showing the integration of infrastructure, configuration, and application code into a Git repository, followed by continuous integration (CI) and continuous deployment (CD) processes to a Kubernetes cluster. It also depicts a branching and merging process in Git.

At the heart of GitOps is the concept of a declaratively defined state. This involves maintaining your infrastructure, application configurations, and related components within one or more Git repositories. An automated process continuously verifies that the state stored in Git matches the actual state in the production environment. This synchronization is managed by a GitOps operator running within a Kubernetes cluster. The operator monitors the repository for updates and applies the desired changes to the cluster—or even to other clusters as needed.

When a developer merges new code into the application repository, a series of automated steps is triggered: unit tests are run, the application is built, a Docker image is created and pushed to a container registry, and finally, the Kubernetes manifests in another Git repository are updated.

The image illustrates a GitOps workflow, showing the process from application code merging and continuous integration to deploying Kubernetes manifests, with GitOps operators ensuring the desired state matches the actual state in production environments.

The GitOps operator continuously compares the desired state (as defined in Git) with the actual state in the Kubernetes cluster. If discrepancies are found, the operator pulls the necessary changes to ensure that the production environment remains aligned with the desired configuration.

The image illustrates a GitOps workflow, showing the process from application code repository through continuous integration to Kubernetes deployment, highlighting the synchronization between desired and actual states.

!!! Note "Ease of Rollbacks"
    One of the key benefits of GitOps is the seamless rollback process. Since the entire configuration is maintained in Git, reverting to a previous state is as simple as executing a git revert command. The GitOps operator detects this change and automatically rolls back the production environment to match the desired state.

The image illustrates a GitOps workflow, showing the process from application code repository through continuous integration to Kubernetes deployment, highlighting the synchronization between desired and actual states.

---

## GitOps Principles

GitOps Principles
In this lesson, we will explore the core principles of GitOps—an approach to continuous deployment that leverages Git as the single source of truth for infrastructure and application state. The GitOps methodology is built upon four foundational principles.

!!! note "Remember"
    GitOps ensures system consistency and reduces human error by enforcing a declarative model of infrastructure management.

**Declarative vs. Imperative Approach:** The first principle stresses a declarative methodology over an imperative one. In the declarative model, the entire system—including both infrastructure and application manifests—is described in a desired state. This contrasts with the imperative approach, where specific commands are executed sequentially to change the system state. Relying on the imperative style can complicate reconciliation since it does not maintain a comprehensive record of the system's intended state.

**Storing the Desired State in Git:** The second principle mandates that all declarative files, which represent the desired state of the system, be stored in a Git repository. Git not only offers powerful version control capabilities but also preserves immutability. Storing the desired state in Git makes it the definitive source of truth for system configuration. Any changes pushed to Git are automatically recognized and applied across the system.

**Automated Application of the Desired State via GitOps Operators:** The third principle involves using GitOps operators—software agents that continuously monitor Git for updates. Once they detect changes, these operators automatically retrieve the desired state from the repository and apply it across one or more clusters or environments. Consider the following deployment manifest example that a GitOps operator might manage:

```yaml linenums="1" title="deployment.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
```

This operator can run in a single cluster and propagate configuration changes to other clusters as necessary, ensuring uniformity and scalability.

**Reconciliation and Self-Healing:** The final principle centers on continuous reconciliation. GitOps operators maintain a self-healing system by constantly checking for discrepancies between the actual state of the system and the desired state stored in Git. They execute this process through three key steps:

- **Observe**: Monitor the Git repository for updates.
- **Diff**: Compare the desired state from Git with the current state of the cluster.
- **Act**: Reconcile any differences by updating the system to reflect the declared desired state.

This ongoing reconciliation loop minimizes the risk of configuration drift and helps maintain a robust, error-resistant system.

By understanding and applying these GitOps principles, you can ensure your infrastructure remains consistent, scalable, and resilient to changes.

Thank you.

---

## DevOps vs GitOps

This lesson dives into the contrasting approaches of DevOps and GitOps—two methodologies that share common goals but differ significantly in execution and toolsets.

GitOps leverages containerization technologies such as OpenShift and Kubernetes. It uses Git as the single source of truth for both infrastructure and deployments. In comparison, DevOps is a broader methodology that can be applied to diverse application environments and workflows.

DevOps Pipeline
A typical DevOps pipeline operates as follows:

A developer writes code in an Integrated Development Environment (IDE) and commits it to a source code management system.
A Continuous Integration (CI) process detects the commit, runs tests, and builds the necessary artifacts.
The pipeline then creates a container image and publishes it to a container repository.
Finally, the Continuous Deployment (CD) process connects to a Kubernetes cluster and uses a command-line tool such as kubectl (with imperative commands) to push updates directly to the cluster.
Key Point

In DevOps, the deployment is initiated by pushing changes directly into the cluster.

GitOps Pipeline
While the CI processes in a GitOps pipeline mirror those of DevOps up to the point of publishing the container image, the deployment process is distinct:

Two separate Git repositories are maintained: one dedicated to application code and another for Kubernetes manifests.
Once the image is published, the manifest repository is cloned and updated—typically the new image name is specified. These changes are then committed and pushed.
The pipeline automatically raises a pull request for the manifest repository. A team member reviews the pull request, suggests adjustments if necessary, and merges the changes upon approval.
A GitOps operator, running within the Kubernetes cluster, continuously monitors the repository. When changes are detected, it synchronizes the cluster state to match the repository configuration.
Takeaway

In a GitOps pipeline, the deployment operator pulls changes from the repository and applies them to the cluster, contrasting with the push-based approach in traditional DevOps workflows.

The image below illustrates a side-by-side comparison of the CI/CD pipelines in both DevOps and GitOps. It highlights the key steps—ranging from code development to deployment—and emphasizes the differences in update management and application.

The image compares DevOps and GitOps CI/CD pipelines, illustrating the processes of continuous integration and deployment for each approach. It highlights the steps from code development to deployment, showing differences in how updates are managed and applied.

Conclusion
This article compared DevOps and GitOps pipelines by detailing the key stages of each process. Understanding these differences is essential for choosing the right methodology for your projects. In the next lesson, we will explore the advantages and challenges associated with each approach.

---

## Push vs Pull

In this article, we explore the differences between push-based and pull-based deployment strategies for Kubernetes clusters. We will examine their benefits, challenges, and use cases, helping you determine the best approach for your environment.

Push-Based Deployment
Push-based deployment is commonly used in CI/CD pipelines. With this approach, the application code goes through various stages within the CI pipeline before updates are pushed directly to the Kubernetes cluster.

Key Characteristics
The CI system requires read-write access to the Kubernetes cluster, which means Kubernetes credentials are stored in the CI system outside the cluster. This arrangement may introduce potential security risks.
Typically, the CI system has read-only access to the Git repository and read-write access to the container registry, while the Kubernetes cluster itself only has read-only access to the registry.
Deployments can leverage a variety of plugins and tools. For instance, Jenkins can use multiple plugins or approaches, and Helm plugins further simplify the deployment of Helm charts.
Security Consideration

Storing Kubernetes credentials in the CI system exposes a potential security risk, as these credentials grant read-write access to the cluster.

Challenges
The deployment configuration is tightly coupled with the CI system. Migrating from one CI platform to another (for example, switching from Jenkins to a different platform) often requires reworking many deployment configurations.
Embedding cluster credentials in the CI system increases the risk of unauthorized access if the CI system is compromised.
Pull-Based Deployment
Pull-based deployment, frequently associated with GitOps, employs an operator running within the Kubernetes cluster. This operator monitors for changes—either in a container registry for new images or in a Git repository for updated manifests—and then autonomously deploys those changes.

Key Characteristics
The CI/CD system only needs read-write access to the container registry, without requiring direct access to the Kubernetes cluster.
Deployments are executed internally from within the cluster, enhancing security by minimizing external access.
GitOps operators are particularly supportive of multi-tenant environments, allowing teams to manage multiple repositories and namespaces. For example, different teams can maintain separate Git repositories and corresponding namespaces for their deployments.
Secrets can be securely managed by encrypting them using tools like HashiCorp Vault or Bitnami Sealed Secrets. These encrypted secrets are stored in Git or decrypted during the deployment process.
GitOps operators can monitor container registries for newer image versions and automatically trigger deployments of the latest images.
Secret Management

While GitOps encourages declarative management—including secrets—in Git, the process often requires additional tools and steps (e.g., encryption and decryption) to ensure security, especially with Helm chart deployments.

Challenges
Managing secrets and configurations can be more complex compared to the push-based model. Although GitOps principles promote a declarative approach, handling encrypted credentials adds an extra layer of complexity.
Visual Comparison
The image compares push-based and pull-based deployment methods for Kubernetes, highlighting their processes, access permissions, and advantages or disadvantages.

The image compares push-based and pull-based deployment methods for Kubernetes, highlighting their processes, advantages, and disadvantages. It includes diagrams and lists of pros and cons for each approach.

Summary
Deployment Strategy	Pros	Cons
Push-Based	- Direct integration with CI/CD pipelines<br>- Flexible deployment configurations using various tools and plugins	- Requires CI system to have cluster credentials<br>- Tightly coupled to specific CI systems, making migrations challenging
Pull-Based (GitOps)	- Enhanced security by limiting external access<br>- Supports multi-tenant environments and automated image updates	- More complex secret management<br>- Additional tools required for encrypting and decrypting configurations
In summary, push-based deployment strategies simplify certain aspects of automation but may lead to inflexibility and potential security issues. In contrast, pull-based (GitOps) deployments enhance internal management and security at the cost of added complexity in handling secrets and configuration management.

Explore more about these methodologies in the Kubernetes Documentation and learn how GitOps can revolutionize your deployment pipeline.

---

## GitOps Feature Set

GitOps Feature Set
This article provides an in-depth overview of GitOps features and their associated use cases, demonstrating how storing every configuration declaratively in a Git repository can transform your deployment workflows.

Every configuration is stored declaratively in Git, which serves as the single source of truth containing the full desired state of the system. This approach not only simplifies application rollbacks—enabling a quick recovery with a simple git revert—but also ensures that audit trails are automatically available through pull requests and commit histories.

Key Benefit

Storing configurations in Git allows teams to effortlessly rollback to a previous state and maintain a complete audit trail for all changes.

Automated CI/CD and Continuous Deployment
CI/CD automation is a cornerstone of GitOps. By leveraging automation:

Building, testing, and deployment tasks are triggered automatically based on the desired state stored in Git.
Continuous deployment becomes seamless and consistent, as applications are deployed automatically to clusters without manual intervention.
Extending GitOps to Infrastructure and Cluster Resources
Once GitOps is established for application deployment, extend these practices to manage both cluster resources and Infrastructure as Code. For instance, in Kubernetes environments, you can manage various resources including:

Secrets management
Networking agents and service mesh configurations
Database provisioning
Prometheus monitoring
The core principle here is automatic reconciliation: the system continuously compares the desired state in Git with the actual state in the cluster. If any unintended changes occur, the system automatically reverts them, ensuring consistency.

Automatic Reconciliation

GitOps continuously compares Git’s desired state against the actual runtime state and reverts any drift, maintaining alignment across your infrastructure.

Detecting and Preventing Configuration Drift
Early detection of configuration drift is a fundamental aspect of GitOps. Identifying drift as soon as it happens allows teams to resolve inconsistencies before they evolve into significant issues. This proactive stance distinguishes GitOps from other deployment methodologies.

Multi-Cluster Deployment Made Easy
Managing multiple clusters, especially across different geographical locations, can be challenging. GitOps simplifies this process by centralizing cluster state within Git. This means:

A single operator can deploy applications across multiple clusters.
There is no need to install or set up the operator individually on each cluster.
The deployment process is streamlined and significantly more efficient.
The image illustrates a GitOps feature set and use cases, showing a workflow involving tools like Helm and Jenkins, Git repositories, and Kubernetes clusters for continuous deployment and automation. It highlights concepts such as single source of truth, everything as code, auditable processes, and multi-cluster deployments.

For more details on deploying and managing resources with GitOps, explore additional resources such as:

Kubernetes Documentation
GitOps Tools Overview
Modern CI/CD Practices
By leveraging GitOps, teams can achieve high levels of deployment efficiency, improved management across diverse environments, and robust recovery mechanisms, making it an essential strategy for modern infrastructure management.

---

## GitOps Benefits Drawbacks

GitOps Benefits Drawbacks
This article reviews the key advantages and challenges associated with GitOps, providing insights for managing Kubernetes application deployments effectively.

Benefits of GitOps
GitOps offers several compelling advantages:

It is lightweight and vendor-neutral, leveraging the open-source Git protocol to work seamlessly across diverse platforms.
GitOps enables faster and safer deployments by ensuring immutable and reproducible environments.
In team setups where environmental changes might occur unexpectedly, GitOps prevents unintended modifications. The GitOps operator enforces consistency by disallowing manual updates, thus eliminating configuration drift.
In the event of a manual update, the GitOps operator automatically restores the desired state from Git.
Developers enjoy the familiarity of using Git and CI/CD tools. The workflow remains straightforward: push the code to the repository, and a CI/CD pipeline handles testing and deployment.
Git’s history tracking allows for easy comparison between declarative file revisions, making it simple to correlate changes with specific change requests.
Note

For more details on CI/CD integrations with GitOps, refer to the official GitOps Documentation.

Challenges of GitOps
Despite its advantages, GitOps introduces a few challenges that need to be addressed:

Centralized Secret Management:
GitOps does not secure secrets by default. Although it recommends storing secrets declaratively in Git repositories, operations teams must integrate additional tools to manage secrets securely.

Repository Organization:
As the number of microservices and environments grows, organizing Git repositories becomes complex. Decisions need to be made about whether to store source code and manifests in a single repository or use multiple repositories/branches. There is no one-size-fits-all solution—each organization must tailor this approach to fit its specific application requirements.

Update Conflicts:
Frequent application updates in continuous delivery environments can trigger simultaneous CI processes, leading to multiple pull requests. This may result in conflicts when several processes attempt to update the GitOps repository concurrently, often necessitating manual resolution.

Governance and Policy Enforcement:
Relying on pull requests (PRs) for approval can reduce the effectiveness of enforcing strict company policies after a PR is approved.

Configuration Validation:
Malformed YAML files or configuration errors can occur. External validation tools are essential for ensuring that manifest files meet the required standards.

Warning

Ensure that you integrate robust secret management and repository organization strategies when implementing GitOps to mitigate these challenges effectively.

---

## GitOps Projects Tools

In this article, we explore a diverse range of GitOps projects and tools available as of this recording. These solutions have been designed to streamline the management of Kubernetes applications by leveraging GitOps practices through various controllers and automation tools.

Overview

This guide provides insights into both GitOps controllers and complementary tools that enhance Kubernetes application deployment and management.

**GitOps Controller: ArgoCD**
ArgoCD is our primary GitOps controller. It is a declarative continuous deployment tool for Kubernetes that simplifies application management while ensuring your deployment process remains automated and consistent.

**Additional GitOps Tools**
Enhance your Kubernetes GitOps workflows with these additional tools:

- **Atlantis:** Automates Terraform workflows by integrating directly with pull requests.
- **AutoApply:** Automatically applies configuration changes from a Git repository to your Kubernetes cluster, saving manual intervention.
- **CloudRollout:** Provides advanced feature flagging, enabling teams to deploy and iterate rapidly without sacrificing safety.
- **GitOps with** FluxCD: Offers continuous and progressive delivery solutions optimized for Kubernetes environments.
- **Helm Operator**: Automates the release of Helm charts following GitOps principles.
- **The image** lists various GitOps projects and tools, each represented by a logo and name, such as ArgoCD, FluxCD, and JenkinsX.
- **Flagger:** A Kubernetes operator focused on progressive delivery. It supports canary releases, A/B testing, and blue-green deployments.
- **Ignite:** Functions as a virtual machine manager with a container-like user experience, incorporating built-in GitOps capabilities.
- **Faros:** A GitOps controller that utilizes Custom Resource Definitions (CRDs) for streamlined operations.
- **GitKube:** Facilitates Docker image building and deployment to Kubernetes clusters through a Git push workflow.
- **Jenkins X**: Tailored for Kubernetes, this CI/CD platform provides pipeline automation with integrated GitOps and preview environments.
- **KubeStack:** Leverages Terraform to provide a GitOps framework for cloud Kubernetes distributions such as AKS, GKE, and EKS, complete with CI/CD examples.
- **Weave Cloud**: An automation and management platform designed to support both development and DevOps teams.
- **PipeCD:** A continuous delivery solution built for declarative Kubernetes, serverless, and infrastructure applications.