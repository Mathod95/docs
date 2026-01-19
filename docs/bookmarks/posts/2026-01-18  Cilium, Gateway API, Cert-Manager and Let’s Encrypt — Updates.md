---
title: "Cilium, Gateway API, Cert-Manager and Let’s Encrypt — Updates"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/cilium-gateway-api-cert-manager-and-lets-encrypt-updates-cc730818cb17"
author:
  - "[[Eleni Grosdouli]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-cc730818cb17---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*wYGkcCEoIkKeAVh-Ry8Ktw.jpeg)

Source: memegenerator.net

***Heads up****! 🚀 The updated documentation is now available at \[*[https://blog.grosdouli.dev/blog/cilium-gateway-api-cert-manager-let's-encrypt](https://blog.grosdouli.dev/blog/cilium-gateway-api-cert-manager-let's-encrypt)*\]. Check it out for the latest info!*

## Introduction

Sunday was a home-lab update day! The [RKE2](https://docs.rke2.io/) automation setup and the different Kubernetes components like [Cilium](https://cilium.io/), [Gateway API](https://gateway-api.sigs.k8s.io/), [cert-manager](https://cert-manager.io/), and l [et’s encrypt](https://letsencrypt.org/) had to get updated. The cool thing is that while reading the for cert-manager **v1.15.0**, the Gateway API support has been graduated to Beta!

What does that mean? We can now use the `--enable-gateway-api` flag during the cert-manager installation and enable support to automatically provision TLS certificates attached to a `Gateway` Kubernetes resource.

In today’s blog post, we will demonstrate how easy it is to integrate Cilium, Gateway API, cert-manager, let’s encrypt, and Cloudflare to dynamically provision TLS certificates on an RKE2 cluster. However, the documentation is not limited to RKE2 deployments. It can be used in any other environment on-prem or in the cloud.

## Prerequisites

1. Operational Kubernetes cluster
2. Cilium as a CNI

## Step 1: Enable Cilium Gateway API

During the RKE2 cluster installation, we need to specify the below configuration to the `rke2-cilium-config.yaml` file to enable the Gateway API functionality.

```c
---
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: rke2-cilium
  namespace: kube-system
spec:
  valuesContent: |-
    image:
      tag: v1.15.1
    kubeProxyReplacement: "true"
    k8sServiceHost: <Server IP address or FQDN>
    k8sServicePort: <Server listening port>
    operator:
      replicas: 3
    gatewayAPI:
      enabled: true
```

**Note:** For Cilium to be fully operational, we need to **pre-deploy** the **Gateway API CRDs** for v1.0.0. If you are unsure how to perform an RKE2 installation, have a look at a [previous post](https://medium.com/p/ab1769cc28a3).

**Note:** To ensure we have the correct Cilium Helm chart version, have a look at the RKE2 [support matrix](https://www.suse.com/suse-rke2/support-matrix/all-supported-versions/rke2-v1-29/).

For any other Kubernetes cluster, if the installation is performed via Helm, follow the instructions found [here](https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/).

## Step 2: Install cert-manager

We will use Helm to install the Kubernetes resources.

### cert-manager

```c
$ helm repo add jetstack https://charts.jetstack.io # Add the Helm repo
$ helm repo update # Update the Helm repositories

$ kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.0/cert-manager.crds.yaml # Deploy the cert-manager CRDs before installation

$ helm install cert-manager jetstack/cert-manager --version v1.15.0 \
    --namespace cert-manager --create-namespace \
    --set "extraArgs={--enable-gateway-api}"
```

For more information about the Helm chart, have a look [here](https://artifacthub.io/packages/helm/cert-manager/cert-manager?modal=install).

## Step 3: Deploy Cloudflare Issuer

> `Issuers`, and `ClusterIssuers`, are Kubernetes resources that represent certificate authorities (CAs) that are able to generate signed certificates by honoring certificate signing requests.

The `Issuers` are namespace specific while the `ClusterIssuers` are cluster wide. For this demo, we will use the `Issuer` definition in the `argocd` namespace.

### Cloudflare Secret

Before we create the `Issuer`, we will deploy a Kubernetes secret that holds the Cloudflare API token. The scope of the token should be `Zone — Zone — Read` and `Zone — DNS — Write`.

```c
---
apiVersion: v1
kind: Secret
metadata:
  name: cloudflare-api-token
  namespace: argocd
type: Opaque
stringData:
  api-token: <Cloudflare API token>
```

### Issuer

```c
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: cloudflare-issuer
  namespace: argocd
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory # For production environments, set the URL to https://acme-v02.api.letsencrypt.org/directory
    email: "<Your email address>"
    privateKeySecretRef:
      name: cloudflare-private-key
    solvers:
      - dns01:
          cloudflare:
            apiTokenSecretRef:
              name: cloudflare-api-token
              key: api-token
```

From the YAML definition we can see the secret created above is referenced in the file and allows us to complete a DNS-01 challenge and issue certificates for the valid DNS domain.

**Note:** As we do not operate a production environment, the let’s encrypt staging server URL was used. In case you want to create a valid certificate for a production environment, use the [https://acme-v02.api.letsencrypt.org/directory](https://acme-v02.api.letsencrypt.org/directory) URL. The **production** **server** has a **rate** **limiter**.

### Validation

```c
$ kubectl get secret -n argocd
NAME                   TYPE     DATA   AGE
cloudflare-api-token   Opaque   1      40s

$ kubectl get issuer -n argocd
NAME                READY   AGE
cloudflare-issuer   True    13s
```

## Step 4: Deploy Cilium GatewayClass

### Cilium GatewayClass

The `GatewayClass` is a template that lets infrastructure providers offer different types of Gateways.

```c
---
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: cilium
spec:
  controllerName: io.cilium/gateway-controller
```
```c
$ kubectl apply -f "cilium_gatewayclass.yaml"

$ kubectl get gatewayclass
NAME     CONTROLLER                     ACCEPTED   AGE
cilium   io.cilium/gateway-controller   True       28m
```

**Note:** If the Cilium GatewayClass is in an Unknown state, check out the official [guide](https://docs.cilium.io/en/v1.15/network/servicemesh/gateway-api/gateway-api/#cilium-gateway-api-support). Ideally, you will describe the Kubernetes resources and check the Cilium pod logging for more information on the underlying issue.

## Step 5: Deploy Gateway and HttpRoute

### Gateway

```c
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: argocd
  namespace: argocd
  annotations:
    cert-manager.io/issuer: cloudflare-issuer # Specify the name of your issuer resource
spec:
  gatewayClassName: cilium
  listeners:
  - hostname: argocd.example.com # Specify a valid domain to reach your application
    name: argocd-example-com-http
    port: 80
    protocol: HTTP
  - hostname: argocd.example.com # Specify a valid domain to reach your application
    name: argocd-example-com-https
    port: 443
    protocol: HTTPS
    tls:
      certificateRefs:
      - kind: Secret
        name: argocd-server-tls # Specify the secret name to be used with your application
    allowedRoutes:
      namespaces:
        from: All
```
```c
$ kubectl get svc -n argocd
NAME                    TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)                      AGE
cilium-gateway-argocd   LoadBalancer   10.43.162.6   x.x.x.x       80:31598/TCP,443:31167/TCP   12s
```

The `Gateway` resource will create a Kubernetes service of type `LoadBalancer`. The `EXTERNAL-IP` will be used to reach the defined application.

### DNS Record

Go back to the Cloudflare UI or [API](https://community.cloudflare.com/t/how-to-create-some-certain-dns-records-using-api/212900) and create an A DNS record pointing to the `EXTERNAL-IP` address.

### HTTPRoute

```c
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  creationTimestamp: null
  name: argocd
  namespace: argocd
spec:
  hostnames:
  - argocd.example.com # Specify a valid domain to reach your application
  parentRefs:
  - name: argocd
  rules:
  - backendRefs:
    - name: argocd-server # Specify the service of the application
      port: 80
    matches:
    - path:
        type: PathPrefix
        value: /
status:
  parents: []
```

**Note:** Ensure the hostname defined reflects a valid DNS domain.

## Step 6: Verify

Now, the only thing that remains is to check whether a valid TLS certificate with the name “argocd-server-tls” was created in the `argocd` namespace.

### Validate Certificate Lifecycle

```c
$ kubectl get certificate,certificaterequest,order -A
NAMESPACE   NAME                                            READY   SECRET              AGE
argocd      certificate.cert-manager.io/argocd-server-tls   True    argocd-server-tls   10m

NAMESPACE   NAME                                                     APPROVED   DENIED   READY   ISSUER              REQUESTOR                                         AGE
argocd      certificaterequest.cert-manager.io/argocd-server-tls-1   True                True    cloudflare-issuer   system:serviceaccount:cert-manager:cert-manager   10m

NAMESPACE   NAME                                                        STATE   AGE
argocd      order.acme.cert-manager.io/argocd-server-tls-1-2066357877   valid   112s
```

### Validate Secrets

```c
$ kubectl get secret -n argocd
NAME                          TYPE                DATA   AGE
cloudflare-api-token          Opaque              1      2m10s
cloudflare-key                Opaque              1      116s
argocd-server-tls             kubernetes.io/tls   2      11s
```

## Conclusions

That’s it! We can now access our application via the External IP and a valid TLS certificate! We demonstrated an easy way to dynamically provision TLS certificates every time a `Gateway` resource is created within a Kubernetes cluster or namespace.

That’s a wrap for this post! 🎉 Thanks for reading! Stay tuned for more exciting updates!

DevOps Engineer @ Cisco | Blogging at [https://blog.grosdouli.dev](https://blog.grosdouli.dev/)

## More from Eleni Grosdouli and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--cc730818cb17---------------------------------------)