---
title: Namespaces
date: 2026-01-22
categories: Kubernetes
tags:
  - Kubernetes
status:
source: 
  - Namespaces: https://thekubeguy.com/how-to-effectively-utilize-kubernetes-namespaces-74a612f7f971
---

Kubernetes Namespaces are essentially labels that partition a cluster into smaller, distinct segments. They allow you to organize your resources into groups that reflect different projects, teams, or environments within the same cluster. Imagine a cluster as a big office building: without any signs or room numbers, finding the right office would be a challenge. Namespaces act as these signs, guiding you to the right room — the right resource — quickly and efficiently.

## Why Use Namespaces?

1. **Organization:** Namespaces keep your cluster resources well-organized and manageable. This is particularly useful in environments where multiple teams or projects share the same Kubernetes cluster.
2. **Resource Management:** They enable fine-grained control over resources. For example, you can set quotas on CPU and memory usage on a per-Namespace basis, preventing one part of your cluster from hogging all the resources.
3. **Access Control:** Namespaces work hand in hand with Kubernetes’ Role-Based Access Control (RBAC) system, allowing administrators to restrict user permissions within specific Namespaces.

## A Closer Look at Namespaces

Kubernetes starts with four initial Namespaces:

- **Default:** The starting point for objects with no other Namespace.
- **Kube-system:** This Namespace contains objects created by the Kubernetes system itself, such as system processes.
- **Kube-public:** This is where public information resides. It’s readable by all users and used for special purposes, like the cluster discovery.
- **Kube-node-lease:** It holds lease objects that ensure node heartbeats. This helps the Kubernetes scheduler make better decisions.

## Creating Your Own Namespace

!!! example ""

    Creating a Namespace is straightforward.

    === "Imperative"

        !!! example ""
            You can do it with a simple command like:
            ```bash hl_lines="1"
            kubectl create namespace my-namespace
            ```

    === "Declarative"

        !!! example ""
            Or, you can create it using a YAML file, which might look something like this:
            ```yaml linenums="1" title="namespace.yaml"
            apiVersion: v1
            kind: Namespace
            metadata:
              name: my-namespace
            ```

            Then, apply it with:

            ```bash hl_lines="1"
            kubectl apply -f my-namespace.yaml
            ```

## Example: A Multi-Team Cluster

Let’s say you’re managing a cluster for an organization with three teams: Development, Staging, and Production. Without Namespaces, managing access and resources for each team would be chaotic. By creating a Namespace for each team, you can easily control who has access to what and set resource limits to prevent any team from using more than their fair share.

- **Development Team:** Works on new features and bug fixes.
- **Staging Team:** Handles testing and quality assurance of new releases.
- **Production Team:** Manages the live application serving real users.

### Step 1: Creating Namespaces for Each Team

First, we create a Namespace for each environment. This separation allows each team to work independently within the cluster, without interfering with each other’s resources.

```bash 
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production
```

These commands set up the basic organisational structure within your Kubernetes cluster, mirroring the organisation’s workflow.

### Step 2: Deploying Applications in Their Respective Namespaces

Each team deploys their version of the application within their designated Namespace. For instance, the Development team deploys the latest version of the app for testing new features:

```bash
kubectl apply -f development-app.yaml -n development
```

Similarly, the Staging and Production teams deploy their versions in the `staging` and `production` Namespaces, respectively. This ensures that the same application, at different stages of its lifecycle, can coexist without conflict in the same cluster.

### Step 3: Setting Resource Quotas

To prevent any team from overconsuming resources and affecting the others, you set resource quotas for each Namespace. For example, you might allocate more resources to Production since it’s critical to keep the live application running smoothly:

```yaml linenums="1"
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
```

This YAML file defines a quota for the Production Namespace, limiting it to specific CPU and memory usage. Similar quotas can be defined for Development and Staging, perhaps with lower resource allocations.

### Step 4: Implementing Access Control

Finally, you use Kubernetes’ Role-Based Access Control (RBAC) to give each team access only to their respective Namespace. This prevents unauthorized access to sensitive environments, especially Production. For instance, you might create roles that allow the Development team to deploy and manage resources in the `development` Namespace but not in `staging` or `production`.

## Tips for Managing Namespaces

- **Naming Conventions:** Establish clear naming conventions for your Namespaces. This will make them easier to manage as your cluster grows.
- **Resource Quotas:** Use resource quotas to prevent any one Namespace from consuming too much of the cluster’s resources.
- **Labels and Annotations:** Use labels and annotations to add metadata to your Namespaces. This can help with organizing and managing resources at a granular level.

By effectively utilizing Namespaces, you can ensure your cluster remains tidy, just like a well-organized library, making it easier for teams to find and utilize the resources they need. Whether you’re managing a cluster for a small team or a large enterprise, mastering Namespaces is a key step toward efficient Kubernetes management.

---

Imagine you’re the manager of a big office building. You’ve got multiple departments (like Finance, HR, and IT), and each department has its own team leaders and sub-teams. You wouldn’t just let everyone roam around wherever they please, right? You’d set up some boundaries and give permissions according to roles. That’s exactly what Kubernetes does with namespaces — but what happens when you need namespaces inside namespaces? Enter Hierarchical Namespaces.

Hierarchical Namespaces will allow you to create a tree-like structure of namespaces, making management much easier when dealing with complex setups.

Let’s break it down from the basics and then get into how to actually implement and use them.

### How Did Hierarchical Namespaces Come into the Picture?

Kubernetes namespaces were originally designed to divide cluster resources between different teams or environments. However, as organizations grew and their clusters became more complex, managing flat namespaces became increasingly challenging. Teams wanted more structure, such as grouping related namespaces or inheriting policies from one namespace to another. That’s where Hierarchical Namespaces came into the picture — to simplify management by introducing parent-child relationships between namespaces.

### Example:

Think of your laptop’s file system. You have folders (namespaces) and subfolders (hierarchical namespaces). Let’s say you have a main folder called “Projects,” and inside it, you have subfolders like “Frontend,” “Backend,” and “DevOps.” Each subfolder inherits the properties and permissions of the parent folder unless specified otherwise. That’s the gist of Hierarchical Namespaces!

### Why Use Hierarchical Namespaces?

1. **Organization:** When dealing with multi-tenant environments, you can group related namespaces under a single parent.
2. **Policy Inheritance:** Apply policies at the parent level, and they get inherited by all child namespaces.
3. **Separation of Concerns:** Maintain cleaner separation between different environments or applications.
4. **Efficient Resource Management:** Group related resources under a single namespace tree.

### Creating Hierarchical Namespaces

To create hierarchical namespaces, you’ll need the Hierarchical Namespace Controller (HNC) installed in your cluster. Let’s walk through the basic setup:

Step 1: Install HNC

```bash
kubectl apply -f https://github.com/kubernetes-sigs/multi-tenancy/releases/download/hnc-v0.9.0/hnc-manager.yaml
```

**Step 2: Create a Parent Namespace**

```bash
kubectl create namespace team-a
```

**Step 3: Create a Child Namespace**

```bash
kubectl hns create dev -n team-a
```

**Step 4: Verify the Hierarchy**

```bash
kubectl hns tree team-a
```

You should see an output similar to this:

```c
team-a
└── dev
```

**Step 5: Inherit Roles and Policies**

Roles and policies applied to the parent namespace will automatically cascade down to child namespaces unless explicitly overridden.

### Real-World Use Case: Multi-Tenant Environment

Imagine you’re managing a Kubernetes cluster for a SaaS product with multiple clients. Each client has different environments like dev, test, and prod. You can create a parent namespace for each client and have hierarchical namespaces for each environment under it. This way, policies applied to the client namespace will trickle down to all its environments, maintaining consistency without redundancy.

### Limitations and Caveats

- **Complexity:** Deeply nested namespaces can become hard to manage.
- **Performance:** Although minimal, there can be slight performance overhead with large hierarchy trees.
- **Limited Support:** Not every Kubernetes feature respects hierarchical namespace boundaries.

### Conclusion

Hierarchical Namespaces in Kubernetes are like a Russian nesting doll of resource management — open one, and there’s another inside. They help organize complex environments efficiently and maintain a clear separation between tenants and environments. Just remember, with great power comes great responsibility (and potential complexity). So, plan your namespace hierarchy carefully!