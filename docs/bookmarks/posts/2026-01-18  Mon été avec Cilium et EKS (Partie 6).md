---
title: "Mon été avec Cilium et EKS (Partie 6)"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-6-a393c9701c12"
author:
  - "[[Joseph Ligier]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

## Introduction

D ans la [précédente partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-5-118814fd100c), nous avons vu comment nous extraire du réseau d’aws avec le mode overlay. Dans cette partie, nous allons voir comment se passer de kube-proxy.

## Au fait c’est quoi kube-proxy?

Kube-proxy est un service réseau de kubernetes qui s’installe sur chaque nœud (un DaemonSet). Il s’occupe principalement de la ressource “service” (je mets entre guillemet car je n’ai jamais été sûr que le terme ait été bien choisi). Il utilise un tout autre réseau que celui des pods.

Il y a différents types de “services”:

- ClusterIP: permet de loadbalancer en interne la communication entre les pods.
- NodePort: permet de loadbalancer en externe la communication d’une resource externe vers des pods du réseau (IPs des nœuds et les ports peuvent être entre 30000–32767)
- LoadBalancer: assez proche du NodePort à part qu’il va s’interfacer avec un LoadBalancer (sur AWS, on a principalement ALB et NLB)
- ExternalName: un peu spécial celui là, c’est pour passer outre du dns par défaut

Pour résumer, kube-proxy va créer des load balancers virtuels (en interne ou en externe).

## Pourquoi le remplacer par Cilium?

kube-proxy utilise massivement iptables (il peut également utiliser [ipvs](https://medium.com/@selfieblue/how-to-enable-ipvs-mode-on-aws-eks-7159ec676965)), cela peut avoir des conséquences au niveau CPU voire sécurité. En effet quand un nouveau “service” est créé les règles d’Iptables doivent être supprimé et créé sur chacun des serveurs.

Autres raisons: certaines fonctionnalités de Cilium ne fonctionnent que si Cilium utilise le mode sans kube-proxy (*kube-proxy free*).

## Pré-requis

- un compte AWS avec des access keys
- un peu d’argent (Pour une heure: 0.1 $ pour le cluster eks, environ 0.08 $ pour deux t3.medium et 0.05 $ pour la nat gateway). Durée minimale: environ 30 minutes
- eksctl: outil pour déployer des clusters eks
- aws iam authenticator: outil pour s’authentifier auprès du cluster eks
- aws cli: outil pour communiquer avec l’API d’AWS
- kubectl: outil pour controler le cluster kubernetes
- cilium cli: outil pour gérer cilium
- helm: outil pour installer cilium

Comme AWS EKS est un service payant, il est conseillé d’avoir bien installé les outils avant de créer le cluster.

## Déploiement d’un cluster AWS EKS

Le déploiement du cluster EKS est le même que pour [la partie 1](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-partie-1-99a66ed6671f), je laisse vous y reporter.

## Installation de Cilium

On va déjà supprimer kube-proxy et l’aws cni:

```c
kubectl -n kube-system delete daemonset kube-proxy
kubectl -n kube-system patch daemonset aws-node --type='strategic' -p='{"spec":{"template":{"spec":{"nodeSelector":{"io.cilium/aws-node-enabled":"true"}}}}}'
```

On va rechercher le dns qui permet de communiquer avec l’API de EKS (le endpoint):

```c
aws eks describe-cluster --name basic-cilium | jq -r .cluster.endpoint
https://29F17965D68DB5502F627B2D22596152.gr7.us-east-1.eks.amazonaws.com
```

On va alors créer les variables:

```c
API_SERVER_IP=29F17965D68DB5502F627B2D22596152.gr7.us-east-1.eks.amazonaws.com
API_SERVER_PORT=443
```

Puis on va installer (enfin!) Cilium:

```c
helm repo add cilium https://helm.cilium.io/
helm repo update
helm install cilium cilium/cilium --version 1.13.4 \
                                  --namespace kube-system \
                                  --set eni.enabled=true \
                                  --set ipam.mode=eni \
                                  --set egressMasqueradeInterfaces=eth0 \
                                  --set tunnel=disabled \
                                  --set kubeProxyReplacement=strict \
                                  --set k8sServiceHost=${API_SERVER_IP} \
                                  --set k8sServicePort=${API_SERVER_PORT}
```

Il faut donc rajouter trois options: *kubeProxyReplacement* pour dire qu’on ne veut plus de kubeproxy (on peut aussi dire qu’on ne veut kube-proxy pour tel type de service et cilium pour tel type de service). *k8sServiceHost* et *k8sServicePort* pour indiquer à cilium comment communiquer avec l’API d’eks.

On vérifie que tout fonctionne bien:

```c
cilium status --wait
    /¯¯\
 /¯¯\__/¯¯\    Cilium:             OK
 \__/¯¯\__/    Operator:           OK
 /¯¯\__/¯¯\    Envoy DaemonSet:    disabled (using embedded mode)
 \__/¯¯\__/    Hubble Relay:       disabled
    \__/       ClusterMesh:        disabled

DaemonSet         cilium             Desired: 2, Ready: 2/2, Available: 2/2
Deployment        cilium-operator    Desired: 2, Ready: 2/2, Available: 2/2
Containers:       cilium             Running: 2
                  cilium-operator    Running: 2
Cluster Pods:     2/2 managed by Cilium
Image versions    cilium             quay.io/cilium/cilium:v1.13.4@sha256:bde8800d61aaad8b8451b10e247ac7bdeb7af187bb698f83d40ad75a38c1ee6b: 2
                  cilium-operator    quay.io/cilium/operator-aws:v1.13.4@sha256:c6bde19bbfe1483577f9ef375ff6de19402ac20277c451fe05729fcb9bc02a84: 2
```

L’installation est résumé ici:

[https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-kube-proxy-free.md](https://github.com/littlejo/cilium-eks-cookbook/blob/main/install-cilium-eks-kube-proxy-free.md)

Autre test intéressant:

```c
kubectl -n kube-system exec ds/cilium -c cilium-agent -- cilium status
KVStore:                 Ok   Disabled
Kubernetes:              Ok   1.27+ (v1.27.3-eks-a5565ad) [linux/amd64]
Kubernetes APIs:         ["cilium/v2::CiliumClusterwideNetworkPolicy", "cilium/v2::CiliumEndpoint", "cilium/v2::CiliumNetworkPolicy", "cilium/v2::CiliumNode", "core/v1::Namespace", "core/v1::Node", "core/v1::Pods", "core/v1::Service", "discovery/v1::EndpointSlice", "networking.k8s.io/v1::NetworkPolicy"]
KubeProxyReplacement:    Strict   [eth0 192.168.53.201 (Direct Routing)]
Host firewall:           Disabled
CNI Chaining:            none
CNI Config file:         CNI configuration file management disabled
Cilium:                  Ok   1.13.4 (v1.13.4-4061cdfc)
NodeMonitor:             Listening for events on 2 CPUs with 64x4096 of shared memory
Cilium health daemon:    Ok
IPAM:                    IPv4: 2/10 allocated,
IPv6 BIG TCP:            Disabled
BandwidthManager:        Disabled
Host Routing:            Legacy
Masquerading:            IPTables [IPv4: Enabled, IPv6: Disabled]
Controller Status:       19/19 healthy
Proxy Status:            OK, ip 192.168.41.230, 0 redirects active on ports 10000-20000
Global Identity Range:   min 256, max 65535
Hubble:                  Ok   Current/Max Flows: 209/4095 (5.10%), Flows/s: 0.37   Metrics: Disabled
Encryption:              Disabled
Cluster health:          2/2 reachable   (2023-07-19T08:13:41Z)
```

La ligne intéressante est:

```c
KubeProxyReplacement:    Strict   [eth0 192.168.53.201 (Direct Routing)]
```

On peut aussi avoir plus de détails avec l’option verbose:

```c
kubectl -n kube-system exec ds/cilium -c cilium-agent -- cilium status --verbose
...
KubeProxyReplacement Details:
  Status:                 Strict
  Socket LB:              Enabled
  Socket LB Tracing:      Enabled
  Socket LB Coverage:     Full
  Devices:                eth0 192.168.53.201 (Direct Routing)
  Mode:                   SNAT
  Backend Selection:      Random
  Session Affinity:       Enabled
  Graceful Termination:   Enabled
  NAT46/64 Support:       Disabled
  XDP Acceleration:       Disabled
  Services:
  - ClusterIP:      Enabled
  - NodePort:       Enabled (Range: 30000-32767)
  - LoadBalancer:   Enabled
  - externalIPs:    Enabled
  - HostPort:       Enabled
...
```

On va regarder point par point ce que veut dire cela…

## HostPort

```c
Services:
  - ClusterIP:      Enabled
  - NodePort:       Enabled (Range: 30000-32767)
  - LoadBalancer:   Enabled
  - externalIPs:    Enabled
  - HostPort:       Enabled
```

On retrouve les services *ClusterIP*, *NodePort*, *LoadBalancer* et *externalIPs*. Il y a aussi HostPort que je n’ai pas parlé. Qu’est-ce que c’est?

C’est simplement pour se connecter depuis un nœud vers un pod

Créons un pod:

```c
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
    - name: nginx
      image: nginx
      ports:
        - containerPort: 80
          hostPort: 80
```
```c
kubectl apply -f nginx-hostport.yaml
```
```c
kubectl get pod -o wide
NAME    READY   STATUS    RESTARTS   AGE   IP              NODE                             NOMINATED NODE   READINESS GATES
nginx   1/1     Running   0          72s   192.168.45.94   ip-192-168-53-201.ec2.internal   <none>           <none>
```

L’ip du pod est “192.168.45.94"

On se connecte sur un nœud, vous pouvez le faire via SSM mais aussi directement avec kubectl:

```c
kubectl debug node/ip-192-168-53-201.ec2.internal -it --image=ubuntu
root@ip-192-168-53-201:/# chroot /host/
```

On tape une commande curl pour tester le port 80:

```c
curl http://192.168.45.94
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

Vous pouvez aussi le faire sur l’autre nœud, ça fonctionne aussi!

Pour voir les services pris en charge par cilium dans un cluster kubernetes, il suffit de taper:

```c
kubectl -n kube-system exec ds/cilium -c cilium-agent -- cilium service list
ID   Frontend               Service Type   Backend
1    10.100.0.1:443         ClusterIP      1 => 192.168.38.254:443 (active)
                                           2 => 192.168.7.21:443 (active)
2    10.100.48.36:443       ClusterIP      1 => 192.168.18.107:4244 (active)
3    10.100.0.10:53         ClusterIP      1 => 192.168.28.19:53 (active)
                                           2 => 192.168.11.178:53 (active)
4    10.100.224.221:8080    ClusterIP      1 => 192.168.51.102:8080 (active)
5    192.168.18.107:30598   NodePort       1 => 192.168.51.102:8080 (active)
6    0.0.0.0:30598          NodePort       1 => 192.168.51.102:8080 (active)
7    10.100.191.108:8080    ClusterIP      1 => 192.168.30.93:8080 (active)
8    192.168.18.107:30786   NodePort       1 => 192.168.30.93:8080 (active)
9    0.0.0.0:30786          NodePort       1 => 192.168.30.93:8080 (active)
10   192.168.18.107:40000   HostPort       1 => 192.168.30.93:8080 (active)
11   0.0.0.0:40000          HostPort       1 => 192.168.30.93:8080 (active)
12   192.168.8.11:40000     HostPort       1 => 192.168.30.93:8080 (active)
13   192.168.8.11:30786     NodePort       1 => 192.168.30.93:8080 (active)
14   192.168.8.11:30598     NodePort       1 => 192.168.51.102:8080 (active)
```

## XDP Acceleration

```c
XDP Acceleration:       Disabled
```

XDP veut dire **eXpress Data Path.** Cela va permettre d’avoir un réseau plus performant. Les flux réseaux vont être directement rattachés à la carte réseau sans devoir passer par les couches réseau du kernel linux. Il est disponible depuis le kernel linux 4.8. Petite condition (pas des moindres), il faut que le driver de carte réseau et la carte réseau gèrent cela.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*Q2ETWNw7_0ekWN_B.png)

On ne s’éloigne pas trop de la couche 1 du modèle OSI

Sur AWS, il faut installer le driver ENA. Il y aurait pas mal à dire sur le sujet pour l’activer.

## NAT46/64

```c
NAT46/64 Support:       Disabled
```

C’est pour la traduction IPv4 ≤=> IPv6. Pour la connexion entre infrastructure IPv4 et cluster kubernetes IPv6.

## Graceful termination

```c
Graceful Termination:   Enabled
```

Lors de la suppression d’un “service”, cela permet de ne pas supprimer immédiatement le service et de laisser les connexions en cours se finir.

Je vous laisse une vidéo sur le sujet:

## Session Affinity

```c
Session Affinity:       Enabled
```

Session affinity est une option de la ressource “service”. Par défaut c’est *None* mais on peut mettre *Client IP*. Ça permet de garder le flux vers le même pod pour chaque client.

Voilà ce que dit explain de kubectl:

```c
kubectl explain Service.spec.sessionAffinity
KIND:       Service
VERSION:    v1

FIELD: sessionAffinity <string>

DESCRIPTION:
    Supports "ClientIP" and "None". Used to maintain session affinity. Enable
    client IP based session affinity. Must be ClientIP or None. Defaults to
    None. More info:
    https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies

    Possible enum values:
     - \`"ClientIP"\` is the Client IP based.
     - \`"None"\` - no session affinity.
```

## Backend Selection

```c
Backend Selection:      Random
```

Comment loadbalancer les pods? Par défaut, c’est random, mais il y a aussi l’algorithme Maglev. Cet algorithme permet d’améliorer la résilience en cas de panne. Ceci est uniquement pour le réseau externe vers le réseau interne (trafic “nord-sud” donc NodePort et Load Balancer).

Pour ce faire, il suffit de changer loadBalancer.algorithm=maglev:

```c
helm upgrade cilium cilium/cilium --version 1.13.4   --reuse-values   --namespace kube-system  --set loadBalancer.algorithm=maglev
kubectl rollout restart -n kube-system ds/cilium
```

On a alors:

```c
kubectl exec -it ds/cilium -n kube-system -c cilium-agent -- cilium status --verbose | grep Backen
  Backend Selection:      Maglev (Table Size: 16381)
```

Notez bien que la fonctionnalité est en beta.

## Mode

```c
Mode:                   SNAT
```

Par défaut le mode est du SNAT mais ça peut aussi être du DSR (Direct Server Return). C’est pour les “services” externes (Load Balancer, NodePort). Il permet la traduction de l’ip externe vers une ip interne via SNAT. Ce qui implique pas mal de surcoût réseau. L’intérêt du DSR est que l’ip externe n’est pas caché. Si on en croit la [doc](https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/), il faut désactiver la vérification check source destination. Chez moi c’est déjà le cas:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*dQam3HAlHb5HfPTCfxwwsA.png)

Je peux a priori le mettre en place:

```c
helm upgrade cilium cilium/cilium --version 1.13.4   --reuse-values   --namespace kube-system  --set loadBalancer.mode=dsr
kubectl rollout restart -n kube-system ds/cilium
```

On vérifie:

```c
kubectl exec -it ds/cilium -n kube-system -c cilium-agent -- cilium status --verbose | grep Mode
  Mode:                   DSR
```

À tester plus en profondeur avant de mettre en production.

## Devices

```c
Devices:                eth0 192.168.53.201 (Direct Routing)
```

C’est simplement par où passe le flux lors de flux avec extérieur

## Socket LB

```c
Socket LB:              Enabled
Socket LB Tracing:      Enabled
Socket LB Coverage:     Full
```

Socket LB c’est pour clusterIP service donc les flux transitant uniquement dans le cluster uniquement.

Je pense qu’on n’a pas mal défraîchi le sujet du remplacement de kube-proxy par Cilium. Le [prochaine partie](https://medium.com/@littel.jo/mon-%C3%A9t%C3%A9-avec-cilium-et-eks-%C3%A9pilogue-e563e40aeab2) sera la dernière. Elle fera le bilan de la série d’article.

## More from Joseph Ligier

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--a393c9701c12---------------------------------------)