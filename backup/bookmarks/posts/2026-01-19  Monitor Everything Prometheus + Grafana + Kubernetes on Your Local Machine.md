---
title: "Monitor Everything: Prometheus + Grafana + Kubernetes on Your Local Machine"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@inyiri.io/monitor-everything-prometheus-grafana-kubernetes-on-your-local-machine-95a64ac5cfe2"
author:
  - "[[Johnstx]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*8eAvIOhdyEo0gpRo6zPEoA.jpeg)

*“Build a self-hosted monitoring pipeline using Prometheus, Grafana, and Kubernetes in a local CI/CD environment.”*

To ensure your application is **stable and healthy** in production, you need effective monitoring. Here is a demonstration to implement a **monitoring stack** using:

- **Prometheus** (metrics collection)
- **Grafana** (visualization)
- **Alertmanager** (alerts)
- **KIND** (Kubernetes in Docker)
- **Jenkins** (CI/CD pipeline)

### 🧱 Prerequisites

- Node.js app (e.g. Bluerise Weather App)
- Docker & DockerHub/GitHub Container Registry access
- Jenkins installed locally
- KIND installed
- Helm installed

1\. 🛠️ Node.js Application Setup

### 🔗 Dependencies

Inside `/testApp/Bluerise-Weather-App/`:

```c
npm install express dotenv axios prom-client
```

🧩 Modify `index.js`

Add Prometheus client metrics to the app:

```c
require('dotenv').config();
const express = require('express');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const client = require('prom-client');  // 📈 Add prom-client

const app = express();
const API_KEY = process.env.WEATHER_API_KEY;
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// 📊 Prometheus metrics setup
const register = new client.Registry();
client.collectDefaultMetrics({ register }); // collects CPU, memory, etc.

const weatherCheckCounter = new client.Counter({
  name: 'weather_checks_total',
  help: 'Total number of weather data fetches',
});
register.registerMetric(weatherCheckCounter);

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.post('/weather', async (req, res) => {
  const city = req.body.city;
  const url = \`http://api.weatherapi.com/v1/current.json?key=${API_KEY}&q=${encodeURIComponent(city)}\`;

  try {
    const response = await axios.get(url);
    const weather = response.data;

    // 👇 Increment weather check counter
    weatherCheckCounter.inc();

    let responseHtml = fs.readFileSync(path.join(__dirname, 'public', 'response.html'), 'utf8');
    responseHtml = responseHtml.replace('{{city}}', weather.location.name);
    responseHtml = responseHtml.replace('{{country}}', weather.location.country);
    responseHtml = responseHtml.replace('{{temp}}', weather.current.temp_c);
    responseHtml = responseHtml.replace('{{condition}}', weather.current.condition.text);
    responseHtml = responseHtml.replace('{{humidity}}', weather.current.humidity);
    responseHtml = responseHtml.replace('{{wind}}', weather.current.wind_kph);

    res.send(responseHtml);
  } catch (err) {
    res.send(\`
      <p>Error: Could not fetch weather data. Please check the city name.</p>
      <a href="/">Try again</a>
    \`);
  }
});

// 📊 Metrics endpoint for Prometheus
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.listen(PORT, () => {
  console.log(\`🌐 Server is running on http://localhost:${PORT}\`);
});
```

✅ **Test locally:**

```c
node index.js  
curl http://localhost:3000/metrics
```

2\. 🐳 Containerize the App

### 📦 Dockerfile

```c
# Use the official Node.js image as the base image
FROM node:18

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies declared in package.json
RUN npm install 

# Copy the rest of the application code
COPY . .

# Expose the port the app will run on (for example, port 3000)
EXPOSE 3000

# Command to run the app
CMD ["npm", "start"]
```

3\. 🤖 Jenkins Pipeline Setup

### 📁 Jenkinsfile

```c
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'johnstx/bluerise'
        IMAGE_TAG = 'v1.3'
        REGISTRY_CREDENTIALS_ID = 'dockerhub-login'  // Jenkins credentials ID
    }

    stages {

        stage('Clean Workspace') {
          steps {
                    cleanWs() // Cleans the workspace before running the pipeline
          }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Login to Docker Registry') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${REGISTRY_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                    }
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout'
        }
    }
}
```

4\. ☸️ Kubernetes Setup (KIND)

🧪 Create Cluster

```c
kind create cluster --name bluerise
```

### 📂 Apply Deployment & Service

Create `bluerise-deploy.yaml`:

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bluerise
spec:
  replicas: 1
  selector:
    matchLabels:
      app: bluerise
  template:
    metadata:
      labels:
        app: bluerise
    spec:
      containers:
        - name: bluerise
          image: johnstx/bluerise:v1.0
          ports:
            - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: bluerise
  labels:
    app: bluerise
spec:
  ports:
    - port: 3000
      targetPort: 3000
  selector:
    app: bluerise
```
```c
kubectl apply -f bluerise-deploy.yaml
```

5\. 📊 Prometheus + Grafana Monitoring Stack

🎯 Add Helm Repo & Install Stack

```c
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install monitors prometheus-community/kube-prometheus-stack -n monitoring
```

6\. 📡 Create ServiceMonitor

Save as `servicemonitor.yaml:`

```c
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: bluerise-monitor
  labels:
    release: monitors
spec:
  selector:
    matchLabels:
      app: bluerise
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
  namespaceSelector:
    matchNames:
      - default
```
```c
kubectl apply -f servicemonitor.yaml
```

7\. 🔎 Access Prometheus & Grafana

## 🧭 Prometheus

```c
kubectl port-forward svc/monitors-kube-prometheus-prometheus -n monitoring 9090
```

Open: [http://localhost:9090/targets](http://localhost:9090/targets)  
Check if `bluerise` target is **UP**

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*y4zJ41qYFvWiOYHRq1w7xQ.jpeg)

check for a query e.g

```c
weather_check_total
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*4GfNGBBc_TXksOtiDgKs1A.jpeg)

**Grafana** helps plot these metrics into dashboards. Common dashboard panels include:

- ✅ Request rate over time
- ⏱️ Request latency (95th percentile)
- ❌ Error rate (4xx/5xx)
- 📊 Memory/CPU usage per pod e.t.c

## 📈 Grafana

```c
kubectl port-forward svc/monitors-grafana -n monitoring 3000:80
```

Open: [http://localhost:3000](http://localhost:3000/)  
**Login:**

User: `admin`

Password: `prom-operator` (or check via `kubectl get secret`)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rhGMRFsCrNSP8Dsva3GfIA.jpeg)

A grafana dashboard

*Now go ahead and grab those metrics with the Prometheus stack — because what you don’t measure, you can’t improve!!*

#Grafana #prometheus-stack #ServiceMonitors #Alertmanager #Monitoring #metrics #healthchecks

Sharing lessons and real-world experiences from the trenches of Cloud Infrastructure, Security Automation, DevSecOps, CI/CD, GitOps and Platform Reliability.

## More from Johnstx

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--95a64ac5cfe2---------------------------------------)