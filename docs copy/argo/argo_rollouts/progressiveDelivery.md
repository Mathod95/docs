# Progressive Delivery

## Essentials of CI/CD and Progressive Delivery in Software Development
Continuous Integration (CI), Continuous Delivery (CD), and Progressive Delivery are key concepts in modern software development, particularly in the context of DevOps and agile practices. They represent different stages or approaches in the software release process. We will discuss them more in this chapter.

---

## Continuous Integration
Continuous Integration is a development practice where developers frequently integrate their code into a shared repository, preferably several times daily. Each integration is then verified by an automated build and automated tests.

CI Features

- **Frequent code commits:** Encourage developers to often integrate their code into the main branch, reducing integration challenges.
- **Automated tests:** Cover frequent code commits. Automatically running tests on the new code to ensure it integrates well with the existing codebase. This does not only include unit tests, but also any other higher-order testing method, such as integration- or end-to-end tests.
- **Immediate problem detection:** Allows for quick detection and fixing of integration issues.
- **Reduced integration problems:** Help to minimize the problems associated with integrating new code.

The main goal of CI is to provide rapid feedback so that if a defect is introduced into the code base, it is identified and corrected as soon as possible.

Once code is in our main branch, it is not deployed in production or even released. This is where the concept of Continuous Delivery comes into play.

---

## Continuous Delivery
Continuous Delivery is an extension of CI, ensuring the software can be reliably released anytime. It involves the automation of the entire software release process.

**CD Features:**

- **Automated release process:** Every change that passes the automated tests can be released to production through an automated process.
- **Reliable deployments:** Ensure that the software is always in a deployable state.
- **Rapid release cycles:** Facilitate frequent and faster release cycles.
- **Close collaboration between teams:** A close alignment between development, QA, and operations teams is required.

The objective of Continuous Delivery is to establish a process where software deployments become predictable, routine, and can be executed on demand.

---

## Progressive Delivery
Progressive delivery is often described as an evolution of continuous delivery. It focuses on releasing updates of a product in a controlled and gradual manner, thereby reducing the risk of the release, typically coupling automation and metric analysis to drive the automated promotion or rollback of the update.

- **Progressive Delivery Features:**

    - **Canary releases:** Gradually roll out the change to a small subset of users before rolling it out to the entire user base.
    - **Feature flags:** Control who gets to see what feature in the application, allowing for selective and targeted deployment.
    - **Experiments & A/B testing:** Test different versions of a feature with different segments of the user base.
    - **Phased rollouts:** Slowly roll out features to incrementally larger segments of the user base, monitoring and adjusting based on feedback.

The primary goal of Progressive Delivery is to reduce the risk associated with releasing new features and to enable faster iteration by getting early feedback from users.

---

## Deployment Strategies
Every software system is different, and deploying complex systems oftentimes requires additional steps and checks. This is why different deployment strategies emerged over time to manage the process of deploying new software versions in a production environment.

These strategies are an integral part of DevOps practices, especially in the context of CI/CD workflows. The choice of a deployment strategy can significantly impact the availability, reliability, and user experience of a software application or software service.

On the following pages, we will present the four most important deployment strategies and discuss their impact on user experience during deployment:

- Recreate
- Rolling update
- Blue-green deployment
- Canary deployment

---

## Recreate

Un déploiement `Recreate` supprime l’ancienne version de l’application avant de démarrer la nouvelle. Par conséquent, cela garantit que deux versions de l’application ne s’exécutent jamais en même temps, mais il y a un temps d’arrêt pendant le déploiement.

![](../../../assets/images/argo/rollouts/rollouts.excalidraw#recreate)

Cette stratégie est une option de l’objet Deployment de Kubernetes et convient aux environnements où un bref temps d’arrêt est acceptable ou lorsque la persistance de l’état n’est pas une préoccupation.

---

## Rolling Update

Une Rolling Update remplace progressivement les pods exécutant l’ancienne version du container par de nouveaux pods exécutant la nouvelle version du container..  
À mesure que la nouvelle version est mise en service, les anciens pods sont réduits afin de maintenir le nombre total d’instances de l’application, tout en surveillant la santé et la disponibilité du service après chaque étape.  
Cela permet de réduire le temps d’arrêt et les risques, car la nouvelle version est déployée de manière contrôlée.  

![](../../../assets/images/argo/rollouts/rollouts.excalidraw#rollingUpdate)

---

## Blue-Green deployment

A blue-green deployment has both the new and old versions of the application deployed at the same time. During this time, only the old version of the application will receive production traffic. This allows the developers to run tests against the new version before switching the live traffic to the new version. Once the new version is ready and tested, the traffic is switched (often at the load balancer level) from the old environment to the new one. The advantage here is a quick rollback in case of issues and minimal downtime during deployment.

An important drawback of a blue-green deployment is, that twice the amount of instances is created during the time of the deployment. This is a common show-stopper for this pattern.

To learn more about the blue-green deployment, see the article by Martin Fowler.

![](../../../assets/images/argo/rollouts/rollouts.excalidraw#blueGreen)

---

## Canary deployment

A small subset of users are directed to the new version of the application while the majority still use the old version. Based on the feedback and performance of the new version, the deployment is gradually rolled out to more users. This reduces risk by affecting a small user base initially, allows for A/B testing and real-world feedback. While this is technically possible in native Kubernetes by manually adjusting Service Selectors between the “old” and “new” versions of a deployment, having an automated solution is more ideal.

Some more detailed information can be found in the Canary Release article by Danilo Sato.

![](../../../assets/images/argo/rollouts/rollouts.excalidraw#canary)

---

## Strategies for Smooth and Reliable Releases
In summary, deployment strategies are fundamental in modern software development and operations for ensuring smooth, safe, and efficient software releases. They cater to the need for balancing rapid deployment with the stability and reliability of production environments.


**Benefits of Introducing Deployment Strategies**

| **Benefit**               | **Description**                                                                                                                                                                                                      |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Risk mitigation**       | - They allow for safer deployments by reducing the risk of introducing bugs or performance issues into the production environment. <br> - Strategies like canary deployments enable gradual exposure to new changes. |
| **User experience**       | - Maintaining a consistent and high-quality user experience is essential. <br> - Strategies like blue-green deployments minimize downtime and potential disruptions to the user experience.                          |
| **Feedback and testing**  | - They provide a framework for gathering real-world user feedback. <br> - Canary deployments, in particular, are valuable for understanding how changes perform in a live environment.                               |
| **Rollback capabilities** | - In case new versions have critical issues, strategies like blue-green deployments allow for quick rollbacks to the previous stable version.                                                                        |


**Common Use Cases for Each Strategy**

| **Strategy**              | **Supported By**   | **Common Use Cases**                                                                                                                                                             |
|---------------------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Fixed deployment**      | Kubernetes Native  | - The most basic way to deploy a workload is whenever downtime is acceptable. <br> - Often stateful workloads (e.g., Databases) require a “recreation” to avoid data corruption. |
| **Rolling update**        | Kubernetes Native  | - Commonly used for stateless, low-maintenance workloads like proxies, RESTful APIs, etc.                                                                                        |
| **Blue-green deployment** | Argo Rollouts      | - Use when a) you can afford the extra cost of running twice the resources and b) need a quick and easy rollback option. <br> - B/G can also be helpful for experimentation scenarios. <br> - Can be advantageous to update services that depend on stateful connections, e.g., via WebSockets. |
| **Canary deployment**     | Argo Rollouts      | - Use it whenever a partial rollout is desirable (experimentation with a subset of users, desire a gradual rollout over hours or days, want to make rollout dependent on certain conditions). <br> - It can be a good alternative if the deployments are too large and the infra cost of running a full blue-green is too high. |