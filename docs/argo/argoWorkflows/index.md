---
title: Argo Workflows
status: draft
hide:
  - toc
---

<p align="center">
  <a href="https://github.com/argoproj/argo-workflows">
    <img src="https://opengraph.githubassets.com/Mathod/argoproj/argo-workflows" />
  </a>
</p>

> Dans ce chapitre, nous explorerons en détail **Argo Workflows**, une extension d’**Argo**, un outil GitOps populaire conçu pour la livraison continue déclarative des applications Kubernetes.

## Aperçu du chapitre et objectifs

Argo Workflows vous permet de définir et de gérer des workflows complexes sous forme de code, offrant un moyen d’orchestrer et d’automatiser des processus multi-étapes dans Kubernetes.

À la fin de ce chapitre, vous devriez être capable de comprendre les bases et l’architecture d’Argo Workflows. Cela implique de comprendre ses composants clés, leur interaction et les concepts fondamentaux qui régissent l’exécution des workflows. Voici les objectifs d’apprentissage pour acquérir une maîtrise d’Argo Workflows :

- Définir et expliquer la structure d’un workflow Argo.
- Reconnaître les éléments clés tels que les **métadonnées**, le **spec**, le **point d’entrée (entrypoint)** et les **templates**.
- Comprendre le rôle des templates dans les workflows.
- Identifier et expliquer les principaux composants d’Argo Workflows, y compris le **Workflow Controller** et l’interface utilisateur (UI).
- Comprendre comment Argo Workflows planifie et exécute les tâches.
- Approfondir les responsabilités du **Workflow Controller**.

---

## TOC

- [ ] [Argo Events Architecture](https://notes.kodekloud.com/docs/Prep-Course-Certified-Argo-Project-Associate-CAPA/Argo-Events/Argo-Events-Architecture/page)
- [ ] [Event Source](https://notes.kodekloud.com/docs/Prep-Course-Certified-Argo-Project-Associate-CAPA/Argo-Events/Event-Source/page)
- [ ] [Event Bus](https://notes.kodekloud.com/docs/Prep-Course-Certified-Argo-Project-Associate-CAPA/Argo-Events/Event-Bus/page)
- [ ] [Sensor](https://notes.kodekloud.com/docs/Prep-Course-Certified-Argo-Project-Associate-CAPA/Argo-Events/Sensor/page)
- [ ] []()
- [ ] []()

---

<div class="grid cards" markdown>

-   :material-apps:{ .lg .middle } __Kubernetes__

    ---

    ![](https://raw.githubusercontent.com/cncf/artwork/3e09078b447395d14093989e8718bf3b115b5101/projects/kubernetes/icon/color/kubernetes-icon-color.svg){ align=left width="50" }

    Lorem ipsum dolor sit amet, consectetur adipiscing

    [:octicons-chevron-right-24: Learning Path](../kubernetes/index.md)

-   :material-apps:{ .lg .middle } __Argo__

    ---

    ![](https://raw.githubusercontent.com/cncf/artwork/9e203aa38643bbf0fcb081dbaa80abbd0f6f0698/projects/argo/icon/color/argo-icon-color.svg){ align=left width="50" }

    Lorem ipsum dolor sit amet, consectetur adipiscing

    [:octicons-chevron-right-24: Learning Path](#)
</div>

---
!!! abstract "Liens et références"
    - [Argo Workflow Official Repository](https://github.com/argoproj/argo-workflows)
    - [Argo Workflow Official Documentation](https://argoproj.github.io/argo-workflows/)
    - [Sécurité et RBAC](https://argoproj.github.io/argo-workflows/security/)
    - [Argo CLI Documentaiton](https://argo-workflows.readthedocs.io/en/latest/cli/argo/)