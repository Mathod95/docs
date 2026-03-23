---
title: "Managed Resource Activation Policy"
date: 2026-01-30
categories: Crossplane
tags:
  - Crossplane
  - ManagedResourceActivationPolicy
souces: 
  - https://medium.com/@chaima.belhedi/from-monolithic-providers-to-provider-families-to-mrap-testing-crossplane-v2-673e761d1135
  - https://evgenijohn.medium.com/compositions-super-power-48d463e7227f
---

## ManagedResourceActivationPolicy

Crossplane is a powerful tool that lets you manage cloud resources using Kubernetes. A few years ago, using the AWS provider in Crossplane was heavy. Installing the monolithic `provider-aws` would create **hundreds of CRDs**, even if you only needed a few resources like S3. This could make the control plane slow or unresponsive, and managing updates was hard.

To solve this, the Crossplane community introduced **Provider Families**. Instead of one big provider, AWS is now split into smaller **sub-providers** like `provider-aws-s3` and `provider-aws-ec2`. All sub-providers share a **family provider** (`provider-family-aws`) for common configuration, like credentials. The benefits of provider families are clear:

- **Fewer CRDs**: Install only what you need.
- **Better performance**: Controllers focus on fewer resources.
- **Easier upgrades**: Update one sub-provider without touching others.

Even with **Provider Families**, we still face a challenge. Each sub-provider installs a **large number of CRDs**, but in most cases, we don’t use them all.

Here’s an example: suppose you only want to use the `vpcs.ec2.aws.upbound.io` resource. To do that, you still have to install **all EC2 CRDs** —101 in version 1, or **202 CRDs in total** if you install an EC2 v2 provider. Imagine installing **202 CRDs just to use a single resource**! That adds unnecessary load to the control plane and increases cluster complexity, even when using Provider Families.

This is where **Crossplane v2** introduced an important feature: **ManagedResourceActivationPolicy (MRAP)**. MRAP lets you **selectively activate only the managed resources you need**, instead of enabling all resources that a provider ships.  
Check: [https://docs.crossplane.io/latest/managed-resources/managed-resource-activation-policies/](https://docs.crossplane.io/latest/managed-resources/managed-resource-activation-policies/)

With MRAPs, you can:

- **Activate only what you need:** For instance, enable just S3 buckets, RDS instances, or EC2 VPCs.
- **Use patterns for flexibility:** Activate multiple resources using wildcards, like `*.ec2.aws.m.crossplane.io`.
- **Track activation status:** MRAPs report which resources are active and which are inactive, so you always know the state of your cluster.
- **MRAPs are additive and flexible:** You can create several MRAPs and they’ll all be applied together. For example, you could have one MRAP for **AWS**, another for **GCP**, and a third for **Azure**.

### Example MRAP

```yaml linenums="1"
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: aws-core-resources
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io      # Activate S3 buckets
  - instances.rds.aws.m.crossplane.io   # Activate RDS instances
  - "*.ec2.aws.m.crossplane.io"         # Activate all EC2 resources
```

### Testing an Example on a Local Kind Cluster

To see MRAP in action, let’s run a simple test on a local **Kind cluster**. In this example, we’ll install an **AWS** **EC2 provider** and observe how MRAP affects memory usage and the number of CRDs.

**Step 1: Create a Kind Cluster**

```c
kind create cluster --name crossplane-test
```

**Step 2: Install Crossplane v2**

```c
helm repo add crossplane-stable https://charts.crossplane.io/stable

helm install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --version 2.0.2 \
  --set "provider.defaultActivations={}"
```

**Note:** By default, Crossplane activates **all managed resources (MRDs)** when a provider is installed. We set `provider.defaultActivations={}` to **disable default activations**, allowing us to create our own MRAP and selectively activate only the resources we need.

**Step 3: Install Metrics Server:** Kind clusters don’t include Metrics Server by default, which is required for `kubectl top` to work. Install it with:

```c
#Download the Metrics Server manifest:
wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

#Edit the manifest to allow insecure TLS communication
#Under spec.template.spec.containers[0].args, add:
# - --kubelet-insecure-tls

#Apply the updated manifest:
kubectl apply -f components.yaml
```

**Step 4: Install the EC2 Provider: Create a YAML file for the provider:**

```c
# ec2.yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: crossplane-contrib-provider-aws-ec2
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-aws-ec2:v2.2.0

kubectl apply -f ec2.yaml
```

Apply it to your cluster:

```c
kubectl apply -f ec2.yaml
```

When you install this provider, you’ll notice that the **Provider Family** `crossplane-contrib-provider-family-aws` is installed automatically. So you don’t have to install it manually.

```c
belhedi@Chaimas-MacBook-Pro-2 ~> kubectl get providers -w
NAME                                     INSTALLED   HEALTHY   PACKAGE                                                            AGE
crossplane-contrib-provider-aws-ec2       True        True     xpkg.crossplane.io/crossplane-contrib/provider-aws-ec2:v2.2.0      66s
crossplane-contrib-provider-family-aws    True        True     xpkg.crossplane.io/crossplane-contrib/provider-family-aws:v2.2.0   56s
```

**Step 5: Observe CRDs and API Server Memory:**

After installing the EC2 provider, you can check **how many CRDs are installed** and the **memory usage** of the Kubernetes API server:

```c
# Count all EC2-related CRDs
kubectl get crds | grep ec2 | wc -l
  202
```
```c
# Check API server memory usage
belhedi@Chaimas-MacBook-Pro-2 ~> kubectl top pod -n kube-system

NAME                                                    CPU(cores)   MEMORY(bytes)   
coredns-7db6d8ff4d-6fhd6                                2m           20Mi            
coredns-7db6d8ff4d-tk8sq                                2m           16Mi            
etcd-crossplane-test-control-plane                      54m          191Mi           
kindnet-k5jx2                                           1m           19Mi            
kube-apiserver-crossplane-test-control-plane            113m         1245Mi          
kube-controller-manager-crossplane-test-control-plane   20m          104Mi           
kube-proxy-ltw4c                                        3m           45Mi            
kube-scheduler-crossplane-test-control-plane            4m           39Mi            
metrics-server-69b767676f-tsvsj                         5m           39Mi
```

**Step 6: Apply a Minimal MRAP**

Now, we will install our EC2 provider and create a **ManagedResourceActivationPolicy (MRAP)** to activate only the resources we actually need. This reduces control plane load while keeping all CRDs installed.

```c
#minimal-ec2-mrap.yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: minimal-ec2
spec:
  activate:
  - vpcs.ec2.aws.m.upbound.io       # Activate only the VPC resource
```

Apply the MRAP:

```c
kubectl apply -f minimal-ec2-mrap.yaml
```

**Step 7: Compare Before and After MRAP**

After applying a **minimal MRAP** that activates only the VPC resource, let’s see how things change.

**Check which EC2 CRDs are active:**

```c
belhedi@Chaimas-MacBook-Pro-2 ~> kubectl get crds | grep ec2
vpcs.ec2.aws.m.upbound.io                                       2025-11-16T21:45:29Z
```

**Check API server memory usage:**

```bash
belhedi@Chaimas-MacBook-Pro-2 ~> kubectl top pod -n kube-system
NAME                                                    CPU(cores)   MEMORY(bytes)   
coredns-7db6d8ff4d-6fhd6                                3m           15Mi            
coredns-7db6d8ff4d-tk8sq                                6m           45Mi            
etcd-crossplane-test-control-plane                      29m          237Mi           
kindnet-k5jx2                                           2m           22Mi            
kube-apiserver-crossplane-test-control-plane            94m          857Mi           
kube-controller-manager-crossplane-test-control-plane   25m          123Mi           
kube-proxy-ltw4c                                        1m           36Mi            
kube-scheduler-crossplane-test-control-plane            5m           38Mi            
metrics-server-69b767676f-tsvsj                         5m           51Mi
```

**Observations:**

- Only the **VPC CRD is installed**.
- **API server memory usage decreased**:for example, from ~1245Mi to ~857Mi. This demonstrates how MRAPs **improve efficiency**: controllers focus only on the resources you actually need, keeping your cluster performant and easier to manage.

### Key Takeaways:

- This blog walks you through how Crossplane evolved from **monolithic providers** — which installed hundreds of CRDs — to **Provider Families**, and now to **MRAP (ManagedResourceActivationPolicy)** in v2.
- **Selective Activation Saves Resources:** MRAP allows you to activate only the managed resources you actually need, reducing CPU and memory usage in the control plane.
- **Improved Performance:** By limiting active resources, the API server and controllers consume less memory and CPU, making clusters more stable and responsive.

```bash
❯ helm repo add crossplane-stable https://charts.crossplane.io/stable
"crossplane-stable" already exists with the same configuration, skipping

❯ helm install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --version 2.0.2 \
  --set "provider.defaultActivations={}"
NAME: crossplane
LAST DEPLOYED: Fri Jan 30 15:13:24 2026
NAMESPACE: crossplane-system
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
Release: crossplane

Chart Name: crossplane
Chart Description: Crossplane is an open source Kubernetes add-on that enables platform teams to assemble infrastructure from multiple vendors, and expose higher level self-service APIs for application teams to consume.
Chart Version: 2.0.2
Chart Application Version: 2.0.2

Kube Version: v1.35.0
```

3. #Download the Metrics Server manifest:
wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

#Edit the manifest to allow insecure TLS communication
#Under spec.template.spec.containers[0].args, add:
# - --kubelet-insecure-tls


#Apply the updated manifest:
kubectl apply -f components.yaml

```yaml title="provider-aws-ec2.yaml" linenums="1"
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: upbound-provider-aws-ec2
spec:
  package: xpkg.upbound.io/upbound/provider-aws-ec2:v2.3.0
```

```
❯ kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
upbound-provider-aws-ec2      True        True      xpkg.upbound.io/upbound/provider-aws-ec2:v2.3.0      114s
upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v2.3.0   106s
```

```
❯ kubectl get crossplane | grep 'ec2.aws' | wc -l
Warning: apiextensions.crossplane.io Usage is deprecated; migrate to protection.crossplane.io Usage or ClusterUsage
202
```


```
❯ kubectl top pod -n kube-system
NAME                                               CPU(cores)   MEMORY(bytes)
coredns-7d764666f9-hbx6j                           2m           13Mi
coredns-7d764666f9-s4bzn                           2m           13Mi
etcd-crossplane-control-plane                      25m          92Mi
kindnet-c597b                                      1m           10Mi
kube-apiserver-crossplane-control-plane            37m          460Mi
kube-controller-manager-crossplane-control-plane   15m          59Mi
kube-proxy-crxkd                                   1m           14Mi
kube-scheduler-crossplane-control-plane            6m           24Mi
metrics-server-7ddc7ff799-jhkpz                    3m           19Mi
```

```yaml linenums="1" title="#minimal-ec2-mrap.yaml"
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: minimal-ec2
spec:
  activate:
  - vpcs.ec2.aws.m.upbound.io
```


```
kubectl get crossplane | grep 'ec2.aws'
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnectionoptions.ec2.aws.m.upbound.io                 Inactive   False         11m
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnectionoptions.ec2.aws.upbound.io                   Inactive   False         11m
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnections.ec2.aws.m.upbound.io                       Inactive   False         11m
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnections.ec2.aws.upbound.io                         Inactive   False         11m
managedresourcedefinition.apiextensions.crossplane.io/vpcs.ec2.aws.m.upbound.io                                        Active     True          11m
managedresourcedefinition.apiextensions.crossplane.io/vpcs.ec2.aws.upbound.io                                          Inactive   False         11m
managedresourcedefinition.apiextensions.crossplane.io/vpnconnectionroutes.ec2.aws.m.upbound.io                         Inactive   False         11m
managedresourcedefinition.apiextensions.crossplane.io/vpnconnectionroutes.ec2.aws.upbound.io                           Inactive   False         11m
```

```
kubectl top pod -n kube-system
NAME                                               CPU(cores)   MEMORY(bytes)
coredns-7d764666f9-hbx6j                           2m           13Mi
coredns-7d764666f9-s4bzn                           2m           13Mi
etcd-crossplane-control-plane                      24m          100Mi
kindnet-c597b                                      1m           10Mi
kube-apiserver-crossplane-control-plane            39m          448Mi
kube-controller-manager-crossplane-control-plane   15m          57Mi
kube-proxy-crxkd                                   1m           15Mi
kube-scheduler-crossplane-control-plane            6m           27Mi
metrics-server-7ddc7ff799-jhkpz                    3m           20Mi
```


```
❯ kubectl top pod -n kube-system
NAME                                               CPU(cores)   MEMORY(bytes)
coredns-7d764666f9-hbx6j                           2m           13Mi
coredns-7d764666f9-s4bzn                           2m           13Mi
etcd-crossplane-control-plane                      45m          247Mi
kindnet-c597b                                      1m           10Mi
kube-apiserver-crossplane-control-plane            86m          1380Mi
kube-controller-manager-crossplane-control-plane   15m          85Mi
kube-proxy-crxkd                                   1m           14Mi
kube-scheduler-crossplane-control-plane            6m           25Mi
metrics-server-7ddc7ff799-jhkpz                    3m           22Mi
```


```
managedresourcedefinition.apiextensions.crossplane.io/vpcipampoolcidrallocations.ec2.aws.upbound.io                    Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcipampoolcidrs.ec2.aws.m.upbound.io                            Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcipampoolcidrs.ec2.aws.upbound.io                              Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcipampools.ec2.aws.m.upbound.io                                Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcipampools.ec2.aws.upbound.io                                  Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcipams.ec2.aws.m.upbound.io                                    Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcipams.ec2.aws.upbound.io                                      Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcipamscopes.ec2.aws.m.upbound.io                               Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcipamscopes.ec2.aws.upbound.io                                 Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcipv4cidrblockassociations.ec2.aws.m.upbound.io                Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcipv4cidrblockassociations.ec2.aws.upbound.io                  Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnectionaccepters.ec2.aws.m.upbound.io               Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnectionaccepters.ec2.aws.upbound.io                 Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnectionoptions.ec2.aws.m.upbound.io                 Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnectionoptions.ec2.aws.upbound.io                   Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnections.ec2.aws.m.upbound.io                       Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcpeeringconnections.ec2.aws.upbound.io                         Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpcs.ec2.aws.m.upbound.io                                        Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpcs.ec2.aws.upbound.io                                          Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpnconnectionroutes.ec2.aws.m.upbound.io                         Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpnconnectionroutes.ec2.aws.upbound.io                           Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpnconnections.ec2.aws.m.upbound.io                              Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpnconnections.ec2.aws.upbound.io                                Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpngatewayattachments.ec2.aws.m.upbound.io                       Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpngatewayattachments.ec2.aws.upbound.io                         Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpngatewayroutepropagations.ec2.aws.m.upbound.io                 Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpngatewayroutepropagations.ec2.aws.upbound.io                   Active   True          6m17s
managedresourcedefinition.apiextensions.crossplane.io/vpngateways.ec2.aws.m.upbound.io                                 Active   True          6m18s
managedresourcedefinition.apiextensions.crossplane.io/vpngateways.ec2.aws.upbound.io                                   Active   True          6m17s
```