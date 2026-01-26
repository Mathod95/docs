---
title: "Redefining Onboarding with Argo CD’s Secret Weapon Helm Chart"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://faun.pub/redefining-onboarding-with-argo-cds-secret-weapon-helm-chart-ef022646e244"
author:
  - "[[Tal Yitzhak]]"
---
<!-- more -->

[Sitemap](https://faun.pub/sitemap/sitemap.xml)## [FAUN.dev() 🐾](https://faun.pub/?source=post_page---publication_nav-10d1a7495d39-ef022646e244---------------------------------------)

[![FAUN.dev() 🐾](https://miro.medium.com/v2/resize:fill:76:76/1*af3uHdSUsv_rXFEufcyTqA.png)](https://faun.pub/?source=post_page---post_publication_sidebar-10d1a7495d39-ef022646e244---------------------------------------)

We help developers learn and grow by keeping them up with what matters. 👉 [www.faun.dev](http://www.faun.dev/)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*3Dl3qcSf-w4vyKdyzY0dgA.png)

Streamlining the onboarding process for new projects and applications in Argo CD has taken a significant leap forward thanks to the introduction of the argocd-apps Helm chart. This robust tool empowers users to effortlessly oversee additional Argo CD Applications and Projects, paving the way for a seamlessly automated onboarding process that enhances overall efficiency.

When considering the widespread usage of Argo CD, it becomes evident that its capabilities are pivotal in orchestrating smooth application deployments. However, as we scale and cater to diverse teams, it’s imperative to shift our perspective towards the broader picture. Rather than merely leveraging Argo CD’s capabilities, we must strategically contemplate the desired structure and implement a tailored self-service process that aligns with the unique needs of different teams. This proactive approach ensures not only efficiency but also sets the foundation for a scalable and organized deployment environment.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*MnXK-JfYOLXIzhqv530x-g.png)

Community Post in ArgoCD Reddit discussing ideas on designing self-service process for onboarding to ArgoCD

## The Power of argocd-apps

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*E__HNsyT6iVQA8PW)

argocd-apps helm chart in Artifact Hub: https://artifacthub.io/packages/helm/argo/argocd-apps

Argo CD is an excellent platform for continuous delivery of Kubernetes applications, but managing [ArgoCD Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/) and [ArgoCD Applications](https://argo-cd.readthedocs.io/en/stable/user-guide/application-specification/) and [ApplicationSets](https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/) manually through the UI can be time-consuming and error-prone. Enter [argocd-apps](https://artifacthub.io/packages/helm/argo/argocd-apps) — a Helm chart designed to simplify the onboarding process, making it more controlled, structured, and automated.

## Key Features/Capabilities

**Effortless Deployment**

- argocd-apps enables you to deploy projects, applications, application sets along with extensions, through a managed set of values.
- This ensures a smoother deployment process, minimizing errors and enhancing reproducibility.

**Improved Control**

- Move away from the manual UI-based approach and gain better control over the onboarding process.
- Maintain the structure of Argo CD as per your preferences, ensuring a consistent and organized environment.

**Integration with ArgoCD (it’s like any other helm chart!)**

- Seamlessly deploy the argocd-apps Helm chart within Argo CD itself.
- Get clear visibility on all the created objects: Projects, AppSets, Applications, etc.

**Automated Onboarding**

- Establish a streamlined onboarding process by creating a pull request (PR) for the values.yaml file.
- Run continuous integration/continuous deployment (CI/CD) processes to validate the values and ensure code quality.
- Sync the changes into Argo CD, automating the onboarding mechanism and reducing manual intervention.
- You can also choose an auto-sync mechanism; that while passing all your checks, can automatically create the relevant resources.

## Implementing Self-Service Onboarding

Deploying [argocd-apps](https://artifacthub.io/packages/helm/argo/argocd-apps) with Argo CD opens the door to a self-service onboarding mechanism. Here’s how you can set it up:

**Step 1: Create PR for values.yaml in argocd-apps chart**

- Developers initiate the onboarding process by creating a pull request for the values.yaml file.
- This PR contains the necessary configurations for the new project or application.

**Step 2: CI/CD Automated Validation on the PR**

- **Leverage CI/CD pipelines to automatically validate the values in the pull request:** enforce naming conventions for projects / Applications / ApplicationSets, run a yaml linter using [available cli tools](https://faun.pub/cli-tools-for-validating-and-linting-yaml-files-5627b66849b1) to prevent merging an invalid YAML and validate the structure of the different resources as per you designed.
- Ensure that the configurations adhere to best practices and meet the required standards.

**Step 3: PR Review by ArgoCD Administrators / Maintainers**

- Apart from the CI/CD validations it’s possible to also include an approval step for the PR before being able to merge it.

**Step 4: PR Merged & Automated Sync with Argo CD**

- Upon successful validation, merge the PR.
- Manually (press the ‘Sync’ button) / Automatically (use auto-sync on [argocd-apps](https://artifacthub.io/packages/helm/argo/argocd-apps) helm chart) sync the changes into Argo CD.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*x6Fhw2SzkQUWLkuJceOgjA.png)

Onboarding process to ArgoCD describe with it’s different steps

The relevant resources are now ready for the user to use in ArgoCD (dedicated project / AppSets / Applications). 🙂

**Conclusion**

[argocd-apps](https://artifacthub.io/packages/helm/argo/argocd-apps) emerged as a critical game-changer in the world of Argo CD, offering a robust solution for managing applications and projects seamlessly. By embracing this Helm chart, teams can enjoy a more controlled, automated, and efficient onboarding process, ultimately contributing to a smoother and more organized development workflow. Elevate your Argo CD experience with argocd-apps and unlock the full potential of automated onboarding.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*oOkc7IiCduSwFerI.png)

### 👋 If you find this helpful, please click the clap 👏 button below a few times to show your support for the author 👇

### 🚀Join FAUN Developer Community & Get Similar Stories in your Inbox Each Week

[![FAUN.dev() 🐾](https://miro.medium.com/v2/resize:fill:96:96/1*af3uHdSUsv_rXFEufcyTqA.png)](https://faun.pub/?source=post_page---post_publication_info--ef022646e244---------------------------------------)

[![FAUN.dev() 🐾](https://miro.medium.com/v2/resize:fill:128:128/1*af3uHdSUsv_rXFEufcyTqA.png)](https://faun.pub/?source=post_page---post_publication_info--ef022646e244---------------------------------------)

[Last published Dec 31, 2025](https://faun.pub/getting-started-with-amazon-bedrock-cli-api-simple-llm-inference-and-model-selection-1927b4826e2f?source=post_page---post_publication_info--ef022646e244---------------------------------------)

We help developers learn and grow by keeping them up with what matters. 👉 [www.faun.dev](http://www.faun.dev/)

DevOps Team Lead at Lightrun | CNCF Ambassador

## More from Tal Yitzhak and FAUN.dev() 🐾

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--ef022646e244---------------------------------------)