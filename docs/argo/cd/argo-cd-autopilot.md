```Shell
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: management
networking:
  apiServerAddress: 192.168.1.23
  apiServerPort: 6443

kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: production
networking:
  apiServerAddress: 192.168.1.23
  apiServerPort: 6444

kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: staging
networking:
  apiServerAddress: 192.168.1.23
  apiServerPort: 6445
```

```shell
kind create cluster --config management.yaml
kind create cluster --config staging.yaml
kind create cluster --config production.yaml
```

```shell
kctx kind-management
```

```shell
❯ kubectl config set-context --current --namespace=argocd
Context "kind-management" modified.
❯ argocd login --core
Context 'kubernetes' updated
❯ argocd cluster add kind-production
WARNING: This will create a service account `argocd-manager` on the cluster referenced by context `kind-production` with full cluster level privileges. Do you want to continue [y/N]? y
INFO[0001] ServiceAccount "argocd-manager" created in namespace "kube-system"
INFO[0001] ClusterRole "argocd-manager-role" created
INFO[0001] ClusterRoleBinding "argocd-manager-role-binding" created
INFO[0001] Created bearer token secret for ServiceAccount "argocd-manager"
Cluster 'https://127.0.0.1:35999' added
❯ argocd cluster add kind-staging
WARNING: This will create a service account `argocd-manager` on the cluster referenced by context `kind-staging` with full cluster level privileges. Do you want to continue [y/N]? y
INFO[0001] ServiceAccount "argocd-manager" created in namespace "kube-system"
INFO[0001] ClusterRole "argocd-manager-role" created
INFO[0001] ClusterRoleBinding "argocd-manager-role-binding" created
INFO[0001] Created bearer token secret for ServiceAccount "argocd-manager"
Cluster 'https://127.0.0.1:37981' added
```

```shell
export GIT_T0KEN=XXXX
export GIT_REPO=https://github.com/Mathod95/argocd-autopilot
argocd-autopilot repo bootstrap
```

```shell title="recover existing repo"
argocd-autopilot repo bootstrap --recover
```
# Create a project

```shell
argocd-autopilot project create production
argocd-autopilot project create staging
argocd-autopilot project create management
```

This will create the `production`,`staging`and `management` [AppProject](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/) and [ApplicationSet](https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/). 
You should see that it was pushed to your installation repository under:
- /projects/production.yaml
- /project/staging.yaml
- /project/management.yaml
# Add an Application

```shell
argocd-autopilot app create hello-world --app github.com/argoproj-labs/argocd-autopilot/examples/demo-app/ -p production --wait-timeout 2m
argocd-autopilot app create hello-world --app github.com/argoproj-labs/argocd-autopilot/examples/demo-app/ -p staging --wait-timeout 2m
```
# Usefull link

- https://www.youtube.com/watch?v=nR-i0Hn6trw
- https://argocd-autopilot.readthedocs.io/en/stable/Getting-Started/
- https://github.com/argoproj/argocd-example-apps