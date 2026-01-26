---
title: Kube-Scheduler
categories: Kubernetes
tags:
  - Kubernetes
status:
sources:
  - Kube-Scheduler: https://thekubeguy.com/kube-scheduler-7468e436ad24
---

### Qu'est-ce que Kube-Scheduler ?
Kube-scheduler est le scheduler par défaut de Kubernetes, responsable d'assigner les pods nouvellement créés aux nodes appropriés au sein du cluster. Il prend ces décisions en fonction de divers facteurs afin d'assurer une performance optimale, une utilisation efficace des ressources et le respect des contraintes ou des politiques définies par l'utilisateur.

### Key responsibilities du Scheduler :

1. **Node Selection:** Identifier le meilleur node pour chaque pod en fonction des exigences en ressources et de leur disponibilité.
2. **Resource Allocation:** S'assurer que le CPU, la mémoire et les autres resources sont correctement alloués.
3. **Constraints Handling:** Prendre en compte des constraints telles que l'affinité des nodes, les taints et les tolerations.
4. **Prioritization:** Classer les nodes en fonction de divers critères pour trouver le plus adapté.

### Example The Restaurant Table Scheduler
Imagine a busy restaurant where guests arrive without reservations and need to be seated at the appropriate tables. The restaurant has a host (analogous to the kube-scheduler) whose job is to seat guests at the best available table based on several factors. Let’s explore how this restaurant scenario parallels the functioning of the kube-scheduler.

#### Step-by-Step Scheduling Process

1.  Guest Arrival (Pod Creation)
    * In Kubernetes, a pod represents one or more containers that need to run on a node. When a new pod is created, it’s similar to a new group of guests arriving at the restaurant.

2.  Checking Table Availability (Node Filtering)
    * The host first checks which tables are available. Similarly, the kube-scheduler filters out nodes that cannot accommodate the pod due to insufficient resources or other constraints.

3.  Considering Guest Preferences (Node Affinity and Anti-Affinity)
    * Some guests may prefer to sit in a specific area of the restaurant (near the window, away from the kitchen). The host considers these preferences. In Kubernetes, this is managed through node affinity and anti-affinity rules that guide the scheduler on preferred or avoided nodes.

4.  Matching Table Size to Party Size (Resource Requests)
    * The host matches the table size with the number of guests. In Kubernetes, the kube-scheduler looks at the resource requests (CPU, memory) specified for the pod and matches them with the available resources on the nodes.

5.  Special Requests (Taints and Tolerations)
    * Some guests might have special requests, like requiring a high chair or a quiet corner. The host must ensure these needs are met. Similarly, nodes can have taints that only certain pods with matching tolerations can tolerate, ensuring special conditions are respected.

6.  Selecting the Best Table (Node Prioritization)
    * Once suitable tables are identified, the host prioritizes them based on factors like proximity to the kitchen for quicker service or distance from noisy areas. The kube-scheduler ranks the nodes using various scoring algorithms to choose the best fit for the pod.

7.  Seating the Guests (Binding the Pod)
    * Finally, the host seats the guests at the selected table. The kube-scheduler assigns the pod to the chosen node, officially binding it.

**Example in Kubernetes Terms**

Let’s consider a concrete example in Kubernetes:

```yaml linenums="1"
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
  nodeSelector:
    disktype: ssd
  tolerations:
  - key: "key1"
    operator: "Equal"
    value: "value1"
    effect: "NoSchedule"
```

Kube-Scheduler Components
Scheduling Algorithm
The kube-scheduler follows a two-step process: filtering and scoring.

1. Filtering: The scheduler filters out nodes that do not meet the pod’s requirements. This includes checks for resource availability, node conditions, taints, and affinity/anti-affinity rules.

2. Scoring: After filtering, the scheduler scores the remaining nodes to find the most suitable one. Various plugins and scoring functions are used, considering factors like resource utilization, pod topology spread, and custom user-defined rules.

Plugins and Extensibility
Kube-scheduler is highly extensible, allowing custom scheduling policies and plugins. This flexibility enables users to tailor the scheduling process to meet specific needs and optimize resource allocation and performance.

### Conclusion
Configurer correctement et comprendre le kube-scheduler est essentiel dans plusieurs scénarios :

- **High-Density Clusters:** Lors de l'exécution d'un grand nombre de pods, une planification efficace garantit une utilisation optimale des ressources et des performances élevées.
- **Resource-Constrained Environments:** Dans des environnements avec des ressources limitées, une planification efficace empêche la contention des ressources et assure un fonctionnement stable.
- **Complex Workloads:** Les applications ayant des besoins spécifiques en matière de placement, comme les règles affinity/anti-affinity et les contraintes de ressources, bénéficient de politiques de planification personnalisées.