---
title: Comment Argo CD vérifie-t-il les changements dans mon dépôt Git ou Helm
date: 2025-12-03
categories:
  - Argo CD
tags:
  - Argo CD
#sources:
---

![](../../assets/images/argo/argo.svg)

## Introduction

Par défaut, ArgoCD vérifie les changements dans le dépôt Git ou Helm toutes les 3 minutes (120 secondes + 60 secondes de jitter).

Vous pouvez ajuster cette fréquence en modifiant les paramètres `timeout.reconciliation` et `timeout.reconciliation.jitter` dans la configMap [argocd-cm](https://github.com/argoproj/argo-cd/blob/master/docs/operator-manual/argocd-cm.yaml#L331-L348). Si des changements sont détectés dans le dépôt Git, Argo CD mettra à jour uniquement les applications pour lesquelles la synchronisation automatique (auto-sync) est activée.

<!-- more -->
---

??? Info "C'est quoi le jitter ?"

    Le "jitter" fait référence à une variation aléatoire dans le délai ou l'intervalle de temps. Dans le contexte d'Argo CD et du processus de polling (vérification des changements dans un dépôt Git ou Helm), le jitter est utilisé pour introduire un peu de variation dans le délai entre les vérifications successives, afin d'éviter un comportement trop prévisible.

    **Explication en détail**

    Dans le cas de Argo CD, par défaut, il vérifie les dépôts Git toutes les 3 minutes (180 secondes). Mais cette fréquence de 3 minutes est en fait composée de deux éléments:

      - 120 secondes (la valeur de base)
      - 60 secondes de jitter, qui est un délai aléatoire ajouté à chaque vérification.

    **Comment ça marche ?**

    Le jitter fait en sorte que l'intervalle de vérification ne soit pas exactement de 3 minutes à chaque fois, mais plutôt un intervalle aléatoire compris entre 120 secondes et 180 secondes (c'est-à-dire entre 2 et 3 minutes). L'idée derrière cela est d'empêcher plusieurs instances d'Argo CD qui fonctionnent en parallèle ou plusieurs clusters d'effectuer leurs vérifications au même moment, ce qui pourrait provoquer des pics de charge.

    Par exemple:  
    Si Argo CD commence avec un délai de 120 secondes, il va ajouter un délai aléatoire de 0 à 60 secondes (c'est le jitter), donc l'intervalle total entre les vérifications pourrait être:

      - 120 secondes + 30 secondes de jitter = 150 secondes (2 minutes 30 secondes)
      - 120 secondes + 60 secondes de jitter = 180 secondes (3 minutes)
      - 120 secondes + 10 secondes de jitter = 130 secondes (2 minutes 10 secondes)

    Cela permet de répartir de manière plus uniforme les vérifications dans le temps et d'éviter des situations où plusieurs vérifications se produisent simultanément, ce qui pourrait entraîner une surcharge du cluster ou des dépôts.

    **Pourquoi c'est utile ?**

    Répartition de la charge: Si plusieurs instances d'Argo CD ou d'autres services effectuent des pollings sur des dépôts Git à des intervalles réguliers (par exemple, toutes les 3 minutes), cela pourrait entraîner une surcharge du serveur Git ou du cluster si toutes ces instances se synchronisent exactement au même moment. Le jitter permet d'éviter cela en échelonnant les vérifications de manière aléatoire.

    Éviter le bruit de trafic: Le jitter empêche également de générer des pics de trafic ou des charges élevées sur le serveur, surtout quand il y a un grand nombre de dépôts ou d'applications à gérer.

    **Résumé**

    Le jitter est une variation aléatoire dans l'intervalle de temps entre les vérifications. Dans le cas d'Argo CD, cela signifie que la fréquence de vérification ne sera pas exactement la même à chaque fois, ce qui permet de mieux gérer les ressources et de réduire les risques de surcharge.

## Comment ajuster la fréquence de vérification du dépôt ?

Si vous définissez timeout.reconciliation à 0, Argo CD arrêtera le polling automatique des dépôts Git. Dans ce cas, vous devrez utiliser des méthodes alternatives, telles que les webhooks ou des synchronisations manuelles, pour déployer les applications.

!!! Info
    Le rafraîchissement du dépôt ne déclenche pas automatiquement la réconciliation des applications.  
    Pour que cela se produise, l'option de synchronisation automatique (auto-sync) doit être activée.

Pour ajuster cette fréquence, vous devez définir la variable d'environnement ARGOCD_RECOCILIATION_TIMEOUT dans le pod argocd-repo-server.  
Cette variable est liée à la clé timeout.reconciliation dans la configMap argocd-cm.

Voici la commande pour vérifier la variable d'environnement dans le pod argocd-repo-server:

```shell hl_lines="1"
kubectl -n argocd describe pods argocd-repo-server-57bdcb5898-g68nv | grep "RECONCILIATION"
  ARGOCD_RECONCILIATION_TIMEOUT: <set to the key 'timeout.reconciliation' of config map 'argocd-cm'> Optional: true
```

Ensuite, vous pouvez mettre à jour la configMap `argocd-cm` pour ajuster la valeur de `timeout.reconciliation` (par exemple, pour une fréquence de 1 heures):

```shell hl_lines="1"
kubectl -n argocd patch configmap argocd-cm -p '{"data": {"timeout.reconciliation": "1h"}}'
```

Enfin, redémarrez le pod argocd-repo-server pour appliquer les changements:

```shell hl_lines="1"
kubectl -n argocd rollout restart deployment argocd-repo-server
```

Cela configurera ArgoCD pour vérifier le dépôt Git toutes les heures. Si la synchronisation automatique est activée et qu’il n’y a pas de fenêtre de synchronisation en cours, la réconciliation du cluster se fera toutes les heures.

---

<div class="admonition abstract">
  <p class="admonition-title">Documentation</p>

```embed
url: https://argo-cd.readthedocs.io/en/stable/faq/#how-often-does-argo-cd-check-for-changes-to-my-git-or-helm-repository
desc: How often does Argo CD check for changes to my Git or Helm repository ?
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg
```

```embed
url: https://argo-cd.readthedocs.io/en/stable/operator-manual/high_availability/#application-sync-timeout-jitter
image: https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg
desc: Application Sync Timeout & Jitter
```
</div>