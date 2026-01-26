---
title: 101 Argo Workflows
date: 2026-01-04
categories:
  - Argo Workflows
tags:
  - Argo Workflows
  - 101
---

![](../../assets/images/argo/argo.svg)

## Introduction

<!-- more -->

```bash hl_lines="1-2"
kubectl create namespace argo
kubectl apply -n argo -f "https://github.com/argoproj/argo-workflows/releases/download/v3.7.6/install.yaml"
```

```bash hl_lines="1"
kubectl -n argo get all
NAME                                      READY   STATUS    RESTARTS   AGE
pod/argo-server-c4c544bdc-8cn2n           1/1     Running   0          3h42m
pod/httpbin-f5ccc9c6-xfj7q                1/1     Running   0          3h42m
pod/minio-5877d79784-tx2g2                1/1     Running   0          3h42m
pod/workflow-controller-cf96fc675-lkcgn   1/1     Running   0          3h42m

NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
service/argo-server   ClusterIP   10.96.43.154   <none>        2746/TCP            3h42m
service/httpbin       ClusterIP   10.96.249.74   <none>        9100/TCP            3h42m
service/minio         ClusterIP   10.96.53.221   <none>        9000/TCP,9001/TCP   3h42m

NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/argo-server           1/1     1            1           3h42m
deployment.apps/httpbin               1/1     1            1           3h42m
deployment.apps/minio                 1/1     1            1           3h42m
deployment.apps/workflow-controller   1/1     1            1           3h42m

NAME                                            DESIRED   CURRENT   READY   AGE
replicaset.apps/argo-server-c4c544bdc           1         1         1       3h42m
replicaset.apps/httpbin-f5ccc9c6                1         1         1       3h42m
replicaset.apps/minio-5877d79784                1         1         1       3h42m
replicaset.apps/workflow-controller-cf96fc675   1         1         1       3h42m
```

```bash hl_lines="1"
kubectl patch deployment argo-server -n argo --type='json' -p '[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": ["server", "--auth-mode=server"]}]'
```

```bash hl_lines="1"
kubectl -n argo port-forward service/argo-server 2746:2746
```

!!! Tip "WORKFLOW EXAMPLE"

    ```bash hl_lines="1"
    argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/main/examples/hello-world.yaml
    ```

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-
      labels:
        workflows.argoproj.io/archive-strategy: "false"
      annotations:
        workflows.argoproj.io/description: |
          This is a simple hello world example.
    spec:
      entrypoint: hello-world
      templates:
      - name: hello-world
        container:
          image: busybox
          command: [echo]
          args: ["hello world"]
    ```

    ---
    
    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: cowsay-
    spec:
      entrypoint: cowsay-template
      templates:
      - name: cowsay-template
        container:
          image: rancher/cowsay
          command: [cowsay]
          args: ["Argo Workflow"]
    ```


Edit the cowsay-workflow.yaml to have the following:

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: cowsay-
  namespace: argo
spec:
  entrypoint: cowsay
  arguments:
    parameters:
    - name: message
      value: "a message from the workflow arguments section"
  templates:
  - name: cowsay
    inputs:
      parameters:
      - name: message
    container:
      image: rancher/cowsay
      command: ["cowsay"]
      args: ["{{inputs.parameters.message}}"]
Submit and watch the workflow:

argo submit cowsay-workflow.yml -n argo --watch
Verify logs contain the workflow argument content using the following command:

argo -n argo logs @latest

Submit the workflow with a parameter override and monitor its progress using the following command:

argo submit -n argo cowsay-workflow.yml --watch -p message="With great power comes great responsibility"
After submission, verify that the latest logs display the overridden value by executing:

argo -n argo logs @latest

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: cosmic-moo-
spec:
  entrypoint: triple-moo
  templates:
  - name: triple-moo
    steps:
    - - name: first-moo
        template: cow-says
        arguments:
          parameters:
          - name: message
            value: "Welcome to the Cosmic Ranch!"
    - - name: parallel-moo-a
        template: cow-says
        arguments:
          parameters:
          - name: message
            value: "Greetings from Galaxy Moo!"
      - name: parallel-moo-b
        template: cow-says
        arguments:
          parameters:
          - name: message
            value: "Hello from the Milky Whey!"

  - name: cow-says
    inputs:
      parameters:
      - name: message
    container:
      image: rancher/cowsay
      command: ["cowsay"]
      args: ["{{inputs.parameters.message}}"]

argo -n argo get @latest

## PARAMETERS

??? TIP "GOTASK"
    ```yaml
    version: '3'

    set: [errexit, pipefail]

    # VARIABLES ########################################################################################

    # INCLUDES #########################################################################################

    includes:

    # MAIN #############################################################################################

    tasks:
      default:
        desc: ""
        summary: ""
        aliases: [setup, init]
        cmds:
          - task: argo-workflows:main
      
      argo-workflows:main:
        desc: ""
        summary: ""
        cmds:
          - echo ""
          - task: required:main
    ```


https://argo-workflows.readthedocs.io/en/latest/