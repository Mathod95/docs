---
hide:
  - tags
title: Argo CD
description: "Argo CD"
date: 2025-12-08
tags:
  - Argo
  - Argo CD
categories:
  - Documentation
  - Argo CD
author: "Mathias FELIX"
---

## Introduction

### Qu'est-ce que GitOps

GitOps est un cadre opérationnel qui utilise Git comme source unique de vérité pour gérer à la fois l'infrastructure et le code des applications. Il étend les principes de l'Infrastructure as Code (IaC), permettant des déploiements et des retours en arrière automatisés en contrôlant l'ensemble du pipeline de livraison de code via le contrôle de version Git.

### Workflow GitOps

Les développeurs commencent par commettre leurs modifications dans un dépôt Git centralisé. En général, ils travaillent dans des branches de fonctionnalités créées comme des copies de la branche principale du code. Ces branches permettent aux équipes de développer de nouvelles fonctionnalités de manière isolée, jusqu'à ce qu'elles soient prêtes. Un service d'Intégration Continue (CI) construit automatiquement l'application et exécute des tests unitaires sur le nouveau code. Une fois les tests passés, les modifications sont soumises à un processus de révision et d'approbation par les membres de l'équipe avant d'être fusionnées dans le dépôt central.

L'étape finale du pipeline est le Déploiement Continu (CD), où les changements du dépôt sont automatiquement déployés dans les clusters Kubernetes.

L'image illustre le workflow GitOps, montrant l'intégration de l'infrastructure, des configurations et du code des applications dans un dépôt Git, suivie des processus d'intégration continue (CI) et de déploiement continu (CD) vers un cluster Kubernetes. Elle représente également le processus de création et de fusion de branches dans Git.

Au cœur de GitOps se trouve le concept d'un état défini de manière déclarative. Cela consiste à maintenir votre infrastructure, vos configurations d'application et les composants associés dans un ou plusieurs dépôts Git. Un processus automatisé vérifie en permanence que l'état stocké dans Git correspond à l'état réel de l'environnement de production. Cette synchronisation est gérée par un opérateur GitOps exécuté au sein d'un cluster Kubernetes. L'opérateur surveille le dépôt pour détecter les mises à jour et applique les changements souhaités au cluster — ou même à d'autres clusters si nécessaire.

Lorsque qu'un développeur fusionne du nouveau code dans le dépôt de l'application, une série d'étapes automatisées est déclenchée : les tests unitaires sont exécutés, l'application est construite, une image Docker est créée et poussée vers un registre de conteneurs, et enfin, les manifestes Kubernetes dans un autre dépôt Git sont mis à jour.

L'image montre un workflow GitOps, illustrant le processus allant de la fusion du code de l'application et de l'intégration continue au déploiement des manifestes Kubernetes, avec des opérateurs GitOps garantissant que l'état souhaité correspond à l'état réel dans les environnements de production.

L'opérateur GitOps compare en permanence l'état souhaité (défini dans Git) avec l'état réel du cluster Kubernetes. Si des divergences sont détectées, l'opérateur récupère les modifications nécessaires pour garantir que l'environnement de production reste aligné avec la configuration souhaitée.

L'image montre également un workflow GitOps, soulignant le processus allant du dépôt du code de l'application via l'intégration continue jusqu'au déploiement Kubernetes, mettant en évidence la synchronisation entre l'état souhaité et l'état réel.

!!! Note "Facilité des Rollbacks"
    L'un des principaux avantages de GitOps est la facilité de retour arrière (rollback). Puisque l'ensemble de la configuration est maintenu dans Git, revenir à un état précédent est aussi simple que d'exécuter une commande `git revert`. L'opérateur GitOps détecte ce changement et rétablit automatiquement l'environnement de production pour qu'il corresponde à l'état souhaité.

L'image illustre à nouveau un workflow GitOps, montrant le processus depuis le dépôt de code de l'application via l'intégration continue jusqu'au déploiement Kubernetes, et mettant en évidence la synchronisation entre les états souhaité et réel.

---


---
## Argo CD Intermediate

### Configuration déclarative
Dans ce guide, nous démontrons comment configurer des ressources Kubernetes de manière déclarative à l’aide d’un exemple d’application Mono. La gestion déclarative consiste à définir les ressources Kubernetes (telles que les Deployments, Services, Secrets et ConfigMaps) et les objets ArgoCD (y compris Applications, Repositories et Projects) dans des fichiers de manifeste. Ces fichiers peuvent être appliqués à l’aide de l’interface en ligne de commande kubectl pour garantir que l'état souhaité soit maintenu.

Auparavant, nous avons créé des applications ArgoCD à l’aide de l'interface en ligne de commande (CLI) et de l'interface utilisateur (UI), en fournissant de manière interactive la source et la destination. En revanche, cette approche utilise des fichiers de manifeste déclaratifs pour définir et gérer ces applications de manière systématique.

!!! note "Pourquoi utiliser la configuration déclarative ?"
    Définir votre infrastructure sous forme de code dans Git offre une traçabilité claire, un contrôle de version et simplifie la gestion des changements à travers différents environnements.

#### Structure du dépôt Git
Supposons que vous ayez un dépôt Git avec la structure ci-dessous. Le dépôt contient un répertoire appelé "declarative" avec deux sous-répertoires : "manifests" et "mono-app".

```shell 
Structure du dépôt Git :
└── declarative
    ├── manifests
    │   ├── geocentric-model
    │   │   ├── deployment.yml
    │   │   └── service.yml
    └── mono-app
        └── geocentric-app.yml
```

Dans le répertoire "mono-app", vous trouverez un fichier YAML d’application ArgoCD. Ce fichier définit l’application en spécifiant :

- **Project Name**: Le projet dans ArgoCD.
- **Source Configuration**: Inclut l'URL du dépôt Git, la révision (par exemple, HEAD), et le chemin pointant vers les manifestes Kubernetes souhaités (c’est-à-dire le répertoire "geocentric-model" dans "declarative/manifests"). Ce répertoire contient deux fichiers YAML : un pour le Deployment et un pour le Service.
- **Destination Configuration**: Spécifie le cluster cible (en utilisant l'URL du cluster local) et le namespace où les ressources seront déployées.
- **Sync Policy**: Une politique optionnelle qui peut automatiser le processus de synchronisation et d'auto-réparation.

#### Création de l'application
Une fois que vous avez défini votre manifeste, créez l’application en exécutant la commande suivante :

```shell hl_lines="1"
$ kubectl apply -f mono-app/geocentric-app.yml  
application.argoproj.io/geocentric-model-app created  
```

Après la création de l'application, ArgoCD va récupérer les manifestes de Deployment et de Service depuis le dépôt Git. Il créera ensuite les ressources sur le cluster cible, soit manuellement via une opération de synchronisation, soit automatiquement si la synchronisation est configurée.

!!! Avantage clé
    En gérant à la fois la définition de votre application et ses ressources correspondantes dans le contrôle de version, vous pouvez facilement suivre les changements et maintenir un état cohérent entre vos environnements.

#### Exemple de manifeste d'application ArgoCD
Voici un exemple de manifeste d'application ArgoCD qui encapsule cette configuration déclarative :

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: geocentric-model-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/sidd-harth/test-cd.git
    targetRevision: HEAD
    path: ./declarative/manifests/geocentric-model
  destination:
    server: https://kubernetes.default.svc
    namespace: geocentric-model
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    automated:
      selfHeal: true
```

Ce manifeste définit l’application en spécifiant tous les détails nécessaires, y compris le dépôt, la révision, et les chemins des ressources. Il configure également des options de synchronisation automatisée, garantissant que votre application correspond en permanence à l'état souhaité défini dans Git.

Utiliser une approche déclarative avec Git comme source unique de vérité garantit que les changements d’infrastructure sont versionnés, audités et facilement annulés si nécessaire. Pour plus de lecture sur les meilleures pratiques Kubernetes et ArgoCD, consultez la Documentation Kubernetes et la Documentation ArgoCD.

---

### Configuration déclarative de l’application Mono
Dans cette leçon, vous apprendrez comment gérer une application ArgoCD unique de manière déclarative. Contrairement aux approches précédentes qui utilisaient l'interface en ligne de commande (CLI) ou l'interface utilisateur (UI) d'ArgoCD, cette méthode consiste à stocker et gérer les manifestes d'application ArgoCD dans un dépôt Git, tout comme pour tout autre manifeste de déploiement ou de service Kubernetes.

L’image montre une interface web pour configurer une application dans ArgoCD, avec des options pour définir le nom de l'application, le nom du projet, la politique de synchronisation et d’autres paramètres. La barre latérale gauche affiche les indicateurs d'état de synchronisation et de santé.

Dans l'UI ArgoCD, vous définissez les métadonnées de l'application, les détails de la source et de la destination. En coulisse, cela crée une spécification YAML qui décrit l’application. Voici un exemple de manifeste :

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sample-app
spec:
  destination:
    namespace: sample
    server: https://kubernetes.default.svc
  source:
    path: ./sample
    repoURL: http://139.59.21.103:3000/siddhanth/gitops-argocd
    targetRevision: HEAD
  project: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

!!! Note
    ArgoCD peut créer et gérer des applications automatiquement en utilisant des spécifications YAML stockées dans des dépôts Git.

#### Créer une application ArgoCD déclarative

Pour configurer une application ArgoCD unique en utilisant l’approche déclarative, suivez ces étapes :

- **1. Localiser le répertoire du dépôt**  
Dans votre dépôt GitOps ArgoCD, trouvez le répertoire "MonoApplication". Dans cet exemple, le manifeste de l'application est stocké dans le répertoire "mono-app". Vous devriez y voir un fichier nommé geocentric-app.yml.

L’image montre une interface de dépôt Gitea avec des détails sur les branches, les commits et les changements récents. Elle comprend des options pour créer un fichier, télécharger un fichier ou appliquer un patch.

- **2. Vérifier le manifeste YAML**  
Voici un extrait du fichier geocentric-app.yml qui définit l'application ArgoCD. Cet exemple inclut des champs essentiels tels que le type, la version API, le projet et les détails de la source :

```yaml linenums="1" title="application.yaml"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: geocentric-model-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: http://165.22.209.118:3000/siddharth/gitops-argocd.git
    targetRevision: HEAD
    path: ./declarative/manifests/geocentric-model
  destination:
    server: https://kubernetes.default.svc
    namespace: geocentric-model
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    automated:
      prune: true
      selfHeal: true
```

Ce manifeste indique à ArgoCD de récupérer les manifestes de l'application depuis le répertoire spécifié, de les déployer dans le namespace geocentric-model, et d'activer la synchronisation automatisée avec des options de nettoyage (pruning) et d'auto-réparation (self-healing).

!!! Tip
    Les extraits YAML dupliqués ont été consolidés pour plus de clarté. Utilisez le même manifeste pour garantir la cohérence des déploiements.

- **3. Déployer l’application avec kubectl**

Suivez ces étapes pour récupérer le dépôt dans votre cluster Kubernetes et créer l'application :

Clonez le dépôt et naviguez jusqu’au dossier mono-app :

```shell 
mkdir demo
cd demo/
git clone http://139.59.21.103:3000/siddharth/gitops-argocd
cd gitops-argocd/
ll
```

Naviguez vers le répertoire declarative/mono-app/ et confirmez le contenu du fichier geocentric-app.yml :

```shell 
cd declarative/mono-app/
cat geocentric-app.yml
```

Appliquez le manifeste dans le namespace argocd avec la commande suivante :

```shell 
kubectl -n argocd apply -f geocentric-app.yml
```

Une fois appliqué, vous devriez voir la sortie suivante, indiquant un succès :

```shell 
application.argoproj.io/geocentric-model-app created
```

- **4. Vérifier le déploiement de l’application**

Confirmez l'état de l'application en utilisant à la fois la CLI ArgoCD et les commandes kubectl :

Listez les applications avec ArgoCD :

```shell 
argocd app list
```

Cela affichera la liste des applications, y compris geocentric-model-app.

Vous pouvez également vérifier son état avec :

```shell
kubectl -n argocd get applications
```

Avec la synchronisation automatisée activée, ArgoCD mettra à jour automatiquement l'application. Vérifiez l'UI ArgoCD pour confirmer que les ressources de déploiement et de service sont correctement déployées.

#### Exposer l'application

Accédez à l'application déployée via le service exposé en NodePort. Par exemple, si le service est exposé sur le port 30682, vous pouvez utiliser ce port pour accéder à l'UI de l'application. Voici un exemple de manifeste de service :

```yaml linenums="1"
apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: >
      {"apiVersion":"v1","kind":"Service","metadata":{},"labels":{"app.kubernetes.io/instance":"geocentric-model-app"},"name":"geocentric-model-svc","namespace":"geocentric-model"}
  creationTimestamp: '2022-09-23T17:52:34Z'
  labels:
    app.kubernetes.io/instance: geocentric-model-app
  name: geocentric-model-svc
  namespace: geocentric-model
spec:
  clusterIP: 10.111.125.181
  ports:
    - nodePort: 38684
      port: 80
      protocol: TCP
      targetPort: 80
  selector:
    app: geocentric-model
  type: NodePort
```

!!! Warning
    Assurez-vous que le fichier geocentric-app.yml est créé dans le namespace ArgoCD pour éviter tout problème de déploiement.

#### Résumé

Dans ce guide, vous avez appris à gérer une application ArgoCD unique de manière déclarative en :

- Stockant le manifeste YAML dans un dépôt Git.
- Déployant l'application à l'aide de kubectl.
- Vérifiant l'état de l'application via la CLI et l'UI ArgoCD.

Cette approche déclarative simplifie la gestion des applications en intégrant les principes GitOps, garantissant que le déploiement de votre application soit reproductible et contrôlé en version.

---

### **App of Apps**
Dans cet article, nous explorons le modèle "App-of-Apps" dans ArgoCD—une approche déclarative qui simplifie la création et la gestion des applications ArgoCD. Plutôt que de déployer manuellement chaque application, ce modèle génère et gère de manière programmatique plusieurs applications ArgoCD à partir d'une seule configuration racine.

L'idée principale est de créer une application racine ArgoCD dont la source pointe vers un dossier contenant des fichiers de définition YAML pour chaque microservice ou application. Chaque fichier YAML spécifie un chemin vers un répertoire contenant les manifestes Kubernetes associés. Une fois tous ces fichiers de configuration commis dans un dépôt Git, ArgoCD détecte automatiquement et déploie les applications définies.

!!! note "Comment cela fonctionne"
    L'application racine agit en tant qu'orchestre. Elle indique à ArgoCD de parcourir le répertoire spécifié, en lisant chaque fichier YAML pour instancier les applications associées. Cela garantit que les mises à jour dans votre dépôt Git déclenchent une synchronisation automatique avec votre cluster Kubernetes.

#### Exemple de structure du dépôt

Supposons que votre dépôt Git soit organisé de sorte que chaque répertoire contienne les fichiers nécessaires pour une application spécifique. L'exemple suivant examine le fichier YAML de l'application racine ArgoCD, qui est placé dans un répertoire multi-applications. Cette application racine pointe vers le répertoire `app-of-apps`, incitant ArgoCD à créer toutes les applications enfants définies dans ce dossier.

```yaml linenums="1"
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-of-apps
spec:
  project: default
  source:
    repoURL: https://github.com/sidd-harth/test-cd.git
    targetRevision: HEAD
    path: ./declarative/app-of-apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Dans cet exemple, trois fichiers YAML d'application ArgoCD sont définis dans le répertoire spécifié. ArgoCD lit ces définitions et crée automatiquement les applications correspondantes.


#### Examen détaillé : Fichier YAML de l'application Circle

Voyons maintenant le fichier YAML de l’application **Circle App** en tant qu'exemple. Chaque fichier YAML d'application comprend un champ **source** qui fait référence à son répertoire de manifeste spécifique. Dans l'exemple de **Circle App**, ArgoCD utilise les détails fournis pour créer ou mettre à jour le déploiement et le service dans le cluster Kubernetes.

```yaml
# declarative/app-of-apps/app-of-apps.yml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-of-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/sidd-harth/test-cd.git
    targetRevision: HEAD
    path: ./declarative/app-of-apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

# declarative/app-of-apps/circle-app.yml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: circle-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/sidd-harth/test-cd.git
    targetRevision: HEAD
    path: ./declarative/manifests/circle
  destination:
    server: https://kubernetes.default.svc
    namespace: circle
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
```

En utilisant ce modèle, ArgoCD crée automatiquement toutes les applications listées et déploie leurs manifestes Kubernetes associés. Cette approche peut être étendue pour gérer n'importe quel objet Kubernetes—y compris ArgoCD lui-même. Chaque fois qu'une définition d'application est mise à jour ou qu'une nouvelle application est ajoutée dans votre dépôt Git, ArgoCD garantit que vos déploiements restent synchronisés en mettant à jour ou en créant automatiquement les applications correspondantes.

#### **Avantages du modèle App-of-Apps**

| **Avantage**                    | **Description**                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Contrôle centralisé**         | Gérer plusieurs applications à partir d'une seule application ArgoCD.                                   |
| **Synchronisation automatisée** | Détecter et déployer automatiquement les changements de votre dépôt Git vers votre cluster Kubernetes.  |
| **Gestion évolutive**           | Ajouter ou mettre à jour des applications facilement sans intervention manuelle sur chaque déploiement. |

#### **Résumé**

Le modèle **App-of-Apps** dans ArgoCD permet de gérer plusieurs applications de manière déclarative et automatisée à partir d'une application racine. Ce modèle facilite la gestion de déploiements complexes tout en améliorant l'efficacité opérationnelle, ce qui en fait un outil essentiel dans les workflows modernes basés sur GitOps.

Pour plus d’informations sur Kubernetes et les modèles de déploiement déclaratifs, vous pouvez consulter les ressources suivantes :

L'utilisation du modèle **App-of-Apps** simplifie les déploiements complexes et améliore l'efficacité des opérations, en garantissant que chaque modification dans votre dépôt Git se reflète instantanément dans vos déploiements Kubernetes.

---

### Configuration déclarative avec l'App of Apps

Dans cette leçon, vous apprendrez à étendre l'approche déclarative des applications ArgoCD en déployant plusieurs applications à l'aide du modèle **"app-of-apps"**. Ce modèle permet à une seule application ArgoCD de gérer d'autres applications ArgoCD, simplifiant ainsi le déploiement et la gestion de plusieurs services.

La structure du dépôt pour cette configuration organise plusieurs configurations ArgoCD dans des répertoires distincts, chacun contenant les fichiers manifestes pour des applications individuelles.

#### Application ArgoCD multi-applications

L'application principale multi-applications pointe vers le dépôt Git et spécifie le chemin contenant les manifestes qui gèrent d'autres applications ArgoCD. Sa définition est la suivante :

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-of-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: http://165.22.209.118:3000/siddharth/gitops-argocd.git
    targetRevision: HEAD
    path: ./declarative/multi-app
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

!!! Note
    La configuration multi-app récupère les manifestes à partir d'un répertoire spécifique, offrant ainsi une configuration centralisée pour gérer les applications imbriquées.


#### Configuration de l'App of Apps

L'application principale fait référence au répertoire `app-of-apps`, où plusieurs manifestes d'applications ArgoCD résident. La configuration pour l'**App of Apps** est la suivante :

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-of-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: http://165.22.209.118:3000/siddharth/gitops-argocd.git
    targetRevision: HEAD
    path: ./declarative/app-of-apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Dans le répertoire `declarative/app-of-apps`, vous trouverez trois manifestes d'applications ArgoCD :

* **Heliocentric App** : récupère les manifestes Kubernetes à partir d'un chemin spécifique.
* **Geocentric App** : pointe vers un autre chemin de manifeste.
* **Applications supplémentaires** : vous pouvez ajouter d'autres sous-applications pour étendre encore les capacités de déploiement.


#### Manifeste de l'application Heliocentric

Voici l'exemple du manifeste pour l'application **Heliocentric** :

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: heliocentric-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: http://165.22.209.118:3000/siddharth/gitops-argocd.git
    targetRevision: HEAD
    path: ./declarative/manifests/heliocentric-model
  destination:
    server: https://kubernetes.default.svc
    namespace: heliocentric
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    automated:
      prune: true
      selfHeal: true
```


#### Manifeste de l'application Geocentric

Le manifeste de l'application **Geocentric** est configuré de manière similaire :

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: geocentric-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: http://165.22.209.118:3000/siddharth/gitops-argocd.git
    targetRevision: HEAD
    path: ./declarative/manifests/geocentric-model
  destination:
    server: https://kubernetes.default.svc
    namespace: geocentric
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    automated:
      prune: true
      selfHeal: true
```



#### Manifestes Kubernetes des applications

Au-delà des manifestes d'applications ArgoCD, le répertoire déclaratif contient également des manifestes Kubernetes séparés pour chaque application, notamment des déploiements et des services. Lorsque vous créez l'application **App-of-Apps** ArgoCD principale, elle déclenche automatiquement la création de trois autres applications ArgoCD.

Par exemple, une version alternative du manifeste **app-of-apps** avec un namespace de destination différent pourrait être définie comme suit :

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-of-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: http://165.22.209.118:3000/siddharth/gitops-argocd.git
    targetRevision: HEAD
    path: ./declarative/app-of-apps
  destination:
    server: https://kubernetes.default.svc
    namespace: kubernetes
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Chaque application imbriquée déploie ensuite ses ressources Kubernetes respectives en fonction de son propre manifeste.



#### Processus de déploiement

Pour déployer des applications à l'aide du modèle **App-of-Apps**, suivez ces étapes :

1. **Supprimez** toute application Geocentric model précédemment déployée si elle existe, car elle sera recréée sous le nouveau modèle de gestion.
2. Naviguez vers le répertoire **multi-app**, qui contient le fichier **app-of-apps.yml**.
3. Appliquez le manifeste dans le namespace `argocd` en exécutant :

```bash
cd multi-app/
ll
# Assurez-vous que le fichier app-of-apps.yml est présent ici.
kubectl -n argocd apply -f app-of-apps.yml
```

Après le déploiement, l'interface ArgoCD affichera plusieurs applications :

* **app-of-apps** (gérant les applications imbriquées)
* **geocentric-app**
* **heliocentric-app**
* **heliocentric-app sans Pluto** (une variante alternative)


#### Conseil de déploiement

Assurez-vous qu'aucune ancienne configuration n'interfère avec le nouveau déploiement en supprimant les applications obsolètes avant d'appliquer le nouveau manifeste.


### **Affichage des applications dans l'interface ArgoCD**

Dans le tableau de bord ArgoCD, cliquez sur n'importe quelle sous-application (par exemple, **geocentric-app** ou **heliocentric-app**) pour afficher des informations détaillées sur le manifeste. Voici un extrait de manifeste pour une application en cours de synchronisation :

```yaml
status:
  health:
    status: Healthy
  history:
    deployStartDate: '2022-09-23T20:05:21Z'
    deployEndDate: '2022-09-23T20:05:24Z'
    revision: e2edb3a016b752028c38adb898d34114c1ec6
    path: ./declarative/manifests/heliocentric-model
    repoURL: http://165.22.209.118:3000/siddharth/gitops-argocd.git
  operationState:
    finishedAt: '2022-09-23T20:05:24Z'
    message: successfully synced (all tasks run)
    initiatedBy:
      automated: true
    retry:
      limit: 5
    sync:
      prune: true
      revision: e2edb3a016b752028c38adb898d34114c1ec6
      syncOptions:
        - CreateNamespace=true
    phase: Succeeded
    startedAt: '2022-09-23T20:05:21Z'
    syncResult:
      resources:
        - group: 
            hookPhase: Succeeded
            kind: Namespace
            message: namespace/heliocentric created
            namespace: heliocentric
            status: Synced
            syncPhase: PreSync
            version: v1
        - group: 
            hookPhase: Running
            kind: Service
            message: service/heliocentric-model-svc created
            name: heliocentric-model-svc
            namespace: heliocentric
            status: Sync
```

### **Accéder aux applications Kubernetes déployées**

Chaque sous-application déploie son propre ensemble de ressources Kubernetes, y compris des services qui exposent les applications. Voici les détails de configuration pour ces services :

**Service du modèle Geocentric** :

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: >
      {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"geocentric-app"},"name":"geocentric-model-svc","namespace":"geocentric"}}
  labels:
    app.kubernetes.io/instance: geocentric-app
  name: geocentric-model-svc
```

**Service du modèle Heliocentric (avec NodePort)** :

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: >
      {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"heliocentric-app"},"name":"heliocentric-model-svc","namespace":"heliocentric"},"spec":{"clusterIP":"10.183.221.139","clusterIPs":["10.183.221.139"],"externalTrafficPolicy":"Cluster","internalTrafficPolicy":"Cluster","ipFamilies":["IPv4"],"ipFamilyPolicy":"SingleStack","ports":[{"nodePort":31334,"port":80,"protocol":"TCP","targetPort":80}],"selector":{"app":"heliocentric-model"},"sessionAffinity":"None","type":"NodePort"}}
spec:
  clusterIP: 10.183.221.139
  clusterIPs:
    - 10.183.221.139
  externalTrafficPolicy: Cluster
  internalTrafficPolicy: Cluster
  ipFamilies:
    - IPv4
  ipFamilyPolicy: SingleStack
  ports:
    - nodePort: 31334
      port: 80
      protocol: TCP
      targetPort: 80
  selector:
    app: heliocentric-model
  sessionAffinity: None
  type: NodePort
  loadBalancer: {}
```

**Service du modèle Heliocentric (sans Pluto)** :

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: >
      {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"heliocentric-model-no-pluto-app"},"name":"heliocentric-model-no-pluto-svc","resourceVersion":"1964046","uid":"73603805-36c2-4296-bd9c-2f14cac42080"}}
spec:
  clusterIP: 10.180.97.241
  externalIPs:
    - 10.180.97.241
  externalTrafficPolicy: Cluster
  internalTrafficPolicy: Cluster
  ipFamily:
    - IPv4
  ipFamilyPolicy: SingleStack
  ports:
    - name: nodePort
      port: 80
      protocol: TCP
      targetPort: 80
  selector:
    app: heliocentric-model-no-pluto
  sessionAffinity: None
  type: NodePort
status:
  loadBalancer: {}
```

!!! Fun Fact
    Beaucoup d’utilisateurs considèrent que Pluto ne devrait pas être classé comme une planète en raison de son orbite distante et de sa rotation rétrograde, ce qui explique pourquoi une variante d’application excluant Pluto est fournie.

Toutes ces applications sont déployées à l'aide d'une seule configuration ArgoCD **App-of-Apps**. Ce modèle simplifie non seulement la gestion, mais permet également un contrôle centralisé sur plusieurs applications à partir d'un seul dépôt Git et instance ArgoCD.

---

### Déployer des applications avec un **Helm Chart**
Dans cet article, nous explorons comment ArgoCD déploie et gère des applications en utilisant des **Helm Charts**, simplifiant ainsi la gestion de Kubernetes et adoptant les principes de GitOps.

**Helm** est le gestionnaire de paquets pour Kubernetes qui simplifie l'installation et la gestion du cycle de vie des applications en utilisant des collections de fichiers de configuration YAML, appelées **Helm Charts**. Ces Charts regroupent les définitions YAML nécessaires au déploiement d'un ensemble de ressources Kubernetes. Avec les définitions d'applications déclaratives comme principe fondamental de GitOps, les **Helm Charts** peuvent être stockés dans des dépôts spécialement conçus pour les empaqueter et les distribuer.

ArgoCD améliore ce processus en déployant des **Helm Charts** empaquetés, en les surveillant pour des mises à jour, et en gérant leur cycle de vie après leur déploiement. Par exemple, si vous avez un dépôt Git structuré avec un **Helm Chart**, l'interface en ligne de commande (CLI) d'ArgoCD peut être utilisée pour créer une application qui le déploie. En spécifiant l'URL du dépôt, le chemin vers le chart, et les valeurs de remplacement via l'option `Helm Set`, vous obtenez un processus de déploiement flexible et continu.

ArgoCD est polyvalent et prend en charge le déploiement à partir de diverses sources :

* Artifactory Hub
* Bitnami Helm Charts

De plus, vous pouvez déployer un **Helm Chart** en utilisant l'interface utilisateur (UI) d'ArgoCD. L'UI simplifie la connexion aux dépôts en prenant en charge les intégrations SSH, HTTPS ou GitHub App. Elle permet également de configurer les détails du dépôt, tels que le nom, le type, l'URL, et les informations d'identification pour accéder aux dépôts privés.

!!! Note
    Une fois qu'ArgoCD déploie une application en utilisant un **Helm Chart**, la gestion est entièrement transférée à ArgoCD. Par conséquent, l'exécution de la commande `helm ls` ne permettra pas d'afficher le **release** déployé, car il n'est plus géré par Helm.

Voici un exemple montrant comment créer deux applications ArgoCD :

1. Une qui déploie un **Helm Chart** depuis un dépôt Git.
2. Une autre qui déploie le **Helm Chart** Nginx depuis le dépôt Bitnami.

Après le déploiement, la commande `helm ls` confirme que les applications sont entièrement gérées par ArgoCD.

```bash
$ argocd app create random-shapes \
  --repo https://github.com/sidd-harth/test-cd.git \
  --path helm-chart \
  --helm-set replicaCount=2 \
  --helm-set color.circle=pink \
  --helm-set color.square=violet \
  --helm-set service.type=NodePort \
  --dest-namespace default \
  --dest-server https://kubernetes.default.svc
application 'random-shapes' created
```

```bash
$ argocd app create nginx \
  --repo https://charts.bitnami.com/bitnami \
  --helm-chart nginx \
  --revision 12.0.3 \
  --values-literal-file values.yaml \
  --dest-namespace default \
  --dest-server https://kubernetes.default.svc
application 'nginx' created
```

```bash
$ helm ls
NAME   NAMESPACE REVISION UPDATED STATUS CHART APP VERSION
```

Cet exemple illustre clairement les points suivants :

* Comment créer des applications ArgoCD en utilisant la CLI.
* Comment configurer les paramètres d'un **Helm Chart** lors du déploiement.
* Comment vérifier qu'après le déploiement, la gestion est assurée par ArgoCD et non par Helm.

#### Principaux Ressources et Références

| **Composant**   | **Description**                                                             | **Commande Exemple / Lien**                                       |
| --------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| ArgoCD CLI      | Utilisé pour créer et gérer les applications ArgoCD                         | Exemples de commande `argocd app create` ci-dessus                |
| Helm Package    | Simplifie l'installation et la gestion des applications Kubernetes          | [Documentation Helm](https://helm.sh/docs/)                       |
| Principe GitOps | Configuration déclarative et automatisation du déploiement des applications | [GitOps Kubernetes](https://www.weave.works/technologies/gitops/) |

!!! Warning
    Assurez-vous que vous avez les bonnes autorisations d'accès et que vos informations d'identification sont correctement configurées lorsque vous vous connectez à des dépôts privés. Une mauvaise configuration peut entraîner des échecs de déploiement.

---

### Déploiement d'applications multi-clusters
ArgoCD simplifie la gestion des déploiements multi-clusters en permettant de déployer des applications soit dans son propre cluster, soit sur des clusters externes. Dans ce guide, nous vous expliquerons comment configurer un cluster Kubernetes externe et déployer des applications sur plusieurs clusters à l’aide d'ArgoCD.

#### Vue d'ensemble

Avant de déployer des applications sur plusieurs clusters, vous devez disposer d'un cluster Kubernetes externe. ArgoCD intègre des clusters externes en lisant leurs détails d'identification depuis le fichier **kubeconfig**. Cela permet à ArgoCD de gérer les déploiements en dehors de son propre cluster.

#### Configuration du Cluster Externe

Commencez par mettre à jour votre fichier **kubeconfig** pour enregistrer votre cluster externe. Utilisez les commandes suivantes pour définir la configuration du cluster et des identifiants :

```bash
$ kubectl config set-cluster prod --server=https://1.2.3.4 --certificate-authority=prod.crt
Cluster "prod" set.
```

```bash
$ kubectl config set-credentials admin --client-certificate=admin.crt --client-key=admin.key
User "admin" set.
```

Après avoir défini le cluster externe dans votre **kubeconfig**, ajoutez-le à ArgoCD en référencant le nom de contexte approprié :

```bash
$ argocd cluster add <context-name>
```

!!! Avertissement
    Cette commande crée un compte de service sur le cluster externe avec un accès complet au niveau du cluster. Assurez-vous de comprendre les implications de sécurité avant de procéder.

Une fois que vous confirmez, ArgoCD crée automatiquement le compte de service, le rôle de cluster, et l'association du rôle de cluster, validant ainsi le cluster externe comme cible de déploiement.

#### Exemple détaillé

Voici un exemple complet illustrant toutes les étapes essentielles pour ajouter un cluster externe :

```bash
$ kubectl config set-cluster prod --server=https://1.2.3.4 --certificate-authority=prod.crt
Cluster "prod" set.

$ kubectl config set-credentials admin --client-certificate=admin.crt --client-key=admin.key
User "admin" set.

$ kubectl config set-context admin-prod --cluster=prod --user=admin --namespace=prod-app
Context "admin-prod" set.

$ argocd cluster add admin-prod
WARNING: This will create a service account `argocd-manager` on the cluster referenced by context `admin-prod` with full cluster level admin privileges. Do you want to continue [y/N]? y
INFO[0011] ServiceAccount "argocd-manager" created in namespace "kube-system"
INFO[0011] ClusterRole "argocd-manager-role" created
INFO[0011] ClusterRoleBinding "argocd-manager-role-binding" created
Cluster 'https://1.2.3.4' added

$ argocd cluster list
SERVER                                  NAME         VERSION  STATUS      MESSAGE   PROJECT
https://1.2.3.4                         admin-prod   1.21     Successful            <none>
https://kubernetes.default.svc          in-cluster   1.20     Successful            <none>
```

Vous pouvez vérifier la liste des clusters disponibles pour le déploiement en exécutant la commande `argocd cluster list`. Notez que les identifiants pour les clusters externes (ou serveurs API) sont stockés de manière sécurisée en tant que secrets dans le namespace ArgoCD.

---

## ArgoCD AdvancedAdmin

### **Gestion des utilisateurs RBAC dans ArgoCD**

Dans cette leçon, nous explorons comment ArgoCD met en œuvre le contrôle d'accès basé sur les rôles (RBAC) pour gérer l'accès à ses ressources de manière efficace. ArgoCD utilise des politiques définies en notation CSV, qui sont appliquées soit à des utilisateurs individuels, soit à des groupes SSO. Il est important de noter que les permissions RBAC pour les applications peuvent différer de celles appliquées à d'autres types de ressources.

#### Comment fonctionne le RBAC dans ArgoCD

Au cœur de la politique RBAC dans ArgoCD, on retrouve quatre composants :

- **Rôle**: Un ensemble de permissions.
- **Ressource**: La ressource cible, comme les clusters, les certificats, les applications, les dépôts ou les journaux.
- **Action**: L'opération autorisée (par exemple, obtenir, créer, mettre à jour, supprimer, synchroniser, ou remplacer).
- **Projet/Objet**: Pour les objets d'application, le chemin de la ressource est exprimé par le nom du projet suivi d'un slash et du nom de l'application.

!!! Note
    Les politiques RBAC personnalisées permettent un contrôle granulaire sur qui peut effectuer des actions spécifiques, garantissant que seuls les utilisateurs autorisés ont accès aux ressources sensibles.

#### Exemple : Création d'un rôle "Créer un cluster" personnalisé

L'exemple suivant montre comment configurer un rôle personnalisé nommé `createCluster` qui permet à un utilisateur de créer des clusters dans ArgoCD. Dans ce scénario, le rôle est attribué à un utilisateur nommé `jai` en patchant la configmap RBAC d'ArgoCD avec la politique appropriée.

```bash
$ kubectl -n argocd patch configmap argocd-rbac-cm \
--patch='{"data":{"policy.csv":"p, role:create-cluster, clusters, create, *, jai, role:create-cluster"}}'
configmap/argocd-rbac-cm patched
```

Dans cette configuration, le rôle `createCluster` est attribué à l'utilisateur `jai`, lui permettant de créer des clusters. Vous pouvez vérifier les permissions avec la commande `argocd account can-i` :

* Vérifier si `jai` peut créer des clusters renvoie "oui".
* Tenter de supprimer un cluster renvoie "non" car le rôle `createCluster` ne comprend pas la permission de suppression.

#### Exemple : Attribution d'un rôle au niveau du projet

Les rôles peuvent également être attribués au niveau du projet. Considérons un rôle personnalisé nommé `kia-admins`, qui accorde des droits de modification illimités pour toute application au sein du projet `kia-project`. Ce rôle est attribué à un utilisateur nommé `ali`. Lorsque `ali` tente de synchroniser les applications dans le projet `kia-project`, le système confirme les permissions avec une réponse "oui".

```bash
$ kubectl -n argocd patch configmap argocd-rbac-cm \
--patch='{"data":{"policy.csv":"p, role:create-cluster, clusters, create, *, jai, role:create-cluster"}}'
configmap/argocd-rbac-cm patched

$ argocd account can-i create clusters '*'
yes # Logged in as - jai

$ kubectl -n argocd patch configmap argocd-rbac-cm \
--patch='{"data":{"policy.csv":"p, role:kia-admins, applications, *, kia-project/*, allow, ali, role:kia-admins"}}'
configmap/argocd-rbac-cm patched

$ argocd account can-i delete clusters '*'
no # Logged in as - jai

$ argocd account can-i sync applications kia-project/*
yes # Logged in as - ali
```

!!! Warning
    Bien que l'utilisateur `ali` ait reçu des permissions au sein du projet `kia-project`, il n'est pas autorisé à synchroniser des applications dans d'autres projets.

#### Conclusion

Cette leçon a fourni un aperçu de la manière de configurer le RBAC dans ArgoCD pour garantir que seuls les utilisateurs correctement autorisés puissent effectuer des actions spécifiques sur diverses ressources. En définissant soigneusement des politiques à l'aide de la notation CSV, vous pouvez gérer efficacement l'accès aux clusters, aux applications et à d'autres composants critiques dans ArgoCD.

---

### Gestion des utilisateurs dans ArgoCD avec RBAC

Cet article explique comment gérer les utilisateurs dans ArgoCD, en se concentrant sur la gestion des utilisateurs locaux. Par défaut, ArgoCD inclut un utilisateur administrateur intégré avec un accès complet de super-utilisateur. Pour de meilleures pratiques de sécurité, il est recommandé d'utiliser le compte administrateur uniquement pour la configuration initiale, puis de le désactiver une fois que tous les utilisateurs nécessaires ont été ajoutés.

ArgoCD prend en charge deux types de comptes utilisateur :

- **Utilisateurs locaux**
- **Utilisateurs authentifiés via Single Sign-On (SSO)** (par exemple, via Okta ou des produits similaires)

Dans ce guide, nous nous concentrons sur la configuration des utilisateurs locaux.

!!! Important
    Il est recommandé de désactiver le compte administrateur par défaut après avoir configuré des comptes supplémentaires afin de minimiser les risques de sécurité.

#### Configuration des utilisateurs locaux

Les utilisateurs locaux dans ArgoCD sont gérés en mettant à jour le **ConfigMap**. Chaque utilisateur est défini avec des capacités associées, telles que la génération de clé API et l'accès à l'interface utilisateur. La capacité de clé API permet à un utilisateur de créer un **JSON Web Token** (JWT) pour les interactions API, tandis que la capacité de connexion permet l'accès à l'interface utilisateur.

Après avoir modifié le ConfigMap, votre liste d'utilisateurs pourrait ressembler à ceci :

```bash
$ argocd account list
NAME   ENABLED  CAPABILITIES
admin  true     login
jai    true     apiKey, login
ali    true     apiKey, login
```

Pour ajouter ou mettre à jour les comptes utilisateur, vous pouvez patcher le ConfigMap avec les commandes appropriées :

```bash
$ kubectl -n argocd patch configmap argocd-cm --patch='{"data":{"accounts.jai": "apiKey,login"}}'
configmap/argocd-cm patched

$ kubectl -n argocd patch configmap argocd-cm --patch='{"data":{"accounts.ali": "apiKey,login"}}'
configmap/argocd-cm patched
```

#### Mise à jour des mots de passe des utilisateurs

ArgoCD fournit des commandes CLI pour définir ou mettre à jour les mots de passe des utilisateurs. Lorsque vous êtes connecté en tant qu'administrateur, vous devez entrer le mot de passe actuel de l'administrateur pour changer le mot de passe d'un autre utilisateur. Notez que les nouveaux utilisateurs n'ont pas d'accès tant que leur mot de passe n'est pas configuré.

ArgoCD vient avec deux rôles prédéfinis :

* **Lecture seule** : Accorde aux utilisateurs un accès uniquement pour visualiser les ressources.
* **Administrateur** : Accorde aux utilisateurs un accès complet et illimité.

Par défaut, le compte administrateur se voit attribuer le rôle **administrateur**. Cependant, vous pouvez modifier cette attribution ou créer des rôles personnalisés en éditant le **ConfigMap RBAC** d'ArgoCD.

Par exemple, pour mettre à jour le mot de passe de l'utilisateur "jai", utilisez la commande suivante :

```bash
$ argocd account update-password --account jai
*** Entrez le mot de passe de l'utilisateur actuellement connecté (admin) :
*** Entrez le nouveau mot de passe pour l'utilisateur jai :
*** Confirmez le nouveau mot de passe pour l'utilisateur jai :
Mot de passe mis à jour
```

Alternativement, vous pouvez exécuter la mise à jour dans une seule commande :

```bash
$ argocd account update-password \
--account jai \
--new-password j€i_p@ssw0rd \
--current-password @dmin_p@$sword
Mot de passe mis à jour
```

#### Personnalisation des rôles

Le rôle **lecture seule** par défaut permet aux utilisateurs de visualiser toutes les ressources sans apporter de modifications. Pour attribuer des rôles personnalisés ou modifier les attributions de rôles, vous devez éditer le **ConfigMap RBAC** d'ArgoCD. En configurant ces paramètres, vous pouvez vous assurer que les utilisateurs sans mappages de rôles explicites se voient attribuer automatiquement un rôle **lecture seule** par défaut.

Pour une compréhension plus approfondie du contrôle d'accès basé sur les rôles (RBAC) dans ArgoCD et pour explorer des configurations détaillées, référez-vous à la **documentation officielle d'ArgoCD**.

!!! Note "Lectures supplémentaires"
    Pour plus d'informations sur la gestion sécurisée des utilisateurs et la configuration RBAC dans ArgoCD, explorez des ressources supplémentaires sur **RBAC dans Kubernetes** et les **meilleures pratiques en matière de sécurité cloud-native**.

---

### 