---
hide:
  - tags
  #- navigation
tags:
  - Crossplane
  - Komoplane
todo:
  - Precise to use namespaced scopped resources with crossplane 2.0 and explain why
youtube:
  - https://www.youtube.com/watch?v=yrj4lmScKHQ
  - https://www.youtube.com/watch?v=eEcgn_gU3SM
github:
  - https://github.com/akuity/awesome-argo?tab=readme-ov-file#ecosystem-projects # search crossplane
---





![](/assets/images/crossplane/image.png)

## Install Crossplane

!!! Note "Install Crossplane using the Helm chart."

    Add the Crossplane Helm repository 

    ```shell hl_lines="1" title="Add the Crossplane stable repository with the helm repo add command."
    helm repo add crossplane-stable https://charts.crossplane.io/stable
    "crossplane-stable" has been added to your repositories
    ```

    ```shell hl_lines="1" title="Update the local Helm chart cache with helm repo update."
    helm repo update
    Hang tight while we grab the latest from your chart repositories...
    ...Successfully got an update from the "crossplane-stable" chart repository
    Update Complete. ⎈Happy Helming!⎈
    ```

    ```shell hl_lines="1" title="Install the Crossplane Helm chart."
    helm search repo crossplane
    NAME                            CHART VERSION   APP VERSION     DESCRIPTION
    crossplane-stable/crossplane    2.1.1           2.1.1           Crossplane is an open source Kubernetes add-on ...
    ```

    !!! Tips
        View the changes Crossplane makes to your cluster with the `helm install --dry-run=client --debug` options.          
        Helm shows what configurations it applies without making changes to the Kubernetes cluster.
        ```shell hl_lines="1"
        helm install crossplane crossplane-stable/crossplane --namespace crossplane-system --create-namespace --dry-run=client --debug
        ```

    ```shell hl_lines="1" title="Crossplane creates and installs into the crossplane-system namespace." 
    helm install crossplane crossplane-stable/crossplane --namespace crossplane-system --create-namespace
    NAME: crossplane
    LAST DEPLOYED: Sun Nov 16 19:22:29 2025
    NAMESPACE: crossplane-system
    STATUS: deployed
    REVISION: 1
    TEST SUITE: None
    NOTES:
    Release: crossplane

    Chart Name: crossplane
    Chart Description: Crossplane is an open source Kubernetes add-on that enables platform teams to assemble infrastructure from multiple vendors, and expose higher level self-service APIs for application teams to consume.
    Chart Version: 2.1.1
    Chart Application Version: 2.1.1

    Kube Version: v1.34.0
    ```

    ??? Info "Check resources installed"

        ```shell hl_lines="1" title="View the installed Crossplane pods."
        kubectl get pods -n crossplane-system
        NAME                                       READY   STATUS    RESTARTS   AGE
        crossplane-6896f6fbff-rt7fz                1/1     Running   0          2m19s
        crossplane-rbac-manager-65f6d66c76-tcm5r   1/1     Running   0          2m19s
        ```

        ```shell hl_lines="1" title="View the installed Crossplane CRDs"
        kubectl get crds | grep crossplane
        clusterusages.protection.crossplane.io                          2025-11-16T18:22:34Z
        compositeresourcedefinitions.apiextensions.crossplane.io        2025-11-16T18:22:34Z
        compositionrevisions.apiextensions.crossplane.io                2025-11-16T18:22:34Z
        compositions.apiextensions.crossplane.io                        2025-11-16T18:22:34Z
        configurationrevisions.pkg.crossplane.io                        2025-11-16T18:22:34Z
        configurations.pkg.crossplane.io                                2025-11-16T18:22:34Z
        cronoperations.ops.crossplane.io                                2025-11-16T18:22:34Z
        deploymentruntimeconfigs.pkg.crossplane.io                      2025-11-16T18:22:34Z
        environmentconfigs.apiextensions.crossplane.io                  2025-11-16T18:22:34Z
        functionrevisions.pkg.crossplane.io                             2025-11-16T18:22:34Z
        functions.pkg.crossplane.io                                     2025-11-16T18:22:34Z
        imageconfigs.pkg.crossplane.io                                  2025-11-16T18:22:34Z
        locks.pkg.crossplane.io                                         2025-11-16T18:22:34Z
        managedresourceactivationpolicies.apiextensions.crossplane.io   2025-11-16T18:22:34Z
        managedresourcedefinitions.apiextensions.crossplane.io          2025-11-16T18:22:34Z
        operations.ops.crossplane.io                                    2025-11-16T18:22:34Z
        providerrevisions.pkg.crossplane.io                             2025-11-16T18:22:34Z
        providers.pkg.crossplane.io                                     2025-11-16T18:22:34Z
        usages.apiextensions.crossplane.io                              2025-11-16T18:22:34Z
        usages.protection.crossplane.io                                 2025-11-16T18:22:34Z
        watchoperations.ops.crossplane.io                               2025-11-16T18:22:34Z
        ```

    !!! Question "**Documentation officielle**"
        [Documentation Crossplane](https://docs.crossplane.io/v2.1/)

---

## Install Providers

!!! note "test"

    The following manifest can be used to install this package in your control plane. After you have connected to your control plane run kubectl apply -f after copying the following into a local file.

    ```shell hl_lines="1" title="provider-aws-iam.yaml"
    apiVersion: pkg.crossplane.io/v1
    kind: Provider
    metadata:
      name: upbound-provider-aws-iam
    spec:
      package: xpkg.upbound.io/upbound/provider-aws-iam:v2.2.0
    ```

    ```shell hl_lines="1" title="Apply the providers for the resources IAM"
    kubectl apply -f provider-aws-s3.yaml
    provider.pkg.crossplane.io/upbound-provider-aws-s3 created
    ```

    !!! info "Check resources installed"
        ```shell hl_lines="1" title="View the installed Crossplane providers."
        kubectl get providers
        NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
        upbound-provider-aws-s3       True        True      xpkg.upbound.io/upbound/provider-aws-s3:v2.2.0       2m30s
        upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v2.2.0   2m25s
        ```

        !!! info 
            All crossplane package has a dependency on provider-family-aws which will be automatically installed.

        ```shell hl_lines="1" title="View the installed Crossplane providers pods."
        kubectl get pods -n crossplane-system
        NAME                                                        READY   STATUS    RESTARTS   AGE
        crossplane-6896f6fbff-sn2x8                                 1/1     Running   0          12m
        crossplane-rbac-manager-65f6d66c76-76ffs                    1/1     Running   0          12m
        upbound-provider-aws-s3-dd62e217befa-85fffd899-qjpzj        1/1     Running   0          4m23s
        upbound-provider-family-aws-0e8a4558ea96-6bff6ccb65-f2x5s   1/1     Running   0          4m24s
        ```


    ??? Abstract "Documentation officiel"
        [https://marketplace.upbound.io/providers/upbound/provider-family-aws/v2.2.0](https://marketplace.upbound.io/providers/upbound/provider-family-aws/v2.2.0)

### Create an user with admin privilege

!!! Info

    ```shell title="aws-credentials.txt"
    [default]
    aws_access_key_id = XXXXXXXXXXXXXXXXXXXX
    aws_secret_access_key = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    ```

    ```shell hl_lines="1" title="Create secret from aws-credentials.txt"
    kubectl create secret generic aws-secret -n crossplane-system --from-file=creds=./aws-credentials.txt
    ```

    ```yaml hl_lines="1"
    ---
    apiVersion: aws.m.upbound.io/v1beta1
    kind: ProviderConfig
    metadata:
      name: default
    spec:
      credentials:
        source: Secret
        secretRef:
            namespace: crossplane-system
            name: aws-secret
            key: creds
    ```

## Create resources

!!! Info "Create bucket s3"

    ```yaml hl_lines="1"
    ---
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    metadata:
      name: app1-bucket-mathod
      namespace: crossplane-system
    spec:
      forProvider:
        region: eu-west-3
          tags:
            company: mathod
            project: app1
            environment: production
        providerConfigRef:
          name: default
    ```

## Import existing Resources


!!! INFO "Import existing resources into your control plane for Crossplane to manage"

    If you have resources that are already provisioned in a Provider,
    you can import them as managed resources and let Crossplane manage them.
    A managed resource's [`managementPolicies`]({{<ref "../managed-resources/managed-resources#managementpolicies">}})
    field enables importing external resources into Crossplane.

    ### Import resources in observe only mode

    Start by importing external resources with an `Observe` [management policy]({{<ref "../managed-resources/managed-resources#managementpolicies">}}).

    **Crossplane imports observe only resources but never changes or deletes the resources.**

    !!! Warning

        The managed resource `managementPolicies` option is a beta feature.

        The Provider determines support for management policies.
        Refer to the Provider's documentation to see if the Provider supports
        management policies.

### Apply the Observe management policy

1. Create a new managed resource matching the apiVersion and kind of the resource to import and add managementPolicies: `Observe` to the spec
For example, to import an AWS EC2 Instance, Create a new resource with the managementPolicies: `Observe` set.
2. Add the crossplane.io/external-name annotation for the resource. This name must match the ID inside the Provider.
For example, for an AWS EC2 Instance use the `Instance ID`, apply the crossplane.io/external-name annotation with the value `i-037556a7512bd1f4b`.
3. Create a name to use for the Kubernetes object. For example, name the Kubernetes object imported-ec2-instance.
4. If more than one resource inside the Provider shares the same name, identify the specific resource with a unique spec.forProvider field.
For example, only import the GCP SQL database in the us-central1 region.

```yaml linenums="1" title="imported-ec2-instance.yaml"
apiVersion: ec2.aws.m.upbound.io/v1beta1
kind: Instance
metadata:
  name: imported-ec2-instance
  annotations:
    crossplane.io/external-name: i-037556a7512bd1f4b
spec:
  managementPolicies: ["Observe"]
  forProvider:
    region: eu-west-3
  providerConfigRef:
    name: default
    kind: ProviderConfig 
```

!!! Warning 
    If u dont precise providerConfigRef it try to lookup for ClusterProviderConfig 



### Apply the managed resource

Apply the new managed resource. Crossplane syncs the status of the external
resource in the cloud with the newly created managed resource.

```yaml hl_lines="1" 
kubectl apply -f imported-ec2.yaml
instance.ec2.aws.m.upbound.io/imported-ec2-instance created
```

### View the discovered resource
Crossplane discovers the managed resource and populates the status.atProvider fields with the values from the external resource.

```yaml linenums="1"
apiVersion: ec2.aws.m.upbound.io/v1beta1
kind: Instance
metadata:
  annotations:
    crossplane.io/external-name: i-037556a7512bd1f4b
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"ec2.aws.m.upbound.io/v1beta1","kind":"Instance","metadata":{"annotations":{"crossplane.io/external-name":"i-037556a7512bd1f4b"},"name":"imported-ec2-instance","namespace":"crossplane-system"},"spec":{"forProvider":{"region":"eu-west-3"},"managementPolicies":["Observe"],"providerConfigRef":{"kind":"ProviderConfig","name":"default"}}}
  creationTimestamp: "2025-11-25T04:34:45Z"
  finalizers:
  - finalizer.managedresource.crossplane.io
  generation: 2
  name: imported-ec2-instance
  namespace: crossplane-system
  resourceVersion: "62176"
  uid: e0aecc43-1878-41ea-a58f-e9f2557f2a3e
spec:
  forProvider:
    region: eu-west-3
  initProvider: {}
  managementPolicies:
  - Observe
  providerConfigRef:
    kind: ProviderConfig
    name: default
status:
  atProvider:
    ami: ami-00769f46ca3bb4381
    arn: arn:aws:ec2:eu-west-3:478084574796:instance/i-037556a7512bd1f4b
    associatePublicIpAddress: false
    availabilityZone: eu-west-3c
    capacityReservationSpecification:
      capacityReservationPreference: open
      capacityReservationTarget: {}
    cpuOptions:
      amdSevSnp: ""
      coreCount: 1
      threadsPerCore: 2
    creditSpecification:
      cpuCredits: unlimited
    disableApiStop: false
    disableApiTermination: false
    ebsOptimized: true
    enclaveOptions:
      enabled: false
    getPasswordData: false
    hibernation: false
    hostId: ""
    iamInstanceProfile: ""
    id: i-037556a7512bd1f4b
    instanceInitiatedShutdownBehavior: stop
    instanceLifecycle: ""
    instanceMarketOptions: {}
    instanceState: stopped
    instanceType: t3.micro
    ipv6AddressCount: 0
    keyName: ""
    launchTemplate: {}
    maintenanceOptions:
      autoRecovery: default
    metadataOptions:
      httpEndpoint: enabled
      httpProtocolIpv6: disabled
      httpPutResponseHopLimit: 2
      httpTokens: required
      instanceMetadataTags: disabled
    monitoring: false
    outpostArn: ""
    passwordData: ""
    placementGroup: ""
    placementGroupId: ""
    placementPartitionNumber: 0
    primaryNetworkInterface:
      deleteOnTermination: true
      networkInterfaceId: eni-05970f9b52533b159
    primaryNetworkInterfaceId: eni-05970f9b52533b159
    privateDns: ip-172-31-42-191.eu-west-3.compute.internal
    privateDnsNameOptions:
      enableResourceNameDnsARecord: true
      enableResourceNameDnsAaaaRecord: false
      hostnameType: ip-name
    privateIp: 172.31.42.191
    publicDns: ""
    publicIp: ""
    region: eu-west-3
    rootBlockDevice:
      deleteOnTermination: true
      deviceName: /dev/xvda
      encrypted: false
      iops: 3000
      kmsKeyId: ""
      throughput: 125
      volumeId: vol-03fdca6cb6fd07a3f
      volumeSize: 8
      volumeType: gp3
    securityGroups:
    - launch-wizard-1
    sourceDestCheck: true
    spotInstanceRequestId: ""
    subnetId: subnet-0df5c09839230c14c
    tags:
      Name: app1
    tagsAll:
      Name: app1
    tenancy: default
    vpcSecurityGroupIds:
    - sg-0d69b6ea8692119d8
  conditions:
  - lastTransitionTime: "2025-11-25T04:34:51Z"
    observedGeneration: 2
    reason: ReconcileSuccess
    status: "True"
    type: Synced
  - lastTransitionTime: "2025-11-25T04:34:51Z"
    reason: Available
    status: "True"
    type: Ready
  - lastTransitionTime: "2025-11-25T04:34:51Z"
    reason: Success
    status: "True"
    type: LastAsyncOperation
```

## Control imported observe only resources

Crossplane can take active control of observe only imported resources by changing the managementPolicies after import.
Change the managementPolicies field of the managed resource to ["*"].
Copy any required parameter values from status.atProvider and provide them in spec.forProvider.

!!! Warning
    Manually copy the important `spec.atProvider` values to `spec.forProvider`.


```yaml linenums="1"
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  name: my-imported-database
  annotations:
    crossplane.io/external-name: my-external-database
spec:
  managementPolicies: ["*"]
  forProvider:
    databaseVersion: POSTGRES_14
    region: us-central1
    settings:
    - diskSize: 100
      tier: db-custom-4-26624
status:
  atProvider:
    databaseVersion: POSTGRES_14
    region: us-central1
    # Removed for brevity
    settings:
    - diskSize: 100
      tier: db-custom-4-26624
      # Removed for brevity
  conditions:
    - lastTransitionTime: "2023-02-22T07:16:51Z"
      reason: Available
      status: "True"
      type: Ready
    - lastTransitionTime: "2023-02-22T11:16:45Z"
      reason: ReconcileSuccess
      status: "True"
      type: Synced
```

Crossplane now fully manages the imported resource. Crossplane applies any
changes to the managed resource in the Provider's external resource.

We can by now specify new tag 

```yaml title="Apply new tag on your manifest"
apiVersion: ec2.aws.m.upbound.io/v1beta1
kind: Instance
metadata:
  name: imported-ec2-instance
  annotations:
    crossplane.io/external-name: i-037556a7512bd1f4b
spec:
  managementPolicies: ["*"]
  forProvider:
    region: eu-west-3
    tags:
      company: mathod
      project: app1
      environment: production
  providerConfigRef:
    name: default
    kind: ProviderConfig 
```

```yaml title="New tag on instance" hl_lines="41 45-46"
Name:         imported-ec2-instance
Namespace:    crossplane-system
Labels:       <none>
Annotations:  crossplane.io/external-name: i-037556a7512bd1f4b
API Version:  ec2.aws.m.upbound.io/v1beta1
Kind:         Instance
Metadata:
  Creation Timestamp:  2025-11-25T04:34:45Z
  Finalizers:
    finalizer.managedresource.crossplane.io
  Generation:        6
  Resource Version:  62949
  UID:               e0aecc43-1878-41ea-a58f-e9f2557f2a3e
Spec:
  For Provider:
    Ami:                ami-00769f46ca3bb4381
    Availability Zone:  eu-west-3c
    Capacity Reservation Specification:
      Capacity Reservation Preference:  open
    Credit Specification:
      Cpu Credits:  unlimited
    Ebs Optimized:  true
    Enclave Options:
    Instance Initiated Shutdown Behavior:  stop
    Instance Type:                         t3.micro
    Maintenance Options:
      Auto Recovery:  default
    Metadata Options:
      Http Endpoint:                enabled
      httpProtocolIpv6:             disabled
      Http Put Response Hop Limit:  2
      Http Tokens:                  required
      Instance Metadata Tags:       disabled
    Primary Network Interface:
      Network Interface Id:  eni-05970f9b52533b159
    Private Dns Name Options:
      Enable Resource Name Dns A Record:  true
      Hostname Type:                      ip-name
    Region:                               eu-west-3
    Tags:
      Company:                      mathod
      Crossplane - Kind:            instance.ec2.aws.m.upbound.io
      Crossplane - Name:            imported-ec2-instance
      Crossplane - Providerconfig:  default
      Environment:                  production
      Project:                      app1
    Tenancy:                        default
  Init Provider:
  Management Policies:
    *
  Provider Config Ref:
    Kind:  ProviderConfig
    Name:  default
Status:
  At Provider:
    Ami:                          ami-00769f46ca3bb4381
    Arn:                          arn:aws:ec2:eu-west-3:478084574796:instance/i-037556a7512bd1f4b
    Associate Public Ip Address:  false
    Availability Zone:            eu-west-3c
    Capacity Reservation Specification:
      Capacity Reservation Preference:  open
      Capacity Reservation Target:
    Cpu Options:
      Amd Sev Snp:       
      Core Count:        1
      Threads Per Core:  2
    Credit Specification:
      Cpu Credits:            unlimited
    Disable API Stop:         false
    Disable API Termination:  false
    Ebs Optimized:            true
    Enclave Options:
      Enabled:                             false
    Force Destroy:                         false
    Get Password Data:                     false
    Hibernation:                           false
    Host Id:                               
    Iam Instance Profile:                  
    Id:                                    i-037556a7512bd1f4b
    Instance Initiated Shutdown Behavior:  stop
    Instance Lifecycle:                    
    Instance Market Options:
    Instance State:    stopped
    Instance Type:     t3.micro
    ipv6AddressCount:  0
    Key Name:          
    Launch Template:
    Maintenance Options:
      Auto Recovery:  default
    Metadata Options:
      Http Endpoint:                enabled
      httpProtocolIpv6:             disabled
      Http Put Response Hop Limit:  2
      Http Tokens:                  required
      Instance Metadata Tags:       disabled
    Monitoring:                     false
    Outpost Arn:                    
    Password Data:                  
    Placement Group:                
    Placement Group Id:             
    Placement Partition Number:     0
    Primary Network Interface:
      Delete On Termination:       true
      Network Interface Id:        eni-05970f9b52533b159
    Primary Network Interface Id:  eni-05970f9b52533b159
    Private Dns:                   ip-172-31-42-191.eu-west-3.compute.internal
    Private Dns Name Options:
      Enable Resource Name Dns A Record:     true
      Enable Resource Name Dns Aaaa Record:  false
      Hostname Type:                         ip-name
    Private Ip:                              172.31.42.191
    Public Dns:                              
    Public Ip:                               
    Region:                                  eu-west-3
    Root Block Device:
      Delete On Termination:  true
      Device Name:            /dev/xvda
      Encrypted:              false
      Iops:                   3000
      Kms Key Id:             
      Throughput:             125
      Volume Id:              vol-03fdca6cb6fd07a3f
      Volume Size:            8
      Volume Type:            gp3
    Security Groups:
      launch-wizard-1
    Source Dest Check:         true
    Spot Instance Request Id:  
    Subnet Id:                 subnet-0df5c09839230c14c
    Tags:
      Name:                         app1
      Company:                      mathod
      Crossplane - Kind:            instance.ec2.aws.m.upbound.io
      Crossplane - Name:            imported-ec2-instance
      Crossplane - Providerconfig:  default
      Environment:                  production
      Project:                      app1
    Tags All:
      Name:                         app1
      Company:                      mathod
      Crossplane - Kind:            instance.ec2.aws.m.upbound.io
      Crossplane - Name:            imported-ec2-instance
      Crossplane - Providerconfig:  default
      Environment:                  production
      Project:                      app1
    Tenancy:                        default
    User Data Replace On Change:    false
    Vpc Security Group Ids:
      sg-0d69b6ea8692119d8
  Conditions:
    Last Transition Time:  2025-11-25T04:40:18Z
    Observed Generation:   6
    Reason:                ReconcileSuccess
    Status:                True
    Type:                  Synced
    Last Transition Time:  2025-11-25T04:34:51Z
    Reason:                Available
    Status:                True
    Type:                  Ready
    Last Transition Time:  2025-11-25T04:34:51Z
    Reason:                Success
    Status:                True
    Type:                  LastAsyncOperation
Events:
  Type    Reason                   Age                From                                                 Message
  ----    ------                   ----               ----                                                 -------
  Normal  UpdatedExternalResource  6s (x2 over 114s)  managed/ec2.aws.m.upbound.io/v1beta1, kind=instance  Successfully requested update of external resource
```

```
kubectl get instance
NAME                    SYNCED   READY   EXTERNAL-NAME         AGE
imported-ec2-instance   True     True    i-037556a7512bd1f4b   7m55s

kubectl get managed
NAME                                                  SYNCED   READY   EXTERNAL-NAME         AGE
instance.ec2.aws.m.upbound.io/imported-ec2-instance   True     True    i-037556a7512bd1f4b   8m25s

kubectl get instance.ec2.aws.m.upbound.io/imported-ec2-instance
NAME                    SYNCED   READY   EXTERNAL-NAME         AGE
imported-ec2-instance   True     True    i-037556a7512bd1f4b   8m31s

kubectl delete instance.ec2.aws.m.upbound.io/imported-ec2-instance
instance.ec2.aws.m.upbound.io "imported-ec2-instance" deleted from crossplane-system namespace
```
The instances as been removed from AWS since we deleted the resources !



##################################################################################################################

## Install Komoplane

!!! Note "Install Komoplane using the Helm chart."

    ```shell hl_lines="1" title="provider-aws-iam.yaml"
    helm repo add komodorio https://helm-charts.komodor.io
    "komodorio" has been added to your repositories
    ```

    ```shell hl_lines="1" title="Update the local Helm chart cache with helm repo update."
    helm repo update
    Hang tight while we grab the latest from your chart repositories...
    ...Successfully got an update from the "komodorio" chart repository
    ...Successfully got an update from the "crossplane-stable" chart repository
    Update Complete. ⎈Happy Helming!⎈
    ```

    ```shell hl_lines="1" title="Install the Komoplane Helm chart." 
    helm upgrade --install komoplane komodorio/komoplane
    Release "komoplane" does not exist. Installing it now.
    NAME: komoplane
    LAST DEPLOYED: Mon Nov 17 15:42:15 2025
    NAMESPACE: crossplane-system
    STATUS: deployed
    REVISION: 1
    NOTES:
    Thank you for installing Komoplane.
    Application can be accessed:
      * Within your cluster, at the following DNS name at port 8090:
    
        komoplane.crossplane-system.svc.cluster.local
    
      * From outside the cluster, run these commands in the same shell:
    
        export POD_NAME=$(kubectl get pods --namespace crossplane-system -l "app.kubernetes.io/name=komoplane,app.kubernetes.io/instance=komoplane" -o jsonpath="{.items[0].metadata.name}")
        export CONTAINER_PORT=$(kubectl get pod --namespace crossplane-system $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
        echo "Visit http://127.0.0.1:8090 to use your application"
        kubectl --namespace crossplane-system port-forward $POD_NAME 8090:$CONTAINER_PORT
    
    Visit our repo at:
    https://github.com/komodorio/komoplane
    ```

    ```shell hl_lines="1" title="Install the Komoplane Helm chart."
    helm install komoplane komodorio/komoplane --namespace komoplane --create-namespace
    ```

    ??? Abstract "Documentation officiel"
        [https://github.com/komodorio/komoplane](https://github.com/komodorio/komoplane)

## Conclusion

### En rapport avec cet article

### Liens utile
  - https://www.youtube.com/watch?v=jw8mMslpqOI
  - https://docs.crossplane.io/latest/guides/import-existing-resources/
  - https://docs.crossplane.io/v2.1/guides/upgrade-to-crossplane-v2/
  - https://docs.crossplane.io/v2.1/whats-new/