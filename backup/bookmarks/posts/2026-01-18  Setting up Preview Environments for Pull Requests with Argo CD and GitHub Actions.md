---
title: Setting up Preview Environments for Pull Requests with Argo CD and GitHub Actions
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://medium.com/@nsalexamy/setting-up-preview-environments-for-pull-requests-with-argo-cd-and-github-actions-9187eef90006
author:
  - "[[Young Gyu Kim]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ZcUyA3p0a5SC8rKK89XR8A.png)

- **YouTube Tutorial Video(short version — 2:14)**: [https://youtu.be/SomxvwBKemI](https://youtu.be/SomxvwBKemI)
- **YouTube Tutorial Video(long version — 13:47)**: [https://youtu.be/EmObZGBp1x8](https://youtu.be/EmObZGBp1x8)

## “It works on my machine” ¯\\\_(ツ)\_/¯

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*UuIL6dDlL-vV96ybumiQig.png)

Figure 1. The classic developer dilemma

We’ve all heard it — or said it — before: **“But it works on my machine!”**

It is a frustratingly common scenario where a feature works perfectly in a local development environment but fails mysteriously when deployed to production. This often happens because local environments (like Docker Compose or Minikube) drift from the actual production configuration over time.

We can solve this by setting up **Preview Environments**.

**The Idea:** When you open a Pull Request (PR), we automatically spin up a temporary, isolated environment that mirrors production.

1. **On Open PR:** CI builds a unique image (e.g., `pr-123`). CD deploys it to a temporary URL (e.g., `[https://pr-123.myapp.com](https://pr-123.myapp.com/)`).
2. **Verify:** QA, Product Managers, and other developers can click the link and test the feature **exactly** as it will run in production.
3. **On Close PR:** The environment and images are automatically cleaned up to save resources.

This tutorial guides you through automating this entire workflow using **GitHub Actions** and **Argo CD**.

## Introduction

By the end of this guide, you will be able to provide your team with fully automated preview environments. This enables “shift-left” testing, allowing you to catch integration issues **before** merging to the main branch.

This document covers:

- **GitHub Actions CI**: Building and pushing ephemeral Docker images for PRs.
- **GitHub Actions Cleanup**: Automatically deleting images when PRs are closed.
- **Argo CD ApplicationSet**: Dynamically creating and deleting Kubernetes environments for each PR.
- **Gateway API**: Exposing each preview environment with a unique URL.

## Prerequisites & References

This tutorial assumes familiarity with concepts covered in our previous guides:

- **Gateway API & Ingress**: [Hostname based Gateway API Service using Traefik, ALB, and Route 53](https://youtu.be/qjaFVdAZ1xk)
- **Argo Rollouts**: [Canary Deployments with Argo Rollouts](https://youtu.be/9MBhWIrkWd0)
- **CI/CD Architecture**: [Modern CI/CD Architecture with GitHub Actions, Argo CD and Argo Rollouts](https://youtu.be/qc42aUjQyGg)

## Why Preview Environments?

Before we build, let’s briefly look at **why** this is a game-changer for DevOps standards.

## The Standard Workflow vs. The “Advanced” Workflow

### Testing

- **Standard workflow**: Local only (Docker/Kind) until merge.
- **Advanced workflow**: Real Kubernetes environment per PR.

### Feedback Loop

- **Standard workflow**: Slow. Bugs found after merge to Dev/Staging.
- **Advanced workflow**: Fast. Bugs found **in the PR** before merge.

### Stakeholder Review

- **Standard workflow**: PMs verify only after deployment to Staging.
- **Advanced workflow**: PMs can verify the live feature immediately on the PR.

### Cost & Complexity

- **Standard workflow**: Low complexity. Low resource usage.
- **Advanced workflow**: Higher setup complexity. Higher resource usage (but ephemeral).

### Summary

While setting this up requires more initial effort and cloud resources, the ability to catch bugs early and unblock effective code reviews usually outweighs the costs for active teams.

## Step 1: GitHub Token Setup

To allow Argo CD to see your Pull Requests and comments, it needs a GitHub Personal Access Token (PAT).

1. **Create a PAT**: Go to GitHub Developer Settings and create a token.
- **Public Repo**: Requires `public_repo` scope.
- **Private Repo**: Requires `repo` (full control of private repositories) scope.
- **Best Practice**: Create a fine-grained token with read-only access to the specific repositories you need.

**2\. Create a Kubernetes Secret**: Argocd needs this token to authenticate with GitHub.

github-token-secret.yaml

```c
apiVersion: v1
kind: Secret
metadata:
  name: service-foundry-web-github-token
  namespace: argocd
type: Opaque
stringData:
  token: ghp_yourGithubTokenHere # <1>
```
1. Replace this with your actual GitHub PAT.

Apply it to your cluster:

```c
kubectl apply -f .github-token-secret.yaml
```

## Step 2: GitHub Actions for CI (Build & Push)

We need a workflow that triggers whenever a developer interacts with a Pull Request. This workflow will build the docker image and push it to the container registry with a tag unique to that PR (e.g., `pr-123`).

Let’s look at the workflow file `.github/workflows/pull-request-ci.yaml`.

```c
name: Pull Request CI
```
```c
on:
  pull_request:
    types: [opened, synchronize, reopened]  # <1>jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write  # <2>    steps:
      - name: Checkout repository
        uses: actions/checkout@v4      # <3>
      - name: Delete existing package version
        uses: actions/delete-package-versions@v5
        with:
          package-name: 'service-foundry-web'
          package-type: 'container'
          min-versions-to-keep: 0
          delete-only-untagged-versions: 'false'
          ignore-versions: '^(?!pr-${{ github.event.number }}$).*'
        continue-on-error: true      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3      - name: Log in to the Container registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          # <4>
          tags: ghcr.io/${{ github.repository_owner }}/service-foundry-web:pr-${{ github.event.number }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Detailed Explanation:**

1. **Trigger**: We want this to run when a PR is first `opened`, when new code is pushed (`synchronize`), or if it’s `reopened`. This ensures the preview is always up to date.
2. **Permissions**: We need `packages: write` permission to push the Docker image to GitHub Container Registry (GHCR).
3. **Cleanup Strategy**: This is a clever step! Since we reuse the tag `pr-{number}` for every update to the same PR, we want to delete the **old** image layer associated with this tag before pushing a new one. This keeps our registry clean and ensures we don’t hit storage limits with orphaned layers. The regex `^(?!pr-${{ github.event.number }}$).*` ensures we only target the specific version for this PR.
4. **Dynamic Tagging**: We tag the image using the PR number: `pr-${{ github.event.number }}`. This is the **key contract** between our CI and CD. Argo CD will look for exactly this tag.

## Step 3: GitHub Actions for Cleanup

When a Pull Request is merged or closed, we don’t need the docker image anymore. Leaving it would just clutter the registry and cost money.

We use a separate workflow `.github/workflows/pull-request-cleanup.yaml` for this.

```c
name: Pull Request Cleanup
```
```c
on:
  pull_request:
    types: [closed] # <1>jobs:
  delete-image:
    runs-on: ubuntu-latest
    permissions:
      packages: write
    steps:
      # <2>
      - name: Delete image from Container Registry
        uses: actions/github-script@v7
        with:
          script: |
            const packageName = 'service-foundry-web';
            const tag = \`pr-${context.issue.number}\`;
            const owner = context.repo.owner;
            console.log(\`Searching for ${packageName}:${tag} in ${owner}...\`);            // ... (helper function to fetch versions) ...            try {
              // ... (logic to find the package version ID) ...              if (version) {
                console.log(\`Found version ${version.id} with tag ${tag}. Deleting...\`);
                // <3>
                if (isOrg) {
                  await github.rest.packages.deletePackageVersionForOrg({
                    package_type: 'container',
                    package_name: packageName,
                    org: owner,
                    package_version_id: version.id
                  });
                } else {
                  await github.rest.packages.deletePackageVersionForUser({ /* ... */ });
                }
                console.log('Version deleted successfully.');
              }
            } catch (error) {
              // ...
            }
```

**Detailed Explanation:**

1. **Trigger**: strict execution only when the PR is `closed`.
2. **GitHub Script**: Instead of a simple action, we use a Javascript script (via `actions/github-script`) because the logic is slightly complex: we need to find the specific **Package Version ID** associated with the tag `pr-{number}`. The standard API requires the ID, not just the tag name, to perform a deletion.
3. **Context Matters**: The script handles both User accounts and Organization accounts, as the API endpoints differ (`deletePackageVersionForOrg` vs `deletePackageVersionForUser`). This makes the workflow portable.

## Step 4: Argo CD ApplicationSet

This is where the magic happens. The **ApplicationSet** controller in Argo CD acts as a factory. It watches for Pull Requests and automatically generates a new Argo CD `Application` for each one.

## The ApplicationSet Configuration

File: `service-foundry-web-pr-appset.yaml`

```c
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: service-foundry-web-pr-previews
  namespace: argocd
spec:
  goTemplate: true
  generators:
    - pullRequest:
        github:
          owner: nsalexamy
          repo: service-foundry-web
          tokenRef:
            secretName: service-foundry-web-github-token # <1>
            key: token
          labels:
            - preview   # <2>
        requeueAfterSeconds: 120  # <3>
```
```c
template:
    metadata:
      name: 'service-foundry-web-pr-{{.number}}' # <4>
      labels:
        previews.argocd.argoproj.io/enabled: "true"
    spec:
      project: service-foundry
      source:
        repoURL: 'git@github.com:nsalexamy/service-foundry-argocd.git'
        targetRevision: 'HEAD'
        path: 'demo-apps/service-foundry-web-gitops/pr' # <5>
        helm:
          parameters:
            - name: "web.image.tag"
              value: "pr-{{.number}}" # <6>
            - name: "prNumber"
              value: "{{.number}}"      destination:
        server: 'https://kubernetes.default.svc'
        namespace: 'service-foundry-web-pr-{{.number}}' # <7>      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true  # <8>
```

**Deep Dive:**

1. **Authentication (**`tokenRef`**)**: Uses the secret we created in Step 1 to call the GitHub API.
2. **Label Filter**: We don’t want **every** PR to spawn an environment (it could be costly!). This filter ensures we only create previews for PRs labeled `preview`.
3. **Polling (**`requeueAfterSeconds`**)**: Checks for updates every 2 minutes. This creates a small buffer time for the CI to finish building the image before Argo CD tries to deploy it.
4. **Dynamic Naming**: The application name includes the PR number (`{{.number}}`), ensuring uniqueness.
5. **Subchart Strategy**: We point to a specific folder `…​/pr`. This folder contains a Helm chart wrapper that overrides the standard values with PR-specific configurations.
6. **Parameter Injection**: We inject the `pr-{{.number}}` tag. This tells the Helm chart to use the image our CI workflow (Step 2) just built.
7. **Namespace Isolation**: Each PR gets its own namespace (`service-foundry-web-pr-123`). This prevents conflicts between different PRs and the main dev environment.
8. **Namespace Management**: `CreateNamespace=true` ensures the namespace is created on the fly. When the Application is deleted (PR closed), Argo CD will also delete this namespace, cleaning up everything.

## The Helm Chart Wrapper

In the `pr/` directory, we have a "Wrapper Chart". It doesn’t duplicate the original chart; it depends on it and overrides specific values.

**pr/Chart.yaml**

```c
apiVersion: v2
name: service-foundry-web-pr
version: 0.1.0
dependencies:
  - name: service-foundry-web
    version: 0.1.0
    repository: file://../chart-home/service-foundry-web
    alias: web
```

This chart defines a dependency on the main `service-foundry-web` chart. Note the `alias: web`. This is critical because it allows us to override values for that dependency under the `web:` key in our values file.

**pr/templates/namespace.yaml**

```c
apiVersion: v1
kind: Namespace
metadata:
  name: service-foundry-web-pr-{{ .Values.prNumber }}
```

We explicitly define the namespace here. This ensures that when Argo CD manages this application, it also treats the namespace as a managed resource. If we simply relied on Argo CD’s `CreateNamespace=true` sync option (which we used earlier), the namespace might be orphaned if the Application is deleted without a cascade. Including it here guarantees it gets cleaned up.

**pr/values.yaml**

```c
prNumber: "0000" # Placeholder
```
```c
web:
  replicaCount: 1 # Save resources
  image:
    tag: "pr-0000" # Placeholder  rollouts:
    enabled: true
    strategy:
      blueGreen:
        activeService: "service-foundry-web"
        previewService: "service-foundry-web-preview"
```

We also add a dynamic **HTTPRoute** to expose this environment.

**pr/templates/httproute.yaml**

```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: service-foundry-web-pr-{{ .Values.prNumber }}
spec:
  parentRefs:
    - name: traefik-gateway
      namespace: traefik
  hostnames:
    - service-foundry-web-pr-{{ .Values.prNumber }}.servicefoundry.org # 1
  rules:
    - matches:
      - path:
          type: PathPrefix
          value: /
      backendRefs:
        - name: service-foundry-web
          port: 80
```
1. **Dynamic Hostname**: This is the best part! The URL is predictable. If your PR is `#42`, your URL will be `[https://service-foundry-web-pr-42.servicefoundry.org](https://service-foundry-web-pr-42.servicefoundry.org/)`.

## Demo Walkthrough

Let’s see this in action. The flow is seamless for the developer.

## 1\. Developer Work

You are working on a new feature. You make your code changes and commit them.

```c
git checkout -b feature/amazing-ui
git commit -am "Update background color to neon pink"
git push origin feature/amazing-ui
```

Then, you go to GitHub and click **Create Pull Request**.

## 2\. Triggering the Preview

By default, nothing happens (to save costs). To see your work live, simply add the label `preview` to your PR.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*MdFQJy1DDvKZB6BaUaOF4g.png)

Figure 2. Adding the preview label on GitHub

**(Alternatively, use the CLI:** `gh pr edit 42 --add-label "preview"`**)**

## 3\. The Automation Kicks In

1. **GitHub Actions** wakes up. The `Pull Request CI` starts building your docker image.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*JvnPZgL_pAykBUU9AGQavA.png)

Figure 3. Action building the image

1. Within minutes, a new package appears in your registry tagged `pr-42`.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*aJ-r9abl_oJmfhJpCv62pw.png)

Figure 4. Docker image pushed to registry

1. **Argo CD** detects the labeled PR. The ApplicationSet generates a new Application: `service-foundry-web-pr-42`.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Oj2LkChPaofeHRcFje0jJQ.png)

Figure 5. Argo CD spawns a new app

1. Kubernetes spins up the pods in a new namespace `service-foundry-web-pr-42`.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0dF5XDCpeRINnOtEF7_NZw.png)

Figure 6. Kubernetes resources created

## 4\. Verification

You (and your Product Manager) can now visit `[https://service-foundry-web-pr-42.servicefoundry.org](https://service-foundry-web-pr-42.servicefoundry.org/)`.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Wsaepu8NPgSVh2d8Z3zPvw.png)

Figure 7. Your specific changes, live on the internet!

## 5\. Cleanup

Once the PR is approved and merged (or closed), the cleanup process begins automatically:

1. **GitHub Actions** deletes the `pr-42` image from the registry.
2. **Argo CD** detects the PR is closed and deletes the `service-foundry-web-pr-42` Application.
3. **Kubernetes** deletes the namespace and all resources within it.

No trash left behind!

## Conclusion

Congratulations! You have successfully implemented a sophisticated **Preview Environment** workflow.

By automating the creation and destruction of these environments, you’ve removed the **“it works on my machine”** barrier. Developers can iterate faster, QA can test independently, and valid feedback comes earlier in the development lifecycle.

In the next tutorial, we will apply these concepts to a more complex, multi-service application to see how this scales.

## More from Young Gyu Kim

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--9187eef90006---------------------------------------)