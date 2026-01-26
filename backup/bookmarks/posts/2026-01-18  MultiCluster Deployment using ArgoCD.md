---
title: "MultiCluster Deployment using ArgoCD"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@csarat424/multicluster-deployment-using-argocd-699f4506d4e9"
author:
  - "[[Sarat Chandra Motamarri]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/1*bO3GF_tJsJAM1--dUqiJmw.png)

ArgoCD is a GitOps-based tool and is very renowned for continuous delivery.

### What is GitOps?

Let’s say we have a special notebook where we jot down all the steps to build a Lego castle. Every time we want to build that castle, we simply follow the instructions in our notebook step by step. Now, imagine GitOps is like having a magic pencil that automatically updates the notebook whenever we change something in our castle plans.

So, instead of having to remember to update the notebook every time we can change our mind about how many towers the castle should have or where the drawbridge should go, the magic pencil does it for us. That way, whenever we want to build our castle, we just look at our notebook, and it always has the latest, most accurate instructions. GitOps does something similar for building and managing computer programs and systems.

### What is ArgoCD?

Imagine having a toy box with lots of toys inside. Sometimes, when we want to organize toys neatly, like putting all the cars in one corner and all the dolls in another. Argo CD acts like a magic toy organizer for computer programs instead of toys.

Imagine a big collection of computer programs, like games or apps, and want to keep them organized and updated. Argo CD helps to do that. It makes sure that all the programs are in the right place and that they’re always up-to-date, just like the way we want our toys to be neatly arranged and ready to play with. So, it’s like having a helper that keeps everything in order!

### Architecture of ArgoCD

Argo CD is a tool used for continuous delivery (CD) of applications to Kubernetes clusters. Its architecture is designed to help automate the deployment and management of applications in Kubernetes environments. Here’s a simplified explanation of its architecture:

1. **Control Plane**: Argo CD has a control plane component, which is responsible for managing the overall deployment process. This includes handling user authentication, managing application configurations, monitoring the cluster’s state, and coordinating deployments.

2\. **Git Repository**: Argo CD relies heavily on Git repositories to store application manifests and configuration files. These repositories contain the desired state of the applications you want to deploy. Whenever changes are made to the repository (e.g., updating application configurations), Argo CD detects these changes and automatically syncs them with the Kubernetes cluster.

3\. **Application CRDs**: Argo CD introduces custom resource definitions (CRDs) called \`Application\` resources. These resources represent the applications you want to deploy and manage with Argo CD. Each \`Application\` CRD specifies details such as the source repository, target cluster, synchronization settings, and deployment parameters.

4\. **Controller**: The Argo CD controller is responsible for reconciling the state of \`Application\` resources with the actual state of the Kubernetes cluster. It continuously monitors changes in the Git repository and orchestrates the deployment process based on the desired state specified in the \`Application\` CRDs.

5\. **Sync Engine**: The sync engine is a core component of Argo CD responsible for comparing the desired state of applications (defined in Git) with the current state of the Kubernetes cluster. It performs synchronization tasks to ensure that the cluster matches the desired state specified in the \`Application\` resources.

6\. **User Interface (UI)**: Argo CD provides a web-based user interface that allows users to visualize and manage their applications, application configurations, and deployment status. The UI interacts with the control plane and presents users with an intuitive dashboard for managing their applications.

In summary, Argo CD’s architecture revolves around managing application configurations stored in Git repositories, reconciling the desired state with the actual state of Kubernetes clusters, and providing users with a user-friendly interface for continuous delivery and application management.

```c
+----------------------------------------+
      |            User Interface (UI)         |
      +----------------------------------------+
                     |    ^
                     |    |
                     v    |
          +-------------------------------+
          |          Control Plane        |
          | - User Authentication         |
          | - Application Configuration   |
          | - Cluster Monitoring          |
          | - Deployment Coordination     |
          +-------------------------------+
                     |    ^
                     |    |
                     v    |
          +-------------------------------+
          |        Git Repository         |
          | - Application Manifests       |
          | - Configuration Files         |
          | - Desired State               |
          +-------------------------------+
                     |    ^
                     |    |
                     v    |
          +-------------------------------+
          |    Argo CD Controller         |
          | - Reconciles Application      |
          |   State with Cluster State    |
          +-------------------------------+
                     |    ^
                     |    |
                     v    |
          +-------------------------------+
          |         Sync Engine           |
          | - Compares Desired State      |
          |   with Current Cluster State  |
          | - Synchronization Tasks       |
          +-------------------------------+
                     |    ^
                     |    |
                     v    |
          +-------------------------------+
          |          Kubernetes           |
          | - Application Deployment      |
          | - Cluster Management          |
          +-------------------------------+
```

```c
Note: If you wish to recreate this project, you will incur charges for creating EKS Clusters on AWS
```

### PROJECT

**Prerequisites:**

Install **kubectl** from [https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)

![](https://miro.medium.com/v2/resize:fit:640/1*_HjmNJmZ4u6Fob9-1OY2Wg.png)

Install **eksctl** from [https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html)

![](https://miro.medium.com/v2/resize:fit:640/1*Geo84aci07xxYtxoAYFDTQ.png)

Install **AWS CLI** from [https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)

![](https://miro.medium.com/v2/resize:fit:640/1*d1yoc3EzUqD9KJFkgExiKQ.png)

Install **ArgoCD CLI** from [https://argo-cd.readthedocs.io/en/stable/cli\_installation/#installation](https://argo-cd.readthedocs.io/en/stable/cli_installation/#installation)

### EKS Setup:

(I took three separate tabs on the Terminal: black terminal — hub cluster; yellow terminal — Spoke Cluster -1; Blue terminal — Spoke Cluster -2)

```c
eksctl create cluster --name hub-cluster --region us-west-1
```

Explanation: This command initiates the process of provisioning a Kubernetes cluster on AWS in the specified region that is us-west-1 with the given name (Hub cluster).

![](https://miro.medium.com/v2/resize:fit:640/1*5zakBm96qbRm8NMVVjn4Cg.png)

Hub Cluster

```c
eksctl create cluster --name spoke-cluster-1 --region us-west-1
eksctl create cluster --name spoke-cluster-2 --region us-west-1
```
```c
Explanation:  The above two commands create multiple Kubernetes clusters, this time named “spoke-cluster-1”, and “spoke-cluster-2”, in the “us-west-1” region using eksctl.
```
```c
Note: This cluster creation will take approximately 20 - 30 min.
```
![](https://miro.medium.com/v2/resize:fit:640/1*3WJcRSSA8ciavzZSV6S3tw.png)

Spoke Cluster-1

![](https://miro.medium.com/v2/resize:fit:640/1*q_GGSSwPY8IeSRiJWijlBA.png)

Spoke Cluster -2

### The reason behind the naming convention:

GitOps controller like ArgoCD comes in two modes of deployment, namely:

1. ***Hub-Spoke Model —***

In GitOps, the hub-spoke model refers to a deployment architecture where there’s a central Git repository (the “hub”) that contains declarative descriptions of the desired state of the entire system or application. Each target environment, such as development, staging, or production (the “spokes”), pulls these configurations from the central repository and applies them to ensure that the actual state of the system matches the desired state.

Here’s how the hub-spoke model typically works in GitOps:

1\. Hub: The central Git repository serves as the single source of truth for the desired state of the system. It contains configuration files, such as Kubernetes manifests, Helm charts, or any other infrastructure-as-code declarations that describe the application’s infrastructure and configuration.

2\. Spokes: Each target environment, or deployment cluster (e.g., development, staging, production), acts as a “spoke.” These environments continuously reconcile their state with the desired state specified in the Git repository. They pull the configuration from the repository and apply it to ensure that the actual infrastructure and application state match what’s defined in the repository.

Changes made to the repository trigger a reconciliation process in each spoke environment, automatically updating the infrastructure and application configurations to reflect the changes.  
— The spokes typically run agents or controllers (e.g., Flux, Argo CD) responsible for syncing the state between the Git repository and the target environment.

*The hub-spoke model offers several benefits in GitOps:*

\- Centralized control: The central Git repository provides a single source of truth, enabling centralized control and visibility over the entire system’s configuration.  
\- Consistency: All environments are configured and managed consistently, reducing configuration drift and ensuring that changes are applied uniformly across environments.  
\- Traceability and versioning: Changes to the system’s configuration are tracked and versioned in the Git repository, providing traceability and enabling rollback to previous configurations if needed.  
\- Scalability: The model scales well for managing multiple environments and clusters, making it suitable for complex deployment scenarios.

Overall, the hub-spoke model in GitOps simplifies the management and deployment of cloud-native applications by leveraging Git as the primary mechanism for configuration management and continuous delivery.

***2\. Standalone Model.***

In GitOps, the standalone model refers to a deployment architecture where each environment or cluster operates independently and manages its configuration without relying on a central Git repository for synchronization. Instead of pulling configuration from a central repository, each environment maintains its own configuration locally or through other means.

*In the standalone model:*

1\. Independent Environments: Each environment, such as development, staging, or production, operates independently and manages its configuration separately from other environments. There is no central repository that dictates the desired state for all environments.

2\. Local Configuration Management: Configuration changes are typically managed locally within each environment. This could involve manual configuration updates, scripts, or other tools specific to the environment.

3\. Limited GitOps Practices: While Git might still be used for version control, it plays a less central role in configuration management and deployment. Configuration changes might not be triggered by Git commits or follow the GitOps principles of declarative infrastructure management.

4\. Potential for Configuration Drift: Without a central source of truth, there is a higher risk of configuration drift between environments. Changes made in one environment might not be consistently applied to others, leading to inconsistencies and potential operational issues.

The standalone model contrasts with the hub-spoke model, where a central Git repository serves as the source of truth for configuration management and synchronization across environments. While the standalone model may offer simplicity and flexibility for smaller deployments or less complex environments, it can also lead to challenges in managing consistency, traceability, and scalability, especially in larger or more dynamic infrastructures.

Since my **hub-cluster, spoke-cluster-1, and spoke-cluster-2** are ready let’s proceed.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2uDhH148Bg9_zfXQn1CKLQ.png)

hub-cluster

![](https://miro.medium.com/v2/resize:fit:640/1*KyQWN1houTh8hsGkBrXNKQ.png)

spoke-cluster-1

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*shefxQYQe8MbXcG91et3Vw.png)

spoke-cluster-2

Let us get all the contexts with the following commands:

```c
kubectl config get-contexts 
kubectl config get-contexts | grep us-west-1 (in case we want particularly)
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*c2C7wOwEaD1e2w5X8f_Adw.png)

*A context in Kubernetes is a combination of a cluster, user, and namespace, defining the current working environment for managing Kubernetes resources.*

Now let‘s switch the context to the hub cluster using the following command:

```c
kubectl config use-context iam-root-account@hub-cluster.us-west-1.eksctl.io
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*4b2Xyp-Jx3bYPSRez6lUIA.png)

Now it’s time to Install Argo CD on this hub-cluster. The command to install Argo CD can be found in the following link:

[https://argo-cd.readthedocs.io/en/stable/getting\_started/](https://argo-cd.readthedocs.io/en/stable/getting_started/)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Im6rn2UsawN9iRXP1iHZtg.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*eucyZJEX9jqEeTVp03UtNw.png)

Let’s see if our pods are up and running with the following command:

```c
kubectl get pods -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*UBUx2yBN33u4_Ffw6vO2lQ.png)

Now that all the pods are up and running, let’s check configmap as well:

```c
kubectl get cm -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Hd4s5nMvPMB528_FQ1u2kw.png)

**Run ArgoCD in HTTP mode (insecure):**

To achieve this select the “ ***argocd-cmd-params-cm*** ” from the list and let’s edit using the following command:

```c
kubectl edit configmap argocd-cmd-params-cm -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PLxnqhdsH3y15o5oB7CyyA.png)

Now we need to add the following data “ ***server.insecure: “true”*** and this can be found at [https://github.com/argoproj/argo-cd/blob/master/docs/operator-manual/argocd-cmd-params-cm.yaml](https://github.com/argoproj/argo-cd/blob/master/docs/operator-manual/argocd-cmd-params-cm.yaml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CvZHHB5zHNrwour8foMyLw.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*hZ9-SQtRZOacGNGKb61deA.png)

In the search look for “ ***cmd-*** ” and look for “ ***docs/operator-manual/argocd-cmd-params-cm-yml*** ”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*e_dEZy5OKfMoutMmPzdUHw.png)

Now in this yaml file search for “ ***insecure*** ”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*YKPq42Kkr5cl7OqixiwpOg.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*goVcN---b8t9AVFrn3G-Uw.png)

copy the “ ***server.insecure: “true”*** content and add it to the configmap file.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*t9MRixPJ6vartfpS9ToonQ.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*4b7pJgYEs-Dql6y7ogSagA.png)

Now save the file.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*8H2rjBh0JNZDEQEZoD-Eew.png)

Let’s double-check to see if the pods and service are up and running using the following commands:

```c
kubectl get pods -n argocd
kubectl get svc -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0gpzhtgT6ws8MQCH-D9nFQ.png)

Now we need to expose argocd-server from “ ***ClusterIP”*** to “ ***NodePort”***.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*76usxHt589yOCIWtG4Bfew.png)

To achieve this use the following command and change the type from “ ***ClusterIP”*** to “ ***NodePort”.***

```c
kubectl edit svc argocd-server -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ASZrXEpLMwxLmqSSnkU_sA.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*pEYNm43opClhbyT7d7BpDw.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*skPEAchpT92veMDGRQdBng.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*aG6CsojJZf2hnieMSDmZ9g.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*FChgoxNoYW8qVV-oQs4tTg.png)

Now that we have changed the type from “ ***ClusterIP*** ” to “ ***NodePort*** ” we can access it using the EC2 instance public ip and port number. For this navigate to AWS Console >> EC2 >> Instances (running). { ***Make sure you are in the “us-west-1” region*** }.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*KO-6UwB_oM3-A2vZI6a2Ag.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*bphK4V6tPl5kuitU3shnkA.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*SoXf0LEMRJ8tdatPOPOtCg.png)

Select the “hub-cluster” instance and copy the public ip.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0jlP0f_Bq0Rv3mImJw-sSw.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*oSYDYhmBZvgeNSot5MbT1g.png)

We need to open this port. So head to the security group of the EC2 Instance>>select edit inbound rules>> add rule>> allow “ ***All Traffic*** ”.(in this case port number is 30590).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*jJRNyWstQIt6SKyWYMr--A.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Gv8SNcPs0d7cvLxON-IP9w.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*_P_4vD7vOgZgYIUzt35eDA.png)

Now let’s try to access our Argo CD server so navigate back to the browser and refresh

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*yi4VvYvlpv3IafBaHdvBGg.png)

Click “ ***Advanced*** ”

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*8hxzAIEySy_8a3_esFxupg.png)

Click “ ***Proceed to 13.56.151.188 (unsafe)*** ”. We now should be able to access the Argo CD UI.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CIPLqR1Dryg10uCyq568cg.png)

Woh…now that we have Argo CD up and running let us now log in. To log in the default “ **Username** ” is “ **admin** ”. For the password, we need to use the following command:

```c
kubectl get secrets -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QWYlOs7m9Mu_uthSMEEA7g.png)

In the list obtained, we need to edit the “ ***argocd-initial-admin-secret*** ”. This can be done by the following command:

```c
kubectl edit secret argocd-intial-admin-secret -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*k3FDxcS-HVFK1rIQC4_vRA.png)

then copy the password as shown

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*nTR75_qsZ1OQc5En6WPSaA.png)

now we need to decode it using the following

```c
echo password | base64 --decode
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Hx89tv3PNkdViidU7I1v1g.png)

Now we have the password to log into the Argo CD UI. (Do not copy the “ ***%*** ”). Copy and paste it in the password field. (Make sure to save the password as we will be using it another time).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*8ptoux2Scp3S-5PX4Z7fig.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*YWRbbytC_DAhAAx4Ypl4Jg.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*OnY92jA24Vm-GeUoBZ7_0Q.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5GO5V4PDpouwNTk4BIYZog.png)

### Adding Clusters:

Now that we were able to log in to the “ ***Argo CD UI*** ”. let us add the two clusters “ ***spoke-cluster-1*** ” and “ ***spoke-cluster-2*** ”. But the catch here is we cannot add clusters directly on the “ ***Argo CD UI*** ”, so we need to add using “ ***Argo CD CLI*** ”.

So, we need to install “Argo CD CLI”. The command to install “ ***Argo CD CLI”*** can be found at [https://argo-cd.readthedocs.io/en/stable/cli\_installation/](https://argo-cd.readthedocs.io/en/stable/cli_installation/)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*uVbZMokx8Ze2dog81ML-1Q.png)

since mine is a Mac I have installed using the “ ***brew install argocd*** ”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*G7pr9lW6Z7jx2wmXFNcjmA.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*boyyiGkIf9EQT73caHpLSw.png)

Now we need to log in to “ ***Argo CD CLI*** ”. So the command is

```c
argocd login EC2 Instance publicip:port
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*BLJmuYsFQUeeigjH3Nhb-w.png)

The “ ***username*** ” is “ ***admin*** ” and the “ ***password*** ” (the same one which we obtained earlier using the decode command).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Hx89tv3PNkdViidU7I1v1g.png)

As we were able to log in now we need to add clusters. The following command can be used to add:

```c
argocd cluster add iam-root-account@spoke-cluster-1.us-west-1.eksctl.io -- server 13.56.151.188:30590
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*VC_gONXIwx5wpcGu2Q2tjQ.png)

Breakdown:

- `argocd`: This is the command-line tool for Argo CD.
- `cluster add`: This subcommand that is used to add a new cluster to Argo CD.
- `iam-root-account@spoke-cluster-1.us-west-1.eksctl.io`: This is the identifier for the cluster being added. It typically includes the IAM user or role, followed by the cluster name and region. (can be found from contexts)
- `--server 13.56.151.188:30590`: This specifies the address of the Argo CD server and the port to which the cluster should connect for communication.

Now we need to add the second cluster

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*D4rGoGgX8XSFOVJ98eS4Pg.png)

Now that we have added clusters let’s go to the UI and check.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*antkOfCUk6ST9NhiiecEgA.png)

As we have added clusters let us deploy our app. In this case, the Guest-book app is located in GitHub.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2m2XDpkrbJ88hgHLswq8fg.png)

Now click on “ ***NEW APP*** ”. Fill in the details as shown below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*TxP3f70_R3yRe2HzFRDUJw.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0BXUoQ3Wbx8BulitbikB7A.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Z30HXABPB6p5Cr8n6CKVBg.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*fO18Mzo049e00mYQwDeCfg.png)

Once filling all the details click “ ***Create*** ”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*nRvHA2blLZhUlw071BYO2g.png)

Now let us deploy our app on the second cluster as well.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*V4g37UMrVnROgH50-vVCwQ.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*-Z3PqxhK6M5cFXENRYdq6Q.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*UQm7kg-QhB46yOPALtjeiA.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*d9myK2pl15vg2z6QAx8fMg.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*tRbBdezC6YVVPilFT7LcSQ.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*_2X5LAsgJgXXEPxof5bE3w.png)

Now let us see the same using the CLI. So use the following command:

```c
kubectl config use-context iam-root-account@spoke-cluster-1.us.-west.1.eksctl.io
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*zX6Me7f_NqLkc3kW0IeUUw.png)

We have successfully deployed our app as we can witness service, deployment, and replica set.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QoZFsFLDw9QK_SolT9QBDQ.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*16_nQCpqf52gjNRTrbfDLw.png)

Now let us edit the configmap. Default it is “ ***Abhishek*** ”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*MdOhs4WLjYrVl6RbO90ueA.png)

Now let us edit the same “ ***configmap.yml*** ” the source of truth that is in “ ***GitHub*** ”. So, I changed it from “ ***abhishek*** ” to “ ***sarat*** ” in the “ ***ui\_properties\_file\_name*** ”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GyPobmEKtf3z7ECQIB8Lng.png)

![](https://miro.medium.com/v2/resize:fit:640/1*wPZS_ZDcs6RwZueCXKspuA.png)

![](https://miro.medium.com/v2/resize:fit:640/1*_48zYwoJOh8NJrFQzL9akw.png)

Generally, it takes “3 minutes” to automatically reflect changes, but let us sync it manually. So, click “ ***SYNC APPS*** ”>> “ ***SYNC*** ”.

![](https://miro.medium.com/v2/resize:fit:640/1*0WBdiKrFEma1NT4tlWeREA.png)

![](https://miro.medium.com/v2/resize:fit:640/1*R8GNf43MemqG7tOTFsJfIw.png)

Select both apps.

![](https://miro.medium.com/v2/resize:fit:640/1*ZTX4QhlqSCSfV1E97vNwuA.png)

Now that we have synced, let’s check the same using CLI using the

```c
kubectl edit configmap
```
![](https://miro.medium.com/v2/resize:fit:640/1*kMdUe8EqGpB7vgjZtqtRzw.png)

![](https://miro.medium.com/v2/resize:fit:640/1*w2MO2eReg9ep1hsTWGbFTA.png)

So when we update the single source of truth that is “ ***GitHub*** ” then ArgoCD will successfully update the cluster.

Now let us manually modify the “configmap” instead of modifying the source of truth. I edited the “ ***ui\_properties\_file\_name: user-interface.properties*** ”. (from “ ***sarat*** ” to “ ***user*** ”).

![](https://miro.medium.com/v2/resize:fit:640/1*fR1qKHwnx31ZOdq7Zbpj_A.png)

![](https://miro.medium.com/v2/resize:fit:640/1*DXkrTdyQVPw1XQfGbREYog.png)

![](https://miro.medium.com/v2/resize:fit:640/1*6v-9P6-XNhMkRoYw5HVryw.png)

It clearly skipped the change.

![](https://miro.medium.com/v2/resize:fit:640/1*i5xERy6nTQfslMI_jUdv_A.png)

This can also be seen on UI.

![](https://miro.medium.com/v2/resize:fit:640/1*LwtcYnj8tlq_-pa0vRiq0g.png)

Now click on “ ***sync*** ”>> “ ***synchronize*** ”.

![](https://miro.medium.com/v2/resize:fit:640/1*prrqz1mKf4Gb0nh3_XIYPg.png)

![](https://miro.medium.com/v2/resize:fit:640/1*fRWw92YqkmoaMXkc6dHcaw.png)

![](https://miro.medium.com/v2/resize:fit:640/1*ygCE1PRxP2ZGuUaO2DowOg.png)

Now because we used “ ***sync*** ” the change was rolled back in the configmap. (from “ ***user*** ” to “ ***sarat*** ”).

![](https://miro.medium.com/v2/resize:fit:640/1*Ie3w45W7zFQsuITWbAkQ9Q.png)

So, Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes. It ensures that the actual state of the Kubernetes clusters matches the desired state defined in declarative configuration files stored in a Git repository. It continuously monitors the cluster’s state and reconciles any differences to maintain the desired state, thereby promoting consistency and reliability in the Kubernetes infrastructure.

Now it is time to delete all the clusters.

![](https://miro.medium.com/v2/resize:fit:640/1*Vo4MC7ykXPB0qJlbevGwdw.png)

![](https://miro.medium.com/v2/resize:fit:640/1*Mj73gFGPI606L2gaEpH7JA.png)

![](https://miro.medium.com/v2/resize:fit:640/1*4jJkZ913KMtJuixhRXj0vA.png)

```c
You can reach me at 
LinkedIn:https://www.linkedin.com/in/sachmo/
GitHub: https://github.com/csarat424
```