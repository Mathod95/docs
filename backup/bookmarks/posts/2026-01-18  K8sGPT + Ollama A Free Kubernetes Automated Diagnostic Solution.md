---
title: "K8sGPT + Ollama: A Free Kubernetes Automated Diagnostic Solution"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://addozhang.medium.com/k8sgpt-ollama-a-free-kubernetes-automated-diagnostic-solution-d453b63f112f"
author:
  - "[[Addo Zhang]]"
---
<!-- more -->

[Sitemap](https://addozhang.medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GDvCWmvCMUBGUK-0ASQn0w.png)

I checked my blog drafts over the weekend and found this one. I remember writing it with “Kubernetes Automated Diagnosis Tool: k8sgpt-operator”(posted in Chinese) about a year ago. My procrastination seems to have reached a critical level. Initially, I planned to use K8sGPT + [LocalAI](https://localai.io/). However, after trying [Ollama](https://ollama.com/), I found it more user-friendly. Ollama also supports the [OpenAI API](https://github.com/ollama/ollama/blob/main/docs/openai.md), so I decided to switch to using Ollama.

After publishing the article introducing k8sgpt-operator, some readers mentioned the high barrier to entry for using OpenAI. This issue is indeed challenging but not insurmountable. However, this article is not about solving that problem but introducing an alternative to OpenAI: Ollama. Late last year, [k8sgpt entered the CNCF Sandbox](https://landscape.cncf.io/?item=observability-and-analysis--observability--k8sgpt).

## 1\. Installing Ollama

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*R0f3gT5RTaJhB6bG.png)

Ollama is an open-source large model tool that allows you to easily install and run [various large models](https://ollama.com/library) locally or in the cloud. It is very user-friendly and can be run with simple commands. On macOS, you can install it with a single command using homebrew:

```c
brew install ollama
```

The latest version is 0.1.44.

```c
ollama -v 
Warning: could not connect to a running Ollama instance
Warning: client version is 0.1.44
```

On Linux, you can also install it with the official script.

```c
curl -sSL https://ollama.com/install.sh | sh
```

Start Ollama and set the listening address to `0.0.0.0` through an environment variable to allow access from containers or K8s clusters.

```c
OLLAMA_HOST=0.0.0.0 ollama start
```
```c
...
time=2024-06-16T07:54:57.329+08:00 level=INFO source=routes.go:1057 msg="Listening on 127.0.0.1:11434 (version 0.1.44)"
time=2024-06-16T07:54:57.329+08:00 level=INFO source=payload.go:30 msg="extracting embedded files" dir=/var/folders/9p/2tp6g0896715zst_bfkynff00000gn/T/ollama1722873865/runners
time=2024-06-16T07:54:57.346+08:00 level=INFO source=payload.go:44 msg="Dynamic LLM libraries [metal]"
time=2024-06-16T07:54:57.385+08:00 level=INFO source=types.go:71 msg="inference compute" id=0 library=metal compute="" driver=0.0 name="" total="21.3 GiB" available="21.3 GiB"
```

## 2\. Downloading and Running Large Models

Llama3, one of the popular large models, was open-sourced by Meta in April. Llama3 has two versions: 8B and 70B.

I am running it on macOS, so I chose the 8B version. The 8B version is 4.7 GB, and it takes 3–4 minutes to download with a fast internet connection.

```c
ollama run llama3
```

On my M1 Pro with 32GB of memory, it takes about 12 seconds to start.

```c
time=2024-06-17T09:30:25.070+08:00 level=INFO source=server.go:572 msg="llama runner started in 12.58 seconds"
```

Each query takes about 14 seconds.

```c
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```
```c
....
"total_duration":14064009500,"load_duration":1605750,"prompt_eval_duration":166998000,"eval_count":419,"eval_duration":13894579000}
```

## 3\. Configuring K8sGPT CLI Backend

If you want to test k8sgpt-operator, you can skip this step.

We will use the Ollama REST API as the backend for k8sgpt, serving as the inference provider. Here, we select the backend type as `localai` because [LocalAI](https://localai.io/) is compatible with the OpenAI API, and the actual provider will still be Ollama running Llama.

```c
k8sgpt auth add --backend localai --model llama3 --baseurl http://localhost:11434/v1
```

Set it as the default provider.

```c
k8sgpt auth default --provider localai
Default provider set to localai
```

**Testing:**

Create a pod in k8s using the image `image-not-exist`.

```c
kubectl get po k8sgpt-test
NAME          READY   STATUS         RESTARTS   AGE
k8sgpt-test   0/1     ErrImagePull   0          6s
```

Use k8sgpt to analyze the error.

```c
k8sgpt analyze --explain --filter=Pod --namespace=default --output=json
```
```c
{
  "provider": "localai",
  "errors": null,
  "status": "ProblemDetected",
  "problems": 1,
  "results": [
    {
      "kind": "Pod",
      "name": "default/k8sgpt-test",
      "error": [
        {
          "Text": "Back-off pulling image \"image-not-exist\"",
          "KubernetesDoc": "",
          "Sensitive": []
        }
      ],
      "details": "Error: Back-off pulling image \"image-not-exist\"\n\nSolution: \n1. Check if the image exists on Docker Hub or your local registry.\n2. If not, create the image using a Dockerfile and build it.\n3. If the image exists, check the spelling and try again.\n4. Verify the image repository URL in your Kubernetes configuration file (e.g., deployment.yaml).",
      "parentObject": ""
    }
  ]
}
```

## 4\. Deploying and Configuring k8sgpt-operator

k8sgpt-operator can automate k8sgpt in the cluster. You can install it using Helm.

```c
helm repo add k8sgpt https://charts.k8sgpt.ai/
helm repo update
helm install release k8sgpt/k8sgpt-operator -n k8sgpt --create-namespace
```

k8sgpt-operator provides two CRDs: `K8sGPT` to configure k8sgpt and `Result` to output analysis results.

```c
kubectl api-resources  | grep -i gpt
k8sgpts                                        core.k8sgpt.ai/v1alpha1                true         K8sGPT
results                                        core.k8sgpt.ai/v1alpha1                true         Result
```

Configure `K8sGPT`, using Ollama's IP address for `baseUrl`.

```c
kubectl apply -n k8sgpt -f - << EOF
apiVersion: core.k8sgpt.ai/v1alpha1
kind: K8sGPT
metadata:
  name: k8sgpt-ollama
spec:
  ai:
    enabled: true
    model: llama3
    backend: localai
    baseUrl: http://198.19.249.3:11434/v1
  noCache: false
  filters: ["Pod"]
  repository: ghcr.io/k8sgpt-ai/k8sgpt
  version: v0.3.8
EOF
```

After creating the `K8sGPT` CR, the operator will automatically create a pod for it. Checking the `Result` CR will show the same results.

```c
kubectl get result -n k8sgpt -o jsonpath='{.items[].spec}' | jq .
{
  "backend": "localai",
  "details": "Error: Kubernetes is unable to pull the image \"image-not-exist\" due to it not existing.\n\nSolution: \n1. Check if the image actually exists.\n2. If not, create the image or use an alternative one.\n3. If the image does exist, ensure that the Docker daemon and registry are properly configured.",
  "error": [
    {
      "text": "Back-off pulling image \"image-not-exist\""
    }
  ],
  "kind": "Pod",
  "name": "default/k8sgpt-test",
  "parentObject": ""
}
```

CNCF Ambassador | LF APAC OpenSource Evangelist | Microsoft MVP | SA and Evangelist at [https://flomesh.io](https://flomesh.io/) | Programmer | Blogger | Mazda Lover | Ex-BBer

## More from Addo Zhang

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--d453b63f112f---------------------------------------)