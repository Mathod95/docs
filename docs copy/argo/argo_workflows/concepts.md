# Argo Workflows Core Concepts

## Workflow
A workflow is a series of tasks, processes, or steps that are executed in a specific sequence to achieve a particular goal or outcome. Workflows are prevalent in various domains, including business, software development, and project management. In the context of Argo and other DevOps tools, a workflow specifically refers to a sequence of automated steps involved in the deployment, testing, and promotion of software applications.

In Argo, the term Workflow is a Kubernetes Custom Resource that represents a sequence of tasks or steps that are defined and orchestrated to achieve a specific goal. It is a higher-level abstraction that allows users to describe complex processes, dependencies, and conditions in a structured and declarative manner. A Workflow also maintains the state of a workflow.

Next, we will take a look at the specs of a simple Workflow.

The main part of a Workflow spec contains an entrypoint and list of templates, as shown in the example below:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  entrypoint: whalesay
  templates:
- name: whalesay
  container:
    image: docker/whalesay
    command: [cowsay]
    args: ["hello world"]
```

A Workflow spec has two core parts:

Entrypoint: Specifies the name of the template that serves as the entrypoint for the workflow. It defines the starting point of the workflow execution.
Templates: A template represents a step or task in the workflow that should be executed. There are six types of templates that we will introduce next.

---

## Template Types

Un template peut être un container, un script, un DAG (Directed-Acyclic Graph), ou d'autres types selon la structure du workflow. Il se divise en deux groupes : les *template definitions* (qui définissent les tâches à accomplir) et les *template invocators* (qui appellent d'autres templates et gèrent le contrôle d'exécution).

Il existe 9 types de templates, répartis en deux catégories différentes.

### Template Definitions

**Container**
Un *container* est le type de template le plus courant et représente une étape dans le workflow qui exécute un container. Il est adapté pour l'exécution d'applications ou de scripts containerisés.

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: whalesay-
spec:
  entrypoint: whalesay
  templates:
  - name: whalesay
    container:
      image: docker/whalesay
      command: [cowsay]
      args: ["hello world"]
```

---

**Resource**
Une *resource* représente un template pour créer, modifier ou supprimer des ressources Kubernetes. Elle est utile pour effectuer des opérations sur les objets Kubernetes dans le cluster où les workflows sont actuellement exécutés.

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: kubernetes-resource-
spec:
  entrypoint: kubernetes-resource
  templates:
  - name: kubernetes-resource
    resource:
      action: create
      manifest: |
        apiVersion: v1
        kind: ConfigMap
        metadata:
          generateName: app-production-
        data:
          some: value
```

---

**Script**
Un *script* est similaire au template container, mais permet de spécifier le script directement, sans faire référence à une image de container externe. Il peut être utilisé pour des scripts simples ou des commandes en une seule ligne.

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: gen-random-int-
spec:
  entrypoint: gen-random-int
  templates:
  - name: gen-random-int
    script:
      image: python:alpine3.6
      command: [python]
      source: |
        import random
        i = random.randint(1, 100)
        print(i)
```

---

!!! Quote "TODO"

    TODO: Ajouter un exemple plus parlant
    
    **Suspend**
    Un suspend est un template qui suspend l'exécution, soit pendant une durée déterminée, soit jusqu'à ce qu'il soit repris manuellement. Il peut être repris via CLI, API ou l'UI.

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: delay-
    spec:
      entrypoint: delay
      templates:
      - name: delay
        suspend:
          duration: "30s"
    ```

---

!!! Quote "TODO"
    **Plugin**
    Un plugin permet d'intégrer des actions avec des services externes, comme Slack. Par exemple, il peut être utilisé pour envoyer des notifications dans un canal Slack directement depuis ton workflow.

    ```yaml linenums="1" title="PLUGIN"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: argocd-example-
    spec:
      entrypoint: main
      templates:
      - name: main
        plugin:
          argocd:
            serverUrl: https://argocd.mathod.io/
            actions:
              - sync:
                  project: platform
                  apps:
                    - crossplane
                    - kyverno
    ```

---

**Container Set**
```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: container-set-template-
spec:
  entrypoint: main
  templates:
    - name: main
      containerSet:
        containers:
          - name: a
            image: rancher/cowsay
            command: [cowsay]
            args: ["container A"]
          - name: b
            image: rancher/cowsay
            command: [cowsay]
            args: ["container B"]
```

---
**HTTP**
```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: http-template-example-
spec:
  entrypoint: fetch-todo-item
  templates:
  - name: fetch-todo-item
    http:
      url: "https://mathod.io/todos/1"
      method: "GET"
      headers:
        - name: "Content-Type"
          value: "application/json"
```

---

### Template Invocators

**DAG**
A DAG (Directed-Acyclic Graph) allows defining our tasks as a graph of dependencies. It is beneficial for workflows with complex dependencies and conditional execution. 

```yaml linenums="1"
- name: diamond
  dag:
    tasks:
    - name: A
      template: echo
    - name: B
      dependencies: [A]
      template: echo
    - name: C
      dependencies: [A]
      template: echo
    - name: D
      dependencies: [B, C]
      template: echo
```

!!! Note

    Dans cet exemple, A s'exécute en premier. Une fois terminé, B et C s'exécuteront en parallèle, et une fois qu'ils auront tous les deux terminé, D s'exécutera

---

**Steps**
Steps are defining multiple steps within a template as several steps need to be executed sequentially or in parallel.

```
- name: hello-hello-hello
  steps:
  - - name: step1
      template: prepare-data
  - - name: step2a
      template: run-data-first-half
    - name: step2b
      template: run-data-second-half
```

---

## Outputs

In Argo Workflows, the outputs section within a step template allows you to define and capture outputs that can be accessed by subsequent steps or referenced in the workflow definition. Outputs are useful when you want to pass data, values, or artifacts from one step to another. Here's an overview of how outputs work in Argo Workflows. The Output comprises two key concepts:

Defining Outputs: You define outputs within a step template using the outputs section. Each output has a name and a path within the container where the data or artifact is produced.
Accessing Outputs: You can reference the outputs of a step using templating expressions in subsequent steps or the workflow definition.
Let’s consider a simple example where one step generates an output parameter and an output artifact, and another step consumes them:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: artifact-passing-
spec:
  entrypoint: artifact-example
  templates:
  - name: artifact-example
    steps:
    - - name: generate-artifact
        template: whalesay
    - - name: consume-artifact
        template: print-message
        arguments:
          artifacts:
          - name: message
            from: "{{steps.generate-artifact.outputs.artifacts.hello-art}}"

  - name: whalesay
    container:
      image: docker/whalesay:latest
      command: [sh, -c]
      args: ["cowsay hello world | tee /tmp/hello_world.txt"]
    outputs:
      artifacts:
    - name: hello-art
      path: /tmp/hello_world.txt

  - name: print-message
    inputs:
      artifacts:
      - name: message
        path: /tmp/message
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["cat /tmp/message"]
```

First the `whalesay` template creates a file name `/tmp/hello-world.txt` by using the cowsay command. Next, it outputs this file as an artifact called hello-art. The `artifact-example` template provides the generated hello-art artifact as an output of the generate-artifact step. Finally, the `print-message` template takes an input artifact called message and consumes it by unpacking it in `/tmp/message` path and using the cat command to print it into standard output.

---

## WorkflowTemplate
In Argo Workflows, a WorkflowTemplate is a resource that defines a reusable and shareable workflow template, allowing users to encapsulate workflow logic, parameters, and metadata. This abstraction promotes modularity and reusability, enabling the creation of complex workflows from pre-defined templates.

Here is an example of a simple WorkflowTemplate definition in Argo Workflows:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: sample-template
spec:
  templates:
   - name: hello-world
     inputs:
       parameters:
         - name: msg
           value: "Hello World!"
     container:
       image: docker/whalesay
       command: [cowsay]
       args: ["{{inputs.parameters.msg}}"]
```

In this example:

- The WorkflowTemplate is named `sample-template`
- It contains a template: `hello-world`
- The `hello-world` template takes a parameter message (with a default value of "Hello, World!") and generates a file with the specified message.
Once defined, this WorkflowTemplate can be referenced and instantiated within multiple workflows. For example:

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
entrypoint: whalesay
templates:
  - name: whalesay
    steps:
      - - name: hello-world
          templateRef:
            name: sample-template
            template: hello-world
```

This workflow references the WorkflowTemplate named sample-template effectively inheriting the structure and logic defined in the template.

Using WorkflowTemplates is beneficial when you want to standardize and reuse specific workflow patterns, making it easier to manage, maintain, and share workflow definitions within your organization. They also help in enforcing consistency and reducing redundancy across multiple workflows.

---