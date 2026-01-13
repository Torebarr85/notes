+++
title = "CI/CD vs GitOps"
date = 2026-01-13
draft = false
tags = ["cicd"]
+++

# CI/CD vs GitOps


🎯 La Vera Distinzione
### Approccio 1: CI/CD Tradizionale (Push-based)
GitLab CI Pipeline:
1. Build image
2. Test
3. Push to registry
4. kubectl apply -f deployment.yaml  ← Deploy diretto
   
* Pro:  Tutto in un tool
* Contro: La pipeline "pusha" verso Kubernetes (accesso diretto necessario)

### Approccio 2: CI/CD + GitOps (Pull-based)
GitLab CI Pipeline:
1. Build image
2. Test  
3. Push to registry
4. Update deployment.yaml in Git  ← Stop qui

ArgoCD (separato):
1. Watcha Git repo
2. Vede cambio in deployment.yaml
3. Applica su Kubernetes  ← Deploy automatico

* Pro: Separazione ruoli, Kubernetes non esposto alla pipeline
* Contro: Due tool da gestire

nel ci/cd moderno sono tools che lavorano in **fasi diverse** della pipeline. 

```bash
CI/CD:
Jenkins / GitLab CI / GitHub Actions

GITOPS:
ArgoCD / Flux
```
Ecco lo schema:

## 🔄 La Pipeline Completa

```
1. CODE PUSH (Developer)
         ↓
2. CI/CD TOOL (Build & Test)  ← Jenkins / GitLab CI / GitHub Actions
         ↓
3. ARTIFACT (Docker Image)
         ↓
4. GitOps TOOL (Deploy)       ← ArgoCD / Flux
         ↓
5. KUBERNETES (Running App)
```

## 📦 I Ruoli Specifici

### **Jenkins / GitLab CI / GitHub Actions**
**Ruolo:** CI/CD Engine (Continuous Integration/Delivery)

**Cosa fanno:**
- Triggano quando fai commit/push
- Eseguono test automatici
- Buildano la Docker image
- Pushano l'immagine su registry (ECR, Docker Hub)
- **STOP QUI** (o al massimo fanno kubectl apply manuale)

**Esempio pratico:**
```yaml
# GitLab CI
stages:
  - build
  - test
  - push

build-image:
  script:
    - docker build -t myapp:v1.2 .
    - docker push myapp:v1.2
```

### **ArgoCD / Flux**
**Ruolo:** GitOps Engine (Continuous Deployment)

**Cosa fanno:**
- Watchano un Git repo con i **manifest Kubernetes**
- Comparano stato desiderato (Git) vs stato reale (Cluster)
- Applicano automaticamente le modifiche
- **Mantengono sincronizzato** Git → Kubernetes

**Esempio pratico:**
```yaml
# Git repo watched by ArgoCD
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:v1.2  # ArgoCD vede questo cambio e deploya
```

## 🔗 Come Lavorano Insieme (Setup Moderno)

**Workflow completo:**

1. Developer fa commit su `main`
2. **GitLab CI** si triggera:
   - Builda immagine `myapp:v1.2`
   - Pusha su Docker Registry
   - **Aggiorna** il file `deployment.yaml` in Git con nuova image tag
3. **ArgoCD** detecta il cambio in Git:
   - Vede `image: myapp:v1.2` (prima era v1.1)
   - Applica il cambio su Kubernetes
   - App aggiornata ✅

## 🆚 Jenkins vs GitLab CI vs GitHub Actions

**Sono COMPETITOR tra loro** (fanno la stessa cosa):

| Tool | Pro | Contro |
|------|-----|--------|
| **Jenkins** | Flessibile, plugin infiniti | Vecchio, complesso da gestire |
| **GitLab CI** | Integrato in GitLab, YAML semplice | Devi usare GitLab |
| **GitHub Actions** | Integrato GitHub, marketplace | Devi usare GitHub |

 
 
 
 