
+++
title = "Progetto Demo CI/CD + GitOps + helm"
date = 2026-01-15
draft = false
tags = ["cicd","argocd","helm"]
+++

* Se l’obiettivo è imparare **GitOps in modo realistico**, usare Helm ha senso.
* **ArgoCD supporta Helm nativamente**, senza workaround.
* Modifichi il `values.yaml` → fai commit → **ArgoCD esegue automaticamente l’upgrade**.
* Il flusso è **identico a quello usato in produzione**.
* Con YAML plain otterresti lo stesso risultato, ma **meno aderente alla realtà**.



# A. Setup Base ArgoCD su Rancher Desktop

## **1. Verifica ambiente**
```bash
kubectl cluster-info          # Verifica cluster attivo
helm version                  # Controlla Helm installato
kubectl get nodes             # Stato nodi K8s
```

## **2. Struttura progetto**
```bash
├── app/
│   └── index.html          # Il tuo "hello world"
├── docker/
│   └── Dockerfile          # Build dell'immagine
├── helm-chart
│   └── templates
├── infra
│   ├── argocd
│   └── namespaces
│       ├── argocd.yaml
│       └── my-gitops-demo.yaml
└── README.md

```

## **3. Namespace**
```bash
kubectl create namespace my-gitops-demo --dry-run=client -o yaml > infra/namespaces/my-gitops-demo.yaml
kubectl create namespace argocd --dry-run=client -o yaml > infra/namespaces/argocd.yaml
kubectl apply -f infra/namespaces/    # Crea i namespace
```

## **4. Installazione ArgoCD**
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get pods -n argocd             # Verifica pod running  
```

```bash
# 1. Esponi ArgoCD in locale (tieni aperto il terminale)
kubectl port-forward services/argocd-server -n argocd 8080:443

# 2. In un ALTRO terminale, recupera password admin
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode
```
## **Risultato** vai su localhost:8080 e accedi
ArgoCD installato e funzionante nel namespace dedicato. Pronto per accesso UI.
user: admin
pwd: pwd decoded
## 



---
# B Creiamo l'applicazione + Dockerfile e Build Immagine Custom

### creare Il file app/index.html (la nostra app)
```html
<!DOCTYPE html>
<html>
<head><title>GitOps Demo</title></head>
<body>
  <h1>Hello GitOps! v1.0</h1>
</body>
</html>
```

### containerizziamola:

## **8. Creazione Dockerfile**
File `docker/Dockerfile`:
```dockerfile
FROM nginx:alpine
COPY ../app/index.html /usr/share/nginx/html/
EXPOSE 80
```

## **9. Build immagine locale**
```bash
docker build -t my-gitops-app:v1.0 -f docker/Dockerfile .  # Build immagine con tag v1.0
docker images | grep my-gitops-app                          # Verifica immagine creata
```

# Spiegazione comando

```bash
docker build -t my-gitops-app:v1.0 -f docker/Dockerfile .
```

--- 




# C: Creazione Helm Chart

## **6. Setup Helm chart**
```bash
helm create helm-chart                # Genera struttura chart
cd helm-chart/templates/
rm -f ingress.yaml hpa.yaml serviceaccount.yaml httproute.yaml  # Rimuove file inutili
rm -rf tests/
```

## **7. Configurazione minimal per immagine locale***
modifica `values.yaml` con:
```yaml
replicaCount: 1
image:
  repository: my-cats-app
  tag: v1.0
  pullPolicy: Never  # Usa immagine locale senza pull da registry
service:
  type: NodePort # cosi posso accedervi da browser locale
  port: 80
  nodePort: 30080
```

## **Perché imagePullPolicy: Never**
K8s usa l'immagine dalla cache locale di Docker invece di cercarla su registry remoto (perfetto per dev locale).

## deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "helm-chart.fullname" . }}
  labels:
    {{- include "helm-chart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "helm-chart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "helm-chart.labels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
```

## service: aggiunta nodePort
```yaml
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
      {{- if eq .Values.service.type "NodePort" }}
      nodePort: {{ .Values.service.nodePort }}
      {{- end }}
  selector:
    {{- include "helm-chart.selectorLabels" . | nindent 4 }}
```
---




# D Test deploy manuale**
```bash
helm install my-app ./helm-chart --namespace my-gitops-demo  # Installa chart
kubectl get pods -n my-gitops-demo                           # Verifica pod running
kubectl get svc -n my-gitops-demo                            # Verifica service NodePort
```

## **14. Verifica applicazione**
Browser: `http://localhost:30080` → Deve mostrare "Hello GitOps! v1.0"

---

**Risultato:** App deployata manualmente con Helm. Prossimo step: collegare ArgoCD per automatizzare.























