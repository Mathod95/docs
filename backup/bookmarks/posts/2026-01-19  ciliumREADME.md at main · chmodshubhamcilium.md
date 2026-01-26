---
title: "cilium/README.md at main · chmodshubham/cilium"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://github.com/chmodshubham/cilium/blob/main/README.md"
author:
  - "[[chmodshubham]]"
---
<!-- more -->

[Open in github.dev](https://github.dev/) [Open in a new github.dev tab](https://github.dev/) [Open in codespace](https://github.com/codespaces/new/chmodshubham/cilium/tree/main?resume=1)

## Cilium

3-Node kind cluster with Cilium CNI + Hubble enabled

## Cilium Architecture

[![image](https://private-user-images.githubusercontent.com/97805339/243391314-9b315e92-8a6b-4efe-b624-6bc3559dc430.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzOTEzMTQtOWIzMTVlOTItOGE2Yi00ZWZlLWI2MjQtNmJjMzU1OWRjNDMwLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTFhZTk4ODIxZTAzMzc5Y2RiMGY2MmQyMDE2OWQyZTU0YTY2MzJmNzliMDc5ZWY3OGQ3YWVhNzg3YzZjNjI1YjQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.iifDS6OE_GORu7aMwukXz7cabKkPAjWFalFzde0I82k)](https://private-user-images.githubusercontent.com/97805339/243391314-9b315e92-8a6b-4efe-b624-6bc3559dc430.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzOTEzMTQtOWIzMTVlOTItOGE2Yi00ZWZlLWI2MjQtNmJjMzU1OWRjNDMwLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTFhZTk4ODIxZTAzMzc5Y2RiMGY2MmQyMDE2OWQyZTU0YTY2MzJmNzliMDc5ZWY3OGQ3YWVhNzg3YzZjNjI1YjQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.iifDS6OE_GORu7aMwukXz7cabKkPAjWFalFzde0I82k)

## Installation Methods

Cilium supports two methods of installation:

The CLI tool makes it easy to get started with Cilium, especially when you’re first learning about it. It uses the Kubernetes API directly to examine the cluster corresponding to an existing kubectl context and choose appropriate install options for the Kubernetes implementation detected. We’ll be using the Cilium CLI install method for most of the labs in the course.

The Helm chart method is meant for advanced installation and production environments where you want granular control of your Cilium installation. It requires you to manually select the best datapath and IPAM mode for your particular Kubernetes environment. You can learn more about the Helm chart installation method in the Cilium documentation resources. We’ll use the Helm chart install method in a later chapter when getting familiar with some advanced capabilities.

## Pre-requisite

We will need a Kubernetes cluster appropriately configured and ready for an external CNI to be installed. We were using `kind` cluster for this. [Install kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.19.0/kind-linux-amd64
sudo chmod +x ./kind
sudo mv ./kind /usr/local/bin
```

To verify:

```
which kind
kind version
```

[![image](https://private-user-images.githubusercontent.com/97805339/243187181-e0e4a400-1e43-4d2e-9e04-42907ba74bd6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMxODcxODEtZTBlNGE0MDAtMWU0My00ZDJlLTllMDQtNDI5MDdiYTc0YmQ2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTk3NWVkYzg1YmUxYzBhMzYzZmYyNGE0NjMyMDU5ZjlmODc3ZTE2NGU0ZDdlY2FhZWUzMWUwMjczYjI0YTMyZjAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.VYLzXsxlmcWNTlmAaWIrMTh4rlbDyjFSXYbUY-gObeE)](https://private-user-images.githubusercontent.com/97805339/243187181-e0e4a400-1e43-4d2e-9e04-42907ba74bd6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMxODcxODEtZTBlNGE0MDAtMWU0My00ZDJlLTllMDQtNDI5MDdiYTc0YmQ2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTk3NWVkYzg1YmUxYzBhMzYzZmYyNGE0NjMyMDU5ZjlmODc3ZTE2NGU0ZDdlY2FhZWUzMWUwMjczYjI0YTMyZjAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.VYLzXsxlmcWNTlmAaWIrMTh4rlbDyjFSXYbUY-gObeE)

> **Note**: kind version >= `v0.7.0`

`kind` does not require `kubectl`, but we will not be able to perform some of the operations without it. [Install Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)

```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

To verify:

```
kubectl version --client
```
```
sudo apt-get update

sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker ${USER}
su - ${USER}
sudo chmod 666 /var/run/docker.sock
```

## Procedure

Here is the YAML configuration file for a 3-node kind cluster with default CNI disabled. Save this locally to your workstation as `kind-config.yaml` with the contents:

```
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
networking:
  disableDefaultCNI: true
```

Now create a new kind cluster using this configuration:

```
kind create cluster --config=kind-config.yaml
```

Kind will create the cluster and will configure an associated `kubectl` context. Confirm your new kind cluster is the default `kubectl` context:

```
kubectl config current-context
```

Now you should be able to use kubectl and the Cilium CLI tool and interact with your newly minted kind cluster.

```
kubectl get nodes
```

[![image](https://private-user-images.githubusercontent.com/97805339/243187698-e1db918a-512a-4855-a6d9-66e5337a5573.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMxODc2OTgtZTFkYjkxOGEtNTEyYS00ODU1LWE2ZDktNjZlNTMzN2E1NTczLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTk2YTZiOGI0ZjkyMWQ0OWQwZjYzNTYyOTU5MTY3ZTgwZGM4MmIyYjQ2YmY5ZTdhOGY1YmI4NzU3NjVlZWE5NTMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Yz_520gYsZc8Jk32IrwBWgkGBTN_NctJnACrrtuAQBA)](https://private-user-images.githubusercontent.com/97805339/243187698-e1db918a-512a-4855-a6d9-66e5337a5573.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMxODc2OTgtZTFkYjkxOGEtNTEyYS00ODU1LWE2ZDktNjZlNTMzN2E1NTczLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTk2YTZiOGI0ZjkyMWQ0OWQwZjYzNTYyOTU5MTY3ZTgwZGM4MmIyYjQ2YmY5ZTdhOGY1YmI4NzU3NjVlZWE5NTMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Yz_520gYsZc8Jk32IrwBWgkGBTN_NctJnACrrtuAQBA)

> **Note**: Because you have created the cluster without a default CNI, the Kubernetes nodes are in a NotReady state.

[Download and install](https://docs.cilium.io/en/v1.13/gettingstarted/k8s-install-default/#install-the-cilium-cli) the Cilium CLI

```
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/master/stable.txt)
CLI_ARCH=amd64
if [ "$(uname -m)" = "aarch64" ]; then CLI_ARCH=arm64; fi
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-${CLI_ARCH}.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin
rm cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
```

To verify:

```
cilium version
```

[![image](https://private-user-images.githubusercontent.com/97805339/243379441-b06679e0-2509-4bb7-a5dc-c45488643d99.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzNzk0NDEtYjA2Njc5ZTAtMjUwOS00YmI3LWE1ZGMtYzQ1NDg4NjQzZDk5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWRlM2ZjNjRmMTMyNGEwNGUxODVmYTdjMTU4ODI4YTY1YTJlY2Q3MjI3OGE3ODA4NmZlMGRhMGI5ZTZiNTZkMTYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.bhMzbuprDyitm6RHLupqQ4Bhjm4565x6D6e_3ITIAck)](https://private-user-images.githubusercontent.com/97805339/243379441-b06679e0-2509-4bb7-a5dc-c45488643d99.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzNzk0NDEtYjA2Njc5ZTAtMjUwOS00YmI3LWE1ZGMtYzQ1NDg4NjQzZDk5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWRlM2ZjNjRmMTMyNGEwNGUxODVmYTdjMTU4ODI4YTY1YTJlY2Q3MjI3OGE3ODA4NmZlMGRhMGI5ZTZiNTZkMTYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.bhMzbuprDyitm6RHLupqQ4Bhjm4565x6D6e_3ITIAck)

We’ll be installing the default Cilium image into the Kubernetes cluster we’ve prepared.

```
cilium install
```

To verify:

```
cilium status --wait
```

[![image](https://private-user-images.githubusercontent.com/97805339/243383200-41b8a21b-8c8d-48dd-8cb3-f8c8c6071167.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzODMyMDAtNDFiOGEyMWItOGM4ZC00OGRkLThjYjMtZjhjOGM2MDcxMTY3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTc1YjE2ZTU2ODE5ODUxMjg0MmE5YzZmY2E1NmZlOTJiNzg1ZjRmZDAzYzMwZmUzYzlmNTRlOGM2YTUxOGI1Y2MmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.edjHL2-zU42UgBDOKFoexOMgIM1T4TQT4sVeZ7rpkUI)](https://private-user-images.githubusercontent.com/97805339/243383200-41b8a21b-8c8d-48dd-8cb3-f8c8c6071167.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzODMyMDAtNDFiOGEyMWItOGM4ZC00OGRkLThjYjMtZjhjOGM2MDcxMTY3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTc1YjE2ZTU2ODE5ODUxMjg0MmE5YzZmY2E1NmZlOTJiNzg1ZjRmZDAzYzMwZmUzYzlmNTRlOGM2YTUxOGI1Y2MmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.edjHL2-zU42UgBDOKFoexOMgIM1T4TQT4sVeZ7rpkUI)

```
cilium hubble enable --ui
```

To verify:

```
cilium status
```

[![image](https://private-user-images.githubusercontent.com/97805339/243384038-6b0b59fb-da81-4d2f-904c-02c172c158bb.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzODQwMzgtNmIwYjU5ZmItZGE4MS00ZDJmLTkwNGMtMDJjMTcyYzE1OGJiLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTYzNzc5NDY5YTRiZjkyNGE3MzdkYzlhOTQxOGRhN2E1ZGJhZTIxMjYyYWY0ZTQ1MzI5YjJmMDBlNmIzOTIwYzEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.NSNL9ip707jsmI_zXpYvUiBZOQ0PA-Q7qzHNg7xaunw)](https://private-user-images.githubusercontent.com/97805339/243384038-6b0b59fb-da81-4d2f-904c-02c172c158bb.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzODQwMzgtNmIwYjU5ZmItZGE4MS00ZDJmLTkwNGMtMDJjMTcyYzE1OGJiLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTYzNzc5NDY5YTRiZjkyNGE3MzdkYzlhOTQxOGRhN2E1ZGJhZTIxMjYyYWY0ZTQ1MzI5YjJmMDBlNmIzOTIwYzEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.NSNL9ip707jsmI_zXpYvUiBZOQ0PA-Q7qzHNg7xaunw)

The Cilium CLI tool also provides a command to install a set of connectivity tests in a dedicated Kubernetes namespace. We can run these tests to validate that the Cilium install is fully operational:

```
cilium connectivity test --request-timeout 30s --connect-timeout 10s
```

> **Note**: The connectivity tests require at least two worker nodes to successfully deploy in a cluster. The connectivity test pods will not be scheduled on nodes operating in the control-plane role. If you did not provision your cluster with two worker nodes, the connectivity test command may stall waiting for the test environment deployments to complete.

With Cilium now installed, we can use kubectl to confirm that the nodes are now ready and the required Cilium operational components are present in the cluster:

```
kubectl get nodes
kubectl get daemonsets --all-namespaces
kubectl get deployments --all-namespaces
```

[![image](https://private-user-images.githubusercontent.com/97805339/243394232-2da14535-18fe-4431-836d-da418ef31c64.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzOTQyMzItMmRhMTQ1MzUtMThmZS00NDMxLTgzNmQtZGE0MThlZjMxYzY0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTIxZjQzODk1YWI4NGVhZTcyMmE5OTg2ZWMyMzk1YzcxOTAxNjc2NzYwODQ1NmZlODZmYmRlNDE1MWE2OTAxMmUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.0-SIqhZHPwj0nm_bRv5WfpVaeeh5vxOG_keQaxTaao0)](https://private-user-images.githubusercontent.com/97805339/243394232-2da14535-18fe-4431-836d-da418ef31c64.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3Njg4MjA1NzMsIm5iZiI6MTc2ODgyMDI3MywicGF0aCI6Ii85NzgwNTMzOS8yNDMzOTQyMzItMmRhMTQ1MzUtMThmZS00NDMxLTgzNmQtZGE0MThlZjMxYzY0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMTklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTE5VDEwNTc1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTIxZjQzODk1YWI4NGVhZTcyMmE5OTg2ZWMyMzk1YzcxOTAxNjc2NzYwODQ1NmZlODZmYmRlNDE1MWE2OTAxMmUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.0-SIqhZHPwj0nm_bRv5WfpVaeeh5vxOG_keQaxTaao0)

The cilium daemonset is running on all 3 nodes in the cluster, and the `cilium-operator` deployment is running on a single node.

Now, `Cilium` is successfully installed.