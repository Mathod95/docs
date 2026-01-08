![](../assets/images/kubernetes/kubernetes.svg)


# Voir les labels du deployment knative-operator
kubectl get deployment knative-operator -n knative-operator --show-labels

# Voir les labels du deployment operator-webhook
kubectl get deployment operator-webhook -n knative-operator --show-labels

# Voir les deux en même temps avec leurs labels
kubectl get deployments -n knative-operator --show-labels

# Plus de détails en format YAML pour voir tous les labels
kubectl get deployment knative-operator -n knative-operator -o yaml | grep -A 5 "labels:"
kubectl get deployment operator-webhook -n knative-operator -o yaml | grep -A 5 "labels:"

# Format tableau avec les labels spécifiques
kubectl get deployments -n knative-operator \
  -o custom-columns=NAME:.metadata.name,APP:.metadata.labels.app,ENV:.metadata.labels.environment

# Voir si les labels app et environment existent
kubectl get deployments -n knative-operator -o json | jq '.items[].metadata.labels | {name: .name, app: .app, environment: .environment}'


# Version plus simple pour voir tous les labels
kubectl get deployments -n knative-operator -o yaml | yq '.items[].metadata | {"name": .name, "labels": .labels}'