# Argo Rollouts Architecture and Core Components

---

## Building Blocks of Argo Rollouts

In this section, we will discuss the building blocks of Argo Rollouts. To give you an overview of what to expect, we’ll briefly describe the relevant components of an Argo Rollouts setup before we discover them in more detail.

![](../../../assets/images/argo/rollouts/rollouts.excalidraw#architecture)

**Argo Rollouts Components**

- **Argo Rollouts Controller:** An operator that manages Argo Rollout Resources. It reads all the details of a rollout (and other resources) and ensures the desired cluster state.
- **Argo Rollout Resource:** A custom Kubernetes resource managed by the Argo Rollouts Controller. It is largely compatible with the native Kubernetes Deployment resource, adding additional fields that manage the stages, thresholds, and techniques of sophisticated deployment strategies, including canary and blue-green deployments.
- **Ingress and the Gateway API:** The Kubernetes Ingress resource is used to enable traffic management for various traffic providers such as service meshes (e.g., Istio or Linkerd) or Ingress Controllers (e.g., Nginx Ingress Controller).  
The Kubernetes Gateway API is also supported with a separate plugin and provides similar functionality.
- **Service:** Argo Rollouts utilizes the Kubernetes Service resource to redirect ingress traffic to the respective workload version by adding specific metadata to a Service.
- **ReplicaSet:** Standard Kubernetes ReplicaSet resource used by Argo Rollouts to keep track of different versions of an application deployment.
- **AnalysisTemplate and AnalysisRun:** Analysis is an optional feature of Argo Rollouts and enables the connection of Rollouts to a monitoring system. This allows automation of promotions and rollbacks. To perform an analysis an AnalysisTemplate defines a metric query and their expected result. If the query matches the expectation, a Rollout will progress or rollback automatically, if it doesn’t. An AnalysisRuns is an instantiation of an AnalysisTemplate (similar to Kubernetes Jobs).

- **Metric Providers:** Metric providers can be used to automate promotions or rollbacks of a rollout. Argo Rollouts provides native integration for popular metric providers such as Prometheus and other monitoring systems.

Please note, that not all of the mentioned components are mandatory to every Argo Rollouts setup. The usage of Analysis resources or metric providers is entirely optional and relevant for more advanced use cases. Also note that the Argo Rollouts components are independent of other Argo projects (like Argo CD or Argo Workflows) and do not require them to function properly.

---

## A Refresher: The Kubernetes Replica Set

A Refresher: The Kubernetes Replica Set
To grasp the workings of Argo Rollouts in handling workloads, it's essential to understand some basics of Kubernetes. Essentially, Argo Rollouts functions in a manner quite similar to Kubernetes Deployment resources. What is less commonly known is that Deployments provide another layer of abstraction for workload management. The Deployment resource was a relatively later addition to Kubernetes, debuting in version 1.5 as part of the apps/v1beta1 API and achieving stability in version 1.9 with the apps/v1 API. Before the introduction of Deployments, workload management was accomplished using ReplicaSets. And under the hood, they are used until today!

A Kubernetes ReplicaSet is a resource used to ensure that a specified number of pod replicas are running at any given time. Essentially, it's a way to manage the lifecycle of pods. The main function of a ReplicaSet is to maintain a stable set of pod replicas running at any given time. It does so by scheduling pods as needed to reach the desired number.

If a pod fails, the ReplicaSet will replace it; if there are more pods than needed, it will terminate the extra pods. ReplicaSets are used to achieve redundancy and high availability within Kubernetes applications.

For more sophisticated orchestration like rolling updates, rollbacks or scaling a ReplicaSet is not enough. Kubernetes introduced a higher-level (and usually better known) concept called Deployment resource that manages both the deployment and updating of applications.

A deployment is managed by the Kubernetes deployment controller and is responsible for updating ReplicaSets by providing declarative updates for them.

Lets create a Deployment of nginx proxies to demonstrate the ownership between Deployment and ReplicaSet.

```bash hl_lines="1"
kubectl create deploy nginx-deployment --image=nginx --replicas=3
deployment.apps/nginx-deployment created
```

Now make sure it properly scaled up.

```bash
kubectl get deployment
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           47s
```

```bash
$ kubectl get replicaset
NAME                          DESIRED   CURRENT   READY   AGE
nginx-deployment-66fb7f764c   3         3         3       47s
```

The ReplicaSet nginx-deployment-66fb7f764c is managed by nginx-deployment. You can tell this by inspecting the ReplicaSet with the following command:

```bash
kubectl get replicaset nginx-deployment-66fb7f764c -ojsonpath='{.metadata.ownerReferences}' | jq
[
  {
    "apiVersion": "apps/v1",
    "blockOwnerDeletion": true,
    "controller": true,
    "kind": "Deployment",
    "name": "nginx-deployment",
    "uid": "1dd44efd-aab5-4475-aff2-32670201e2ef"
  }
]
```

As we see, the ownerReferences of the ReplicaSet state, that this resource is “owned” by a Deployment resource with the uid “1dd44efd-aab5-4475-aff2-32670201e2ef”. And indeed, this uid matches with the other Deployment we just created.

```bash
kubectl get deployment nginx-deployment -ojsonpath='{.metadata.uid}'
1dd44efd-aab5-4475-aff2-32670201e2ef
```
Deployments are a great invention of vanilla Kubernetes and are a successful abstraction. Rarely do people manage their pods manually through ReplicaSets. Deployments are the standard.

But despite all the praise, Deployment resources are still limited in their capabilities. They still do not support all deployment strategies we described in the previous section, “A Primer on Progressive Delivery”.

---

## Argo Rollouts

Here, we will explore the Argo Rollouts resource, which is the central element in Argo Rollouts, enabling advanced deployment strategies. A Rollout, in essence, is a Kubernetes resource that closely mirrors the functionality of a Kubernetes Deployment object. However, it steps in as a more advanced substitute for Deployment objects, particularly in scenarios demanding intricate deployment of progressive delivery techniques.

---

## Key Features of Argo Rollouts
Argo Rollouts outshine regular Kubernetes Deployments with several enhanced features.

**Argo Rollouts Functionalities:**

- **Blue-green deployments:** This approach minimizes downtime and risk by switching traffic between two versions of the application.
- **Canary deployments:** Gradually roll out changes to a subset of users to ensure stability before full deployment.
- **Advanced traffic routing:** Integrates seamlessly with ingress controllers and service meshes, facilitating sophisticated traffic management.
- **Integration with metric providers:** Offers analytical insights for blue-green and canary deployments, enabling informed decisions.
- **Automated decision making:** Automatically promote or roll back deployments based on the success or failure of defined metrics.

The Rollout resource is a custom Kubernetes resource introduced and managed by the Argo Rollouts Controller. This Kubernetes controller monitors resources of type Rollout and ensures that the described state will be reflected in the cluster.

The Rollout resource maintains high compatibility with the conventional Kubernetes Deployment resource but is augmented with additional fields. These fields are instrumental in governing the phases, thresholds, and methodologies of advanced deployment approaches, such as canary and blue-green strategies.

It’s crucial to understand that the Argo Rollouts controller is attuned exclusively to changes in Rollout resources. It remains inactive for standard deployment resources. Consequently, to use the Argo Rollouts for existing Deployments, a migration from traditional Deployments to Rollouts is required.

Overall, Deployment and Rollout resources look pretty similar. Refer to the following table to understand the minimal differences between both.

| Deployment Resource | Argo Rollout Resource | Comment |
|-|-|-|
||| Basic resource metadata. |
| replicas: 3 | replicas: 3 | Number of desired pods. Defaults to 1. |
||| Label selector for pods. |
||| Describes the pod template that will be used to instantiate pods. The template does not differ. |
||| A Deployment strategy can be either “RollingUpdate” (default) or “Recreate”. A Rollout strategy can either be “blueGreen” or “canary” |

Of course, there are way more configuration options to control the behavior of a Rollout. Please refer to the official Argo Rollouts specification for more options.

---

## Migrating Existing Deployments to Rollouts
The similarity of Deployments and Rollouts spec makes it easier to convert from one to the other resource type. Argo Rollouts supports a great way to migrate existing Deployment resources to Rollouts.

By providing a spec.workloadRef instead of spec.template a Rollout can refer to a Deployments template:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: nginx-rollout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  workloadRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
[...]
```
The Rollout will fetch the template information from the Deployment (in our example named nginx-deployment) and start the in the Rollout specified number of pods.

Please note, that lifecycles of Deployment and Rollouts are distinct and managed by their respective controllers. This means that the Kubernetes Deployment controller will not start to manage Pods created by the Rollout. Also, the Rollout will not start to manage pods that are controlled by the Deployment.

This enables a zero-downtime introduction of Argo Rollouts to your existing cluster. It furthermore makes experimentation with multiple deployment scenarios possible.

---

## Discussion: Create Rollouts or Reference Deployments from Rollouts?
As Rollout resources can exist and operate without vanilla Deployments, the following question might arise: Should I always reference Deployments or is it better to start over with an independent Rollout resource, without the dependency of a reference?

And the simple answer to it is… it depends.

Generally, workloadRef has been invented to enable a simple and seamless way of migrating from Deployments to Rollouts. We even consider it useful as Administrators who are unfamiliar with Argo Rollouts might be confused if they see an array of Pods running but neither a running Deployment nor StatefulSet. To lower the barrier, referencing existing Deployments from a Rollout can be a good option.

If you use Deployment referencing, the Argo controller will copy the generation number of the referenced Deployment and stores it in a status field called workloadObservedGeneration. Therefore the rollouts own rollout.argoproj.io/workload-generation annotation should always match the generation of the deployment. This helps to identify deviation due to manipulation of either of the resources.

However, referencing comes at the cost of another resource dependency. Yet another resource to check in case of failure!

So, if you are sure you want to work with Argo Rollouts, use the native Rollout Resource.

Hint: It is also possible to migrate a Rollout resource to a native Deployment. Please refer to the official documentation for further information.

Additional learning resources:

To explore the detailed specification of a Rollout, visit Argo Rollouts Specification.
For guidance on transitioning from a Deployment to a Rollout, consult Migrating a Deployment to Rollout.

---

## Ingress and Service Resources

**Relevant Resources for Traffic Routing**

**Kubernetes Ingress:** A Kubernetes Ingress is a Kubernetes native resource that manages external access to services in a cluster (typically via HTTP). An Ingress allows defining rules for inbound connections to reach cluster-internal Kubernetes Services. As such, they are an important abstraction to programmatically control the flow of incoming network traffic. They can even be used for SSL/TLS termination.

This approach is expanded by the Kubernetes Gateway API. The Gateway API splits the Ingress approach into the Kubernetes Gateway and Kubernetes HTTPRoute - the latter of which is managed by Argo Rollouts as it did Ingress. The advantage is that the Gateway API provides additional modes of access beyond HTTP/HTTPS and does not require controller-specific code like Ingress did.

**Kubernetes Service:** A Kubernetes Service is a resource that abstracts how to expose an application running on a set of Pods. Services can load-balance traffic and provide service discovery within the cluster. The primary role of a Service is to provide a consistent IP address and port number for accessing the running application, irrespective of the changes in the pods.

In the context of Argo Rollouts, these resources play a pivotal role when it comes to, for example, canary deployments. The general behavior of Service and Ingress resources is no different when used with Argo. Argo Rollouts uses Kubernetes Services to manage traffic flow to different versions of an application during a rollout process and they do so by augmenting the service with additional metadata.

**Pod Template Hash:**
Argo Rollouts utilizes the Pod Template Hash, which uniquely identifies Pods of a common ReplicaSset. So to switch incoming traffic from the “old” ReplicaSet to our new ReplicaSet, the Argo Rollouts controller mutates the Service spec.selector to match the new Pod Template Hash.

Kubernetes Services have selectors that find matching pods according to their label set; the pod-template-hash label is added to every ReplicaSet and used to make routing decisions

**Stable/Canary ReplicaSets:** By introducing a “stable service” and “canary services” in the Rollouts Spec, Argo can not only switch the traffic to Stable/Canary ReplicaSets, but also decide about the distribution of which ReplicaSet should receive how much traffic.

---

## Rollout Analysis & Experiments
The ability to split traffic between stable and canary workloads is good. But how do we decide if the canary workload is performing well and is therefore considered "stable"? That's right, metrics! An operator would closely observe the monitoring system (e.g., Prometheus, VMWare Wavefront or others) for certain metrics that indicate the application is working well. If you're thinking that this "observing metrics and making a decision" could be automated, you're right!

Argo Rollouts allows the user to run “Analysis” during the progressive delivery process. It primarily focuses on evaluating and ensuring the success of deployment based on defined criteria. These criteria can include custom metrics of your specific metric monitoring provider (see the official documentation for a conclusive list of supported metric providers).

The analysis process in Argo Rollouts involves following custom resources that work hand in hand with the already discussed resources.

Table 5.4: Analysis Custom Resource Definitions

| Templates	| Description/Use Case |
| --------- | -------------------- |
| `AnalysisTemplate` | This template defines the metrics to be queried and the conditions for success or failure. The AnalysisTemplate specifies what metrics should be monitored and the thresholds for determining the success or failure of a deployment. It can be parameterized with input values to make it more dynamic and adaptable to different situations.|
| `AnalysisRun` | An AnalysisRun is an instantiation of an AnalysisTemplate. It is a Kubernetes resource that behaves similarly to a job in that it runs to completion. The outcome of an AnalysisRun can be successful, failed, or inconclusive, and this result directly impacts the progression of the Rollout's update. If the AnalysisRun is successful, the update continues; if it fails, the update is aborted; and if it's inconclusive, the update is paused.|

Analysis resources allow Argo Rollouts to make informed decisions during the deployment process, like promoting a new version, rolling back to a previous version, or pausing the rollout for further investigation based on real-time data and predefined success criteria.

AnalysisRuns support various providers like Prometheus or multiple other monitoring solutions to obtain measurements for analysis. Those measurements can then be used to automate promotion decisions.

Besides just looking at metrics, there are other ways to decide if your rollout is doing well. The most basic (but commonly used) one might be the Kubernetes “Job” provider: if a job is successful, the metric is considered “successful". If the job returns with anything else than return code zero, the metric is considered “failed”.

The Web provider helps with seamless integration to custom services to help make promotion decisions.

Remember, it's not mandatory to use analysis and metrics when you're rolling out updates in Argo Rollouts.

If you want, you can control the rollout yourself. This means you can stop or advance the rollout whenever you choose. You can do this through the API or the command line. Also, you don't have to rely on automatic metrics for using Argo Rollouts. It's totally fine to combine automatic steps, like those based on analysis, with your own manual steps.

---

## Experiments
Experiments are an extended feature of Argo Rollouts designed to test and evaluate changes in two or more versions of an application in a controlled, temporary environment. The Experiment custom resource can launch AnalysisRuns alongside ReplicaSets. This is useful to confirm that new ReplicaSets are running as expected.

You can use experiments in Argo Rollouts to test different versions of your app at the same time. This is like doing A/B/C testing. You can set up each experiment with its own version of the app to see which one works best. Each experiment uses a template to define its specific version of the app.

The great thing about these experiments is that you can run several of them simultaneously, and each one is separate from the others. This means they don't interfere with each other.

To learn more about Analysis or Experiments, please consult the official documentation.

---














---

!!! AnalysisTemplate and AnalysisRun in Canary

Analysis Tempalte : A reusable blueprint for health checks - defines metrics, data sources (example Prometheus), and success or failure conditions

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: api-performance-check
spec:
  args:
  - name: service-name
  - name: namespace
  metrics:
  - name: check-success-rate
    provider:
      prometheus:
        address: http://prometheus.kub-prometheus-stack.svc.cluster.local.9090
        query: |
          sum(rate(http_requests_total{service_name="{{args.service-name}}",namespace="{{args.namespace}}",code!~"5.*"}[2m]))
          /
          sum(rate(http_requests_total{service_name="{{args.service-name}}",namespace="{{args.namespace}}"[2m]))
    count: 3 #(1)!
    interval: 20s #(2)!
    failureLimite: 1 #(3)!
    successCondition: result >= 0.99 #(4)!
```

1. Indique d'éxectuter 3 fois la query 
2. La query seras executer avec 20s d'intervalle
3. Si une seul des trois mesures échoue alors l'ensemble de l'analyse est considérer comme échoué
4. Uniquement réussi si 0.99 atteint

**background Analysis**
Continious monitoring that runs parallel to deployment stages

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: app-api
spec:
...
  strategy:
    canary:
      analysis:
        template:
        - templateName: api-performance-check
        startingStep: 2
        args:
        - name: service-name
          value: app-svc.default.svc.cluster.local
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 40
      - pause: {duration: 10m}
      - setWeight: 60
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 10m}
```

**Inline Analysis**
Discrete verification checkpoints that must pass before advancing

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: app-api
spec:
...
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 5m}
      - analysis:
          template:
          - templateName: api-performance-check
          args:
          - name: service-name
            value: app-svc.default.svc.cluster.local
```

!!! AnalysisTemplate and AnalysisRun in BlueGreen pre-promotion and post-promotion

**PrePromotion**
Test then switch - Validate before user exposure
```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: app-api
spec:
...
  strategy:
    blueGreen:
      activeService: active-svc
      previewService: preview-svc
      prePromotionAnalysis:
        template:
        - templateName: api-performance-check
        args:
        - name: service-name
          value: preview-svc.default.svc.cluster.local
```

**PostPromotion**
Switch then verify - Validate with real traffic, auto rollback
```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: app-api
spec:
...
  strategy:
    blueGreen:
      activeService: active-svc
      previewService: preview-svc
      scaleDownDelaySeconds: 600 # 10 minutes
      postPromotionAnalysis:
        template:
        - templateName: api-performance-check
        args:
        - name: service-name
          value: preview-svc.default.svc.cluster.local
```

## Demo: Health Check

## Demo AnalysisRun