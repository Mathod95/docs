---
title: "The Complete Guide to Setting Up Cilium on K3s with Kubernetes Gateway API"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blogs.learningdevops.com/the-complete-guide-to-setting-up-cilium-on-k3s-with-kubernetes-gateway-api-8f78adcddb4d"
author:
  - "[[Rajesh Kumar]]"
---
<!-- more -->

[Sitemap](https://blogs.learningdevops.com/sitemap/sitemap.xml)

## Introduction

In this guide, we will walk through setting up **Cilium** as the CNI for a **K3s** cluster while integrating the **Kubernetes Gateway API**. **Kubernetes Gateway API** is the evolution of Kubernetes Ingress, providing advanced routing, better traffic control, and support for multiple protocols.

***On a free medium plan?*** [***Read here for free***](https://blogs.learningdevops.com/the-complete-guide-to-setting-up-cilium-on-k3s-with-kubernetes-gateway-api-8f78adcddb4d?sk=185f746f14a0ca683cdf7243fec5a5ab)***.***

## Step 1: Install K3s with Required Options

First, install K3s without the default network components, allowing **Cilium** to function as the primary CNI. We are using a single-node K3S cluster. Please refer to the [documentation](https://docs.cilium.io/en/stable/installation/k3s/) for more info.

```c
$ curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" sh -s - --flannel-backend=none --disable-kube-proxy --disable servicelb --disable-network-policy --disable traefik --tls-san rancher.rajesh-kumar.in
```

## Explanation of Options:

- `--flannel-backend=none`: Disables Flannel as the default CNI (we will use Cilium instead).
- `--disable-kube-proxy`: Cilium has its own eBPF-based networking and does not require kube-proxy.
- `--disable servicelb`: K3s includes `ServiceLB`, but we disable it to use Cilium’s L4/L7 load balancing.
- `--disable-network-policy`: Network policies will be managed by Cilium.
- `--disable traefik`: K3s comes with Traefik by default, but we want to use **Cilium Gateway API** for ingress traffic.
- `--tls-san rancher.rajesh-kumar.in`: Ensures API server TLS is valid for the given hostname.

## Step 2: Install Kubernetes Gateway API CRDs

The **Gateway API CRDs** must be installed **before** deploying Cilium. Otherwise, the **Cilium Operator** may need to be restarted after deploying the CRDs. For the safer side, apply CRDs beforehand.

```c
$ kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.0/standard-install.yaml\
👉 The latest release (v1.2.1) does not include TLSRoutes in the standard release channel. Since Cilium depends on it, we must install it manually from the experiment channel.
```

💡 **Tip:** Always check the latest updates on Kubernetes Gateway API releases [here](https://github.com/kubernetes-sigs/gateway-api/tree/main).

## Step 3: Install Cilium

## Install Cilium CLI

```c
$ CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
$ CLI_ARCH=amd64
$ if [ "$(uname -m)" = "aarch64" ]; then CLI_ARCH=arm64; fi 
$ curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
$ sha256sum --check cilium-linux-${CLI_ARCH}.tar.gz.sha256sum
$ sudo tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin
$ rm cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
```

Verify installation:

```c
$ cilium status
```

## Create Cilium Values File

The following values file configures Cilium for optimal performance in a K3s setup:

```c
k8sServiceHost: "192.168.90.102"  # The Kubernetes API server address
k8sServicePort: "6443"  # Kubernetes API server port
kubeProxyReplacement: true  # Enables eBPF-based kube-proxy replacement for better performance
l2announcements:
  enabled: true  # Enables Layer 2 announcements for external IP management
externalIPs:
  enabled: true  # Allows services to use external IPs for better connectivity
k8sClientRateLimit:
  qps: 50  # API request rate limit to avoid overwhelming the K8s API
  burst: 200  # Maximum burst rate for API requests
operator:
  replicas: 1  # Ensures a single replica of the Cilium operator, suitable for small clusters
rollOutPods: true  # Ensures smooth rolling updates of Cilium components
rollOutCiliumPods: true  # Ensures that Cilium pods are updated properly during upgrades
gatewayAPI:
  enabled: true  # Enables support for the Kubernetes Gateway API
envoy:
  enabled: true  # Enables Envoy integration for advanced networking and security features
securityContext:
  capabilities:
    keepCapNetBindService: true  # Ensures correct capabilities for networking
debug:
  enabled: true  # Enables debug logging for troubleshooting
```

## Export Kubeconfig & Install Cilium

Cilium needs kubeconfig to interact with the cluster, so export it and then install Cilium with cilium-values.yaml file

```c
$ export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
$ cilium install -f cilium-values.yaml
```

Check Cilium status:

```c
$ cilium status
```

Expected output:

```c
cilium status
    /¯¯\
 /¯¯\__/¯¯\    Cilium:             OK
 \__/¯¯\__/    Operator:           OK
 /¯¯\__/¯¯\    Envoy DaemonSet:    OK
 \__/¯¯\__/    Hubble Relay:       disabled
    \__/       ClusterMesh:        disabled

DaemonSet              cilium             Desired: 1, Ready: 1/1, Available: 1/1
DaemonSet              cilium-envoy       Desired: 1, Ready: 1/1, Available: 1/1
Deployment             cilium-operator    Desired: 1, Ready: 1/1, Available: 1/1
Containers:            cilium             Running: 1
                       cilium-envoy       Running: 1
                       cilium-operator    Running: 1
Cluster Pods:          11/11 managed by Cilium
Helm chart version:    1.16.5
Image versions         cilium             quay.io/cilium/cilium:v1.16.5@sha256:758ca0793f5995bb938a2fa219dcce63dc0b3fa7fc4ce5cc851125281fb7361d: 1
                       cilium-envoy       quay.io/cilium/cilium-envoy:v1.30.8-1733837904-eaae5aca0fb988583e5617170a65ac5aa51c0aa8@sha256:709c08ade3d17d52da4ca2af33f431360ec26268d288d9a6cd1d98acc9a1dced: 1
                       cilium-operator    quay.io/cilium/operator-generic:v1.16.5@sha256:f7884848483bbcd7b1e0ccfd34ba4546f258b460cb4b7e2f06a1bcc96ef88039: 1
```

Check if the GatewayClass is registered correctly:

```c
$ kubectl get gatewayclasses
```

## Troubleshooting CRD Issues

Check gatewayclass resource

```c
$ kubectl describe gatewayclasses
```

If the `Accepted` field shows `Unknown` or gatewayclass is not showing, check Cilium Operator logs:

```c
$ kubectl describe gatewayclasses.gateway.networking.k8s.io

Name:         cilium
Namespace:
Labels:       app.kubernetes.io/managed-by=Helm
Annotations:  meta.helm.sh/release-name: cilium
              meta.helm.sh/release-namespace: kube-system
API Version:  gateway.networking.k8s.io/v1
Kind:         GatewayClass
Metadata:
  Creation Timestamp:  2025-01-30T04:13:39Z
  Generation:          1
  Resource Version:    30451
  UID:                 409bfdba-b6ad-4df9-9341-a11dc0b2c04e
Spec:
  Controller Name:  io.cilium/gateway-controller
  Description:      The default Cilium GatewayClass
Status:
  Conditions:
    Last Transition Time:  1970-01-01T00:00:00Z
    Message:               Waiting for controller
    Reason:                Pending
    Status:                Unknown
    Type:                  Accepted
Events:                    <none>
```
```c
$ kubectl -n kube-system logs -f -l app.kubernetes.io/name=cilium-operator

time="2025-01-30T06:54:19Z" level=error msg="Required GatewayAPI resources are not found, please refer to docs for installation instructions" error="customresourcedefinitions.apiextensions.k8s.io \"tlsroutes.gateway.networking.k8s.io\" not found" subsys=gateway-api
```

Fix all the CRD issues and restart the Cilium operator, or scale to 0 and then re-scale.

```c
$ kubectl rollout restart -n kube-system deployment/cilium-operator
```

Verify Cilium status:

```c
$ cilium status
$ kubectl get gatewayclasses # ensure gatewayclass is visibile and ACCEPTED: true
```

If `gatewayclass` isn’t visible even after restarting the operator, uninstall Cilium and install it.

```c
$ cilium uninstall 

🔥 Deleting pods in cilium-test namespace...
🔥 Deleting cilium-test namespace...
⌛ Uninstalling Cilium

$ cilium install -f cilium-values.yaml 

🔮 Auto-detected Kubernetes kind: K3s
ℹ️  Using Cilium version 1.17.2
🔮 Auto-detected cluster name: default
```

Verify Cilium status:

```c
$ cilium status
$ kubectl get gatewayclasses # ensure gatewayclass is visibile and ACCEPTED: true
```

## Step 4: Setup Cilium Gateway

We will deploy a single **Gateway** resourcein the **cilium-gateway** namespace and use multiple **HTTPRoutes** to route traffic to different services. We are also storing TLS certificates in a separate **certificates** namespace**.**

## Why a Single Gateway?

- **Centralized Routing**: One entry point simplifies traffic management.
- **Flexibility**: Multiple routes can be defined using `HTTPRoute`.
- **Security**: TLS termination and authentication are handled in one place.

### Create Namespaces

```c
$ kubectl create namespace cilium-gateway
$ kubectl create namespace certificates
```

### Store TLS Certificates

Use your existing TLS certificates to create a Kubernetes secret:

```c
$ kubectl -n certificates create secret tls rajesh-tls-cert --cert=cert.pem --key=key.pem
```

### Deploy ReferenceGrant

As we are creating the certificate in a separate namespace, we need to grant permission to access the certificates from other namespaces. The **ReferenceGrant** allows the Gateway in `cilium-gateway` to access the TLS certificate stored in the `certificates` namespace.

```c
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-gateway-to-use-cert
  namespace: certificates
spec:
  from:
  - group: gateway.networking.k8s.io
    kind: Gateway
    namespace: cilium-gateway
  to:
  - group: ""
    kind: Secret
```

💡 Kubernetes restricts access to resources across namespaces. The `ReferenceGrant` enables cross-namespace reference while maintaining security.

### Deploy Cilium Gateway

```c
apiVersion: gateway.networking.k8s.io/v1beta1
kind: Gateway
metadata:
  name: rancher-master-gateway
  namespace: cilium-gateway
spec:
  gatewayClassName: cilium
  listeners:
  - protocol: HTTPS
    port: 443
    name: rancher-master-gateway
    tls:
      mode: Terminate
      certificateRefs:
      - name: rajesh-tls-cert
        namespace: certificates
        kind: Secret
    allowedRoutes:
      namespaces:
        from: All
```

✅ **TLS Termination**: The gateway terminates HTTPS traffic and uses the provided certificate.  
**Allowed Routes**: Accepts HTTPRoutes from all namespaces.

### Load Balancer & L2 Announcement.

For LoadBalancer IP assignment:

```c
apiVersion: "cilium.io/v2alpha1"
kind: CiliumLoadBalancerIPPool
metadata:
  name: "rancher-master-cluster-pool"
spec:
  blocks:
    - start: "192.168.90.245"
      stop: "192.168.90.250"
```

For L2 announcement:

```c
apiVersion: cilium.io/v2alpha1
kind: CiliumL2AnnouncementPolicy
metadata:
  name: default-l2-announcement-policy
  namespace: kube-system
spec:
  externalIPs: true
  loadBalancerIPs: true
```
```c
$ kubectl apply -f cilium-ip-pool.yaml -f cilium-announce.yaml
```

## Step 5: Deploy Applications & HTTPRoutes

## Deploy Applications

```c
$ kubectl create namespace nginx
$ kubectl create namespace webui
$ kubectl apply -n nginx -f nginx-deployment.yaml
$ kubectl apply -n webui -f webui-deployment.yaml
```

## Important Consideration: Path Rewrites Do Not Work As Expected

Path rewrites do not work effectively because `/nginx` or `/webui` will be rewritten as,`/` which affects all other paths that the application may be accessing. This causes issues with applications loading properly, especially UI-based applications that rely on fetching static assets from specific paths.

UI applications may also need to be configured appropriately, as they might expect to fetch static assets from a different path structure. More details on this issue can be found in the following discussion: [GitHub Issue #1954](https://github.com/kubernetes-sigs/gateway-api/issues/1954).

To resolve this, each application should have its own dedicated hostname, rather than relying on path-based routing.

To resolve this, each application should have its own dedicated hostname, rather than relying on path-based routing.

## Mapping HTTPRoute Domains to the Load Balancer IP

Once the Gateway resource is created, it will be assigned a **LoadBalancer IP**. To ensure domain resolution works correctly, map the **HTTPRoute domains** to this IP in your hosting provider’s DNS records or update your local `/etc/hosts` file.

Retrieve the assigned LoadBalancer IP:

```c
$ kubectl get svc -n cilium-gateway
```

Example output:

```c
NAME                                    TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)         AGE
cilium-gateway-rancher-master-gateway   LoadBalancer   10.43.224.132   192.168.90.240   443:31357/TCP   3h15m
```
- Update your `/etc/hosts` file (for local testing). Add the following lines:
```c
192.168.90.240 nginx.rajesh-kumar.in
192.168.90.240 argo.rajesh-kumar.in
```
- If using a domain registrar or cloud DNS provider, create **A records** pointing to the LoadBalancer IP.

This ensures that requests to `nginx.rajesh-kumar.in` and `argo.rajesh-kumar.in` correctly resolve to the Cilium Gateway.

## Configure HTTPRoutes

```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: nginx-route
  namespace: nginx
spec:
  hostnames:
  - "nginx.rajesh-kumar.in"
  parentRefs:
  - name: rancher-master-gateway
    namespace: cilium-gateway
  rules:
  - matches:
    - path:
        type: Prefix
        value: /
    backendRefs:
    - name: nginx-service
      port: 80
```
```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: webui-route
  namespace: webui
spec:
  hostnames:
  - "webui.rajesh-kumar.in"
  parentRefs:
  - name: rancher-master-gateway
    namespace: cilium-gateway
  rules:
  - matches:
    - path:
        type: Prefix
        value: /
    backendRefs:
    - name: webui-service
      port: 80
```

## Step 5: Verify Everything Works

```c
kubectl get gateways -A
kubectl get httproutes -A
kubectl describe gateway rancher-master-gateway -n cilium-gateway

$ curl -v https://nginx.rajesh-kumar.in
$ curl -v https://webui.rajesh-kumar.in
```

🎉 **Congratulations!** You have successfully set up **Cilium with Kubernetes Gateway API on K3s!** 🚀

## Conclusion

With this setup, we successfully deployed **Cilium on k3s with Kubernetes Gateway API**, enabled secure **TLS termination**, and implemented **hostname-based routing.**## [Rajesh Kumar](https://buymeacoffee.com/rajeshk02?source=post_page-----8f78adcddb4d---------------------------------------)

I'm a Support Engineer with deep expertise in Kubernetes, Golang, and cloud-native security. I specialize in network…

buymeacoffee.com

[View original](https://buymeacoffee.com/rajeshk02?source=post_page-----8f78adcddb4d---------------------------------------)

## Connect & Continue Learning 🚀

Enjoyed this article? Clap until your fingers hurt (or just 50 times, whichever comes first)!

[**Read my other articles**](https://medium.com/@rk90229) — because one tech rabbit hole deserves another!

[**Connect with me on LinkedIn**](https://www.linkedin.com/in/techwith-rajesh/) for more tech insights — it’s like subscribing, but with fewer annoying notifications.

Have a suggestion for my next post? Drop a comment below! I read them all (even the ones suggesting I should’ve used spaces instead of tabs).

*P.S. Let me know what topics you’d like me to cover next!*

DevOps/SRE engineer diving deep into Go & open source. Learning through breaking things, then fixing them. Coffee-fueled technical deep dives ahead.

## More from Rajesh Kumar

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--8f78adcddb4d---------------------------------------)