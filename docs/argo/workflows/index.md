# ARGO WORKFLOWS

## Introduction

### Chapter Overview and Objectives
In this chapter, we will explore the details of Argo Workflows, an extension of Argo, a popular GitOps tool designed for declarative continuous delivery of Kubernetes applications. Argo Workflows allows you to define and manage complex workflows as code, providing a way to orchestrate and automate multi-step processes within the Kubernetes environment.

By the end of this chapter, you should be able to comprehend the basics and architecture of Argo Workflows. This involves understanding its key components, how they interact, and the fundamental concepts that govern the execution of workflows. Here are learning objectives for gaining proficiency in Argo Workflows:

- Define and explain the structure of an Argo Workflow.
- Recognize key elements such as metadata, spec, entrypoint, and templates.
- Understand the role of templates in workflows.
- Identify and explain the primary components of Argo Workflows, including the Workflow Controller, and UI.
- Understand how Argo Workflows schedules and executes tasks.
- Dive into the responsibilities of the Workflow Controller.

## Argo Workflows Core Concepts

### Workflow
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

### Template Types

Un template peut être un container, un script, un DAG (Directed-Acyclic Graph), ou d'autres types selon la structure du workflow. Il se divise en deux groupes : les *template definitions* (qui définissent les tâches à accomplir) et les *template invocators* (qui appellent d'autres templates et gèrent le contrôle d'exécution).

Il existe 9 types de templates, répartis en deux catégories différentes.

#### Template Definitions

##### Container
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

##### Script
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

##### Resource
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

!!! Quote "TODO"

    TODO: Ajouter un exemple plus parlant
    
    ##### Suspend
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

!!! Note "CHECK"
    ##### Plugin
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

##### Container Set
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
##### HTTP
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

#### Template Invocators
Ces templates sont utilisés pour invoquer/appeler d'autres templates et fournir un contrôle d'exécution.

!!! Quote "TODO"

    **TODO**: Principe de synchronization et when

    ##### Steps
    Les steps permettent de définir plusieurs étapes dans un template, avec des tâches exécutées séquentiellement ou en parallèle. 

    Un steps template suit une structure de *list of lists*:

      - Les listes extérieures s’exécutent séquentiellement  
      - Les listes intérieures en parallèle.

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: steps-
    spec:
      entrypoint: hello-hello-hello

      # This spec contains two templates: hello-hello-hello and print-message
      templates:
      - name: hello-hello-hello
        # Instead of just running a container
        # This template has a sequence of steps
        steps:
        - - name: hello1            # hello1 is run before the following steps
            template: print-message
            arguments:
              parameters:
              - name: message
                value: "hello1"
        - - name: hello2a           # double dash => run after previous step
            template: print-message
            arguments:
              parameters:
              - name: message
                value: "hello2a"
          - name: hello2b           # single dash => run in parallel with previous step
            template: print-message
            arguments:
              parameters:
              - name: message
                value: "hello2b"

      # This is the same template as from the previous example
      - name: print-message
        inputs:
          parameters:
          - name: message
        container:
          image: busybox
          command: [echo]
          args: ["{{inputs.parameters.message}}"]
    ```

    !!! Note

        ```bash
        argo -n argo get hello-hello-hello
        STEP            TEMPLATE           PODNAME                 DURATION  MESSAGE
        ✔ steps-z2zdn  hello-hello-hello
        ├───✔ hello1   print-message      steps-z2zdn-27420706    2s
        └─┬─✔ hello2a  print-message      steps-z2zdn-2006760091  3s
          └─✔ hello2b  print-message      steps-z2zdn-2023537710  3s
        ```

    !!! Note

        Dans cet exemple, hello1 s'exécute en premier. Une fois terminé, hello2a et hello2b s'exécuteront en parallèle

---

##### DAG
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

### Outputs

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

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: simple-output-example-
spec:
  entrypoint: main
  templates:
  - name: main
    steps:
    - - name: generate
        template: producer
    - - name: consume
        template: consumer
        arguments:
          parameters:
          - name: outputMessage
            from: "{{steps.generate.outputs.result}}"

  - name: producer
    script:
      image: busybox:1.28
      command: [sh, -c]
      args: echo "hello from the producer step"
  - name: consumer
    inputs:
      parameters:
      - name: message
    container:
      image: busybox:1.28
      command: [sh, -c]
      args: [" Received: '{{inputs.parameters.outputMessage}}'"]
```

!!! Quote "Expliquer argument parameters et artefact"

    In Argo Workflows, the terms parameters, arguments, and artifacts are related but play different roles. Here’s a clear, practical breakdown with examples.

    1. Parameters
    What they are


    Small, simple values (strings, numbers, booleans, JSON-as-string)


    Used to control logic or configuration


    Passed by value


    Where they live


    Defined in a template


    Referenced inside that template


    Example
    templates:
    - name: greet
      inputs:
        parameters:
        - name: name
      container:
        image: alpine
        command: [sh, -c]
        args: ["echo Hello {{inputs.parameters.name}}"]

    Think of parameters as

    Command-line flags or function parameters


    2. Arguments
    What they are


    Concrete values you pass to a template’s inputs


    Can include parameters and artifacts


    They are the instance of an input, not the definition


    Where they live


    At the workflow level or when calling another template


    Example
    workflow:
      entrypoint: greet
      arguments:
        parameters:
        - name: name
          value: Alice

    or when calling a template from another template:
    - name: call-greet
      template: greet
      arguments:
        parameters:
        - name: name
          value: Bob

    Think of arguments as

    The actual values you pass when calling a function


    3. Artifacts
    What they are


    Files or directories, often large


    Used for data exchange between steps


    Stored in artifact repositories (S3, GCS, MinIO, etc.)


    Passed by reference, not by value


    Where they live


    Defined as inputs or outputs of templates


    Example
    templates:
    - name: generate-file
      container:
        image: alpine
        command: [sh, -c]
        args: ["echo hello > /tmp/hello.txt"]
      outputs:
        artifacts:
        - name: greeting-file
          path: /tmp/hello.txt

    Passing the artifact to another step:
    - name: consume-file
      template: read-file
      arguments:
        artifacts:
        - name: greeting-file
          from: "{{steps.generate-file.outputs.artifacts.greeting-file}}"

    Think of artifacts as

    Files passed via shared storage


    Side-by-Side Comparison
    ConceptPurposeSizePassed HowTypical UseParameterControl behavior/configSmallBy valueFlags, names, countsArgumentAssign input valuesN/AN/ACalling templatesArtifactShare files/data between stepsLargeBy referenceModels, datasets, reports

    Mental Model (Most Helpful)
    If Argo were a programming language:


    Template = function definition


    Parameters = function parameters


    Arguments = function call arguments


    Artifacts = files passed via shared storage



    If you want, I can:


    Show a full end-to-end workflow example


    Explain when to use parameter vs artifact


    Compare artifacts vs volumes vs outputs

    ---

    ✅ Parameters vs. Arguments

    The docs explain that:

    A Workflow provides arguments, which are the values you supply when you run or call a template.

    A template defines inputs, and those inputs include parameters. When you call that template, you pass arguments to match those input parameters. 
    Argo Workflows

    Key points from docs:

    arguments are what the workflow or another caller supplies to a template.

    parameters are defined by the template as named values it expects. 
    Argo Workflows

    This aligns with the analogy:

    Parameters = function parameter definitions
    Arguments = actual values supplied at call time

    ✅ Artifacts

    The documentation also clearly distinguishes artifacts from parameters:

    Artifacts are files or directories passed between steps, typically stored in or retrieved from an artifact repository.

    In the workflow spec, artifacts are part of the inputs or outputs of templates, similarly to parameters, but they represent large data objects, not simple values. 
    Argo Workflows

    For example, in an arguments: block you see both:

    arguments:
      parameters:
        - name: ...
          value: ...
      artifacts:
        - name: ...
          from: ...


    Which matches how Argo separates values (parameters) from file artifacts. 
    Argo Workflows

    📌 Summary with Doc Support
    Term	Meaning in Argo Docs	Example in Spec
    Parameters	Named values templates expect	inputs: parameters: 
    Argo Workflows

    Arguments	Values passed to templates	arguments: parameters: 
    Argo Workflows

    Artifacts	Files/large data passed between steps	arguments: artifacts: 
    Argo Workflows
    +1

    If you want, I can point you to the exact sections of the official docs that cover each concept (“Workflow Inputs”, “Artifacts”, and “Output Parameters”) so you can see the definitions side-by-side.

---

### WorkflowTemplate
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

## Argo Workflows Architecture

### Defining Argo Workflows and Its Components
Argo Workflows is an open source workflow orchestration platform designed for Kubernetes. It enables users to define, run, and manage complex workflows using Kubernetes as the underlying execution environment. All of Argo Workflows’ components are independent of other Argo projects and are usually deployed into their own Kubernetes namespace in a cluster.

**Argo Server**
The Argo Server is a central component that manages the overall workflow resources, state, and interactions. It exposes a REST API for workflow submission, monitoring, and management. The server maintains the state of workflows and their execution and interacts with the Kubernetes API server to create and manage resources.

**Workflow Controller**
The Argo Workflows Controller is a critical component within the Argo Workflows system. It is responsible for managing the lifecycle of workflows, interacting with the Kubernetes API server, and ensuring the execution of workflows according to their specifications. The Argo Workflows Controller continuously watches the Kubernetes API server for changes related to Argo Workflows Custom Resources (CRs). The primary CR involved is the Workflow, which defines the workflow structure and steps. Upon detecting the creation or modification of a Workflow CR, the controller initiates the corresponding workflow execution. The controller is responsible for managing the complete lifecycle of a workflow, including its creation, execution, monitoring, and completion. It also resolves dependencies between steps within a workflow. It ensures that steps are executed in the correct order, based on dependencies specified in the workflow definition.

**Argo UI**
The Argo UI is a web-based user interface for visually monitoring and managing workflows. It allows users to view workflow status, logs, and artifacts, as well as submit new workflows.

Both the Workflow Controller and Argo Server run in the argo namespace. We can opt for one of the cluster or namespaced installations, however, the generated Workflows and the Pods will be run in the respective namespace.

The diagram below shows an overview of a Workflow and also details of a namespace with generated pods.

https://d36ai2hkxl16us.cloudfront.net/course-uploads/e0df7fbf-a057-42af-8a1f-590912be5460/utgl42dbrozx-LFS256_CourseTrainingGraphics-3.png

Argo Workflow building blocks

 

A user defines a workflow using YAML or JSON files, specifying the sequence of steps, dependencies, inputs, outputs, parameters, and any other relevant configurations. Then the workflow definition file is submitted to the Kubernetes cluster where Argo Workflows is deployed. This submission can be done via the Argo CLI, Argo UI, or programmatically through Kubernetes API clients.

The Workflow Controller component of Argo Workflows continuously monitors the Kubernetes cluster for new workflow submissions or updates to existing workflows. When a new workflow is submitted, the Workflow Controller parses the workflow definition to validate its syntax and semantics. If there are any errors or inconsistencies, the Workflow Controller reports them to the user for correction.

Once the workflow definition is validated, the Workflow Controller creates the necessary Kubernetes resources to represent the workflow, such as Workflow CRDs (Custom Resource Definitions) and associated Pods, Services, ConfigMaps, and Secrets.

Finally, Workflow Controller begins executing the steps defined in the workflow. Each step may involve running containers, executing scripts, or performing other actions specified by the user. Argo Workflows ensures that steps are executed in the correct order based on dependencies defined in the workflow.

## Argo Workflows Architecture

### Argo Workflow Overview
Each Step and DAG causes the generation of a Pod which comprises three containers:

- init: a template that contains an init container that performs initialization tasks. In this case, it echoes a message and sleeps for 30 seconds, but you can replace these commands with your actual initialization steps.
- main: a template contains the main container that executes the primary process once the initialization is complete.
- wait: a container that executes tasks such as clean up, saving off parameters, and artifacts.
To learn more about Experiments, please consult the [official documentation](https://argo-workflows.readthedocs.io/en/latest/workflow-concepts/).

---

## Use Cases for Argo Workflow
### Examples
Argo Workflows is a versatile tool with a wide range of use cases in the context of Kubernetes and containerized environments. Here are some common use cases where Argo Workflows can be beneficial:

- To orchestrate end-to-end data processing pipelines, including data extraction, transformation, and loading (ETL) tasks.
- In machine learning projects, Argo Workflows can orchestrate tasks such as data preprocessing, model training, evaluation, and deployment.
- Argo Workflows can serve as the foundation for continuous integration and continuous deployment (CI/CD) pipelines. It enables the automation of building, testing, and deploying applications in a Kubernetes environment.
- For batch processing and periodic tasks, Argo Workflows can be configured to run at specified intervals or based on cron schedules. This is useful for automating routine tasks, report generation, and other scheduled jobs.

---

## Lab Exercises

### Lab 4.1. Installing Argo Workflows
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

### Lab 4.2. A Simple DAG Workflow
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

### Lab 4.3. CI/CD Using Argo Workflows
Lab Tips and Best Practices
When working on the lab exercises, please keep the following in mind:

When accessing external URLs embedded in the PDF document below, always use right-click and open in a new tab or window. Attempting to open the URL by directly clicking on it will close your course window/tab.
Depending on your PDF viewer, if you are cutting and pasting from the document, you may lose the original formatting. For example, underscores might disappear and be replaced by spaces. Therefore, you may need to manually edit the text. Always double-check that the pasted text is correct.

---

## Walk Through

!!! QUOTE

    ### Parameters

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hello-world-parameters-
    spec:
      # invoke the print-message template with "hello world" as the argument to the message parameter
      entrypoint: print-message
      arguments:
        parameters:
        - name: message
          value: hello world

      templates:
      - name: print-message
        inputs:
          parameters:
          - name: message       # parameter declaration
        container:
          # run echo with that message input parameter as args
          image: busybox
          command: [echo]
          args: ["{{inputs.parameters.message}}"]
    ```

    ```bash hl_lines="1"  
    argo submit arguments-parameters.yaml -p message="goodbye world"
    ```

    #### Parameters file

    In case of multiple parameters that can be overridden, the argo CLI provides a command to load parameters files in YAML or JSON format. Here is an example of that kind of parameter file:

    ```yaml linenums="1" title="params.yaml"
    message: goodbye world
    ```
    To run use following command:

    ```bash hl_lines="1"
    argo submit arguments-parameters.yaml --parameter-file params.yaml
    ```

    #### Entrypoint ???

    FROM THE UI you can override the parameters

## WorkflowTemplate

A reusable recipe for workflows, defined once and used across multiple workflows

Benefits:
  - central, version-controlled library
  - promote consistency across workflows
  - cleaner and easier to manage
  - reduce duplication and maintenance effort


```yaml linenums="1" title="workflow-template-library.yaml"
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: cowsay-template
  namespace: argo
spec:
  entrypoint: cowsay
  templates:
  - name: cowsay
    inputs:
      parameters:
        - name: message
    container:
      image: rancher/cowsay
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]
```

```bash hl_lines="1"
argo -n argo template create workflow-template-library.yaml
```

```yaml title="templateRef.yaml"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: use-single-template-
spec:
  entrypoint: my-custom-workflow
  templates:
  - name: my-custom-workflow
    steps:
      - - name: first-step
          templateRef:
            name: cowsay-template
            template: cowsay
          arguments:
            parameters:
              - name: message
                values: "I called this from another workflow!"
```

```yaml title="templateRef.yaml"
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: run-whole-template-
  namespace: argo
spec:
  arguments:
    parameters:
      - name: message
        value: "Hello from WorkflowTemplate!"
  workflowTemplateRef:
    name: cowsay-template
```

### Cluster Workflow Template

cluster-wide version of a WorkflowTemplate
cluster-scoped: Usable across all namespaces
Managed by DevOps
Provides a central library of reusable templates and promotes consistency

Donc pour de la création de resources clusterworkflowtemplate et pour des commande de check de pods etc workflowTemplate tous court

https://learn.kodekloud.com/user/courses/certified-argo-project-associate-capa/module/44223b5d-ccc3-4dcb-8292-66036e2ea023/lesson/7fd60c67-290c-4eb8-a6d6-47ad6a9ea72c?autoplay=true
```
clusterScope: true
```

```yaml
spec:
  entrypoint: main
  arguments:
    parameters:
      - name: environment
        value: "production"
  templates:
    - name: main
      steps:
        - - name: build
        - - template: build-step
        - - name: test
        - - template: test-step
        - - when: "{{workflow.parameters.environment}} != production"
        - - name: deploy
        - - template: deploy-step
        
    - name: build-step
        container:
          image: alpine
          command: [sh, -c]
          args: ["echo 'Building application...'"]
    - name: test-step
      container:
        image: alpine
        command: [sh, -c]
        args: ["echo 'Running tests...'"]
    - name: deploy-step
      container:
        image: alpine
        command: [sh, -c]
        args: ["echo 'Deploying to {{workflow.parameters.environment}}'"]
```

#### when


#### daemon
#### activeDeadlineSecondes

!!! Quote "Timeouts"

    #### onExit

    You can use the field activeDeadlineSeconds to limit the elapsed time for a workflow:

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: timeouts-
    spec:
      activeDeadlineSeconds: 10 # terminate workflow after 10 seconds
      entrypoint: sleep
      templates:
      - name: sleep
        container:
          image: alpine:3.23
          command: [sh, -c]
          args: ["echo sleeping for 1m; sleep 60; echo done"]
    ```
    You can limit the elapsed time for a specific template as well:

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: timeouts-
    spec:
      entrypoint: sleep
      templates:
      - name: sleep
        activeDeadlineSeconds: 10 # terminate container template after 10 seconds
        container:
          image: alpine:3.23
          command: [sh, -c]
          args: ["echo sleeping for 1m; sleep 60; echo done"]
    ```  

!!! Quote "Retrying Failed or Errored Steps"

    #### retryStrategy

    You can specify a retryStrategy that will dictate how failed or errored steps are retried:

    ```yaml linenums="1"
    # This example demonstrates the use of retry back offs
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: retry-backoff-
    spec:
      entrypoint: retry-backoff
      templates:
      - name: retry-backoff
        retryStrategy:
          limit: 10
          retryPolicy: "Always"
          backoff:
            duration: "1"      # Must be a string. Default unit is seconds. Could also be a Duration, e.g.: "2m", "6h", "1d"
            factor: 2
            maxDuration: "1m"  # Must be a string. Default unit is seconds. Could also be a Duration, e.g.: "2m", "6h", "1d"
          affinity:
            nodeAntiAffinity: {}
        container:
          image: python:alpine3.23
          command: ["python", -c]
          # fail with a 66% probability
          args: ["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"]
    ```

    limit is the maximum number of times the container will be retried.
    retryPolicy specifies if a container will be retried on failure, error, both, or only transient errors (e.g. i/o or TLS handshake timeout). "Always" retries on both errors and failures. Also available: OnFailure (default), "OnError", and "OnTransientError" (available after v3.0.0-rc2).
    backoff is an exponential back-off
    nodeAntiAffinity prevents running steps on the same host. Current implementation allows only empty nodeAntiAffinity (i.e. nodeAntiAffinity: {}) and by default it uses label kubernetes.io/hostname as the selector.
    Providing an empty retryStrategy (i.e. retryStrategy: {}) will cause a container to retry until completion.


#### successCondition