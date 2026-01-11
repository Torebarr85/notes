
+++
title = "Kubernetes: misha CKA - HELM"
date = 2025-12-30
draft = false
tags = ["kubernetes"]
+++


# HELM - TL;DR: Helm vs Kubectl

Invece di scrivere 10 file YAML manualmente
↓
Usi 1 comando Helm che installa tutto


```bash
# Senza Helm
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f configmap.yaml
# ... 10 file YAML

# Con Helm
helm install my-app bitnami/wordpress
# Fine! 1 comando
```

# install helm in locale o sulla VM
- !Helm non runna sul cluster ma sul computer e poi add repositories to helm
- quando usi il comand helm si connette al currently active K8S cluster in the current context
- helm fa azioni sul cluster al posto tuo (under the hood usa kubectl commands)
- la best practice però è che sia gitOps che usa helm

#### macOS
brew install helm

#### Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/install-helm.sh | bash



# Creare un chart personalizzato
```bash
# Genera struttura base
helm create my-chart

# Struttura creata:
# my-chart/
# ├── Chart.yaml        # metadata
# ├── values.yaml       # valori default
# ├── templates/        # YAML con variabili
# └── charts/           # dipendenze

folder: templates
values.yaml -> contiene i default values e tutte le cose che puoi passare es. replicaCount: 3
chart.yaml
``` 




# esempio deploy a set of resources with helm:

# 1. Aggiungi repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 2. Crea namespace
kubectl create namespace wordpress

# 3. Crea values.yaml
```bash
cat <<EOF > wordpress-values.yaml
wordpressUsername: admin
wordpressPassword: admin123
wordpressEmail: admin@example.com

service:
  type: LoadBalancer

persistence:
  enabled: true
  size: 10Gi

mariadb:
  auth:
    rootPassword: rootpass
    database: wordpress
  primary:
    persistence:
      enabled: true
      size: 8Gi
EOF
```

# 4. Installa
helm install my-wordpress bitnami/wordpress \
  -n wordpress \
  -f wordpress-values.yaml

# 5. Vedi lo status
helm status my-wordpress -n wordpress

# 6. Prendi la password (se generata random)
kubectl get secret my-wordpress -n wordpress -o jsonpath="{.data.wordpress-password}" | base64 -d

# 7. Accedi (se LoadBalancer)
kubectl get svc -n wordpress
# Vai su EXTERNAL-IP

