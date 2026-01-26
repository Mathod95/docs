---
title: Reloader
date: 2025-12-13
draft: true
categories:
  - Reloader
tags:
  - Reloader
  - Lab
todo: utiliser podMonitor
---

## Introduction

Versions déployées lors de la rédaction de cet article:

- Chart Helm : 2.2.6
- Application Kyverno : v1.4.11
- Repository : https://github.com/stakater/Reloader

<!-- more -->

```bash title="Structure de base du wrapper"
reloader/
├── Chart.yaml
├── values.yaml
├── README.md
└── templates/
    ├── _helpers.tpl
    ├── service.yaml
    ├── servicemonitor.yaml
    ├── network-policy.yaml
    ├── pod-disruption-budget.yaml
    └── priority-class.yaml
```

```shell hl_lines="1" title="Ajouter le repository Helm"
helm repo add stakater https://stakater.github.io/stakater-charts
"stakater" has been added to your repositories
```

```bash hl_lines="1" title="Mettre à jour les repositories"
helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "stakater" chart repository
Update Complete. ⎈Happy Helming!⎈
```

!!! Tip "VERSION"

    ```bash hl_lines="1" title="Voir la dernière version"
    helm search repo stakater/reloader
    NAME                    CHART VERSION   APP VERSION     DESCRIPTION
    stakater/reloader       2.2.6           v1.4.11         Reloader chart that runs on kubernetes
    ```

    ??? tip "USEFUL COMMANDS"

        ```bash hl_lines="1" title="Lister toutes les versions disponibles"
        helm search repo stakater/reloader --versions
        NAME                    CHART VERSION   APP VERSION     DESCRIPTION
        stakater/reloader       2.2.6           v1.4.11         Reloader chart that runs on kubernetes
        stakater/reloader       2.2.5           v1.4.10         Reloader chart that runs on kubernetes
        stakater/reloader       2.2.4           v1.4.9          Reloader chart that runs on kubernetes
        ... Omis par souci de brièveté
        ```

!!! info "CHART"

    ```bash hl_lines="1" title="Voir la Chart"
    helm show chart stakater/reloader
    ```

    ??? quote "OUTPUT"

        ```yaml linenums="1" title="Chart.yaml"
        apiVersion: v1
        appVersion: v1.4.11
        description: Reloader chart that runs on kubernetes
        home: https://github.com/stakater/Reloader
        icon: https://raw.githubusercontent.com/stakater/Reloader/master/assets/web/reloader-round-100px.png
        keywords:
        - Reloader
        - kubernetes
        maintainers:
        - email: hello@stakater.com
          name: Stakater
        - email: rasheed@stakater.com
          name: rasheedamir
        - email: faizan@stakater.com
          name: faizanahmad055
        name: reloader
        sources:
        - https://github.com/stakater/Reloader
        version: 2.2.6
        ```

!!! info "VALUES"

    ```bash hl_lines="1" title="Voir les values par défaut"
    helm show values stakater/Reloader
    ```

    ??? tip "USEFUL COMMANDS"

        ```bash hl_lines="1" title="Lister toutes les versions disponibles"
        helm show values stakater/Reloader > values.yaml
        ```
    
    !!! Warning 

        Un `values.yaml` vide applique automatiquement les valeurs par défaut.

        **Surcharge des valeurs Kyverno**

        Si tu veux personnaliser des valeurs Kyverno, tu peux le faire dans ton values.yaml

        ```yaml linenums="1" title="values.yaml"
        kyverno:
          replicaCount: 2
          serviceAccount:
            create: false
        ```

        Helm va fusionner tes valeurs avec les valeurs par défaut de Kyverno.  
        Tout ce qui n’est pas défini reste par défaut








































---

3️⃣ Surcharge des valeurs Kyverno

Si tu veux personnaliser des valeurs Kyverno, tu peux le faire dans ton values.yaml wrapper :

kyverno:
  replicaCount: 2
  serviceAccount:
    create: false


Helm va fusionner tes valeurs avec les valeurs par défaut de Kyverno

Tout ce qui n’est pas défini reste par défaut

4️⃣ Points importants à savoir

Les valeurs par défaut sont toujours prises depuis le chart de dépendance.

Si tu mets ton fichier values.yaml vide, aucune valeur n’est perdue, le chart Kyverno fonctionne normalement.

Tu peux vérifier les valeurs appliquées avant l’installation :

helm template my-kyverno ./kyverno-wrapper


Ça te montre exactement le YAML final que Helm va déployer, avec valeurs par défaut + tes surcharges éventuelles.

---



## Chart

```yaml linenums="1" title="Chart.yaml"
apiVersion: v2 #(1)!
name: reloader-wrapper #(2)!
description: Enterprise wrapper for Stakater Reloader with monitoring and security #(3)!
type: application #(4)!
version: 1.0.0 #(5)!
appVersion: "v1.4.11" #(6)! 
maintainers: #(7)!
  - name: Platform Team
    email: platform@company.com

dependencies:
  - name: reloader #(8)!
    version: 2.2.6 #(9)!
    repository: https://stakater.github.io/stakater-charts #(10)!

home: https://github.com/stakater/Reloader #(11)!
```

1.  **Obligatoire**  
    Version de l'API Helm utilisée
      - v2 = Helm 3 (introduit en 2019)
      - v1 = Helm 2 (déprécié)

2.  **Obligatoire**  
    Nom unique de ton chart
      - Utilisé pour identifier le chart dans les repos
      - Doit être en minuscules, avec tirets autorisés

3.  **Optionnel**  
    Description courte du chart
      - Affichée dans helm search
      - Explique ce que fait le chart

4.  **Optionnel (défaut = application)**  
    Type de chart
      - application : Déploie une application
      - library : Chart réutilisable (templates partagés, pas de déploiement direct)

5.  **Obligatoire**  
    Version du chart (pas de l'application)
    Suit le SemVer : MAJOR.MINOR.PATCH
    Incrémente quand tu modifies le chart:
      - MAJOR : Changements incompatibles (breaking changes)
      - MINOR : Nouvelles fonctionnalités (compatibles)
      - PATCH : Corrections de bugs

    Exemple : 1.0.0 → 1.1.0 (ajout ServiceMonitor) → 2.0.0 (changement structure values)

6.  **Optionnel**  
    Version de l'application déployée
      - Indique quelle version de Reloader sera installée
      - Entre guillemets car peut contenir des lettres (v1.0.69)
      - Informatif uniquement

7.  **Optionnel**  
    Liste des responsables du chart
      - Contact en cas de problème
      - Peut avoir plusieurs mainteneurs

8.  **Obligatoire**  
    Nom du chart dépendant
      - Doit correspondre au nom dans le repo Helm

9.  **Obligatoire**  
    Version exacte du chart à utiliser

10. **Obligatoire**  
    URL du repo Helm où trouver le chart  
    Peut aussi être :
      - file://../local-chart : Chart local
      - oci://registry.example.com/charts : Registry OCI

11. **Optionnel**  
    URL du projet principal
    Lien vers la documentation

!!! info "INFORMATION" 
    Le fichier Chart.yaml suit le [schéma officiel Helm](https://helm.sh/docs/topics/charts/#the-chartyaml-file), qui définit les champs autorisés.

## Values

!!! Info "RETRIEVE DEFAULT VALUES"
    Depuis le répertoire ou ce trouve la charts

    ```bash title="# Mettre à jour les dépendances d'abord" hl_lines="1"
    helm dependency update
    Hang tight while we grab the latest from your chart repositories...
    ...Successfully got an update from the "stakater" chart repository
    Update Complete. ⎈Happy Helming!⎈
    Saving 1 charts
    Downloading reloader from repo https://stakater.github.io/stakater-charts
    Deleting outdated charts
    ❯ ls
     Chart.lock   Chart.yaml   charts
    ```

    ```bash title="# Voir les valeurs par défaut du chart reloader" hl_lines="1"
    helm show values charts/reloader-2.2.6.tgz
    ```

    ```yaml title="OUTPUT"
    # Generated from deployments/kubernetes/templates/chart/values.yaml.tmpl
    global:
      ## Reference to one or more secrets to be used when pulling images
      ## ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/
      ##
      imageRegistry: ""
      imagePullSecrets: []
      #imagePullSecrets:
      #  - name: my-pull-secret

    kubernetes:
      host: https://kubernetes.default

    nameOverride: ""
    fullnameOverride: ""

    image:
      name: stakater/reloader
      repository: ghcr.io/stakater/reloader
      tag: v1.4.11
      # digest: sha256:1234567
      pullPolicy: IfNotPresent

    reloader:
      autoReloadAll: false
      isArgoRollouts: false
      isOpenshift: false
      ignoreSecrets: false
      ignoreConfigMaps: false
      # Set to true to exclude Job workloads from automatic reload monitoring
      # Useful when you don't want Jobs to be restarted when their referenced ConfigMaps/Secrets change
      ignoreJobs: false
      # Set to true to exclude CronJob workloads from automatic reload monitoring
      # Useful when you don't want CronJobs to be restarted when their referenced ConfigMaps/Secrets change
      ignoreCronJobs: false
      reloadOnCreate: false
      reloadOnDelete: false
      syncAfterRestart: false
      reloadStrategy: default # Set to default, env-vars or annotations
      ignoreNamespaces: "" # Comma separated list of namespaces to ignore
      namespaceSelector: "" # Comma separated list of k8s label selectors for namespaces selection
      resourceLabelSelector: "" # Comma separated list of k8s label selectors for configmap/secret selection
      logFormat: "" # json
      logLevel: info # Log level to use (trace, debug, info, warning, error, fatal and panic)
      watchGlobally: true
      # Set to true to enable leadership election allowing you to run multiple replicas
      enableHA: false
      # Set to true to enable pprof for profiling
      enablePProf: false
      # Address to start pprof server on. Default is ":6060"
      pprofAddr: ":6060"
      # Set to true if you have a pod security policy that enforces readOnlyRootFilesystem
      readOnlyRootFileSystem: false
      legacy:
        rbac: false
      matchLabels: {}
      # Set to true to expose a prometheus counter of reloads by namespace (this metric may have high cardinality in clusters
      enableMetricsByNamespace: false
      deployment:
        # Specifies the deployment DNS configuration.
        dnsConfig: {}
        # nameservers:
        #   - 1.2.3.4
        # searches:
        #   - ns1.svc.cluster-domain.example
        #   - my.dns.search.suffix
        # options:
        #   - name: ndots
        #     value: "1"
        #   - name: attempts
        #     value: "3"

        # If you wish to run multiple replicas set reloader.enableHA = true
        replicas: 1

        revisionHistoryLimit: 2

        nodeSelector:
        # cloud.google.com/gke-nodepool: default-pool

        # An affinity stanza to be applied to the Deployment.
        # Example:
        #   affinity:
        #     nodeAffinity:
        #       requiredDuringSchedulingIgnoredDuringExecution:
        #         nodeSelectorTerms:
        #         - matchExpressions:
        #           - key: "node-role.kubernetes.io/infra-worker"
        #             operator: "Exists"
        affinity: {}

        volumeMounts: []
        volumes: []

        securityContext:
          runAsNonRoot: true
          runAsUser: 65534
          seccompProfile:
            type: RuntimeDefault

        containerSecurityContext:
          {}
          # capabilities:
          #   drop:
          #     - ALL
          # allowPrivilegeEscalation: false
          # readOnlyRootFilesystem: true

        # A list of tolerations to be applied to the Deployment.
        # Example:
        #   tolerations:
        #   - key: "node-role.kubernetes.io/infra-worker"
        #     operator: "Exists"
        #     effect: "NoSchedule"
        tolerations: []

        # Topology spread constraints for pod assignment
        # Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/
        # Example:
        # topologySpreadConstraints:
        #   - maxSkew: 1
        #     topologyKey: zone
        #     whenUnsatisfiable: DoNotSchedule
        #     labelSelector:
        #       matchLabels:
        #         app.kubernetes.io/instance: my-app
        topologySpreadConstraints: []

        annotations: {}
        labels:
          provider: stakater
          group: com.stakater.platform
          version: v1.4.11
        # Support for extra environment variables.
        env:
          # Open supports Key value pair as environment variables.
          open:
          # secret supports Key value pair as environment variables. It gets the values based on keys from default reloader se
          secret:
          #  ALERT_ON_RELOAD: <"true"|"false">
          #  ALERT_SINK: <"slack"> # By default it will be a raw text based webhook
          #  ALERT_WEBHOOK_URL: <"webhook_url">
          #  ALERT_ADDITIONAL_INFO: <"Additional Info like Cluster Name if needed">
          # field supports Key value pair as environment variables. It gets the values from other fields of pod.
          field:
          # existing secret, you can specify multiple existing secrets, for each
          # specify the env var name followed by the key in existing secret that
          # will be used to populate the env var
          existing:
          #  existing_secret_name:
          #    ALERT_ON_RELOAD: alert_on_reload_key
          #    ALERT_SINK: alert_sink_key
          #    ALERT_WEBHOOK_URL: alert_webhook_key
          #    ALERT_ADDITIONAL_INFO: alert_additional_info_key

        # Liveness and readiness probe timeout values.
        livenessProbe: {}
        #  timeoutSeconds: 5
        #  failureThreshold: 5
        #  periodSeconds: 10
        #  successThreshold: 1
        readinessProbe: {}
        #  timeoutSeconds: 15
        #  failureThreshold: 5
        #  periodSeconds: 10
        #  successThreshold: 1

        # Specify resource requests/limits for the deployment.
        # Example:
        # resources:
        #   limits:
        #     cpu: "100m"
        #     memory: "512Mi"
        #   requests:
        #     cpu: "10m"
        #     memory: "128Mi"
        resources: {}
        pod:
          annotations: {}
        priorityClassName: ""
        # imagePullSecrets:
        #   - name: myregistrykey

        # Put "0" in either to have go runtime ignore the set value.
        # Otherwise, see https://pkg.go.dev/runtime#hdr-Environment_Variables for GOMAXPROCS and GOMEMLIMIT
        gomaxprocsOverride: ""
        gomemlimitOverride: ""

      service:
        {}

        # labels: {}
        # annotations: {}
        # port: 9090

      rbac:
        enabled: true
        labels: {}
      # Service account config for the agent pods
      serviceAccount:
        # Specifies whether a ServiceAccount should be created
        create: true
        labels: {}
        annotations: {}
        # The name of the ServiceAccount to use.
        # If not set and create is true, a name is generated using the fullname template
        name:
      # Optional flags to pass to the Reloader entrypoint
      # Example:
      #   custom_annotations:
      #     configmap: "my.company.com/configmap"
      #     secret: "my.company.com/secret"
      custom_annotations: {}

      serviceMonitor:
        # Deprecated: Service monitor will be removed in future releases of reloader in favour of Pod monitor
        # Enabling this requires service to be enabled as well, or no endpoints will be found
        enabled: false
        # Set the namespace the ServiceMonitor should be deployed
        # namespace: monitoring

        # Fallback to the prometheus default unless specified
        # interval: 10s

        ## scheme: HTTP scheme to use for scraping. Can be used with `tlsConfig` for example if using istio mTLS.
        # scheme: ""

        ## tlsConfig: TLS configuration to use when scraping the endpoint. For example if using istio mTLS.
        ## Of type: https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#tlsconfig
        # tlsConfig: {}

        # bearerTokenFile:
        # Fallback to the prometheus default unless specified
        # timeout: 30s

        ## Used to pass Labels that are used by the Prometheus installed in your cluster to select Service Monitors to work wi
        ## ref: https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#prometheusspec
        labels: {}

        ## Used to pass annotations that are used by the Prometheus installed in your cluster to select Service Monitors to wo
        ## ref: https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#prometheusspec
        annotations: {}

        # Retain the job and instance labels of the metrics pushed to the Pushgateway
        # [Scraping Pushgateway](https://github.com/prometheus/pushgateway#configure-the-pushgateway-as-a-target-to-scrape)
        honorLabels: true

        ## Metric relabel configs to apply to samples before ingestion.
        ## [Metric Relabeling](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#metric_relabel_config
        metricRelabelings: []
        # - action: keep
        #   regex: 'kube_(daemonset|deployment|pod|namespace|node|statefulset).+'
        #   sourceLabels: [__name__]

        ## Relabel configs to apply to samples before ingestion.
        ## [Relabeling](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#relabel_config)
        relabelings: []
        # - sourceLabels: [__meta_kubernetes_pod_node_name]
        #   separator: ;
        #   regex: ^(.*)$
        #   targetLabel: nodename
        #   replacement: $1
        #   action: replace

        targetLabels: []

      podMonitor:
        enabled: false
        # Set the namespace the podMonitor should be deployed
        # namespace: monitoring

        # Fallback to the prometheus default unless specified
        # interval: 10s

        ## scheme: HTTP scheme to use for scraping. Can be used with `tlsConfig` for example if using istio mTLS.
        # scheme: ""

        ## tlsConfig: TLS configuration to use when scraping the endpoint. For example if using istio mTLS.
        ## Of type: https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#tlsconfig
        # tlsConfig: {}

        # bearerTokenSecret:
        # Fallback to the prometheus default unless specified
        # timeout: 30s

        ## Used to pass Labels that are used by the Prometheus installed in your cluster to select Service Monitors to work wi
        ## ref: https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#prometheusspec
        labels: {}

        ## Used to pass annotations that are used by the Prometheus installed in your cluster to select Service Monitors to wo
        ## ref: https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#prometheusspec
        annotations: {}

        # Retain the job and instance labels of the metrics pushed to the Pushgateway
        # [Scraping Pushgateway](https://github.com/prometheus/pushgateway#configure-the-pushgateway-as-a-target-to-scrape)
        honorLabels: true

        ## Metric relabel configs to apply to samples before ingestion.
        ## [Metric Relabeling](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#metric_relabel_config
        metricRelabelings: []
        # - action: keep
        #   regex: 'kube_(daemonset|deployment|pod|namespace|node|statefulset).+'
        #   sourceLabels: [__name__]

        ## Relabel configs to apply to samples before ingestion.
        ## [Relabeling](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#relabel_config)
        relabelings: []
        # - sourceLabels: [__meta_kubernetes_pod_node_name]
        #   separator: ;
        #   regex: ^(.*)$
        #   targetLabel: nodename
        #   replacement: $1
        #   action: replace

        podTargetLabels: []

      podDisruptionBudget:
        enabled: false
        # Set the minimum available replicas
        # minAvailable: 1
        # OR Set the maximum unavailable replicas
        # maxUnavailable: 1
        # If both defined only maxUnavailable will be used

      netpol:
        enabled: false
        from: []
        # - podSelector:
        #     matchLabels:
        #       app.kubernetes.io/name: prometheus
        to: []

      # Enable vertical pod autoscaler
      verticalPodAutoscaler:
        enabled: false

        # Recommender responsible for generating recommendation for the object.
        # List should be empty (then the default recommender will generate the recommendation)
        # or contain exactly one recommender.
        # recommenders:
        # - name: custom-recommender-performance

        # List of resources that the vertical pod autoscaler can control. Defaults to cpu and memory
        controlledResources: []
        # Specifies which resource values should be controlled: RequestsOnly or RequestsAndLimits.
        # controlledValues: RequestsAndLimits

        # Define the max allowed resources for the pod
        maxAllowed: {}
        # cpu: 200m
        # memory: 100Mi
        # Define the min allowed resources for the pod
        minAllowed: {}
        # cpu: 200m
        # memory: 100Mi

        updatePolicy:
          # Specifies minimal number of replicas which need to be alive for VPA Updater to attempt pod eviction
          # minReplicas: 1
          # Specifies whether recommended updates are applied when a Pod is started and whether recommended updates
          # are applied during the life of a Pod. Possible values are "Off", "Initial", "Recreate", and "Auto".
          updateMode: Auto

      webhookUrl: ""
    ```

??? example "values.yaml"

    ```yaml
    # Configuration du chart Reloader sous-jacent
    reloader:
      enabled: true

      reloader:
        # Support pour Argo Rollouts
        isArgoRollouts: true

        # Stratégie de reload
        reloadStrategy: annotations  # ou 'env-vars'

        # Surveillance globale de tous les namespaces
        watchGlobally: true

        # Ignorer certains types de ressources
        ignoreSecrets: false
        ignoreConfigMaps: false

        # Namespaces à ignorer (séparés par des virgules)
        namespaceSelector: ""
        # Exemple: "kube-system,kube-public"

        # Ressources à ignorer
        resourceLabelSelector: ""

        # Logging
        logFormat: "json"  # ou "text"

      deployment:
        # Nombre de replicas
        replicas: 2

        # Node selector pour cibler les nodes infra
        nodeSelector:
          type: infra

        # Tolerations si vos nodes infra ont des taints
        tolerations:
          - key: "node-role.kubernetes.io/infra"
            operator: "Equal"
            value: "true"
            effect: "NoSchedule"

        # Affinity pour la haute disponibilité
        affinity:
          podAntiAffinity:
            preferredDuringSchedulingIgnoredDuringExecution:
              - weight: 100
                podAffinityTerm:
                  labelSelector:
                    matchLabels:
                      app: reloader
                  topologyKey: kubernetes.io/hostname

        # Ressources
        resources:
          limits:
            cpu: 200m
            memory: 256Mi
          requests:
            cpu: 100m
            memory: 128Mi

        # Security Context
        securityContext:
          runAsNonRoot: true
          runAsUser: 65534
          fsGroup: 65534
          seccompProfile:
            type: RuntimeDefault

        # Pod Security Context
        podSecurityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
              - ALL
          readOnlyRootFilesystem: true

        # Liveness et Readiness probes
        livenessProbe:
          enabled: true
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
          successThreshold: 1

        readinessProbe:
          enabled: true
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
          successThreshold: 1

      # Labels personnalisés pour l'organisation
      labels:
        managed-by: helm-wrapper
        team: platform
        component: reloader
        environment: "{{ .Values.global.environment }}"

      # Annotations personnalisées
      annotations:
        compliance.company.com/required: "true"
        security.company.com/scan: "passed"

    # Configuration globale
    global:
      environment: production  # dev, staging, production

    # Monitoring avec Prometheus
    monitoring:
      enabled: true

      # Service pour exposer les métriques
      service:
        enabled: true
        type: ClusterIP
        port: 9090
        annotations: {}

      # ServiceMonitor pour Prometheus Operator
      serviceMonitor:
        enabled: true
        interval: 30s
        scrapeTimeout: 10s
        # Labels pour que Prometheus trouve le ServiceMonitor
        labels:
          prometheus: kube-prometheus
          release: prometheus-operator
        # Relabeling des métriques
        metricRelabelings: []
        relabelings: []

    # NetworkPolicy pour sécuriser le trafic
    networkPolicy:
      enabled: true

      # Politique Ingress
      ingress:
        # Autoriser Prometheus à scraper les métriques
        - from:
          - namespaceSelector:
              matchLabels:
                name: monitoring
          ports:
          - protocol: TCP
            port: 9090

      # Politique Egress
      egress:
        # Autoriser l'accès à l'API Kubernetes
        - to:
          - namespaceSelector: {}
          ports:
          - protocol: TCP
            port: 443
        # Autoriser DNS
        - to:
          - namespaceSelector:
              matchLabels:
                name: kube-system
          ports:
          - protocol: UDP
            port: 53

    # PodDisruptionBudget pour la haute disponibilité
    podDisruptionBudget:
      enabled: true
      minAvailable: 1
      # ou maxUnavailable: 1

    # PriorityClass pour garantir que Reloader ne soit pas évincé
    priorityClass:
      enabled: true
      name: reloader-priority
      value: 1000000
      globalDefault: false
      description: "Priority class for Reloader to prevent eviction"

    # RBAC supplémentaire (si besoin)
    rbac:
      # Permissions additionnelles
      extraRules: []
      # - apiGroups: ["argoproj.io"]
      #   resources: ["rollouts"]
      #   verbs: ["get", "list", "watch", "update", "patch"]
    ```