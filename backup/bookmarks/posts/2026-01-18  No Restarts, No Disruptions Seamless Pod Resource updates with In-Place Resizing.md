---
title: "No Restarts, No Disruptions: Seamless Pod Resource updates with In-Place Resizing"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://engineering.doit.com/no-restarts-no-disruptions-seamless-pod-resource-updates-with-in-place-resizing-f3cf41654216"
author:
  - "[[Chimbu Chinnadurai]]"
---
<!-- more -->

[Sitemap](https://engineering.doit.com/sitemap/sitemap.xml)## [DoiT](https://engineering.doit.com/?source=post_page---publication_nav-b5de5190d27c-f3cf41654216---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*zV9SljT9OM-LyXbc_f0Zng.jpeg)

Photo by Andrii Yalanskyi from Shutterstock

Optimizing resource utilization while maintaining application performance is a never-ending challenge in Kubernetes. Figuring out how much resources your app needs at the start is complex, and the traditional approach of resizing CPU and/or memory resources can be disruptive, requiring the recreating of pods and potentially impacting running workloads. This interruption can lead to service degradation, downtime, and operational headaches. This is where platforms like [PerfectScale](https://www.perfectscale.io/) can help by continuously analyzing resource usage across workloads and identifying optimal allocations before resorting to disruptive changes.

Many users have been eagerly anticipating the ability to resize Kubernetes pods without a restart, and the feature is available in Alpha from **Kubernetes v1.27** and graduated to **beta in** [**v1.33**](https://kubernetes.io/blog/2025/05/16/kubernetes-v1-33-in-place-pod-resize-beta/). The feature is called `InPlacePodVerticalScaling` and the `resources` field in a pod's containers now allows mutation for `cpu` and `memory` resources. They can be changed simply by patching the running pod spec.

Advantages of in-place pod resource resizing:

- **Reduced Downtime:** Eliminates the downtime and potential data loss caused by pod restart, ensuring smooth operations and uninterrupted service for your users.
- **Enhanced Efficiency:** Right-sizing your pods is crucial for optimal resource utilization. `InPlacePodVerticalScaling` lets you allocate resources precisely as needed, avoiding both overprovisioning (wasting money) and underprovisioning (hampering performance).
- **Improved Agility:** Dynamic scaling allows you to respond instantly to changing demands. Whether it's a sudden surge in traffic or a scheduled batch job, your pods can adjust their resource usage seamlessly, ensuring optimal performance and responsiveness.
- **Cost Savings:** By avoiding overprovisioning and optimizing resource usage, InPlacePodVerticalScaling translates directly to cost savings, especially in cloud environments where you pay per resource unit.
- **Simplified Management:** Managing complex deployments is challenging, but InPlacePodVerticalScaling streamlines the process by eliminating manual restarts and offering an innovative approach to resource management.

In this blog post, I will show you how to try in-place pod resource resizing. The feature is currently in Beta as of [kubernetes v1.33](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/#:~:text=%E2%80%93-,InPlacePodVerticalScaling,-false) and is not recommended for production. The Kubernetes community continues to focus on hardening the feature, improving performance, and ensuring it is robust for production environments.

## In-place pod resource resize in action

The `InPlacePodVerticalScaling` feature is enabled by default in clusters running version v1.33. You can explicitly activate this feature in a [minikube](https://minikube.sigs.k8s.io/docs/start/) cluster using the following command, or enable this feature gate in your managed Kubernetes cluster if it is not already enabled by default.

```hs
minikube start --feature-gates=InPlacePodVerticalScaling=true
```

Let's deploy a sample pod to the cluster, and the new `restartPolicy` in the pod spec gives control to users over how their containers are handled when resources are resized.

In the below sample pod configuration for memory resources, the `resizePolicy` indicates that changes to the memory allocation require a restart of the container, and for CPU resources a restart is not necessary during resizing.

The decision to restart a container depends on whether the application can use the updated resource without requiring a restart or not. For example, if an application's memory usage is critical to its operation, restarting the container when memory changes occur ensures that the application starts with the correct amount of memory. This step helps prevent potential issues or malfunctions.

```hs
cat <<EOF | kubectl apply -f -
---
apiVersion: v1
kind: Pod
metadata:
  labels:
    run: nginx
  name: nginx
spec:
  containers:
  - image: nginx
    name: nginx
    resizePolicy:
    - resourceName: "memory"
      restartPolicy: "RestartContainer"
    - resourceName: "cpu"
      restartPolicy: "NotRequired"
    resources:
      limits:
        cpu: "300m"
        memory: "1Gi"
      requests:
        cpu: "100m"
        memory: "500Mi"
EOF
```

Wait until the pod is moved to a running state and explore the pod configuration. A new field `allocatedResources` has been added to `containerStatuses` in the pod's status, and this field reflects the current node resources allocated to the pod's containers.

In addition, a new field called `resources` has been added to the container's status, and this field reflects the actual resource requests and limits configured on the running containers as reported by the container runtime.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*-08XSOl_4GObh1OgyB3zAQ.png)

### CPU resize

let's adjust the `CPU` resources of the pod with the following patch command and observe the resize operation. Modifying Pod resources must now be done via the Pod’s `resize` subresource, `kubectl` versions v1.32+ support this argument.

```hs
kubectl patch pod nginx --subresource resize --patch '{"spec": {"containers": [{"name":"nginx", "resources":{"requests": {"cpu" :"300m"},"limits": {"cpu" :"500m"}}}]}}'
```

The status of a resize operation is now exposed via two Pod conditions:

- `PodResizePending`: Indicates that Kubelet cannot grant the resize immediately (e.g., `reason: Deferred` if temporarily unable, `reason: Infeasible` if impossible on the node).
- `PodResizeInProgress`: Indicates the resize is accepted and being applied. Errors encountered during this phase are now reported in this condition's message with `reason: Error`
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ZwrJQP8l2XOU5-TXMz-uGA.png)

The community improved Kubelet’s Pod Lifecycle Event Generator (PLEG), enabling Kubelet to respond to and complete resizes more quickly in beta. However, occasionally resizing a pod may experience a race condition with other pod updates. This can cause a delay in the activation of the pod to resize, and the updated container resources may take some time to be reflected in the pod’s status.

### Memory resize

let's continue with the `Memory` resource adjustments, and the container will be restarted as per the `restartPolicy`.

```hs
kubectl patch pod nginx --subresource resize --patch '{"spec": {"containers": [{"name":"nginx", "resources":{"requests": {"memory" :"700Mi"}}}]}}'
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*BKexvhT-FyXjnWflcXSoCw.png)

The screenshot displays the successful completion of the resize operation and container restart 🚀.

## Conclusion

While this feature is still maturing, platforms like [PerfectScale](https://www.perfectscale.io/) already deliver production-grade optimization workflows — combining safety, performance, and cost-efficiency into automated resource management. Follow the steps outlined in this blog post to try it out and experience its benefits firsthand.

I hope this blog post has been helpful. For more information, please refer to the following resources:

- [KEP-1287: In-place Update of Pod Resources](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/1287-in-place-update-pod-resources)
- [Kubernetes 1.27: In-place Resource Resize for Kubernetes Pods](https://kubernetes.io/blog/2023/05/12/in-place-pod-resize-alpha/)
- [Kubernetes v1.33: In-Place Pod Resize Graduated to Beta](https://kubernetes.io/blog/2025/05/16/kubernetes-v1-33-in-place-pod-resize-beta/)
- [Resize CPU and Memory Resources assigned to Containers](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/)

## More from Chimbu Chinnadurai and DoiT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--f3cf41654216---------------------------------------)