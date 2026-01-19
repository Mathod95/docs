---
title: "GitOps CI/CD Pipeline with GitHub Actions & ArgoCD."
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@vikwaso/gitops-ci-cd-pipeline-with-github-actions-argocd-56628a133bc2"
author:
  - "[[Victor wasonga onyango]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2uScaB6nrD_RDBHesAg8TQ.gif)

In today’s fast-paced DevOps landscape, GitOps is emerging as the standard for secure and automated application delivery. This project begins with a Jira task and walks through setting up a complete CI/CD pipeline using GitHub Actions and ArgoCD to deploy a Node.js application to a Kubernetes cluster hosted on an AWS EC2 instance. It covers the full lifecycle — from containerization and vulnerability scanning to fully automated, version-controlled deployments.

**Jira Task:** Automate CI/CD Pipeline Using GitOps  
**Task ID:** DEVOPS-102  
**Title:** Implement GitOps-Driven CI/CD with GitHub Actions and ArgoCD  
**Status:** To Do ➝ In Progress

**Project Goals**

- Build a CI pipeline with GitHub Actions to test, scan, and push Docker images
- Implement GitOps-based CD with ArgoCD for auto-sync and deployment.
- Manage credentials securely with GitHub Secrets
- Enable zero-downtime delivery using ArgoCD’s sync and self-heal features

## Project Structure

Here’s a visual overview of the directory layout:

```c
.
├── .github
│   └── workflows
│       └── argo-actions.yaml   # CI/CD GitHub Actions workflow
├── manifest
│   ├── deployment.yaml         # K8s deployment file with image reference
│   └── service.yaml            # Service to expose app in Kubernetes
├── Dockerfile                  # Container specification
├── index.js                    # Node.js app entrypoint
└── package.json                # Node.js dependencies
```

For this setup, we’ll use an Ubuntu t3.medium EC2 instance to install Minikube and create a local Kubernetes cluster. Docker will be installed for containerization, and kubectl will be used to manage the cluster.

Before proceeding, ensure your EC2 instance is up and running. I’ve already launched one, as shown.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ys2phU-xa1q4mxlIt2vTRg.png)

SSH into the server, then update and upgrade the system by running the following command:

```c
sudo apt update && sudo apt upgrade -y
```

To easily identify the server, run the following command to change its hostname.

```c
sudo hostnamectl set-hostname githubactions-server
```

After the update, install Docker using the following command.

```c
sudo apt  install docker.io -y
```

Verify that the installation is successful by running the hello-world.

```c
sudo docker run hello-world
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*EASYJaud6MfAupmtfEv0FQ.png)

[Post-installation steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/).

To run Docker without root privileges,

```c
sudo groupadd docker
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*i0Ep3RLFiEzVqz7e9DrHDA.png)

Add your user to the Docker group to enable running Docker without using sudo

```c
sudo usermod -aG docker $USER
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*JLSYt3Z2UTuxNi2RBM4iEA.png)

Log out and log back in to apply the group changes.  
Alternatively, run the following command to activate the new group membership without logging out.

```c
newgrp docker
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*jFTuAqC4_SaaNgYRGOKr5Q.png)

Install kubectl

```c
sudo snap install kubectl –classic
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*8_5HCBBwRm_xGHmJGcLAHQ.png)

Run the following command to download Minikube:

```c
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*oX0E4xpzVams1FJxkagH-A.png)

Run the following command to install Minikube

```c
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*81GvfQ5enYLWBPkcnl0f2g.png)

```c
minikube version
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*BQ7qmh-t0XUgR_GhUNzIMA.png)

Once Minikube is installed, start your Minikube cluster.

```c
minikube start --driver=docker
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*V26gnawKSAc9Sk-uXEIziQ.png)

```c
kubectl get nodes
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*lyfRoICwIm6-LSxcIbfhVQ.png)

Enable ingress on minikube

```c
minikube addons enable ingress
```

**GitHub Actions: Continuous Integration and Deployment**

**What is GitHub Actions?**  
A native GitHub CI/CD tool that automates and customizes workflows directly where your code lives.

**What are GitHub Runners?**  
Environments (Ubuntu, Windows, macOS) where workflows run. This project uses GitHub-hosted runners (`ubuntu-latest`).

**Benefits:**

- No infrastructure to manage
- Seamless GitHub integration
- Supports containers and Kubernetes
- Easy secret management via GitHub Settings

**CI/CD Workflow Overview**  
To follow this workflow, fork this repo or use your code with the provided sample directory structure.

```c
https://github.com/Victorwasonga/End-to-End-GitOps-CI-CD-Pipeline-on-Kubernetes
```
```c
.
├── .github
│   └── workflows
│       └── argo-actions.yaml   # CI/CD GitHub Actions workflow
├── manifest
│   ├── deployment.yaml         # K8s deployment file with image reference
│   └── service.yaml            # Service to expose app in Kubernetes
├── Dockerfile                  # Container specification
├── index.js                    # Node.js app entrypoint
└── package.json                # Node.js dependencies
```

**Workflow name:** GitOps pipeline with ArgoCD

- **Trigger:** Runs on every push to the `main` branch.
- **Environment variables:** Loads secrets like DockerHub credentials, ArgoCD login info, and Git user details securely.

**Jobs:**

**1\. Build**

- Runs on Ubuntu latest.
- Check out the code.
- Sets up Node.js v14 and installs dependencies.
- Builds a Docker image tagged with the current commit SHA.
- Scans the image for vulnerabilities using Trivy.
- Logs in to DockerHub and pushes the image.

**2\. Deploy**

- Depends on the build job.
- Check out the full git history.
- Installs `kubectl` and the ArgoCD CLI tools.
- Logs into the ArgoCD server using stored credentials, preparing for GitOps deployment.
```c
name: Gitops pipeline with Argocd

on:
  push:
    branches:
      - main  # Trigger the workflow on pushes to the main branch

env:
  # Load sensitive info from GitHub Secrets
  PERSONAL_ACCESS_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
  ARGOCD_PASSWORD: ${{ secrets.ARGOCD_PASSWORD }}
  ARGOCD_USERNAME: ${{ secrets.ARGOCD_USERNAME }}
  ARGOCD_SERVER: ${{ secrets.ARGOCD_SERVER }}
  GIT_EMAIL: ${{ secrets.GIT_EMAIL }}
  GIT_USERNAME: ${{ secrets.GIT_USERNAME }}

jobs:
  build:
    runs-on: ubuntu-latest  # Use the latest Ubuntu runner

    steps:
      - name: checkout code
        uses: actions/checkout@v3  # Checkout the repo code
        with:
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}  # Use personal access token for full repo access
          fetch-depth: 0  # Fetch full git history

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '14'  # Use Node.js version 14

      - name: Install Node.js dependencies
        run: npm install  # Install project dependencies

      - name: Build Docker image
        run: docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }} .  # Build Docker image tagged with commit SHA

      - name: Scan Docker Image with Trivy
        run: docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}  # Scan image for vulnerabilities

      - name: Log in to DockerHub
        run: echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u "${{ secrets.DOCKERHUB_USERNAME }}" --password-stdin  # Authenticate to DockerHub

      - name: Push Docker image to DockerHub
        run: docker push ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}  # Push image to DockerHub

  deploy:
    needs: build  # Run deploy after build completes
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3  # Checkout repo again for deploy step
        with:
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          fetch-depth: 0  # Full history for ArgoCD

      - name: Install kubectl
        run: |
          curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.30.7/2024-12-12/bin/linux/amd64/kubectl
          chmod +x ./kubectl
          sudo mv ./kubectl /usr/local/bin/kubectl  # Download and install kubectl CLI

      - name: Install ArgoCD CLI
        run: |
          curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
          chmod +x argocd
          sudo mv argocd /usr/local/bin/argocd  # Download and install ArgoCD CLI

      - name: Login to ArgoCD
        run: |
          argocd login ${{ secrets.ARGOCD_SERVER }} \
            --username ${{ secrets.ARGOCD_USERNAME }} \
            --password ${{ secrets.ARGOCD_PASSWORD }} \
            --insecure  # Authenticate to ArgoCD server
```

## Install ArgoCD in the Minikube Namespace argocd

Create an ArgoCD namespace

```c
kubectl create namespace argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*21BDgWs5CBhBCbuwcYb3XA.png)

Run this command to install ArgoCD

```c
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Get pods in the ArgoCD namespace

```c
kubectl get pods -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*j8HPcNe99JohzX3UXG27Mg.png)

**Expose ArgoCD Server**

First, add port 8080 to the Inbound Rules for the EC2 Instance

```c
kubectl port-forward - address 0.0.0.0 svc/argocd-server 8080:443 -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*sU-o8K74_F_Y-4pEK06T_g.png)

Get the ArgoCD password

```c
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d && echo
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CR5Lawipqh00rHLwv6wshg.png)

Use passwords to log in to the ArgoCD dashboard

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*esv-e46x_PEwLzVHrloJgw.png)

## Configure Repository in ArgoCD UI (or via CLI)

After logging in to ArgoCD, in the above code section, we need to connect the GitHub repository we’re working with:

1. Go to **Settings** → **Repositories** → **Connect Repo**
2. **Connection Method:** HTTPS
3. **Type:** Git
4. **Project:** default
5. **Repository URL:***\[Paste your repo URL\]*
6. **Username / Password:***(Optional, use if private repo)*
7. Leave the rest as default and click **Connect**

## Create a New Application in ArgoCD UI

1. Navigate to **Applications** → **New App**
2. **Application Name:**`argocd-github-actions`
3. **Project:**`default`
4. **Sync Policy:** Automatic
- Enable *Prune Resources*
- Enable *Self-Heal*
1. **Repo URL:** Select the one you just connected to
2. **Revision:**`main`
3. **Path:**`manifest` *(folder in the repo containing Kubernetes YAMLs)*
4. **Cluster URL:** Select `[https://kubernetes.default.svc](https://kubernetes.default.svc/)`
5. **Namespace:**`argocd`
6. Leave other settings as default or customize as needed, then click **Create**

**Alternatively, Create a New Application Using ArgoCD CLI**

```c
argocd app create my-app \
--repo https://github.com/your-username/your-repo.git \
--path manifest \
--dest-server https://kubernetes.default.svc \
--dest-namespace argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*qGJxO6GtAT5MeC6yb5wAmw.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*BeXXeDfnShAOVeUruSXZZg.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*i4ws20lhJe_hXVu7t-38ww.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*q7Y7drGI81Yu5JZXH_cvwg.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*oPdI2hNr58iHX8n8ov2rjA.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CXoMpdFppXC-I0Yq-p8kiw.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0eDjw5p0ZUuH6MFKTII5zQ.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*piQJTzW1UzWlEdPYnDG-Ew.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*W_30Jq9OLvNoI0XDNvdM-Q.png)

Get service in the ArgoCD namespace by running the following command

```c
kubectl get svc -n argocd
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*hdLI5ThlpoGvfwDBFJpCKQ.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Cntq-zboXN9_76U9X080dg.png)

After successfully configuring ArgoCD, we can now proceed to update the final part of our workflow code.

This final stage of the workflow updates the `deployment.yaml` file with the new Docker image tag (based on the latest commit SHA), commits and pushes the change to the main branch, and then triggers an ArgoCD sync. This ensures that ArgoCD detects the updated manifest and automatically deploys the new version to the cluster.

```c
# 🔄 Update deployment.yaml with the new image tag
- name: Update deployment.yaml with newly built image
  run: |
    git config user.name "${{ secrets.GIT_USERNAME }}"         # Set Git username
    git config user.email "${{ secrets.GIT_EMAIL }}"           # Set Git email
    git fetch origin                                           # Fetch latest updates
    git checkout main                                          # Switch to main branch
    git pull origin main                                       # Pull latest changes
    sed -i "s+${{ secrets.DOCKERHUB_USERNAME }}/my-app.*+${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}+g" manifest/deployment.yaml
    # Replace old image tag in deployment.yaml with the new one using current commit SHA

# 💾 Commit and push the updated deployment.yaml back to GitHub
- name: Commit and Push Updated deployment.yaml
  run: |
    git config user.name "${{ secrets.GIT_USERNAME }}"         # Configure Git user again
    git config user.email "${{ secrets.GIT_EMAIL }}"
    git remote set-url origin https://$GIT_USERNAME:$PERSONAL_ACCESS_TOKEN@github.com/${{ github.repository }}.git
    git fetch origin
    git checkout main
    git pull origin main
    git add .                                                  # Stage all changes
    git commit -m "Update image to my-app:${{ github.sha }}"   # Commit with message
    git push origin main                                       # Push changes to GitHub

# Trigger ArgoCD to sync the app and deploy the new image
- name: Refresh ArgoCD App and Sync
  run: argocd app sync my-app                                  # Force sync with ArgoCD to apply updated manifest
```

After the update, ArgoCD automatically syncs the application and replaces the deployment with the newly built image. As shown below, the application has been successfully updated. You can make further code changes to test and confirm this behavior.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2VXoMP-xuHa4MPqszuGqcg.png)

As shown in the ArgoCD dashboard, the application is successfully synced and up to date with the latest changes.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*cuqfX3q3fwNspb-637LUIQ.png)

**The whole workflow**

This GitHub Actions workflow automates a GitOps CI/CD pipeline using **GitHub Actions** and **ArgoCD** to build, scan, and deploy a Dockerized Node.js app to Kubernetes.

- It triggers on every push to the `main` branch.
- It uses secrets for sensitive info like DockerHub credentials, ArgoCD login, and Git config.
- The workflow has two jobs: **build** and **deploy**.
- The **build** job:
- Check out the code.
- Sets up Node.js and installs dependencies.
- Builds a Docker image tagged with the commit SHA.
- Scans the image for vulnerabilities using Trivy.
- Logs into DockerHub and pushes the image.
- The **deploy** job (runs after the build finishes):
- Check out the repo again.
- Installs `kubectl` the ArgoCD CLI tools.
- Logs into the ArgoCD server.
- Updates the Kubernetes deployment manifest with the new Docker image tag.
- Commits and pushes the updated manifest back to the repo.
- Syncs ArgoCD to apply the new deployment to the Kubernetes cluster.
```c
name: Gitops pipeline with Argocd

on:
  push:
    branches:
      - main   # Trigger workflow on push to main branch

env:
  # Secrets injected as environment variables for use in steps
  PERSONAL_ACCESS_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
  ARGOCD_PASSWORD: ${{ secrets.ARGOCD_PASSWORD }}
  ARGOCD_USERNAME: ${{ secrets.ARGOCD_USERNAME }}
  ARGOCD_SERVER: ${{ secrets.ARGOCD_SERVER }}
  GIT_EMAIL: ${{ secrets.GIT_EMAIL }}
  GIT_USERNAME: ${{ secrets.GIT_USERNAME }}
  
jobs:
  build:
    runs-on: ubuntu-latest  # Use latest Ubuntu runner
    steps:
      - name: checkout code
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          fetch-depth: 0   # Fetch full git history for accurate tagging

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '14'   # Use Node.js v14

      - name: Install Node.js dependencies
        run: npm install   # Install dependencies from package.json

      - name: Build Docker image
        run: docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha}} .
        # Build Docker image tagged with commit SHA

      - name: Scan Docker Image with Trivy
        run: docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}
        # Run vulnerability scan on image using Trivy

      - name: Log in to DockerHub
        run: echo "${{ secrets.DOCKERHUB_TOKEN }}" | docker login -u "${{ secrets.DOCKERHUB_USERNAME }}" --password-stdin
        # Authenticate to DockerHub with token

      - name: Push Docker image to DockerHub
        run: docker push ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}
        # Push tagged Docker image to DockerHub registry

  deploy:
    needs: build    # Wait for build job to finish
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          fetch-depth: 0  # Get full git history

      - name: Install kubectl
        run: |
          curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.30.7/2024-12-12/bin/linux/amd64/kubectl
          chmod +x ./kubectl
          sudo mv ./kubectl /usr/local/bin/kubectl
        # Download and install kubectl CLI for Kubernetes interaction

      - name: Install ArgoCD CLI
        run: |
          curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
          chmod +x argocd
          sudo mv argocd /usr/local/bin/argocd
        # Download and install ArgoCD CLI tool

      - name: Login to ArgoCD
        run: |
          argocd login ${{ secrets.ARGOCD_SERVER }} \
            --username ${{ secrets.ARGOCD_USERNAME }} \
            --password ${{ secrets.ARGOCD_PASSWORD }} \
            --insecure
        # Authenticate ArgoCD CLI with the ArgoCD server

      - name: Update deployment.yaml with newly built image
        run: |
          git config user.name "${{ secrets.GIT_USERNAME }}"
          git config user.email "${{ secrets.GIT_EMAIL }}"
          git fetch origin
          git checkout main
          git pull origin main
          # Show current directory and deployment file content (for debugging)
          pwd
          cat manifest/deployment.yaml
          # Replace image tag in deployment.yaml with new Docker image tagged by commit SHA
          sed -i "s+${{ secrets.DOCKERHUB_USERNAME }}/my-app.*+${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}+g" manifest/deployment.yaml
          cat manifest/deployment.yaml
        # Updates Kubernetes manifest to use the new image

      - name: Commit and Push Updated deployment.yaml
        run: |
          git config user.name "${{ secrets.GIT_USERNAME }}"
          git config user.email "${{ secrets.GIT_EMAIL }}"
          git remote set-url origin https://$GIT_USERNAME:$PERSONAL_ACCESS_TOKEN@github.com/${{ github.repository }}.git
          git fetch origin
          git checkout main
          git pull origin main
          git add .
          git commit -m "Update image to my-app:${{ github.sha }}"
          git push origin main
        # Commit and push updated manifest back to the repo

      - name: Refresh ArgoCD App and Sync
        run: argocd app sync my-app
        # Tell ArgoCD to sync the application, deploying the new image to Kubernetes
```

## Recap

**What ArgoCD Does:**

- Monitors the `manifest/` directory
- Pulls the latest commits automatically
- Syncs deployments on Kubernetes
- Self-healing manual changes in the cluster

**Final Results:**

- CI builds and pushes images to DockerHub
- CD updates `deployment.yaml` automatically
- ArgoCD syncs changes to Kubernetes

## Conclusion

We built a GitOps-based CI/CD pipeline using GitHub Actions and ArgoCD to deploy a Node.js app to a Kubernetes cluster on AWS EC2. The pipeline handles containerization, image scanning, and automated deployments. This setup ensures reliable, traceable, and hands-free delivery, all powered by modern DevOps best practices.

A dedicated Cloud DevOps Eng. with a passion for streamlining development and operations processes in the cloud. Am also passionate about sharing knowledge.

## More from Victor wasonga onyango

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--56628a133bc2---------------------------------------)