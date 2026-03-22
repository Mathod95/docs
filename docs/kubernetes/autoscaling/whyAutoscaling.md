---
title: Why Do We Need to Autoscale
status: draft
sources:
  - https://notes.kodekloud.com/docs/Kubernetes-Autoscaling/Manual-Scaling/Why-Do-We-Need-to-Autoscale/page
sourcesVideos:
  - https://learn.kodekloud.com/user/courses/kubernetes-autoscaling/module/66710f67-c094-4a4c-b718-4a031d1ddebe/lesson/e57460fa-c121-4d31-b5a2-1d54caee9b49
--- 

> This article explains the importance of autoscaling in Kubernetes to manage resources dynamically during traffic spikes.

When your application experiences an unexpected spike in traffic, manual intervention often comes too late. Autoscaling dynamically adjusts compute resources—whether nodes or Pods—to match demand, ensuring seamless performance and preventing costly downtime.

## Benefits of Autoscaling

1. **Cost Savings:**
   Autoscaling prevents overprovisioning by scaling down idle resources, reducing your cloud spend.
2. **Improved Availability:**
   Automatically adds capacity during peak traffic—perfect for flash sales or feature launches.
3. **Efficient Resource Utilization:**
   Matches compute to workload, avoiding crashes from insufficient capacity and idle infrastructure.
4. **True Elasticity:**
   Adapts to unpredictable workloads without manual effort, a hallmark of cloud-native design.
5. **Fault Tolerance & Recovery:**
   Distributes load and replaces unhealthy resources to maintain resilience.
6. **Simplified Operations:**
   Frees your team from firefighting infrastructure so they can focus on building features.

---

## Autoscaling Components in Kubernetes

Kubernetes offers two primary autoscaling layers:

- **Cluster Scaling** adjusts the number of worker nodes (VMs).
- **Pod Scaling** modifies the replica count or resource requests of your applications.

<Frame>
  ![The image is a diagram illustrating "Scaling in Kubernetes," showing two main types: Cluster Scaling (worker node scaling) and Pod Scaling (pod, deployment, and statefulset scaling).](https://kodekloud.com/kk-media/image/upload/v1752880234/notes-assets/images/Kubernetes-Autoscaling-Why-Do-We-Need-to-Autoscale/scaling-in-kubernetes-diagram.jpg)
</Frame>

***

## Cluster Scaling

Cluster scaling manages your node pool size to ensure there’s enough CPU, memory, disk, or GPU capacity for all Pods. Kubernetes’ **Cluster Autoscaler** inspects pending Pods and resource requests, then adds or removes VMs accordingly.

```bash
# Example: Deploy Cluster Autoscaler on your cluster
kubectl apply -f https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/deploy/cluster-autoscaler.yaml
```

<Callout icon="lightbulb" color="#1CB2FE">
  Make sure your cloud provider permissions (IAM roles) are configured so the autoscaler can spin up or tear down nodes.
</Callout>

<Frame>
  ![The image illustrates a Kubernetes cluster with multiple worker nodes and a cluster autoscaler.](https://kodekloud.com/kk-media/image/upload/v1752880236/notes-assets/images/Kubernetes-Autoscaling-Why-Do-We-Need-to-Autoscale/kubernetes-cluster-worker-nodes-autoscaler.jpg)
</Frame>

***

## Core Autoscaling Tools

| Autoscaler                | Purpose                                    | Documentation     |
| ------------------------- | ------------------------------------------ | ----------------- |
| Cluster Autoscaler (CA)   | Scale VMs based on pending Pods            | [GitHub][ca]      |
| Horizontal Pod Autoscaler | Scale Pod replicas by CPU/memory           | [Kubernetes][hpa] |
| Vertical Pod Autoscaler   | Adjust Pod resource requests/limits        | [Kubernetes][vpa] |
| KEDA                      | Event-driven scaling from external sources | [KEDA][keda]      |

[ca]: https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler

[hpa]: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/

[vpa]: https://kubernetes.io/docs/tasks/run-application/vertical-pod-autoscaling/

[keda]: https://keda.sh/

***

## Pod Scaling vs. Cluster Scaling

| Aspect          | Cluster Scaling              | Pod Scaling                            |
| --------------- | ---------------------------- | -------------------------------------- |
| What it adjusts | Number of worker nodes (VMs) | Number of Pods or resource settings    |
| Primary impact  | Infrastructure capacity      | Application concurrency and throughput |
| Key benefits    | Ensures node-level resources | Ensures right replica count & sizing   |

<Frame>
  ![The image compares "Cluster Scaling" and "Pod Scaling" strategies, highlighting aspects like scaling nodes, cluster availability, and capacity for clusters, and scaling pods/replicas and application availability for pods.](https://kodekloud.com/kk-media/image/upload/v1752880237/notes-assets/images/Kubernetes-Autoscaling-Why-Do-We-Need-to-Autoscale/cluster-scaling-vs-pod-scaling.jpg)
</Frame>

---

## Bringing It All Together

Effective Kubernetes autoscaling leverages both cluster and pod strategies:

- Cluster Autoscaler maintains sufficient node capacity.
- Pod Autoscalers (HPA/VPA/KEDA) tailor application replicas and resource requests.

Together, they ensure cost-efficient, resilient, and performant workloads in dynamic environments.

<Frame>
  ![The image explains the need for different strategies in Kubernetes, highlighting "Cluster Scaling" for infrastructure and "Pod Scaling" for applications, ensuring both have the required capacity.](https://kodekloud.com/kk-media/image/upload/v1752880238/notes-assets/images/Kubernetes-Autoscaling-Why-Do-We-Need-to-Autoscale/kubernetes-scaling-strategies-diagram.jpg)
</Frame>

---

## Links & References

- [Kubernetes Autoscaling Concepts](https://kubernetes.io/docs/concepts/cluster-administration/autoscaling/)