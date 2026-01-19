---
title: "6 Key Practices for Monitoring, Logging, and Runtime Security in Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@tamerbenhassan/6-key-practices-for-monitoring-logging-and-runtime-security-in-kubernetes-089a63e08ff7"
author:
  - "[[Tamer Benhassan]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

Imagine you have a treasure chest filled with valuable items.

To protect it, you would need to keep an eye on it, log who accesses it, and ensure its contents remain unchanged.

In the world of Kubernetes, your applications are like that treasure chest.

To protect them, you need to monitor activities, log important events, and secure them at runtime.

This article will explore six crucial practices for monitoring, logging, and ensuring runtime security in Kubernetes, complete with practical examples.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Tpi87VBXU2LHkJG3c_dm8g.png)

## 1\. Perform Behavioral Analytics of Syscall Process and File Activities

### Use Case: Detecting Malicious Activities at the Host and Container Level

Behavioral analytics helps in identifying unusual activities that may indicate a security breach.

Tools like Falco can monitor system calls and file activities to detect anomalies.

### Example: Using Falco

Falco is an open-source runtime security tool that can detect unexpected behavior in your Kubernetes environment.

Falco works by monitoring system calls made by containerized applications and comparing them to a set of predefined rules to identify suspicious activity.

### Installing Falco

You can install Falco using a Helm chart:

```c
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
helm install falco falcosecurity/falco
```

### Configuring Falco

Falco uses rules to define what behavior is considered normal or suspicious.

You can add custom rules by editing the Falco configuration.

```c
# Add this to your Falco configuration file
- rule: Write below etc
  desc: Detect any write below /etc
  condition: evt.type = "open" and evt.dir = < and fd.name startswith "/etc"
  output: "File below /etc opened for writing (user=%user.name command=%proc.cmdline file=%fd.name)"
  priority: WARNING
  tags: [filesystem, mitre_credential_access]
```

### Running Falco in a Pod

Here’s how you can run Falco inside a Kubernetes Pod:

```c
apiVersion: v1
kind: Pod
metadata:
  name: falco
spec:
  containers:
  - name: falco
    image: falcosecurity/falco:latest
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: dockersock
    - mountPath: /host/proc
      name: proc
      readOnly: true
    - mountPath: /host/boot
      name: boot
      readOnly: true
    - mountPath: /host/lib/modules
      name: modules
      readOnly: true
    - mountPath: /host/usr
      name: usr
      readOnly: true
  volumes:
  - name: dockersock
    hostPath:
      path: /var/run/docker.sock
  - name: proc
    hostPath:
      path: /proc
  - name: boot
    hostPath:
      path: /boot
  - name: modules
    hostPath:
      path: /lib/modules
  - name: usr
    hostPath:
      path: /usr
```

### What It Does

Falco monitors system calls and file system activities to detect potential security threats in real-time, helping to identify and respond to suspicious behavior.

The above example ensures Falco has the necessary access to monitor host-level system calls and directories.

## 2\. Detect Threats Within Physical Infrastructure, Apps, Networks, Data, Users, and Workloads

### Use Case: Comprehensive Threat Detection Across the Entire Stack

Threat detection tools can monitor various layers of your infrastructure to identify potential security issues.

### Example: Using Sysdig

Sysdig is a security tool that provides deep visibility into your containerized infrastructure.

It captures system calls and other OS-level events, providing insights into application behavior, network activity, and user actions.

### Installing Sysdig

Sysdig can be installed on your host system or within a container.

```c
# Install Sysdig on your host system
curl -s https://s3.amazonaws.com/download.draios.com/stable/install-sysdig | sudo bash

# Run Sysdig to capture system events
sysdig -pc -M 60 -w capture.scap
```

### Running Sysdig in a Pod

Here’s how to run Sysdig in a Kubernetes Pod:

```c
apiVersion: v1
kind: Pod
metadata:
  name: sysdig
spec:
  containers:
  - name: sysdig
    image: sysdig/sysdig:latest
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host/proc
      name: proc
      readOnly: true
    - mountPath: /host/sys
      name: sys
      readOnly: true
    - mountPath: /host/boot
      name: boot
      readOnly: true
    - mountPath: /host/lib/modules
      name: modules
      readOnly: true
  volumes:
  - name: proc
    hostPath:
      path: /proc
  - name: sys
    hostPath:
      path: /sys
  - name: boot
    hostPath:
      path: /boot
  - name: modules
    hostPath:
      path: /lib/modules
```

### What It Does

Sysdig captures system events and provides insights into application, network, and user activities, helping to detect threats across your entire stack.

It can be used to monitor for anomalies and unauthorized activities in real-time.

## 3\. Detect All Phases of Attack Regardless of Where It Occurs and How It Spreads

### Use Case: Monitoring the Entire Attack Lifecycle

Monitoring tools need to detect attacks at every stage, from initial access to lateral movement and data exfiltration.

### Example: Using ELK Stack (Elasticsearch, Logstash, Kibana)

The ELK Stack is a powerful solution for collecting, processing, and visualizing logs from your Kubernetes environment.

### Setting Up ELK Stack

Here’s how to set up the ELK Stack in your Kubernetes cluster:

```c
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logstash
spec:
  replicas: 1
  selector:
    matchLabels:
      app: logstash
  template:
    metadata:
      labels:
        app: logstash
    spec:
      containers:
      - name: logstash
        image: docker.elastic.co/logstash/logstash:7.10.0
        ports:
        - containerPort: 5044
        volumeMounts:
        - name: logstash-config
          mountPath: /usr/share/logstash/pipeline
  volumes:
  - name: logstash-config
    configMap:
      name: logstash-config
```

### Configuring Logstash

Create a ConfigMap to configure Logstash:

```c
apiVersion: v1
kind: ConfigMap
metadata:
  name: logstash-config
data:
  logstash.conf: |
    input {
      beats {
        port => 5044
      }
    }
    output {
      elasticsearch {
        hosts => ["http://elasticsearch:9200"]
        index => "%{[@metadata][beat]}-%{+YYYY.MM.dd}"
      }
    }
```

### What It Does

The ELK Stack collects and analyzes logs from various sources, allowing you to detect and investigate all phases of an attack within your Kubernetes environment.

This helps in identifying attack vectors and understanding the impact of security incidents.

## 4\. Perform Deep Analytical Investigation and Identification of Bad Actors

### Use Case: Investigating and Identifying Malicious Activities

Tools like Splunk can help perform deep analytical investigations to identify bad actors and understand the nature of attacks.

### Example: Using Splunk

Splunk can ingest, analyze, and visualize data from your Kubernetes environment.

### Installing Splunk

Download and install Splunk:

```c
# Install Splunk on your system
wget -O splunk-8.2.2-87344edfcdb4-Linux-x86_64.tgz 'https://www.splunk.com/page/download_track?file=8.2.2/splunk/linux/splunk-8.2.2-87344edfcdb4-Linux-x86_64.tgz&ac=&wget=true&name=wget&platform=linux&architecture=x86_64&version=8.2.2&product=splunk&typed=release'

# Extract and run Splunk
tar xvzf splunk-8.2.2-87344edfcdb4-Linux-x86_64.tgz
cd splunk
./splunk start --accept-license
```

## What It Does

Splunk provides advanced analytics capabilities, allowing you to investigate security incidents and identify malicious activities within your Kubernetes cluster.

It helps in understanding the root cause of incidents and taking corrective actions.

## 5\. Ensure Immutability of Containers at Runtime

### Use Case: Preventing Changes to Containers After Deployment

Ensuring that containers remain immutable at runtime helps maintain security and consistency.

### Example: Using Kubernetes Pod Security Policies

Pod Security Policies can enforce immutability by preventing changes to the container’s filesystem.

### Defining a Pod Security Policy

Create a PodSecurityPolicy to enforce read-only root filesystems:

```c
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: read-only-root-filesystem
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  readOnlyRootFilesystem: true
  fsGroup:
    rule: RunAsAny
  runAsUser:
    rule: MustRunAsNonRoot
  seLinux:
    rule: RunAsAny
  supplementalGroups:
\`\`\`yaml
    rule: RunAsAny
  volumes:
  - configMap
  - emptyDir
  - persistentVolumeClaim
  - projected
  - secret
  - downwardAPI
```

### Applying the Pod Security Policy

To apply the PodSecurityPolicy, you need to create a Role and RoleBinding:

```c
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: psp-role
  namespace: default
rules:
- apiGroups: ['policy']
  resources: ['podsecuritypolicies']
  verbs:     ['use']
  resourceNames:
  - read-only-root-filesystem

---

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: psp-rolebinding
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: psp-role
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
```

### What It Does

This policy ensures that containers have a read-only root filesystem, preventing unauthorized changes during runtime.

By enforcing immutability, you maintain a consistent and secure environment for your applications.

## 6\. Use Audit Logs to Monitor Access

### Use Case: Tracking and Monitoring Access to Resources

Audit logs help track access and changes to resources, providing a record for security audits and investigations.

### Example: Enabling Kubernetes Audit Logging

Configure the Kubernetes API server to enable audit logging.

### Configuring the API Server

Edit the Kubernetes API server configuration to enable audit logging:

```c
# /etc/kubernetes/manifests/kube-apiserver.yaml
spec:
  containers:
  - name: kube-apiserver
    command:
    - kube-apiserver
    - --audit-log-path=/var/log/kubernetes/audit.log
    - --audit-policy-file=/etc/kubernetes/audit-policy.yaml
```

### Creating an Audit Policy

Define an audit policy file to specify what events should be logged:

```c
# /etc/kubernetes/audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["pods", "services", "configmaps"]
```

### What It Does

Enabling audit logs provides a detailed record of access and changes to your Kubernetes resources.

This helps monitor and investigate security events, ensuring that any unauthorized access or modifications are detected and addressed promptly.

## Conclusion

Monitoring, logging, and runtime security are critical components of maintaining a secure Kubernetes environment.

By performing behavioral analytics, detecting threats across the entire stack, monitoring all phases of attacks, conducting deep investigations, ensuring container immutability, and using audit logs, you can significantly enhance the security and resilience of your Kubernetes deployments.

## More from Tamer Benhassan

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--089a63e08ff7---------------------------------------)