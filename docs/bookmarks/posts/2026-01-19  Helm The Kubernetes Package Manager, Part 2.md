---
title: "Helm: The Kubernetes Package Manager, Part 2"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://olymahmud.medium.com/helm-the-kubernetes-package-manager-part-2-4aee3048bb0e"
author:
  - "[[M. Oly Mahmud]]"
---
<!-- more -->

[Sitemap](https://olymahmud.medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Mcogskras9IKUxM1bP1ycw.png)

Helm: The Kubernetes Package Manager Part 2

In the first part of this series, we explored the basics of Helm. Now, in Part 2, we’ll create our own Helm chart for an Express.js application that we previously containerized and deployed to Kubernetes using manifest files.

## Step 1: Scaffold A Helm Chart

We start by creating the chart using Helm’s built-in scaffolding tool:

```c
helm create kube-express
```

This command generates a Helm chart with default files and folder structure. The structure looks like this:

```c
kube-express
├── charts
├── Chart.yaml
├── templates
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── NOTES.txt
│   ├── secret.yaml
│   ├── service.yaml
│   └── tests
│       └── test-connection.yaml
└── values.yaml
```

The default templates include many files, but since we don’t need everything for our simple application, we can clean it up by removing the unnecessary ones.

## Step 2: Clean Up Default Templates

We delete `ingress.yaml`, `hpa.yaml`, and `serviceaccount.yaml` from the `templates` folder to keep only what we need for our Express app. The remaining files will be `deployment.yaml`, `service.yaml`, `secret.yaml`, and `NOTES.txt`.

## Step 3: Configure Deployment.yaml

We define how our application will be deployed in Kubernetes. Here’s our `templates/deployment.yaml`:

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.deployment.deploymentName }}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {{ .Values.deployment.deploymentName }}
  template:
    metadata:
      labels:
        app: {{ .Values.deployment.deploymentName }}
    spec:
      containers:
      - name: {{ .Values.deployment.deploymentName }}
        image: olymahmudmugdho/express-app-kubernetes:latest
        ports:
        - containerPort: 3000
        env:
        - name: {{ .Values.deployment.environment.envName }}
          valueFrom:
            secretKeyRef:
              name: {{ .Values.deployment.environment.secretName }}
              key: {{ .Values.deployment.environment.secretKey }}
```

### Why Use {{.Values.\* }} Syntax?

In Helm templates, `{{ .Values.* }}` refers to values defined in `values.yaml`. This allows us to reuse the same chart across environments by simply changing the `values.yaml`. It makes the chart dynamic and configurable without changing the template files.

## Step 4: Configure Service.yaml

Our service exposes the application inside the cluster:

```c
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.service.serviceName }}
spec:
  selector:
    app: {{ .Values.service.selector.app.appName }}
  ports:
  - protocol: {{ .Values.service.protocol }}
    port: {{ .Values.service.port }}
    targetPort: 3000
  type: {{ .Values.service.type }}
```

This is a `NodePort` service that maps external traffic to port `80` on the cluster nodes, which will route it to the port `3000` Inside the container.

## Step 5: Configure Secret.yaml

We create a Kubernetes secret that stores sensitive information such as API keys, environment variables, etc.:

```c
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Values.secret.name }}
type: {{ .Values.secret.type }}
data:
  {{ .Values.secret.data.key }}: {{ .Values.secret.data.value }}  # Base64 encoded
```

We can now reference this secret in our deployment using the environment configuration we defined earlier.

## Step 6: Add A NOTES.txt

Helm allows us to show helpful output after installation using a `NOTES.txt` file in the templates folder. Here’s our version:

```c
{{ .Values.name }} app  
Run the app by running the following command:  
kubectl port-forward svc/{{ .Values.service.name }} 3000:80
```

This helps users understand how to access the app after it’s installed.

## Step 7: Update values.yaml

We define all dynamic values for the chart here:

```c
name: express-app

deployment:
  deploymentName: express-app
  environment:
    envName: MY_SECRET
    secretName: my-secret
    secretKey: MY_SECRET

service:
  serviceName: express-app-service
  selector:
    app:
      appName: express-app
  protocol: TCP
  port: 80
  type: NodePort

secret:
  name: my-secret
  type: Opaque
  data:
    key: MY_SECRET
    value: bXluZXdzZWNyZXR2YWx1ZQ==  # Base64 encoded 'mynewsecretvalue'This file keeps our configuration DRY and reusable.
```

This file keeps our configuration DRY and reusable.

## Step 8: Package And Install The Helm Chart

Now that our chart is ready, we can package and install it. First, we navigate to the directory where the `kube-express` folder exists:

```c
cd path/to/your/project/root
ls
```

You should see the output like this

```c
kube-express
```

Then, we run:

```c
helm package kube-express
```

This generates a `.tgz` file, which is a Helm package. To install the chart into your cluster:

```c
helm install kube-express kube-express
```

To verify the installation:

```c
helm list --all-namespaces
```

To see previously uninstalled or failed releases, add `-a`:

```c
helm list --all-namespaces -a
```

To render the template output without installing:

```c
helm template kube-express
```

To uninstall the release:

```c
helm uninstall kube-express
```

## Conclusion

In the second part of this series on Helm, we have explored the basics of Helm and created and installed our own Helm chart.

*Thanks for reading.*

## More from M. Oly Mahmud

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--4aee3048bb0e---------------------------------------)