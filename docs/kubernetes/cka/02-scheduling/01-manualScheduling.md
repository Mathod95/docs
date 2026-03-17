---
title: Manual Scheduling
status: draft
sources:
  - https://notes.kodekloud.com/docs/Certified-Kubernetes-Administrator-CKA/Scheduling/Manual-Scheduling/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/cka-certification-course-certified-kubernetes-administrator/module/cd124bdf-9911-4cc1-8177-f2d8b6dfd2a0/lesson/5e3dfca7-9f2f-41ea-bc35-0be1e71da107
---

> This guide explains how to assign pods to nodes without relying on Kubernetes’ built-in scheduler for tighter control over pod placement.

Welcome to this lesson on manually scheduling pods in Kubernetes. This guide explains how to assign pods to nodes without relying on Kubernetes’ built-in scheduler. Manual scheduling can be useful in niche scenarios where you need tighter control over pod placement. In this article, we review a basic pod manifest, demonstrate how manual scheduling works, and show you how to use binding objects to reassign pods if necessary.

## Understanding the Default Scheduler Behavior

Every pod definition includes a field called `nodeName`, which is left unset by default. The Kubernetes scheduler automatically scans for pods without a `nodeName` and selects an appropriate node by updating this field and creating a binding object. Consider the basic pod manifest below:

```yaml linenums="1" title="pod.yaml"
apiVersion: v1
kind: Pod
metadata:
  name: podinfo
  labels:
    name: podinfo
spec:
  containers:
  - name: podinfo
    image: ghcr.io/stefanprodan/podinfo:latest
    ports:
    - containerPort: 9898
```

Typically, you do not include the `nodeName` field in your manifest. The scheduler uses this field only after selecting a node for the pod.

## Manually Setting the Node Name

To manually assign a pod to a specific node during creation, populate the `nodeName` field in the manifest. For example, to schedule the pod on a node called "node02", update your manifest as follows:

```yaml linenums="1" title="pod.yaml" hl_lines="8"
apiVersion: v1
kind: Pod
metadata:
  name: podinfo
  labels:
    name: podinfo
spec:
  nodeName: kind-worker2
  containers:
  - name: podinfo
    image: ghcr.io/stefanprodan/podinfo:latest
    ports:
    - containerPort: 9898
```

After creating the pod with this manifest, check its status with:

```bash
kubectl get pods -A --field-selector spec.nodeName=kind-worker2 -l name=podinfo
NAMESPACE   NAME      READY   STATUS    RESTARTS   AGE
default     podinfo   1/1     Running   0          4m59s
```

!!! info
    The `nodeName` must be set during pod creation. Once the pod is running, Kubernetes does not permit modifications to the `nodeName` field.

<!--
## Reassigning a Running Pod Using a Binding Object

If a pod is already running and you need to change its node assignment, you cannot modify its `nodeName` directly. In this scenario, you can create a binding object that mimics the scheduler’s behavior.

1. Create a binding object that specifies the target node ("node02"):

   ```yaml linenums="1" title="binding.yaml"
    apiVersion: v1
    kind: Binding
    metadata:
      name: podinfo
    target:
      apiVersion: v1
      kind: Node
      name: kind-worker2
   ```

2. The original pod definition remains unchanged:

   ```yaml linenums="1" title="pod.yaml"
    apiVersion: v1
    kind: Pod
    metadata:
      name: podinfo
      labels:
        name: podinfo
    spec:
      containers:
      - name: podinfo
        image: ghcr.io/stefanprodan/podinfo:latest
        ports:
        - containerPort: 9898
   ```

3. Convert the YAML binding to JSON (e.g., save it as `binding.json`) and send a POST request to the pod’s binding API using curl:

   ```bash
   curl --header "Content-Type: application/json" --request POST --data @binding.json http://$SERVER/api/v1/namespaces/default/pods/nginx/binding
   ```

This binding instructs Kubernetes to assign the existing pod to the specified node without altering its original manifest.

## Quick Reference Table

| Method                 | Use Case                           | Example Snippet Reference            |
| ---------------------- | ---------------------------------- | ------------------------------------ |
| Direct Assignment      | Set `nodeName` during pod creation | See manifest with `nodeName: node02` |
| Using a Binding Object | Reassign a running pod             | See binding object example           |

-->

## Additional Resources

* [Kubernetes Basics](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)
* [Kubernetes Documentation](https://kubernetes.io/docs/)