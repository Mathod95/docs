---
title: "Solving Kubernetes DNS Performance Issues with CoreDNS Autopath Plugin"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blogs.learningdevops.com/solving-kubernetes-dns-performance-issues-with-coredns-autopath-plugin-3650eb0c477a"
author:
  - "[[Rajesh Kumar]]"
---
<!-- more -->

[Sitemap](https://blogs.learningdevops.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*_eHbHm2jDN48reeY53tntA.png)

DNS issue

Ever had one of those weeks when your Kubernetes cluster’s DNS resolution feels like it’s running through molasses? Yeah, me too. Last month, I dove deep into a performance issue that had our microservices crawling during external API calls. Turns out, the default CoreDNS configuration was doing something pretty wasteful, and there’s this thing called “autopath” that can cut the DNS resolution time in half.

Let me walk you through exactly what I discovered, with real commands you can run and actual packet captures to see the problem in action.

🎯 Experience this optimization yourself: Try the Interactive [CoreDNS Autopath Demo](https://demos.learningdevops.com/coredns-autopath/) to see the DNS query reduction in real-time before diving into the technical details.

***On a free medium plan?*** [***Read here for free***](https://blogs.learningdevops.com/solving-kubernetes-dns-performance-issues-with-coredns-autopath-plugin-3650eb0c477a?sk=4b63e6d9ebd8ce1f36c5b87bbeb4918f)***.***

## Setting up the test environment

Before we start hunting DNS gremlins, we need some proper tools and test applications. I learned that having a good test setup is crucial for understanding what’s actually happening under the hood.

First, let’s get the packet capture tools installed. We’ll need krew for the kubectl sniff plugin:

```c
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)
```

Add [krew](https://krew.sigs.k8s.io/docs/user-guide/setup/install/) to your PATH and install the packet capture plugin:

```c
# Add this to ~/.zshrc or ~/.bashrc
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
source ~/.zshrc  # or ~/.bashrc

# Install the packet capture plugin
kubectl krew install sniff
```

Now let’s create a test application that will help us see DNS behavior:

```c
# Create our DNS testing pod
kubectl run dnsutils --image=debian:bullseye --restart=Never -- sleep 36000
```

Wait for everything to be running:

```c
kubectl get pods -o wide
```

## Understanding the problem with default CoreDNS

Let’s look at the current CoreDNS configuration to understand what’s happening. This is where I first realized that the default setup might not be optimal for clusters that make a lot of external API calls.

```c
kubectl get configmap coredns -n kube-system -o yaml
```

Here’s what mine looked like before I started investigating:

```c
Corefile: |
    .:53 {
        errors
        health
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
          pods insecure
          fallthrough in-addr.arpa ip6.arpa
        }
        hosts /etc/coredns/NodeHosts {
          ttl 60
          reload 15s
          fallthrough
        }
        prometheus :9153
        forward . /etc/resolv.conf
        cache 30
        loop
        reload
        loadbalance
        import /etc/coredns/custom/*.override
    }
    import /etc/coredns/custom/*.server
```

This looks innocent enough, right? But here’s where it gets interesting. The default search domain behavior in Kubernetes means that when your pod tries to resolve an external domain like `google.com`, it doesn't go straight to the external query. Instead, it tries several internal queries first.

## Capturing the problem in action

Let’s run a packet capture to see exactly what’s happening when we resolve DNS names. This is where the real detective work begins:

```c
# Start capturing DNS traffic from our test pod
kubectl sniff -n default dnsutils -f "port 53" -o /tmp/dns-without-autopath.pcap &
SNIFF_PID=$!
```

Now let’s make a simple DNS query and see what happens:

```c
kubectl exec dnsutils -- nslookup google.com
```

Stop the packet capture and analyze what happened:

```c
kill $SNIFF_PID
tcpdump -r /tmp/dns-without-autopath.pcap -n
```

Here’s what I saw in my cluster:

```c
12:55:47.996624 IP 10.0.0.9.51809 > 10.0.0.28.domain: A? google.com.default.svc.cluster.local.
12:55:47.996913 IP 10.0.0.28.domain > 10.0.0.9.51809: NXDomain
12:55:47.997142 IP 10.0.0.9.46739 > 10.0.0.28.domain: A? google.com.svc.cluster.local.
12:55:47.997327 IP 10.0.0.28.domain > 10.0.0.9.46739: NXDomain
12:55:47.997568 IP 10.0.0.9.51080 > 10.0.0.28.domain: A? google.com.cluster.local.
12:55:47.997739 IP 10.0.0.28.domain > 10.0.0.9.51080: NXDomain
12:55:47.997959 IP 10.0.0.9.50776 > 10.0.0.28.domain: A? google.com.
12:55:48.003769 IP 10.0.0.28.domain > 10.0.0.9.50776: A 142.250.207.174
```

See what’s happening? When your pod tries to resolve `google.com`, the default search domain behavior makes it try several useless queries first:

1. It tries `google.com.default.svc.cluster.local` - gets NXDOMAIN
2. Then `google.com.svc.cluster.local` - gets NXDOMAIN
3. Then `google.com.cluster.local` - gets NXDOMAIN
4. Finally just `google.com` - success!

Each of those failed queries adds latency and load on your CoreDNS servers. For internal services, this search path makes perfect sense. For external APIs? It’s pure waste.

## CoreDNS autopath

Here’s where autopath comes in. It’s a CoreDNS plugin that intelligently decides whether to use the search path based on whether the query is likely to succeed. The plugin analyzes the query pattern and can skip unnecessary search path attempts when it recognizes that a domain clearly doesn’t match any Kubernetes service patterns.

The autopath plugin works by maintaining awareness of your cluster’s service and pod topology. When it receives a DNS query, it can make an educated decision about whether to attempt the full search path or take a shortcut.

## Configuring autopath

Let’s modify the CoreDNS configuration to enable autopath. The key changes we need to make are adding the autopath plugin and changing the pods setting from `insecure` to `verified`:

```c
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        kubernetes cluster.local {
           pods verified  # REQUIRED for autopath to work correctly
        }
        autopath @kubernetes # This is the autopath plugin configuration
        prometheus :9153
        forward . /etc/resolv.conf
        cache 30
        loop
        reload
        loadbalance
    }
```

The two critical changes here are:

1. Added `autopath @kubernetes` - This enables the autopath plugin and tells it to work with the Kubernetes plugin
2. Changed `pods insecure` to `pods verified` - This is required for autopath to function properly, as it needs to verify pod information to make intelligent routing decisions

Now restart CoreDNS to pick up the changes:

```c
kubectl -n kube-system apply -f autopath-enabled-dns-config.yaml

kubectl rollout restart deployment/coredns -n kube-system
kubectl rollout status deployment/coredns -n kube-system
```

## Testing the improvement

Now let’s capture traffic again and run the same test to see what autopath actually does:

```c
# Start capturing with autopath enabled
kubectl sniff dnsutils -f "port 53" -o /tmp/dns-with-autopath.pcap &
SNIFF_PID=$!
# Run the same DNS query
kubectl exec dnsutils -- nslookup google.com
```

Stop the capture and analyze the results:

```c
kill $SNIFF_PID
tcpdump -r /tmp/dns-with-autopath.pcap -n
```

Here’s what I got with autopath enabled:

```c
12:54:19.833244 IP 10.0.0.9.59546 > 10.0.0.28.domain: A? google.com.default.svc.cluster.local.
12:54:19.836437 IP 10.0.0.28.domain > 10.0.0.9.59546: CNAME google.com., A 142.251.220.46
12:54:19.836914 IP 10.0.0.9.46566 > 10.0.0.28.domain: AAAA? google.com.
12:54:19.842809 IP 10.0.0.28.domain > 10.0.0.9.46566: AAAA 2404:6800:4009:807::200e
```

This is beautiful! Look at what happened:

**Without autopath (5 DNS queries total):**

- `google.com.default.svc.cluster.local` → NXDOMAIN (wasted)
- `google.com.svc.cluster.local` → NXDOMAIN (wasted)
- `google.com.cluster.local` → NXDOMAIN (wasted)
- `google.com` → SUCCESS
- `google.com` → IPv6 SUCCESS

**With autopath (2 DNS queries total):**

- `google.com.default.svc.cluster.local` → CNAME google.com + SUCCESS!
- `google.com` → IPv6 SUCCESS

## The magic revealed

The key difference is in that first response. Notice how with autopath enabled, when CoreDNS receives the query for `google.com.default.svc.cluster.local`, instead of returning NXDOMAIN, it returns:

```c
google.com.default.svc.cluster.local    canonical name = google.com.
```

CoreDNS recognized that `google.com` doesn't match any Kubernetes service pattern, so instead of returning NXDOMAIN and forcing the client to continue through the search path, it returned a CNAME pointing directly to the external domain. This eliminates the need for the remaining search path queries entirely.

The result is a 67% reduction in DNS queries (from 6 to 2) and significantly faster resolution times.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*l1KMEgDgPW-YBA0cpFgh0g.png)

## What autopath actually costs

While exploring this, I learned that autopath isn’t free. There are trade-offs you need to understand before implementing it in production.

`**pods verified**` **mode's impact**: While `pods verified` is necessary for `autopath`, it comes with a memory and CPU cost. CoreDNS needs to watch the Kubernetes API for all pod changes, which increases its memory footprint and puts additional load on the Kubernetes API server. In very large clusters, this needs to be factored into CoreDNS resource allocations.

- `**pods insecure**`: This option (instead of `verified`) simply returns an A record with the IP from the request without checking Kubernetes. It's less secure and generally not recommended with `autopath`.
- `**pods disabled**`: CoreDNS will not process pod requests at all, always returning `NXDOMAIN`. `autopath` cannot function in this mode for in-cluster lookups.

You can monitor CoreDNS memory usage to understand the impact in your environment:

```c
# Check current CoreDNS memory usage
kubectl top pods -n kube-system -l k8s-app=kube-dns
```

## Monitoring the impact

Let’s set up monitoring to understand what autopath is actually doing:

```c
# Port-forward to CoreDNS metrics
kubectl port-forward -n kube-system service/kube-dns 9153:9153 &

# Check key metrics
curl -s http://localhost:9153/metrics | grep -E "(coredns_dns_request|coredns_autopath|coredns_cache)"
```

Key metrics to watch:

- `coredns_dns_requests_total` - Overall query rate
- `coredns_autopath_success_total` - Autopath operations working correctly
- `coredns_cache_hits_total` vs `coredns_cache_misses_total` - Cache effectiveness

## When autopath might not be the right choice

During my exploration, I discovered that autopath isn’t always the best solution. Here are alternatives worth considering:

**NodeLocal DNSCache** for very large clusters (5000+ pods):

This approach promises 10x reduction in DNS calls to CoreDNS, 100x reduction in DNS errors, and TCP upstream connections that eliminate UDP packet loss. However, it’s more complex to operate and debug.

**NDOTS tuning** for applications that primarily make external calls:

```c
apiVersion: v1
kind: Pod
spec:
  dnsConfig:
    options:
    - name: ndots
      value: "1"  # Reduced from default 5
    - name: single-request-reopen
      value: ""   # Helps with conntrack races
```

This reduces search path attempts, but requires application-level changes and careful consideration of your specific workload patterns.

**Application-level DNS caching** for high-volume applications:

```c
# Python example with connection pooling
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(
    max_retries=retry_strategy, 
    pool_connections=100, 
    pool_maxsize=100
)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

## Debugging techniques for DNS issues

When DNS goes wrong in Kubernetes (and it will), you need solid debugging techniques. Here are the approaches I learned during this investigation:

**Enable CoreDNS query logging** for temporary troubleshooting:

```c
kubectl patch configmap coredns -n kube-system --type merge -p '{
  "data": {
    "Corefile": ".:53 {\n    log\n    errors\n    health\n    ready\n    autopath @kubernetes\n    kubernetes cluster.local in-addr.arpa ip6.arpa {\n        pods verified\n        fallthrough in-addr.arpa ip6.arpa\n    }\n    prometheus :9153\n    forward . /etc/resolv.conf\n    cache 30\n    loop\n    reload\n    loadbalance\n}"
  }
}'

# Watch the logs to see query patterns
kubectl logs -f -n kube-system -l k8s-app=kube-dns
```

**Check for conntrack issues** that often hide behind DNS problems:

```c
# Create a privileged debug pod
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: debug-node
spec:
  containers:
  - name: debug
    image: nicolaka/netshoot
    command: ["/bin/bash", "-c", "sleep 3600"]
    securityContext:
      privileged: true
  hostNetwork: true
  hostPID: true
EOF

# Check for conntrack races
kubectl exec -it debug-node -- conntrack -S | grep insert_failed
# Monitor conntrack table utilization  
kubectl exec -it debug-node -- cat /proc/sys/net/netfilter/nf_conntrack_count
kubectl exec -it debug-node -- cat /proc/sys/net/netfilter/nf_conntrack_max
```

If `insert_failed` is growing, you've got the UDP DNS race condition that NodeLocal DNSCache is designed to solve. More on these in the next article.

## What I learned from this deep dive

After exploring autopath thoroughly, here’s what I’d recommend for fellow engineers:

**Consider enabling autopath if:**

- Your cluster makes frequent external API calls
- You have fewer than 5000 pods
- You want to reduce DNS query load on CoreDNS
- You’re comfortable with increased memory usage

**Look at alternatives if:**

- You’re working with very large clusters (research NodeLocal DNSCache)
- Memory usage is a primary concern
- Your workloads are purely internal (ndots tuning might be sufficient)
- You want the simplest possible solution

The key insight I gained from this DNS performance exploration is that default Kubernetes DNS configuration is fundamentally inefficient for mixed internal/external workloads. Whether you fix it with autopath, NodeLocal DNSCache, or ndots tuning matters less than recognizing and understanding the problem in the first place.

Try It Yourself

Experience the CoreDNS autopath optimization interactively at [demos.learningdevops.com/coredns-autopath](https://demos.learningdevops.com/coredns-autopath/). The demo simulates the exact DNS behavior we explored, letting you see the performance difference between default CoreDNS and autopath-enabled configurations.

## Conclusion:

This investigation taught me that modern Kubernetes DNS performance isn’t just about the dramatic improvements you see in blog posts. Sometimes the most valuable lessons come from understanding why something doesn’t work as expected, or why the improvements are more subtle than anticipated.

The 50% reduction in DNS queries and improved resolution times might not sound earth-shattering, but when you’re processing thousands of API calls per second, these optimizations add up quickly. More importantly, understanding how DNS resolution actually works in your cluster gives you the knowledge to troubleshoot issues when they inevitably arise.

Remember, DNS problems love to hide in plain sight, and good observability combined with a solid understanding of how resolution actually works is your best defense against those late-night incidents.

## Connect & Continue Learning 🚀

Enjoyed this article? Clap until your fingers hurt (or just 50 times, whichever comes first)!

[**Read my other articles**](https://medium.com/@rk90229) **—** because one tech rabbit hole deserves another!

[**Connect with me on LinkedIn**](https://www.linkedin.com/in/techwith-rajesh/) for more tech insights — it’s like subscribing, but with fewer annoying notifications.

Have a suggestion for my next post? Drop a comment below! I read them all (even the ones suggesting I should’ve used spaces instead of tabs).

*P.S. Let me know what topics you’d like me to cover next!*

DevOps/SRE engineer diving deep into Go & open source. Learning through breaking things, then fixing them. Coffee-fueled technical deep dives ahead.

## More from Rajesh Kumar

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--3650eb0c477a---------------------------------------)