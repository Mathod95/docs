---
title: "Kubectl — List all resources in same namespace"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://towardsdev.com/kubectl-list-all-resources-in-same-namespace-d984e2109e49"
author:
  - "[[Bill WANG]]"
---
<!-- more -->

[Sitemap](https://towardsdev.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@bill)## [Towards Dev](https://towardsdev.com/?source=post_page---publication_nav-a648dc4ecb66-d984e2109e49---------------------------------------)

[![Towards Dev](https://miro.medium.com/v2/resize:fill:76:76/1*c2OaLMtxURd1SJZOGHALWA.png)](https://towardsdev.com/?source=post_page---post_publication_sidebar-a648dc4ecb66-d984e2109e49---------------------------------------)

A publication for sharing projects, ideas, codes, and new theories.

Follow up on my Kubernetes blogs about

- [Kubectl — List all resources in same namespace](https://medium.com/towardsdev/kubectl-list-all-resources-in-same-namespace-d984e2109e49)
- [kubectl — Check Service Health with one Line Command](https://medium.com/@ozbillwang/kubectl-check-service-health-with-one-line-command-14b682a4ebb8)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*sBlTz_A2jWys-nuzRD10AQ.jpeg)

We all know to use `kubectl -n <namespace> get all` to list the resources in **<namespace>**, but the list doesn’t include all resources, such as ingress, secrets, endpoints, pv, pvc, cm, CRDs (Custom Resource Definitions), etc.

To get a comprehensive list of all resources, you can use the following command:

```c
kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n <namespace>
```

For example, I’d like to list all resources in namespace `loki` I recently installed (follow my previous blog: [my Research on Grafana Loki in conjunction with Kubernetes](https://medium.com/@ozbillwang/research-on-grafana-loki-in-conjunction-with-kubernetes-4c34c4a1bf07))

you can run the command

```c
$ kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n loki

NAME                         DATA   AGE
configmap/kube-root-ca.crt   1      2d
configmap/loki               1      2d
configmap/loki-gateway       1      2d
configmap/loki-grafana       1      2d
configmap/loki-runtime       1      2d
NAME                        ENDPOINTS                                                        AGE
endpoints/loki              10.xxx.3.41:9095,10.xxx.7.33:9095,10.xxx.3.41:3100 + 1 more...   2d
endpoints/loki-canary       10.xxx.3.5:3500,10.xxx.4.3:3500,10.xxx.7.3:3500                  2d
endpoints/loki-gateway      10.xxx.3.20:8080                                                 2d
endpoints/loki-grafana      10.xxx.3.48:3000                                                 2d
endpoints/loki-headless     10.xxx.3.5:3500,10.xxx.4.3:3500,10.xxx.7.3:3500 + 2 more...      2d
endpoints/loki-memberlist   10.xxx.3.41:7946,10.xxx.7.33:7946                                2d
NAME                                   STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/loki-grafana     Bound    pvc-xxxxxxxx-10d7-4a8a-93b9-xxxxxxxx1f57   10Gi       RWO            default        27d
persistentvolumeclaim/storage-loki-0   Bound    pvc-xxxxxxxx-8d63-4c17-8ce3-xxxxxxxx4a41   10Gi       RWO            default        39d
persistentvolumeclaim/storage-loki-1   Bound    pvc-xxxxxxxx-6207-4dbe-810d-xxxxxxxx23b5   10Gi       RWO            default        39d
NAME                                               READY   STATUS    RESTARTS   AGE
pod/loki-0                                         1/1     Running   0          28d
pod/loki-1                                         1/1     Running   0          28d
pod/loki-canary-hzt2z                              1/1     Running   0          28d
pod/loki-canary-vmhqv                              1/1     Running   0          28d
pod/loki-canary-x56kf                              1/1     Running   0          28d
pod/loki-gateway-9b9967f9f-64zvm                   1/1     Running   0          28d
pod/loki-grafana-79fcdb96b5-5pvls                  1/1     Running   0          27d
pod/loki-grafana-agent-operator-574d44fd67-5jkhl   1/1     Running   0          28d
pod/loki-logs-nsmcs                                2/2     Running   0          28d
pod/loki-logs-smhtz                                2/2     Running   0          14d
pod/loki-logs-xjm5x                                2/2     Running   0          28d
NAME                                        TYPE                 DATA   AGE
secret/loki-grafana                         Opaque               3      2d
secret/loki-logs-config                     Opaque               1      2d
secret/loki-secrets                         Opaque               0      2d
secret/grafana-staging-tls            kubernetes.io/tls    2      2d
secret/sh.helm.release.v1.loki-grafana.v1   helm.sh/release.v1   1      2d
secret/sh.helm.release.v1.loki-grafana.v2   helm.sh/release.v1   1      27d
secret/sh.helm.release.v1.loki.v1           helm.sh/release.v1   1      2d
secret/sh.helm.release.v1.loki.v2           helm.sh/release.v1   1      28d
NAME                                         SECRETS   AGE
serviceaccount/default                       0         2d
serviceaccount/loki                          0         2d
serviceaccount/loki-canary                   0         2d
serviceaccount/loki-grafana                  0         2d
serviceaccount/loki-grafana-agent            0         2d
serviceaccount/loki-grafana-agent-operator   0         2d
NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
service/loki              ClusterIP   10.xxx.116.245   <none>        3100/TCP,9095/TCP   2d
service/loki-canary       ClusterIP   10.xxx.89.249    <none>        3500/TCP            2d
service/loki-gateway      ClusterIP   10.xxx.120.88    <none>        80/TCP              2d
service/loki-grafana      ClusterIP   10.xxx.223.245   <none>        80/TCP              2d
service/loki-headless     ClusterIP   None           <none>        3100/TCP            2d
service/loki-memberlist   ClusterIP   None           <none>        7946/TCP            2d
NAME                                                                    STATE   AGE
order.acme.cert-manager.io/grafana-staging-tls-z5g5s-1209401248   valid   2d
NAME                                            CONTROLLER                   REVISION   AGE
controllerrevision.apps/loki-56bc57c4d7         statefulset.apps/loki        1          2d
controllerrevision.apps/loki-66459d9ddc         statefulset.apps/loki        2          2d
controllerrevision.apps/loki-canary-bd4d74655   daemonset.apps/loki-canary   1          2d
controllerrevision.apps/loki-logs-77594ff8bd    daemonset.apps/loki-logs     1          2d
NAME                         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/loki-canary   3         3         3       3            3           <none>          2d
daemonset.apps/loki-logs     3         3         3       3            3           <none>          2d
NAME                                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/loki-gateway                  1/1     1            1           2d
deployment.apps/loki-grafana                  1/1     1            1           2d
deployment.apps/loki-grafana-agent-operator   1/1     1            1           2d
NAME                                                     DESIRED   CURRENT   READY   AGE
replicaset.apps/loki-gateway-9b9967f9f                   1         1         1       2d
replicaset.apps/loki-grafana-6c69d49979                  0         0         0       2d
replicaset.apps/loki-grafana-79fcdb96b5                  1         1         1       27d
replicaset.apps/loki-grafana-agent-operator-574d44fd67   1         1         1       2d
NAME                    READY   AGE
statefulset.apps/loki   2/2     2d
NAME                                                                 APPROVED   DENIED   READY   ISSUER        REQUESTOR                                         AGE
certificaterequest.cert-manager.io/grafana-staging-tls-z5g5s   True                True    letsencrypt   system:serviceaccount:cert-manager:cert-manager   2d
NAME                                                    READY   SECRET                      AGE
certificate.cert-manager.io/grafana-staging-tls   True    grafana-staging-tls   2d
NAME                                                   ADDRESSTYPE   PORTS       ENDPOINTS                          AGE
endpointslice.discovery.k8s.io/loki-canary-zxlzh       IPv4          3500        10.xxx.3.5,10.xxx.4.3,10.xxx.7.3   2d
endpointslice.discovery.k8s.io/loki-gateway-txzpk      IPv4          8080        10.xxx.3.20                        2d
endpointslice.discovery.k8s.io/loki-grafana-zdb7l      IPv4          3000        10.xxx.3.48                        2d
endpointslice.discovery.k8s.io/loki-headless-dshck     IPv4          3500        10.xxx.3.5,10.xxx.4.3,10.xxx.7.3   2d
endpointslice.discovery.k8s.io/loki-headless-ng9ct     IPv4          3100        10.xxx.3.41,10.xxx.7.33            28d
endpointslice.discovery.k8s.io/loki-headless-wkvnr     IPv4          <unset>     10.xxx.3.20                        2d
endpointslice.discovery.k8s.io/loki-m88c2              IPv4          9095,3100   10.xxx.3.41,10.xxx.7.33            2d
endpointslice.discovery.k8s.io/loki-memberlist-nc7l7   IPv4          7946        10.xxx.3.41,10.xxx.7.33            2d
LAST SEEN   TYPE     REASON   OBJECT                 MESSAGE
49m         Normal   Sync     ingress/loki-grafana   Scheduled for sync
NAME                                                                     CPU         MEMORY     WINDOW
podmetrics.metrics.k8s.io/loki-0                                         24369920n   343904Ki   1m8.585s
podmetrics.metrics.k8s.io/loki-1                                         19932692n   396264Ki   55.967s
podmetrics.metrics.k8s.io/loki-canary-hzt2z                              1407589n    26300Ki    1m6.616s
podmetrics.metrics.k8s.io/loki-canary-vmhqv                              1035257n    27516Ki    1m3.078s
podmetrics.metrics.k8s.io/loki-canary-x56kf                              1232996n    24532Ki    48.344s
podmetrics.metrics.k8s.io/loki-gateway-9b9967f9f-64zvm                   2668592n    12264Ki    1m3.517s
podmetrics.metrics.k8s.io/loki-grafana-79fcdb96b5-5pvls                  1469840n    107792Ki   1m2.849s
podmetrics.metrics.k8s.io/loki-grafana-agent-operator-574d44fd67-5jkhl   813378n     59468Ki    58.691s
podmetrics.metrics.k8s.io/loki-logs-nsmcs                                6911219n    85536Ki    1m6.253s
podmetrics.metrics.k8s.io/loki-logs-smhtz                                4592055n    68124Ki    49.548s
podmetrics.metrics.k8s.io/loki-logs-xjm5x                                5419168n    103636Ki   1m4.439s
NAME                                        AGE
servicemonitor.monitoring.coreos.com/loki   2d
NAME                                       AGE
grafanaagent.monitoring.grafana.com/loki   2d
NAME                                       AGE
logsinstance.monitoring.grafana.com/loki   2d
NAME                                          AGE
metricsinstance.monitoring.grafana.com/loki   2d
NAME                                  AGE
podlogs.monitoring.grafana.com/loki   2d
NAME                                     CLASS    HOSTS                          ADDRESS         PORTS     AGE
ingress.networking.k8s.io/loki-grafana   <none>   grafana.staging.com.au   xx.xx.xxx.xxx   80, 443   2d
NAME                                                 ROLE                AGE
rolebinding.rbac.authorization.k8s.io/loki-grafana   Role/loki-grafana   2d
NAME                                          CREATED AT
role.rbac.authorization.k8s.io/loki-grafana   2023-10-16T13:40:32Z                             2/2     Running   0          28d
```

So with above commands, it lists resources

- certificate.cert-manager.io
- certificaterequest.cert-manager.io
- configmap
- controllerrevision.apps
- daemonset.apps
- deployment.apps
- endpoints
- endpointslice.discovery.k8s.io
- grafanaagent.**monitoring**.grafana.com
- ingress.networking.k8s.io
- logsinstance.**monitoring**.grafana.com
- metricsinstance.**monitoring**.grafana.com
- order.acme.cert-manager.io
- persistentvolumeclaim
- pod
- podlogs.**monitoring**.grafana.com
- podmetrics.metrics.k8s.io
- replicaset.apps
- role.rbac.authorization.k8s.io
- rolebinding.rbac.authorization.k8s.io
- secret
- service
- serviceaccount
- servicemonitor.**monitoring**.coreos.com
- statefulset.apps

This command lists all API resources that support the list operation in the specified namespace, and then retrieves instances of each resource. Obviously, some `monitoring` resources are CRDs

If you want to know which resources are CRDs, you can double check with

```c
kubectl get crds
```

If you use the command frequently, you can set alias on it, such as, put it in `~/.bash_profile`

```c
alias kl="kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n"

# then you can run the short command
kl loki
```

[![Towards Dev](https://miro.medium.com/v2/resize:fill:96:96/1*c2OaLMtxURd1SJZOGHALWA.png)](https://towardsdev.com/?source=post_page---post_publication_info--d984e2109e49---------------------------------------)

[![Towards Dev](https://miro.medium.com/v2/resize:fill:128:128/1*c2OaLMtxURd1SJZOGHALWA.png)](https://towardsdev.com/?source=post_page---post_publication_info--d984e2109e49---------------------------------------)

[Last published 1 day ago](https://towardsdev.com/go-error-handling-gets-better-introducing-errors-astype-7bf716924902?source=post_page---post_publication_info--d984e2109e49---------------------------------------)

A publication for sharing projects, ideas, codes, and new theories.

## More from Bill WANG and Towards Dev

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d984e2109e49---------------------------------------)