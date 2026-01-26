---
title: "Play with Cilium native routing in Kind cluster"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@nahelou.j/play-with-cilium-native-routing-in-kind-cluster-5a9e586a81ca"
author:
  - "[[Jérôme NAHELOU]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*MkUQnUC3JRWvx6lZSyOLHA.jpeg)

The KubeCon conference is approaching, offering an exciting opportunity to enhance our networking skills for Kubernetes clusters!

It’s highly likely that you’ve encountered many Kubernetes clusters deployed on virtual machines, created using Ansible playbooks and Kubeadm. Here, we won’t be discussing clusters managed by your favorite cloud providers, but rather those opting for self-managed infrastructure.

In this article, we’ll focus on network management through CNI management tools. This discussion stems from an article published on the Cilium blog aimed at improving the networking performance of our Kubernetes cluster:## [Cilium Standalone Layer 4 Load Balancer XDP](https://cilium.io/blog/2022/04/12/cilium-standalone-L4LB-XDP/?source=post_page-----5a9e586a81ca---------------------------------------)

See the performance increase Seznam.cz saw using Cilium for load balancing...

cilium.io

[View original](https://cilium.io/blog/2022/04/12/cilium-standalone-L4LB-XDP/?source=post_page-----5a9e586a81ca---------------------------------------)

The idea is not to just check the exposed metrics, but to assess the complexity and software prerequisites required to achieve this level of performance.

Before diving headfirst into a production implementation, it’s wise to deploy your own cluster on your workstation or homelab. Kind needs no introduction; it’s ideal for deploying a Kubernetes cluster, allowing us to test and modify configurations quickly and independently.

## Kind the kickstarter

Let’s start by creating a kubernetes cluster locally, ensuring to:

- Set up multiple nodes: 1 used as the control plane and 2 nodes for the data plane
- Disable the deployment of a CNI plugin (Cilium will be installed later)
- Avoid using kube-proxy for network management (aiming to transition everything to eBPF)
```c
# kind-config.yaml 
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
networking:
  disableDefaultCNI: true
  kubeProxyMode: none

# Use \`kind create cluster --config=kind-config.yaml\` command to create the cluster
```

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Qn-rnRfLomSr2er7Ee1Uog.png)

Once the ‘kind’ command is launched to create the cluster (on the left), we notice that some pods remain in the “pending” state. This phenomenon is caused by the absence of a CNI plugin in the cluster to manage internal cluster IP addresses (pods and services). Let’s proceed with deploying Cilium in our ‘kind’ cluster to address this.

## Cilium for network management

Installing Cilium is straightforward, whether via a Helm chart or by using a command-line interface (CLI) that also utilizes the Helm chart.

However, before proceeding, let’s revisit the focus of our article: optimizing network performance in our cluster.

Unfortunately, simply deploying Cilium is not enough; it’s crucial to understand how it works.

Cilium offers two types of network configurations: encapsulation and direct routing (native).## [Routing - Cilium 1.15.1 documentation](https://docs.cilium.io/en/stable/network/concepts/routing/?source=post_page-----5a9e586a81ca---------------------------------------)

In native routing mode, Cilium will delegate all packets which are not addressed to another local endpoint to the…

docs.cilium.io

[View original](https://docs.cilium.io/en/stable/network/concepts/routing/?source=post_page-----5a9e586a81ca---------------------------------------)

Native routing will be preferred to maximize performance. Although it requires more advanced configuration, it will allow administrators to fully leverage the network capabilities offered by eBPF and completely eliminate the need for iptables/ipvs.

If you want to read more into the topic, don’t hesitate to read [@\_asayah](https://twitter.com/_asayah) ’s article:## [Choosing the Right Routing in Cilium](https://www.solo.io/blog/choosing-right-routing-cilium/?source=post_page-----5a9e586a81ca---------------------------------------)

Cilium provides two primary methods of routing traffic between nodes -- learn about the advantages and disadvantages of…

www.solo.io

[View original](https://www.solo.io/blog/choosing-right-routing-cilium/?source=post_page-----5a9e586a81ca---------------------------------------)

Let’s proceed with installing Cilium in our cluster using the following configuration:

```c
# cilium-medium.yaml
cluster:
  name: kind-kind

k8sServiceHost: kind-control-plane
k8sServicePort: 6443
kubeProxyReplacement: strict

ipv4:
  enabled: true
ipv6:
  enabled: false

hubble:
  relay:
    enabled: true
  ui:
    enabled: true
ipam:
  mode: kubernetes

# Cilium Routing
routingMode: native
ipv4NativeRoutingCIDR: 10.244.0.0/16
enableIPv4Masquerade: true
autoDirectNodeRoutes: true
```

And using the Helm command:

```c
$ helm install -n kube-system cilium cilium/cilium -f cilium-medium.yaml
```

After a few minutes, all pods will be deployed as expected.

Note: It’s important to specify the attributes *k8sServiceHost* and *k8sServicePort* so that the Cilium operator knows how to address the control plane. In the absence of these two attributes, the Cilium operator will remain in a status of crashloopbackoff because it will not be able to perform DNS resolution (via the service created by CoreDNS but which does not yet have an IP).

## Deep into Cilium configuration

Adopting native networking is not without implications. In Kubernetes, each node inherits a unique addressing plan that it uses to identify the pods it runs.

```c
$ kubectl get configmaps -n kube-system kubeadm-config -o yaml | grep podSubnet
      podSubnet: 10.244.0.0/16
$ # Or using kubectl cluster-info dump | grep -m 1 cluster-cidr

$ kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.podCIDR}{"\n"}'
kind-control-plane      10.244.0.0/24
kind-worker     10.244.2.0/24
kind-worker2    10.244.1.0/24
```

For each node in the cluster to access pods running on other nodes, it’s imperative that these subnets be correctly routed.

The documentation is explicit on this point: by default, this configuration is not in place:

> Each individual node is made aware of all pod IPs of all other nodes and routes are inserted into the Linux kernel routing table to represent this.  
> [https://docs.cilium.io/en/stable/network/concepts/routing/#id4](https://docs.cilium.io/en/stable/network/concepts/routing/#id4)

This situation can be easily observed on a node of the cluster:

```c
root@kind-worker:/# ip route   
default via 172.18.0.1 dev eth0 
10.244.2.0/24 via 10.244.2.224 dev cilium_host proto kernel src 10.244.2.224 
10.244.2.224 dev cilium_host proto kernel scope link 
172.18.0.0/16 dev eth0 proto kernel scope link src 172.18.0.3
```

However, when all nodes are in the same network (L2), it’s possible to enable the attribute **autoDirectNodeRoutes: true**. This allows the Cilium agent to automatically add all routes for each node in the cluster, thus avoiding the need to do so manually.

```c
root@kind-worker:/# ip route   
default via 172.18.0.1 dev eth0 
10.244.0.0/24 via 172.18.0.2 dev eth0 proto kernel 
10.244.1.0/24 via 172.18.0.4 dev eth0 proto kernel 
10.244.2.0/24 via 10.244.2.224 dev cilium_host proto kernel src 10.244.2.224 
10.244.2.224 dev cilium_host proto kernel scope link 
172.18.0.0/16 dev eth0 proto kernel scope link src 172.18.0.3
```

## Deployment of an application in the cluster

To confirm the validity of the configurations and ensure the continuity of communications between pods, I opted to use the chart provided by Cilium:

[https://raw.githubusercontent.com/cilium/cilium/HEAD/examples/minikube/http-sw-app.yaml](https://raw.githubusercontent.com/cilium/cilium/HEAD/examples/minikube/http-sw-app.yaml)

```c
$ kubectl exec tiefighter -- curl --connect-timeout 10 -s https://swapi.dev/api/starships
{"count":36,"next":"https://swapi.dev/api/starships/?page=2","previous":null,"results":[...]}

$ kubectl exec tiefighter -- curl --connect-timeout 10 -s -XPOST deathstar.default.svc.cluster.local/v1/request-landing
Ship landed
```

It allows me to validate:

- DNS resolution within my cluster
- Private and public communications

## More eBpf features

By default, Cilium uses iptables to configure masquerade rules.

Masquerade is a networking technique that hides the IP addresses of an internal network (such as the pods’ network) when they communicate with external networks (outside the cluster). Whenever a packet leaves the cluster’s network to reach an external network, the packet’s source address is modified to be that of the node running the container.

Example:

```c
root@kind-worker:/# iptables -t nat -S  CILIUM_POST_nat
-N CILIUM_POST_nat
-A CILIUM_POST_nat -s 10.244.2.0/24 -m set --match-set cilium_node_set_v4 dst -m comment --comment "exclude traffic to cluster nodes from masquerade" -j ACCEPT
-A CILIUM_POST_nat -s 10.244.2.0/24 ! -d 10.244.0.0/16 ! -o cilium_+ -m comment --comment "cilium masquerade non-cluster" -j MASQUERADE
-A CILIUM_POST_nat -m mark --mark 0xa00/0xe00 -m comment --comment "exclude proxy return traffic from masquerade" -j ACCEPT
-A CILIUM_POST_nat -s 127.0.0.1/32 -o cilium_host -m comment --comment "cilium host->cluster from 127.0.0.1 masquerade" -j SNAT --to-source 10.244.2.224
-A CILIUM_POST_nat -o cilium_host -m mark --mark 0xf00/0xf00 -m conntrack --ctstate DNAT -m comment --comment "hairpin traffic that originated from a local pod" -j SNAT --to-source 10.244.2.224
```

It is possible to modify this behavior to fully leverage the capabilities offered by the Linux kernel. You simply need to customize the Helm deployment by adding masquerade capabilities via eBPF:

```c
# cilium-medium.yaml
...

bpf:
  masquerade: true
ipMasqAgent:
  enabled: true
  config:
    nonMasqueradeCIDRs:
      - 10.244.0.0/8
```

Next, proceed with updating the deployment and verify the configuration:

```c
$ helm upgrade -n kube-system cilium cilium/cilium -f cilium-medium.yaml
...

$ kubectl -n kube-system exec ds/cilium -- cilium-dbg status | grep Masquerading
Masquerading:            BPF (ip-masq-agent)   [eth0]   10.244.0.0/16 [IPv4: Enabled, IPv6: Disabled]

$ kubectl -n kube-system exec ds/cilium -- cilium-dbg bpf ipmasq list
IP PREFIX/ADDRESS
10.244.0.0/16
169.254.0.0/16
```

At this stage, you may encounter issues with external DNS resolution. Indeed, Docker also uses iptables rules to redirect external requests to the machine where the ‘kind’ cluster is deployed:

```c
docker exec -ti kind-worker bash
root@kind-worker:/# iptables -t nat -S DOCKER_OUTPUT
-N DOCKER_OUTPUT
-A DOCKER_OUTPUT -d 172.18.0.1/32 -p tcp -m tcp --dport 53 -j DNAT --to-destination 127.0.0.11:44581
-A DOCKER_OUTPUT -d 172.18.0.1/32 -p udp -m udp --dport 53 -j DNAT --to-destination 127.0.0.11:33181
```

An alternative is to modify the CoreDNS configuration to directly specify the DNS server address to use, thus providing a workaround solution for our environment:

```c
$ nmcli dev show | grep 'IP4.DNS'
IP4.DNS[1]:                             192.168.1.1

$ kubectl edit configmaps -n kube-system coredns
# Replace "forward . /etc/resolv.conf" with "forward . 192.168.1.1"

$ kubectl -n kube-system rollout restart deployment coredns
```

## It’s time to address north/south load balancing

We’re finally at the last configuration recommended by the original article, which involves activating XDP technology.

But before that, it’s necessary to create a service for our application.

```c
# cat deathstar-svc.yaml 
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/name: deathstar
  name: deathstar-lb
  namespace: default
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    class: deathstar
    org: empire
  sessionAffinity: None
  type: LoadBalancer
```

At this stage, the service does not retrieve an external IP address.

Managing external service IP addresses, known as “LoadBalancer IP Address Management (LB IPAM),” is a feature of Cilium. To accomplish this task, it’s necessary to specify the subnet in which Cilium will reserve IP addresses.

To facilitate routing between the Docker layer (kind backend) and our laptop, it’s recommended to use a subnet from the CIDR used and routed by Docker (default is “172.18.0.0/16”).## [LoadBalancer](https://kind.sigs.k8s.io/docs/user/loadbalancer/?source=post_page-----5a9e586a81ca---------------------------------------)

This guide covers how to get service of type LoadBalancer working in a kind cluster using Metallb. This guide…

kind.sigs.k8s.io

[View original](https://kind.sigs.k8s.io/docs/user/loadbalancer/?source=post_page-----5a9e586a81ca---------------------------------------)

We can verify that routing is already in place for this destination:

```c
$ ip route
default via 192.168.1.1 dev wlp2s0 proto dhcp src 192.168.1.63 metric 600 
169.254.0.0/16 dev wlp2s0 scope link metric 1000 
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 
172.18.0.0/16 dev br-53ce6d3e9cb9 proto kernel scope link src 172.18.0.1 
192.168.1.0/24 dev wlp2s0 proto kernel scope link src 192.168.1.63 metric 600
```

In my example, I’m using the subnet “172.18.250.0/24” to define the IPs for my services.

```c
# cilium-lbsvc-pool.yaml
apiVersion: "cilium.io/v2alpha1"
kind: CiliumLoadBalancerIPPool
metadata:
  name: "default"
spec:
  blocks:
  - cidr: "172.18.250.0/24"
```

To check the detailed status of the service, we can directly consult the configuration on the agents

```c
$ kubectl get service deathstar-lb
NAME           TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
deathstar-lb   LoadBalancer   10.96.208.17   172.18.250.1   80:32367/TCP   16h

$ kubectl -n kube-system exec pods/cilium-9vc2l - cilium-dbg service list
ID   Frontend            Service Type   Backend                           
....
16   172.18.250.1:80     LoadBalancer   1 => 10.244.2.117:80 (active)     
                                        2 => 10.244.1.108:80 (active)
```

When using a different addressing plan than Docker’s default (for example, 192.168.250.0/24), to access the service from your machine, you will need to additionally:

- Setup ARP announcements using the l2announcement feature
```c
# cilium-medium.yaml
...

l2announcements:
  enabled: true
```
- Proceed with updating the Cilium agents (the init-containers need to be replayed)
```c
$ helm upgrade -n kube-system cilium cilium/cilium -f cilium-medium.yaml
$ kubectl rollout -n kube-system restart daemonset cilium
```
- Create an announcement policy
```c
apiVersion: "cilium.io/v2alpha1"
kind: CiliumL2AnnouncementPolicy
metadata:
  name: default
spec:
  nodeSelector:
    matchExpressions:
      - key: node-role.kubernetes.io/control-plane
        operator: DoesNotExist
  interfaces:
  - ^eth[0-9]+
  externalIPs: true
  loadBalancerIPs: true
```
- Configure a route (192.168.250.0/24) on our machine to enable routing from our host to the Docker environment
```c
$ sudo ip route add 192.168.250.0/24 dev br-53ce6d3e9cb9 src 172.18.0.1

$ ip route
default via 192.168.1.1 dev wlp2s0 proto dhcp src 192.168.1.63 metric 600 
169.254.0.0/16 dev wlp2s0 scope link metric 1000 
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 
172.18.0.0/16 dev br-53ce6d3e9cb9 proto kernel scope link src 172.18.0.1 
192.168.1.0/24 dev wlp2s0 proto kernel scope link src 192.168.1.63 metric 600 
192.168.250.0/24 dev br-53ce6d3e9cb9 scope link src 172.18.0.1
```
- Verify that the announcement is being successfully received
```c
$ ip neigh | grep 172.18
172.18.0.4 dev br-53ce6d3e9cb9 lladdr 02:42:ac:12:00:04 STALE
172.18.0.2 dev br-53ce6d3e9cb9 lladdr 02:42:ac:12:00:02 STALE
172.18.250.1 dev br-53ce6d3e9cb9 lladdr 02:42:ac:12:00:04 REACHABLE
172.18.0.3 dev br-53ce6d3e9cb9 lladdr 02:42:ac:12:00:03 STALE
```

**If you have opted for Docker’s default addressing plan or have correctly configured L2 announcements, you can proceed here.**

XDP (Express Data Path) technology is a feature of the Linux kernel that enables ultra-fast processing of network packets directly at the network card driver level, before they are even passed to the kernel’s conventional network stack. This approach offers very high performance and minimal latency for packet processing.

Enabling XDP acceleration is simpler to set up (be mindful of prerequisites).

```c
# cilium-medium.yaml
...

loadBalancer:
  acceleration: native
  mode: hybrid
```

Once again, it’s imperative to trigger the update of the Cilium agents.

```c
$ helm upgrade -n kube-system cilium cilium/cilium -f cilium-medium.yaml
$ kubectl rollout -n kube-system restart daemonset cilium
```

This way, we can validate the configuration.

```c
$ kubectl -n kube-system exec ds/cilium -- cilium-dbg status --verbose | grep XDP
  XDP Acceleration:       Native

$ docker exec -ti kind-worker bash
root@kind-worker:/# ip addr  | grep xdp
36: eth0@if37: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 xdp/id:81834 qdisc noqueue state UP group default qlen 1000
```

In conclusion, implementing the configurations described in the preceding steps will optimize performance and network management in your Kubernetes environment by fully leveraging the advanced features offered by tools such as Cilium, eBPF, and XDP.

This approach offers very high performance and minimal latency for packet processing, making it an ideal solution for applications requiring intensive network processing (API management, IDS, and others).

However, administrators will need to acquire new skills, understand new concepts, or simply consider adopting solutions managed by cloud providers.

Cloud rider at SFEIR the day, Akita Inu lover #MyAkitaInuIsNotAWolf