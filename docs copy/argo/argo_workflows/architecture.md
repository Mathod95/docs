# Argo Workflows Architecture

## Defining Argo Workflows and Its Components
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

---

## Argo Workflow Overview
Each Step and DAG causes the generation of a Pod which comprises three containers:

- init: a template that contains an init container that performs initialization tasks. In this case, it echoes a message and sleeps for 30 seconds, but you can replace these commands with your actual initialization steps.
- main: a template contains the main container that executes the primary process once the initialization is complete.
- wait: a container that executes tasks such as clean up, saving off parameters, and artifacts.
To learn more about Experiments, please consult the [official documentation](https://argo-workflows.readthedocs.io/en/latest/workflow-concepts/).

---