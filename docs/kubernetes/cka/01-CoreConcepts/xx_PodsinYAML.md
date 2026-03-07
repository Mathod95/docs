---
title: Pods with YAML
status: draft
sources:
  - https://notes.kodekloud.com/docs/CKA-Certification-Course-Certified-Kubernetes-Administrator/Core-Concepts/Pods-with-YAML/page#creating-and-verifying-the-pod # [x]
  - https://notes.kodekloud.com/docs/kubernetes-for-the-absolute-beginners-hands-on-tutorial/Kubernetes-Concepts-Pods-ReplicaSets-Deployments/Pods-with-YAML/page#creating-the-pod 
---

> Ce cours explique comment créer un Pod Kubernetes à l’aide d’un fichier de configuration YAML. Vous y apprendrez à structurer le fichier YAML, à créer le Pod avec kubectl, puis à vérifier son statut afin de vous assurer qu’il fonctionne correctement.

## Top-Level Fields d’un fichier YAML Kubernetes

Kubernetes utilise des fichiers YAML pour définir des objets tels que les `Pods`, `ReplicaSets`, `Deployments`, `Services`, etc. Ces fichiers suivent une structure standard composée de quatre champs principaux.
Chaque fichier de définition Kubernetes doit inclure les champs suivants :

```yaml
apiVersion:
kind:
metadata:
spec:
```

<!--
- apiVersion : version de l’API Kubernetes utilisée pour créer l’objet
- kind : type d’objet à créer (par exemple : Pod, Deployment, Service)
- metadata : informations d’identification de l’objet, comme le nom et les labels
- spec : spécification détaillée de l’objet, c’est-à-dire sa configuration et son état souhaité
-->

1. **apiVersion:**
   This field indicates the version of the Kubernetes API you are using. For a Pod, set `apiVersion: v1`. Depending on the object you define, you might need different versions such as apps/v1, extensions/v1beta1, etc.

2. **kind:**
   This specifies the type of object being created. In this lesson, since we're creating a Pod, you'll define it as `kind: Pod`. Other objects might include ReplicaSet, Deployment, or Service.

3. **metadata:**
   The metadata section provides details about the object, including its name and labels. It is represented as a dictionary. It is essential to maintain consistent indentation for sibling keys to ensure proper YAML nesting. For example:

4. **spec:**
   The spec section provides specific configuration details for the object. For a Pod, this is where you define its containers. Since a Pod can run multiple containers, the `containers` field is an array. In our example, with a single container, the array has just one item. The dash (`-`) indicates a list item, and each container must be defined with at least `name` and `image` keys.

Below is the complete YAML configuration for our Pod:

!!! note 
    Be sure to follow proper indentation rules. Use two spaces per level (avoid tabs), as misalignment can lead to errors.

```yaml linenums="1" title="pod.yaml"
apiVersion: v1
kind: Pod
metadata:
  name: podinfo
  namespace: default
  labels:
    app.kubernetes.io/name: podinfo
spec:
  containers:
  - name: podinfo
    image: ghcr.io/stefanprodan/podinfo:6.11.0
```

!!! note
    To add additional containers, insert another block within the containers list with the appropriate name and image.

## Creating and Verifying the Pod

After you have saved your configuration (for example, as `pod.yaml`), use the following command to create the Pod:

!!! note
    kubectl run podinfo --image=ghcr.io/stefanprodan/podinfo:6.11.0 --dry-run=client -o yaml > pod.yaml

```bash
kubectl apply -f pod.yaml
```

!!! note "apply vs create"
    Utiliser la commande `kubectl apply -f` plutot que `kubectl create -f`

    - `kubectl apply -f`
        - crée le Pod s’il n’existe pas
        - échoue si la ressource existe déjà
    - `kubectl create -f`
        - crée la ressource si elle n’existe pas
        - met à jour la configuration si elle existe

    ---
    
    ??? note "Tester le manifest sans créer la ressource"

        ```bash hl_lines="1"
        kubectl apply -f pod.yaml --dry-run=client -o yaml
        apiVersion: v1
        kind: Pod
        metadata:
          annotations:
            kubectl.kubernetes.io/last-applied-configuration: |
              {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"labels":{"app.kubernetes.io/managed-by":"kubectl","app.kubernetes.io/name":"podinfo"},"name":"podinfo","namespace":"default"},"spec":{"containers":[{"image":"ghcr.io/stefanprodan/podinfo:6.11.0","name":"podinfo"}]}}
          creationTimestamp: "2026-03-07T02:45:33Z"
          generation: 1
          labels:
            app.kubernetes.io/managed-by: kubectl
            app.kubernetes.io/name: podinfo
          name: podinfo
          namespace: default
          resourceVersion: "64366"
          uid: 8161158a-24c2-43d6-a048-91ae77fc780f
        spec:
          containers:
          - image: ghcr.io/stefanprodan/podinfo:6.11.0
            imagePullPolicy: IfNotPresent
            name: podinfo
            resources: {}
            terminationMessagePath: /dev/termination-log
            terminationMessagePolicy: File
            volumeMounts:
            - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
              name: kube-api-access-psmmf
              readOnly: true
          dnsPolicy: ClusterFirst
          enableServiceLinks: true
          nodeName: test-control-plane
          preemptionPolicy: PreemptLowerPriority
          priority: 0
          restartPolicy: Always
          schedulerName: default-scheduler
          securityContext: {}
          serviceAccount: default
          serviceAccountName: default
          terminationGracePeriodSeconds: 30
          tolerations:
          - effect: NoExecute
            key: node.kubernetes.io/not-ready
            operator: Exists
            tolerationSeconds: 300
          - effect: NoExecute
            key: node.kubernetes.io/unreachable
            operator: Exists
            tolerationSeconds: 300
          volumes:
          - name: kube-api-access-psmmf
            projected:
              defaultMode: 420
              sources:
              - serviceAccountToken:
                  expirationSeconds: 3607
                  path: token
              - configMap:
                  items:
                  - key: ca.crt
                    path: ca.crt
                  name: kube-root-ca.crt
              - downwardAPI:
                  items:
                  - fieldRef:
                      apiVersion: v1
                      fieldPath: metadata.namespace
                    path: namespace
        status:
          conditions:
          - lastProbeTime: null
            lastTransitionTime: "2026-03-07T02:45:34Z"
            observedGeneration: 1
            status: "True"
            type: PodReadyToStartContainers
          - lastProbeTime: null
            lastTransitionTime: "2026-03-07T02:45:33Z"
            observedGeneration: 1
            status: "True"
            type: Initialized
          - lastProbeTime: null
            lastTransitionTime: "2026-03-07T02:45:34Z"
            observedGeneration: 1
            status: "True"
            type: Ready
          - lastProbeTime: null
            lastTransitionTime: "2026-03-07T02:45:34Z"
            observedGeneration: 1
            status: "True"
            type: ContainersReady
          - lastProbeTime: null
            lastTransitionTime: "2026-03-07T02:45:33Z"
            observedGeneration: 1
            status: "True"
            type: PodScheduled
          containerStatuses:
          - containerID: containerd://e7f72ede38ccd52133d1a3e98d01eb313a436fd301f4302d662519f22c0ea4fe
            image: ghcr.io/stefanprodan/podinfo:6.11.0
            imageID: ghcr.io/stefanprodan/podinfo@sha256:5b789251f4b35f4ac6319c48b57eb6d29356d67471404c5fd3733db2eb8c11cf
            lastState: {}
            name: podinfo
            ready: true
            resources: {}
            restartCount: 0
            started: true
            state:
              running:
                startedAt: "2026-03-07T02:45:33Z"
            user:
              linux:
                gid: 101
                supplementalGroups:
                - 101
                uid: 100
            volumeMounts:
            - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
              name: kube-api-access-psmmf
              readOnly: true
              recursiveReadOnly: Disabled
          hostIP: 172.18.0.2
          hostIPs:
          - ip: 172.18.0.2
          observedGeneration: 1
          phase: Running
          podIP: 10.244.0.8
          podIPs:
          - ip: 10.244.0.8
          qosClass: BestEffort
          startTime: "2026-03-07T02:45:33Z"
        ```

Once the Pod is created, you can verify its status by listing all Pods:

```bash
kubectl get pods -n default
NAME      READY   STATUS    RESTARTS   AGE
podinfo   1/1     Running   0          5m6s
```

To view detailed information about the Pod, run:
This command provides extensive details, including metadata, node assignment, container specifics, and event history such as scheduling, volume mounting, and container start-up. Here is an example output:

```bash hl_lines="1"
kubectl describe pod podinfo
Name:             podinfo
Namespace:        default
Priority:         0
Service Account:  default
Node:             test-control-plane/172.18.0.2
Start Time:       Sat, 07 Mar 2026 03:45:33 +0100
Labels:           app.kubernetes.io/name=podinfo
Annotations:      <none>
Status:           Running
IP:               10.244.0.8
IPs:
  IP:  10.244.0.8
Containers:
  podinfo:
    Container ID:   containerd://e7f72ede38ccd52133d1a3e98d01eb313a436fd301f4302d662519f22c0ea4fe
    Image:          ghcr.io/stefanprodan/podinfo:6.11.0
    Image ID:       ghcr.io/stefanprodan/podinfo@sha256:5b789251f4b35f4ac6319c48b57eb6d29356d67471404c5fd3733db2eb8c11cf
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Sat, 07 Mar 2026 03:45:33 +0100
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-psmmf (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-psmmf:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age    From               Message
  ----    ------     ----   ----               -------
  Normal  Scheduled  5m33s  default-scheduler  Successfully assigned default/podinfo to test-control-plane
  Normal  Pulled     5m33s  kubelet            spec.containers{podinfo}: Container image "ghcr.io/stefanprodan/podinfo:6.11.0" already present on machine and can be accessed by the pod
  Normal  Created    5m33s  kubelet            spec.containers{podinfo}: Container created
  Normal  Started    5m33s  kubelet            spec.containers{podinfo}: Container started
```

!!! note
    Using `kubectl describe` helps you gain detailed insights into the internal state of your Pod, which can be invaluable for troubleshooting.

## Conclusion

In this lesson, you learned how to structure a Kubernetes YAML file for a Pod, create it using kubectl, and verify its status. This hands-on approach equips you to manage and troubleshoot your Kubernetes resources effectively. Happy Kubernetes-ing!

For more information, refer to the following resources:

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes Basics](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)