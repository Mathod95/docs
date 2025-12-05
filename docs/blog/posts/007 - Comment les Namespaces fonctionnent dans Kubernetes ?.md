---
title: Comment les Namespaces fonctionnent dans Kubernetes ?
date: 2025-12-03
categories:
  - Kubernetes
tags:
  - Kubernetes
  - namespace
---

![](../../assets/images/kubernetes/kubernetes.svg)

## Introduction

Dans Kubernetes, un namespace (abrégé ns) est un mécanisme qui permet d’isoler des groupes de ressources au sein d’un même cluster. 

Les objets dans un namespace doivent avoir des noms uniques, mais il est possible d’avoir des objets portant le même nom dans des namespaces différents. Les namespaces sont utilisés principalement pour les objets namespaced (comme les `Deployments`, `Services`, etc.), et ne s’appliquent pas aux objets cluster-wide (comme `StorageClass`, `Nodes`, `PersistentVolumes`, etc.).

<!-- more -->
---

## Objectifs des Namespaces

- Organisation des ressources : Les namespaces aident à maintenir les ressources du cluster bien organisées, ce qui est particulièrement utile lorsque plusieurs équipes ou projets partagent le même cluster Kubernetes.

- Gestion des ressources : Ils permettent un contrôle fin sur l'utilisation des ressources. Par exemple, il est possible d'appliquer des quotas de CPU et de mémoire à chaque namespace, ce qui empêche une partie du cluster de monopoliser toutes les ressources.

- Contrôle d'accès : Les namespaces s'intègrent bien avec le système RBAC (Role-Based Access Control) de Kubernetes, permettant aux administrateurs de restreindre les permissions des utilisateurs à des namespaces spécifiques.

## Un aperçu des Namespaces par défaut

Lors de la création d’un cluster Kubernetes, plusieurs namespaces sont créés par défaut. Ces namespaces sont utilisés pour organiser et isoler les ressources au sein du cluster. Voici les namespaces principaux créés par défaut :

- default : Le namespace par défaut pour les objets qui n'ont pas de namespace spécifié.
- kube-system : Contient les objets créés par Kubernetes lui-même, comme les processus système.
- kube-public : Un namespace public où sont stockées les informations accessibles à tous les utilisateurs. Ce namespace est utilisé pour des buts spéciaux, comme la découverte du cluster.
- kube-node-lease : Contient les objets de type "lease" qui assurent les "heartbeats" des nœuds, afin que le planificateur Kubernetes prenne de meilleures décisions concernant les nœuds.

## Créer un Namespace

Créer un namespace est simple et peut se faire de deux manières :

=== "Déclarative"

    Méthode déclarative : Vous pouvez créer un fichier YAML contenant la définition du namespace et l'appliquer avec la commande kubectl.

    Exemple de fichier YAML pour créer un namespace :

    ```yaml linenums="1" title="namespace.yaml"
    apiVersion: v1
    kind: Namespace
    metadata:
	    name: <namespace>
    ```
    Appliquer ce fichier avec la commande suivante :
    ```bash hl_lines="1"
    kubectl apply -f namespace.yaml
    ```
    
=== "Impérative"
    
    Méthode impérative : Utilisez simplement la commande suivante pour créer un namespace :

    ```bash hl_lines="1"
    kubectl create namespace <namespaceName>
    ```

??? tip "Commandes utiles pour gérer les Namespaces"
    Voici une liste de commandes pour interagir avec les namespaces dans Kubernetes:

    ```shell hl_lines="1" title="Lister tous les namespaces"
    kubectl get namespaces
    ```
    ```shell hl_lines="1" title="Supprimer un namespace"
    kubectl delete namespace <namespaceName>
    ```
    ```shell hl_lines="1" title="Lister les pods dans tous les namespaces"
    kubectl get pods --all-namespaces
    ```

??? tip "Ressources Namespacées et Non Namespacées"
    ```shell hl_lines="1"
    kubectl api-resources
    NAME                                SHORTNAMES   APIVERSION                        NAMESPACED   KIND
    bindings                                         v1                                true         Binding
    componentstatuses                   cs           v1                                false        ComponentStatus
    configmaps                          cm           v1                                true         ConfigMap
    endpoints                           ep           v1                                true         Endpoints
    events                              ev           v1                                true         Event
    limitranges                         limits       v1                                true         LimitRange
    namespaces                          ns           v1                                false        Namespace
    nodes                               no           v1                                false        Node
    persistentvolumeclaims              pvc          v1                                true         PersistentVolumeClaim
    persistentvolumes                   pv           v1                                false        PersistentVolume
    pods                                po           v1                                true         Pod
    podtemplates                                     v1                                true         PodTemplate
    replicationcontrollers              rc           v1                                true         ReplicationController
    resourcequotas                      quota        v1                                true         ResourceQuota
    secrets                                          v1                                true         Secret
    serviceaccounts                     sa           v1                                true         ServiceAccount
    services                            svc          v1                                true         Service
    mutatingwebhookconfigurations                    admissionregistration.k8s.io/v1   false        MutatingWebhookConfiguration
    validatingadmissionpolicies                      admissionregistration.k8s.io/v1   false        ValidatingAdmissionPolicy
    validatingadmissionpolicybindings                admissionregistration.k8s.io/v1   false        ValidatingAdmissionPolicyBinding
    validatingwebhookconfigurations                  admissionregistration.k8s.io/v1   false        ValidatingWebhookConfiguration
    customresourcedefinitions           crd,crds     apiextensions.k8s.io/v1           false        CustomResourceDefinition
    apiservices                                      apiregistration.k8s.io/v1         false        APIService
    controllerrevisions                              apps/v1                           true         ControllerRevision
    daemonsets                          ds           apps/v1                           true         DaemonSet
    deployments                         deploy       apps/v1                           true         Deployment
    replicasets                         rs           apps/v1                           true         ReplicaSet
    statefulsets                        sts          apps/v1                           true         StatefulSet
    selfsubjectreviews                               authentication.k8s.io/v1          false        SelfSubjectReview
    tokenreviews                                     authentication.k8s.io/v1          false        TokenReview
    localsubjectaccessreviews                        authorization.k8s.io/v1           true         LocalSubjectAccessReview
    selfsubjectaccessreviews                         authorization.k8s.io/v1           false        SelfSubjectAccessReview
    selfsubjectrulesreviews                          authorization.k8s.io/v1           false        SelfSubjectRulesReview
    subjectaccessreviews                             authorization.k8s.io/v1           false        SubjectAccessReview
    horizontalpodautoscalers            hpa          autoscaling/v2                    true         HorizontalPodAutoscaler
    cronjobs                            cj           batch/v1                          true         CronJob
    jobs                                             batch/v1                          true         Job
    certificatesigningrequests          csr          certificates.k8s.io/v1            false        CertificateSigningRequest
    leases                                           coordination.k8s.io/v1            true         Lease
    endpointslices                                   discovery.k8s.io/v1               true         EndpointSlice
    events                              ev           events.k8s.io/v1                  true         Event
    flowschemas                                      flowcontrol.apiserver.k8s.io/v1   false        FlowSchema
    prioritylevelconfigurations                      flowcontrol.apiserver.k8s.io/v1   false        PriorityLevelConfiguration
    ingressclasses                                   networking.k8s.io/v1              false        IngressClass
    ingresses                           ing          networking.k8s.io/v1              true         Ingress
    ipaddresses                         ip           networking.k8s.io/v1              false        IPAddress
    networkpolicies                     netpol       networking.k8s.io/v1              true         NetworkPolicy
    servicecidrs                                     networking.k8s.io/v1              false        ServiceCIDR
    runtimeclasses                                   node.k8s.io/v1                    false        RuntimeClass
    poddisruptionbudgets                pdb          policy/v1                         true         PodDisruptionBudget
    clusterrolebindings                              rbac.authorization.k8s.io/v1      false        ClusterRoleBinding
    clusterroles                                     rbac.authorization.k8s.io/v1      false        ClusterRole
    rolebindings                                     rbac.authorization.k8s.io/v1      true         RoleBinding
    roles                                            rbac.authorization.k8s.io/v1      true         Role
    deviceclasses                                    resource.k8s.io/v1                false        DeviceClass
    resourceclaims                                   resource.k8s.io/v1                true         ResourceClaim
    resourceclaimtemplates                           resource.k8s.io/v1                true         ResourceClaimTemplate
    resourceslices                                   resource.k8s.io/v1                false        ResourceSlice
    priorityclasses                     pc           scheduling.k8s.io/v1              false        PriorityClass
    csidrivers                                       storage.k8s.io/v1                 false        CSIDriver
    csinodes                                         storage.k8s.io/v1                 false        CSINode
    csistoragecapacities                             storage.k8s.io/v1                 true         CSIStorageCapacity
    storageclasses                      sc           storage.k8s.io/v1                 false        StorageClass
    volumeattachments                                storage.k8s.io/v1                 false        VolumeAttachment
    volumeattributesclasses             vac          storage.k8s.io/v1                 false        VolumeAttributesClass
    ```

---  
## Conclusion

Les namespaces sont un outil puissant pour organiser, gérer les ressources, et contrôler l'accès au sein d'un cluster Kubernetes. Ils permettent de structurer les ressources d'un cluster partagé, d'appliquer des quotas de ressources et de renforcer la sécurité en contrôlant les permissions d'accès via RBAC.

Une bonne gestion des namespaces est essentielle pour éviter la surcharge d'un cluster, surtout dans des environnements où plusieurs équipes ou projets se partagent le même cluster Kubernetes.

<div class="admonition abstract">
  <p class="admonition-title">Documentation</p>

```embed
url: https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/kubernetes/stacked/all-blue-color/kubernetes-stacked-all-blue-color.svg
```
</div>