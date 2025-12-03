```yaml
apiVersion: v2
name: crossplane
description: A Helm chart for Crossplane
type: application
version: "0.1.0" #(1)!
appVersion: "2.1.1" #(2)!

dependencies:
  - name: crossplane
    version: "2.1.1"
    repository: "https://charts.crossplane.io/stable"
```

  1.  **REQUIRED**
  
      **version**: La version de ton manifest Chart.yaml.  
      
  2.  **OPTIONAL**
  
      **appVersion**: La version de l'application que tu déploie.

!!! Tip "Best practice recommandation"

    Utiliser un wrapper Helm chart centralise les configurations et évite de modifier chaque chart individuellement. Vous pouvez définir des valeurs par défaut propres à votre organisation et synchroniser automatiquement tous les clusters, simplifiant la maintenance et réduisant les erreurs.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: crossplane
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "10"
spec:
  project: management
  destination:
    name: management #(1)!
    namespace: crossplane-system
  source:
    repoURL: "https://gitea.mathod.fr/mathod/argocd.git"
    targetRevision: HEAD
    path: "apps/crossplane"
    directory:
      recurse: true
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

  1.  **name** fait référence à un cluster enregistré dans ArgoCD via `argocd cluster add`.

      Sinon utiliser le champ **server**