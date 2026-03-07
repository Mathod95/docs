---
title: HELM
#status: draft
hide:
  - toc
---

<p align="center">
  <a href="https://github.com/helm/helm">
    <img src="https://opengraph.githubassets.com/Mathod/helm/helm" />
  </a>
</p>

---

> This course explores how Helm simplifies deploying and managing applications on Kubernetes, covering installation, architecture, and advanced features like charts and functions.

## Introduction

Kubernetes has surged in popularity in recent years. Several Kubernetes resources, such as pods, services, deployments, and replica sets, must be defined and managed when deploying an application on Kubernetes. Each of these necessitates the creation of a set of YAML manifest files. Maintaining multiple manifest files for each of these resources becomes problematic in the context of complicated application deployment. Furthermore, generating manifest files and supplying configuration options externally might be critical in allowing deployments to be customized. Other essential considerations include dependency management and version control.

This is where Helm comes to the rescue.

Helm is a Kubernetes package manager similar to NPM or YARN. It’s not only a Package Manager, though; it’s also a Kubernetes Deployment Management. To put it another way, instead of needing to declare numerous Kubernetes resources to deploy an application, Helm allows you to simply execute a few commands in the terminal and press enter, and you’re done!

Helm is crucial in automating the process of installing, configuring, and upgrading complicated Kubernetes applications in this case. Helm employs a chart-based packing system. A chart is a group of files that explain a set of Kubernetes resources that are connected.

## Ce que vous apprendrez:

In this course, you will discover: / In this course, you will learn about the following:

- Les bases de Helm, y compris les procédures d'installation et un guide de démarrage rapide.
- L'architecture détaillée et les composants principaux de Helm, tels que les charts, les dépôts, les releases et les révisions.
- Qu'est-ce que Helm
- Installation et configuration de Helm
- Helm2 vs Helm3
- Architecture de Helm
- Tout sur les charts Helm
- Gestion du cycle de vie avec Helm
- Fonctions
- Pipelines
- Conditionnelles
- Blocs With
- Ranges
- Modèles nommés
- Hooks de chart
- Packaging et signature des charts

## Prérequis
  - Des connaissances de base en Kubernetes sont requises.
  - Des connaissances en YAML sont requises.

---
!!! abstract "Links and References"
    - https://github.com/helm/helm