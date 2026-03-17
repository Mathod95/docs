---
title: CheatSheet
categories: Kubernetes
tags:
  - Kubernetes
  - CheatSheet
status: draft
---

Here’s a tip!

As you might have seen already, creating and editing YAML files is a bit difficult, especially in the CLI. During the exam, you might find it difficult to copy and paste YAML files from the browser to the terminal. Using the kubectl run command can help in generating a YAML template. And sometimes, you can even get away with just the kubectl run command without having to create a YAML file at all. For example, if you were asked to create a pod or deployment with a specific name and image, you can simply run the kubectl run command.

Use the below set of commands and try the previous practice tests again, but this time, try to use the below commands instead of YAML files. Try to use these as much as you can going forward in all exercises.

Reference (Bookmark this page for the exam. It will be very handy):

https://kubernetes.io/docs/reference/kubectl/conventions/

Create an NGINX Pod

kubectl run nginx --image=nginx
Generate POD Manifest YAML file (-o yaml). Don’t create it(–dry-run)

kubectl run nginx --image=nginx --dry-run=client -o yaml
Create a deployment

kubectl create deployment --image=nginx nginx
Generate Deployment YAML file (-o yaml). Don’t create it(–dry-run)

kubectl create deployment --image=nginx nginx --dry-run=client -o yaml
Generate Deployment YAML file (-o yaml). Don’t create it(–dry-run) and save it to a file.

kubectl create deployment --image=nginx nginx --dry-run=client -o yaml > nginx-deployment.yaml
Make necessary changes to the file (for example, adding more replicas) and then create the deployment.

kubectl create -f nginx-deployment.yaml
OR

In k8s version 1.19+, we can specify the –replicas option to create a deployment with 4 replicas.

kubectl create deployment --image=nginx nginx --replicas=4 --dry-run=client -o yaml > nginx-deployment.yaml





```bash title="Voir les labels du deployment knative-operator"
kubectl get deployment knative-operator -n knative-operator --show-labels
```

```bash title="Voir les labels du deployment operator-webhook"
kubectl get deployment operator-webhook -n knative-operator --show-labels
```

```bash title="Voir les deux en même temps avec leurs labels"
kubectl get deployments -n knative-operator --show-labels
```

```bash title="Plus de détails en format YAML pour voir tous les labels"
kubectl get deployment knative-operator -n knative-operator -o yaml | grep -A 5 "labels:"
kubectl get deployment operator-webhook -n knative-operator -o yaml | grep -A 5 "labels:"
```

```bash title="Format tableau avec les labels spécifiques"
kubectl get deployments -n knative-operator \
  -o custom-columns=NAME:.metadata.name,APP:.metadata.labels.app,ENV:.metadata.labels.environment
```

```bash title="Voir si les labels app et environment existent"
kubectl get deployments -n knative-operator -o json | jq '.items[].metadata.labels | {name: .name, app: .app, environment: .environment}'
```

```bash title="Version plus simple pour voir tous les labels"
kubectl get deployments -n knative-operator -o yaml | yq '.items[].metadata | {"name": .name, "labels": .labels}'
```