# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

# Maillage de services avec Istio

## Objectifs du chapitre et prérequis

## Présentation d'Istio

### Micro-services et mise en réseau de services

### Présentation d’Istio

Istio intègre plusieurs produits open source permettant de mettre en réseau un ensemble de services. Il assure une gestion du trafic, l'application de règle et la collecte de metriques

Par nature, Istio est conçu pour gérer la communication des micro-services d'une application. Il prend en charge de nombreuses opérations sans impacter les éléments existants:

* Collecte des temps de communication entre services
* Chiffrement de bout en bout entre services
* Traçabilité des appels entre services
* routage avancé (déploiment canari, blue/green deployment)
* mécanisme de gestion d'érreurs

### Principe de fonctionnement

## Installation d’Istio

### Configuration d'external-dns

### Dépôt des charts Istio

### Installation du chart istio-init

### Installation du chart Istio

#### Activation des tableaux de bord

#### Activation du mécanisme SDS

#### Configuration d'Istio

#### Installation d’Istio

### Configuration du gateway Istio

#### Présentation du mécanisme

#### Configuration du gateway

#### Génération du certificat

## Utilisation d’Istio

### Injection de pods dans le maillage de services

#### Installation d’istioctl

#### Injection du sidecar à l’aide d’istioctl

#### Injection du sidecar par annotation

#### Désactivation du sidecar par annotation

### Déploiement d’une application de test

#### Principe de l’exposition d’application avec Istio

#### Préparation du fichier de déploiement MailHog

#### Déclaration du service MailHog

#### Création du gateway

#### Création du service virtuel (VirtualService)

### Sécurisation des flux

#### Activation de Mutual TLS (mTLS)

La puissance d'istio est qu'une fois qu'un service y est intégré, il devient possible de changer à la volée le protocole de communication et faire appel à du Mutual TLS à la place d'une communication sans chiffrement.

TLS utilise des certificats pour vérifier l'athenticité de ses interlocuteurs. Dans le cas du protocole TLS simple, le client vérifie le serveur. De fait, n'importe qui peut donc communiquer avec le serveur

En plus de cette vérification, le serveur peut également s'assurer de l'identité du client. On parle dans ce cas d'authentification TLS mutuelle (ou également de SSL two-way)

Dans ce cas-là, le client est lui aussi soumis à une vérification pour interdire les communications externes non sollicités.

L'activiation de ce mécanisme se fait à l'aide de déclaration d'objet DestinationRule dans lequel est spécifié:

* Le champ ``host`` indiquant l'entrée à protéger
* Le champ ``trafficPolicy`` indiquant le mode souhaité

.. note::
    Pour activer l'utilisation du protocole mTLS sur le service XXX du namespace XXX, déclarez le cotenue suivant:

    .. code-block::

        apiVersion: networking.istio.io/v1alpha3
        kind: DestinationRule
        metadata:
          name: xxx
          namespace: xxx
        spec:
          host: ratings.prod.svc.cluster.local
          trafficPolicy:
            tls:
              mode: ISTIO_MUTUAL


#### Consultation des polices du service MailHog

#### Forcer l’utilisation de mTLS

## Tableaux de bord

### Présentation des différentes briques

### Interface Kiali

### Interface Grafana

### Interface Jaeger
