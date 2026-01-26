---
title: "Hierarchical Namespaces in Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/google-cloud/hierarchical-namespaces-in-kubernetes-4f99548f50b2"
author:
  - "[[The kube guy]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@thekubeguy)## [Google Cloud - Community](https://medium.com/google-cloud?source=post_page---publication_nav-e52cf94d98af-4f99548f50b2---------------------------------------)

[![Google Cloud - Community](https://miro.medium.com/v2/resize:fill:76:76/1*FUjLiCANvATKeaJEeg20Rw.png)](https://medium.com/google-cloud?source=post_page---post_publication_sidebar-e52cf94d98af-4f99548f50b2---------------------------------------)

A collection of technical articles and blogs published or curated by Google Cloud Developer Advocates. The views expressed are those of the authors and don't necessarily reflect those of Google.

Imagine you’re the manager of a big office building. You’ve got multiple departments (like Finance, HR, and IT), and each department has its own team leaders and sub-teams. You wouldn’t just let everyone roam around wherever they please, right? You’d set up some boundaries and give permissions according to roles. That’s exactly what Kubernetes does with namespaces — but what happens when you need namespaces inside namespaces? Enter Hierarchical Namespaces.

Hierarchical Namespaces will allow you to create a tree-like structure of namespaces, making management much easier when dealing with complex setups.

Let’s break it down from the basics and then get into how to actually implement and use them.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Oj733K5M-W_QHn_6mtbtlQ.png)

Image By Author

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

```c
kubectl apply -f https://github.com/kubernetes-sigs/multi-tenancy/releases/download/hnc-v0.9.0/hnc-manager.yaml
```

**Step 2: Create a Parent Namespace**

```c
kubectl create namespace team-a
```

**Step 3: Create a Child Namespace**

```c
kubectl hns create dev -n team-a
```

**Step 4: Verify the Hierarchy**

```c
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

If you made it this far, congratulations! You’re officially part of the Kubernetes hierarchy elite. Follow TheKubeGuy for more mind-bending Kubernetes content. Who knows — maybe one day you’ll master the elusive art of taming the namespace beast. Spoiler alert: it’s never truly tamed.

[![Google Cloud - Community](https://miro.medium.com/v2/resize:fill:96:96/1*FUjLiCANvATKeaJEeg20Rw.png)](https://medium.com/google-cloud?source=post_page---post_publication_info--4f99548f50b2---------------------------------------)

[![Google Cloud - Community](https://miro.medium.com/v2/resize:fill:128:128/1*FUjLiCANvATKeaJEeg20Rw.png)](https://medium.com/google-cloud?source=post_page---post_publication_info--4f99548f50b2---------------------------------------)

[Last published 6 hours ago](https://medium.com/google-cloud/gcp-cli-gcloud-commands-cheat-sheet-ultimate-devops-cloud-engineer-guide-2026-5f04debca51a?source=post_page---post_publication_info--4f99548f50b2---------------------------------------)

A collection of technical articles and blogs published or curated by Google Cloud Developer Advocates. The views expressed are those of the authors and don't necessarily reflect those of Google.

I'll help you sail through the ocean of Kubernetes with minimal efforts

## More from The kube guy and Google Cloud - Community

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--4f99548f50b2---------------------------------------)