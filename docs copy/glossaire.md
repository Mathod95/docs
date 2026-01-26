---
hide:
  - navigation
---

## A
### `Alerting`
: L’alerting consiste à configurer des notifications automatiques lorsqu’un événement critique ou anormal survient dans le système. Cela permet aux équipes DevOps de réagir rapidement aux incidents et de maintenir la disponibilité et la performance des applications.

### `Argo`
: Argo est un écosystème d’outils cloud-native pour Kubernetes, conçu pour automatiser les workflows, les déploiements et la gestion opérationnelle. Il comprend Argo CD pour le GitOps, Argo Workflows pour orchestrer des pipelines, Argo Rollouts pour les déploiements progressifs et Argo Events pour l’automatisation pilotée par événements. Argo s’intègre de manière native avec Kubernetes, facilitant la mise en place de pipelines déclaratifs et reproductibles.

### `Artifact`
: Un artifact est un fichier généré par un pipeline CI/CD, tel qu’un binaire, une image Docker ou un bundle applicatif. Il représente une version stable du code qui peut être déployée de manière reproductible dans différents environnements.

### `Autoscaling (HPA / VPA)`
: L’autoscaling ajuste automatiquement le nombre de pods ou les ressources allouées en fonction de la charge du système. Le HPA (Horizontal Pod Autoscaler) ajuste le nombre de pods, tandis que le VPA (Vertical Pod Autoscaler) adapte les ressources CPU/mémoire des pods existants pour optimiser la performance et l’utilisation des ressources.

## B
### `Blue-Green Deployment`
: Le blue-green deployment consiste à maintenir deux environnements identiques, l’un actif et l’autre inactif. Lorsqu’une nouvelle version est prête, le trafic est basculé vers l’environnement secondaire, permettant une mise à jour sans interruption et une reprise rapide en cas de problème.

### `Build`
: La phase de build transforme le code source en un livrable exécutable ou déployable. Elle inclut la compilation, la gestion des dépendances, les tests unitaires et l’analyse statique, garantissant que l’artefact produit est stable et prêt pour les étapes suivantes du pipeline CI/CD.

## C
### `Canary Release`
: Un canary release déploie progressivement une nouvelle version à un sous-ensemble de trafic pour détecter d’éventuels problèmes avant un déploiement global. Cette stratégie réduit les risques pour les utilisateurs finaux et permet de valider les changements en production.

### `CD (Continuous Delivery / Continuous Deployment)`
: La CD automatise le déploiement du code vers la pré-production ou la production. Elle garantit que les modifications validées dans le pipeline CI peuvent être mises en production rapidement et de manière fiable, réduisant le temps entre développement et livraison.

### `CI (Continuous Integration)`
: La CI consiste à intégrer et tester automatiquement le code à chaque commit. Elle permet de détecter rapidement les erreurs et de maintenir un code fonctionnel à tout moment dans le pipeline.

### `CLI`
: La CLI (Command Line Interface) permet d’interagir avec un logiciel ou un système via des commandes textuelles. Elle est essentielle pour l’automatisation, la configuration et le contrôle précis des opérations dans un environnement DevOps.

### `CNI`
: La Container Network Interface (CNI) est un standard permettant aux conteneurs de se connecter à un réseau. Kubernetes utilise des plugins CNI comme Cilium, Calico ou Flannel pour gérer la communication entre les pods et assurer un réseau sécurisé et fiable.

### `ConfigMap`
: Un ConfigMap est un objet Kubernetes qui stocke des données de configuration non sensibles (fichiers, variables d’environnement, paramètres). Il permet de séparer la configuration du code et de rendre les applications plus modulaires et flexibles.

### `Container registry`
: Un container registry est une plateforme pour stocker, gérer et distribuer des images de conteneurs. Des exemples incluent Docker Hub, GHCR, ECR, GCR et Harbor, utilisés pour versionner et partager des images entre environnements et clusters.

### `Controller Manager`
: Le Controller Manager est un composant Kubernetes qui supervise différents contrôleurs. Il veille à ce que l’état réel du cluster corresponde à l’état désiré défini par les manifests, en effectuant les ajustements nécessaires sur les ressources.

### `CronJob`
: Un CronJob permet d’exécuter des tâches planifiées automatiquement selon une syntaxe cron. Il est utilisé pour des opérations récurrentes telles que les sauvegardes, les rapports ou les traitements batch.

### `CRD`
: Une Custom Resource Definition (CRD) permet d’ajouter de nouveaux types de ressources personnalisées dans Kubernetes. Les CRD sont à la base des opérateurs et permettent d’étendre les fonctionnalités du cluster sans modifier son cœur.

## D
### `DaemonSet`
: Un DaemonSet assure qu’un pod spécifique est exécuté sur chaque nœud du cluster. Il est utilisé pour déployer des agents système, des collecteurs de logs ou des plugins réseau sur tous les nœuds.

### `Deployment`
: Un Deployment gère le cycle de vie des pods en orchestrant les ReplicaSets et en permettant les mises à jour progressives. Il facilite les déploiements, les rollbacks et le maintien de l’état souhaité d’une application.

## E
### `Entrypoint / CMD`
: L’Entrypoint ou CMD définit la commande principale exécutée automatiquement lorsqu’un conteneur démarre. Il permet de contrôler le comportement initial d’une application conteneurisée.

## F
### `Failover`
: Le failover bascule automatiquement vers un système de secours lorsqu’un composant tombe en panne. Cela assure la continuité de service et réduit l’impact des incidents sur les utilisateurs.

### `Flannel`
: Flannel est un plugin CNI qui fournit un réseau overlay pour les pods Kubernetes. Il est simple à configurer et convient aux clusters de petite taille ou aux environnements de test.

### `FluxCD`
: FluxCD est un outil GitOps open source qui synchronise automatiquement l’état d’un cluster Kubernetes avec un dépôt Git. Il applique les changements de manière déclarative et assure une gestion cohérente de l’infrastructure.

## G
### `GitOps`
: GitOps est une approche où l’état de l’infrastructure est défini dans Git et appliqué automatiquement aux clusters. Cette méthode permet un déploiement fiable, traçable et reproductible des applications et des configurations.

## H
### `Helm`
: Helm est le gestionnaire de packages pour Kubernetes, utilisant des charts regroupant modèles YAML, valeurs par défaut et dépendances. Il simplifie le déploiement, la configuration et la mise à jour d’applications complexes, tout en facilitant la gestion multi-environnements et le versioning des déploiements.

### `High Availability (HA)`
: L’HA désigne une architecture conçue pour garantir la disponibilité maximale d’un service et la tolérance aux pannes. Elle repose sur la redondance des composants, la réplication des données et des mécanismes de basculement automatique.

## I
### `Immutable Infrastructure`
: L’infrastructure immuable est une approche où les serveurs ou conteneurs existants ne sont jamais modifiés. Toute mise à jour consiste à déployer une nouvelle version, garantissant la cohérence et la prévisibilité du système.

### `Ingress`
: Un Ingress définit les règles de routage HTTP/HTTPS pour exposer des services Kubernetes à l’extérieur. Il centralise le contrôle du trafic et peut inclure des fonctionnalités de réécriture d’URL, SSL et redirections.

### `Ingress Controller`
: L’Ingress Controller applique les règles d’Ingress dans le cluster. Des solutions comme NGINX, Traefik ou Kong assurent la gestion du trafic entrant et la sécurité des services exposés.

## J
### `Job`
: Un Job exécute une tâche unique ou répétée jusqu’à sa complétion. Il est utilisé pour les migrations, traitements batch ou autres tâches ponctuelles nécessitant un contrôle précis.

## K
### `Kind`
: Kind (Kubernetes IN Docker) permet de créer des clusters Kubernetes locaux dans des conteneurs Docker. Il est particulièrement utile pour le développement, les tests CI/CD et l’expérimentation sans déployer de cluster complet sur le cloud.

## L
### `Liveness Probe`
: La Liveness Probe vérifie périodiquement qu’un conteneur est en bon état de fonctionnement. Si le contrôle échoue, Kubernetes redémarre le pod pour restaurer un état sain.

### `Load balancer`
: Un load balancer répartit le trafic réseau entre plusieurs instances d’une application. Il améliore la performance, la disponibilité et la tolérance aux pannes.

### `Load Balancing`
: Le load balancing consiste à distribuer le trafic ou les demandes utilisateur sur plusieurs serveurs pour optimiser les performances et éviter les surcharges.

### `Logging`
: Le logging centralise la collecte et le stockage des journaux applicatifs et systèmes. Il permet d’analyser le comportement du système, détecter les erreurs et assurer la traçabilité des événements.

## M
### `Metrics`
: Les metrics sont des mesures quantitatives sur les ressources et performances d’un système (CPU, RAM, latence, erreurs). Elles servent à surveiller, diagnostiquer et optimiser les applications et l’infrastructure.

## N
### `N8N`
: N8N est un outil open source d’automatisation de workflows permettant de connecter des applications et services. Il offre une interface visuelle pour créer des pipelines et automatiser des processus sans écrire beaucoup de code.

### `Namespace`
: Un namespace isole les ressources au sein d’un cluster Kubernetes. Il facilite l’organisation, la gestion des permissions, l’application de quotas et la séparation des environnements ou projets.

### `Network Policy`
: Les Network Policies définissent les règles de communication entre pods dans un cluster Kubernetes. Elles permettent de sécuriser le réseau interne en contrôlant quel pod peut parler à quel service.

### `Node`
: Un node est une machine physique ou virtuelle exécutant des pods Kubernetes. Chaque node fournit les ressources nécessaires pour faire tourner les conteneurs et communiquer avec le cluster.

## O
### `Observability`
: L’observabilité regroupe les pratiques permettant de comprendre l’état interne d’un système à partir des logs, metrics et traces distribuées. Elle est essentielle pour diagnostiquer les problèmes et optimiser les performances.

### `OCI (Open Container Initiative)`
: OCI définit des standards pour les formats d’images et les runtimes de conteneurs, assurant l’interopérabilité entre outils comme Docker, containerd ou Podman.

### `Operator`
: Un Operator est un composant Kubernetes qui automatise la gestion d’applications complexes à l’aide de CRD et de contrôleurs personnalisés, permettant de gérer le cycle de vie complet d’une application.

## P
### `PersistentVolume (PV)`
: Un PV est une ressource de stockage durable dans Kubernetes, indépendante du cycle de vie des pods, utilisée pour conserver les données de manière persistante.

### `PersistentVolumeClaim (PVC)`
: Un PVC est une requête faite par un pod pour utiliser un volume persistant. Il permet de lier dynamiquement ou statiquement un stockage à un pod selon ses besoins.

### `Pipeline CI/CD`
: Un pipeline CI/CD est une suite d’étapes automatisées incluant tests, build, analyse et déploiement, permettant de livrer du code de manière fiable et reproductible.

### `Pod`
: Un pod est l’unité de base d’exécution dans Kubernetes, pouvant contenir un ou plusieurs conteneurs partageant réseau et stockage. Les pods sont gérés par des contrôleurs tels que Deployment ou StatefulSet.

## Q
### `QoS (Quality of Service Class)`
: QoS classe les pods selon leur priorité et leurs demandes/limites de ressources (Guaranteed, Burstable, BestEffort), influençant la planification et la tolérance aux ressources du cluster.

### `Quota`
: Un quota limite l’usage des ressources (CPU, mémoire, stockage, objets) dans un namespace, garantissant un partage équitable et la stabilité du cluster.

## R
### `Readiness Probe`
: La Readiness Probe indique si un pod est prêt à recevoir du trafic. Si le pod n’est pas prêt, il est exclu des services exposés jusqu’à ce qu’il le devienne.

### `ReplicaSet`
: Un ReplicaSet garantit qu’un nombre défini de pods identiques est toujours en fonctionnement. Il est souvent géré indirectement via des Deployments pour les mises à jour progressives.

### `Rolling Update`
: Le rolling update met à jour les pods progressivement, un par un, pour limiter les interruptions et maintenir la disponibilité du service pendant la mise à jour.

## S
### `Secret`
: Un Secret stocke des données sensibles encodées, comme des tokens ou mots de passe, permettant de sécuriser la configuration et l’accès aux services.

### `Service (ClusterIP / NodePort / LoadBalancer)`
: Un Service expose un ou plusieurs pods via une IP stable ou vers l’extérieur, offrant un point d’accès unique pour la communication réseau.

### `Service Mesh`
: Un service mesh gère la communication entre services dans un cluster, offrant sécurité, routage, observabilité et résilience, avec des outils comme Istio ou Linkerd.

### `sailor.sh`
: Sailor.sh est un simulateur en ligne pour pratiquer les examens Kubernetes (CKA, CKAD, CKS), avec des laboratoires et scénarios réalistes pour s’entraîner aux compétences pratiques.

### `Scheduler`
: Le scheduler décide sur quel node chaque pod doit être placé, en fonction des ressources disponibles, des contraintes et des politiques définies.

### `SLI`
: Un SLI (Service Level Indicator) mesure la performance réelle d’un service par rapport à un objectif défini, comme le temps de réponse ou le taux d’erreur.

### `SLO`
: Un SLO (Service Level Objective) définit un objectif de performance mesurable pour un service, utilisé pour évaluer le respect d’un SLA.

### `SLA`
: Un SLA (Service Level Agreement) est un contrat définissant les niveaux de service attendus entre un fournisseur et un client.

### `StatefulSet`
: Un StatefulSet gère les pods nécessitant une identité stable, du stockage persistant ou un ordre de déploiement spécifique.

### `StorageClass`
: Une StorageClass définit la manière dont un PersistentVolume doit être provisionné, y compris le type de disque et les performances attendues.

## T
### `Tracing / Distributed Tracing`
: Le tracing distribué suit les requêtes à travers différents services et composants, permettant de comprendre les interactions et identifier les goulots d’étranglement.

## U
### `Upstream`
: L’upstream désigne la source principale d’un projet open source, souvent utilisée pour distinguer les dépôts officiels des forks ou dérivés.

### `Undeploy`
: Undeploy consiste à retirer proprement une application déployée, en supprimant ses ressources Kubernetes et l’infrastructure associée.

## V
### `Volume`
: Un volume est un espace de stockage attaché à un pod pour conserver les données, éphémères ou persistantes, selon le type de volume.

## W
### `Webhook`
: Un webhook est un mécanisme qui permet à un service d’envoyer automatiquement une requête HTTP lorsqu’un événement survient, par exemple pour déclencher un pipeline CI/CD.

### `Workload`
: Un workload désigne toute ressource responsable d’exécuter des applications dans Kubernetes, comme Deployment, Job, DaemonSet ou StatefulSet.

### `WASM (WebAssembly)`
: Le WebAssembly est un format bytecode performant permettant d’exécuter des applications sandboxées. Il commence à être utilisé dans Kubernetes pour des workloads légers et sécurisés.

## X
### `X.509`
: X.509 est un standard de certificats utilisés pour chiffrer et authentifier les communications, notamment pour TLS/mTLS et les API Kubernetes.

### `XP (Extreme Programming)`
: XP est une méthodologie Agile centrée sur l’amélioration continue, la qualité du code et la réduction du cycle de feedback grâce à des pratiques comme le TDD ou le pair programming.

## Y
### `YAML`
: YAML est un format de fichier structuré très utilisé dans Kubernetes pour déclarer les ressources de manière hiérarchique et lisible par l’homme.

### `YTT (YAML Templating Tool)`
: YTT est un outil de templating pour YAML qui permet de générer ou modifier dynamiquement des manifests Kubernetes, facilitant la réutilisation et la personnalisation des configurations.

## Z
### `ZSH`
: ZSH est un shell Unix puissant et personnalisable, alternatif à Bash, souvent utilisé avec des frameworks comme Oh My Zsh pour améliorer la productivité et la configuration du terminal.
