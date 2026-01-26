## KIND

!!! Example "KIND"

    !!! Warning 

        `apiServerAddress` much match your **LOCAL_WSL_IP**

    === "MANAGEMENT"

        ```yaml linenums="1" title="management.yaml"
        kind: Cluster
        apiVersion: kind.x-k8s.io/v1alpha4
        name: management
        networking:
          apiServerAddress: 192.168.1.2
          apiServerPort: 6443
        nodes:
        - role: control-plane
        - role: worker
        - role: worker
        - role: worker
        ```

    === "PRODUCTION"

        ```yaml linenums="1" title="production.yaml"
        kind: Cluster
        apiVersion: kind.x-k8s.io/v1alpha4
        name: production
        networking:
          apiServerAddress: 192.168.1.2
          apiServerPort: 6444
        nodes:
        - role: control-plane
        - role: worker
        - role: worker
        - role: worker
        ```

    === "STAGING"

        ```yaml linenums="1" title="staging.yaml"
        kind: Cluster
        apiVersion: kind.x-k8s.io/v1alpha4
        name: staging
        networking:
          apiServerAddress: 192.168.1.2
          apiServerPort: 6445
        nodes:
        - role: control-plane
        - role: worker
        - role: worker
        - role: worker
        ```

    ```bash hl_lines="1-3"
    kind create cluster --config staging.yaml
    kind create cluster --config production.yaml
    kind create cluster --config management.yaml
    ```

!!! Example "STRUCTURE"

    ```shell title="Structure du dépôt"
    argocd/
    ├── README.md
    ├── bootstrap/
    │   ├── argocd-values.yaml             # Valeurs initiales d'Argo CD pour Helm
    │   └── platform-project.yaml          ← AppProject "platform"
    │   └── app-of-apps.yaml               # Root application (gère toutes les autres)
    ├── apps/
    │   ├── reloader-appset.yaml           ← Generator Git Directory
    │   │                                     Lit: charts/reloader/environments/*
    │   │                                     Crée: reloader-prod, reloader-staging
    │   │                                     Project: platform
    │   │
    │   ├── prometheus-appset.yaml         ← Generator Git Directory
    │   │                                     Lit: charts/prometheus/environments/*
    │   │                                     Crée: prometheus-prod, prometheus-staging
    │   │                                     Project: platform
    │   │
    │   └── metrics-server.yaml             ← Generator Git Directory
    │                                         Lit: charts/metrics-server/environments/*
    │                                         Crée: metrics-server-prod, metrics-server-staging
    │                                         Project: platform
    └── charts/
        ├── reloader/
        │   ├── Chart.yaml                 ← Metadata wrapper
        │   ├── values.yaml                ← Config COMMUNE (prod + staging)
        │   ├── .helmignore
        │   ├── environments/
        │   │   ├── prod/
        │   │   │   └── values.yaml       ← Surcharges PROD
        │   │   └── staging/
        │   │       └── values.yaml       ← Surcharges STAGING
        │   ├── charts/
        │   │   └── reloader-2.2.6.tgz    ← Chart Stakater (généré)
        │   └── templates/
        │       ├── service.yaml           ← Ressources additionnelles
        │       ├── servicemonitor.yaml
        │       ├── network-policy.yaml
        │       ├── pod-disruption-budget.yaml
        │       ├── priority-class.yaml
        │       └── _helpers.tpl
        │
        ├── prometheus/
        │   ├── Chart.yaml
        │   ├── values.yaml
        │   ├── environments/
        │   │   ├── prod/
        │   │   │   └── values.yaml
        │   │   └── staging/
        │   │       └── values.yaml
        │   ├── charts/
        │   │   └── prometheus-25.0.0.tgz
        │   └── templates/
        │       └── ...
        │
        └── metrics-server/
            ├── Chart.yaml
            ├── values.yaml
            ├── environments/
            │   ├── prod/
            │   │   └── values.yaml
            │   └── staging/
            │       └── values.yaml
            └── templates/
                └── ...
    ```




    ```bash title="Créer le répertoire du dépôt" hl_lines="1-2"
    mkdir argocd
    cd argocd
    ```

    ```bash title="Initialiser Git" hl_lines="1"
    git init
    ```

    ```bash title="Créer la structure de répertoires" hl_lines="1"
    mkdir -p bootstrap apps manifests/metrics-server
    ```

    ```bash title="Initialiser le dépôt Git" hl_lines="1-2"
    git add .
    git commit -m "Initial structure"
    ```

    ```bash title="Push vers votre hébergement Git (GitHub, GitLab, etc.)" hl_lines="1-2"
    git remote add origin https://github.com/YOUR-USERNAME/argocd-gitops.git
    git push -u origin main
    ```


!!! Example "ARGO CD"

    ```bash hl_lines="1" title="Install Argo CD CLI"
    brew install argocd
    ```
    
    === "KUBECTL"

        ```bash hl_lines="1" title="Ensure Management Cluster is selected"
        kubectl config use-context kind-management
        Switched to context "kind-management".
        ```

    === "KUBECTX"

        ```bash hl_lines="1" title="Ensure Management Cluster is selected"
        kubectx kind-management                                                                                             
        Switched to context "kind-management".
        ```

    ```bash hl_lines="1-5" title="Install Argo CD via Helm"
    helm install argocd argo/argo-cd \
      --namespace argocd \
      --create-namespace \
      --values bootstrap/argocd-values.yaml \
      --wait
    ```

    **AJOUTER LA RECUPERATION DU VALUES.YAML DE BASE**

    ```bash hl_lines="1" title="Switch to argocd Namespace"
    kubens argocd
    Context "kind-management" modified.
    Active namespace is "argocd".
    ```

    ```bash hl_lines="1" title="Connect to Argo CD (core mode)"
    argocd login --core
    Context 'kubernetes' updated
    ```

    ```bash 
    # Production
    kubectl --context kind-production create serviceaccount argocd-manager -n kube-system
    kubectl --context kind-production create clusterrolebinding argocd-manager-role-binding \
      --clusterrole=cluster-admin --serviceaccount=kube-system:argocd-manager

    kubectl --context kind-production apply -f - <<'EOF'
    apiVersion: v1
    kind: Secret
    metadata:
      name: argocd-manager-token
      namespace: kube-system
      annotations:
        kubernetes.io/service-account.name: argocd-manager
    type: kubernetes.io/service-account-token
    EOF

    # Staging
    kubectl --context kind-staging create serviceaccount argocd-manager -n kube-system
    kubectl --context kind-staging create clusterrolebinding argocd-manager-role-binding \
      --clusterrole=cluster-admin --serviceaccount=kube-system:argocd-manager

    kubectl --context kind-staging apply -f - <<'EOF'
    apiVersion: v1
    kind: Secret
    metadata:
      name: argocd-manager-token
      namespace: kube-system
      annotations:
        kubernetes.io/service-account.name: argocd-manager
    type: kubernetes.io/service-account-token
    EOF
    ```

    ```bash
    # Récupérer les tokens
    echo ""
    echo "Récupération des tokens de service account..."
    PROD_TOKEN=$(kubectl --context kind-production get secret argocd-manager-token -n kube-system -o jsonpath='{.data.token}' | base64 -d)
    STAG_TOKEN=$(kubectl --context kind-staging get secret argocd-manager-token -n kube-system -o jsonpath='{.data.token}' | base64 -d)

    if [ -z "$PROD_TOKEN" ] || [ -z "$STAG_TOKEN" ]; then
        echo "❌ ERREUR: Impossible de récupérer les tokens!"
        exit 1
    fi

    echo "✅ Tokens récupérés avec succès"
    ```

    ```bash
    # Créer les secrets de cluster dans ArgoCD avec les noms Docker
    echo ""
    echo "Création des secrets de cluster dans ArgoCD..."

    kubectl --context kind-management apply -f - <<EOF
    apiVersion: v1
    kind: Secret
    metadata:
      name: production-cluster
      namespace: argocd
      labels:
        argocd.argoproj.io/secret-type: cluster
    type: Opaque
    stringData:
      name: production
      server: https://production-control-plane:6443
      config: |
        {
          "bearerToken": "$PROD_TOKEN",
          "tlsClientConfig": {
            "insecure": true
          }
        }
    ---
    apiVersion: v1
    kind: Secret
    metadata:
      name: staging-cluster
      namespace: argocd
      labels:
        argocd.argoproj.io/secret-type: cluster
    type: Opaque
    stringData:
      name: staging
      server: https://staging-control-plane:6443
      config: |
        {
          "bearerToken": "$STAG_TOKEN",
          "tlsClientConfig": {
            "insecure": true
          }
        }
    EOF
    ```




















    
!!! Example "ARGO CD AUTOPILOT"

    ```bash hl_lines="1" title="Install argocd-autopilot CLI"
    brew install argocd-autopilot
    ```

    ```bash hl_lines="1-2" title="Set up Git credentials"
    export GIT_TOKEN=<your-git-token>
    export GIT_REPO=<your-repo-url>
    ```

    ```bash hl_lines="1" title="Bootstrap ArgoCD in HA mode"
    argocd-autopilot repo bootstrap --app https://github.com/argoproj-labs/argocd-autopilot/manifests/ha
    ```
    ??? quote "OUTPUT"

        ```bash hl_lines="1"
        argocd-autopilot repo bootstrap --app https://github.com/argoproj-labs/argocd-autopilot/manifests/ha
        INFO cloning repo: https://gitlab.com/mathod-io/infrastructure/services/argocd.git
        Enumerating objects: 2, done.
        Counting objects: 100% (2/2), done.
        Total 2 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
        INFO using revision: "", installation path: ""
        INFO using context: "kind-management", namespace: "argocd"
        INFO applying bootstrap manifests to cluster...
        namespace/argocd created
        I1214 13:18:48.012999   49532 warnings.go:110] "Warning: unrecognized format \"int64\""
        customresourcedefinition.apiextensions.k8s.io/applications.argoproj.io created
        I1214 13:18:48.249233   49532 warnings.go:110] "Warning: unrecognized format \"int64\""
        customresourcedefinition.apiextensions.k8s.io/applicationsets.argoproj.io created
        I1214 13:18:48.430214   49532 warnings.go:110] "Warning: unrecognized format \"int64\""
        customresourcedefinition.apiextensions.k8s.io/appprojects.argoproj.io created
        serviceaccount/argocd-application-controller created
        serviceaccount/argocd-applicationset-controller created
        serviceaccount/argocd-dex-server created
        serviceaccount/argocd-notifications-controller created
        serviceaccount/argocd-redis-ha created
        serviceaccount/argocd-redis-ha-haproxy created
        serviceaccount/argocd-repo-server created
        serviceaccount/argocd-server created
        role.rbac.authorization.k8s.io/argocd-application-controller created
        role.rbac.authorization.k8s.io/argocd-applicationset-controller created
        role.rbac.authorization.k8s.io/argocd-dex-server created
        role.rbac.authorization.k8s.io/argocd-notifications-controller created
        role.rbac.authorization.k8s.io/argocd-redis-ha created
        role.rbac.authorization.k8s.io/argocd-redis-ha-haproxy created
        role.rbac.authorization.k8s.io/argocd-server created
        clusterrole.rbac.authorization.k8s.io/argocd-application-controller created
        clusterrole.rbac.authorization.k8s.io/argocd-applicationset-controller created
        clusterrole.rbac.authorization.k8s.io/argocd-server created
        rolebinding.rbac.authorization.k8s.io/argocd-application-controller created
        rolebinding.rbac.authorization.k8s.io/argocd-applicationset-controller created
        rolebinding.rbac.authorization.k8s.io/argocd-dex-server created
        rolebinding.rbac.authorization.k8s.io/argocd-notifications-controller created
        rolebinding.rbac.authorization.k8s.io/argocd-redis-ha created
        rolebinding.rbac.authorization.k8s.io/argocd-redis-ha-haproxy created
        rolebinding.rbac.authorization.k8s.io/argocd-server created
        clusterrolebinding.rbac.authorization.k8s.io/argocd-application-controller created
        clusterrolebinding.rbac.authorization.k8s.io/argocd-applicationset-controller created
        clusterrolebinding.rbac.authorization.k8s.io/argocd-server created
        configmap/argocd-cm created
        configmap/argocd-cmd-params-cm created
        configmap/argocd-gpg-keys-cm created
        configmap/argocd-notifications-cm created
        configmap/argocd-rbac-cm created
        configmap/argocd-redis-ha-configmap created
        configmap/argocd-redis-ha-health-configmap created
        configmap/argocd-ssh-known-hosts-cm created
        configmap/argocd-tls-certs-cm created
        secret/argocd-notifications-secret created
        secret/argocd-secret created
        service/argocd-applicationset-controller created
        service/argocd-dex-server created
        service/argocd-metrics created
        service/argocd-notifications-controller-metrics created
        I1214 13:18:49.864417   49532 warnings.go:110] "Warning: spec.SessionAffinity is ignored for headless services"
        service/argocd-redis-ha created
        service/argocd-redis-ha-announce-0 created
        service/argocd-redis-ha-announce-1 created
        service/argocd-redis-ha-announce-2 created
        service/argocd-redis-ha-haproxy created
        service/argocd-repo-server created
        service/argocd-server created
        service/argocd-server-metrics created
        deployment.apps/argocd-applicationset-controller created
        deployment.apps/argocd-dex-server created
        deployment.apps/argocd-notifications-controller created
        deployment.apps/argocd-redis-ha-haproxy created
        deployment.apps/argocd-repo-server created
        deployment.apps/argocd-server created
        statefulset.apps/argocd-application-controller created
        statefulset.apps/argocd-redis-ha-server created
        networkpolicy.networking.k8s.io/argocd-application-controller-network-policy created
        networkpolicy.networking.k8s.io/argocd-applicationset-controller-network-policy created
        networkpolicy.networking.k8s.io/argocd-dex-server-network-policy created
        networkpolicy.networking.k8s.io/argocd-notifications-controller-network-policy created
        networkpolicy.networking.k8s.io/argocd-redis-ha-proxy-network-policy created
        networkpolicy.networking.k8s.io/argocd-redis-ha-server-network-policy created
        networkpolicy.networking.k8s.io/argocd-repo-server-network-policy created
        networkpolicy.networking.k8s.io/argocd-server-network-policy created
        secret/argocd-repo-creds created

        INFO pushing bootstrap manifests to repo
        INFO applying argo-cd bootstrap application
        I1214 13:20:24.317974   49532 warnings.go:110] "Warning: metadata.finalizers: \"resources-finalizer.argocd.argoproj.io\": prefer a domain-qualified finalizer name including a path (/) to avoid accidental conflicts with other finalizer writers"
        application.argoproj.io/autopilot-bootstrap created
        INFO running argocd login to initialize argocd config
        E1214 13:20:24.399201   49532 portforward.go:391] "Unhandled Error" err="error copying from remote stream to local connection: readfrom tcp4 127.0.0.1:43889->127.0.0.1:60354: write tcp4 127.0.0.1:43889->127.0.0.1:60354: write: broken pipe" logger="UnhandledError"
        'admin:login' logged in successfully
        Context 'autopilot' updated

        INFO argocd initialized. password: s3GoqZRYAACFDnzM
        INFO run:

            kubectl port-forward -n argocd svc/argocd-server 8080:80
        ```

    ```bash hl_lines="1" title="Switch to Management Cluster"
    kubectx kind-management
    Switched to context "kind-management".
    ```

    ```bash hl_lines="1" title="Switch to argocd Namespace"
    kubens argocd
    Context "kind-management" modified.
    Active namespace is "argocd".
    ```

    ```bash hl_lines="1" title="Connect to Argo CD (core mode)"
    argocd login --core
    Context 'kubernetes' updated
    ```

    ??? Tip "List available Cluster"
        ```bash hl_lines="1"
        argocd cluster add
        {"level":"error","msg":"Choose a context name from:","time":"2025-12-14T13:33:35+01:00"}
        CURRENT  NAME             CLUSTER          SERVER
        *        kind-management  kind-management  https://192.168.1.2:6443
                  kind-production  kind-production  https://192.168.1.2:6444
                  kind-staging     kind-staging     https://192.168.1.2:6445
        ```

    ```bash hl_lines="1" title="Add Cluster Production"
    argocd cluster add kind-production
    WARNING: This will create a service account `argocd-manager` on the cluster referenced by context `kind-production` with full cluster level privileges. Do you want to continue [y/N]? y
    {"level":"info","msg":"ServiceAccount \"argocd-manager\" created in namespace \"kube-system\"","time":"2025-12-14T13:37:56+01:00"}
    {"level":"info","msg":"ClusterRole \"argocd-manager-role\" created","time":"2025-12-14T13:37:56+01:00"}
    {"level":"info","msg":"ClusterRoleBinding \"argocd-manager-role-binding\" created","time":"2025-12-14T13:37:56+01:00"}
    {"level":"info","msg":"Created bearer token secret \"argocd-manager-long-lived-token\" for ServiceAccount \"argocd-manager\"","time":"2025-12-14T13:37:56+01:00"}
    {"execID":"277f9","level":"error","msg":"`helm version --client --short` failed exit status 1: Error: unknown flag: --client","time":"2025-12-14T13:37:57+01:00"}
    Cluster 'https://192.168.1.2:6444' added
    ```

    ```bash hl_lines="1" title="Add Cluster Staging"
    argocd cluster add kind-staging
    WARNING: This will create a service account `argocd-manager` on the cluster referenced by context `kind-staging` with full cluster level privileges. Do you want to continue [y/N]? y
    {"level":"info","msg":"ServiceAccount \"argocd-manager\" created in namespace \"kube-system\"","time":"2025-12-14T13:38:07+01:00"}
    {"level":"info","msg":"ClusterRole \"argocd-manager-role\" created","time":"2025-12-14T13:38:07+01:00"}
    {"level":"info","msg":"ClusterRoleBinding \"argocd-manager-role-binding\" created","time":"2025-12-14T13:38:07+01:00"}
    {"level":"info","msg":"Created bearer token secret \"argocd-manager-long-lived-token\" for ServiceAccount \"argocd-manager\"","time":"2025-12-14T13:38:07+01:00"}
    {"execID":"c2c02","level":"error","msg":"`helm version --client --short` failed exit status 1: Error: unknown flag: --client","time":"2025-12-14T13:38:07+01:00"}
    Cluster 'https://192.168.1.2:6445' added
    ```


??? TIP "SUPERSCRIPT AUTOPILOT"

    ```bash linenums="1"
    #!/bin/bash
    set -e

    echo "=========================================="
    echo "Setup ArgoCD Autopilot - 3 Clusters KIND"
    echo "=========================================="

    # Configuration Git
    export GIT_TOKEN=
    export GIT_REPO=https://gitlab.com/mathod-io/infrastructure/services/argocd.git

    echo "Git Repository: $GIT_REPO"

    # Créer les fichiers de configuration
    echo ""
    echo "Création des fichiers de configuration KIND..."

    cat > /tmp/management.yaml <<'EOF'
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    name: management
    networking:
      apiServerAddress: 192.168.1.2
      apiServerPort: 6443
    nodes:
    - role: control-plane
    - role: worker
    - role: worker
    - role: worker
    EOF

    cat > /tmp/production.yaml <<'EOF'
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    name: production
    networking:
      apiServerAddress: 192.168.1.2
      apiServerPort: 6444
    nodes:
    - role: control-plane
    - role: worker
    - role: worker
    - role: worker
    EOF

    cat > /tmp/staging.yaml <<'EOF'
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    name: staging
    networking:
      apiServerAddress: 192.168.1.2
      apiServerPort: 6445
    nodes:
    - role: control-plane
    - role: worker
    - role: worker
    - role: worker
    EOF

    # Créer les clusters
    echo ""
    echo "Création des clusters KIND..."
    echo "  - Management (port 6443)..."
    kind create cluster --config /tmp/management.yaml

    echo "  - Production (port 6444)..."
    kind create cluster --config /tmp/production.yaml

    echo "  - Staging (port 6445)..."
    kind create cluster --config /tmp/staging.yaml

    # Vérifier le réseau
    echo ""
    echo "Vérification de la configuration réseau..."
    MGMT_NET=$(docker inspect management-control-plane --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')
    PROD_NET=$(docker inspect production-control-plane --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')
    STAG_NET=$(docker inspect staging-control-plane --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')

    echo "MANAGEMENT sur réseau: $MGMT_NET"
    echo "PRODUCTION sur réseau: $PROD_NET"
    echo "STAGING sur réseau: $STAG_NET"

    if [ "$MGMT_NET" != "$PROD_NET" ] || [ "$MGMT_NET" != "$STAG_NET" ]; then
        echo "⚠️  ATTENTION: Les clusters ne sont pas tous sur le même réseau Docker!"
    fi

    echo ""
    echo "Conteneurs Docker créés:"
    docker ps --filter name=control-plane --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    docker ps --filter name=worker --format "table {{.Names}}\t{{.Status}}"

    # Installer ArgoCD Autopilot
    echo ""
    echo "Installation d'ArgoCD Autopilot en mode HA..."
    kubectl config use-context kind-management

    argocd-autopilot repo bootstrap \
      --app https://github.com/argoproj-labs/argocd-autopilot/manifests/ha \
      --repo $GIT_REPO

    echo ""
    echo "Attente que tous les pods ArgoCD soient prêts..."
    kubectl --context kind-management wait --for=condition=available --timeout=300s -n argocd deployment/argocd-server
    kubectl --context kind-management wait --for=condition=available --timeout=300s -n argocd deployment/argocd-repo-server
    kubectl --context kind-management wait --for=condition=available --timeout=300s -n argocd deployment/argocd-applicationset-controller

    # Switch to argocd namespace
    echo ""
    echo "Configuration du contexte kubectl..."
    kubectl config set-context kind-management --namespace=argocd
    kubectl config use-context kind-management

    # Login to ArgoCD in core mode
    echo ""
    echo "Connexion à ArgoCD (core mode)..."
    argocd login --core

    # Créer manuellement les service accounts sur les autres clusters
    echo ""
    echo "Création des service accounts sur production et staging..."

    # Production
    kubectl --context kind-production create serviceaccount argocd-manager -n kube-system
    kubectl --context kind-production create clusterrolebinding argocd-manager-role-binding \
      --clusterrole=cluster-admin --serviceaccount=kube-system:argocd-manager

    kubectl --context kind-production apply -f - <<'EOF'
    apiVersion: v1
    kind: Secret
    metadata:
      name: argocd-manager-token
      namespace: kube-system
      annotations:
        kubernetes.io/service-account.name: argocd-manager
    type: kubernetes.io/service-account-token
    EOF

    # Staging
    kubectl --context kind-staging create serviceaccount argocd-manager -n kube-system
    kubectl --context kind-staging create clusterrolebinding argocd-manager-role-binding \
      --clusterrole=cluster-admin --serviceaccount=kube-system:argocd-manager

    kubectl --context kind-staging apply -f - <<'EOF'
    apiVersion: v1
    kind: Secret
    metadata:
      name: argocd-manager-token
      namespace: kube-system
      annotations:
        kubernetes.io/service-account.name: argocd-manager
    type: kubernetes.io/service-account-token
    EOF

    echo "Attente de la création des tokens..."
    sleep 10

    # Récupérer les tokens
    echo ""
    echo "Récupération des tokens de service account..."
    PROD_TOKEN=$(kubectl --context kind-production get secret argocd-manager-token -n kube-system -o jsonpath='{.data.token}' | base64 -d)
    STAG_TOKEN=$(kubectl --context kind-staging get secret argocd-manager-token -n kube-system -o jsonpath='{.data.token}' | base64 -d)

    if [ -z "$PROD_TOKEN" ] || [ -z "$STAG_TOKEN" ]; then
        echo "❌ ERREUR: Impossible de récupérer les tokens!"
        exit 1
    fi

    echo "✅ Tokens récupérés avec succès"

    # Créer les secrets de cluster dans ArgoCD avec les noms Docker
    echo ""
    echo "Création des secrets de cluster dans ArgoCD..."

    kubectl --context kind-management apply -f - <<EOF
    apiVersion: v1
    kind: Secret
    metadata:
      name: production-cluster
      namespace: argocd
      labels:
        argocd.argoproj.io/secret-type: cluster
    type: Opaque
    stringData:
      name: production
      server: https://production-control-plane:6443
      config: |
        {
          "bearerToken": "$PROD_TOKEN",
          "tlsClientConfig": {
            "insecure": true
          }
        }
    ---
    apiVersion: v1
    kind: Secret
    metadata:
      name: staging-cluster
      namespace: argocd
      labels:
        argocd.argoproj.io/secret-type: cluster
    type: Opaque
    stringData:
      name: staging
      server: https://staging-control-plane:6443
      config: |
        {
          "bearerToken": "$STAG_TOKEN",
          "tlsClientConfig": {
            "insecure": true
          }
        }
    EOF

    # Renommer le cluster in-cluster en management
    echo ""
    echo "Renommage du cluster in-cluster -> management..."
    INCLUSTER_SECRET=$(kubectl --context kind-management get secret -n argocd -l argocd.argoproj.io/secret-type=cluster -o name | grep -v production | grep -v staging | head -1)

    if [ -n "$INCLUSTER_SECRET" ]; then
        kubectl --context kind-management patch $INCLUSTER_SECRET -n argocd \
          --type merge \
          -p '{"stringData":{"name":"management"}}'
    fi

    # Redémarrer ArgoCD pour prendre en compte les nouveaux clusters
    echo ""
    echo "Redémarrage d'ArgoCD..."
    kubectl --context kind-management rollout restart -n argocd statefulset/argocd-application-controller
    kubectl --context kind-management rollout restart -n argocd deployment/argocd-server
    kubectl --context kind-management rollout status -n argocd statefulset/argocd-application-controller --timeout=180s
    kubectl --context kind-management rollout status -n argocd deployment/argocd-server --timeout=180s

    # Récupérer le mot de passe ArgoCD
    echo ""
    echo "Récupération du mot de passe ArgoCD..."
    sleep 5
    ARGOCD_PASSWORD=$(kubectl --context kind-management get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d 2>/dev/null || echo "Voir logs autopilot bootstrap")

    # Créer les projets ArgoCD Autopilot
    echo ""
    echo "Création des projets ArgoCD Autopilot..."

    argocd-autopilot project create management \
      --dest-server https://kubernetes.default.svc 2>/dev/null || echo "  ℹ️  Projet management existe déjà"

    argocd-autopilot project create production \
      --dest-server https://production-control-plane:6443 2>/dev/null || echo "  ℹ️  Projet production existe déjà"

    argocd-autopilot project create staging \
      --dest-server https://staging-control-plane:6443 2>/dev/null || echo "  ℹ️  Projet staging existe déjà"

    # Attendre que ArgoCD reconnaisse les clusters
    echo ""
    echo "Attente de la synchronisation ArgoCD..."
    sleep 15

    echo ""
    echo "=========================================="
    echo "✅ Installation terminée avec succès!"
    echo "=========================================="
    echo ""
    echo "📦 ArgoCD Autopilot (HA mode)"
    echo "   Git Repository: $GIT_REPO"
    if [ "$ARGOCD_PASSWORD" != "Voir logs autopilot bootstrap" ]; then
        echo "   Password: $ARGOCD_PASSWORD"
    fi
    echo ""
    echo "🎯 Clusters KIND créés:"
    echo "   - MANAGEMENT: 1 control-plane + 3 workers (192.168.1.2:6443)"
    echo "   - PRODUCTION: 1 control-plane + 3 workers (192.168.1.2:6444)"
    echo "   - STAGING:    1 control-plane + 3 workers (192.168.1.2:6445)"
    echo ""
    echo "📁 Projets ArgoCD Autopilot:"
    echo "   - management  → https://kubernetes.default.svc"
    echo "   - production  → https://production-control-plane:6443"
    echo "   - staging     → https://staging-control-plane:6443"
    echo ""
    echo "🔧 Commandes utiles:"
    echo "   # Port-forward ArgoCD UI"
    echo "   kubectl port-forward -n argocd svc/argocd-server 8080:80"
    echo ""
    echo "   # Vérifier les clusters"
    echo "   argocd cluster list"
    echo ""
    echo "   # Vérifier les projets"
    echo "   argocd proj list"
    echo ""
    echo "   # Créer une app dans un projet"
    echo "   argocd-autopilot app create <app-name> --app <manifest-url> --project production"
    echo ""
    echo "=========================================="
    echo ""

    # Afficher l'état final
    echo "📊 État des clusters ArgoCD:"
    argocd cluster list 2>/dev/null || echo "Exécutez: argocd login --core"

    echo ""
    echo "📋 Projets ArgoCD:"
    argocd proj list 2>/dev/null || true

    echo ""
    echo "🎮 Nodes Management:"
    kubectl --context kind-management get nodes

    echo ""
    echo "✨ Setup terminé! Bon développement! 🚀"
    ```