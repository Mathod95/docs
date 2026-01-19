---
title: "NodeClasses"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://karpenter.sh/docs/concepts/nodeclasses/"
author:
  - "[[ec2:DescribeCapacityReservations]]"
  - "[[ec2:RunInstances]]"
---
<!-- more -->

Node Classes enable configuration of AWS specific settings. Each NodePool must reference an EC2NodeClass using `spec.template.spec.nodeClassRef`. Multiple NodePools may point to the same EC2NodeClass.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
---
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  kubelet:
    podsPerCore: 2
    maxPods: 20
    systemReserved:
      cpu: 100m
      memory: 100Mi
      ephemeral-storage: 1Gi
    kubeReserved:
      cpu: 200m
      memory: 100Mi
      ephemeral-storage: 3Gi
    evictionHard:
      memory.available: 5%
      nodefs.available: 10%
      nodefs.inodesFree: 10%
    evictionSoft:
      memory.available: 500Mi
      nodefs.available: 15%
      nodefs.inodesFree: 15%
    evictionSoftGracePeriod:
      memory.available: 1m
      nodefs.available: 1m30s
      nodefs.inodesFree: 2m
    evictionMaxPodGracePeriod: 60
    imageGCHighThresholdPercent: 85
    imageGCLowThresholdPercent: 80
    cpuCFSQuota: true
    clusterDNS: ["10.0.1.100"]
  # Optional, dictates UserData generation and default block device mappings.
  # May be ommited when using an \`alias\` amiSelectorTerm, otherwise required.
  amiFamily: AL2

  # Required, discovers subnets to attach to instances
  # Each term in the array of subnetSelectorTerms is ORed together
  # Within a single term, all conditions are ANDed
  subnetSelectorTerms:
    # Select on any subnet that has the "karpenter.sh/discovery: ${CLUSTER_NAME}"
    # AND the "environment: test" tag OR any subnet with ID "subnet-09fa4a0a8f233a921"
    - tags:
        karpenter.sh/discovery: "${CLUSTER_NAME}"
        environment: test
    - id: subnet-09fa4a0a8f233a921

  # Required, discovers security groups to attach to instances
  # Each term in the array of securityGroupSelectorTerms is ORed together
  # Within a single term, all conditions are ANDed
  securityGroupSelectorTerms:
    # Select on any security group that has both the "karpenter.sh/discovery: ${CLUSTER_NAME}" tag
    # AND the "environment: test" tag OR any security group with the "my-security-group" name
    # OR any security group with ID "sg-063d7acfb4b06c82c"
    - tags:
        karpenter.sh/discovery: "${CLUSTER_NAME}"
        environment: test
    - name: my-security-group
    - id: sg-063d7acfb4b06c82c

  # Optional, IAM role to use for the node identity.
  # Must specify one of "role" or "instanceProfile" for Karpenter to launch nodes
  role: "KarpenterNodeRole-${CLUSTER_NAME}"

  # Optional, IAM instance profile to use for the node identity.
  # Must specify one of "role" or "instanceProfile" for Karpenter to launch nodes
  instanceProfile: "KarpenterNodeInstanceProfile-${CLUSTER_NAME}"

  # Each term in the array of amiSelectorTerms is ORed together
  # Within a single term, all conditions are ANDed
  amiSelectorTerms:
    # Select on any AMI that has both the \`karpenter.sh/discovery: ${CLUSTER_NAME}\`
    # AND \`environment: test\` tags OR any AMI with the name \`my-ami\` OR an AMI with
    # ID \`ami-123\` OR an AMI with ID matching the value of my-custom-parameter
    - tags:
        karpenter.sh/discovery: "${CLUSTER_NAME}"
        environment: test
    - name: my-ami
    - id: ami-123
    - ssmParameter: my-custom-parameter # ssm parameter name or ARN
    # Select EKS optimized AL2023 AMIs with version \`v20240703\`. This term is mutually
    # exclusive and can't be specified with other terms.
    # - alias: al2023@v20240703

  # Optional, each term in the array of capacityReservationSelectorTerms is ORed together.
  capacityReservationSelectorTerms:
    - tags:
        karpenter.sh/discovery: ${CLUSTER_NAME}
    - id: cr-123
    - instanceMatchCriteria: open

  # Optional, propagates tags to underlying EC2 resources
  tags:
    team: team-a
    app: team-a-app

  # Optional, configures IMDS for the instance
  metadataOptions:
    httpEndpoint: enabled
    httpProtocolIPv6: disabled
    httpPutResponseHopLimit: 1 # This is changed to disable IMDS access from containers not on the host network
    httpTokens: required

  # Optional, configures storage devices for the instance
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 100Gi
        volumeType: gp3
        iops: 10000
        encrypted: true
        kmsKeyID: "1234abcd-12ab-34cd-56ef-1234567890ab"
        deleteOnTermination: true
        throughput: 125
        snapshotID: snap-0123456789
        volumeInitializationRate: 100

  # Optional, use instance-store volumes for node ephemeral-storage
  instanceStorePolicy: RAID0

  # Optional, overrides autogenerated userdata with a merge semantic
  userData: |
    echo "Hello world"    

  # Optional, configures detailed monitoring for the instance
  detailedMonitoring: true

  # Optional, configures if the instance should be launched with an associated public IP address.
  # If not specified, the default value depends on the subnet's public IP auto-assign setting.
  associatePublicIPAddress: true
status:
  # Resolved subnets
  subnets:
    - id: subnet-0a462d98193ff9fac
      zone: us-east-2b
    - id: subnet-0322dfafd76a609b6
      zone: us-east-2c
    - id: subnet-0727ef01daf4ac9fe
      zone: us-east-2b
    - id: subnet-00c99aeafe2a70304
      zone: us-east-2a
    - id: subnet-023b232fd5eb0028e
      zone: us-east-2c
    - id: subnet-03941e7ad6afeaa72
      zone: us-east-2a

  # Resolved security groups
  securityGroups:
    - id: sg-041513b454818610b
      name: ClusterSharedNodeSecurityGroup
    - id: sg-0286715698b894bca
      name: ControlPlaneSecurityGroup-1AQ073TSAAPW

  # Resolved AMIs
  amis:
    - id: ami-01234567890123456
      name: custom-ami-amd64
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values:
            - amd64
    - id: ami-01234567890123456
      name: custom-ami-arm64
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values:
            - arm64

  # Capacity Reservations
  capacityReservations:
    - availabilityZone: us-west-2a
      id: cr-01234567890123456
      instanceMatchCriteria: targeted
      instanceType: g6.48xlarge
      ownerID: "012345678901"
      reservationType: capacity-block
      state: expiring
    - availabilityZone: us-west-2c
      id: cr-12345678901234567
      instanceMatchCriteria: open
      instanceType: g6.48xlarge
      ownerID: "98765432109"
      reservationType: default
      state: active

  # Generated instance profile name from "role"
  instanceProfile: "${CLUSTER_NAME}-0123456778901234567789"
  conditions:
    - lastTransitionTime: "2024-02-02T19:54:34Z"
      status: "True"
      type: InstanceProfileReady
    - lastTransitionTime: "2024-02-02T19:54:34Z"
      status: "True"
      type: SubnetsReady
    - lastTransitionTime: "2024-02-02T19:54:34Z"
      status: "True"
      type: SecurityGroupsReady
    - lastTransitionTime: "2024-02-02T19:54:34Z"
      status: "True"
      type: AMIsReady
    - lastTransitionTime: "2024-02-02T19:54:34Z"
      status: "True"
      type: Ready
```

Refer to the [NodePool docs](https://karpenter.sh/docs/concepts/nodepools/) for settings applicable to all providers. To explore various `EC2NodeClass` configurations, refer to the examples provided [in the Karpenter Github repository](https://github.com/aws/karpenter/blob/main/examples/v1/).

## spec.kubelet

Karpenter provides the ability to specify a few additional Kubelet arguments. These are all optional and provide support for additional customization and use cases. Adjust these only if you know you need to do so. For more details on kubelet settings, see the [KubeletConfiguration reference](https://kubernetes.io/docs/reference/config-api/kubelet-config.v1/). The implemented fields are a subset of the full list of upstream kubelet configuration arguments.

```yaml
kubelet:
  podsPerCore: 2
  maxPods: 20
  systemReserved:
    cpu: 100m
    memory: 100Mi
    ephemeral-storage: 1Gi
  kubeReserved:
    cpu: 200m
    memory: 100Mi
    ephemeral-storage: 3Gi
  evictionHard:
    memory.available: 5%
    nodefs.available: 10%
    nodefs.inodesFree: 10%
  evictionSoft:
    memory.available: 500Mi
    nodefs.available: 15%
    nodefs.inodesFree: 15%
  evictionSoftGracePeriod:
    memory.available: 1m
    nodefs.available: 1m30s
    nodefs.inodesFree: 2m
  evictionMaxPodGracePeriod: 60
  imageGCHighThresholdPercent: 85
  imageGCLowThresholdPercent: 80
  cpuCFSQuota: true
  clusterDNS: ["10.0.1.100"]
```

#### Pods Per Core

An alternative way to dynamically set the maximum density of pods on a node is to use the `.spec.kubelet.podsPerCore` value. Karpenter will calculate the pod density during scheduling by multiplying this value by the number of logical cores (vCPUs) on an instance type. This value will also be passed through to the `--pods-per-core` value on kubelet startup to configure the number of allocatable pods the kubelet can assign to the node instance.

The value generated from `podsPerCore` cannot exceed `maxPods`, meaning, if both are set, the minimum of the `podsPerCore` dynamic pod density and the static `maxPods` value will be used for scheduling.

#### Max Pods

For small instances that require an increased pod density or large instances that require a reduced pod density, you can override this default value with `.spec.kubelet.maxPods`. This value will be used during Karpenter pod scheduling and passed through to `--max-pods` on kubelet startup.

### Reserved Resources

Karpenter will automatically configure the system and kube reserved resource requests on the fly on your behalf. These requests are used to configure your node and to make scheduling decisions for your pods. If you have specific requirements or know that you will have additional capacity requirements, you can optionally override the `--system-reserved` configuration defaults with the `.spec.kubelet.systemReserved` values and the `--kube-reserved` configuration defaults with the `.spec.kubelet.kubeReserved` values.

### Eviction Thresholds

The kubelet supports eviction thresholds by default. When enough memory or file system pressure is exerted on the node, the kubelet will begin to evict pods to ensure that system daemons and other system processes can continue to run in a healthy manner.

Kubelet has the notion of [hard evictions](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/#hard-eviction-thresholds) and [soft evictions](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/#soft-eviction-thresholds). In hard evictions, pods are evicted as soon as a threshold is met, with no grace period to terminate. Soft evictions, on the other hand, provide an opportunity for pods to be terminated gracefully. They do so by sending a termination signal to pods that are planning to be evicted and allowing those pods to terminate up to their grace period.

Karpenter supports [hard evictions](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/#hard-eviction-thresholds) through the `.spec.kubelet.evictionHard` field and [soft evictions](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/#soft-eviction-thresholds) through the `.spec.kubelet.evictionSoft` field. `evictionHard` and `evictionSoft` are configured by listing [signal names](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/#eviction-signals) with either percentage values or resource values.

```yaml
kubelet:
  evictionHard:
    memory.available: 500Mi
    nodefs.available: 10%
    nodefs.inodesFree: 10%
    imagefs.available: 5%
    imagefs.inodesFree: 5%
    pid.available: 7%
  evictionSoft:
    memory.available: 1Gi
    nodefs.available: 15%
    nodefs.inodesFree: 15%
    imagefs.available: 10%
    imagefs.inodesFree: 10%
    pid.available: 10%
```

#### Supported Eviction Signals

| Eviction Signal | Description |
| --- | --- |
| memory.available | memory.available:= node.status.capacity\[memory\] - node.stats.memory.workingSet |
| nodefs.available | nodefs.available:= node.stats.fs.available |
| nodefs.inodesFree | nodefs.inodesFree:= node.stats.fs.inodesFree |
| imagefs.available | imagefs.available:= node.stats.runtime.imagefs.available |
| imagefs.inodesFree | imagefs.inodesFree:= node.stats.runtime.imagefs.inodesFree |
| pid.available | pid.available:= node.stats.rlimit.maxpid - node.stats.rlimit.curproc |

For more information on eviction thresholds, view the [Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction) section of the official Kubernetes docs.

#### Soft Eviction Grace Periods

Soft eviction pairs an eviction threshold with a specified grace period. With soft eviction thresholds, the kubelet will only begin evicting pods when the node exceeds its soft eviction threshold over the entire duration of its grace period. For example, if you specify `evictionSoft[memory.available]` of `500Mi` and a `evictionSoftGracePeriod[memory.available]` of `1m30`, the node must have less than `500Mi` of available memory over a minute and a half in order for the kubelet to begin evicting pods.

Optionally, you can specify an `evictionMaxPodGracePeriod` which defines the administrator-specified maximum pod termination grace period to use during soft eviction. If a namespace-owner had specified a pod `terminationGracePeriodInSeconds` on pods in their namespace, the minimum of `evictionPodGracePeriod` and `terminationGracePeriodInSeconds` would be used.

```yaml
kubelet:
  evictionSoftGracePeriod:
    memory.available: 1m
    nodefs.available: 1m30s
    nodefs.inodesFree: 2m
    imagefs.available: 1m30s
    imagefs.inodesFree: 2m
    pid.available: 2m
  evictionMaxPodGracePeriod: 60
```

### Pod Density

By default, the number of pods on a node is limited by both the number of networking interfaces (ENIs) that may be attached to an instance type and the number of IP addresses that can be assigned to each ENI. See [IP addresses per network interface per instance type](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html#AvailableIpPerENI) for a more detailed information on these instance types’ limits.

## spec.amiFamily

AMIFamily dictates the default bootstrapping logic for nodes provisioned through this `EC2NodeClass`. An `amiFamily` is only required if you don’t specify a `spec.amiSelectorTerms.alias` object. For example, if you specify `alias: al2023@v20240807`, the `amiFamily` is implicitly `AL2023`.

AMIFamily does not impact which AMI is discovered, only the UserData generation and default BlockDeviceMappings. To automatically discover EKS optimized AMIs, use the new [`alias` field in amiSelectorTerms](https://karpenter.sh/docs/concepts/nodeclasses/#specamiselectorterms).

### AL2

```bash
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash -xe
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
/etc/eks/bootstrap.sh 'test-cluster' --apiserver-endpoint 'https://test-cluster' --b64-cluster-ca 'ca-bundle' \
--dns-cluster-ip '10.100.0.10' \
--use-max-pods false \
--kubelet-extra-args '--node-labels=karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=test  --max-pods=110'
--//--
```

### AL2023

```text
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: application/node.eks.aws

# Karpenter Generated NodeConfig
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    name: test-cluster
    apiServerEndpoint: https://example.com
    certificateAuthority: ca-bundle
    cidr: 10.100.0.0/16
  kubelet:
    config:
      maxPods: 110
    flags:
      - --node-labels=karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=test

--//--
```

### Bottlerocket

```toml
[settings]
[settings.kubernetes]
api-server = 'https://test-cluster'
cluster-certificate = 'ca-bundle'
cluster-name = 'test-cluster'
cluster-dns-ip = '10.100.0.10'
max-pods = 110

[settings.kubernetes.node-labels]
'karpenter.sh/capacity-type' = 'on-demand'
'karpenter.sh/nodepool' = 'test'
```

### Windows2019

```powershell
<powershell>
[string]$EKSBootstrapScriptFile = "$env:ProgramFiles\Amazon\EKS\Start-EKSBootstrap.ps1"
& $EKSBootstrapScriptFile -EKSClusterName 'test-cluster' -APIServerEndpoint 'https://test-cluster' -Base64ClusterCA 'ca-bundle' -KubeletExtraArgs '--node-labels="karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=test" --max-pods=110' -DNSClusterIP '10.100.0.10'
</powershell>
```

### Windows2022

```powershell
<powershell>
[string]$EKSBootstrapScriptFile = "$env:ProgramFiles\Amazon\EKS\Start-EKSBootstrap.ps1"
& $EKSBootstrapScriptFile -EKSClusterName 'test-cluster' -APIServerEndpoint 'https://test-cluster' -Base64ClusterCA 'ca-bundle' -KubeletExtraArgs '--node-labels="karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=test" --max-pods=110' -DNSClusterIP '10.100.0.10'
</powershell>
```

### Custom

The `Custom` AMIFamily ships without any default userData to allow you to configure custom bootstrapping for control planes or images that don’t support the default methods from the other families. For this AMIFamily, kubelet must add the taint `karpenter.sh/unregistered:NoExecute` via the `--register-with-taints` flag ([flags](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/#options)) or the KubeletConfiguration spec ([options](https://kubernetes.io/docs/reference/config-api/kubelet-config.v1/#kubelet-config-k8s-io-v1-CredentialProviderConfig) and [docs](https://kubernetes.io/docs/tasks/administer-cluster/kubelet-config-file/)). Karpenter will fail to register nodes that do not have this taint.

## spec.subnetSelectorTerms

Subnet Selector Terms allow you to specify selection logic for a set of subnet options that Karpenter can choose from when launching an instance from the `EC2NodeClass`. Karpenter discovers subnets through the `EC2NodeClass` using ids or [tags](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html). When launching nodes, a subnet is automatically chosen that matches the desired zone. If multiple subnets exist for a zone, the one with the most available IP addresses will be used.

This selection logic is modeled as terms, where each term contains multiple conditions that must all be satisfied for the selector to match. Effectively, all requirements within a single term are ANDed together. It’s possible that you may want to select on two different subnets that have unrelated requirements. In this case, you can specify multiple terms which will be ORed together to form your selection logic. The example below shows how this selection logic is fulfilled.

#### Examples

Select all with a specified tag key:

Select by name and tag (all criteria must match):

Select using multiple tag terms:

Select using wildcards:

Select using ids:

## spec.securityGroupSelectorTerms

Security Group Selector Terms allow you to specify selection logic for all security groups that will be attached to an instance launched from the `EC2NodeClass`. The security group of an instance is comparable to a set of firewall rules.[EKS creates at least two security groups by default](https://docs.aws.amazon.com/eks/latest/userguide/sec-group-reqs.html).

This selection logic is modeled as terms, where each term contains multiple conditions that must all be satisfied for the selector to match. Effectively, all requirements within a single term are ANDed together. It’s possible that you may want to select on two different security groups that have unrelated requirements. In this case, you can specify multiple terms which will be ORed together to form your selection logic. The example below shows how this selection logic is fulfilled.

#### Examples

Select all assigned to a cluster:

Select all with a specified tag key:

Select by name and tag (all criteria must match):

Select using multiple tag terms:

Select by name using a wildcard:

Select using ids:

## spec.role

`Role` is an optional field and tells Karpenter which IAM identity nodes should assume. You must specify one of `role` or `instanceProfile` when creating a Karpenter `EC2NodeClass`. If using the [Karpenter Getting Started Guide](https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/) to deploy Karpenter, you can use the `KarpenterNodeRole-$CLUSTER_NAME` role provisioned by that process.

```yaml
spec:
  role: "KarpenterNodeRole-$CLUSTER_NAME"
```

`InstanceProfile` is an optional field and tells Karpenter which IAM identity nodes should assume. You must specify one of `role` or `instanceProfile` when creating a Karpenter `EC2NodeClass`. If you use the `instanceProfile` field instead of `role`, Karpenter will not manage the InstanceProfile on your behalf; instead, it expects that you have pre-provisioned an IAM instance profile and assigned it a role.

You can provision and assign a role to an IAM instance profile using [CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-instanceprofile.html) or by using the [`aws iam create-instance-profile`](https://docs.aws.amazon.com/cli/latest/reference/iam/create-instance-profile.html) and [`aws iam add-role-to-instance-profile`](https://docs.aws.amazon.com/cli/latest/reference/iam/add-role-to-instance-profile.html) commands in the CLI.

## spec.amiSelectorTerms

AMI Selector Terms are **required** and are used to configure AMIs for Karpenter to use. AMIs are discovered through alias, id, owner, name, and [tags](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html).

This selection logic is modeled as terms, where each term contains multiple conditions that must all be satisfied for the selector to match. Effectively, all requirements within a single term are ANDed together. It’s possible that you may want to select on two different AMIs that have unrelated requirements. In this case, you can specify multiple terms which will be ORed together to form your selection logic. The example below shows how this selection logic is fulfilled.

An `alias` term can be used to select EKS-optimized AMIs. An `alias` is formatted as `family@version`. Family can be one of the following values:

- `al2`
- `al2023`
- `bottlerocket`
- `windows2019`
- `windows2022`

The version string can be set to `latest`, or pinned to a specific AMI using the format of that AMI’s GitHub release tags. For example, AL2 and AL2023 use dates for their release, so they can be pinned as follows:

```yaml
alias: al2023@v20240703
```

Bottlerocket uses a semantic version for their releases. You can pin bottlerocket as follows:

```yaml
alias: bottlerocket@v1.20.4
```

The Windows family does not support pinning, so only `latest` is supported.

The following commands can be used to determine the versions availble for an alias in your region:

To select an AMI by name, use the `name` field in the selector term. To select an AMI by id, use the `id` field in the selector term. To select AMIs that are not owned by `amazon` or the account that Karpenter is running in, use the `owner` field - you can use a combination of account aliases (e.g. `self` `amazon`, `your-aws-account-name`) and account IDs.

If owner is not set for `name`, it defaults to `self,amazon`, preventing Karpenter from inadvertently selecting an AMI that is owned by a different account. Tags don’t require an owner as tags can only be discovered by the user who created them.

#### Examples

Select by AMI family and version:

Select all with a specified tag:

Select by name:

Select by `Name` tag:

Select by name and owner:

Select by name using a wildcard:

Select by all under an owner:

Specify using ids:

Specify using custom ssm parameter name or ARN:

## spec.capacityReservationSelectorTerms

**Feature State:** [Beta](https://karpenter.sh/docs/reference/settings/#feature-gates)

Capacity Reservation Selector Terms allow you to select [on-demand capacity reservations](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-reservations.html) (ODCRs), which will be made available to NodePools which select the given EC2NodeClass. Karpenter will prioritize utilizing the capacity in these reservations before falling back to on-demand and spot. Capacity reservations can be discovered using ids, tags, or instance match criteria.

This selection logic is modeled as terms. A term can specify an ID, a set of tags, or instance match criteria to select against. When specifying tags, it will select all capacity reservations accessible from the account with matching tags. When specifying instance match criteria, it selects reservations by their matching behavior: `open` (matches all compatible instances) or `targeted` (matches only explicitly targeted instances). This can be further restricted by specifying an owner ID.

For more information on utilizing ODCRs with Karpenter, refer to the [Utilizing ODCRs Task](https://karpenter.sh/docs/tasks/odcrs/).

#### Examples

Select the reservations with the given IDs:

Select the reservations by tags:

Select by tags and owner ID:

Select by instance match criteria:

Select by instance match criteria and tags:

## spec.tags

Karpenter adds tags to all resources it creates, including EC2 Instances, EBS volumes, and Launch Templates. The default set of tags are listed below.

```yaml
Name: <node-name>
karpenter.sh/nodeclaim: <nodeclaim-name>
karpenter.sh/nodepool: <nodepool-name>
karpenter.k8s.aws/ec2nodeclass: <ec2nodeclass-name>
kubernetes.io/cluster/<cluster-name>: owned
eks:eks-cluster-name: <cluster-name>
```

Additional tags can be added in the tags section, which will be merged with the default tags specified above.

```yaml
spec:
  tags:
    InternalAccountingTag: 1234
    dev.corp.net/app: Calculator
    dev.corp.net/team: MyTeam
```

Control the exposure of [Instance Metadata Service](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html) on EC2 Instances launched by this EC2NodeClass using a generated launch template.

Refer to [recommended, security best practices](https://aws.github.io/aws-eks-best-practices/security/docs/iam/#restrict-access-to-the-instance-profile-assigned-to-the-worker-node) for limiting exposure of Instance Metadata and User Data to pods.

If metadataOptions are omitted from this EC2NodeClass, the following default settings are applied:

```yaml
spec:
  metadataOptions:
    httpEndpoint: enabled
    httpProtocolIPv6: disabled
    httpPutResponseHopLimit: 1
    httpTokens: required
```

## spec.blockDeviceMappings

The `blockDeviceMappings` field in an `EC2NodeClass` can be used to control the [Elastic Block Storage (EBS) volumes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html#instance-block-device-mapping) that Karpenter attaches to provisioned nodes. Karpenter uses default block device mappings for the AMIFamily specified. For example, the `Bottlerocket` AMI Family defaults with two block device mappings, one for Bottlerocket’s control volume and the other for container resources such as images and logs.

```yaml
spec:
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 100Gi
        volumeType: gp3
        iops: 10000
        encrypted: true
        kmsKeyID: "1234abcd-12ab-34cd-56ef-1234567890ab"
        deleteOnTermination: true
        throughput: 125
        snapshotID: snap-0123456789
        volumeInitializationRate: 100
```

The following blockDeviceMapping defaults are used for each `AMIFamily` if no `blockDeviceMapping` overrides are specified in the `EC2NodeClass`

### AL2

```yaml
spec:
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 20Gi
        volumeType: gp3
        encrypted: true
```

### AL2023

```yaml
spec:
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 20Gi
        volumeType: gp3
        encrypted: true
```

### Bottlerocket

```yaml
spec:
  blockDeviceMappings:
    # Root device
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 4Gi
        volumeType: gp3
        encrypted: true
    # Data device: Container resources such as images and logs
    - deviceName: /dev/xvdb
      ebs:
        volumeSize: 20Gi
        volumeType: gp3
        encrypted: true
```

### Windows2019/Windows2022

```yaml
spec:
  blockDeviceMappings:
    - deviceName: /dev/sda1
      ebs:
        volumeSize: 50Gi
        volumeType: gp3
        encrypted: true
```

### Custom

The `Custom` AMIFamily ships without any default `blockDeviceMappings`.

## spec.instanceStorePolicy

The `instanceStorePolicy` field controls how [instance-store](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html) volumes are handled. By default, Karpenter and Kubernetes will simply ignore them.

### RAID0

If you intend to use these volumes for faster node ephemeral-storage, set `instanceStorePolicy` to `RAID0`:

```yaml
spec:
  instanceStorePolicy: RAID0
```

This will set the allocatable ephemeral-storage of each node to the total size of the instance-store volume(s). This configuration is likely to be useful for workloads that leverage dense storage instance types or require the low latency from instance-stores that are nvme ssd based.

The disks must be formatted & mounted in a RAID0 and be the underlying filesystem for the Kubelet & Containerd. Even if you already configure your volumes with RAID0, Karpenter won’t recognize this by default unless you set the `instanceStorePolicy` to `RAID0`. Without this, scheduling workloads that depend on ephemeral-storage from the instance-stores may result in a deadlock due to insufficient storage.

Instructions for each AMI family are listed below:

#### AL2

On AL2, Karpenter automatically configures the disks through an additional boostrap argument (`--local-disks raid0`). The device name is `/dev/md/0` and its mount point is `/mnt/k8s-disks/0`. You should ensure any additional disk setup does not interfere with these.

#### AL2023

On AL2023, Karpenter automatically configures the disks via the generated `NodeConfig` object. Like AL2, the device name is `/dev/md/0` and its mount point is `/mnt/k8s-disks/0`. You should ensure any additional disk setup does not interfere with these.

#### Bottlerocket

On Bottlerocket, Karpenter automatically configures the disks by adding the required bootstrap commands to the settings. The ephemeral storage configuration is handled automatically, so you should not manually configure ephemeral storage settings in your userData.

#### Others

For all other AMI families, you must configure the disks yourself. Check out the [`setup-local-disks`](https://github.com/awslabs/amazon-eks-ami/blob/main/templates/shared/runtime/bin/setup-local-disks) script in [amazon-eks-ami](https://github.com/awslabs/amazon-eks-ami) to see how this is done for AL2.

## spec.userData

You can control the UserData that is applied to your worker nodes via this field. This allows you to run custom scripts or pass-through custom configuration to Karpenter instances on start-up.

```yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: bottlerocket-example
spec:
  ...
  amiFamily: Bottlerocket
  userData:  |
    [settings.kubernetes]
    "kube-api-qps" = 30
    "shutdown-grace-period" = "30s"
    "shutdown-grace-period-for-critical-pods" = "30s"
    [settings.kubernetes.eviction-hard]
    "memory.available" = "20%"
```

This example adds SSH keys to allow remote login to the node (replace *my-authorized\_keys* with your public key file):

```yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: al2-example
spec:
  ...
  amiFamily: AL2
  userData: |
    #!/bin/bash
    mkdir -p ~ec2-user/.ssh/
    touch ~ec2-user/.ssh/authorized_keys
    cat >> ~ec2-user/.ssh/authorized_keys <<EOF
    {{ insertFile "../my-authorized_keys" | indent 4  }}
    EOF
    chmod -R go-w ~ec2-user/.ssh/authorized_keys
    chown -R ec2-user ~ec2-user/.ssh
```

Alternatively, you can save the [key in your SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-create-console.html) and use the get-parameter command mentioned below to retrieve the key for authorized\_keys.

```
aws ssm get-parameter --name "<parameter-name>" --region <region> --with-decryption --query "Parameter.Value" --output text > /home/ec2-user/.ssh/authorized_keys
```

For more examples on configuring fields for different AMI families, see the [examples here](https://github.com/aws/karpenter/blob/main/examples/v1).

Karpenter will merge the userData you specify with the default userData for that AMIFamily. See the [AMIFamily](https://karpenter.sh/docs/concepts/nodeclasses/#specamifamily) section for more details on these defaults. View the sections below to understand the different merge strategies for each AMIFamily.

### AL2

- Your UserData can be in the format.
- Karpenter will transform your custom user-data as a MIME part, if necessary, and then merge a final MIME part to the end of your UserData parts which will bootstrap the worker node. Karpenter will have full control over all the parameters being passed to the bootstrap script.
	- Karpenter will continue to set MaxPods, ClusterDNS and all other parameters defined in `spec.kubeletConfiguration` as before.

Consider the following example to understand how your custom UserData will be merged -

#### Passed-in UserData (bash)

```bash
#!/bin/bash
echo "Running custom user data script (bash)"
```

#### Merged UserData (bash)

```bash
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash
echo "Running custom user data script (bash)"

--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash -xe
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
/etc/eks/bootstrap.sh 'test-cluster' --apiserver-endpoint 'https://test-cluster' --b64-cluster-ca 'ca-bundle' \
--use-max-pods false \
--kubelet-extra-args '--node-labels=karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=test  --max-pods=110'
--//--
```

#### Passed-in UserData (MIME)

```bash
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="BOUNDARY"

--BOUNDARY
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash
echo "Running custom user data script (mime)"

--BOUNDARY--
```

#### Merged UserData (MIME)

```bash
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash
echo "Running custom user data script (mime)"

--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash -xe
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
/etc/eks/bootstrap.sh 'test-cluster' --apiserver-endpoint 'https://test-cluster' --b64-cluster-ca 'ca-bundle' \
--use-max-pods false \
--kubelet-extra-args '--node-labels=karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=test  --max-pods=110'
--//--
```

### AL2023

- Your UserData may be in one of three formats: a , a NodeConfig YAML / JSON string, or a shell script.
- Karpenter will transform your custom UserData into a MIME part, if necessary, and then create a MIME multi-part archive. This archive will consist of a generated NodeConfig, containing Karpenter’s default values, followed by the transformed custom UserData. For more information on the NodeConfig spec, refer to the [AL2023 EKS Optimized AMI docs](https://awslabs.github.io/amazon-eks-ami/nodeadm/doc/examples/).

#### Passed-in UserData (NodeConfig)

```yaml
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  kubelet:
    config:
      maxPods: 42
```

#### Merged UserData (NodeConfig)

```text
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: application/node.eks.aws

apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  kubelet:
    config:
      maxPods: 42

--//
Content-Type: application/node.eks.aws

# Karpenter Generated NodeConfig
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    apiServerEndpoint: https://test-cluster
    certificateAuthority: cluster-ca
    cidr: 10.100.0.0/16
    name: test-cluster
  kubelet:
    config:
      clusterDNS:
      - 10.100.0.10
      maxPods: 118
    flags:
    - --node-labels="karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=default"

--//--
```

#### Passed-in UserData (bash)

```shell
#!/bin/bash
echo "Hello, AL2023!"
```

#### Merged UserData (bash)

```text
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash
echo "Hello, AL2023!"

--//
Content-Type: application/node.eks.aws

# Karpenter Generated NodeConfig
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    apiServerEndpoint: https://test-cluster
    certificateAuthority: cluster-ca
    cidr: 10.100.0.0/16
    name: test-cluster
  kubelet:
    config:
      clusterDNS:
      - 10.100.0.10
      maxPods: 118
    flags:
    - --node-labels="karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=default"

--//--
```

#### Passed-in UserData (MIME)

```text
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash
echo "Hello, AL2023!"

--//
Content-Type: application/node.eks.aws

apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  kubelet:
    config:
      maxPods: 42
--//
```

#### Merged UserData (MIME)

```text
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="//"

--//
Content-Type: application/node.eks.aws

apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  kubelet:
    config:
      maxPods: 42
--//
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash
echo "Hello, AL2023!"

--//
Content-Type: application/node.eks.aws

# Karpenter Generated NodeConfig
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    apiServerEndpoint: https://test-cluster
    certificateAuthority: cluster-ca
    cidr: 10.100.0.0/16
    name: test-cluster
  kubelet:
    config:
      clusterDNS:
      - 10.100.0.10
      maxPods: 118
    flags:
    - --node-labels="karpenter.sh/capacity-type=on-demand,karpenter.sh/nodepool=default"

--//--
```

### Bottlerocket

- Your UserData must be valid TOML.
- Unknown TOML fields will be ignored when the final merged UserData is generated by Karpenter.

Consider the following example to understand how your custom UserData settings will be merged in.

#### Passed-in UserData

```toml
[settings.kubernetes.eviction-hard]
"memory.available" = "12%"
[settings.kubernetes]
"unknown-setting" = "unknown"
[settings.kubernetes.node-labels]
'field.controlled.by/karpenter' = 'will-be-overridden'
```

#### Merged UserData

```toml
[settings]
[settings.kubernetes]
api-server = 'https://cluster'
cluster-certificate = 'ca-bundle'
cluster-name = 'cluster'

[settings.kubernetes.node-labels]
'karpenter.sh/capacity-type' = 'on-demand'
'karpenter.sh/nodepool' = 'default'

[settings.kubernetes.node-taints]

[settings.kubernetes.eviction-hard]
'memory.available' = '12%%'
```

#### Device ownership in Bottlerocket

Bottlerocket `v1.30.0+` supports device ownership using the [security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) provided in the Kubernetes specfile. To enable this, you will need the following user-data configurations:

```toml
[settings]
[settings.kubernetes]
device-ownership-from-security-context = true
```

This allows the container to take ownership of devices allocated to the pod via device-plugins based on the `runAsUser` and `runAsGroup` values provided in the spec. For more details on this, see the [Kubernetes documentation](https://kubernetes.io/blog/2021/11/09/non-root-containers-and-devices/)

This setting helps you enable Neuron workloads on Bottlerocket instances. See [Accelerators/GPU Resources](https://karpenter.sh/docs/concepts/scheduling/#acceleratorsgpu-resources) for more details.

### Windows2019/Windows2022

- Your UserData must be specified as PowerShell commands.
- The UserData specified will be prepended to a Karpenter managed section that will bootstrap the kubelet.
- Karpenter will continue to set ClusterDNS and all other parameters defined in spec.kubeletConfiguration as before.

Consider the following example to understand how your custom UserData settings will be merged in.

#### Passed-in UserData

```powershell
Write-Host "Running custom user data script"
```

#### Merged UserData

```powershell
<powershell>
Write-Host "Running custom user data script"
[string]$EKSBootstrapScriptFile = "$env:ProgramFiles\Amazon\EKS\Start-EKSBootstrap.ps1"
& $EKSBootstrapScriptFile -EKSClusterName 'test-cluster' -APIServerEndpoint 'https://test-cluster' -Base64ClusterCA 'ca-bundle' -KubeletExtraArgs '--node-labels="karpenter.sh/capacity-type=spot,karpenter.sh/nodepool=windows2022" --max-pods=110' -DNSClusterIP '10.0.100.10'
</powershell>
```

### Custom

- No merging is performed, your UserData must perform all setup required of the node to allow it to join the cluster.
- Custom UserData must meet the following requirements to work correctly with Karpenter:
	- It must ensure the node is registered with the `karpenter.sh/unregistered:NoExecute` taint (via kubelet configuration field `registerWithTaints`)
	- It must set kubelet config options to match those configured in `spec.kubelet`

## spec.detailedMonitoring

Enabling detailed monitoring controls the [EC2 detailed monitoring](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-cloudwatch-new.html) feature. If you enable this option, the Amazon EC2 console displays monitoring graphs with a 1-minute period for the instances that Karpenter launches.

```yaml
spec:
  detailedMonitoring: true
```

## spec.associatePublicIPAddress

You can explicitly set `AssociatePublicIPAddress: false` when you are only launching into private subnets. Previously, Karpenter auto-set `associatePublicIPAddress` on the primary ENI to false if a user’s subnet options were all private subnets. This value is a boolean field that controls whether instances created by Karpenter for this EC2NodeClass will have an associated public IP address. This overrides the `MapPublicIpOnLaunch` setting applied to the subnet the node is launched in. If this field is not set, the `MapPublicIpOnLaunch` field will be respected.

## spec.ipPrefixCount

This value is a integer field that controls how many ip prefixes will be assigned to `NodeClaim`. See the [EC2 Launch Template Network Interface Spec](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-ec2-launchtemplate-networkinterface.html) for more information. Sets ipv4PrefixCount if you are using an IPv4 Cluster, or ipv6PrefixCount if you are using IPv6.

## status.subnets

[`status.subnets`](https://karpenter.sh/docs/concepts/nodeclasses/#statussubnets) contains the resolved `id` and `zone` of the subnets that were selected by the [`spec.subnetSelectorTerms`](https://karpenter.sh/docs/concepts/nodeclasses/#specsubnetselectorterms) for the node class. The subnets will be sorted by the available IP address count in decreasing order.

#### Examples

## status.securityGroups

[`status.securityGroups`](https://karpenter.sh/docs/concepts/nodeclasses/#statussecuritygroups) contains the resolved `id` and `name` of the security groups that were selected by the [`spec.securityGroupSelectorTerms`](https://karpenter.sh/docs/concepts/nodeclasses/#specsecuritygroupselectorterms) for the node class. The subnets will be sorted by the available IP address count in decreasing order.

#### Examples

## status.amis

[`status.amis`](https://karpenter.sh/docs/concepts/nodeclasses/#statusamis) contains the resolved `id`, `name`, `requirements`, and the `deprecated` status of either the default AMIs for the [`spec.amiFamily`](https://karpenter.sh/docs/concepts/nodeclasses/#specamifamily) or the AMIs selected by the [`spec.amiSelectorTerms`](https://karpenter.sh/docs/concepts/nodeclasses/#specamiselectorterms) if this field is specified. The `deprecated` status will be shown for resolved AMIs that are deprecated.

#### Examples

AMIs resolved with an AL2 alias:

AMIs resolved from tags:

## status.capacityReservations

[`status.capacityReservations`](https://karpenter.sh/docs/concepts/nodeclasses/#statuscapacityreservations) contains the following information for each resolved capacity reservation:

| Field | Example | Description |
| --- | --- | --- |
| `availabilityZone` | `us-east-1a` | The availability zone the capacity reservation is available in |
| `id` | `cr-56fac701cc1951b03` | The ID of the capacity reservation |
| `instanceMatchCriteria` | `open` | The instanceMatchCriteria for the capacity reservation. Can be `open` or `targeted`. |
| `instanceType` | `m5.large` | The EC2 instance type of the capacity reservation |
| `ownerID` | `459763720645` | The account ID that owns the capacity reservation |
| `reservationType` | `default` | The type of the capacity reservation. Can be `default` or `capacity-block`. |
| `state` | `active` | The state of the capacity reservation. Can be `active` or `expiring`. |

#### Examples

```yaml
status:
  capacityReservations:
  - availabilityZone: us-west-2a
    id: cr-01234567890123456
    instanceMatchCriteria: targeted
    instanceType: g6.48xlarge
    ownerID: "012345678901"
    reservationType: capacity-block
    state: expiring
  - availabilityZone: us-west-2c
    id: cr-12345678901234567
    instanceMatchCriteria: open
    instanceType: g6.48xlarge
    ownerID: "98765432109"
    reservationType: default
    state: active
```

[`status.instanceProfile`](https://karpenter.sh/docs/concepts/nodeclasses/#statusinstanceprofile) contains the resolved instance profile generated by Karpenter from the [`spec.role`](https://karpenter.sh/docs/concepts/nodeclasses/#specrole)

```yaml
spec:
  role: "KarpenterNodeRole-${CLUSTER_NAME}"
status:
  instanceProfile: "${CLUSTER_NAME}-0123456778901234567789"
```

## status.conditions

[`status.conditions`](https://karpenter.sh/docs/concepts/nodeclasses/#statusconditions) indicates EC2NodeClass readiness. This will be `Ready` when Karpenter successfully discovers AMIs, Instance Profile, Subnets, Cluster CIDR (AL2023 only) and SecurityGroups for the EC2NodeClass.

NodeClasses have the following status conditions:

| Condition Type | Description |
| --- | --- |
| SubnetsReady | Subnets are discovered. |
| SecurityGroupsReady | Security Groups are discovered. |
| InstanceProfileReady | Instance Profile is discovered. |
| AMIsReady | AMIs are discovered. |
| Ready | Top level condition that indicates if the nodeClass is ready. If any of the underlying conditions is `False` then this condition is set to `False` and `Message` on the condition indicates the dependency that was not resolved. |

If a NodeClass is not ready, NodePools that reference it through their `nodeClassRef` will not be considered for scheduling.

Last modified January 15, 2026: [docs: update for new release version (#8849) (44c3088)](https://github.com/aws/karpenter-provider-aws/commit/44c308875455fb50d011552cda0bc0b1c74d9aa5)