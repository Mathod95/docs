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