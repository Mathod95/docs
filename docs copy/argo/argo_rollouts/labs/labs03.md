# Migrating an Existing Deployment to Argo Rollouts

Chances are, that you are not starting with a fresh Kubernetes installation but already have a running cluster with deployed workloads. Argo Rollouts has this scenario in mind and provides a migration path to migrate Deployments to Rollout resources.

## Objective
Migrate a vanilla Kubernetes Deployment to an Argo Rollout resource.

## Prerequisites
  - Kubernetes cluster with an argo-rollouts controller.
  - kubectl with an argo-rollouts plugin (optional).

---

## Transitioning to Argo Rollouts

1. Preparing resources

For this lab, we will create an NGINX deployment—a task you may have already undertaken numerous times.  
Run the command below:

```bash hl_lines="1"
kubectl create deploy nginx-deployment --image=nginx --replicas=3
deployment.apps/nginx-deployment created
```

Now check our running pods and deployments using the following command:

```bash hl_lines="1"
kubectl get pods,deployment
NAME                                    READY   STATUS    RESTARTS   AGE
pod/nginx-deployment-6ff797d4c9-ftwcc   1/1     Running   0          57s
pod/nginx-deployment-6ff797d4c9-nbxf5   1/1     Running   0          57s
pod/nginx-deployment-6ff797d4c9-pw2cl   1/1     Running   0          57s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-deployment   3/3     3            3           58s
```

2. Convert Deployment to Rollout
Now we want to use the deployment definition to reference it in a new rollout. 
Run the command below:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: nginx-rollout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-deployment
  workloadRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: {duration: 10s}
EOF

rollout.argoproj.io/nginx-rollout created
```

!!! Note 
    The field `workloadRef`, which references the nginx-deployment resource.  
    As a result, we have 6 nginx instances running, 3 managed by our vanilla deployment, 3 by the newly created rollout. 
    
Run the command below:

```bash hl_lines="1"
kubectl get rollout,deployment,pod
NAME                                DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
rollout.argoproj.io/nginx-rollout   3         3         3            3           2m16s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-deployment   3/3     3            3           26m

NAME                                    READY   STATUS    RESTARTS   AGE
pod/nginx-deployment-6ff797d4c9-ftwcc   1/1     Running   0          26m
pod/nginx-deployment-6ff797d4c9-nbxf5   1/1     Running   0          26m
pod/nginx-deployment-6ff797d4c9-pw2cl   1/1     Running   0          26m
pod/nginx-rollout-6d7df6cfcb-bt78w      1/1     Running   0          2m16s
pod/nginx-rollout-6d7df6cfcb-z6srf      1/1     Running   0          2m16s
pod/nginx-rollout-6d7df6cfcb-zmm7v      1/1     Running   0          2m16s
```

3. Scale Down Deployment
To finish the migration, we now need to manually scale down the deployment. 
Run the following command:

```bash hl_lines="1"
kubectl scale deployment/nginx-deployment --replicas=0
```

Output:

```bash hl_lines="1"
kubectl get rollouts,deployments,pods
NAME                                DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
rollout.argoproj.io/nginx-rollout   3         3         3            3           4m9s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-deployment   0/0     0            0           28m

NAME                                 READY   STATUS    RESTARTS   AGE
pod/nginx-rollout-6d7df6cfcb-bt78w   1/1     Running   0          4m9s
pod/nginx-rollout-6d7df6cfcb-z6srf   1/1     Running   0          4m9s
pod/nginx-rollout-6d7df6cfcb-zmm7v   1/1     Running   0          4m9s
```

This leaves you with an up-and-running workload, managed by a rollout resource!

The step of scaling down the deployment once referenced by the Rollout resource can be taken over by the Argo Rollout controller. A special scaleDown parameter exists that enables administrators to specify how the deployment should be scaled down (never, onsuccess, progressively).

After confirming the deployment is scaled down, scale it up one more time with the following command:

```bash hl_lines="1"
kubectl scale deployment/nginx-deployment --replicas=3
```

And apply the following new rollout spec which includes the scaleDown parameter:
```bash hl_lines="1"
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: nginx-rollout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-deployment
  workloadRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
    scaleDown: onsuccess
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: {duration: 10s}
EOF
```

This will provide the same result as before, except this time there was no need for any manual intervention!

Command:

```bash hl_lines="1"
kubectl get rollouts,deployments,pods
NAME                                DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
rollout.argoproj.io/nginx-rollout   3         3         3            3           126m

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-deployment   0/0     0            0           150m

NAME                                 READY   STATUS    RESTARTS   AGE
pod/nginx-rollout-6d7df6cfcb-bt78w   1/1     Running   0          126m
pod/nginx-rollout-6d7df6cfcb-z6srf   1/1     Running   0          126m
pod/nginx-rollout-6d7df6cfcb-zmm7v   1/1     Running   0          126m
```

More details on the feature can be found on the Rollout Migration documentation page.

4. Clean Up Resources
Make sure to leave the cluster nice and clean.

Command:

```bash
$ kubectl delete rollout nginx-rollout
```

Output:

```bash
rollout.argoproj.io "nginx-rollout" deleted
```

Command:

```bash
$ kubectl delete deployment nginx-deployment
```

Output:

```bash
deployment.apps "nginx-deployment" deleted
```

---