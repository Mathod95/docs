---
title: "Kubernetes Networking Labyrinth: A Packet’s Journey from This Pod on This Node to That Pod on That…"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@seantywork/kubernetes-networking-labyrinth-a-packets-journey-from-this-pod-on-this-node-to-that-pod-on-that-485eb2876a84"
author:
  - "[[Taehoon Yoon]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PcPzzI1jCqFYsDAP6wka1A.png)

(For those who are running out of time, here is the link to each section)

[**The Setup of Google Cloud**](https://medium.com/@seantywork/#95a5)

[**The Setup of Kubernetes**](https://medium.com/@seantywork/#ecc7)

[**The Journey**](https://medium.com/@seantywork/#8c5b)

It’s not that Kubernetes is hard to get used to.

That it’s very difficult to find the right context where it serves as a good engineering choice, and that it’s almost impossible to convince the C-suite there is very little gain or overall slowdown in adopting Kubernetes in OUR cases, those were the real problems.

Those were the problems that put me off back in time when I was the one to deal with Kubernets both as a sysadmin and as a “cloud-native” software engineer.

Yes, I grew wary because of them.

And then just a few weeks ago, suddenly it felt like to me that the AI hype has done a great job stealing all the highlights and absurd marketing materials from Kubernetes. I sensed the frequency of the word “DevOps” and its equally quircky names in shiny context has noticeably declined recently (practically gone, I mean). It feels certainly more down to earth especially compared to about 2 or 3 years, precisely the time of ChatGPT’s launch.

Under this feeling, I guess this might be the right time for me to revisit and have a little fun with it again.

Back then, I had to set up a Kubernetes cluster on-premise bare-metal on a somewhat older Linux kernel with version 3.x. Therefore, it wasn’t possible to set up Cilium as a CNI because its required kernel version was at least 4.x. The alternative at the time was Calico. It wasn’t a bad one though, if not the best.

Even though I was free to use Cilium on the platform product I was working on, the fact that the main production cluster was based not on that one felt … unaligned. Also, while it was certainly a fun activity managing a bare metal on-premise cluster, it quickly turned not so much if the building’s power or network was unstable and I had to spend a total of 20 minutes going back and forth between where I was working and the site where our cluster was to fix the problem.

So, this time, I decided that this demonstration takes the exact opposite way:

On cloud, with Cilium.

As usual, get the source first. However, in this article, the use of the source might be minimal compared to other ones.

```c
git clone https://github.com/seantywork/linuxyz.git -b 2505-05

cd linuxyz/kube-net
```

Let’s dive in!

## The Setup of Google Cloud

**ALERT: This stage involves the actual creation of three VMs on Google Cloud. It will cost you handsomely if you forget to delete those after this exercise. Do not forget to delete them after you’re finished if you are not rich enough to burn cash and regret nothing.**

Let’s create a Kubernetes cluster on Google Cloud. Of course, it doesn’t have to be Google Cloud, though. It’s just a personal preference.

First, we’re going to create VPC Network so that our cluster setup can remain separated from other network setup for normal virtual machines.

Go to cloud.google.com, and hit the console on the top right corner right beside your profile icon. If you click the left panel, you will a menu screen as below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*vftFafCqEKvjykkXU52b7A.png)

Down the list, as you can see in the above screen capture, there is a VPC Network menu. Click to get into it.

In this menu, you can see from the top part of your screen the “Create VPC Network” button. Click it and you will see something like below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*SNDXs-xz5MXpnb_AypMRAw.png)

I’ve configured the IP address range as 10.168.0.0/24 as you can see.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CqKG9Zq6Wm-2Geh_e09pEg.png)

There are a few default firewall rules for every VM that is going to use this particular network setting. As you can see below, check “allow-ssh”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*diUO4TNUovhcGRfMkHgFUw.png)

Hit, “create” after this.

After the creation of the network, hit “Firewall” on the left menu bar. You will see something like the screen below (it’s natural for you to have much fewer entries than the screen capture if this is the first time doing it)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*_WG7e6RpmwZPDbQz9r-F5w.png)

Hit “Create firewall rule” at the top of the screen.

Give this rule a recognizable name, and configure the network setting that is going to use this firewall rule as seen below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*WUQxj3Oj0VEx4p6UyaeNyQ.png)

You can check which ports and protocols Kubernetes is using from the below link.

```c
# https://kubernetes.io/docs/reference/networking/ports-and-protocols/
```

However, there will be a lot more ports that will be taken up as the traffic flows in and out between all nodes. So for simplicity’s sake, I configured the rule as below. Again, it’s not wise to use such a broad range if this is a serious one.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*RPFY1fHVo5VLCWmEonAfVQ.png)

Hit “create” if you’re done.

Again, back to the left menu bar, it’s time to create VMs using the Compute Engine menu.

We’re going to create three VMs. One of which will be the control plane and the other two will be our worker nodes.

To do so, let’s create the first one. I named it “node0”, set its region as Northern Virginia, and left the machine type as the default one, e2-medium. From this moment on, I’ll call the control plane “node0”, and the worker nodes “node1” and “node2” respectively.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5SV7eG6r_Wr6sfgBc70ypA.png)

Configure OS and disk as seen below. Ubuntu24.04 on x86/64 with 32GB of standard persistent disk.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*nHmfRVbKA4YzuHir1_Grxw.png)

Now it’s time to configure the network to the one we’ve just created “labyrinth”.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*1zH4fCYuFkINPppNAwM0JA.png)

After this, hit create. Then you will see in a moment that the VM setup is complete and the machine is up and running.

Repeat for the other two VMs with only the different names on each VM while setting every other thing the same way.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*PHj7LrNBilGSJTv0ospE8A.png)

If everything goes well, you will see something like the screen below.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9ryPzYgRrT4muH0E8PFXLg.png)

Do check if the internal IPs of the three VMs are in the same IP range you’ve set up in the “labyrinth” network setup.

Now, seeing those VMs up and running, it’s time to check out if the connectivity is all right. Hit “SSH” button on the right side of the “external IP” column. It will open up the web interface of the ssh connection into the specific VM you want to control.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*RyNfmx4ieNu5aN5E5r-q5w.png)

Use the cherished “nc” to check if there are no problems connecting those two.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*3d-zssd_I-QmObofrCKMEA.png)

Do this for each pair of VMs if you want to take extra care.

## The Setup of Kubernetes

This is where the source code is coming into play finally. On node0, copy or upload “node-ctl.sh”.

Do check out what this script does. Most importantly above all, you need to properly configure the IP value of this script before running it.

Change the IP value to the one that’s corresponding to the internal IP column value.

```c
HOME="/root" 
IP="10.168.0.2"
VERSION="1.33"
CILIUM_VERSION="1.17.4"
```

If you’re done, for convenience’s sake, switch user to root.

```c
sudo -i
```

After this, run the script.

```c
./node-ctl.sh
```

If everything is fine, you should see no errors after about 5 minutes or so, and be able to see this output as the command output.

```c
root@node-0:~# kubectl get nodes
NAME     STATUS   ROLES           AGE   VERSION
node-0   Ready    control-plane   73s   v1.33.1
```

Before jumping to other nodes to create worker nodes, use the below command and save the output somewhere. It’s needed for joining worker nodes to the control plane.

```c
root@node-0:~# kubeadm token create --print-join-command 
kubeadm join 10.168.0.2:6443 --token r61w3k.oom2m7zqt6m8p0fc --discovery-token-ca-cert-hash sha256:9dcf53ebff2089c12cf3af75e4540e58674ccd44282ba0285420852e4ebc5114
```

Now, move to the next node, node1.

Here, different from the node0, the script you need is “node-wrk.sh”

Switch to root again.

```c
sudo -i
```

Properly configure the IP value of the node-wrk.sh, and run it.

```c
./node-wrk.sh
```

If everything is successful, you can now paste and run the output you saved from the node0 to join the cluster.

```c
root@node-1:~# kubeadm join 10.168.0.2:6443 --token r61w3k.oom2m7zqt6m8p0fc --discovery-token-ca-cert-hash sha256:9dcf53ebff2089c12cf3af75e4540e58674ccd44282ba0285420852e4ebc5114 
[preflight] Running pre-flight checks
[preflight] Reading configuration from the "kubeadm-config" ConfigMap in namespace "kube-system"...
[preflight] Use 'kubeadm init phase upload-config --config your-config-file' to re-upload it.
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Starting the kubelet
[kubelet-check] Waiting for a healthy kubelet at http://127.0.0.1:10248/healthz. This can take up to 4m0s
[kubelet-check] The kubelet is healthy after 1.002236822s
[kubelet-start] Waiting for the kubelet to perform the TLS Bootstrap

This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.
```

If you get back to the node0 and run the command below, you will see now there are two nodes in the cluster.

```c
root@node-0:~# kubectl get nodes
NAME                                             STATUS   ROLES           AGE     VERSION
node-0                                           Ready    control-plane   8m21s   v1.33.1
node-1.us-east4-b.c.vpn-server-422904.internal   Ready    <none>          47s     v1.33.1
```

Repeat this process for node2.

```c
root@node-2:~# kubeadm join 10.168.0.2:6443 --token r61w3k.oom2m7zqt6m8p0fc --discovery-token-ca-cert-hash sha256:9dcf53ebff2089c12cf3af75e4540e58674ccd44282ba0285420852e4ebc5114
[preflight] Running pre-flight checks
[preflight] Reading configuration from the "kubeadm-config" ConfigMap in namespace "kube-system"...
[preflight] Use 'kubeadm init phase upload-config --config your-config-file' to re-upload it.
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Starting the kubelet
[kubelet-check] Waiting for a healthy kubelet at http://127.0.0.1:10248/healthz. This can take up to 4m0s
[kubelet-check] The kubelet is healthy after 1.003909562s
[kubelet-start] Waiting for the kubelet to perform the TLS Bootstrap

This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.
```

Check again on the node0.

```c
root@node-0:~# kubectl get nodes
NAME                                             STATUS   ROLES           AGE    VERSION
node-0                                           Ready    control-plane   12m    v1.33.1
node-1.us-east4-b.c.vpn-server-422904.internal   Ready    <none>          5m3s   v1.33.1
node-2.us-east4-b.c.vpn-server-422904.internal   Ready    <none>          51s    v1.33.1
```

As I’ve forgotten the line to properly short-naming the node in my script, I used the commands below to label the nodes.

```c
root@node-0:~# kubectl label node node-1.us-east4-b.c.vpn-server-422904.internal nodelabel=node-wrk-1 
node/node-1.us-east4-b.c.vpn-server-422904.internal labeled
root@node-0:~# kubectl label node node-2.us-east4-b.c.vpn-server-422904.internal nodelabel=node-wrk-2
node/node-2.us-east4-b.c.vpn-server-422904.internal labeled
```

Now, we’re ready to take on our journey!

## The Journey

Let’s create two namespaces. We’re going to deploy two same containers in each of the namespaces.

```c
root@node-0:~# kubectl create namespace wrk-1
namespace/wrk-1 created
root@node-0:~# kubectl create namespace wrk-2
namespace/wrk-2 created
root@node-0:~# vim 1.yaml
```

After the creation of the namespaces, check out the content of 1.yaml in the source code directory. As you can see below, the yaml file is a Kubernetes manifest file that deploys service object and deployment object. According to the yaml, we should be able to connect from the outside (but not the outside of Kubernetes cluster by itself) of the pod through port 9999 using TCP or UDP protocol. And importantly for our journey, at the end of the manifest, there is a nodeSelector field which is used to schedule a particular pod on a particular node. In our case, 1.yaml will be consumed to schedule one pod on node1 and 2.yaml for another pod on node2.

```c
apiVersion: v1
kind: Service
metadata:
  name: node-wrk-1-ubuntu24
  labels:
    app: node-wrk-1-ubuntu24
spec:
  type: ClusterIP
  ports:
  - name: tcp-9999
    port: 9999
    targetPort: 9999
    protocol: TCP
  - name: udp-9999
    port: 9999
    targetPort: 9999
    protocol: UDP
  selector:
    app: node-wrk-1-ubuntu24
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-wrk-1-ubuntu24
spec:
  selector:
    matchLabels:
      app: node-wrk-1-ubuntu24
  replicas: 1
  template:
    metadata:
      labels:
        app: node-wrk-1-ubuntu24
    spec:
      containers:
        - name: node-wrk-1-ubuntu24
          image: docker.io/seantywork/ubuntu24
          imagePullPolicy: Always
          ports:
          - containerPort: 9999
            protocol: TCP
          - containerPort: 9999
            protocol: UDP
      nodeSelector:
        nodelabel: node-wrk-1
```

The image it is pulling is pre-baked using the Dockerfile in the source directory.

```c
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

RUN apt-get update 

RUN apt-get install -y ncat tshark

CMD ["tail", "-f","/dev/null"]
```

Let’s deploy the app!

```c
root@node-0:~# kubectl -n wrk-1 apply -f ./1.yaml 
service/node-wrk-1-ubuntu24 created
deployment.apps/node-wrk-1-ubuntu24 created
```

You can check out if the deployment is successful using the command below (it might take some time to pull the image on the first run).

```c
root@node-0:~# kubectl -n wrk-1 get pods 
NAME                                   READY   STATUS    RESTARTS   AGE
node-wrk-1-ubuntu24-684f7d8fd6-2zncq   1/1     Running   0          112s
```

Now, do the same for the 2.yaml. Its content is practically identical to 1.yaml except for the name and the nodeSelector.

```c
root@node-0:~# kubectl -n wrk-2 apply -f ./2.yaml 
service/node-wrk-2-ubuntu24 created
deployment.apps/node-wrk-2-ubuntu24 created
```

Check out.

```c
root@node-0:~# kubectl -n wrk-2 get pods 
NAME                                   READY   STATUS    RESTARTS   AGE
node-wrk-2-ubuntu24-85748464f7-mwmrt   1/1     Running   0          3m5s
```

Now, it’s time to install the guide in chief throughout our journey, tshark. It’s the command line version of the famous packet capture tool WireShark. We’re going to install it on node1 and node2.

```c
root@node-1:~# apt update && apt install -y tshark
```
```c
root@node-2:~# apt update && apt install -y tshark
```

What we’re trying to do here is to let a server run on node2 and make a connection from node1 to the server. But, before doing so, let’s restart the in-cluster DNS service called coredns.

```c
root@node-0:~# kubectl -n kube-system rollout restart deployment coredns
```

Let’s enter a pod on node1, and another on node2. Your pod name will obviously differ.

```c
root@node-0:~# kubectl -n wrk-1 get pods
NAME                                   READY   STATUS    RESTARTS   AGE
node-wrk-1-ubuntu24-684f7d8fd6-2zncq   1/1     Running   0          13m
root@node-0:~# kubectl -n wrk-1 exec -it node-wrk-1-ubuntu24-684f7d8fd6-2zncq -- /bin/bash
root@node-wrk-1-ubuntu24-684f7d8fd6-2zncq:/workspace#
```
```c
root@node-0:~# kubectl -n wrk-2 get pods
NAME                                   READY   STATUS    RESTARTS   AGE
node-wrk-2-ubuntu24-85748464f7-mwmrt   1/1     Running   0          11m
root@node-0:~# kubectl -n wrk-2 exec -it node-wrk-2-ubuntu24-85748464f7-mwmrt -- /bin/bash
root@node-wrk-2-ubuntu24-85748464f7-mwmrt:/workspace#
```

As you can see below, run the server using our precious nc command on node2. Then connect to it from the node1 by the address supplied. That domain name is structured as {pod-service-name}.{namespace-name}, and made possible because of the process we’re going to explore.

```c
root@node-wrk-2-ubuntu24-85748464f7-mwmrt:/workspace# nc -l 0.0.0.0 9999
asdfasdfasdfasd
```
```c
root@node-wrk-1-ubuntu24-684f7d8fd6-2zncq:/workspace# nc node-wrk-2-ubuntu24.wrk-2 9999
asdfasdfasdfasd
```

As we’re going to see using tshark, what happens when you make a request inside a certain pod is that it generates a DNS query, as usual for any normal process on a Linux host, if IP address is unknown. The only difference in this case, however, is that the primary DNS resolver is Kubernetes’ service called CoreDNS. It gives out IP address (not a real one though, you’re going to see what it means to be “not real” IP) of the service being called.

To check out the exact traffic, we need to know what interface the packet is being bound to when it goes out of the pod. And to do so, we need a little more understanding of what exactly a pod is.

What is exactly a pod?

The short answer goes:

It’s just a Linux namespace.

Well, there are obviously way more than just namespace, such as cgroup, overlayfs, and etc. But at this time we only have to understand that the most basic logical border that defines the territory of a pod is Linux namespace.

If multiple containers reside in the same pod (namespace), they can talk to each other using the local interface. If not (meaning pod-to-pod networking), they need the journey we’re witnessing.

To actually see how this Linux namespace is at work in Kubernetes, run the below command in the pod on node1. We’re going to see that the pod we’ve entered using the kubectl command is also accessible using purely Linux core commands.

In a pod on node1, let a simple command run for a long time as seen below.

```c
root@node-wrk-1-ubuntu24-684f7d8fd6-2zncq:/workspace# sleep 3000
```

Outside the pod on node1 (on the host), check out what Linux namespaces are in use. As you can see from the below commands, you can actually see the interface with the address 10.0.1.15 inside the namespace. Using the ps command and grep, you can see the sleep command in the namespace is running.

```c
root@node-1:~# ip netns list
36322294-9a3a-47fd-8be4-6530f0123581 (id: 2)
5b58d4f1-eb3e-4cb7-b823-bbb08ee37b18 (id: 1)
02aa7ed5-2d8b-44ff-9865-d1b2ef17665c
dbe865d4-e332-40cc-8d95-459445ff6574
a300e0fa-b79e-48b5-aabf-bd8bbcebc428
```
```c
root@node-1:~# ip netns exec 5b58d4f1-eb3e-4cb7-b823-bbb08ee37b18 ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1460 qdisc noqueue state UP group default qlen 1000
    link/ether 4e:e0:85:d5:68:f9 brd ff:ff:ff:ff:ff:ff link-netns 02aa7ed5-2d8b-44ff-9865-d1b2ef17665c
    inet 10.0.1.15/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::4ce0:85ff:fed5:68f9/64 scope link 
       valid_lft forever preferred_lft forever
```
```c
root@node-1:~# ip netns exec 5b58d4f1-eb3e-4cb7-b823-bbb08ee37b18 ps aux | grep sleep
root       85586  0.0  0.0   2696  1380 pts/1    S+   00:41   0:00 sleep 3000
```

In that namespace, you can also check the routing rules.

```c
root@node-1:~# ip netns exec 5b58d4f1-eb3e-4cb7-b823-bbb08ee37b18 ip route
default via 10.0.1.49 dev eth0 mtu 1410 
10.0.1.49 dev eth0 scope link
```

So, where exactly is our default gateway, 10.0.1.49, of the pod on node1?

You can find that out using the ip command on node1 host.

I mistakenly failed to record the part where I captured the output of the command, but you will be sure to find out that the default gateway address seen in the namespace is assigned to the cilium\_host of cilium\_net interface on the host side.

Now is the time to decide which interface on the host we’re going to monitor using tshark based on what we’ve learned.

In order for us to capture packets that are generated inside the pod on node1, we will have to capture the interface that is connected to the namespace 5b58d4f1-eb3e-4cb7-b823-bbb08ee37b18 because that is where we’ve seen the sleep command is running.

Again, parsing ip command output can let us know the information.

```c
root@node-1:~# ip -d link show 
...
9: lxc7dc050ebabd6@if8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1460 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether a6:8a:15:36:dc:cb brd ff:ff:ff:ff:ff:ff link-netns 5b58d4f1-eb3e-4cb7-b823-bbb08ee37b18 promiscuity 0  allmulti 0 minmtu 68 maxmtu 65535 
    veth addrgenmode eui64 numtxqueues 2 numrxqueues 2 gso_max_size 65536 gso_max_segs 65535 tso_max_size 524280 tso_max_segs 65535 gro_max_size 65536 
11: lxc1e0b7c2c5527@if10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1460 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 0e:9c:2c:8c:64:77 brd ff:ff:ff:ff:ff:ff link-netns 36322294-9a3a-47fd-8be4-6530f0123581 promiscuity 0  allmulti 0 minmtu 68 maxmtu 65535 
    veth addrgenmode eui64 numtxqueues 2 numrxqueues 2 gso_max_size 65536 gso_max_segs 65535 tso_max_size 524280 tso_max_segs 65535 gro_max_size 65536

root@node-1:~# ip netns list
36322294-9a3a-47fd-8be4-6530f0123581 (id: 2)
5b58d4f1-eb3e-4cb7-b823-bbb08ee37b18 (id: 1)
....
```

In the above output, we can see the interface whose link-netns field in the interface information has 5b58d4f1… is interface lxc7dc050ebabd6.

So, we put our tshark at work on the interface lxc7dc050ebabd6, and run the nc command (don’t forget to check the nc server in the other pod is still running).

```c
root@node-1:~# tshark -i lxc7dc050ebabd6
Running as user "root" and group "root". This could be dangerous.
Capturing on 'lxc7dc050ebabd6'
    1 0.000000000    10.0.1.15 → 10.96.0.10   DNS 109 Standard query 0x262f A node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local
    2 0.000122975    10.0.1.15 → 10.96.0.10   DNS 109 Standard query 0xf132 AAAA node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local
    3 0.001248872   10.96.0.10 → 10.0.1.15    DNS 202 Standard query response 0xf132 No such name AAAA node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local SOA ns.dns.cluster.local
    4 0.001283013   10.96.0.10 → 10.0.1.15    DNS 202 Standard query response 0x262f No such name A node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local SOA ns.dns.cluster.local
    5 0.001410506    10.0.1.15 → 10.96.0.10   DNS 103 Standard query 0x76e7 A node-wrk-2-ubuntu24.wrk-2.svc.cluster.local
    6 0.001456907    10.0.1.15 → 10.96.0.10   DNS 103 Standard query 0x67e4 AAAA node-wrk-2-ubuntu24.wrk-2.svc.cluster.local
    7 0.001863086   10.96.0.10 → 10.0.1.15    DNS 196 Standard query response 0x67e4 AAAA node-wrk-2-ubuntu24.wrk-2.svc.cluster.local SOA ns.dns.cluster.local
    8 0.001984626   10.96.0.10 → 10.0.1.15    DNS 162 Standard query response 0x76e7 A node-wrk-2-ubuntu24.wrk-2.svc.cluster.local A 10.105.134.33
    9 0.091833823    10.0.1.15 → 10.105.134.33 TCP 74 38430 → 9999 [SYN] Seq=0 Win=64390 Len=0 MSS=1370 SACK_PERM TSval=167971729 TSecr=0 WS=128
   10 0.092468056 10.105.134.33 → 10.0.1.15    TCP 74 9999 → 38430 [SYN, ACK] Seq=0 Ack=1 Win=65184 Len=0 MSS=1370 SACK_PERM TSval=2085648661 TSecr=167971729 WS=128
   11 0.092505544    10.0.1.15 → 10.105.134.33 TCP 66 38430 → 9999 [ACK] Seq=1 Ack=1 Win=64512 Len=0 TSval=167971730 TSecr=2085648661
```

As you can see from the above, the DNS query is at work at first between CoreDNS (10.96.0.10) and our nc client (10.0.1.15).

From packet number 8, we are able to determine that the domain name node-wrk-2-ubuntu24.wrk-2.wrk-1 is resolved to 10.105.134.33.

Right after the address resolution, the typical TCP handshake is done as you can see using the given IP.

But let’s pause for a moment. I said earlier that the IP returned by the CoreDNS is not the real IP of the process we’re trying to reach. In this stage where we try to reach the process by the IP given by CoreDNS, is where kube-proxy comes in, and massive iptable rules are involved.

Let’s find out which part of the iptable rules our destination IP appears.

```c
root@node-1:~# iptables -t nat -L -v | grep "10.105.134.33"
    0     0 KUBE-SVC-IWPXKGE4TAJJE4GD  tcp  --  any    any     anywhere             10.105.134.33        /* wrk-2/node-wrk-2-ubuntu24:tcp-9999 cluster IP */ tcp dpt:9999
    0     0 KUBE-SVC-HX23KANCFUYJINGR  udp  --  any    any     anywhere             10.105.134.33        /* wrk-2/node-wrk-2-ubuntu24:udp-9999 cluster IP */ udp dpt:9999
    0     0 KUBE-MARK-MASQ  udp  --  any    any    !10.10.0.0/16         10.105.134.33        /* wrk-2/node-wrk-2-ubuntu24:udp-9999 cluster IP */ udp dpt:9999
    0     0 KUBE-MARK-MASQ  tcp  --  any    any    !10.10.0.0/16         10.105.134.33        /* wrk-2/node-wrk-2-ubuntu24:tcp-9999 cluster IP */ tcp dpt:9999
```
```c
Chain KUBE-SVC-IWPXKGE4TAJJE4GD (1 references)
 pkts bytes target     prot opt in     out     source               destination         
    0     0 KUBE-MARK-MASQ  tcp  --  any    any    !10.10.0.0/16         10.105.134.33        /* wrk-2/node-wrk-2-ubuntu24:tcp-9999 cluster IP */ tcp dpt:9999
    0     0 KUBE-SEP-FXHI2MOU7V5XIHJD  all  --  any    any     anywhere             anywhere             /* wrk-2/node-wrk-2-ubuntu24:tcp-9999 -> 10.0.2.215:9999 */
```

As you can see, our server app node-wrk-2-ubuntu24:tcp-9999 is being referred to in the iptables as ip 10.105.134.33, and “originally” the iptable rule should be hit and the packet has to be modified.

Not so with Cilium networking!

It involves eBPF and VxLAN so it works differently than the pure kube-proxy-based networking in the past Kubernetes way.

As proof, you can see in the above rules that none of it has been hit (on the leftmost two numbers being 0 for both) where it should have been.

To check if eBPF is truly at work, we can use a tool called “bpftool”. But it’s not available from the APT as a standard package so to use it, you need extra installation and compilation.

[**Bpftool**](https://github.com/libbpf/bpftool)

Anyway, this is the output of the tool that tells you which eBPF program is loaded on which interface.

You can check out the source code for those eBPF programs in the below link.

```c
root@node-1:~/bpftool/src# bpftool link
2: tcx  prog 572  
        ifindex cilium_vxlan(5)  attach_type tcx_ingress  
3: tcx  prog 571  
        ifindex cilium_vxlan(5)  attach_type tcx_egress  
4: tcx  prog 657  
        ifindex cilium_host(4)  attach_type tcx_ingress  
5: tcx  prog 652  
        ifindex cilium_host(4)  attach_type tcx_egress  
6: tcx  prog 664  
        ifindex cilium_net(3)  attach_type tcx_ingress  
7: tcx  prog 674  
        ifindex ens4(2)  attach_type tcx_ingress  
8: tcx  prog 600  
        ifindex lxc_health(7)  attach_type tcx_ingress  
9: tcx  prog 681  
        ifindex lxc7dc050ebabd6(9)  attach_type tcx_ingress  
10: tcx  prog 694  
        ifindex lxc1e0b7c2c5527(11)  attach_type tcx_ingress
```
```c
# https://github.com/cilium/cilium/blob/main/bpf/bpf_lxc.c
```

All interfaces have their own programs!

It also explains why the VxLAN interfaces set up by Cilium are somewhat different than the typical VxLAN environment where it usually involves a bridge to attach one end of the virtual ethernet interface from a namespace.

Because, using eBPF, you can actually redirect traffic between interfaces without consulting Linux kernel. If it was not for eBPF, cilium\_host which holds the default gateway address should have been set up as a bridge.

It’s very clear that VxLAN will be used for node-to-node communication and what we’re doing is node-to-node communication, we can safely put tshark on cilium\_vxlan interface. Connect the client again.

```c
root@node-1:~# tshark -i cilium_vxlan 
Running as user "root" and group "root". This could be dangerous.
Capturing on 'cilium_vxlan'
...
    3 0.153379717    10.0.1.15 → 10.0.2.17    DNS 109 Standard query 0x69a9 A node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local
    4 0.153453149    10.0.1.15 → 10.0.2.17    DNS 109 Standard query 0x71b4 AAAA node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local
    5 0.154519494    10.0.2.17 → 10.0.1.15    DNS 202 Standard query response 0x69a9 No such name A node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local SOA ns.dns.cluster.local
    6 0.156446844    10.0.2.17 → 10.0.1.15    DNS 202 Standard query response 0x71b4 No such name AAAA node-wrk-2-ubuntu24.wrk-2.wrk-1.svc.cluster.local SOA ns.dns.cluster.local
    7 0.156651889    10.0.1.15 → 10.0.2.17    DNS 103 Standard query 0x0fd2 A node-wrk-2-ubuntu24.wrk-2.svc.cluster.local
    8 0.156713018    10.0.1.15 → 10.0.2.17    DNS 103 Standard query 0xf8cf AAAA node-wrk-2-ubuntu24.wrk-2.svc.cluster.local
    9 0.157366940    10.0.2.17 → 10.0.1.15    DNS 196 Standard query response 0xf8cf AAAA node-wrk-2-ubuntu24.wrk-2.svc.cluster.local SOA ns.dns.cluster.local
   10 0.157367119    10.0.2.17 → 10.0.1.15    DNS 162 Standard query response 0x0fd2 A node-wrk-2-ubuntu24.wrk-2.svc.cluster.local A 10.105.134.33
   11 0.247844051    10.0.1.15 → 10.0.2.215   TCP 74 41208 → 9999 [SYN] Seq=0 Win=64390 Len=0 MSS=1370 SACK_PERM TSval=168433304 TSecr=0 WS=128
   12 0.248302570   10.0.2.215 → 10.0.1.15    TCP 74 9999 → 41208 [SYN, ACK] Seq=0 Ack=1 Win=65184 Len=0 MSS=1370 SACK_PERM TSval=2086110236 TSecr=168433304 WS=128
   13 0.248397099    10.0.1.15 → 10.0.2.215   TCP 66 41208 → 9999 [ACK] Seq=1 Ack=1 Win=64512 Len=0 TSval=168433305 TSecr=2086110236
...
```

It’s very clear eBPF program changed the destination address to communicate properly within VxLAN network. The IP is also, as we’ll see soon, the real process IP (our nc server).

You can find this also in the iptables rules again. And again, you will see the eBPF is at work since no rule has been hit where it should have.

```c
root@node-1:~# iptables -t nat -L -v | grep 10.0.2.215
    0     0 KUBE-MARK-MASQ  all  --  any    any     10.0.2.215           anywhere             /* wrk-2/node-wrk-2-ubuntu24:tcp-9999 */
    0     0 DNAT       tcp  --  any    any     anywhere             anywhere             /* wrk-2/node-wrk-2-ubuntu24:tcp-9999 */ tcp to:10.0.2.215:9999
    0     0 KUBE-MARK-MASQ  all  --  any    any     10.0.2.215           anywhere             /* wrk-2/node-wrk-2-ubuntu24:udp-9999 */
    0     0 DNAT       udp  --  any    any     anywhere             anywhere             /* wrk-2/node-wrk-2-ubuntu24:udp-9999 */ udp to:10.0.2.215:9999
    0     0 KUBE-SEP-VWQM2HSDJBARAX5I  all  --  any    any     anywhere             anywhere             /* wrk-2/node-wrk-2-ubuntu24:udp-9999 -> 10.0.2.215:9999 */
    0     0 KUBE-SEP-FXHI2MOU7V5XIHJD  all  --  any    any     anywhere             anywhere             /* wrk-2/node-wrk-2-ubuntu24:tcp-9999 -> 10.0.2.215:9999 */
```

Finally, if a packet is using VxLAN, it will be encapped. So we put tshark on the only real (though it’s still virtual from Google Cloud’s point of view) interface, ens4.

```c
root@node-1:~# tshark -i ens4 -f udp
Running as user "root" and group "root". This could be dangerous.
Capturing on 'ens4'
    1 0.000000000   10.168.0.4 → 10.168.0.5   UDP 159 45304 → 8472 Len=117
    2 0.000026094   10.168.0.4 → 10.168.0.5   UDP 159 45304 → 8472 Len=117
    3 0.000787520   10.168.0.5 → 10.168.0.4   UDP 252 45292 → 8472 Len=210
    4 0.000879542   10.168.0.5 → 10.168.0.4   UDP 252 45292 → 8472 Len=210
    5 0.001084107   10.168.0.4 → 10.168.0.5   UDP 153 59946 → 8472 Len=111
    6 0.001121632   10.168.0.4 → 10.168.0.5   UDP 153 59946 → 8472 Len=111
    7 0.001991176   10.168.0.5 → 10.168.0.4   UDP 246 56913 → 8472 Len=204
    8 0.003240963   10.168.0.5 → 10.168.0.4   UDP 212 56913 → 8472 Len=170
    9 0.091070101   10.168.0.4 → 10.168.0.5   UDP 124 32918 → 8472 Len=82
   10 0.091373667   10.168.0.5 → 10.168.0.4   UDP 124 43769 → 8472 Len=82
   11 0.091482484   10.168.0.4 → 10.168.0.5   UDP 116 32918 → 8472 Len=74
```

As we can see, the traffic is encapsulated and moves between node1 and node2.

You can see this behavior documented in Cilium documentation also.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*QAD-uOQamS1Q28s4PyPM1Q.png)

Now, we’re going to move on to the next node, node2.

Here, we’re going to first put tshark on the underlying interface.

```c
root@node-2:~# tshark -i ens4 -f udp
Running as user "root" and group "root". This could be dangerous.
Capturing on 'ens4'
    1 0.000000000   10.168.0.4 → 10.168.0.5   UDP 159 54392 → 8472 Len=117
    2 0.000000394   10.168.0.4 → 10.168.0.5   UDP 159 54392 → 8472 Len=117
    3 0.000924839   10.168.0.5 → 10.168.0.4   UDP 252 33949 → 8472 Len=210
    4 0.001091915   10.168.0.5 → 10.168.0.4   UDP 252 33949 → 8472 Len=210
    5 0.090827819   10.168.0.4 → 10.168.0.5   UDP 124 46625 → 8472 Len=82
    6 0.091005902   10.168.0.5 → 10.168.0.4   UDP 124 39053 → 8472 Len=82
    7 0.091299352   10.168.0.4 → 10.168.0.5   UDP 116 46625 → 8472 Len=74
```

Same as the node1, put it on the cilium\_vxlan interface. You can see the packet is decapped.

```c
root@node-2:~# tshark -i cilium_vxlan -f "tcp port 9999"
Running as user "root" and group "root". This could be dangerous.
Capturing on 'cilium_vxlan'
    1 0.000000000    10.0.1.15 → 10.0.2.215   TCP 74 40686 → 9999 [SYN] Seq=0 Win=64390 Len=0 MSS=1370 SACK_PERM TSval=166156308 TSecr=0 WS=128
    2 0.000242183   10.0.2.215 → 10.0.1.15    TCP 74 9999 → 40686 [SYN, ACK] Seq=0 Ack=1 Win=65184 Len=0 MSS=1370 SACK_PERM TSval=2083833240 TSecr=166156308 WS=128
    3 0.000623879    10.0.1.15 → 10.0.2.215   TCP 66 40686 → 9999 [ACK] Seq=1 Ack=1 Win=64512 Len=0 TSval=166156309 TSecr=2083833240
```

Let’s pull off the namespace parsing technique we did previously again to find out which interface exactly is connected to the namespace where our nc server is residing.

```c
root@node-2:~# ip route
...
10.0.2.0/24 via 10.0.2.244 dev cilium_host proto kernel src 10.0.2.244 
...
```
```c
root@node-2:~# ip netns list
47f92595-eb21-46c7-b0ac-5efbf1cd4d59 (id: 2)
ceb7eaea-1923-4233-9253-9b7d25a9fb93 (id: 1)
fe1dc96d-ef17-4afd-a1f7-4b65bdd64bd0
c686294b-4802-4767-9057-69c83626a5ee
477ebbff-90d2-43f3-9e8f-15dbac6501f2
```
```c
root@node-2:~# ip netns exec ceb7eaea-1923-4233-9253-9b7d25a9fb93 ip a
...
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1460 qdisc noqueue state UP group default qlen 1000
    link/ether 92:42:dd:7b:6f:be brd ff:ff:ff:ff:ff:ff link-netns fe1dc96d-ef17-4afd-a1f7-4b65bdd64bd0
    inet 10.0.2.215/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::9042:ddff:fe7b:6fbe/64 scope link 
       valid_lft forever preferred_lft forever
```
```c
root@node-2:~# ip netns exec ceb7eaea-1923-4233-9253-9b7d25a9fb93 ps aux | grep nc
...
root       39372  0.0  0.1  14912  5548 pts/0    S+   May21   0:00 nc -l 0.0.0.0 9999
```
```c
root@node-2:~# ip -d link show
...
9: lxc3afb1f126f2c@if8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1460 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 52:17:b0:95:31:94 brd ff:ff:ff:ff:ff:ff link-netns ceb7eaea-1923-4233-9253-9b7d25a9fb93 promiscuity 0  allmulti 0 minmtu 68 maxmtu 65535 
    veth addrgenmode eui64 numtxqueues 2 numrxqueues 2 gso_max_size 65536 gso_max_segs 65535 tso_max_size 524280 tso_max_segs 65535 gro_max_size 65536 
11: lxc3fe8b5095c99@if10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1460 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 72:15:1d:3a:ad:d0 brd ff:ff:ff:ff:ff:ff link-netns 47f92595-eb21-46c7-b0ac-5efbf1cd4d59 promiscuity 0  allmulti 0 minmtu 68 maxmtu 65535 
    veth addrgenmode eui64 numtxqueues 2 numrxqueues 2 gso_max_size 65536 gso_max_segs 65535 tso_max_size 524280 tso_max_segs 65535 gro_max_size 65536 
...
```

Finally!

```c
root@node-2:~# tshark -i lxc3afb1f126f2c
Running as user "root" and group "root". This could be dangerous.
Capturing on 'lxc3afb1f126f2c'
    1 0.000000000    10.0.1.15 → 10.0.2.215   TCP 74 50210 → 9999 [SYN] Seq=0 Win=64390 Len=0 MSS=1370 SACK_PERM TSval=173851431 TSecr=0 WS=128
    2 0.000035143   10.0.2.215 → 10.0.1.15    TCP 74 9999 → 50210 [SYN, ACK] Seq=0 Ack=1 Win=65184 Len=0 MSS=1370 SACK_PERM TSval=2091528363 TSecr=173851431 WS=128
    3 0.000359301    10.0.1.15 → 10.0.2.215   TCP 66 50210 → 9999 [ACK] Seq=1 Ack=1 Win=64512 Len=0 TSval=173851431 TSecr=2091528363
```

Thanks!

## More from Taehoon Yoon

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--485eb2876a84---------------------------------------)