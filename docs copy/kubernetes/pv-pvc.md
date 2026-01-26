---
title: Persistent Volumes (PV) and Persistent Volume Claims (PVC)
categories: Kubernetes
tags:
  - Kubernetes
status:
sources:
  - PV & PVC: https://thekubeguy.com/understanding-persistent-volumes-pv-and-persistent-volume-claims-pvc-in-kubernetes-fb5f808ed9db
---

In Kubernetes, managing storage efficiently stands out as a crucial aspect of ensuring applications run smoothly and data persists beyond the life of individual pods. This is where Persistent Volumes (PV) and Persistent Volume Claims (PVC) come into play. Today let’s learn these concepts and understand their significance in the Kubernetes ecosystem.

### Persistent Volumes (PV)

A Persistent Volume (PV) is a piece of storage in the cluster that has been provisioned by an administrator or dynamically provisioned using Storage Classes. It’s a way to abstract the details of how the storage is provided and how it’s consumed. Think of PV as a physical hard drive in a network storage system, but with a twist. It’s not tied to any single pod; instead, it exists independently of pod lifecycles, ensuring that data persists across pod restarts and failures.

PVs can come from various sources:

- Network-attached storage systems like NFS, iSCSI, or cloud-based storage such as AWS EBS, Google Cloud Persistent Disk, or Azure Disk Storage.
- Local storage on the nodes.

Administrators can define PVs in the cluster without associating them with any particular pod. This way, they can manage storage resources separately from pod-specific configurations.

### Persistent Volume Claims (PVC)

While PVs are the storage volumes available within the cluster, Persistent Volume Claims are essentially requests for storage by a user. A PVC specifies size, and access modes like read-only, read-write, among other criteria. You can think of a PVC as a storage request ticket given to the Kubernetes cluster by a pod that needs storage.

The magic of Kubernetes matches a PVC to a PV based on the requirements cited in the claim (size, access modes, etc.). If the cluster has a PV that satisfies the claim, it binds the PV to the PVC, making the storage available to the pod that made the request. If no suitable PV is available, and dynamic provisioning is enabled, the cluster may dynamically create a new PV that matches the claim.

### Why PV and PVC?

This separation of concerns is what makes the PV/PVC model powerful:

- Decoupling of storage configuration from the usage: Administrators can prepare a pool of storage (PVs) without knowing the specific needs of each pod, allowing for a more flexible and efficient use of resources.
- Storage consumption as needed: Pods can claim storage resources as needed without requiring direct access or knowledge of the underlying storage infrastructure.
- Dynamic provisioning: The ability to dynamically create storage resources based on demand, reducing manual intervention and speeding up deployment processes.

### Example Scenario

To put it into perspective, imagine if you’re moving into a new apartment (pod) and you need a storage unit (PV). You fill out a form specifying your needs (PVC), and the apartment complex matches you with an available unit that fits your criteria. If no units are available, they build a new one just for you. This way, you get the storage you need without worrying about the details of how it’s provided.

### Conclusion

Persistent Volumes and Persistent Volume Claims are foundational elements in Kubernetes that ensure data persists and is accessible to applications, irrespective of the lifecycle of individual pods. By understanding and leveraging PVs and PVCs, developers can focus on building and deploying applications, leaving the complexities of storage management to Kubernetes.

I'll help you sail through the ocean of Kubernetes with minimal efforts