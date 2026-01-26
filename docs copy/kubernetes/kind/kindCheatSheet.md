---
title: Kind CheatSheet 
tags:
  - CheatSheet
  - Kind
todo:
---

# Kind cheat sheet
Kind cheatsheet featuring all the necessary commands required to deploy a kubernetes cluster through Kind.

```shell hl_lines="1" title="Create a cluster"
kind create cluster
```

```shell hl_lines="1" title="Use a custom name for the cluster"
kind create cluster --name=clusterName
```

```shell hl_lines="1" title="Create a cluster with a custom node image"
kind create cluster --image=image
```

```shell hl_lines="1" title="Use a custom configuration for the cluster"
kind create cluster --config=cluster.yaml
```

```shell hl_lines="1" title="When creating a cluster, assign a waiting time for the control plane to go up"
kind create cluster --wait <timeInterval>
```

```shell hl_lines="1" title="View the list of the running clusters"
kind get clusters
```

```shell hl_lines="1" title="View information about a cluster"
kubectl cluster-info --context kind-clusterName
```

```shell hl_lines="1" title="Export logs"
kind export logs
```

```shell hl_lines="1" title="Delete a cluster"
kind delete cluster --name clusterName
```

??? Tips "ABBR"

    ``` shell
    abbr "kicc"="kind create cluster"
    abbr "kiccn"="kind create cluster --name %"
    abbr "kiccc"="kind create cluster --config %"
    abbr "kigc"="kind get clusters"
    abbr "kign"="kind get nodes"
    abbr "kidc"="kind delete cluster"
    abbr "kidcn"="kind delete cluster --name %"
    abbr "kidca"="kind delete clusters -A"
    abbr "kigk"="kind get kubeconfig"
    ```
