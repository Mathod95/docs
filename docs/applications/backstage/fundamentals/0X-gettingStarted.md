# Getting Started

> Cette page couvre la création d'une image Backstage custom avec les plugins ArgoCD, Kubernetes et Prometheus, son build, sa publication sur un registry, et son déploiement via le Helm chart.

## Pourquoi une image custom ?

L'image vanilla `ghcr.io/backstage/backstage:latest` est uniquement destinée à la démo. Pour installer des plugins supplémentaires, il est obligatoire de créer sa propre image custom à partir du code source Backstage.

> 📖 Référence : [backstage/charts — README officiel](https://github.com/backstage/charts#:~:text=This%20Helm%20chart,the%20Backstage%20documentation){target=_blank}

---

## Prérequis

| Outil    | Version minimale |
|----------|------------------|
| `node`   | >= 20 (LTS)      |
| `yarn`   | >= 4             |
| `docker` | >= 24            |
| `git`    | any              |

> 📖 Référence : [Backstage — Prerequisites](https://backstage.io/docs/getting-started/#:~:text=Prerequisites%E2%80%8B,or%20remote%20system.){target=_blank}

---

## 1. Créer l'app Backstage

> 📖 Référence : [Backstage — Create an App](https://backstage.io/docs/getting-started/create-an-app/)

La méthode officielle recommandée est de créer son app Backstage avec `create-app`, puis de la builder en dehors de Docker (host build) pour bénéficier d'un cache plus efficace et d'une build plus rapide.

```bash
npx @backstage/create-app@latest
# Entrer le nom de l'app, ex: my-backstage
cd my-backstage
```

Structure générée :

```
my-backstage/
├── app-config.yaml              # Config principale
├── app-config.production.yaml   # Config de production (à créer)
├── packages/
│   ├── app/                     # Frontend React
│   │   └── src/
│   │       └── components/
│   │           └── catalog/
│   │               └── EntityPage.tsx  # UI des entités du catalog
│   └── backend/                 # Backend Node.js
│       ├── Dockerfile           # Généré automatiquement ✅
│       └── src/
│           └── index.ts         # Point d'entrée backend
└── .dockerignore
```

> **Note :** Quand tu scaffoldes une nouvelle app avec `create-app`, un `Dockerfile` production-ready est automatiquement généré dans `packages/backend/Dockerfile`. Tu peux t'appuyer dessus directement sans repartir de zéro.

---

## 2. Installer les plugins

### Plugin Kubernetes

> 📖 Référence : [Backstage — Kubernetes plugin installation](https://backstage.io/docs/features/kubernetes/installation/)

```bash
# Frontend
yarn --cwd packages/app add @backstage/plugin-kubernetes

# Backend
yarn --cwd packages/backend add @backstage/plugin-kubernetes-backend
```

### Plugin ArgoCD

> 📖 Référence : [RoadieHQ — ArgoCD plugin frontend (npm)](https://www.npmjs.com/package/@roadiehq/backstage-plugin-argo-cd)  
> 📖 Référence : [RoadieHQ — ArgoCD plugin backend (npm)](https://www.npmjs.com/package/@roadiehq/backstage-plugin-argo-cd-backend)

```bash
# Frontend
yarn --cwd packages/app add @roadiehq/backstage-plugin-argo-cd

# Backend
yarn --cwd packages/backend add @roadiehq/backstage-plugin-argo-cd-backend
```

### Plugin Prometheus

> 📖 Référence : [RoadieHQ — Prometheus plugin (npm)](https://www.npmjs.com/package/@roadiehq/backstage-plugin-prometheus)

```bash
# Frontend uniquement (lit les métriques via le proxy Backstage)
yarn --cwd packages/app add @roadiehq/backstage-plugin-prometheus
```

---

## 3. Configurer le plugin Kubernetes

> 📖 Référence : [Backstage — Kubernetes plugin installation](https://backstage.io/docs/features/kubernetes/installation/)  
> 📖 Référence : [Backstage — Kubernetes plugin configuration](https://backstage.io/docs/features/kubernetes/configuration/)

### Frontend — `packages/app/src/components/catalog/EntityPage.tsx`

```tsx
// Ajouter l'import
import { EntityKubernetesContent } from '@backstage/plugin-kubernetes';

// Ajouter l'onglet Kubernetes dans serviceEntityPage
const serviceEntityPage = (
  <EntityLayout>
    {/* autres onglets... */}
    <EntityLayout.Route path="/kubernetes" title="Kubernetes">
      <EntityKubernetesContent refreshIntervalMs={30000} />
    </EntityLayout.Route>
  </EntityLayout>
);
```

### Backend — `packages/backend/src/index.ts`

```ts
import { createBackend } from '@backstage/backend-defaults';

const backend = createBackend();
// ... autres plugins
backend.add(import('@backstage/plugin-kubernetes-backend'));
backend.start();
```

### Configuration — `app-config.yaml`

```yaml
kubernetes:
  serviceLocatorMethod:
    type: multiTenant
  clusterLocatorMethods:
    - type: config
      clusters:
        - name: backstage-kind
          url: https://kubernetes.default.svc
          authProvider: serviceAccount
          skipTLSVerify: true
```

### ServiceAccount pour Backstage

```bash
kubectl create serviceaccount backstage -n backstage
kubectl create clusterrolebinding backstage-cluster-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=backstage:backstage
```

---

## 4. Configurer le plugin ArgoCD

> 📖 Référence : [RoadieHQ — ArgoCD plugin README (GitHub)](https://github.com/RoadieHQ/roadie-backstage-plugins/blob/main/plugins/frontend/backstage-plugin-argo-cd/README.md)  
> 📖 Référence : [RoadieHQ — ArgoCD backend plugin README (GitHub)](https://github.com/RoadieHQ/roadie-backstage-plugins/tree/main/plugins/backend/backstage-plugin-argo-cd-backend)  
> 📖 Référence : [Roadie — ArgoCD plugin guide](https://roadie.io/backstage/plugins/argo-cd/)

### Frontend — `packages/app/src/components/catalog/EntityPage.tsx`

```tsx
import {
  EntityArgoCDOverviewCard,
  EntityArgoCDHistoryCard,
  isArgocdAvailable,
} from '@roadiehq/backstage-plugin-argo-cd';

const overviewContent = (
  <Grid container spacing={3} alignItems="stretch">
    {/* ... */}
    <EntitySwitch>
      <EntitySwitch.Case if={e => Boolean(isArgocdAvailable(e))}>
        <Grid item sm={4}>
          <EntityArgoCDOverviewCard />
        </Grid>
        <Grid item sm={6}>
          <EntityArgoCDHistoryCard />
        </Grid>
      </EntitySwitch.Case>
    </EntitySwitch>
  </Grid>
);
```

### Backend — `packages/backend/src/index.ts`

```ts
import { createBackend } from '@backstage/backend-defaults';

const backend = createBackend();
// ... autres plugins
backend.add(import('@roadiehq/backstage-plugin-argo-cd-backend'));
backend.start();
```

### Configuration — `app-config.yaml`

```yaml
argocd:
  appLocatorMethods:
    - type: config
      instances:
        - name: backstage-kind
          url: http://argocd-server.argocd.svc.cluster.local
          token: ${ARGOCD_AUTH_TOKEN}
```

### Créer le token ArgoCD pour Backstage

```bash
# Créer un compte dédié Backstage dans ArgoCD
kubectl patch configmap argocd-cm -n argocd --patch '
data:
  accounts.backstage: apiKey,login
'

# Créer la policy RBAC
kubectl patch configmap argocd-rbac-cm -n argocd --patch '
data:
  policy.csv: |
    p, backstage, applications, get, */*, allow
    p, backstage, clusters, get, *, allow
    p, backstage, repositories, get, *, allow
'

# Générer le token
argocd account generate-token --account backstage
# → Copier le token généré
```

---

## 5. Configurer le plugin Prometheus

> 📖 Référence : [RoadieHQ — Prometheus plugin README (GitHub)](https://github.com/RoadieHQ/roadie-backstage-plugins/blob/main/plugins/frontend/backstage-plugin-prometheus/README.md)  
> 📖 Référence : [Roadie — Prometheus plugin guide](https://roadie.io/backstage/plugins/prometheus/)

### Frontend — `packages/app/src/components/catalog/EntityPage.tsx`

```tsx
import {
  EntityPrometheusContent,
  EntityPrometheusAlertCard,
  EntityPrometheusGraphCard,
  isPrometheusAvailable,
} from '@roadiehq/backstage-plugin-prometheus';

const serviceEntityPage = (
  <EntityLayout>
    {/* autres onglets... */}
    <EntityLayout.Route path="/prometheus" title="Prometheus">
      <EntityPrometheusContent />
    </EntityLayout.Route>
  </EntityLayout>
);

// Dans overviewContent
const overviewContent = (
  <Grid container spacing={3} alignItems="stretch">
    {/* ... */}
    <EntitySwitch>
      <EntitySwitch.Case if={isPrometheusAvailable}>
        <Grid item md={8}>
          <EntityPrometheusAlertCard />
        </Grid>
        <Grid item md={6}>
          <EntityPrometheusGraphCard />
        </Grid>
      </EntitySwitch.Case>
    </EntitySwitch>
  </Grid>
);
```

### Configuration — `app-config.yaml`

```yaml
proxy:
  '/prometheus/api':
    target: http://prometheus-server.monitoring.svc.cluster.local:9090/api/v1/
    changeOrigin: true

prometheus:
  proxyPath: /prometheus/api
  uiUrl: http://prometheus-server.monitoring.svc.cluster.local:9090
```

---

## Étape 6 — app-config.production.yaml

> 📖 Référence : [Backstage — Building a Docker image](https://backstage.io/docs/deployment/docker/)  
> 📖 Référence : [Backstage — Deploying with Kubernetes](https://backstage.io/docs/deployment/k8s/)

Créer un fichier `app-config.production.yaml` à la racine pour les surcharges de production :

```yaml
# app-config.production.yaml
app:
  baseUrl: http://localhost:7007

backend:
  baseUrl: http://localhost:7007
  database:
    client: pg
    connection:
      host: ${POSTGRES_HOST}
      port: ${POSTGRES_PORT}
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}

auth:
  environment: production
  providers:
    github:
      production:
        clientId: ${AUTH_GITHUB_CLIENT_ID}
        clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}
        signIn:
          resolvers:
            - resolver: usernameMatchingUserEntityName
    gitlab:
      production:
        clientId: ${AUTH_GITLAB_CLIENT_ID}
        clientSecret: ${AUTH_GITLAB_CLIENT_SECRET}
        signIn:
          resolvers:
            - resolver: usernameMatchingUserEntityName

argocd:
  appLocatorMethods:
    - type: config
      instances:
        - name: backstage-kind
          url: http://argocd-server.argocd.svc.cluster.local
          token: ${ARGOCD_AUTH_TOKEN}

proxy:
  '/prometheus/api':
    target: http://prometheus-server.monitoring.svc.cluster.local:9090/api/v1/
    changeOrigin: true

kubernetes:
  serviceLocatorMethod:
    type: multiTenant
  clusterLocatorMethods:
    - type: config
      clusters:
        - name: backstage-kind
          url: https://kubernetes.default.svc
          authProvider: serviceAccount
          skipTLSVerify: true
```

---

## Étape 7 — Builder l'image Docker

> 📖 Référence : [Backstage — Building a Docker image (host build)](https://backstage.io/docs/deployment/docker/)  
> 📖 Référence : [Backstage — Build system](https://backstage.io/docs/tooling/cli/build-system/)

La méthode recommandée est le **host build** : les étapes de build s'exécutent sur l'hôte, puis Docker ne fait que copier les artefacts dans l'image finale. C'est plus rapide et le cache est plus efficace.

```bash
# 1. Installer les dépendances
yarn install --immutable

# 2. Générer les types TypeScript
yarn tsc

# 3. Builder le backend (bundlé dans packages/backend/dist/)
yarn build:backend

# 4. Builder l'image Docker
# Le Dockerfile est dans packages/backend/Dockerfile
# mais le contexte doit être la racine du repo
docker build \
  --file packages/backend/Dockerfile \
  --tag ghcr.io/<ton-org>/backstage:1.0.0 \
  .
```

> **Important :** Le build doit toujours être lancé depuis la **racine** du repo, pas depuis `packages/backend/`.

### .dockerignore recommandé

```
.git
.yarn/cache
.yarn/install-state.gz
node_modules
packages/*/src
packages/*/node_modules
plugins
*.local.yaml
```

---

## Étape 8 — Pousser sur le registry

### GitHub Container Registry (GHCR)

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u <ton-username> --password-stdin

# Push
docker push ghcr.io/<ton-org>/backstage:1.0.0

# Tag latest
docker tag ghcr.io/<ton-org>/backstage:1.0.0 ghcr.io/<ton-org>/backstage:latest
docker push ghcr.io/<ton-org>/backstage:latest
```

### GitLab Container Registry

```bash
# Login
docker login registry.gitlab.com -u <ton-username> -p $GITLAB_TOKEN

# Push
docker tag ghcr.io/<ton-org>/backstage:1.0.0 \
  registry.gitlab.com/<ton-namespace>/backstage:1.0.0
docker push registry.gitlab.com/<ton-namespace>/backstage:1.0.0
```

---

## Étape 9 — Déployer via Helm

> 📖 Référence : [backstage/charts — Helm chart officiel](https://github.com/backstage/charts)

### Mettre à jour values.yaml

```yaml
# values.yaml
ingress:
  enabled: false

backstage:
  image:
    registry: ghcr.io
    repository: <ton-org>/backstage   # ← Ton image custom
    tag: "1.0.0"                       # ← Tag précis, jamais latest en prod

  extraEnvVars:
    - name: NODE_ENV
      value: production
    - name: APP_CONFIG_app_baseUrl
      value: "http://localhost:7007"
    - name: APP_CONFIG_backend_baseUrl
      value: "http://localhost:7007"

  extraEnvVarsSecrets:
    - backstage-secrets

  appConfig:
    signInPage: github
    auth:
      environment: production
      providers:
        github:
          production:
            clientId: ${AUTH_GITHUB_CLIENT_ID}
            clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}
            signIn:
              resolvers:
                - resolver: usernameMatchingUserEntityName
        gitlab:
          production:
            clientId: ${AUTH_GITLAB_CLIENT_ID}
            clientSecret: ${AUTH_GITLAB_CLIENT_SECRET}
            signIn:
              resolvers:
                - resolver: usernameMatchingUserEntityName
    argocd:
      appLocatorMethods:
        - type: config
          instances:
            - name: backstage-kind
              url: http://argocd-server.argocd.svc.cluster.local
              token: ${ARGOCD_AUTH_TOKEN}
    proxy:
      '/prometheus/api':
        target: http://prometheus-server.monitoring.svc.cluster.local:9090/api/v1/
        changeOrigin: true
    kubernetes:
      serviceLocatorMethod:
        type: multiTenant
      clusterLocatorMethods:
        - type: config
          clusters:
            - name: backstage-kind
              url: https://kubernetes.default.svc
              authProvider: serviceAccount
              skipTLSVerify: true

postgresql:
  enabled: true
  auth:
    username: bn_backstage
    database: backstage_plugin_catalog
    password: ""
    existingSecret: ""
```

### Mettre à jour le Secret Kubernetes

```bash
kubectl create secret generic backstage-secrets \
  --namespace backstage \
  --from-literal=BACKEND_SECRET="$(openssl rand -base64 32)" \
  --from-literal=AUTH_GITHUB_CLIENT_ID="<github-client-id>" \
  --from-literal=AUTH_GITHUB_CLIENT_SECRET="<github-client-secret>" \
  --from-literal=AUTH_GITLAB_CLIENT_ID="<gitlab-application-id>" \
  --from-literal=AUTH_GITLAB_CLIENT_SECRET="<gitlab-secret>" \
  --from-literal=ARGOCD_AUTH_TOKEN="<argocd-token>" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Helm upgrade

```bash
helm upgrade backstage backstage/backstage \
  --namespace backstage \
  --values values.yaml \
  --wait
```

---

## Étape 10 — Cycle de vie & upgrades

> 📖 Référence : [Backstage — Deploying with Kubernetes](https://backstage.io/docs/deployment/k8s/)

### Ajouter un nouveau plugin

```bash
# 1. Installer le package
yarn --cwd packages/app add @nouveau/plugin

# 2. Modifier EntityPage.tsx ou index.ts

# 3. Rebuilder
yarn install --immutable && yarn tsc && yarn build:backend

# 4. Rebuilder l'image avec un nouveau tag
docker build \
  --file packages/backend/Dockerfile \
  --tag ghcr.io/<ton-org>/backstage:1.1.0 \
  .

# 5. Pousser
docker push ghcr.io/<ton-org>/backstage:1.1.0

# 6. Mettre à jour le tag dans values.yaml et upgrader
helm upgrade backstage backstage/backstage \
  --namespace backstage \
  --values values.yaml \
  --set backstage.image.tag=1.1.0 \
  --wait
```

### Rollback rapide

```bash
# Lister l'historique Helm
helm history backstage -n backstage

# Rollback à la révision précédente
helm rollback backstage -n backstage

# PostgreSQL n'est pas affecté — les données sont conservées
```

### Workflow CI/CD recommandé (GitLab CI)

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

build-image:
  stage: build
  script:
    - yarn install --immutable
    - yarn tsc
    - yarn build:backend
    - docker build -f packages/backend/Dockerfile -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

deploy:
  stage: deploy
  script:
    - helm upgrade backstage backstage/backstage
        --namespace backstage
        --values values.yaml
        --set backstage.image.tag=$CI_COMMIT_SHORT_SHA
        --wait
  environment: production
```

---

## Annotations catalog-info.yaml

> 📖 Référence : [Backstage — Kubernetes annotations](https://backstage.io/docs/features/kubernetes/configuration/)  
> 📖 Référence : [RoadieHQ — ArgoCD annotations](https://github.com/RoadieHQ/roadie-backstage-plugins/blob/main/plugins/frontend/backstage-plugin-argo-cd/README.md)  
> 📖 Référence : [RoadieHQ — Prometheus annotations](https://github.com/RoadieHQ/roadie-backstage-plugins/blob/main/plugins/frontend/backstage-plugin-prometheus/README.md)

Pour qu'un composant affiche les données des plugins, ajouter ces annotations dans son `catalog-info.yaml` :

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: mon-service
  annotations:
    # Plugin Kubernetes
    backstage.io/kubernetes-id: mon-service
    backstage.io/kubernetes-namespace: default

    # Plugin ArgoCD
    argocd/app-name: mon-service

    # Plugin Prometheus
    prometheus.io/rule: |
      container_cpu_usage_seconds_total{namespace="default",pod=~"mon-service-.*"},
      container_memory_usage_bytes{namespace="default",pod=~"mon-service-.*"}
spec:
  type: service
  lifecycle: production
  owner: platform-team
```

---

## Ressources

| Sujet | Lien |
|-------|------|
| Créer une app Backstage | [backstage.io/docs/getting-started/create-an-app](https://backstage.io/docs/getting-started/create-an-app/) |
| Build Docker image (officiel) | [backstage.io/docs/deployment/docker](https://backstage.io/docs/deployment/docker/) |
| Déploiement Kubernetes (officiel) | [backstage.io/docs/deployment/k8s](https://backstage.io/docs/deployment/k8s/) |
| Kubernetes plugin — installation | [backstage.io/docs/features/kubernetes/installation](https://backstage.io/docs/features/kubernetes/installation/) |
| Kubernetes plugin — configuration | [backstage.io/docs/features/kubernetes/configuration](https://backstage.io/docs/features/kubernetes/configuration/) |
| ArgoCD plugin frontend (npm) | [npmjs.com/@roadiehq/backstage-plugin-argo-cd](https://www.npmjs.com/package/@roadiehq/backstage-plugin-argo-cd) |
| ArgoCD plugin backend (npm) | [npmjs.com/@roadiehq/backstage-plugin-argo-cd-backend](https://www.npmjs.com/package/@roadiehq/backstage-plugin-argo-cd-backend) |
| ArgoCD plugin README (GitHub) | [github.com/RoadieHQ/roadie-backstage-plugins — argo-cd](https://github.com/RoadieHQ/roadie-backstage-plugins/blob/main/plugins/frontend/backstage-plugin-argo-cd/README.md) |
| Prometheus plugin (npm) | [npmjs.com/@roadiehq/backstage-plugin-prometheus](https://www.npmjs.com/package/@roadiehq/backstage-plugin-prometheus) |
| Prometheus plugin README (GitHub) | [github.com/RoadieHQ/roadie-backstage-plugins — prometheus](https://github.com/RoadieHQ/roadie-backstage-plugins/blob/main/plugins/frontend/backstage-plugin-prometheus/README.md) |
| Helm chart officiel | [github.com/backstage/charts](https://github.com/backstage/charts) |
| Backstage build system | [backstage.io/docs/tooling/cli/build-system](https://backstage.io/docs/tooling/cli/build-system/) |