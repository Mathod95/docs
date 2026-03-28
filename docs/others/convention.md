---
icon: lucide/book-check
title: CONVENTION
---

<!--
# Comment lire cette documentation

Cette documentation couvre un large spectre de sujets DevSecOps. Pour en tirer le meilleur parti, il est utile de comprendre comment elle est organisée et comment l'aborder selon votre profil et vos objectifs.

## Pourquoi cette documentation existe

Ce site existe pour une raison simple : réduire l'écart entre "j'ai entendu parler de DevSecOps" et "je sais l'appliquer concrètement". L'objectif n'est pas de collecter des tutoriels, mais de construire une compréhension solide des principes avant de manipuler les outils.

La sécurité n'est pas une section à part : c'est un fil conducteur. Chaque guide intègre les considérations de sécurité dès le départ, pas comme un ajout tardif. Vous apprendrez à déployer, automatiser et opérer des systèmes en tenant compte des risques dès la conception.

## À qui s'adresse cette documentation

**Vous découvrez le domaine.** Les termes comme "CI/CD", "conteneur" ou "infrastructure as code" sont encore flous. Cette documentation vous donne le vocabulaire, les concepts de base et une progression logique. Vous n'avez pas besoin de tout lire : commencez par les fondamentaux, puis explorez selon vos besoins.

**Vous savez coder, mais l'environnement d'exécution reste une boîte noire.** Vous voulez comprendre ce qui se passe après le `git push`. Ici, vous trouverez les ponts entre le code et l'infrastructure : conteneurisation, pipelines, déploiement automatisé.

**Vous gérez des systèmes, mais la sécurité reste un sujet à part, traité "quand on a le temps".** Cette documentation vous montre comment intégrer la sécurité dans vos pratiques quotidiennes : durcissement, analyse, détection, sans devenir expert en pentesting.

**Vous connaissez le sujet.** Vous cherchez une procédure précise, une commande, un rappel. Utilisez la recherche ou le glossaire.

## Comment est organisée la documentation

La documentation est organisée en sections thématiques. Chacune répond à un besoin spécifique :

- **Fondamentaux** — Poser les bases : vocabulaire, principes, modèles mentaux. À lire en premier si vous débutez.
- **Administration** — Gérer des systèmes Linux au quotidien : services, réseaux, utilisateurs. Le socle technique.
- **Conteneurisation** — Isoler, packager, orchestrer des applications.
- **Infrastructure as Code** — Automatiser la création et la configuration d'infrastructure. Reproductibilité et versionnement.
- **Pipelines CI/CD** — Automatiser les tests, les builds, les déploiements. Le cœur de l'intégration continue.
- **Sécurité** — Durcir, analyser, détecter. Intégrer la sécurité à chaque étape.
- **Observabilité** — Comprendre ce qui se passe en production : logs, métriques, alertes.

Chaque section peut être lue indépendamment, mais des liens internes connectent les sujets liés.

## Navigation

La navigation est segmenter en catégories:

  - **KUBERNETES**
  - **ARGO**
  - **AWS**
  - **OBSERVABILITY**
  - **APPLICATIONS**
  - **LINUX**
  - **DEVOPS**
  - **HOMELAB:** Monter son lab personnel
  - **INFRASTRUCTURE**
  - **OTHERS:** Regroupement de page non catégoriser
    - **AWESOME:** Une page regroupement des repository git
    - **CONVENTION:** 
    - **BLOG:** Articles et actualités
    - **TAGS:** 
    - **GLOSSAIRE:** les définitions de tous les termes techniques Terminology et définitions
    - **CONTACT**

Les liens vers d'autres pages utilisent des chemins absolus `/docs/...`. Ils permettent de naviguer entre sujets connexes sans perdre le fil.

## Comment contribuer

Vous avez repéré une erreur, une information obsolète ou vous souhaitez proposer une amélioration ? Rejoignez le Discord pour échanger et contribuer.

## À retenir

- Commencez par comprendre avant d'outiller — les concepts d'abord, les outils ensuite
- La documentation est modulaire — chaque guide peut être lu indépendamment
- Adaptez votre lecture à votre profil — les points d'entrée diffèrent selon votre expérience
- La sécurité est intégrée, pas ajoutée — c'est un fil conducteur, pas une section optionnelle

## Ce que vous ne trouverez PAS ici
Pas de magie : on n’installe pas Kubernetes en 5 minutes sans comprendre ce qu’on fait
Pas de copier-coller aveugle : chaque commande est expliquée (pourquoi on la tape, comment vérifier qu’elle marche)
Pas de listes en l’air : les bonnes pratiques viennent avec des exemples concrets
Pas tout sur tout : je documente ce que j’utilise vraiment, pas une encyclopédie
Pas de théorie sans pratique : chaque concept a un exemple réel
-->
---

## Navigation

La navigation est segmenter en catégories:

  - **KUBERNETES**
  - **ARGO**
  - **AWS**
  - **OBSERVABILITY**
  - **APPLICATIONS**
  - **LINUX**
  - **DEVOPS**
  - **HOMELAB:** Monter son lab personnel
  - **INFRASTRUCTURE**
  - **OTHERS:** Regroupement de page non catégoriser
    - **AWESOME:** Une page regroupement des repository git
    - **CONVENTION:** 
    - **BLOG:** Articles et actualités
    - **TAGS:** 
    - **GLOSSAIRE:** les définitions de tous les termes techniques Terminology et définitions
    - **CONTACT**

## Authoring

### Barticks

Tous ce qui fields/values dans du texte est sous `barticks`

### Bold

Tous ce qui est nom d'application, acronyme

### Admonition

The following admonition types are available in Zensical. The default is `note`.

!!! note

    Pour du contexte, historique, non essentiel

!!! abstract

    Pour un résumé / introduction

!!! info

    Pour une info utile dans le flow principal

!!! tip

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! success

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! question

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! warning

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! failure

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! danger

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! bug

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! example

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

!!! quote

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
    euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
    purus auctor massa, nec semper lorem quam in massa.

### Code blocks


Les blocs de code
Les commandes à taper sont dans des blocs gris. Le langage est indiqué en haut (bash, yaml, python…).

Fenêtre de terminal

systemctl is-active --quiet nginx && echo "OK" || echo "Service arrêté"

Important : ne copiez pas les commandes sans lire ce qui est écrit autour. Le texte explique pourquoi on tape cette commande et comment vérifier qu’elle a marché.

2 types de code blocks

#### Terminal
```bash hl_lines="1"
kind create cluster
Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.35.0) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂
```

#### Fichier
```yaml linenums="1" title="pod.yaml"
apiVersion: v1
kind: Pod
metadata:
  name: mon-pod
  labels:
    app: mon-app
spec:
  containers:
  - name: mon-container
    image: nginx:latest
    ports:
    - containerPort: 80
```