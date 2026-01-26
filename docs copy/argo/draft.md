---

Argo Rollouts Features
Architecture
Argo Rollouts Components
Key Features of Argo Rollouts
Installation Options
Standard Cluster-Wide Installation
Deploy Argo Rollouts
Restrictedn Namespace-Scoped Installation
Deploy Argo Rollouts Namespace Scoped
CLI Installation



Deployment Strategies / Deyployment and Release pattern
Direct Conversion Method
workloadRef Method
Strategies for Smooth and Reliable Releases
Benefits of Introducing Deployment Strategies
Common Use Cases for Each Strategy
Rollout Analysis & Experiments
Experiments
Lab exercices
Lab - Installing Argo Rollouts
Objective
Prerequisites
Install Cluster and Argo Rollouts

Objective
Prerequisites
Transitioning to Argo Rollouts
Dashboard
Solutions à essayer dans l'ordre :
1. Vérifier la version d'Argo Rollouts
2. Utiliser le dashboard déployé dans le cluster (recommandé)
3. Créer un Rollout minimal
4. Essayer avec des options différentes
5. Utiliser l'extension ArgoCD (si tu as ArgoCD)
6. Debug avancé
Solution temporaire si urgent
1. Installation d'ArgoCD via Helm
2. Installation d'Argo Rollouts (nécessaire pour utiliser l'extension)
3. Accès à l'interface ArgoCD
4. Test de l'extension avec un Rollout exemple
Alternative : Si tu préfères configurer directement avec les volumes
Blue/Green - Initial Version
Specification
Demo blue green deployment
Canary

---

## Argo Rollouts Features

Progressive Delivery: Déployer progressivement de nouvelles versions de logiciels à un sous ensemble d'utilisateurs pour minimiser le risque
Rollout CRD: Rollout Controller est un CRD Kubernetes qui remplace l'objet de déploiement standard pour permettre ces stratégies avances
Canary Release: Expose une nouvelle version à un petit groupe d'utilistaur pour des test en direct avant un déploiement complet
Blue-Green Deployment: Fonctionner deux environement blue est stable et green est la nouvelle version. Switch traffic une fois que green est déployer green deviens blue
Analysis (metric providers): Intéroge des fourniseur de metriques comme Prometheus pour verfiiser si la nouvelle version est saine avant de continuer
Traffic Shaping: % pourcentage d'utilisateur qui bascule sur la nouvelle version (ingress controllers ou service mesh)
Automated rollbacks: Scrap des donnée de performance si l'analyse échoue le déploiement est automatiquement rétablie a la version stable précédente
gitops integration:

Argo Rollouts
Here, we will explore the Argo Rollouts resource, which is the central element in Argo Rollouts, enabling advanced deployment strategies. A Rollout, in essence, is a Kubernetes resource that closely mirrors the functionality of a Kubernetes Deployment object. However, it steps in as a more advanced substitute for Deployment objects, particularly in scenarios demanding intricate deployment of progressive delivery techniques.

---

## Installation Options

### Standard Cluster-Wide Installation

#### Deploy Argo Rollouts

Create a namespace for Argo Rollouts using the following command:

```bash hl_lines="1"
kubectl create namespace argo-rollouts
```

Deploy Argo Rollouts using the quick start manifest:

```bash hl_lines="1"
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/download/v1.8.3/install.yaml
```

This will install custom resource definitions as well as the Argo Rollouts controller.  
During this course we use Argo Rollouts in version 1.8.3. We recommend using the same version to ensure consistent results.  

Verify that Argo Rollouts is installed by running the following command:

```bash hl_lines="1"
kubectl get pods -n argo-rollouts
```

### Restrictedn Namespace-Scoped Installation

Limité à un namespace

#### Deploy Argo Rollouts Namespace Scoped

Create a namespace for Argo Rollouts using the following command:

```bash hl_lines="1"
kubectl create namespace argo-rollouts
```

Deploy Argo Rollouts using the quick start manifest:

```bash hl_lines="1"
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/../v1.8.3/download/namespace-install.yaml
```

Admin de cluster requi pour installer les CRDs de rollout séparement

---

```bash hl_lines="1"
kubectl -n argo-rollouts get all
NAME                                 READY   STATUS    RESTARTS   AGE
pod/argo-rollouts-7858b65d86-bcbhq   1/1     Running   0          8m55s

NAME                            TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
service/argo-rollouts-metrics   ClusterIP   10.96.68.1   <none>        8090/TCP   8m55s

NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/argo-rollouts   1/1     1            1           8m55s

NAME                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/argo-rollouts-7858b65d86   1         1         1       8m55s
```

#### Rolling Update

!!! Quote "Contexte"
    Vous devez déployer une nouvelle version de votre application sans pouvoir tolérer la moindre interruption de service. Cependant, lancer simultanément l’ensemble des nouveaux pods n’est pas envisageable, car cela risquerait de surcharger le cluster.

    Il est donc nécessaire d’adopter une stratégie de déploiement progressive permettant de remplacer les anciennes versions par les nouvelles tout en maintenant la disponibilité et la stabilité du système.



<p align="center">
   <img src="../../assets/images/argo/rollouts/rollingUpdate.svg" width="700">
</p>

Cette approche garantit une perturbation minimale et une disponibilité continue de l’application.
En cas de problème avec un nouveau pod, le rollout peut être mis en pause ou annulé.

!!! Note 
    Rolling Update et la stratégie par défaut de l’objet `Deployment` de Kubernetes.  
    Kubernetes utilise les valeurs par défaut (25%)

    Il n'est pas nécéssaire de rajouter une strategy dans l'objet `Deployment` par défault il utiliseras la configuration ci-dessous:
    Tu n’es pas obligé de rajouter ça dans ton Deployment si tu veux juste le comportement par défaut.

    ```yaml
      strategy:
        type: RollingUpdate
        rollingUpdate:
          maxSurge: 1 
          maxUnavailable: 1 
    ```
    
    Voici pourquoi :

    1️⃣ Comportement par défaut

    Pour un Deployment Kubernetes, si tu ne précises pas de strategy :

    strategy:
      type: RollingUpdate


    C’est exactement le rolling update qui va se passer.

    Les valeurs par défaut pour maxSurge et maxUnavailable sont :

    maxSurge: 25%       # jusqu’à 25% de pods en plus
    maxUnavailable: 25% # jusqu’à 25% de pods indisponibles


    Donc pour ton Deployment avec replicas: 3 :

    maxSurge: 25% → arrondi à 1 pod supplémentaire au maximum

    maxUnavailable: 25% → arrondi à 0 ou 1 pod indisponible (Kubernetes arrondit à l’entier supérieur pour maxUnavailable)

    2️⃣ Quand tu voudrais le mettre explicitement

    Tu utiliserais :

    strategy:
      type: RollingUpdate
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 1


    Ici tu contrôles exactement qu’au maximum 1 pod supplémentaire sera créé et qu’au maximum 1 pod peut être indisponible à la fois.

    C’est utile si tu veux contrôler très finement le trafic ou si tu as des pods qui consomment beaucoup de ressources.

    ✅ Conclusion

    Si tu es d’accord avec le comportement par défaut (Kubernetes fait un rolling update avec au maximum 1 pod sur 3 indisponible à la fois), tu n’as pas besoin de l’ajouter.

    Ajouter cette section est juste pour plus de précision et contrôle, pas pour que ça fonctionne.

    Si tu veux, je peux te montrer un petit tableau qui compare le comportement par défaut vs maxSurge/maxUnavailable explicites, ça rend tout super clair pour 3 pods. Veux que je fasse ça ?

    maxSurge et maxUnavailable sont des pourcentage obligatoire ?

    Non, ils ne sont pas obligatoirement des pourcentages, tu peux les spécifier en nombre absolu de pods. Kubernetes accepte les deux formats :

    1️⃣ En pourcentage
    maxSurge: 25%       # 25% des replicas, arrondi à l'entier supérieur
    maxUnavailable: 25% # idem


    Pour ton Deployment de 3 pods :

    25% → 0,75 → arrondi à 1 pod.

    Avantage : ça s’adapte automatiquement si tu changes le nombre de replicas.

    2️⃣ En nombre absolu
    maxSurge: 1
    maxUnavailable: 1


    Ici, Kubernetes prend exactement 1 pod, peu importe le nombre total de replicas.

    Avantage : tu as un contrôle strict, utile pour des déploiements sensibles ou des petits clusters.

    3️⃣ Important

    Tu dois toujours mettre une valeur pour maxSurge et maxUnavailable si tu définis strategy: RollingUpdate.

    Mais si tu ne définis pas strategy du tout, Kubernetes utilise les valeurs par défaut (25%), donc tu n’as rien à mettre.
---


GitOps:
Le dev modifie dans le manifest de deployment la version de 1.0 à 2.0 et le push 
argo prendra en considération la modification et déploieras la nouvelle app selon les indication fournis dans la strategy

```yaml linenums="1"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-app
  namespace: default
  labels:
    app: example-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1 # (1)! 
      maxUnavailable: 1 # (2)! 
  selector:
    matchLabels:
      app: example-app
  template:
    metadata:
      labels:
        app: example-app
    spec:
      containers:
      - name: app
        image: nginx:1.24
        ports:
        - containerPort: 80
          name: http
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 20
```

1.  **maxSurge**  
    Nombre max ***(Pourcentage ou Absolue)*** de pods en plus pendant l'update
2.  **maxUnavailable**  
    Nombre max ***(Pourcentage ou Absolue)*** de pods indisponibles pendant l'update

Pour déclencher un Rolling Update, tu modifies simplement l'image dans le Deployment :

```bash
# Via kubectl
kubectl set image deployment/example-app app=nginx:1.25

# Ou en éditant le manifest et en appliquant
kubectl apply -f deployment.yaml

# Suivre le status du rollout
kubectl rollout status deployment/example-app

# Voir l'historique
kubectl rollout history deployment/example-app

# Rollback si nécessaire
kubectl rollout undo deployment/example-app
```

Les points clés pour un Rolling Update efficace:

  - Strategy configuration : Les paramètres maxSurge et maxUnavailable contrôlent la vitesse et la disponibilité pendant l'update  
  - Readiness/Liveness probes : Essentielles pour que Kubernetes sache quand un pod est prêt à recevoir du trafic  
  - Resources limits : Permet au scheduler de placer correctement les pods pendant l'update

---

## Direct Conversion Method

Migrating Existing Deployments to Rollouts
The similarity of Deployments and Rollouts spec makes it easier to convert from one to the other resource type. Argo Rollouts supports a great way to migrate existing Deployment resources to Rollouts.

By providing a spec.workloadRef instead of spec.template a Rollout can refer to a Deployments template:

apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: nginx-rollout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  workloadRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
[...]

The Rollout will fetch the template information from the Deployment (in our example named nginx-deployment) and start the in the Rollout specified number of pods.

Please note, that lifecycles of Deployment and Rollouts are distinct and managed by their respective controllers. This means that the Kubernetes Deployment controller will not start to manage Pods created by the Rollout. Also, the Rollout will not start to manage pods that are controlled by the Deployment.

This enables a zero-downtime introduction of Argo Rollouts to your existing cluster. It furthermore makes experimentation with multiple deployment scenarios possible.



deployment.yaml
Que fait Kubernetes exactement ?

1. Kubernetes compare la nouvelle spec avec l’ancienne.
2. Il voit que l’image a changé, donc il doit créer de nouveaux pods.
3. Le rolling update va fonctionner comme suit:b

    - Kubernetes va créer un nouveau pod avec l’image green.
    - Quand ce pod est Ready (liveness et readiness passent), il supprime un pod blue existant.
    - Il répète ce processus jusqu’à ce que tous les pods soient remplacés par des pods green.

Donc le cycle est :

- 3 pods blue
- 3 pods blue → 1 pod green
- 2 pods blue → 2 pods green
- 1 pod blue → 3 pods green
- 3 pod green

Détails sur les pods:

- Les pods blue sont supprimés progressivement.
- Les pods green sont créés progressivement.
- Tu n’as jamais de downtime complet si tes pods sont correctement configurés avec readiness probes, car le Service continuera à router le trafic vers les pods Ready.

!!! Quote "Deployment and Argo Rollout Resource in Comparison"

    <div class="grid" markdown>

    !!! Quote ""

        ```yaml linenums="1" title="deployment.yaml" hl_lines="1 2 4"
        apiVersion: {==apps/v1==}
        kind: {==Deployment==}
        metadata:
          name: blue-green-deployment
        spec:
          replicas: 3
          selector:
            matchLabels:
              app: blue-green
          template:
            metadata:
              labels:
                app: blue-green
            spec:
              containers:
                - name: blue-green-container
                  image: siddharth67/app:blue
          strategy:
            {==type: RollingUpdate==}
            rollingUpdate:
              maxSurge: 1 
              maxUnavailable: 1 
        ```

    !!! Quote ""

        ```yaml linenums="1" title="rollout.yaml" hl_lines="1 2 4 18-22"
        apiVersion: {==argoproj.io/v1alpha1==}
        kind: {==Rollout==}
        metadata:
          name: blue-green-rollout
        spec:
          replicas: 3
          selector:
            matchLabels:
              app: blue-green
          template:
            metadata:
              labels:
                app: blue-green
            spec:
              containers:
                - name: blue-green-container
                  image: siddharth67/app:blue
          strategy:
            blueGreen:
              activeService: blue-green-active-svc
              previewService: blue-green-preview-svc
              autoPromotionEnabled: false
        ```

        **Pros**:

          - Rollout adds advanced strategies like blue-green and canary
          - Keeps the same pod template and replicas
          - Traffic can be controlled via active/preview services
          - Auto-promotion can be manual ou automatic

    </div>

---

## workloadRef Method 
https://learn.kodekloud.com/user/courses/certified-argo-project-associate-capa/module/959dfde0-9415-4fc2-bcad-fe9e4bf84cc7/lesson/d363f5a0-40da-4442-9a84-91862257155e

```yaml linenums="1" title="deployment.yaml" hl_lines="1 2 4"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blue-green-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: blue-green
  template:
    metadata:
      labels:
        app: blue-green
    spec:
      containers:
        - name: blue-green-container
          image: siddharth67/app:blue
```

```yaml linenums="1" title="rollout.yaml" hl_lines="1 2 4 18-22"
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: blue-green-rollout
spec:
  workloadRef:
    apiVersion: apps/v1
    kind: Deployment
    name: blue-green-deployment
    scaleDown: never | onsuccess | progressively
  strategy:
    blueGreen:
      activeService: blue-green-active-svc
      previewService: blue-green-preview-svc
      autoPromotionEnabled: false
```

https://argo-rollouts.readthedocs.io/en/stable/features/specification/




---







## Dashboard

L'erreur `ERR_EMPTY_RESPONSE` avec le message `grpc: addrConn.createTransport failed` est un problème connu. Voici comment le résoudre :

## Solutions à essayer dans l'ordre :

### 1. **Vérifier la version d'Argo Rollouts**
D'abord, vérifie ta version :
```bash
kubectl argo rollouts version
```

Si tu es en v1.8.0, c'est probablement la cause - cette version a un bug critique qui casse le dashboard.

### 2. **Utiliser le dashboard déployé dans le cluster** (recommandé)
Au lieu d'utiliser `kubectl argo rollouts dashboard`, déploie le dashboard comme service dans Kubernetes :

```bash
# Si tu utilises Helm
helm upgrade --install argo-rollouts argo/argo-rollouts \
  --namespace argo-rollouts \
  --set dashboard.enabled=true

# Ou avec les manifests officiels
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/dashboard-install.yaml
```

Puis accède-y via port-forward :
```bash
kubectl port-forward -n argo-rollouts svc/argo-rollouts-dashboard 3100:3100
```

### 3. **Créer un Rollout minimal**
Le dashboard a besoin d'au moins un Rollout pour fonctionner correctement :

```yaml
# test-rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: test-rollout
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
```

```bash
kubectl apply -f test-rollout.yaml
```

### 4. **Essayer avec des options différentes**
```bash
# Spécifier le namespace explicitement
kubectl argo rollouts dashboard -n default

# Ou essayer un autre port
kubectl argo rollouts dashboard --port 8080
```

### 5. **Utiliser l'extension ArgoCD** (si tu as ArgoCD)
C'est l'alternative la plus stable actuellement :
```bash
# Installer l'extension dans ArgoCD
kubectl apply -n argocd -f https://github.com/argoproj-labs/rollout-extension/releases/latest/download/install.yaml
```

L'extension ajoute un onglet "Rollouts" directement dans l'interface ArgoCD pour chaque application.

### 6. **Debug avancé**
Si rien ne fonctionne, vérifie les logs du controller :
```bash
# Logs du controller
kubectl logs -n argo-rollouts deployment/argo-rollouts

# Vérifier si les CRDs sont installés
kubectl get crd rollouts.argoproj.io
```

### Solution temporaire si urgent
En attendant de résoudre le problème du dashboard, tu peux utiliser le CLI pour visualiser tes rollouts :
```bash
# Voir l'état d'un rollout
kubectl argo rollouts get rollout <nom-rollout> --watch

# Lister tous les rollouts
kubectl argo rollouts list rollouts -A
```

**Le problème le plus probable** dans ton cas est soit :
1. La v1.8.0 qui est cassée
2. Aucun Rollout n'existe dans le cluster
3. Le dashboard n'est pas déployé comme service dans le cluster

Tu peux me dire quelle version tu utilises et si tu as déjà des Rollouts ? Je pourrai t'aider plus précisément.


---

D'accord ! Je vais te préparer un process complet pour installer ArgoCD via Helm et ensuite ajouter l'extension Rollout selon la documentation du repo.

## 1. Installation d'ArgoCD via Helm

```bash
# Créer le namespace argocd
kubectl create namespace argocd

# Ajouter le repo Helm d'ArgoCD
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# Créer un fichier values pour ArgoCD avec l'extension
cat > argocd-values.yaml <<EOF
server:
  extensions:
    enabled: true
    extensionList:
      - name: rollout-extension
        env:
          - name: EXTENSION_URL
            value: https://github.com/argoproj-labs/rollout-extension/releases/download/v0.3.7/extension.tar
EOF

# Installer ArgoCD avec l'extension
helm install argocd argo/argo-cd \
  --namespace argocd \
  --version 7.7.12 \
  --values argocd-values.yaml
```

## 2. Installation d'Argo Rollouts (nécessaire pour utiliser l'extension)

```bash
# Créer le namespace pour argo-rollouts
kubectl create namespace argo-rollouts

# Installer Argo Rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
```

## 3. Accès à l'interface ArgoCD

```bash
# Récupérer le mot de passe admin initial
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port-forward pour accéder à l'interface (ou utilise ton LoadBalancer avec kind)
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## 4. Test de l'extension avec un Rollout exemple

```bash
# Déployer les exemples du getting started d'Argo Rollouts
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-rollouts/master/docs/getting-started/basic/rollout.yaml
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-rollouts/master/docs/getting-started/basic/service.yaml
```

## Alternative : Si tu préfères configurer directement avec les volumes

Si la méthode avec `server.extensions` ne fonctionne pas, tu peux utiliser cette configuration alternative dans ton `argocd-values.yaml` :

```yaml
server:
  initContainers:
    - name: rollout-extension
      image: quay.io/argoprojlabs/argocd-extension-installer:v0.0.8
      env:
      - name: EXTENSION_URL
        value: https://github.com/argoproj-labs/rollout-extension/releases/download/v0.3.7/extension.tar
      volumeMounts:
        - name: extensions
          mountPath: /tmp/extensions/
      securityContext:
        runAsUser: 1000
        allowPrivilegeEscalation: false
  volumeMounts:
    - name: extensions
      mountPath: /tmp/extensions/
  volumes:
    - name: extensions
      emptyDir: {}
```

Une fois tout installé, tu devrais voir l'onglet Rollout dans l'interface ArgoCD quand tu visualises une ressource de type Rollout !

## Blue/Green - Initial Version

BG est une stratégie de publication d'application qui utilise deux environnement de production identiques

Blue qui est celui en ligne et Green qui est l'options de secours.

### Specification

Deployer une nouvelle version green au cotés de la version blue stable et ensuite rediriger le trafic en direct vers elle seulement après qu'elle ait été entièrement vérifié

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web-api-rollout
spec:
  replicas: 4
  selector:
    matchLabels:
      app: web-api
  spec:
    container:
    - name: web-api-container
      image: my-repo/web-api:v1
      ports:
      - containerPort: 8080
  strategy:
    blueGreen:
      activeService: web-api-active-svc
      previewService: web-api-preview-svc
      previewReplicaCount: 1
      autoPromotionEnables: false
      postPromotionAnalysis:
        templates:
        - templateName: check-error-rate
      scaleDownDelaySeconds: 30
      abortScaleDownDelaySeconds: 10
```

activeService: est le service kubernetes principal pour le traffic de production en direct
previewService: est un service interne séparer qui pointe toujours cers la nouvelle version Green cela fournit un point de terminaison stable pour les test automatisées et le QA manual avant que le trafic utilisateur ne soit affecté

previewReplicaCount: Cela va essentiellement déployer un nombre spécificié plus petit de réplicas pour la version Green durant la phase de prévisualisation afin de conserver les ressources du cluster tout en permettant des tests complets
autoPromotionEnabled: Comme un interrupteur de sécurité critique. Le rollout déploie la version Green, mais ensuite il fait une pause et attend une approbation manuelle en utilisant kubectl ou une UI avant de charger le traffic. Par défaut si vous ne mentionnez pas cela, l'auto-promotion activées est toujorus vraie!

```bash hl_lines="1"
kubectl argo rollouts promote
```

postPromotionAnalysis: configurer pour exécuter une vérification de santé d'analyse automatisé comme interroger Prometheus après que la nouvelle version prenne 100% du traffic en direct pour s'assurer que les SLOs sont toujours respecter.

scaleDownDelaySecondes: C'est comme une fenêtres de rollback rapide. Après avoir redirige le traffic vers la nouvelle version Green, le controleur attend ce nombre de secondes avant de terminer les anciens pods bleus ce qui permet un rollback instantané si un problèmes est détecter.

abortScaleDownDelaySeconds: Pour annuler la reduction d'échèlle. Donc si le rollout est annulé manuellement, le controlleur attend ce nombre de secondes avant de terminer les pods vers défectueux.
Ce bref délai permet au développeurs de collecter des logs ou des dumps de mémoire à des fin de débogage.

### Demo blue green deployment

![](../../../assets/images/argo/rollouts/rollouts.excalidraw#blueGreenSpecification)

### Canary

```
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web-api-rollout
spec:
  replicas: 10
  selector:
    matchLabels:
      app: web-api
  template:
    metadata:
      labels:
        app: web-api
  spec:
    container:
    - name: web-api-container
      image: my-repo/web-api:v1
      ports:
      - containerPort: 8080
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {}
      - setWeight: 25
      - analysis:
          templates:
          - templateName: check-api-error-rate
          args:
          - name: service-name
            value: web-api-canary-svc
      - setWeight: 50
      - pause: { duration: 5m }
      canaryService: web-api-canary-svc # pointe 1.1
      stableService: web-api-stable-svc # pointe 1.0
```

| Feature        | Blue/Green                                                                     | Canary Deployment                                                            |
| -------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| Primary Goal   | Zero Downtime full environment switch, rapid rollback                          | Reduce risk by gradual exposure. Real-user feedback                          |
| Environment    | Two complete, identical environments (Blue & Green)                            | Single environment, with a small subset of new instances                     |
| Traffic Split  | All-or-nothing (or very rapid) switch of all traffic                           | Gradual, weighted routing of portion of traffic                              |
| Rollback       | Instantaneous switch back to the old "Blue" Environment                        | Revert traffic weight to 0% for the new version                              |
| Complexity     | Can be simpler to set up initially, but resource-heavy (two full environments) | More complex to set up due to traffic routing (service mesh)                 |
| Feedback Loop  | Feedback mostly gathered before the full traffic switch in Green               | Continious, real-time feedback from a small user segment during rollout      |
| Risk Reduction | Reduces risk of downtime, high confidence after green validation               | Reduces "blast radius" of issues to a small subset of users                  |
| Resource Usage | Higher ( two full environments running simultaneously)                         | Lower (only a small percentage of new resources initially)                   |
| Best for       | Applications sensitive to downtime, quick "go/no-go" decisions                 | Risk-averse releases, A/B testing, user behavior monitoring, unknown impatcs |

---