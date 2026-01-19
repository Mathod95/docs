---
title: "How to deploy a Harbor on Kubernetes with Helm"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@emircanagac/how-to-deploy-a-harbor-with-helm-k8s-minikube-25f89af83610"
author:
  - "[[Emircan Agac]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*jlEtBmSLVnPT8i6jr7349w.png)

> Read this blog for [free](https://medium.com/@ithesadson/how-to-deploy-a-harbor-with-helm-k8s-minikube-25f89af83610?sk=d92758126fce2d24bbc1c226d5ace450).

Before you start Services you need:  
1- Minikube(or any k8s), Kubectl, Helm.  
2- Enabled ingress addons.

- Before you start, make sure you have installed the necessary tools and enabled the ingress addon.*  
	$kubectl version  
	$minikube version*  
	*$helm version  
	$minikube addons enable ingress*

### 1-) Deploy Harbor with Helm

- To add a Helm repository, use the command `***helm repo add harbor https://helm.goharbor.io***`*,* and then update the repositories with `helm repo update`.
```c
helm repo add harbor https://helm.goharbor.io
helm repo update
```
- Create **values-harbor.yaml** file in the same directory.
```c
# Global variables
externalURL: https://tss-dev.core.harbor.dev.lab
harborAdminPassword: "Harbor12345"

expose:
  ingress:
    hosts:
      core: tss-dev.core.harbor.dev.lab
    className: "<INGRESS_NAME>"
```
- ~/harbor-deploy$ ls  
	\- *harbor* - *values-harbor.yaml*
- Install harbor with helm by parameterizing values-harbor.yaml
```c
helm install harbor harbor/harbor -f values-harbor.yaml -n harbor --create-namespace
```
- Please wait for several minutes for Harbor deployment to complete.
```c
kubectl get pod -n harbor
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*xiMhPoRyRHaXsr7c46cExw.png)

K9s show pods

- Check the ingress after the pods are running.
```c
k get ingress -n harbor
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CzzNGxgpfWKUFKG2SFbZ-Q.png)

K9s show ingress

- Add the following line to /etc/hosts file ( Ingress Address + Hosts)
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*H3GIOUzoUstpVzbpk4TXwg.png)

/etc/hosts file

### 2-) Accessing Harbor UI Securely

To ensure your connection to the Harbor UI is secure (HTTPS), you need to retrieve the certificate and add it to your browser’s trusted certificates.

```c
# Retrieve the Harbor ingress secret and save it to a file
kubectl get secret harbor-ingress -n harbor -o json | jq -r '.data."ca.crt"' | base64 -d > harbor-ca.crt
```
- Save the certificate output to a file named `harbor-ca.crt` and add it to your browser's trusted certificates. This will ensure your connection is secure (HTTPS).  
	(I didn’t set up an https connection because I didn’t add the certificate.)

**Access the domain URL (HOST) from the browser**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rgnGPgAEdAYLWiLFMBoFXg.png)

Default username: admin, default password: Harbor12345

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*MWZDyuKMuUAZMy9H5B-geQ.png)

### 3-) How to push an image to Harbor

```c
kubectl get secret harbor-ingress -n harbor -o json | jq -r '.data."tls.crt"' | base64 -d
```
- Copy the certificate and paste it at the end of /etc/ssl/certs/ca-certificates.crt

> If you skip this step, you may receive the “tls: certificate verification failed: x509: certificate signed by unknown authority” error when pushing your image to the harbor registry.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Ad89HZbW78TfVnBxCu1tfA.png)

- I will use the helm push command, you can try whatever you want.
```c
docker login {domain} -u admin

helm package harbor/
helm push harbor-1.14.2.tgz oci://{Domain}/library
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*oh9MNtrvEYvxcBV1w_UuLg.png)

That’s it, this is how you can deploy your harbor with the helm. Happy day everyone🎉👻🎉

\=============================

***🤯 Knowledge should be Free and Disseminated.***

\=============================

## More from Emircan Agac

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--25f89af83610---------------------------------------)