---
title: Deployments
status: draft
sources:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/Core-Concepts/Deployments/page
  - https://notes.kodekloud.com/docs/kubernetes-for-the-absolute-beginners-hands-on-tutorial/Kubernetes-Concepts-Pods-ReplicaSets-Deployments/Deployments/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/cka-certification-course-certified-kubernetes-administrator/module/c6d2ac7d-8192-4cff-aa54-e36d888c5bd9/lesson/5f6448e3-51e0-41c1-8abb-865cbdbc611d
---

> This guide explores Kubernetes deployments, simplifying application management with features like rolling updates, rollbacks, and high availability.

Hello and welcome! My name is Mumshad Mannambeth. In this guide, we dive into Kubernetes deployments—an abstraction that simplifies managing your applications in a production environment. Rather than interacting directly with pods and ReplicaSets, deployments offer advanced features that enable you to:

- Deploy multiple instances of your application (like a web server) to ensure high availability and load balancing.
- Seamlessly perform rolling updates for Docker images so that instances update gradually, reducing downtime.
- Quickly roll back to a previous version if an upgrade fails unexpectedly.
- Pause and resume deployments, allowing you to implement coordinated changes such as scaling, version updates, or resource modifications.

Previously, we discussed how individual pods encapsulate containers and how ReplicaSets maintain multiple pod copies. A deployment, however, sits at a higher level, automatically managing ReplicaSets and pods while providing enhanced features like rolling updates and rollbacks.

## Creating a Deployment

To create a deployment, start by writing a deployment definition file. This file is similar to a ReplicaSet definition, with the key difference being that the kind is set to Deployment instead of ReplicaSet. Below is an example of a correct deployment definition file:

```yaml linenums="1" title="deployment.yaml"
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: app01-replicaset
  labels:
    app: app01
    type: front-end
spec:
  replicas: 3
  selector:
    matchLabels:
      type: front-end
  template:
    metadata:
      labels:
        app: app01-rs
        type: front-end
    spec:
      containers:
      - name: podinfo-container
        image: ghcr.io/stefanprodan/podinfo:latest
```

Once your deployment definition file (for example, named deployment-definition.yml) is ready, create the deployment with the following command:

```bash
kubectl create -f deployment-definition.yml
```

The command output should confirm that the deployment has been created:

```console
deployment "myapp-deployment" created
```

To verify the deployment, run:

```bash
kubectl get deployments
```

The output will look similar to this:

```console
NAME                DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
myapp-deployment    3         3         3            3           21s
```

## Behind the Scenes: How Deployments Work

When you create a deployment, Kubernetes automatically creates an associated ReplicaSet. To see this in action, run:

```bash
kubectl get replicasets
```

You'll notice a new ReplicaSet with a name derived from your deployment. This ReplicaSet oversees the creation and management of pods. To view the pods managed by the ReplicaSet, run:

```bash
kubectl get pods
```

While deployments and ReplicaSets work together seamlessly, deployments provide additional functionalities such as rolling updates, rollbacks, and the ability to pause/resume changes.

<Callout icon="lightbulb" color="#1CB2FE">
  To view all the created Kubernetes objects—deployments, ReplicaSets, pods, and more—use the following command:

  ```bash
  kubectl get all
  ```

  This gives you a comprehensive overview of your deployment's components.
</Callout>

A sample output of the "kubectl get all" command might be:

```console
NAME                            DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deploy/myapp-deployment         3         3         3            3           9h

NAME                                        DESIRED   CURRENT   READY   AGE
rs/myapp-deployment-6795844b58              3         3         3       9h

NAME                                      READY   STATUS    RESTARTS   AGE
po/myapp-deployment-6795844b58-5rbjl        1/1     Running   0          9h
po/myapp-deployment-6795844b58-h4w55         1/1     Running   0          9h
po/myapp-deployment-6795844b58-1fjhv         1/1     Running   0          9h
```

In this output, you can clearly see the deployment, its associated ReplicaSet, and the managed pods.

## Conclusion

This article has covered the fundamentals of creating a deployment in Kubernetes. By leveraging deployments, you gain powerful capabilities like rolling updates and rollbacks that make managing application updates and maintenance in production more efficient. Whether you are scaling your application or rolling out new features, Kubernetes deployments provide a robust solution for modern application management.


---
---

> This article provides a comprehensive guide on Kubernetes Deployments, focusing on simplifying application rollouts and ensuring seamless updates with zero downtime.

Welcome to this comprehensive guide on Kubernetes Deployments. In this article, we explore how Deployments simplify the rollout of production applications and ensure seamless updates with zero downtime.

Imagine having a web server that needs to run reliably in production. You require multiple instances of this web server to handle load distribution and high availability. Moreover, when a new version of the application is available on the Docker registry, you want to upgrade your instances one by one—a process known as a rolling update—to minimize user disruption. In case an update introduces an error, a quick rollback mechanism is essential. Additionally, you might need to modify various aspects of your environment, such as the web server version, deployment scaling, or resource allocations, and apply these changes simultaneously after a planned pause.

While individual Pods run your application instances, ReplicaSets (or Replication Controllers) manage these Pods, ensuring the correct number are always running. A Deployment builds on these components by offering a higher-level abstraction. It not only handles rolling updates and rollbacks but also lets you pause and resume deployments as needed.

<Frame>
  ![The image shows a cloud with Python icons labeled v1 and v2, connected to multiple Python icons below, indicating version deployment or distribution.](https://kodekloud.com/kk-media/image/upload/v1752884860/notes-assets/images/Kubernetes-for-the-Absolute-Beginners-Hands-on-Tutorial-Deployments/frame_50.jpg)
</Frame>

The diagram above demonstrates a scenario where you deploy and upgrade versions of your web application incrementally, ensuring continuous availability.

<Frame>
  ![The image illustrates a Kubernetes deployment with a replica set containing multiple pods, each running a Python application, and versioning indicated in a cloud icon.](https://kodekloud.com/kk-media/image/upload/v1752884861/notes-assets/images/Kubernetes-for-the-Absolute-Beginners-Hands-on-Tutorial-Deployments/frame_130.jpg)
</Frame>

This second diagram details how a Deployment coordinates with a ReplicaSet, which in turn creates and maintains multiple application Pods. The Deployment sits at the top of this hierarchy, enabling advanced management features such as rolling updates, rollbacks, and dynamic pausing/resuming of deployments.

## Creating a Kubernetes Deployment

To create a Deployment, you first define a deployment configuration file. This file's structure is similar to that of a ReplicaSet, with the key difference being that the `kind` is set to "Deployment". Below is an example of a Deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
  labels:
    app: myapp
    type: front-end
spec:
  replicas: 3
  selector:
    matchLabels:
      type: front-end
  template:
    metadata:
      name: myapp-pod
      labels:
        app: myapp
        type: front-end
    spec:
      containers:
      - name: nginx-container
        image: nginx
```

In this configuration:

* The `apiVersion` is set to `apps/v1`.
* The `kind` is "Deployment".
* The metadata section provides the name and relevant labels.
* The `spec` section defines the desired state, including the number of replicas, the pod selector, and the pod template which details metadata and container specifications.

Once you have your deployment definition file (e.g., `deployment-definition.yml`), create the Deployment with the following command:

```bash
kubectl create -f deployment-definition.yml
```

### Verifying the Deployment

After creation, verify the Deployment, ReplicaSet, and Pods using these commands:

1. **Check Deployments:**

   ```bash
   kubectl get deployments
   ```

   Example output:

   ```text
   NAME                DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
   myapp-deployment    3         3         3            3           21s
   ```

2. **View the ReplicaSet:**

   ```bash
   kubectl get replicaset
   ```

   Example output:

   ```text
   NAME                             DESIRED   CURRENT   READY   AGE
   myapp-deployment-6795844b58     3         3         3       2m
   ```

3. **Examine the Pods:**

   ```bash
   kubectl get pods
   ```

   Example output:

   ```text
   NAME                                         READY   STATUS    RESTARTS   AGE
   myapp-deployment-6795844b58-5rbj1            1/1     Running   0          2m
   myapp-deployment-6795844b58-h4w5t             1/1     Running   0          2m
   myapp-deployment-6795844b58-1fjhv             1/1     Running   0          2m
   ```

<Callout icon="lightbulb" color="#1CB2FE">
  The Deployment automates the creation of a ReplicaSet, which manages your Pods. This layering ensures that updates are rolled out in a controlled and managed manner.
</Callout>

## Viewing All Created Objects

To see all Kubernetes objects associated with your Deployment at once, run:

```bash
kubectl get all
```

Example output:

```text
NAME                                    DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deploy/myapp-deployment                 3         3         3            3           9h
NAME                                    DESIRED   CURRENT   READY   AGE
rs/myapp-deployment-6795844b58         3         3         3       9h
NAME                                    READY   STATUS    RESTARTS   AGE
po/myapp-deployment-6795844b58-5rbjl   1/1     Running   0          9h
po/myapp-deployment-6795844b58-h4w55    1/1     Running   0          9h
po/myapp-deployment-6795844b58-1fjhv    1/1     Running   0          9h
```

This comprehensive view confirms that your Deployment has successfully created all associated resources—Deployment, ReplicaSet, and Pods.

<Callout icon="lightbulb" color="#1CB2FE">
  In the upcoming sections, we will dive deeper into advanced features like rolling updates, rollbacks, and pausing/resuming deployments. Stay tuned to master these powerful deployment mechanisms.
</Callout>

That concludes our guide on Kubernetes Deployments. Happy deploying!

For more insights and in-depth tutorials, explore the following resources:

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes Basics](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)
- [Docker Hub](https://hub.docker.com/)