---
title: "ArgoCD Deployment on RKE2 with Cilium Gateway API"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@eleni.grosdouli/argocd-deployment-on-rke2-with-cilium-gateway-api-ab1769cc28a3"
author:
  - "[[Eleni Grosdouli]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

***Heads up****! 🚀 The updated documentation is now available at \[*[https://blog.grosdouli.dev/blog/rke2-dual-stack-cluster-mesh-cilium-complementary-features](https://blog.grosdouli.dev/blog/rke2-dual-stack-cluster-mesh-cilium-complementary-features)*\]. Check it out for the latest info!*

## Introduction

It has already been a couple of years since the Kubernetes [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) was defined as a “frozen” feature while further development will be added to the [Gateway API](https://gateway-api.sigs.k8s.io/).

After initial exposure to the Cilium Gateway API [docs](https://docs.cilium.io/en/v1.14/network/servicemesh/gateway-api/gateway-api/) and the interactive [lab](https://isovalent.com/labs/gateway-api/) session, it sounded promising to move the ArgoCD deployment from the Kubernetes Ingress to the Cilium Gateway API. The purpose of the blog post is to illustrate how easy it is to move the ArgoCD installation to the Cilium Gateway API. For this demonstration, the Gateway and the HTTPRoute have been created in the argocd namespace.

## Diagram

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*_p4v6d_vjOcCgIqDDSsV0Q.jpeg)

Cilium Gateway API

## Lab Setup

```c
+----------------+----------------------+-------------------------+
|  Cluster Name  |         Type         |         Version         |
+----------------+----------------------+-------------------------+
|  rke2-test01   | Test Management      | RKE2 v1.26.12+rke2r1    |
|                | Cluster              |                         |
+----------------+----------------------+-------------------------+

+-------------+----------+
|  Deployment | Version  |
+-------------+----------+
|    ArgoCD   | v2.9.3   |
|    Cilium   | v1.14.5  |
|  GatewayAPI | v0.7.0   |
+-------------+----------+
```

## Step 1: Deploy RKE2 Cluster with Cilium CNI

Before diving in, it is a good idea to checkout the **RKE2** official [documentation](https://docs.rke2.io/install/network_options) on Kubernetes Networking and the **Cilium** [documentation](https://docs.cilium.io/en/v1.14/installation/k8s-install-rke/). Also, take a peek at the prerequisites for deploying the [Gateway API deployment](https://docs.cilium.io/en/v1.14/network/servicemesh/gateway-api/gateway-api/).

### RKE2 Pre-work

```c
$ cat /etc/rancher/rke2/config.yaml
write-kubeconfig-mode: 0644
tls-san:
  - {Master Node hostname}
token: {Your Token}
cni: cilium
disable-kube-proxy: true
etcd-expose-metrics: false
```
```c
$ cat /var/lib/rancher/rke2/server/manifests/rke2-cilium-config.yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: rke2-cilium
  namespace: kube-system
spec:
  valuesContent: |-
    image:
      tag: v1.14.5
    kubeProxyReplacement: strict
    k8sServiceHost: 127.0.0.1
    k8sServicePort: 6443
    operator:
      replicas: 1
    gatewayAPI:
      enabled: true
```

According to the Cilium documentation, to enable the Gateway API, we need at least the **1.14.5** Cilium Helm chart with the `kubeProxyReplacement` value set to `true` and the `gatewayAPI` inside the Helm chart definition set to `enabled: true`.

Once the remaining steps for the RKE2 installation are complete, we will have a two node RKE2 cluster with Cilium as a CNI.

Since Kubernetes v.1.26.x does not come with the Gateway API CRDs included, we will need to deploy them manually and let the Cilium containers restart until everything is in a “Running” state.

```c
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v0.7.0/config/crd/standard/gateway.networking.k8s.io_gatewayclasses.yaml
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v0.7.0/config/crd/standard/gateway.networking.k8s.io_gateways.yaml
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v0.7.0/config/crd/standard/gateway.networking.k8s.io_httproutes.yaml
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v0.7.0/config/crd/standard/gateway.networking.k8s.io_referencegrants.yaml
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v0.7.0/config/crd/experimental/gateway.networking.k8s.io_tlsroutes.yaml
```

**Note:** According to the RKE2 documentation, RKE2 v1.26.12 does not officially support Cilium v1.14.5. The latest supported version is v1.14.4. However, during the demo setup, we did not encounter any issues.

### Verification

```c
$ kubectl get nodes -o wide
NAME            STATUS   ROLES                       AGE    VERSION           INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                              KERNEL-VERSION              CONTAINER-RUNTIME
rke2-master01   Ready    control-plane,etcd,master   111m   v1.26.12+rke2r1                  <none>        SUSE Linux Enterprise Server 15 SP5   5.14.21-150500.53-default   containerd://1.7.11-k3s2
rke2-worker01   Ready    <none>                      98m    v1.26.12+rke2r1                  <none>        SUSE Linux Enterprise Server 15 SP5   5.14.21-150500.53-default   containerd://1.7.11-k3s2

$ kubectl get pods -n kube-system | grep -i cilium
cilium-k9vhf                                            1/1     Running     0              111m
cilium-lc7jn                                            1/1     Running     0              99m
cilium-operator-548958b5bf-nc95q                        1/1     Running     5 (108m ago)   111m
helm-install-rke2-cilium-tp5l6                          0/1     Completed   0              112m

$ kubectl -n kube-system get daemonset cilium -o jsonpath="{.spec.template.spec.containers[0].image}"
rancher/mirrored-cilium-cilium:v1.14.5
```

## Step 2: Install ArgoCD

We will follow the official “Getting Started” guide found [here](https://argo-cd.readthedocs.io/en/stable/getting_started/), and use the manifest installation option.

```c
$ kubectl create namespace argocd
$ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

The code above will create the `argocd` Kubernetes namespace and deploy the latest **stable** manifest. If you would like to install a specific manifest, have a look [here](https://github.com/argoproj/argo-cd/releases).

### Verification

```c
$ kubectl get pods,svc -n argocd
NAME                                                    READY   STATUS    RESTARTS   AGE
pod/argocd-application-controller-0                     1/1     Running   0          82m
pod/argocd-applicationset-controller-6b67b96c9f-7szsr   1/1     Running   0          82m
pod/argocd-dex-server-c9d4d46b5-mdf67                   1/1     Running   0          82m
pod/argocd-notifications-controller-6975bff68d-ltbkc    1/1     Running   0          82m
pod/argocd-redis-7d8d46cc7f-2br7f                       1/1     Running   0          82m
pod/argocd-repo-server-59f5479b7-dfg9x                  1/1     Running   0          82m
pod/argocd-server-547bf65466-68554                      1/1     Running   0          58m

NAME                                              TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)                      AGE
service/argocd-applicationset-controller          ClusterIP      10.43.98.162    <none>         7000/TCP,8080/TCP            82m
service/argocd-dex-server                         ClusterIP      10.43.71.44     <none>         5556/TCP,5557/TCP,5558/TCP   82m
service/argocd-metrics                            ClusterIP      10.43.162.177   <none>         8082/TCP                     82m
service/argocd-notifications-controller-metrics   ClusterIP      10.43.55.157    <none>         9001/TCP                     82m
service/argocd-redis                              ClusterIP      10.43.62.79     <none>         6379/TCP                     82m
service/argocd-repo-server                        ClusterIP      10.43.224.205   <none>         8081/TCP,8084/TCP            82m
service/argocd-server                             ClusterIP      10.43.166.25    <none>         80/TCP,443/TCP               82m
service/argocd-server-metrics                     ClusterIP      10.43.165.222   <none>         8083/TCP                     82m
```

## Step 3: Pre-Work

Before we move on with the Gateway API implementation, we need to create additional Kubernetes resources.

### Argocd TLS Secret

```c
$ kubectl create secret tls argocd-server-tls -n argocd --key=argocd-key.pem --cert=argocd.example.com.pem
```

The above assumes that we have already created a private/public key pair via an available utility. Also, keep in mind that the TLS secret name should be `argocd-server-tls` as it will be used at a later point.

### Cilium IP Pool

In our lab environment, we do not have a tool to hand over `Loadbalancer` IP addresses. Therefore, we will use the Cilium [LoadBalancer IP Address Management](https://docs.cilium.io/en/v1.14/network/lb-ipam/) (LB IPAM).

```c
$ cat ipam-pool.yaml
apiVersion: "cilium.io/v2alpha1"
kind: CiliumLoadBalancerIPPool
metadata:
  name: "rke2-pool"
spec:
  cidrs:
  - cidr: "10.10.10.0/24"
```

**Verification**

```c
$ kubectl apply -f "ipam-pool.yaml"

$ kubectl get ippool
NAME        DISABLED   CONFLICTING   IPS AVAILABLE   AGE
rke2-pool   false      False         253             79m
```

### Cilium GatewayClass

If the `GatewayClass` resource is not present in the cluster, we have to create one for Cilium. The resource will be used in a later step and while deploying the `Gateway`. The `GatewayClass` is a template that lets infrastructure providers offer different types of Gateways.

```c
$ cat gatewayclass.yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: GatewayClass
metadata:
  name: cilium
spec:
  controllerName: io.cilium/gateway-controller
```

**Verification**

```c
$ kubectl apply -f "gatewayclass.yaml"

$ kubectl get gatewayclass
NAME     CONTROLLER                     ACCEPTED   AGE
cilium   io.cilium/gateway-controller   True       104m
```

## Step 4: Create a Gateway and an HTTPRoute Resources

### Gateway

The `Gateway` is an instance of the `GatewayClass` created above.

```c
$ cat argocd_gateway.yaml

2 apiVersion: gateway.networking.k8s.io/v1beta1
3 kind: Gateway
4 metadata:
5   name: argocd
6   namespace: argocd
7 spec:
8   gatewayClassName: cilium
9   listeners:
10   - hostname: argocd.example.com
11     name: argocd-example-com-http
12     port: 80
13     protocol: HTTP
14   - hostname: argocd.example.com
15     name: argocd-example-com-https
16     port: 443
17     protocol: HTTPS
18  tls:
19    certificateRefs:
20    - kind: Secret
21      name: argocd-server-tls
```

**Line 3:** We define the kind Resource to `Gateway`

**Line 6:** We set the namespace to `argocd`

**Line 8:** We use the name of the `GatewayClass` created in the previous step

**Line 9:** We define the listeners for the ArgoCD server

**Line 21:** We define the TLS secret name created in the previous step

**Note:** In the definition above we use the `.example.com` as the Domain however, the value should be replaced with a valid Domain name.

### HTTP Route

The `HTTPRoute` is used to distribute multiple HTTP requests. For example, based on the `PathPrefix`.

```c
$ cat argocd_http_route.yaml

2 apiVersion: gateway.networking.k8s.io/v1beta1
3 kind: HTTPRoute
4 metadata:
5   creationTimestamp: null
6   name: argocd
7   namespace: argocd
8 spec:
9   hostnames:
10   - argocd.example.com
11   parentRefs:
12   - name: argocd
13   rules:
14   - backendRefs:
15     - name: argocd-server
16       port: 80
17     matches:
18     - path:
19         type: PathPrefix
20         value: /
21 status:
22   parents: []
```

**Line 10:** We set the hostname we want the ArgoCD Server to get exposed to

**Line 15:** We define the name of the ArgoCD server service

### Apply the Kubernetes Resources

```c
$ kubectl apply -f argocd_gateway.yaml,argocd_http_route.yaml

$ kubectl get gateway,httproute -n argocd
NAME                                       CLASS    ADDRESS        PROGRAMMED   AGE
gateway.gateway.networking.k8s.io/argocd   cilium   10.10.10.173   True         9s

NAME                                         HOSTNAMES                AGE
httproute.gateway.networking.k8s.io/argocd   ["argocd.example.com"]   9s
```

## Step 5: Test Time

We want to see if everything works as expected and whether we are able to access the ArgoCD server with the Cilium Gateway API. Let’s perform a CURL request.

```c
$ curl -kv https://argocd.example.com
*   Trying 10.10.10.173:443...
* Connected to argocd.example.com (10.10.10.173) port 443 (#0)
* ALPN: offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_CHACHA20_POLY1305_SHA256
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: O=mkcert development certificate; OU=root@server
*  start date: Feb  2 07:11:49 2024 GMT
*  expire date: May  2 07:11:49 2026 GMT
*  issuer: O=mkcert development CA; OU=root@server; CN=mkcert root@server
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
* using HTTP/1.x
> GET / HTTP/1.1
> Host: argocd.example.com
> User-Agent: curl/8.0.1
> Accept: */*
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* old SSL session ID is stale, removing
< HTTP/1.1 307 Temporary Redirect
< content-type: text/html; charset=utf-8
< location: https://argocd.example.com/
< date: Fri, 02 Feb 2024 07:58:21 GMT
< content-length: 63
< x-envoy-upstream-service-time: 0
< server: envoy
< 
<a href="https://argocd.example.com/">Temporary Redirect</a>.

* Connection #0 to host argocd.example.com left intact
```

From the above, it is visible that we are experiencing a well-known issue with 307 redirects. To resolce this, we will need to disable the TLS on the API server. This involves modifying the `argocd-cmd-params-cm` ConfigMap in the `argocd` namespace and setting the `server.insecure: “true”`. More information can be found [here](https://argo-cd.readthedocs.io/en/stable/operator-manual/server-commands/additional-configuration-method/).

Once the changes are performed we need to restart the `argocd-server` deployment for the changes to take effect.

```c
$ kubectl rollout restart deploy argocd-server -n argocd

$ kubectl rollout status deploy argocd-server -n argocd

Waiting for deployment "argocd-server" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "argocd-server" rollout to finish: 1 old replicas are pending termination...
deployment "argocd-server" successfully rolled out
```

Let us try once again.

```c
$ curl -ki https://argocd.example.com
HTTP/1.1 200 OK
accept-ranges: bytes
content-length: 788
content-security-policy: frame-ancestors 'self';
content-type: text/html; charset=utf-8
vary: Accept-Encoding
x-frame-options: sameorigin
x-xss-protection: 1
date: Fri, 02 Feb 2024 13:03:45 GMT
x-envoy-upstream-service-time: 0
server: envoy

<!doctype html><html lang="en"><head><meta charset="UTF-8"><title>Argo CD</title><base href="/"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" type="image/png" href="assets/favicon/favicon-32x32.png" sizes="32x32"/><link rel="icon" type="image/png" href="assets/favicon/favicon-16x16.png" sizes="16x16"/><link href="assets/fonts.css" rel="stylesheet"><script defer="defer" src="main.f14bff1ed334a13aa8c2.js"></script></head><body><noscript><p>Your browser does not support JavaScript. Please enable JavaScript to view the site. Alternatively, Argo CD can be used with the <a href="https://argoproj.github.io/argo-cd/cli_installation/">Argo CD CLI</a>.</p></noscript><div id="app"></div></body><script defer="defer" src="extensions.js"></script></html>
```

Great, we received a 200 OK status message!

**Note:** The `-v` short option in the CURL request stands for `--verbose`, the `-k` short option stands for `--insecure`, and the `-i` short option is for `--include`.

The next steps will be to test the above deployment with the **latest** **Cilium** version and the **Gateway** **API v.1.0.0**.

## Resources

- Cilium Gateway API Lab: [https://isovalent.com/labs/gateway-api/](https://isovalent.com/labs/gateway-api/)
- Cilium Advanced Gateway API Lab: [https://isovalent.com/labs/advanced-gateway-api-use-cases/](https://isovalent.com/labs/advanced-gateway-api-use-cases/)
- Migrate from Ingress to Gateway: [https://docs.cilium.io/en/v1.14/network/servicemesh/ingress-to-gateway/ingress-to-gateway/](https://docs.cilium.io/en/v1.14/network/servicemesh/ingress-to-gateway/ingress-to-gateway/)
- RKE2 Installation Methods: [https://docs.rke2.io/install/methods](https://docs.rke2.io/install/methods)

Thanks for reading!

DevOps Engineer @ Cisco | Blogging at [https://blog.grosdouli.dev](https://blog.grosdouli.dev/)

## More from Eleni Grosdouli

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--ab1769cc28a3---------------------------------------)