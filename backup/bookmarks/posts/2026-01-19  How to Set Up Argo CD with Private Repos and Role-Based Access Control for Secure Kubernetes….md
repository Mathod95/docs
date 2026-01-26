---
title: "How to Set Up Argo CD with Private Repos and Role-Based Access Control for Secure Kubernetes…"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://priyanshubhatt18.medium.com/how-to-set-up-argo-cd-with-private-repos-and-role-based-access-control-for-secure-kubernetes-87b1dbafc933"
author:
  - "[[Priyanshu Bhatt]]"
---
<!-- more -->

[Sitemap](https://priyanshubhatt18.medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*nxgplKhHzmQdzlGgDgNP3g.png)

==Argo CD has quickly become a favorite among DevOps teams for its ability to manage Kubernetes deployments using the GitOps methodology. One key feature that makes Argo CD powerful and secure is its robust Role-Based Access Control (RBAC) system. In this blog post, we’ll delve into the intricacies of policies and roles in Argo CD, and how you can leverage them to enhance the security and efficiency of your deployment workflows by using Private Repository.==

### USING PRIVATE REPO FOR ARGOCD

**STEP 1:** Create an Access Token for your GitHub account from the developer settings in the settings tabs of your account.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*mO9LS44EjnDU16iO)

**STEP 2:** Create a Kubernetes secret for the GitHub token, this will be utilized to authenticate to the GitHub repository.

```c
apiVersion: v1
kind: Secret
metadata: 
  name: argo-private-repo-secret
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository # important label
stringData:
  type: git
  url: https://github.com/Unthink-pri18/Argo-private-repo.git
  username: argo-cd-private-repo # name of the token created in github
  password: ghp_fws4ZUASHWAFi6Z6Wq2gslpmdOjhkjsnkxjnsl
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*-m8hP1imxoFIdRgp)

When we see the Argo CD GUI settings of the repository you can see the configurations.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*MgMaSgFe4BESrSsd)

**STEP 3:** Create a sample Application to test the setup:

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
 name: private-application
 namespace: argocd  # Argo CD's namespace
spec:
 destination:
   namespace: default  # Target namespace where the application will be deployed
   server: https://kubernetes.default.svc  # URL of the Kubernetes API server
 source:
   repoURL: 'https://github.com/Unthink-pri18/Argo-private-repo.git'
   targetRevision: main  # Git revision (branch, tag, commit SHA)
   path: 'manifest'
 project: default  # Argo CD Project
```

The application is deployed and is all synchronized to the current environment.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*KpgW5WBlk6ye6ijd)

==But here’s a problem with this approach, to up credentials for each private repo in our project can be a repetitive step, so to optimize this we will use Credential Templates:==

**STEP 4:** Credential templates define credentials for the whole account, we need to pass the prefix and it will automatically allow the private repositories to have the same prefix.

```c
apiVersion: v1
kind: Secret
metadata:
 name: argo-private-repo-secret
 namespace: argocd
 labels:
   argocd.argoproj.io/secret-type: repo-creds # important label
stringData:
 type: git
 url: https://github.com/Unthink-pri18   # prefix only the repo name and whatever repo we use here with private we can use no need to define again and again
 username: argo-cd-private-repo # name of the token created in github
 password: ghp_fws4ZUASHWAFi6Z6Wq2gslpxyxhkjhkjhkj
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*NMvXRFQegqUmMOa3)

Now that we are secure from the Private repo side, Let’s create policies and roles for our ArgoCD applications.

Roles in Argo CD are defined in a declarative manner using YAML files. Each role consists of permissions that specify what actions the role can perform. For example, a role could have permission to create applications, sync projects, or delete resources. Policies are defined for each role and it can allow permissions to all applications in a certain project or only a single application in the whole project.

Let’s create a Project with Roles and Policies attached:

```c
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
 name: roles-project
 namespace: argocd
spec:
 clusterResourceWhitelist:
 - group: '*'
   kind: '*'
 destinations:
 - namespace: '*'
   server: '*'
 sourceRepos:
 - 'https://github.com/Unthink-pri18/Agro-Beg.git'
 roles:
   - name: read-sync-delete
     description: "This is a read and sync role" # get or read only all the applications in the roles-project project. this role can also sync the application in the project
     policies:
       - p, proj:roles-project:read-sync-delete, applications, get, roles-project/*, allow
       - p, proj:roles-project:read-sync-delete, applications, sync, roles-project/*, allow
       - p, proj:roles-project:read-sync-delete, applications, delete, roles-project/hello-world, allow
```

This project contains a role called read-delete with an attached policy to get all applications in roles-project and sync permission for all applications in the project. It also has permission to delete the hello-world application from the roles-project project.

Create this project by using:

```c
Kubectl apply -f roles-project.yaml
```

Create the role using the below command.

```c
argocd proj role create-token roles-project read-delete
```

It will provide an auth token which should be used to access the applications in the roles-project project.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*FyFaCuomgk8M15Ss)

Argocd app list for the default shows all the applications.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*hChef_nva9mWoTou)

Create an Application in the roles-project project:

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
 name: roles-application
 namespace: argocd  # Argo CD's namespace
spec:
 destination:
   namespace: default  # Target namespace where the application will be deployed
   server: https://kubernetes.default.svc  # URL of the Kubernetes API server
 source:
   repoURL: 'https://github.com/Unthink-pri18/Agro-Beg.git'
   targetRevision: main  # Git revision (branch, tag, commit SHA)
   path: '.'
 project: roles-project  # Argo CD Project
```

When we use the token generated by the create role command we can see that the application in the roles-project is present, the rest is not shown as this role has access to this project only.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*rKjavPWrrynYEkHU)

This Token can then be used for CI pipelines to trigger deployment or for the Argo-cli mode to access the argocd resources. Jenkins can handle the CI, including building, testing, and packaging your application. Once the CI process is complete, Jenkins can trigger ArgoCD to hold the CD part, deploying the application to your Kubernetes clusters.

```c
pipeline {
      agent any
      environment {
          ARGOCD_SERVER = 'https://argocd.example.com'
          ARGOCD_TOKEN = credentials('argocd-token') // Assuming the token is stored in Jenkins credentials
      }
      stages {
          stage('Deploy') {
              steps {
                  sh """
                  argocd login ${ARGOCD_SERVER} --token ${ARGOCD_TOKEN}
                  argocd app sync my-application
                  """
              }
          }
      } 
}
```

### CONCLUSION

Argo CD’s robust RBAC system and seamless integration with Git Ops methodology make it a powerful tool for managing Kubernetes deployments. By leveraging private repositories and credential templates, you can enhance the security and efficiency of your deployment workflows. The step-by-step guide above walks you through setting up private repository access, creating applications, and defining roles and policies within Argo CD, ensuring that your deployments are secure and streamlined.

## More from Priyanshu Bhatt

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--87b1dbafc933---------------------------------------)