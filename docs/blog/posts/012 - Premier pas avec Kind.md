---
title: Premier pas avec Kind
date: 2025-12-03
categories:
  - Kind
tags:
  - Kind
info: Il existe un articles plus complet dans "archives/012.md"
todo: Ajouter un embed de la doc en fin d'article
sources:
  - https://mcvidanagama.medium.com/set-up-a-multi-node-kubernetes-cluster-locally-using-kind-eafd46dd63e5
  - https://itnext.io/kubernetes-multi-cluster-implementation-in-under-10-minutes-2927952fb84c
  - https://medium.com/ibm-cloud/gitops-quick-start-with-kubernetes-kind-cluster-5677f94adf69
  - https://shashanksrivastava.medium.com/install-configure-argo-cd-on-kind-kubernetes-cluster-f0fee69e5ac4
  - https://magmax.org/en/blog/argocd/
  - https://phoenixnap.com/kb/kubernetes-kind
  - https://blog.kubesimplify.com/getting-started-with-kind-creating-a-multi-node-local-kubernetes-cluster
  - https://developers.redhat.com/articles/2023/01/16/how-prevent-computer-overload-remote-kind-clusters
  - https://linuxconcept.com/creating-a-multi-node-cluster-with-kind/
  - https://docs.dapr.io/operations/hosting/kubernetes/cluster/setup-kind/
  - https://www.baeldung.com/ops/kubernetes-kind
  - https://itnext.io/starting-local-kubernetes-using-kind-and-docker-c6089acfc1c0
  - https://mcvidanagama.medium.com/set-up-a-multi-node-kubernetes-cluster-locally-using-kind-eafd46dd63e5
---

![](../../assets/images/kind/kind.png)

## Introduction
[Kind](https://kind.sigs.k8s.io/) (Kubernetes in Docker) est un outil permettant de créer des clusters Kubernetes locaux à l’aide de conteneurs Docker. D’autres solutions existent, comme Kubeadm, Kops ou Minikube, mais elles sont souvent plus complexes à configurer.

Kind se distingue par sa simplicité, avec une [documentation](https://kind.sigs.k8s.io/docs/user/quick-start/) claire.

<!-- more -->

### Objectifs
- Apprendre à installer kind
- Créer un cluster single ou multi node
- Déployer une version spécifique de Kubernetes
- Supprimer un Cluster single ou multi node
- Exporter les logs d'un cluster kind
- Déployer une application

### Prérequis
- Docker/Docker Desktop

### Ma configuration
- Debian 12
- kubectl
- [Docker desktop](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=dd-smartbutton&utm_location=module) 4.28.0

---

## Installation de Kind

### Prérequis

Le seul prérequis pour utiliser Kind est d'avoir Docker d'installer. Dans notre cas nous utiliserons Docker-Desktop sous Windows lié à WSL.

Sur Debian pour l'installation nous utiliserons les commandes suivante:

=== "Brew"

    ```shell hl_lines="1"
    brew install kind
    ```
    
    !!! info

        The following are community supported efforts. The kind maintainers are not involved in the creation of these packages, and the upstream community makes no claims on the validity, safety, or content of them.

=== "Release Binaries"
    
    ```shell hl_lines="1 7 8"
    [ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100    97  100    97    0     0    822      0 --:--:-- --:--:-- --:--:--   829
      0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
    100 6304k  100 6304k    0     0  6132k      0  0:00:01  0:00:01 --:--:-- 6132k
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    ```

Afin de s'assurer que Kind est bien installer nous pouvons utiliser la commande `kind version` pour s'assurer de son bon fonctionnement.

```shell hl_lines="1"
kind version
kind v0.30.0 go1.25.4 linux/amd64
```

## Création d'un cluster

=== "Single Node"

    Aucune configuration nécéssaire pour créer un cluster single node juste la commande suivante:

    ```shell hl_lines="1"
    kind create cluster
    Creating cluster "kind" ...
     ✓ Ensuring node image (kindest/node:v1.34.0) 🖼
     ✓ Preparing nodes 📦
     ✓ Writing configuration 📜
     ✓ Starting control-plane 🕹
     ✓ Installing CNI 🔌
     ✓ Installing StorageClass 💾
    Set kubectl context to "kind-kind"
    You can now use your cluster with:

    kubectl cluster-info --context kind-kind

    Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂
    ```

    La création du cluster ce feras avec une image pré-built héberger sur [Docker Hub](https://hub.docker.com/r/kindest/node/)

    Vous switcher automatiqment sur le context du cluster que vous venez de créer.  
    Vous pouvez utiliser la commande `kubectl get nodes` pour vérifier que votre cluster fonctionne correctement.

    ```shell hl_lines="1"
    kubectl get nodes
    NAME                 STATUS   ROLES           AGE     VERSION
    kind-control-plane   Ready    control-plane   5m28s   v1.34.0
    ```

=== "Multi Node"

    Pour un cluster avec plusieurs nodes un fichier de configuration comme suit seras nécéssaire

    ```yaml linenums="1" title="multiNode.yaml"
    apiVersion: kind.x-k8s.io/v1alpha4
    kind: Cluster
    nodes:
    - role: control-plane
    - role: control-plane
    - role: control-plane
    - role: worker
    - role: worker
    - role: worker
    ```

    Dans ce fichier de configuration, nous créons un cluster multi-nodes avec 3 control-plane et 3 worker

    Pour la commande on ajoute juste le flag `--config` et le chemin de notre configuration

    ```shell hl_lines="1"
    kind create cluster --config multiNode.yaml
    Creating cluster "kind" ...
     ✓ Ensuring node image (kindest/node:v1.34.0) 🖼
     ✓ Preparing nodes 📦 📦 📦 📦 📦 📦
     ✓ Configuring the external load balancer ⚖
     ✓ Writing configuration 📜
     ✓ Starting control-plane 🕹
     ✓ Installing CNI 🔌
     ✓ Installing StorageClass 💾
     ✓ Joining more control-plane nodes 🎮
     ✓ Joining worker nodes 🚜
    Set kubectl context to "kind-kind"
    You can now use your cluster with:

    kubectl cluster-info --context kind-kind

    Not sure what to do next? 😅  Check out https://kind.sigs.k8s.io/docs/user/quick-start/
    ```

    La création du cluster ce feras avec une image pré-built héberger sur [Docker Hub](https://hub.docker.com/r/kindest/node/)

    Vous switcher automatiqment sur le context du cluster que vous venez de créer.  
    Vous pouvez utiliser la commande `kubectl get nodes` pour vérifier que votre cluster fonctionne correctement.

    ```shell hl_lines="1"
    kubectl get nodes
    NAME                  STATUS     ROLES           AGE   VERSION
    kind-control-plane    Ready      control-plane   65s   v1.34.0
    kind-control-plane2   Ready      control-plane   65s   v1.34.0
    kind-control-plane3   Ready      control-plane   65s   v1.34.0
    kind-worker           Ready      <none>          65s   v1.34.0
    kind-worker2          Ready      <none>          65s   v1.34.0
    kind-worker3          Ready      <none>          65s   v1.34.0
    ```

## Cluster Configurations
Par défaut le fichier de configuration de votre cluster se trouveras dans ${HOME}/.kube/config

```shell hl_lines="1"
cat ${HOME}/.kube/config
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJME1ESXhNREUwTXpjd09Wb1hEVE0wTURJd056RTBNemN3T1Zvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTWZmCjk5YmxnV1FFN1RBWXhSNmd5Yk9PbG0rRFRvdjBMTklUSG5ydDdkTzVydTljK3FvLzNqQzZWcTVseTByZ21odUIKTXgvVVlvd09MWWJrZ21kWkpNS0NENjh6bENFSVRNSHB4Q2xlaXYrdVdkVCtTYWJ2MkkyM2wvVjdsUjFVTzRQRwpJdWNLaFZNT0JGQ1Axci8yMDVPQVJlWDNtSjg0SER2UW03K2RKaWdtVUhVYk9DallidXIzeW9xcldxdXZ5d2hFCmNPaW1aN1hzMVc4WjBpTFF2L2pkYXhzMThqYWMzci9VbUJRa3FCV2ozSUJ2S3o3NHVPWVYxUWNoa0ZEMWJMVkkKSkZKMWc3UmUxazNHWkpUUzRHeEo0RWpoR3NyV01vRmlRT21uWTZneFA5TlpvZ2k2bkNRaWQ1Q0ZteUJnM1ZocAovMkRWcHUrVGNtUktxTlhPMEEwQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZCcmVlaHFVOHpkNjlTSXdYaC9FQ1Jwc05HcURNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBQ3hrT2J0L3hXayt2dTdGMTk1UQpNTVpYUWR0alUvNjVidHp1MDZWVU9icEtOZVA0Qzkwb0VNWDBpbzJKbVhlelE2TTJnUGYyb2Z4MEdEOUE1dWxtCjYxWXFmR0ViQ1FzNytRaVFyc1ppbmhDMXI3L3Q1OUpwbkp4VCtVV1NwVkhUSmNnSlFQbXI3QlRDd2tkR3ZscEYKdFgxQTBTUGNPdVJUM2RRM3EvVkJ0b3BGMWhiWUN5S2cyM0t1YUZJZjZmSlY1K2hSNWgreENTNGpUT3Z6RVNqWgprZVhxTmxaM0ZWS0JTQzVZeWhORmhMelNKT3U1ZUJhTU9YVGl2aVg5ckVRcUFRYmlNcWMyVGZlekZWV3VUL0M3Cnc5R0FhamJNTnY4UVZQNU9jc0RDTGRIS1BRTDRpSEUxMHpEVllvRkwyb2JHQXFJMVNJamt0RTVTMFlNTS9uYlcKSFlrPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://127.0.0.1:40299
  name: kind-kind
contexts:
- context:
    cluster: kind-kind
    user: kind-kind
  name: kind-kind
current-context: kind-kind
kind: Config
preferences: {}
users:
- name: kind-kind
  user:
    client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lJRnpiYUxLcDl6MlV3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TkRBeU1UQXhORE0zTURsYUZ3MHlOVEF5TURreE5ETTNNVEZhTURReApGekFWQmdOVkJBb1REbk41YzNSbGJUcHRZWE4wWlhKek1Sa3dGd1lEVlFRREV4QnJkV0psY201bGRHVnpMV0ZrCmJXbHVNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXRHU2R2V0liQ2Y0SkpqVXoKNTM2VEh0WGRSeFN6bWVmYWo5L2kvU0xBQ3B0dCtISTBLV2ZOby9SQjB6UmxyMWFaN2UxclRLQUpHNFZLRDhydgpkak9CdDZPZUMwdElUVUQxZndJUGlTbUVRVURxMUhuRURHMnI2a0J3ek82Z0ZEcGxjbFpyV3p0WGRmdXZweXJICkVqOTVLZ0pDS0tmbUIzZFBlcjk5cTVRdU1URGw0MXBZNUhJWUswL3FNTFRsVVFUSnVlQVdqOHViaGVURDBUZDAKdFRBNElIZlA2UkJGWmtGUlJWeUh3N3BsdU4yNlJqOW9QYXVPckNUcWhTdGxtb2NKM1o2dXV4a1BPZkg1YXJ5TwpIbFNNWnJZWDdLVGk0Wmx6bTl1Ymg0b1V2NXhuZHJOajNabWV1S1hubWx3SVNsY0lWSnZTNE5SYWhBOC92TEF2CklPbk5Jd0lEQVFBQm8xWXdWREFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUgKQXdJd0RBWURWUjBUQVFIL0JBSXdBREFmQmdOVkhTTUVHREFXZ0JRYTNub2FsUE0zZXZVaU1GNGZ4QWthYkRScQpnekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBVFhJM3BtenZvZDFTR1BhcGdCTWsyQ3g0OU4vaE92OUgvanNICkc5MUV0VCtYR2FMM1I3WWhIMG8vMm41MVcrTncxazdiY3l4NkJtT0IzNW9OQlJJNHpZS3lOYWZuN0x3UjRCSVAKb1QvZzZaZUJ2bTNhWC9JeDNCTUt1eHFHVmowZHZXREFWRDB1WGdiVE0zSHpOcXc1dnVNZTNyNXNWRmxoWDFoZgpPa2ttTFZXeTZuYXVvZzUxb0hadHNnVk9jNkl4M3lDTEJkeis0RDRSQVVtSTYwdlc4NmN3SUE3UE4yQlNhZlNiClJWMzZrQWduNGFTMmlmQXZCRDNDeFF1N0swYzYzNUx3aXYvR08vMkRSakx0NzV0ZVROdGQ4QXBIKzRsMFQzelMKRFh1VW1qcVZLRHZQL0lYbXVUTStZWXBkdzVZdzg1QXQ4UlhBY012dGQ1c2xSSUo2a3c9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBdEdTZHZXSWJDZjRKSmpVejUzNlRIdFhkUnhTem1lZmFqOS9pL1NMQUNwdHQrSEkwCktXZk5vL1JCMHpSbHIxYVo3ZTFyVEtBSkc0VktEOHJ2ZGpPQnQ2T2VDMHRJVFVEMWZ3SVBpU21FUVVEcTFIbkUKREcycjZrQnd6TzZnRkRwbGNsWnJXenRYZGZ1dnB5ckhFajk1S2dKQ0tLZm1CM2RQZXI5OXE1UXVNVERsNDFwWQo1SElZSzAvcU1MVGxVUVRKdWVBV2o4dWJoZVREMFRkMHRUQTRJSGZQNlJCRlprRlJSVnlIdzdwbHVOMjZSajlvClBhdU9yQ1RxaFN0bG1vY0ozWjZ1dXhrUE9mSDVhcnlPSGxTTVpyWVg3S1RpNFpsem05dWJoNG9VdjV4bmRyTmoKM1ptZXVLWG5tbHdJU2xjSVZKdlM0TlJhaEE4L3ZMQXZJT25OSXdJREFRQUJBb0lCQUdxL3Q5Q2dRNXZ3Sm4zagpzZWxscjYzcHBONHhVKzdaa3k3Y3NEaFgzZ2pvM1hUT01Ddm9iM3A4U28rdlRCVXNURDdONWxjYnhRZnlJbGVpCklYNXpFR29aZXFiNFQ3clhtKzhpeXdyQjlLK2d1Tll2a0dKQ2JCOWRMdU0ydXFmOXZwYWdxVHI5ck0zMnVJVlYKL1NQQlIvUWlEZ0I5Q3RTVU9BWk5WeEszeDNYM21WUWV0Y1R3U1BXcU5aWDJ4WjZCQzVzeW9ZUXdTSXVacVVhTgpSenNzaE5ZWkk5UUtSMnFJOE9LL2tMV2RYSEVUcDc3YjRXejkzeitpS0NIRURUNFQxL3FqQit4cEhZblBZVzdQCjBvdElnSkROQVUrcHB0aUZ2MXZ0cWdCTGtRK2VrQmNRUlh0SE5lcGVWWmRrdy9VaUFmaVlhUU9tMmpXN3J2ZncKN3V5T0dhRUNnWUVBMDRUU1JIaW5vdEJhdmZpQml4akRISmhPT0N0bU5oMG1Uckc4SjVmSk40a0Q1aEVpTUFPTwpwUTV6OHoyN2VKUzljeUZ2REg4VmVRRXcyQkxMTi8ya1UxZUFFcGFoMDBJN2dyTzhJOWZ6MG1sUVgwTHZZdldvCmovWmlDN1lBb1BmN3A2b2R3Q0lKRUY4UTFhYlRjSHViSXdiaHp4dW5GZVlNT3htK2FpcWxPbnNDZ1lFQTJsUWcKelI2UEROSjdIS3FiVlltdW5sU0FaZE42b2lBOHVwY3ExaUtyN2cxTFE5VnZJdjNPVHU1akR3ZTdQVUxjRllwZAp2Sm9QbTROUHpSVi9sNS9CcDZEOS8wNXRsWHY2UDIvU1ErT3ZuQWFnM1pXaXRidGFpNjcvL0NybmRHczZ4MlNNCjVYRW5WQWE1a3V4bThnUjZ3MUZVQ0NjaTlVdTJFbnpsbXNqenEza0NnWUVBdzZpMmxHNERxNkVPZjNJejZzWmkKSGI1cGhKM29zNS90UXBnNGsydGR6NGhuMmRiNWgrNlNjZTVYcGFieUZzMklIY3JNbllPbENrVG11TWxSd0o1WQo5bHNYZHBwdVlTeUFQaHdpcWdsbVdybmVoZkExM3BXZGNtWVlOZnNLdzl3QXB3eSs3bTdOY1o1dXhTUEhyT0k2CkZJR1dPZTI3ZG85UnV3M0tUUXpid0tjQ2dZQWpxTG55eHByMnJTb09kSThLV1lKN3ViRis4QnVIZjF4cjNXVFIKdExnQUdZdkJlSXErWEZYbDdtbWZldFBLSGJGMGt6VGNLUTJEaU43djBDTVcwTEVBZi9yOFNBTDk5MUhZS3B0ZApHME1EYU5HOVgwTkVDMld1aXRha2lSMWtsbDd6VWlqeEVKb3J6eTFnSWR4dWl1ekNHZlp2bm5USE82WnhQcFVCCnd2Q0pnUUtCZ0NNdkNSS25lek12d2ttekRwUC9XZTFpOUVRZmJlaVhkZGtrakRTa0dPeThaY0NyRlNDeEVkSmcKYmFCMkdmZUwwOTNlUkhucGtnU1BVV1JTMlQvVWU0dG9wWE1Hdldza0tUUlF5U3VYeFI3NmkrNm85L1o4cTF5UApyTi9Wdkk0UzdUbVdGYTFUeUxpMGhFY0diSUZWaDFrbWhaSGJ1Qmp3N09nY2JIbVVvWWdUCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg==
```

## Utiliser une image node différente
L'utilisation d'une image différente vous permet de changer la version du cluster Kubernetes créé. Chaque version de Kind supporte une liste spécifique des versions de Kubernetes, vous pouvez voir la liste des versions supportées de Kubernetes depuis cette [page](https://github.com/kubernetes-sigs/kind/releases#:~:text=Images%20pre%2Dbuilt,v1.29.0%40sha256%3Aeaa1450915475849a73a9227b8f201df25e55e268e5d619312131292e324d570).

```shell hl_lines="1"
Images pre-built for this release:

v1.34.0: kindest/node:v1.34.0@sha256:7416a61b42b1662ca6ca89f02028ac133a309a2a30ba309614e8ec94d976dc5a
v1.33.4: kindest/node:v1.33.4@sha256:25a6018e48dfcaee478f4a59af81157a437f15e6e140bf103f85a2e7cd0cbbf2
v1.32.8: kindest/node:v1.32.8@sha256:abd489f042d2b644e2d033f5c2d900bc707798d075e8186cb65e3f1367a9d5a1
v1.31.12: kindest/node:v1.31.12@sha256:0f5cc49c5e73c0c2bb6e2df56e7df189240d83cf94edfa30946482eb08ec57d2
```

Pour spécifier une autre image, utilisez l'option `--image`

```shell hl_lines="1"
kind create cluster --image kindest/node:v1.33.4@sha256:25a6018e48dfcaee478f4a59af81157a437f15e6e140bf103f85a2e7cd0cbbf2
```

## Changer le nom context de votre cluster
Par défaut le context de votre cluster sera nommé `kind`. Vous pouvez utiliser le flag `--name` pour assigner un nom différent.

```shell hl_lines="1"
kind create cluster --name mathod
Creating cluster "mathod" ...
 ✓ Ensuring node image (kindest/node:v1.34.0) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-mathod"
You can now use your cluster with:

kubectl cluster-info --context kind-mathod

Thanks for using kind! 😊
```

La command `kubectl config get-contexts` permet de lister les clusters et indiquer le context en cours d'utilisation

```shell hl_lines="1"
❯ kubectl config get-contexts
CURRENT   NAME           CLUSTER        AUTHINFO       NAMESPACE
          kind-kind      kind-kind      kind-kind      default
*         kind-mathod    kind-mathod    kind-mathod
```

Pour passer d'un cluster à un autre, vous pouvez utiliser `kubectl config use-context <cluster-name>`.

??? tip "Kubectx"

    - kubectx permet de changer rapidement de contexte.
    - kubens permet de basculer facilement entre les namespaces d'un cluster. (intégrer à kubectx)

    ```shell hl_lines="1"
    brew install kubectx
    ```

## Interagir avec le cluster
Après avoir créé un cluster, vous pouvez utiliser kubectl pour interagir avec ce dernier.

```shell hl_lines="1"
kubectl cluster-info
Kubernetes control plane is running at https://127.0.0.1:32991
CoreDNS is running at https://127.0.0.1:32991/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

Vous pouvez également lister tous les containers Kind avec la commande suivante:

```shell hl_lines="1"
docker ps
CONTAINER ID   IMAGE                                COMMAND                  CREATED         STATUS         PORTS                       NAMES
973259b15c3b   kindest/haproxy:v20230606-42a2262b   "haproxy -W -db -f /…"   8 minutes ago   Up 8 minutes   127.0.0.1:39103->6443/tcp   kind-external-load-balancer
6120719d8b42   kindest/node:v1.34.0                 "/usr/local/bin/entr…"   8 minutes ago   Up 8 minutes   127.0.0.1:45665->6443/tcp   kind-control-plane2
fd2be64055ab   kindest/node:v1.34.0                 "/usr/local/bin/entr…"   8 minutes ago   Up 8 minutes   127.0.0.1:33845->6443/tcp   kind-control-plane
f14296cc3f77   kindest/node:v1.34.0                 "/usr/local/bin/entr…"   8 minutes ago   Up 8 minutes   127.0.0.1:40977->6443/tcp   kind-control-plane3
63ba6aa113b6   kindest/node:v1.34.0                 "/usr/local/bin/entr…"   8 minutes ago   Up 8 minutes                               kind-worker3
0098259cc8ce   kindest/node:v1.34.0                 "/usr/local/bin/entr…"   8 minutes ago   Up 8 minutes                               kind-worker2
a4d8e4971eab   kindest/node:v1.34.0                 "/usr/local/bin/entr…"   8 minutes ago   Up 8 minutes                               kind-worker
```

## Suppression d'un cluster

Pour supprimer un cluster nous utiliserons la commande `kind delete clusters <clusterName>`.  

```shell hl_lines="2 9"
❯ kind delete clusters kind
Deleted nodes: ["kind-external-load-balancer" "kind-control-plane2" "kind-control-plane" "kind-control-plane3" "kind-worker3" "kind-worker2" "kind-worker"]
Deleted clusters: ["kind"]
```

---

## Conclusion
Plus d'excuse possible, vous savez maintenant déployer et configurer un cluster Kubernetes single ou multi-nodes via Kind afin d'y déployer toutes sorte d'applications ! Je ne peux que vous conseiller de poursuivre avec l'installation de Helm pour déployer Crossplane, Argo CD et Gitlab.


