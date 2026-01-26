# Installing Argo Rollouts

## Objective

Set up a local Kubernetes cluster using Kind, install Argo Rollouts, and understand how to access Argo Rollout resources.

## Prerequisites

- Basic understanding of Docker, Kubernetes, and command-line interface operations.
- Access to a computer with an internet connection.
- An installation of Kubernetes that you have full control over
  - See Chapter 2’s Deploying Kubernetes for Argo section for details on how to set one up for yourself

---

## Install Cluster and Argo Rollouts

**NOTE:** Steps 1-4 might not be necessary if you already followed the setup during a previous chapter.

1. Installing Docker
Ensure Docker is installed and running on your machine.
● Installation instructions can be found on the Docker website.

2. Installing Kind
Download and install Kind following the instructions from the Kind official website.

3. Creating a Kubernetes Cluster with Kind
Create a cluster by running the following command:

```bash
kind create cluster

```
This command creates a single-node Kubernetes cluster running inside a Docker container named `kind-kind`.

4. Installing kubectl
Instructions for downloading kubectl can be found in the Kubernetes official documentation.

5. Deploy Argo Rollouts
Create a namespace for Argo Rollouts using the following command:

```bash
kubectl create namespace argo-rollouts
```

Deploy Argo Rollouts using the quick start manifest:

```bash
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/download/v1.8.3/install.yaml
```

This will install custom resource definitions as well as the Argo Rollouts controller.
During this course we use Argo Rollouts in version 1.8.3. We recommend using the same version to ensure consistent results.

Verify that Argo Rollouts is installed by running the following command:

```bash
kubectl get pods -n argo-rollouts
```

6. Install Rollouts kubectl Plugin

Unlike Argo CD and Argo Workflows, Argo Rollouts uses a kubectl plugin as its CLI client.
Download the latest Argo Rollouts kubectl plugin version from

https://github.com/argoproj/argo-rollouts/releases/latest/.

On Ubuntu 24.04, you can install the CLI using the following commands:

```bash
wget https://github.com/argoproj/argo-rollouts/releases/download/v1.8.3/kubectl-argo-rollouts-linux-amd64 -O kubectl-argo-rollouts
chmod +x kubectl-argo-rollouts
sudo mv kubectl-argo-rollouts /usr/local/bin/
```

More detailed installation instructions can be found via the CLI installation documentation.

This is also available in Mac, Linux and WSL Homebrew. Use the following command:

```bash
brew install argoproj/tap/kubectl-argo-rollouts
```

Verify that the argo CLI is installed correctly by running the following command:

``` bash
kubectl argo rollouts version
```

7. UI Dashboard
For the sake of completeness it needs to be mentioned that Argo Rollouts ships with a fully
fledged UI Dashboard. It can be accessed via the kubectl argo rollouts dashboard
command and provides a nice overview and basic commands for administration.

```bash
kubectl argo rollouts dashboard
```

Output:

```bash
INFO[0000] Argo Rollouts Dashboard is now available at
http://localhost:3100/rollouts
INFO[0000] [core] [Channel #1 SubChannel #2]grpc:
addrConn.createTransport failed to connect to {Addr: "0.0.0.0:3100",
ServerName: "0.0.0.0:3100", }. Err: connection error: desc =
"transport: Error while dialing: dial tcp 0.0.0.0:3100: connect:
connection refused"
```

Despite any “connection refused” errors, you can now access it via the UI at
http://localhost:3100 or your VM’s public IP address at port 3100.

As the Dashboard is self-explanatory, we will not discuss it in detail during this course.
The Argo Rollouts Dashboard displaying a sample app “rollout-bluegreen”
NOTE: If no rollout resources are in place, the dashboard will display “Loading…”.

8. Optional: Shell Auto-Completion
To get easy access to Argo Rollout resources, the CLI can add shell completion code for several
shells. For bash, you can use the following command:
source <(kubectl-argo-rollouts completion bash)
Other shells are supported as well. Please refer to the completion command documentation for
more details.

9. Using Argo Rollouts
There are a wide variety of commands that you can use to control Argo Rollouts via the CLI, as
described in the -h output for the kubectl argo rollouts command. As a kubectl plugin, it
uses the Kubernetes API to perform all management tasks.
Here is a list of the most common commands to operate with Argo Rollouts:

```bash
kubectl get rollout
kubectl argo rollouts get rollout
kubectl argo rollouts promote
kubectl argo rollouts undo
```

---