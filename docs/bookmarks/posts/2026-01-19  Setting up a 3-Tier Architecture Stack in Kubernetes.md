---
title: "Setting up a 3-Tier Architecture Stack in Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://levelup.gitconnected.com/setting-up-a-3-tier-architecture-stack-in-kubernetes-55c6d9e5c7b3"
author:
  - "[[Jake Teo]]"
---
<!-- more -->

[Sitemap](https://levelup.gitconnected.com/sitemap/sitemap.xml)## [Level Up Coding](https://levelup.gitconnected.com/?source=post_page---publication_nav-5517fd7b58a6-55c6d9e5c7b3---------------------------------------)

Kubernetes, or K8s, is the gold standard for container orchestration even after its release by Google a decade ago. It coincides with the rise of Docker to bring about the standardisation and widespread adoption of containerisation, boosting its use across industries.

In this article, we will create a basic 3-Tier Architecture stack in Kubernetes to create a web application to predict your chances of surviving if you were on the doomed Titanic cruise ship as shown below.

For those who struggle to learn its basics, this will be a perfect place to understand most of the common resources in K8s, and how they work together.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*M2g575Wf7-1eqQwlQadmng.gif)

A web application to predict your survival in the Titanic. Image by author

*Some prerequisites: refer to my previous Medium articles on the basics of Kubernetes \[*[*1*](https://blog.devops.dev/the-very-basics-of-kubernetes-b036cfbd5999)*\] and how this example demo app works \[*[*2*](https://levelup.gitconnected.com/building-a-3-tier-architecture-with-docker-dcc58e478460)*\]. Install* [*kubectl*](https://kubernetes.io/docs/tasks/tools/#kubectl)*, the Kubernetes command line tool*

## Contents

**Preparation**  
\- [Create a Kubernetes cluster](https://levelup.gitconnected.com/#8f0e)  
\- [Upload images to DockerHub](https://levelup.gitconnected.com/#dd58)  
**Provisioning**  
\- [Frontend](https://levelup.gitconnected.com/#600e)  
\- [Backend](https://levelup.gitconnected.com/#c343)  
\- [Model](https://levelup.gitconnected.com/#eae4)  
\- [Database](https://levelup.gitconnected.com/#ed85)  
[**Kcustomize**](https://levelup.gitconnected.com/#2581)

## Preparation

### Create a Kubernetes Cluster

Every cloud service provider allows us to provision Kubernetes clusters easily. In this instance, we will use [DigitalOcean](https://www.digitalocean.com/) to do that, due to its ease of use and affordable rates. It should cost about $10 a month if you choose the lowest-tiered specifications.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*v4pm8khO8ewIZl-Y6kQpJw.png)

Create a cluster in Digital Ocean. Screenshot by author

On the main page of DigitalOcean, select Kubernetes and create a new cluster. It will take 5–15 minutes for the cluster to be provisioned.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*W4UJ7pDAyTMg7Q-oN4M4RQ.png)

Check the provision status, and download the kubeconfig file. Screenshot by author

When it is ready, on the dashboard, you should see the “Node Pool Status” as *Running*. Download the kubeconfig file on the left. This includes the Kubernetes cluster’s credentials, allowing you to access and provision resources from your local machine. It should have a name like `k8s-*-kubeconfig.yaml`.

```hs
# copy kubeconfig to default dir
cp k8s-1-32-2-do-1-sgp1-1746855129494-kubeconfig.yaml ~/.kube/config

# set kubectl as k in macOS
echo "alias k='kubectl'" >> ~/.zshrc
source ~/.zshrc
```

We will then copy the kubeconfig file to its default location at `~/.kube/config`, so that `kubectl` commands will be sent to this newly created cluster. Additionally, let’s create an alias so that `kubectl` can be called using ' `k'` instead, for convenience.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*G8Oqn6kDmFfiQj-UyM-5PA.png)

Create a namespace. Screenshot by author

With that done, let’s provision our first Kubernetes resource! `k create ns titanic` creates a new namespace, which is a logical compartment in the cluster to separate application tiers or projects. Should you create any resources without specifying the namespace, they will be created within the `default` namespace.

We can check that it is created using or `k get namespace` or `k get ns` in short.

### Upload Images to DockerHub

Our application stack consists of the frontend, backend and model servers, as well as the database. The database is MySQL, which can be pulled from the official image in DockerHub.

For the rest, since they are custom-coded, they need to be stored in a container registry so that they can be retrieved by Kubernetes later. These were also uploaded to DockerHub as public repositories.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*ImHHcFlrK8vpVSlpmAN7mg.png)

The required Docker images were uploaded to DockerHub. Screenshot by author

## Provisioning

### Frontend

With the preparations complete, let’s dive into the fun part! Let’s provision the frontend resources as displayed in the architecture diagram below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*IKfhKHAqrk0AROum-9PDTA.png)

Frontend resources include the load balancer and pods. Image by author

The logic of the Kubernetes resources we want to provision is stored in YAML files, also known as **manifest** files. First, we will create a manifest for the frontend web application. This is a type of resource called Deployment**.**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*04D5GuQ1pcO3Bd2G0ADyBA.png)

A deployment consists of a replicaset and pod. Image by author

A **deployment** allows zero-downtime rollouts and keeps versions of the deployment, so that rollbacks can be seamlessly done in the event of a failure. It also allows specification of how many replicas we want for the application, known as a **replicaset**. The smallest unit of a deployment is a **pod**, which is the resource that hosts your container application, in this case, the frontend webapp.

```hs
# frontend.yml, part I, frontend webapp

apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: titanic
  name: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: sassy19a/titanic-frontend
          imagePullPolicy: Always
          ports:
            - containerPort: 8501
          env:
            - name: backend_url
              value: "http://backend-svc.titanic.svc.cluster.local:8080"
```

A basic manifest for deployment is shown above. We chose the deployment resource in `kind: Deployment` and select the number of replicas as `replicas:2`.

Specifications for the pod are defined under `containers`, where we include the DockerHub image for the frontend app, the port and an environment variable for the backend’s URL. More on that later.

```hs
# frontend.yml, part II, load balancer
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-alb
  namespace: titanic
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
```

For the frontend application to be accessed via the internet, through a browser, we will need a type of **service** resource, called a **load balancer**. This allows traffic from the internet to be distributed evenly to each of the earlier two frontend pods being provisioned. The port is set to 80, so that we can access via HTTP.

Note that it can link to the frontend pods via the `selector: app: frontend`, which is the same as in the frontend `labels`.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*cYVJDCU7BMO9-M_wQszCiw.png)

Provision for the frontend and load balancer. Screenshot by author

Now let’s provision the deployment and load balancer by running `k apply -f frontend.yml -n titanic`. We can check the status of all the resources with `k get all -n titanic`. It shows two pods created, a replicaset, a deployment and a load balancer created. Notice that the load balancer’s external IP is pending.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*hGZalrxyE4HyDK9KXIT2cw.png)

Get the external IP address from the load balancer. Screenshot by author

Wait for a minute and try to query the load balancer again. You will see the external IP now, which contains an IPv4 and IPv6 address. Copy the former, in this case, `209.38.57.110` and load the address in your browser. You should be able to see the web application shown at the start of this article!

Certainly, using an IP address is not the usual way of accessing a website. It should be associated with a Domain Name System (DNS), but that is beyond the aim of this article.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*w-S71kMeek9sZPJhh6RD2g.png)

Error message when the frontend calls the backend. Screenshot by author

Now let’s try to run the prediction by pressing the button on the left. It will show an error message, as a request is sent to the backend, but there is none being provisioned yet.

### Backend

Now, let’s provision the backend application and link it to the frontend.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*VTuVa_vC-aZDvZsSVVnWqA.png)

Addition of backend deployment and cluster IP. Image by author

Before that, we need to introduce a new resource called **Secret**. As the backend needs to call the database, it must be able to log in with a username and password first. These credentials will be encrypted and stored securely in your Kubernetes namespace.

```hs
# secret.yml

apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: titanic
type: Opaque
data:
  username: cm9vdA==
  password: cm9vdHBhc3N3b3Jk

# convert to base64
# e.g., echo -n 'admin' | base64
```

In the secret manifest, we add the keys of `username` and `password`, whereby the values are base64 encoded. We should note that this manifest file with the plain credentials should never be committed directly to your repository for obvious security reasons.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*3m5OssIHA4Y1uxJfwl3Jiw.png)

Create a secret for database credentials. Screenshot by author

With that done, we can now set up the backend application’s manifest.

```hs
# backend.yml, part I, backend app

apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: titanic
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: sassy19a/titanic-backend
          imagePullPolicy: Always
          ports:
            - containerPort: 8080
          env:
            - name: model_url
              value: http://model-svc.titanic.svc.cluster.local:8081
            - name: DB_HOST 
              value: database-svc.titanic.svc.cluster.local
            - name: DB_PORT
              value: "3306"
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: username
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: password
            - name: DB_NAME
              value: titanic_db
```

The logic is similar to the earlier frontend deployment, but in the pods’ environment variables of `DB_PASSWORD` and `DB_NAME`, you can see that we are referring them to the earlier secret resource created.

```hs
# backend.yml, part II, clusterIP

---
apiVersion: v1
kind: Service
metadata:
  namespace: titanic
  name: backend-svc
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

For the frontend pods to communicate with the backend pods, a new kind of service called **ClusterIP**. This is a service used internally within a Kubernetes cluster, hence the name, and distributes the traffic to other pods via a single URL. Think of it as a load balancer for distributing internal loads.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*o0qAyD_zVpN53nmca9-Ocw.png)

Provisioning the backend resources, highlighted. Screenshot by author

When we provision these resources, notice that the ClusterIP’s `EXTERNAL-IP` is `<none>`, since this is only meant for internal use. Each ClusterIP also have a standard domain name, with the naming convention as `<clusterip-name>.<namespace>.svc.cluster.local`. This is why in the earlier frontend’s manifest, the environment variable for the backend URL is `backend-svc.titanic.svc.cluster.local`.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*uSLUr-7rPI7lSfMMagc4Rg.png)

Error message when the frontend calls the backend. Screenshot by author

With the backend resources provisioned, let’s try the prediction at the web app again. Now it shows a new error message as the backend is unable to access the model server and database.

### Model

Now, let’s provision the model server and link it to the backend pods.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Gsjerxo2Yqumhu-HPEn_5A.png)

Provisioning the model server to integrate with the backend. Image by author

There is nothing new from what we have done earlier. We create a deployment for the model server with just one replica. And then we create a ClusterIP to provide the load balancing for the traffic from the backend to reach the model server.

```hs
# model.yml, model server and clusterIP

apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: titanic
  name: model
spec:
  replicas: 1
  selector:
    matchLabels:
      app: model
  template:
    metadata:
      labels:
        app: model
    spec:
      containers:
        - name: model
          image: sassy19a/titanic-model
          imagePullPolicy: Always
          ports:
            - containerPort: 8081
---
apiVersion: v1
kind: Service
metadata:
  namespace: titanic
  name: model-svc
spec:
  selector:
    app: model
  ports:
    - protocol: TCP
      port: 8081
      targetPort: 8081
  type: ClusterIP
```

When we provision these, the namespace will now include the stated model resources.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*HV7yo0xEBitdB3OuI5ErfA.png)

Model resources are provisioned as highlighted. Screenshot by author

### Database

Now we are just left with the database, and we will see a complete and working 3-tier architecture stack shown below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*cpaLKkIZg3SBZTLdBJKEvw.png)

Full digram of the 3-tier architecture in a Kubernetes cluster. Image by author.

For the database deployment, we will use the default mySQL’s image in DockerHub. Notice that the database password is similarly referenced from what was created earlier at the backend section.

```hs
# database.yml, part I, database app & clusterIP

apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: titanic
  name: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
        - name: database
          image: mysql:9.2
          imagePullPolicy: Always
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: password
            - name: MYSQL_DATABASE
              value: titanic_db
          volumeMounts:
            - name: titanic-db-data
              mountPath: /data/db
            - name: init-script
              mountPath: /docker-entrypoint-initdb.d/init.sql
              subPath: init.sql
      volumes:
        - name: titanic-db-data
          persistentVolumeClaim:
            claimName: titanic-data-pvc
        - name: init-script
          configMap:
            name: mysql-initdb
---
apiVersion: v1
kind: Service
metadata:
  namespace: titanic
  name: database-svc
spec:
  selector:
    app: database
  ports:
    - protocol: TCP
      port: 3306
      targetPort: 3306
  type: ClusterIP
```

We can see two new specifications for the database pod. First, the `volumeMounts` indicate where the paths where files and data are linked. In this case, this refers to the external persistent storage block for storing the database tables, and an initialisation script when the database pod is first created.

Second, the `volumes` are linked the `volumeMounts`, whereby they are referenced to the persistent volume claim and a configMap with the initialisation script.

```hs
# database.yml, part II, persistent volume claim

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: titanic-data-pvc
  namespace: titanic
spec:
  storageClassName: do-block-storage
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Since a pod can be deleted or updated, saving the database data within a pod is not ideal. Therefore an external and persistent storage is required. DigitalOcean’s Kubernetes already include a **CSI (Container Storage Interface)** driver, that allows us to “claim” storage dynamically. This is called a **Persistent Volume Claim** **(PVC)**.

In the manifest, we need to specify the `storageClassName` as `do-block-storage` and indicate the storage size, which in this case is `1Gi`.

```hs
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-initdb
  namespace: titanic
data:
  init.sql: |
    CREATE DATABASE IF NOT EXISTS titanic_db;
    USE titanic_db;
    CREATE TABLE passengers (
        survived BOOLEAN,
        familysize INT,
        fare INT,
        sex INT,
        age INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
```

A **ConfigMap** allows us to store small snippets of text or code. This includes environment variables or in this case, an initialisation script. This script is in SQL to create the database and table with the specified schema.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Vu6A00kDKFRMyVim4rzgew.png)

After applying the resources and checking that each of them are successfully created, we can try the frontend web application again and successfully run your predictions without any errors!

## kustomize

We have provisioned each tier of the resources in separate manifest files. This can be done much easier using a tool called `kcustomize`. They come preinstalled in the latest version of `kubectl`, but you can install separately with `brew install kustomize`.

```hs
# kustomization.yml

resources:
- frontend.yml
- backend.yml
- database.yml
- model.yml

commonAnnotations:
  creator: jake
  requestor: jake
```

The logic of `kustomize` must be written in a file called `kustomization.yml`. Within, we have all the associated manifests. We can also include additional specifications to all the resources, like annotations. This allows us to avoid repeated code, adhering to the DRY principle.

```hs
└── manifests
    ├── backend.yml
    ├── database.yml
    ├── frontend.yml
    ├── kustomization.yml
    └── model.yml
```

Place this kustomize file in the same directory as the other manifests, and we can use a single command to apply or delete all the resources.

```hs
# provisioning
k apply -k <dir>

# deletion
k delete -k <dir>
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*kGTJAWS9LKgPVKnYWi7VWw.png)

Using kcustomize to apply to all resources. Screenshot by author

## Summary

We have covered the most commonly used Kubernetes resources from a high-level perspective. This includes services (load balancer, cluster IP), workloads (deployment, replicaset, pods) and other auxiliary resources (secret, configMap, persistent volume claim). While there’s certainly more depth to explore, this overview should provide a solid foundation for most developers to continue from here.

## References

1. Medium article: The very basics of Kubernetes \[[Link](https://medium.com/devops-dev/the-very-basics-of-kubernetes-b036cfbd5999)\]
2. Medium article: Building a 3-tier architecture with Docker \[[Link](https://medium.com/gitconnected/building-a-3-tier-architecture-with-docker-dcc58e478460)\]
3. Github repository: source codes and manifest files \[[Link](https://github.com/mapattacker/3-tier-Architecture)\]

Nature Lover | Tech Nerd | DevSecOps Lead

## More from Jake Teo and Level Up Coding

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--55c6d9e5c7b3---------------------------------------)