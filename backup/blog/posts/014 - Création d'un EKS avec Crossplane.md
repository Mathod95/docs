---
title: Création d'un EKS avec Crossplane
date: 2025-12-03
draft: true
categories:
  - Crossplane
  - AWS
tags:
  - Crossplane
  - Composition
  - EKS
  - Labs
todo:
  - You can find tutorial [here](https://youtu.be/mpfqPXfX6mg).
  - ajouter le repo quand il seras créer
source: 
  - https://github.com/antonputra/tutorials/tree/main/lessons/176
---

![](../../assets/images/crossplane/crossplane.svg)

## Introduction

Ce guide vous explique comment déployer un cluster EKS (Elastic Kubernetes Service) via crossplane depuis un cluster kind en local.

<!-- more -->

### Objectifs

L’objectif est de déployer un serveur EKS chez AWS

- Déployer un EKS

### Prérequis
  - Un cluster Kind

### Ma configuration
  - kind v0.30.0 go1.25.4 linux/amd64
  - Provider: 2.3.0

---

## Installation des providers requis

=== "Provider EKS"

    ```yaml title="provider-aws-eks.yaml" linenums="1"
    apiVersion: pkg.crossplane.io/v1
    kind: Provider
    metadata:
      name: upbound-provider-aws-eks
    spec:
      package: xpkg.upbound.io/upbound/provider-aws-eks:v2.3.0
    ```
    
=== "Provider EC2"

    ```yaml title="provider-aws-ec2.yaml" linenums="1"
    apiVersion: pkg.crossplane.io/v1
    kind: Provider
    metadata:
      name: upbound-provider-aws-ec2
    spec:
      package: xpkg.upbound.io/upbound/provider-aws-ec2:v2.3.0
    ```

=== "Provider IAM"
    
    ```yaml title="provider-aws-iam.yaml" linenums="1"
    apiVersion: pkg.crossplane.io/v1
    kind: Provider
    metadata:
      name: upbound-provider-aws-iam
    spec:
      package: xpkg.upbound.io/upbound/provider-aws-iam:v2.3.0
    ```

```shell hl_lines="1"
kubectl apply -f .
providerconfig.aws.m.upbound.io/default created
provider.pkg.crossplane.io/upbound-provider-aws-ec2 created
provider.pkg.crossplane.io/upbound-provider-aws-eks created
provider.pkg.crossplane.io/upbound-provider-aws-iam created
```

```shell hl_lines="1"
kubectl get pods --namespace crossplane-system
NAME                                                        READY   STATUS    RESTARTS   AGE
crossplane-6896f6fbff-49vbk                                 1/1     Running   0          113s
crossplane-rbac-manager-65f6d66c76-d4rf6                    1/1     Running   0          113s
upbound-provider-aws-ec2-a8a9f2ec0d4d-6c54fc456d-678dv      1/1     Running   0          77s
upbound-provider-aws-eks-ddb729fe156a-6c795595f8-k6j8s      1/1     Running   0          70s
upbound-provider-aws-iam-4aa994b6794d-7998f656bd-g7qkk      1/1     Running   0          83s
upbound-provider-family-aws-a22fe515ffa9-6666464b4c-r8zjd   1/1     Running   0          87s
```

```shell hl_lines="1"
kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
upbound-provider-aws-ec2      True        True      xpkg.upbound.io/upbound/provider-aws-ec2:v2.3.0      3m
upbound-provider-aws-eks      True        True      xpkg.upbound.io/upbound/provider-aws-eks:v2.3.0      2m45s
upbound-provider-aws-iam      True        True      xpkg.upbound.io/upbound/provider-aws-iam:v2.3.0      2m51s
upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v2.3.0   2m52s
```

```shell hl_lines="1"
kubectl get crds | grep aws.upbound.io
accessentries.eks.aws.upbound.io                                 2025-12-06T09:29:23Z
accesskeys.iam.aws.upbound.io                                    2025-12-06T09:28:55Z
accesspolicyassociations.eks.aws.upbound.io                      2025-12-06T09:29:24Z
accountaliases.iam.aws.upbound.io                                2025-12-06T09:28:55Z
accountpasswordpolicies.iam.aws.upbound.io                       2025-12-06T09:28:55Z
addons.eks.aws.upbound.io                                        2025-12-06T09:29:25Z
amicopies.ec2.aws.upbound.io                                     2025-12-06T09:29:12Z
amilaunchpermissions.ec2.aws.upbound.io                          2025-12-06T09:29:07Z
amis.ec2.aws.upbound.io                                          2025-12-06T09:29:17Z
availabilityzonegroups.ec2.aws.upbound.io                        2025-12-06T09:29:18Z
capacityreservations.ec2.aws.upbound.io                          2025-12-06T09:29:21Z
carriergateways.ec2.aws.upbound.io                               2025-12-06T09:29:09Z
clusterauths.eks.aws.upbound.io                                  2025-12-06T09:29:26Z
clusters.eks.aws.upbound.io                                      2025-12-06T09:29:30Z
customergateways.ec2.aws.upbound.io                              2025-12-06T09:29:21Z
defaultnetworkacls.ec2.aws.upbound.io                            2025-12-06T09:29:20Z
defaultroutetables.ec2.aws.upbound.io                            2025-12-06T09:29:12Z
defaultsecuritygroups.ec2.aws.upbound.io                         2025-12-06T09:29:07Z
defaultsubnets.ec2.aws.upbound.io                                2025-12-06T09:29:04Z
defaultvpcdhcpoptions.ec2.aws.upbound.io                         2025-12-06T09:29:08Z
defaultvpcs.ec2.aws.upbound.io                                   2025-12-06T09:29:03Z
ebsdefaultkmskeys.ec2.aws.upbound.io                             2025-12-06T09:29:01Z
ebsencryptionbydefaults.ec2.aws.upbound.io                       2025-12-06T09:29:08Z
ebssnapshotcopies.ec2.aws.upbound.io                             2025-12-06T09:29:13Z
ebssnapshotimports.ec2.aws.upbound.io                            2025-12-06T09:29:04Z
ebssnapshots.ec2.aws.upbound.io                                  2025-12-06T09:29:01Z
ebsvolumes.ec2.aws.upbound.io                                    2025-12-06T09:29:02Z
egressonlyinternetgateways.ec2.aws.upbound.io                    2025-12-06T09:29:17Z
eipassociations.ec2.aws.upbound.io                               2025-12-06T09:29:19Z
eips.ec2.aws.upbound.io                                          2025-12-06T09:29:12Z
fargateprofiles.eks.aws.upbound.io                               2025-12-06T09:29:24Z
fleets.ec2.aws.upbound.io                                        2025-12-06T09:29:05Z
flowlogs.ec2.aws.upbound.io                                      2025-12-06T09:29:01Z
groupmemberships.iam.aws.upbound.io                              2025-12-06T09:29:00Z
grouppolicyattachments.iam.aws.upbound.io                        2025-12-06T09:28:55Z
groups.iam.aws.upbound.io                                        2025-12-06T09:28:55Z
hosts.ec2.aws.upbound.io                                         2025-12-06T09:29:08Z
identityproviderconfigs.eks.aws.upbound.io                       2025-12-06T09:29:28Z
instanceprofiles.iam.aws.upbound.io                              2025-12-06T09:29:00Z
instances.ec2.aws.upbound.io                                     2025-12-06T09:29:15Z
instancestates.ec2.aws.upbound.io                                2025-12-06T09:29:09Z
internetgateways.ec2.aws.upbound.io                              2025-12-06T09:29:14Z
keypairs.ec2.aws.upbound.io                                      2025-12-06T09:29:09Z
launchtemplates.ec2.aws.upbound.io                               2025-12-06T09:29:24Z
mainroutetableassociations.ec2.aws.upbound.io                    2025-12-06T09:29:18Z
managedprefixlistentries.ec2.aws.upbound.io                      2025-12-06T09:29:16Z
managedprefixlists.ec2.aws.upbound.io                            2025-12-06T09:29:11Z
natgateways.ec2.aws.upbound.io                                   2025-12-06T09:29:22Z
networkaclrules.ec2.aws.upbound.io                               2025-12-06T09:29:02Z
networkacls.ec2.aws.upbound.io                                   2025-12-06T09:29:22Z
networkinsightsanalyses.ec2.aws.upbound.io                       2025-12-06T09:29:28Z
networkinsightspaths.ec2.aws.upbound.io                          2025-12-06T09:29:17Z
networkinterfaceattachments.ec2.aws.upbound.io                   2025-12-06T09:29:23Z
networkinterfaces.ec2.aws.upbound.io                             2025-12-06T09:29:22Z
networkinterfacesgattachments.ec2.aws.upbound.io                 2025-12-06T09:29:31Z
nodegroups.eks.aws.upbound.io                                    2025-12-06T09:29:23Z
openidconnectproviders.iam.aws.upbound.io                        2025-12-06T09:28:56Z
placementgroups.ec2.aws.upbound.io                               2025-12-06T09:29:21Z
podidentityassociations.eks.aws.upbound.io                       2025-12-06T09:29:32Z
policies.iam.aws.upbound.io                                      2025-12-06T09:28:54Z
providerconfigs.aws.upbound.io                                   2025-12-06T09:28:51Z
providerconfigusages.aws.upbound.io                              2025-12-06T09:28:51Z
rolepolicies.iam.aws.upbound.io                                  2025-12-06T09:28:57Z
rolepolicyattachments.iam.aws.upbound.io                         2025-12-06T09:28:55Z
roles.iam.aws.upbound.io                                         2025-12-06T09:28:56Z
routes.ec2.aws.upbound.io                                        2025-12-06T09:29:28Z
routetableassociations.ec2.aws.upbound.io                        2025-12-06T09:29:31Z
routetables.ec2.aws.upbound.io                                   2025-12-06T09:29:24Z
samlproviders.iam.aws.upbound.io                                 2025-12-06T09:28:55Z
securitygroupegressrules.ec2.aws.upbound.io                      2025-12-06T09:29:23Z
securitygroupingressrules.ec2.aws.upbound.io                     2025-12-06T09:29:21Z
securitygrouprules.ec2.aws.upbound.io                            2025-12-06T09:29:24Z
securitygroups.ec2.aws.upbound.io                                2025-12-06T09:29:27Z
serialconsoleaccesses.ec2.aws.upbound.io                         2025-12-06T09:29:27Z
servercertificates.iam.aws.upbound.io                            2025-12-06T09:29:17Z
servicelinkedroles.iam.aws.upbound.io                            2025-12-06T09:29:18Z
servicespecificcredentials.iam.aws.upbound.io                    2025-12-06T09:28:55Z
signingcertificates.iam.aws.upbound.io                           2025-12-06T09:29:12Z
snapshotcreatevolumepermissions.ec2.aws.upbound.io               2025-12-06T09:29:22Z
spotdatafeedsubscriptions.ec2.aws.upbound.io                     2025-12-06T09:29:27Z
spotfleetrequests.ec2.aws.upbound.io                             2025-12-06T09:29:28Z
spotinstancerequests.ec2.aws.upbound.io                          2025-12-06T09:29:21Z
subnetcidrreservations.ec2.aws.upbound.io                        2025-12-06T09:29:22Z
subnets.ec2.aws.upbound.io                                       2025-12-06T09:29:30Z
tags.ec2.aws.upbound.io                                          2025-12-06T09:29:29Z
trafficmirrorfilterrules.ec2.aws.upbound.io                      2025-12-06T09:29:31Z
trafficmirrorfilters.ec2.aws.upbound.io                          2025-12-06T09:29:27Z
transitgatewayconnectpeers.ec2.aws.upbound.io                    2025-12-06T09:29:21Z
transitgatewayconnects.ec2.aws.upbound.io                        2025-12-06T09:29:29Z
transitgatewaymulticastdomainassociations.ec2.aws.upbound.io     2025-12-06T09:29:21Z
transitgatewaymulticastdomains.ec2.aws.upbound.io                2025-12-06T09:29:23Z
transitgatewaymulticastgroupmembers.ec2.aws.upbound.io           2025-12-06T09:29:25Z
transitgatewaymulticastgroupsources.ec2.aws.upbound.io           2025-12-06T09:29:29Z
transitgatewaypeeringattachmentaccepters.ec2.aws.upbound.io      2025-12-06T09:29:28Z
transitgatewaypeeringattachments.ec2.aws.upbound.io              2025-12-06T09:29:31Z
transitgatewaypolicytables.ec2.aws.upbound.io                    2025-12-06T09:29:22Z
transitgatewayprefixlistreferences.ec2.aws.upbound.io            2025-12-06T09:29:28Z
transitgatewayroutes.ec2.aws.upbound.io                          2025-12-06T09:29:22Z
transitgatewayroutetableassociations.ec2.aws.upbound.io          2025-12-06T09:29:23Z
transitgatewayroutetablepropagations.ec2.aws.upbound.io          2025-12-06T09:29:25Z
transitgatewayroutetables.ec2.aws.upbound.io                     2025-12-06T09:29:25Z
transitgateways.ec2.aws.upbound.io                               2025-12-06T09:29:21Z
transitgatewayvpcattachmentaccepters.ec2.aws.upbound.io          2025-12-06T09:29:28Z
transitgatewayvpcattachments.ec2.aws.upbound.io                  2025-12-06T09:29:30Z
usergroupmemberships.iam.aws.upbound.io                          2025-12-06T09:28:56Z
userloginprofiles.iam.aws.upbound.io                             2025-12-06T09:28:54Z
userpolicyattachments.iam.aws.upbound.io                         2025-12-06T09:29:06Z
users.iam.aws.upbound.io                                         2025-12-06T09:29:14Z
usersshkeys.iam.aws.upbound.io                                   2025-12-06T09:29:13Z
virtualmfadevices.iam.aws.upbound.io                             2025-12-06T09:29:02Z
volumeattachments.ec2.aws.upbound.io                             2025-12-06T09:29:30Z
vpcdhcpoptions.ec2.aws.upbound.io                                2025-12-06T09:29:25Z
vpcdhcpoptionsassociations.ec2.aws.upbound.io                    2025-12-06T09:29:30Z
vpcendpointconnectionnotifications.ec2.aws.upbound.io            2025-12-06T09:29:24Z
vpcendpointroutetableassociations.ec2.aws.upbound.io             2025-12-06T09:29:23Z
vpcendpoints.ec2.aws.upbound.io                                  2025-12-06T09:29:27Z
vpcendpointsecuritygroupassociations.ec2.aws.upbound.io          2025-12-06T09:29:28Z
vpcendpointserviceallowedprincipals.ec2.aws.upbound.io           2025-12-06T09:29:30Z
vpcendpointservices.ec2.aws.upbound.io                           2025-12-06T09:29:31Z
vpcendpointsubnetassociations.ec2.aws.upbound.io                 2025-12-06T09:29:30Z
vpcipampoolcidrallocations.ec2.aws.upbound.io                    2025-12-06T09:29:22Z
vpcipampoolcidrs.ec2.aws.upbound.io                              2025-12-06T09:29:30Z
vpcipampools.ec2.aws.upbound.io                                  2025-12-06T09:29:31Z
vpcipams.ec2.aws.upbound.io                                      2025-12-06T09:29:28Z
vpcipamscopes.ec2.aws.upbound.io                                 2025-12-06T09:29:27Z
vpcipv4cidrblockassociations.ec2.aws.upbound.io                  2025-12-06T09:29:21Z
vpcpeeringconnectionaccepters.ec2.aws.upbound.io                 2025-12-06T09:29:32Z
vpcpeeringconnectionoptions.ec2.aws.upbound.io                   2025-12-06T09:29:30Z
vpcpeeringconnections.ec2.aws.upbound.io                         2025-12-06T09:29:30Z
vpcs.ec2.aws.upbound.io                                          2025-12-06T09:29:27Z
vpnconnectionroutes.ec2.aws.upbound.io                           2025-12-06T09:29:29Z
vpnconnections.ec2.aws.upbound.io                                2025-12-06T09:29:27Z
vpngatewayattachments.ec2.aws.upbound.io                         2025-12-06T09:29:24Z
vpngatewayroutepropagations.ec2.aws.upbound.io                   2025-12-06T09:29:29Z
vpngateways.ec2.aws.upbound.io                                   2025-12-06T09:29:25Z
```

## Configuration d'un providerConfig

```yaml title="provider-aws-config.yaml" linenums="1"
apiVersion: aws.m.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
  namespace: crossplane-system
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-secret
      key: creds
```

```shell hl_lines="1"
kubectl create secret generic aws-secret -n crossplane-system --from-file=creds=./aws-credentials.txt
```











































##################################################################################

# Create AWS VPC - EKS - IRSA - Cluster Autoscaler - CSI Driver

## Create S3 Bucket using Crossplane

```shell hl_lines="1" 
kubectl apply -f 0-crossplane/1-provider-aws-s3.yaml
kubectl get providers
kubectl get pods -n crossplane-system
kubectl get crds | grep aws.upbound.io
kubectl create secret generic aws-secret \
    -n crossplane-system \
    --from-file=creds=./aws-credentials.txt
kubectl apply -f 0-crossplane/0-provider-aws-config.yaml
kubectl apply -f 1-s3/0-my-bucket.yaml
kubectl get bucket
kubectl describe bucket
kubectl get bucket
kubectl apply -f 1-s3/1-my-bucket-versioning.yaml
kubectl get bucketversioning
```

## Create AWS VPC using Crossplane

```shell hl_lines="1" 
kubectl apply -f 0-crossplane/2-provider-aws-ec2.yaml
kubectl get providers
kubectl apply -f 2-vpc
kubectl get VPC
kubectl get InternetGateway
kubectl get RouteTableAssociation
```

## Create EKS Cluster using Crossplane

```shell hl_lines="1" 
kubectl apply -f 0-crossplane
kubectl get providers
kubectl apply -f 3-eks
kubectl get Cluster
kubectl get NodeGroup
aws configure --profile crossplane
aws eks update-kubeconfig --name dev-demo --region us-east-2 --profile crossplane
kubectl get nodes
```

## Create OpenID Connect Provider (OIDC)

```shell hl_lines="1" 
kubectl apply -f 4-irsa
kubectl get OpenIDConnectProvider
kubectl get Addon
```

## Deploy EBS CSI driver

```shell hl_lines="1" 
kubectl apply -f 5-storageclass
```

## Deploy Cluster Autoscaler

```shell hl_lines="1" 
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm search repo cluster-autoscaler

helm install autoscaler \
    --namespace kube-system \
    --version 9.29.3 \
    --values 6-cluster-autoscaler/1-helm-values.yaml \
    autoscaler/cluster-autoscaler
```