---
title: "How We Load Test Argo CD at Scale: 1,000 vClusters with GitOps on Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/how-we-load-test-argo-cd-at-scale-1-000-vclusters-with-gitops-on-kubernetes-d8ea2a8935b6"
author:
  - "[[Artem Lajko]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@artem_lajko)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-d8ea2a8935b6---------------------------------------)

Featured

> **Note:** In this blog, we share how we performed a high-scale load test on an Argo CD setup using principles, [vCluster](https://www.vcluster.com/), and a Kubernetes platform — backed by over €20,000 (instead of €200.000) worth of infrastructure resources. This test was run on [**STACKIT**](https://www.stackit.de/en/), a German , under heavy load conditions.
> 
> ⚠️ **Heads-up**: This is a deep-dive technical blog. To follow along, you should be familiar with [Helm](https://helm.sh/), [Argo CD](https://argo-cd.readthedocs.io/en/stable/), [ApplicationSets](https://argo-cd.readthedocs.io/en/latest/user-guide/application-set/), [App-of-Apps pattern](https://medium.com/@andersondario/argocd-app-of-apps-a-gitops-approach-52b17a919a66), vCluster, and the basics of GitOps.
> 
> 🚨 Missed our live session? No problem! The full webinar **recording** is now available. If you’re interested in seeing our Argo CD setup and testing strategies in action, grab a coffee and watch the full 90-minute session here:  
> [https://www.youtube.com/watch?v=0XEWn4VmiDE](https://www.youtube.com/watch?v=0XEWn4VmiDE&t=5210s)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*IuVJX3LQXNvCVEJlXNBp6w.png)

Fig. 0: 1,000 vClusters? What Could Possibly Go Wrong?

## Introduction: The Challenge of Multi-Tenancy at Scale

> “Building a multi-tenant GitOps platform with Argo CD without properly testing its limits is like flying blind.”

That was our starting point. Multi-tenancy in Kubernetes is complex. You don’t just deploy tools — you build the platform others will depend on. And while Argo CD is a powerful cornerstone for GitOps, one question remained:  
**How far can it actually scale?**

In this blog, we share our approach to stress-testing Argo CD with up to **1,000 virtual clusters (vClusters)** and an infrastructure setup costing over **€20,000–40.000** — all hosted on **STACKIT**, a German hyperscaler, under real load conditions.

## Why We Did This

As a platform team, our mission was to provide a tool that encapsulates best practices for Kubernetes platform operations — not for app developers, but for the platform engineers themselves.  
That’s why we built [**Kubara**](https://www.youtube.com/watch?v=U4AgmEo3oV8&t=1s), a templating binary that helps bootstrap a secure, GitOps-enabled Kubernetes control plane. Kubara works in air-gapped environments, public cloud, or even on the edge — and simplifies multi-cluster, multi-tenant operations.

(We’ll cover Kubara itself in a separate blog — this post is all about the Argo CD load test. Or rather scale tests.)

## What the Platform Setup Does

[Our architecture](https://www.youtube.com/watch?v=U4AgmEo3oV8&t=1s) enables:

- Bootstrapping a **control plane cluster** with all necessary tooling
- Adding **fleet/workload clusters** dynamically
- Deploying apps from the control plane across fleets using **Argo CD, GitOps, and multi-tenancy patterns**

Yes, you could run dedicated Argo CD instances on each cluster — but we wanted to know:  
**How far can one control plane Argo CD instance go?**

## The Big Questions We Asked

As soon as we got the setup running, we hit the obvious bottleneck:

> *✅ It works in demos.  
> ❓ But how far can you push it?*

We needed answers:

- At what point does Argo CD start to fail?
- How many clusters can one Argo CD instance realistically handle?
- How many applications can it sync before the UI slows to a crawl?
- Which Argo CD components need tuning under load?
- Can we optimize it without introducing extra tools like Kargo?

Problem: we had no “real” teams or projects using the platform yet. They were just getting started — and expected us to figure it out for them.

So we did.

## What the Market Says

Before jumping in, we looked at benchmarks and reports from the community:

[From Argo CD’s own docs:](https://argo-cd.readthedocs.io/en/release-1.8/roadmap/#performance)

> ***2000+ applications****: UI performance degrades beyond 1000 apps  
> ****100+ clusters****: Controller needs horizontal scaling and sharding  
> ****Monorepos****: Manifest generation becomes a bottleneck beyond 50 apps*

From our own past projects:

> *1,500 applications across 50 clusters worked — but syncing all apps could take up to* ***10 minutes****, depending on cluster location and network.*

From AI tools like Gemini 2.5 Flash (based on [Codefresh](https://www.youtube.com/watch?v=p8BluR5WT5w) running on GKE [Argo CD HA](https://codefresh.io/learn/argo-cd/a-comprehensive-overview-of-argo-cd-architectures-2025/)):

> *Without tuning:  
> • ~1,500 apps  
> • ~50 clusters  
> • ~200 devs  
> • ~14,000 K8s objects*

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*4vgqSSwzGD14O04530TKRA.png)

Fig. 1: So far, Argo CD is just stretching

Argo CD can still handle this without breaking a sweat — but what comes next is a different story. I hope gemini didn’t hallucinate too much.

> *With tuning:  
> • 10,000+ apps  
> • 250–500 clusters  
> • Performance depends heavily on horizontal scaling, sharding, and infrastructure*

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*XNW6dfsYxPNReIsG60lqaQ.png)

Fig. 2: Argo CD be like: “You did what now?

I believe this is achievable, but it requires significant adaptation and optimization — including sharding, *HorizontalPodAutoscaler* ([HPA](https://kubernetes.io/de/docs/tasks/run-application/horizontal-pod-autoscale/)) tuning, and potentially agent-based approaches.

Those were good references — but we were curious. We wanted to test it ourselves, under **real** conditions.

Lets take a look on our Architecture setup and workflow for the scale out test.

## Architecture & Workflow: How We Scaled Argo CD with 1,000 vClusters

To understand how we pulled off the load test, let’s first look at the architecture behind it.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*kJF2cG4kX4D2ACcWDWZWPA.png)

Fig. 3: Architecture Setup for the Scale-Out Test

At the core of our setup is **GitOps-first design** using Argo CD, Helm, and vCluster. The key building blocks:

### 1\. Terraform + Helm Catalog

We maintain a **service catalog** using Terraform for infrastructure provisioning and Helm for Kubernetes resources. [Umbrella charts](https://m.youtube.com/watch?v=Ps_IdnfVO7k&pp=0gcJCc0AaK0XXGki) under a `managed` folder provide a baseline setup, while overlays allow per-cluster customization.

We use **ApplicationSets with Cluster** [**Generators**](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Cluster/), which apply services based on cluster labels — enabling targeted deployment of tools like [External-DNS](https://github.com/kubernetes-sigs/external-dns), [External-Secrets-Operator (ESO)](https://external-secrets.io/latest/), [Ingress-NGINX](https://github.com/kubernetes/ingress-nginx), etc.

### 2\. Control Plane Node Pool — Infra

A dedicated node pool runs all the shared infrastructure tools. These include:

- External Secrets Operator
- [Cert-Manager](https://cert-manager.io/)
- Ingress NGINX
- Kube-Prometheus Stack  
	…all deployed via ApplicationSets across clusters.

### 3\. vCluster Pooling Strategy — App of Apps

Running 1,000 real Kubernetes clusters would easily cost us ~€200,000 — unacceptable. Instead, we use **vCluster** to simulate isolated clusters inside a shared pool.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*AfWqeLBmZ4dfqC2VW3-NiA.png)

Fig. 4: Smallest Kubernetes Cluster on STACKIT — Approx. €200

We spin up a dynamic node pool called “app” on STACKIT just for vClusters. The pool is **tainted**, and vClusters are configured with appropriate `tolerations` so only they are scheduled there. This approach brought our costs down to ~€20,000.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*BPe70uNU2quQDN7UcUEkWw.png)

Fig. 5: Estimated Cost for App Pool (25× S1.6 Nodes) — €20,000

### 4\. GitOps-Driven vCluster Onboarding

Every vCluster gets its own Argo CD Application (App of Apps) and is onboarded via GitOps. We use [**ExternalSecrets**](https://external-secrets.io/v0.4.4/api-externalsecret/) and **Vault** to manage credentials securely. Argo CD then connects to each vCluster as a cluster target and deploys services accordingly to the labels.

## Workflow: From 0 up to 1,000 vClusters

This section describes the full process of how we used GitOps to scale from 0 up to 1,000 vClusters, establish secure cluster connections, and roll out workloads dynamically using Argo CD.

Let’s break down the end-to-end workflow.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*xkCreMiBfY2vfi43Fz6LJw.png)

Fig. 6: Workflow Part 1 — Generate vCluster Applications

**Step 1: Generate Argo CD Applications (using plain YAML templates)**

We start by setting environment variables specific (1) to our STACKIT and Vault context. The most important one:

```c
export CLUSTER_COUNT=100
```

This defines how many Argo CD `[Application](https://argo-cd.readthedocs.io/en/latest/user-guide/application-specification/)` resources we want to generate.

Instead of Helm, we use a **plain YAML template** with Bash-based variable substitution (e.g., `${CLUSTER}` placeholders). This template defines one Argo CD Application per vCluster.

Here’s a simplified excerpt from the raw YAML template (`app-vcluster-template.yaml`):

```c
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ${CLUSTER}
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  destination:
    namespace: ${CLUSTER}
    server: "https://kubernetes.default.svc"
  sources:
    - repoURL: https://...@dev.azure.com/..../_git/load-test
      targetRevision: main
      path: "./managed-service-catalog/helm/vcluster"
      helm:
        ignoreMissingValueFiles: true
        releaseName: "${CLUSTER}"
        valueFiles:
          - "values.yaml"
        values: |
          vcluster:
            controlPlane:
              coredns:
                deployment:
                  tolerations:
                    - key: "role"
                      operator: "Equal"
                      value: "app"
                      effect: "NoSchedule"
                  nodeSelector:
                    role: "app"
              proxy:
                extraSANs:
                  - ${CLUSTER}.loadtest.stackit.run
              ingress:
                enabled: true
                host: "${CLUSTER}.loadtest.stackit.run"
                pathType: ImplementationSpecific
                annotations:
                  nginx.ingress.kubernetes.io/backend-protocol: HTTPS
                  nginx.ingress.kubernetes.io/ssl-passthrough: "true"
                  nginx.ingress.kubernetes.io/ssl-redirect: "true"
                  cert-manager.io/cluster-issuer: letsencrypt-prod
                spec:
                  ingressClassName: nginx
              statefulSet:
                scheduling:
                  nodeSelector:
                    role: "app"
                  tolerations:
                    - key: "role"
                      operator: "Equal"
                      value: "app"
                      effect: "NoSchedule"
              backingStore:
                etcd:
                  deploy:
                    statefulSet:
                      scheduling:
                        nodeSelector:
                          role: "app"
                        tolerations:
                          - key: "role"
                            operator: "Equal"
                            value: "app"
                            effect: "NoSchedule"
  project: controlplane-production
  ignoreDifferences:
    - group: apps
      version: v1
      kind: StatefulSet
      name: ${CLUSTER}
      namespace: ${CLUSTER}
      jsonPointers:
        - /spec/updateStrategy
        - /spec/volumeClaimTemplates
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
      allowEmpty: true
    syncOptions:
      - CreateNamespace=false
      - PruneLast=true
      - FailOnSharedResource=true
      - RespectIgnoreDifferences=true
      - ApplyOutOfSyncOnly=true
      - ServerSideApply=true
```

We then run the script `1-create-applications.sh(2)`, which loops through the defined cluster count and renders one YAML file per vCluster:

```c
OSX  …/load-test    main ● ?  ./1-create-applications.sh                               14.06.25  20:34:37  ske-loa-pro/default ⎈ 
🔄 Generating 100 ArgoCD Application manifests using 'app-vcluster-template.yaml'…
• vcluster-0 → apps/vcluster-0.yaml
• vcluster-1 → apps/vcluster-1.yaml
• vcluster-2 → apps/vcluster-2.yaml
• vcluster-3 → apps/vcluster-3.yaml
• vcluster-4 → apps/vcluster-4.yaml
• vcluster-5 → apps/vcluster-5.yaml
• vcluster-6 → apps/vcluster-6.yaml
• vcluster-7 → apps/vcluster-7.yaml
• vcluster-8 → apps/vcluster-8.yaml
.....
```

These YAMLs are committed into the Git repo under the `apps/` folder.

Argo CD uses the **App-of-Apps pattern** and watches this folder. Once committed, the controller automatically picks up and applies the Applications — each managing its own vCluster deployment.

At this point, 100 vClusters exist in the platform — isolated, scheduled on a dedicated node pool, and ready to be linked to Argo CD for full lifecycle management.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*AXzMqKFSKwH1aawW5gGj5g.png)

Fig. 7: 100 vClusters Created — Wuhu!

**Step 2: Sync vCluster Kubeconfigs to Vault**

At this stage, the vClusters exist, but Argo CD doesn’t know how to connect to them. We need to fetch each vCluster’s `kubeconfig` and store it securely in **Vault**, which acts as a backend for the **External Secrets Operator (ESO)**.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CxJmash6gzH8G1jH6z13Ew.png)

Fig. 8: Step 2 — Retrieve vCluster Kubeconfigs and Push to Vault

We run the `2-sync-vclusters.sh (3)` script, which:

1. Authenticates against Vault
2. Extracts and escapes the `kubeconfig`
3. Patches Vault secret fields for each cluster
4. Cleans up local temp files

Example log output:

```c
OSX  …/load-test    main ● ?  ./2-sync-vclusters.sh                                    14.06.25  20:42:51  ske-loa-pro/default ⎈ 
🔐 Logging in to Vault...
→ Received Vault token
⏳ Generating kubeconfig for vcluster-0
📝 Escaping kubeconfig to JSON
💾 Preparing patch payload
📡 Patching Vault secret 'my_clusters' → field 'vcluster-0'
{"request_id":"00000000-0000-0000-0000-000000000000","lease_id":"","renewable":false,"lease_duration":0,"data":{"created_time":"2025-06-14T18:43:07.532027Z","custom_metadata":null,"deletion_time":"","destroyed":false,"version":412},"wrap_info":null,"warnings":null,"auth":null}
✓ Patched vcluster-0
🗑  Removed kubeconfig-vcluster-0.yaml and data-vcluster-0.json
⏳ Generating kubeconfig for vcluster-1
📝 Escaping kubeconfig to JSON
💾 Preparing patch payload
📡 Patching Vault secret 'my_clusters' → field 'vcluster-1'
{"request_id":"00000000-0000-0000-0000-000000000000","lease_id":"","renewable":false,"lease_duration":0,"data":{"created_time":"2025-06-14T18:43:08.748387Z","custom_metadata":null,"deletion_time":"","destroyed":false,"version":413},"wrap_info":null,"warnings":null,"auth":null}
✓ Patched vcluster-1
🗑  Removed kubeconfig-vcluster-1.yaml and data-vcluster-1.json
⏳ Generating kubeconfig for vcluster-2
📝 Escaping kubeconfig to JSON
💾 Preparing patch payload
📡 Patching Vault secret 'my_clusters' → field 'vcluster-2'
{"request_id":"00000000-0000-0000-0000-000000000000","lease_id":"","renewable":false,"lease_duration":0,"data":{"created_time":"2025-06-14T18:43:09.907719Z","custom_metadata":null,"deletion_time":"","destroyed":false,"version":414},"wrap_info":null,"warnings":null,"auth":null}
✓ Patched vcluster-2
```

Each vCluster’s credentials are now available to ESO via Vault under the `ClusterSecretStore`.

**Step 3: Connect Argo CD to vClusters and Define Labels**

With kubeconfigs in Vault, we now generate the configuration that tells Argo CD how to connect to the vClusters. Based on labels (6).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ZHSwNkRzHxaMHbsh2d9slg.png)

Fig. 9: Establishing the Connection Between Argo CD and vClusters

We support three variants, using Bash scripts to output the correct YAML values:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*OBQQQ33ylsZRgfopTtHoTQ.png)

Table 0: Three Variants for Generating Load Scenarios

This how `3-1-generate-values.sh` looks like:

```c
#!/usr/bin/env bash
set -euo pipefail

# Usage: CLUSTER_COUNT=5 ./3-1-generate-values.sh > values.yaml
# or: ./3-1-generate-values.sh 5 > values.yaml

# Read cluster count
if [[ -n "${1-}" ]]; then
  CLUSTER_COUNT=$1
elif [[ -n "${CLUSTER_COUNT-}" ]]; then
  CLUSTER_COUNT=$CLUSTER_COUNT
else
  echo "Error: specify CLUSTER_COUNT (e.g. export CLUSTER_COUNT=5 or pass as arg)" >&2
  exit 1
fi

# --- 1) Static preamble ---
cat <<'EOF'
argo-cd:
  configs:
    cm:
      dex.config: |
        connectors:
          - type: github
            id: github
            name: GitHub
            config:
              clientID: $oauth2-credentials:client-id
              clientSecret: $oauth2-credentials:client-secret
              orgs:
                - name: blueprint-sec
      url: https://cp.loadtest.stackit.run/argocd
    params:
      server.basehref: /argocd
      server.insecure: true
      server.rootpath: /argocd
    rbac:
      policy.csv: |
        g, blueprint-sec:kak-team, role:admin
      policy.default: role:readonly
  controller:
    metrics:
      enabled: true
      rules:
        enabled: false
      serviceMonitor:
        additionalLabels:
          monitoring.instance: controlplane-production
        enabled: true
  global:
    domain: cp.loadtest.stackit.run
    imagePullSecrets:
      - name: image-pull-secret
    revisionHistoryLimit: 5
  server:
    ingress:
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt-prod
        nginx.ingress.kubernetes.io/auth-signin: https://$host/oauth2/start?rd=$escaped_request_uri
        nginx.ingress.kubernetes.io/auth-url: https://$host/oauth2/auth
        nginx.ingress.kubernetes.io/backend-protocol: HTTP
        nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
      enabled: true
      ingressClassName: nginx
      path: /argocd
      tls: true
    ingressGrpc:
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt-prod
        nginx.ingress.kubernetes.io/backend-protocol: GRPC
      enabled: true
      ingressClassName: nginx
      path: /argocd
      tls: true
bootstrapValues:
  applicationSets:
    - apps:
        - name: argocd
          path: argo-cd
        - name: kyverno
          path: kyverno
        - name: kyverno-policies
          path: kyverno-policies
        - name: external-secrets
          path: external-secrets
        - name: cert-manager
          path: cert-manager
        - name: cert-manager-lean
          path: cert-manager-leans
        - name: ingress-nginx
          path: ingress-nginx
        - name: metallb
          path: metallb
        - name: external-dns
          path: external-dns
        - name: oauth2-proxy
          path: oauth2-proxy
        - name: longhorn
          path: longhorn
        - name: kube-prometheus-stack
          path: kube-prometheus-stack
        - name: kube-prometheus-stack-lean
          path: kube-prometheus-stack-lean
        - name: loki
          path: loki
        - name: kyverno-policy-reporter
          path: kyverno-policy-reporter
        - name: homer-dashboard
          path: homer-dashboard
        - name: metrics-server
          path: metrics-server
        - name: kro
          path: kro
        - name: kamaji
          path: kamaji
      customerServices:
        path: customer-service-catalog/helm
        repoURL: https://....@dev.azure.com/...../_git/load-test
        targetRevision: main
      managedServices:
        path: managed-service-catalog/helm
        repoURL: https://....go@dev.azure.com/...../_git/load-test
        targetRevision: main
      projectName: controlplane-production
  cluster:
EOF

# --- 2) Dynamic cluster entries ---
for ((i = 0; i < CLUSTER_COUNT; i++)); do
  cat <<EOF
    - additionalLabels:
        kro: disabled
      name: vcluster-${i}
      project: controlplane-production
      remoteRef:
        remoteKey: my_clusters
        remoteKeyProperty: vcluster-${i}
      secretStoreRef:
        kind: ClusterSecretStore
        name: controlplane-production
EOF
done

# --- 3) Static postamble ---
cat <<'EOF'
  dockerPullSecrets:
    - matchNamespaceLabels:
        project-name: controlplane
        stage: production
      name: image-pull-secret
      remoteRef:
        remoteKey: docker_config
        remoteKeyProperty: pull-secret
      secretStoreRef:
        kind: ClusterSecretStore
        name: controlplane-production
  applications:
    - destination:
        serverName: controlplane
      info:
        - name: type
          value: app-of-apps
      name: app-of-apps
      namespace: argocd
      projectName: controlplane-production
      repoPath: apps
      repoUrl: https://.....@dev.azure.com/.../_git/load-test
  projects:
    - description: controlplane-production project
      name: controlplane-production
      namespace: argocd
      orphanedResources:
        ignore:
          - kind: Secret
            name: cert-manager-webhook-ca
        warn: false
      sourceRepos:
        - registry.onstackit.cloud/stackit-edge-cloud-blueprint
inClusterName: controlplane
inClusterSecretLabels:
  argocd: enabled
  cert-manager: enabled
  cilium: enabled
  external-dns: enabled
  external-secrets: enabled
  homer-dashboard: enabled
  ingress-nginx: enabled
  kube-prometheus-stack: enabled
  kyverno: enabled
  kyverno-policies: enabled
  kyverno-policy-reporter: enabled
  loki: enabled
  longhorn: disabled
  metallb: disabled
  metrics-server: disabled
  oauth2-proxy: enabled
  kamaji: disabled
namespace:
  labels:
    project-name: controlplane
    stage: production
secretStoreRef:
  kind: ClusterSecretStore
  name: controlplane-production
EOF
```

Each script generates a Helm values file for the control plane. Example from `3-1-generate-values.sh`:

```c
./3-1-generate-values.sh > customer-service-catalog/helm/controlplane/argo-cd/values.yaml

...
cluster:
    - additionalLabels:
      name: vcluster-0
      project: controlplane-production
      remoteRef:
        remoteKey: my_clusters
        remoteKeyProperty: vcluster-0
      secretStoreRef:
        kind: ClusterSecretStore
        name: controlplane-production
    - additionalLabels:
      name: vcluster-1
      project: controlplane-production
      remoteRef:
        remoteKey: my_clusters
        remoteKeyProperty: vcluster-1
      secretStoreRef:
        kind: ClusterSecretStore
        name: controlplane-production
.....
```

As you can see, this is where the relationship between Argo CD and each vCluster is established. An `ExternalSecret` is created to fetch the kubeconfig from Vault. You can also apply labels directly in the `ExternalSecret`, which are then used to control what gets deployed.

Here’s how it looks when using `3-2-generate-values.sh`:

```c
cluster:
    - additionalLabels:
        kro: enabled
      name: vcluster-0
      project: controlplane-production
      remoteRef:
        remoteKey: my_clusters
        remoteKeyProperty: vcluster-0
      secretStoreRef:
        kind: ClusterSecretStore
        name: controlplane-production
    - additionalLabels:
        kro: enabled
      name: vcluster-1
      project: controlplane-production
      remoteRef:
        remoteKey: my_clusters
        remoteKeyProperty: vcluster-1
      secretStoreRef:
        kind: ClusterSecretStore
        name: controlplane-production
```

You can see the label `kro: enabled` applied to the cluster configuration.

After running:

```c
./3-2-generate-values.sh > customer-service-catalog/helm/controlplane/argo-cd/values.yaml
```

Argo CD will:

- Discover the vCluster
- Pull the kubeconfig via External Secrets
- Deploy workloads based on labels (e.g., [KRO](https://github.com/kro-run/kro) if `kro: enabled` is present)

Alright, let’s bring it all together and take a look at the process in action with this GIF series.

### Putting It All Together (GIF Sequence)

To visualize the full process, we’ve broken it down into short GIFs that show each key step in the vCluster lifecycle:

Step 1:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*JWibAFzaQ1oqETJD0aWRTg.gif)

GIF 0: App-of-Apps creates 10 vClusters

Step 2:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*1aSzZKuw08zN7gnw5WYj-Q.gif)

GIF 1: 2-sync-vclusters.sh pushes kubeconfigs to Vault

Step 3.2:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*bRHaIe61t9MwbKi9KfP-xA.gif)

GIF 2: 3-2-generate-values.sh creates overlays with kro: enabled

the deployment of the [Kubernetes Resource Operator](https://github.com/kro-run/kro) (kro) on each vCluster.

(We trimmed the GIF here to keep it mobile-friendly — syncing and secret creation in Argo CD takes a bit longer.)

Step 3.2 — Continued

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0xoEkY5sol-8lT-hB537sQ.gif)

GIF 3: Argo CD syncs and connects to the new clusters

Final Result:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*L6eIoAy5bZpA6VQkr4rGLg.gif)

GIF 4: Argo CD UI shows synced vClusters and deployed apps

For demonstration purposes, we used just 10 clusters to make the flow easier to follow — but the same pattern scales up to 1,000+ vClusters.

Let’s now look at the use cases we wanted to validate as part of our scale testing.

## Use Cases and Scale Test Scenarios

## Scenario Overview

We tested three configurations:

### Scenario 1: Connect Empty vClusters (No Applications)

**Script:**`3-1-generate-values.sh`  
**Goal:**  
Determine how many clusters Argo CD can handle when no applications are deployed. Focus is purely on connection management and control plane load without manifest syncing.

### Scenario 2: vClusters with One Application Each

**Script:**`3-2-generate-values.sh`  
**Goal:**  
Each vCluster receives one application (Kubernetes Resource Operator / Kro). This simulates a lightweight multi-tenant setup and helps observe behavior as the number of sync targets grows.

### Scenario 3: vClusters with Three Applications Each

**Script:**`3-3-generate-values.sh`  
**Goal:**  
Simulate more realistic workloads where each cluster runs several operationally relevant services (Kro, Cert-Manager, Kube-Prometheus-Stack). This increases overall object count and pressure on both Argo CD and the Kubernetes control plane.

### What We Set Out to Challenge

We took Argo CD in its standard HA configuration (no deep tuning):

- ~1,500 applications
- ~50 clusters
- Monorepo wtih ~500 Apps

These numbers align with community benchmarks and Argo CD’s own roadmap. According to the official docs and experience:

- **2,000+ Applications:** UI becomes noticeably slower; requires architectural optimization.
- **100+ Clusters:** Argo CD controller cannot handle this reliably without horizontal scaling and sharding.
- **Monorepos with >50 apps:** Manifest generation performance degrades. Repository server optimizations are needed.

## Test Scenario 1: Maximum Cluster Connections (No Apps)

We wanted to find out how many clusters we could register in Argo CD before performance or stability issues occur.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*uTfxLRwfw5Wdiq2FHVE5ug.png)

Fig. 10: 500 vClusters Successfully Added to Argo CD

We used `3-1-generate-values.sh` to register each vCluster as a cluster target in Argo CD, but without deploying any applications.

- We scaled up to **500 vClusters** successfully.
- Each vCluster was connected via External Secrets pulling from Vault.
- No manifest syncing, only passive cluster registration.

Only 500? Weren’t we aiming for 1,000?

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*wFNhD2LzQ01DGVAL8Hf8aw.png)

Fig. 11: Spoiler Alert: We Didn’t Actually Hit 1,000 vClusters

Despite initial expectations of scaling up to 1,000, we stopped at 500 due to practical limitations:

- Each vCluster corresponds to one Argo CD Application, adding load.
- With 25 compute nodes already under significant usage, further scaling would’ve meant higher infrastructure cost (VMs, storage, etc.).

Even without applications, we began to see resource pressure on Argo CD around 100 vClusters (~114 Argo CD Applications):

- Application Controller (5 replicas, HPA enabled) started failing with **Out of Memory (**[**OOMKilled**](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/)**)**.
- Original settings: `400Mi` memory request, `800Mi` limit.
- We increased to `2Gi` request and `2.5Gi` limit per replica to stabilize.

### Test Scenario 2: One Application Per vCluster

We used `3-2-generate-values.sh` to label each vCluster with `kro: enabled`, triggering deployment of a single application via Argo CD.

This is a realistic setup for lightweight platform use cases (e.g., teams owning a cluster with one or few core services).

**Observed Scaling:**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*XMIqHPC32u3sjT7e_H2x3g.png)

Table 1: Label-Based Deployment — One App per vCluster

At 500 vClusters:

- Application Controller replicas with 10 pods were **not sufficient**.
- Repo Server **crashed under load**.
- CPU usage reached ~12 cores.
- Argo CD Application refresh (UI or CLI) across all apps took ~15 minutes.
- Prometheus (from Kube-Prometheus-Stack) **crashed** due to memory pressure and tight limits.
- Argo CD dashboard reported a **resource object count between 250.000 Objects**
- Kubernetes API server showed significant strain from controller activity.
- Eventually, Application Controllers began to crash repeatedly due to memory exhaustion.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0fpTafWAcwnwsRuxAopO2g.png)

Fig. 12: Scaling Pain — Refreshing 1,000 Apps Led to OOM Kills

At this point, we decided to stop the test, analyze the failure points, and draw conclusions for tuning and architectural changes.

### Test Scenario 3: Three Applications per vCluster

This setup increased the operational complexity per vCluster. Using `3-3-generate-values.sh`, we deployed:

- Kro
- Cert-Manager
- [Kube-Prometheus-Stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)

Compared to Scenario 2, each application created significantly more Kubernetes objects, especially Kube-Prometheus-Stack, which includes *ServiceMonitors*, *Alerting Rule* s, and other *CRDs*.

We hit limits **earlier** than in Scenario 2:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QNgva6PKZzK1Y35Q-9BlAg.png)

Table 2: Scenario 3 — Breakpoint Reached at ~814 Applications

**Key observations:**

- Argo CD Application Controller began failing between 800–850 total applications.
- Prometheus memory usage spiked again.
- System performance degraded more rapidly than in Scenario 2, despite fewer clusters.
- This scenario confirms that **object count per application matters just as much as the application count itself**.

## Learnings from Our Scale Test

Before we get into the detailed learnings, a quick note: if you notice screenshots showing both Argo CD [version 2.x and 3.x](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/2.14-3.0/) — that’s intentional. We tested with both to evaluate whether recent changes in version 3 had any impact on performance or resource usage.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*JACeZ6qLL-SByIyc4f6ytQ.png)

Fig. 13: Learn, you must!

In short: [**Argo CD 3.x appears more stable**](https://argo-cd.readthedocs.io/en/stable/operator-manual/upgrading/2.14-3.0/), and in [Grafana](https://grafana.com/), it seemed to consume less memory per application under load. However, once we crossed a certain threshold (in terms of application or cluster count), the differences became negligible. Both versions eventually slowed down and showed similar behavior.

### STACKIT Scaling Performance

STACKIT, our German hyperscaler of choice, handled our dynamic scaling requirements extremely well. We scaled up to **25 S1.6 nodes** (32 vCPUs, 32 GB RAM) during peak test windows, and the infrastructure was provisioned quickly and reliably — no reservations required. This is in stark contrast to what we’ve seen with other providers that often require pre-booked reserved instances for burst workloads. Big respect to the STACKIT team here!!

### Detailed Technical Learnings

- **ApplicationSets and Differences**  
	Our ApplicationSets were initially not configured with `[ignoreDifferences](https://argo-cd.readthedocs.io/en/stable/user-guide/diffing/)`. As a result, the sync loop frequently triggered re-syncs, and the HPA acted unnecessarily.  
	Fix: we enabled `RespectIgnoreDifferences=true` in the `syncOptions` to avoid unnecessary diffs.  
	Still: we need to find a way to extend our Helm chart template for *ApplicationSets* so we can add `ignoreDifferences` for specific resources, like `replicas` in the *StatefulSet* of the Application Controller.
- [**Request/Limit Evaluation**](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)  
	Third-party tools like **Kube-Prometheus-Stack**, **OAuth2-Proxy**, and **Ingress-NGINX** require careful tuning. We evaluated and adjusted their resource profiles based on actual usage.
- **Argo CD Job Behavior**  
	When running Argo CD self-managed, we noticed that jobs such as the `redis-init` job were retriggered on every sync. This was due to their `generateName` behavior and non-idempotent nature, leading to unnecessary restarts.
- **Use of** [**Kubernetes Resource Recommendations (KRR)**](https://github.com/robusta-dev/krr)  
	After 2–4 weeks of usage data, we used KRR to refine CPU and memory configurations. This prevented idle resource waste and allowed us to stabilize usage patterns more accurately.
- **Internal Knowledge Base**  
	We started building a documentation base for platform teams to understand under which conditions performance issues are likely to occur — and how to avoid or prepare for them.
- **Sharding Consideration for Control Plane**  
	For larger setups, we evaluated the potential of splitting Argo CD responsibilities via sharding or by deploying dedicated core instances in target clusters.
- [**Avoiding CPU Limits on Certain Services**](https://home.robusta.dev/blog/stop-using-cpu-limits)  
	We learned that hard CPU limits are counterproductive for some workloads. In those cases, it’s better to rely on **HPA with proper requests** to avoid starvation while still maintaining elasticity.
- **Metrics Awareness**  
	Not all metrics are collected by default. For example, we realized too late that [OAuth2-Proxy](https://github.com/oauth2-proxy/oauth2-proxy) metrics weren’t being scraped — which became an issue as more users accessed the Argo CD UI. At scale, even auxiliary components like these can become pressure points.
- **Scaling Thresholds**  
	A ControlPlane-based Argo CD setup performs well up to:  
	\-> ~500 Applications  
	\-> ~50–60 Clusters
- [**Monorepo usage**](https://dnastacio.medium.com/gitops-repositories-the-right-way-part-1-mapping-strategies-6409dff758b5)  
	Beyond 600–700 applications and 100+ clusters, **the Application Controller began to OOM**, even with tuned limits. Once one controller crashes, others take over the load, leading to a chain reaction of OOM events across all replicas.
- **No Universal Limits**  
	It’s not meaningful to define a strict number of applications or clusters per Argo CD instance. The real limits depend on:  
	\- > Application object complexity  
	\-> Manifest generation time  
	\-> Cluster API responsiveness  
	\-> Resource profiles of Argo CD components
- **Test Objectives Matter**  
	It sounds trivial, but: **define what exactly you want to test before you start**. We began testing without a clear definition of which metrics would be meaningful at scale. That led to several iterations of tooling, dashboards, and analysis pipelines.

You should also consider your [**Argo CD HA setup**](https://codefresh.io/learn/argo-cd/a-comprehensive-overview-of-argo-cd-architectures-2025/) and consult the [**benchmarking report from CNO**](https://cnoe.io/blog/argo-cd-application-scalability) **E** (Engineers from Intuit and AWS). This report offers valuable insights into how to optimally configure **QPS/Burst QPS** and the **number of Status/Operation Processors**, as well as determining how many **shards** would be most beneficial for your environment.

### Architectural Caveat: Shared Control Plane and vClusters

One final point worth mentioning: our setup placed both the **ControlPlane (Argo CD, ESO, Vault, etc.) and the vClusters on the same kubernetes host cluster**. This introduced several side effects:

- All objects were stored in the same etcd instance.
- All API requests went through the same Kubernetes API server.
- Internal mesh traffic between vClusters and control components was not isolated.

This likely amplified the load issues we saw. In other client setups where vClusters and Control Plane are separated across different physical clusters, we’ve seen more consistent performance — even at 1,500–2,000 applications and 50–80 clusters.

## Alternatives and What We Could Improve

### Limitations of Argo CD at Scale

It’s no secret: Argo CD reaches its limits at some point — even with aggressive tuning. [Akuity](https://akuity.io/) recognized this early on and developed [**Kargo**](https://kargo.io/) to address some of the fundamental limitations:

- **Kargo** separates manifest generation and multi-stage promotions logic from Argo CD itself.
- It allows stage-based promotion workflows (e.g., dev → staging → production).
- Kargo renders manifests independently and passes fully rendered output to Argo CD — reducing load on the Argo CD **Repo Server** significantly.

This is critical because:

- Even with `RespectIgnoreDifferences=true`, the **Repo Server** remains a bottleneck.
- It handles Git repository cloning, manifest rendering, and caching.
- With many repositories and complex charts (e.g., Kube-Prometheus-Stack), even an HPA-backed Repo Server eventually struggles under load.

### Know Your Components: How Argo CD Works Internally

To optimize Argo CD effectively, it’s essential to understand the role and scaling behavior of each core component:

- [**Application Controller**](https://argo-cd.readthedocs.io/en/release-1.8/operator-manual/server-commands/argocd-application-controller/)**:**  
	Responsible for reconciling actual vs. desired state and syncing applications. This is the component most affected by object count and sync frequency.
- [**Repo Server**](https://argo-cd.readthedocs.io/en/stable/operator-manual/server-commands/argocd-repo-server/)**:**  
	Handles manifest rendering, Git interactions, and caching. Its performance depends heavily on the number of repositories, their size, and the complexity of Helm/Kustomize usage.
- [**Argo CD Server (API/UI)**](https://argo-cd.readthedocs.io/en/release-2.1/operator-manual/server-commands/argocd-server/)**:**  
	Mainly serves CLI, UI, and API access. Usually low-impact, but high concurrent usage (automation, CI/CD bots, dashboards) can push it to its limits.
- and so on….

Understanding this separation is key to planning proper resource limits, scaling policies, and isolation strategies.

### Architectural Alternatives and Extensions

[**1\. Dedicated Argo CD Instances per Cluster**](https://akuity.io/blog/argo-cd-architectures-explained)

One way to scale more safely is to deploy dedicated Argo CD instances per cluster and let a central ControlPlane manage these instances.

- **Pros:**  
	Better fault isolation, reduced blast radius, less cross-cluster interference.
- **Cons:**  
	Higher infrastructure cost, more operational complexity, duplicated setup logic.

This trade-off is often acceptable in larger environments where platform stability matters more than cost savings.

**2\. Lightweight Clustering with vCluster**

For those optimizing for cost, **vCluster** offers a middle ground: isolated Kubernetes API surfaces per tenant, without the full overhead of real clusters. We use this in our setup to simulate hundreds of “clusters” while keeping infra spend within reason.

**3\. Bring Your Own Nodes with** [**Kamaji**](https://kamaji.clastix.io/)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*zbJGMQekQNtIrKFhWAKa1Q.png)

Fig. 14: Kamaji: Run Your Nodes Where You Like!

If you want to provide multi-tenant Kubernetes **control planes**, while sourcing the underlying infrastructure (e.g., VMs) from other providers like [Hetzner](https://www.hetzner.com/), [**Kamaji** is worth evaluating.](https://medium.com/itnext/build-your-own-saas-cloud-platform-with-kamaji-and-gitops-aeec1b5f17fd)

- Kamaji allows running multiple Kubernetes control planes as tenants on a shared base cluster.
- You can attach your own node pools and define custom resource profiles.

### Argo CD Is Not the Only Option

If Argo CD’s model doesn’t fit your use case, other projects exist that solve similar challenges:

- [**Flux CD**](https://fluxcd.io/)**:**  
	A GitOps engine with a different architecture. It favors reconciliation from multiple sources and works well with large fleets.
- [**Sveltos**](https://medium.com/itnext/sveltos-argo-cd-and-flux-cd-are-not-the-only-gitops-tools-for-kubernetes-fa2b94b2ea48)**:**  
	A project focused on Kubernetes **fleet management**, designed to manage many clusters and applications across environments — often more scalable out-of-the-box for multicluster and multi-tenancy setups.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*0f43C21hsr92WkebCX2oDA.png)

Fig. 15: Sveltos — rule them all!

## Wrap-Up

We came for GitOps.  
We stayed for the scaling limits.  
We left with 500+ vClusters, a melted Argo CD controller, and a few gray hairs.

Argo CD can scale — but not endlessly, and certainly not blindly.  
Know your components, know your limits, and bring snacks for the long syncs.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*WxNTx4q0qKK73t5vi6yBhQ.jpeg)

Fig. Final: Know Your Stuff!

In case you missed the 90-minute webinar, you can check out the recording here:

If you’re interested in topics like developer platforms, GitOps, and abstraction layers that don’t suck, definitely check out:

- [From CI to Kubernetes Catalog: Building a Composable Platform with GitOps and vCluster](https://medium.com/itnext/from-ci-to-kubernetes-catalog-building-a-composable-platform-with-gitops-and-vcluster-7e1decaa81da)
- [Build Your Own Kubernetes based SaaS Cloud Platform with Kamaji and GitOps](https://medium.com/itnext/build-your-own-saas-cloud-platform-with-kamaji-and-gitops-aeec1b5f17fd)
- [How to Build a Multi-Tenancy Internal Developer Platform with GitOps and vCluster](https://medium.com/itnext/how-to-build-a-multi-tenancy-internal-developer-platform-with-gitops-and-vcluster-d8f43bfb9c3d)
- [Build a Lightweight Internal Developer Platform with Argo CD and Kubernetes Labels](https://itnext.io/build-a-lightweight-internal-developer-platform-with-argo-cd-and-kubernetes-labels-4c0e52c6c0f4)

## Contact Information

Got questions, want to chat, or just keen to stay connected? Skip the Medium comments and let’s connect on [LinkedIn](http://www.linkedin.com/in/lajko) 🤙. Don’t forget to subscribe to the [Medium Newsletter](https://itnext.io/@artem_lajko/subscribe) so you never miss an update!

Do something with cloud, kubernetes, gitops and all the fancy stuff [https://www.linkedin.com/in/lajko](https://www.linkedin.com/in/lajko)

## More from Artem Lajko and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d8ea2a8935b6---------------------------------------)