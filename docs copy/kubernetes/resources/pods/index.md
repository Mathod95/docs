---
title: Pods
categories: Kubernetes
tags:
  - Kubernetes
status:
sources:
  - Pods: https://thekubeguy.com/understanding-pods-a9e6d4b6e1c8
---

# Pods

These pods are like the tiny, essential building blocks that make the magic of container orchestration happen. If you’re new to Kubernetes or just curious, join us as we explore the significance of pods and how they seamlessly group containers in a way that makes managing applications feel like a breeze.

## What exactly is a pod?

At its core, a Kubernetes pod is like a cosy, shared flat for your containers. Think of it as a little universe where your containers live together. Now, why would you want containers to share space? Well, here’s the magic: Containers in the same pod can communicate with each other easily, almost like they’re in the same room having a conversation.

In simpler terms, a pod is the smallest, most fundamental unit in Kubernetes. It’s the tiniest deployable package that can hold one or more containers. But why group containers together? Let’s find out!

## Why Pods Group Containers

1\. Buddies Stick Together: Imagine you’re moving into a new city and need a roommate to share expenses. In the Kubernetes world, containers are like your roommates, and pods are the flats you all share. When containers live together in a pod, they can chat and work together smoothly because they share the same network and storage space.

2\. Collaboration Made Easy: Sometimes, applications require multiple containers to work together, like a chef and a waiter teaming up to serve delicious meals. Pods make this collaboration a breeze. Containers within the same pod can share data and resources effortlessly.

3\. Isolation when Needed: Pods also offer a level of isolation. You can have containers in one pod that don’t need to interact with containers in another pod. This separation helps keep things tidy and organized.

## Things inside a pod

Now, picture a pod as a little box that can hold one or more containers. These containers inside the pod share certain things:

1\. Network: Containers in a pod share the same IP address and port space. This means they can talk to each other using “localhost,” just like you can chat with your roommate across the room.

2\. Storage: Pods can also share storage resources. So, if one container in a pod needs access to a file, another container in the same pod can provide it. They can share storage, like sharing a bookshelf.

## Need for Multiple Containers in a Pod?

Good question! Here are some scenarios when you might want multiple containers in a pod:

1\. Sidecar Containers: Imagine a delivery truck that not only carries packages but also has a GPS tracker. In a pod, you might have your main application container (the delivery truck) and a sidecar container (the GPS tracker) that helps with tasks like logging or monitoring.

2\. Helper Containers: Sometimes, you require a little helper. In a pod, you can have your main container doing the heavy lifting and another container that helps with tasks like setting up configurations.

## Conclusion

In the enchanting world of Kubernetes, pods are the heartbeat of containerization. They bring containers together, fostering collaboration and communication while ensuring isolation when required. Think of pods as the cosy flats where your containers reside, working in harmony to deliver your applications flawlessly.

So, the next time you see a pod in Kubernetes, remember that it’s like a tiny ecosystem, where containers are neighbours sharing resources and making your applications run like a well-orchestrated symphony.

---

Welcome to this in-depth guide on Kubernetes Pods. In this article, we assume your application is already developed, built into Docker images, and hosted on a Docker repository (such as Docker Hub). We also assume that your Kubernetes cluster is configured and operational—whether it is a single-node or multi-node cluster. With Kubernetes, the goal is to run containers on worker nodes, but rather than deploying containers directly, Kubernetes encapsulates them within an object called a pod. A pod represents a single instance of an application and is the smallest deployable unit in Kubernetes.

In the simplest scenario, a single-node Kubernetes cluster may run one instance of your application inside a Docker container encapsulated by a pod.

When user load increases, you can scale your application by spinning up additional instances—each running in its own pod. This approach isolates each instance, allowing Kubernetes to distribute the pods across available nodes as needed.

The image illustrates a Kubernetes cluster with a pod containing a Python application, showing user interaction and node structure.

Instead of adding more containers to the same pod, additional pods are created. For instance, running two instances in separate pods allows the load to be shared across the node or even across multiple nodes if the demand escalates and additional cluster capacity is required.

The image illustrates a Kubernetes cluster with multiple nodes, each containing pods running Python applications, and one pod marked with an error.

!!! Note "Scaling Pods"
    Remember, scaling an application in Kubernetes involves increasing or decreasing the number of pods, not the number of containers within a single pod.

Typically, each pod hosts a single container running your main application. However, a pod can also contain multiple containers, which are usually complementary rather than redundant. For example, you might include a helper container alongside your main application container to support tasks like data processing or file uploads. Both containers in the pod share the same network namespace (allowing direct communication via localhost), storage volumes, and lifecycle events, ensuring they start and stop together.

The image illustrates a Kubernetes multi-container pod setup, showing two containers within a pod on a node, labeled as "Helper Containers."

To better understand the concept, consider a basic Docker example. Suppose you initially deploy your application with a simple command:

docker run python-app
When the load increases, you may launch additional instances manually:

docker run python-app
docker run python-app
docker run python-app
docker run python-app
Now, if your application needs a helper container that communicates with each instance, managing links, custom networks, and shared volumes manually becomes complex. You’d have to run commands like:

docker run helper --link app1
docker run helper --link app2
docker run helper --link app3
docker run helper --link app4
With Kubernetes pods, these challenges are resolved automatically. When a pod is defined with multiple containers, they share storage, the network namespace, and lifecycle events—ensuring seamless coordination and simplifying management.

Even if your current application design uses one container per pod, Kubernetes enforces the pod abstraction. This design prepares your application for future scaling and architectural changes, even though multi-container pods remain less common. This article primarily focuses on single-container pods for clarity.

## Deploying Pods
A common method to deploy pods is using the kubectl run command. For example, the following command creates a pod that deploys an instance of the nginx Docker image, pulling it from a Docker repository:

```bash hl_lines="1"
kubectl run nginx --image nginx
```
Once deployed, you can verify the pod's status with the kubectl get pods command. Initially, the pod might be in a "ContainerCreating" state, followed by a transition to the "Running" state as the application container becomes active. Below is an example session:

```bash hl_lines="1"
kubectl get pods
NAME                   READY   STATUS    RESTARTS   AGE
nginx-8586cf59-whssr   1/1     Running   0          8s
```

At this stage, note that external access to the nginx web server has not been configured. The service is accessible only within the node. In a future article, we will explore configuring external access through Kubernetes networking and services.

---

Pods with YAML
Welcome to this lesson on creating a Pod in Kubernetes using a YAML configuration file. In this guide, you'll learn how to structure your YAML file, create the Pod with kubectl, and verify its status. Kubernetes leverages YAML files to define objects such as Pods, ReplicaSets, Deployments, and Services. These definitions adhere to a consistent structure, with four essential top-level properties: apiVersion, kind, metadata, and spec.

## Top-Level Fields in a Kubernetes YAML File
Every Kubernetes definition file must include the following four fields:

```yaml linenums="1"
apiVersion:
kind:
metadata:
spec:
```

  - **apiVersion:** This field indicates the version of the Kubernetes API you are using. For a Pod, set apiVersion: v1. Depending on the object you define, you might need different versions such as apps/v1, extensions/v1beta1, etc.
  - **kind:** This specifies the type of object being created. In this lesson, since we're creating a Pod, you'll define it as kind: Pod. Other objects might include ReplicaSet, Deployment, or Service.
  - **metadata:** The metadata section provides details about the object, including its name and labels. It is represented as a dictionary. It is essential to maintain consistent indentation for sibling keys to ensure proper YAML nesting. For example:

apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
Indentation Reminder

Make sure that the properties under metadata (like name and labels) are indented to the same level. This is crucial for correct YAML parsing.

**spec:**
The spec section provides specific configuration details for the object. For a Pod, this is where you define its containers. Since a Pod can run multiple containers, the containers field is an array. In our example, with a single container, the array has just one item. The dash (-) indicates a list item, and each container must be defined with at least name and image keys.

Below is the complete YAML configuration for our Pod:

```yaml linenums="1"
apiVersion: v1
kind: Pod
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

Creating and Verifying the Pod
After you have saved your configuration (for example, as pod-definition.yaml), use the following command to create the Pod:

kubectl create -f pod-definition.yaml
Once the Pod is created, you can verify its status by listing all Pods:

kubectl get pods
You should see output similar to this:

NAME         READY   STATUS    RESTARTS   AGE
myapp-pod    1/1     Running   0          20s
To view detailed information about the Pod, run:

kubectl describe pod myapp-pod
This command provides extensive details, including metadata, node assignment, container specifics, and event history such as scheduling, volume mounting, and container start-up. Here is an example output:

Name:         myapp-pod
Namespace:    default
Node:         minikube/192.168.99.100
Start Time:   Sat, 03 Mar 2018 14:26:14 +0800
Labels:       app=myapp
Annotations:  <none>
Status:       Running
IP:           172.17.0.24
Containers:
  nginx:
    Container ID:   docker://830bb56c8c42a860b4b70e9c1488faelbc38663e49186bc2f5a78e7688b8c9d
    Image:          nginx
    Image ID:       docker-pullable://nginx@sha256:4771d09578c7ca65299e110b3ee1c0a2592f5ea2618d32e4ffe7a4cab1c5de
    Port:           <none>
    State:          Running
      Started:      Sat, 03 Mar 2018 14:26:21 +0800
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-x95w7 (ro)


Conditions:
  Type              Status
  Initialized       True
  Ready             True
  PodScheduled      True


Events:
  Type    Reason                 Age   From               Message
  ----    ------                 ----  ----               -------
  Normal  Scheduled              27s   default-scheduler  Successfully assigned myapp-pod to minikube
  Normal  SuccessfulMountVolume  27s   minikube           MountVolume.SetUp succeeded for volume "default-token-x95w7"
  Normal  Pulling                27s   minikube           pulling image "nginx"
  Normal  Pulled                 27s   minikube           Successfully pulled image "nginx"
  Normal  Created                27s   minikube           Created container
  Normal  Started                27s   minikube           Started container
Tip

Using kubectl describe helps you gain detailed insights into the internal state of your Pod, which can be invaluable for troubleshooting.

Conclusion
In this lesson, you learned how to structure a Kubernetes YAML file for a Pod, create it using kubectl, and verify its status. This hands-on approach equips you to manage and troubleshoot your Kubernetes resources effectively. Happy Kubernetes-ing!

For more information, refer to the following resources:

---

Demo Pods with YAML
In this lesson, we will create a Kubernetes Pod using a YAML definition file instead of the "kubectl run" command. This method offers more control by allowing you to define pod specifications explicitly in a file. You can choose any text editor for this task; for instance, Windows users may prefer Notepad++ over Notepad, while Linux users might opt for vim. In future sections, we will explore additional IDEs and tools to streamline YAML editing, but we will stick with the basics for now.

Step 1: Creating the YAML File
Open your terminal and use vim to create a file named pod.yaml:

vim pod.yaml
Inside the file, define the following key elements:

apiVersion: Should be set to v1 for a Pod.
kind: Must be Pod (case-sensitive).
metadata: A dictionary that includes the pod's name and any labels used for grouping.
spec: Contains the pod specifications, including a list of containers.
Note

Be sure to follow proper indentation rules. Use two spaces per level (avoid tabs), as misalignment can lead to errors.

Below is a complete example configuration for a single-container Pod using the nginx image:

apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: nginx
    tier: frontend
spec:
  containers:
    - name: nginx
      image: nginx
Tip

To add additional containers, insert another block within the containers list with the appropriate name and image.

Step 2: Saving and Verifying the YAML File
After editing the file, exit vim and save your changes by typing:

:wq
Verify the contents of your YAML file with:

cat pod.yaml
The output should match the YAML configuration shown above.

Step 3: Creating the Pod in the Cluster
Create the Pod on your Kubernetes cluster using your YAML file. You can use either the kubectl create or kubectl apply command. Here’s an example with kubectl apply:

kubectl apply -f pod.yaml
# Output:
# pod/nginx created
To check the status of your Pod, run:

kubectl get pods
Initially, you might see an output similar to this:

NAME    READY   STATUS              RESTARTS   AGE
nginx   0/1     ContainerCreating   0          7s
After a short while, re-running the command should show the Pod in a running state:

kubectl get pods
Example output:

NAME    READY   STATUS    RESTARTS   AGE
nginx   1/1     Running   0          9s
Step 4: Inspecting the Pod Details
For a detailed overview of your Pod, use the kubectl describe command:

kubectl describe pod nginx
This command provides comprehensive details about the Pod, including container statuses, event logs, volumes, and node assignments. Below is an example of typical output:

Initialized              True
Ready                    True
ContainersReady          True
PodScheduled             True
Volumes:
  default-token-f5ntk:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-f5ntk
    Optional:    false
QoS Class:   BestEffort
Node-Selectors: <none>
Tolerations: node.kubernetes.io/not-ready:NoExecute for 300s
             node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type     Reason        Age   From                Message
  ----     ------        ----  ----                -------
  Normal   Scheduled     21s   default-scheduler   Successfully assigned default/nginx to minikube
  Normal   Pulling       20s   kubelet, minikube   Pulling image "nginx"
  Normal   Pulled        14s   kubelet, minikube   Successfully pulled image "nginx"
  Normal   Created       14s   kubelet, minikube   Created container nginx
  Normal   Started       14s   kubelet, minikube   Started container nginx
Conclusion
This demonstration has guided you through creating a Kubernetes Pod using a YAML configuration file. This approach not only reinforces good configuration practices but also provides enhanced flexibility compared to command-based object creation. In our next lesson, we will cover advanced IDEs and tools to further ease YAML file management.

---