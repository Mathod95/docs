```yaml linenums="1" title="Chart.yaml"
apiVersion: v2 #(1)!
name: reloader-wrapper #(2)!
description: Enterprise wrapper for Stakater Reloader with monitoring and security #(3)!
type: application #(4)!
version: 1.0.0 #(5)!
appVersion: "v1.4.11" #(6)! 
maintainers: #(7)!
  - name: Mathias FELIX
    email: mathias.felix@mathod.io

dependencies:
  - name: reloader #(8)!
    version: 2.2.6 #(9)!
    repository: https://stakater.github.io/stakater-charts #(10)!

sources: 
  - https://github.com/stakater/Reloader #(11)!
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

!!! info "INFORMATION" 
    Le fichier Chart.yaml suit le [schéma officiel Helm](https://helm.sh/docs/topics/charts/#the-chartyaml-file), qui définit les champs autorisés.

!!! Tip "BEST PRACTICE"

    Utiliser un wrapper Helm chart centralise les configurations et évite de modifier chaque chart individuellement. Vous pouvez définir des valeurs par défaut propres à votre organisation et synchroniser automatiquement tous les clusters, simplifiant la maintenance et réduisant les erreurs.