
+++
title = "Progetto Demo CI/CD + GitOps + helm part 2"
date = 2026-01-15
draft = false
tags = ["cicd","argocd","helm"]
+++


# parte 2 goal: Setup Pipeline + GitHub Actions + GitOps

---

## **Flusso completo:**

```
[Tu]
  ↓ modifichi index.html + git push
[GitHub Actions - CI]
  ↓ build docker img + push img su Docker Hub
  ↓ aggiorna helm-chart/values.yaml su git Repository con nuovo tag
  ↓ commit automatico
[Git Repository]
  ↓ ArgoCD rileva cambio
[ArgoCD - GitOps]
  ↓ helm upgrade automatico
[Kubernetes]
  ↓ nuova versione deployed
[http://localhost:30080]
  ✅ Vedi modifiche live
```

---

# Overview: cosa stiamo costruendo

---

### **Fase 1: CI Pipeline (GitHub Actions)**
**Cosa fa:**
- Quando fai `git push`
- GitHub Actions parte automaticamente
- Build immagine Docker
- Push su Docker Hub con tag univoco (es: `v1.0.1`, `abc123`)
- **Modifica automaticamente** `values.yaml` nel repo con nuovo tag
- Commit automatico della modifica

**Risultato:** Ogni push genera nuova immagine + aggiorna repo Git

---

### **Fase 2: GitOps (ArgoCD)**
**Cosa fa:**
- ArgoCD "osserva" la cartella `helm-chart/` su GitHub
- Quando vede che `values.yaml` è cambiato (nuovo tag immagine)
- **Automaticamente** fa `helm upgrade` nel cluster
- Deploy della nuova versione

**Risultato:** Quando values.yaml cambia → deploy automatico


## **Prossimi step concreti:**

1. Configuriamo **GitHub Secrets** (password Docker Hub)
2. Creiamo **`.github/workflows/ci.yaml`** (pipeline)
3. Configuriamo **ArgoCD Application** (watcha il repo)

---



# 1. github secrets

# Step 13: GitHub Secrets

## **Cosa sono i GitHub Secrets?**

**Problema:** 
- La pipeline deve fare login su Docker Hub
- NON puoi mettere username/password direttamente nel codice (pubblico su GitHub!)

**Soluzione:**
- GitHub Secrets = variabili cifrate salvate nel tuo repo
- Accessibili solo dalla pipeline
- Non visibili nel codice

---

## **Secrets da configurare:**

1. **DOCKER_USERNAME**: `salvatorebarretta14`
2. **DOCKER_TOKEN**: Access token Docker Hub (più sicuro della password)

---

## **Procedura:**

### **1. Crea Docker Access Token**

- Vai su https://hub.docker.com/settings/security
- Click **"New Access Token"**
- Description: `GitHub Actions`
- Permissions: **Read & Write**
- Copia il token (lo vedi solo una volta!)

### **2. Aggiungi secrets su GitHub**

- Vai su: `https://github.com/Torebarr85/my-gitops-demo/settings/secrets/actions`
- Click **"New repository secret"**

**Secret 1:**
- Name: `DOCKER_USERNAME`
- Value: `sal******14`

**Secret 2:**
- Name: `DOCKER_TOKEN`
- Value: [token copiato prima]

---

## **Come li usa la pipeline:**

```yaml
# Nella pipeline (prossimo step)
- name: Login Docker Hub
  run: |
    echo ${{ secrets.DOCKER_TOKEN }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
```

Sintassi `${{ secrets.NOME }}` → GitHub inietta il valore cifrato

---


# 2. crea pipeline github ci.yaml

 
# ** Crea `.github/workflows/ci.yaml`: **

```yaml
name: Build and Deploy

# Quando parte la pipeline
on:
  push:
    branches:
      - master  # Solo su push a master
    paths:
      - 'app/**'  # Solo se cambia qualcosa in app/

# Variabili globali
env:
  IMAGE_NAME: salvatorebarretta14/my-cats-app
  REGISTRY: docker.io

jobs:
  build-and-push:
    runs-on: ubuntu-latest  # Macchina virtuale GitHub
    
    steps:
      # 1. Checkout del codice
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}  # Per fare commit dopo
      
      # 2. Setup Docker Buildx (build avanzato)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      # 3. Login su Docker Hub
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
      
      # 4. Genera tag univoco (SHA commit breve)
      - name: Generate image tag
        id: tag
        run: echo "IMAGE_TAG=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
      
      # 5. Build e push immagine Docker
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/Dockerfile
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:${{ steps.tag.outputs.IMAGE_TAG }}
            ${{ env.IMAGE_NAME }}:latest
      
      # 6. Aggiorna values.yaml con nuovo tag
      - name: Update Helm values
        run: |
          sed -i "s/tag: .*/tag: ${{ steps.tag.outputs.IMAGE_TAG }}/" helm-chart/values.yaml
          sed -i "s|repository: .*|repository: ${{ env.IMAGE_NAME }}|" helm-chart/values.yaml
      
      # 7. Commit e push modifiche values.yaml
      - name: Commit updated values
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          git add helm-chart/values.yaml
          git commit -m "Update image tag to ${{ steps.tag.outputs.IMAGE_TAG }}"
          git push
```

---

## **Cosa fa ogni step:**

1. **Checkout**: Scarica il codice del repo
2. **Buildx**: Setup tool Docker avanzato
3. **Login**: Autentica su Docker Hub con i secrets
4. **Tag**: Crea tag univoco dal commit SHA (es: `abc1234`)
5. **Build/Push**: Build immagine + push su Docker Hub con 2 tag (`abc1234` + `latest`)
6. **Update values**: Modifica `values.yaml` con nuovo tag via `sed`
7. **Commit**: Pusha il values.yaml aggiornato su GitHub

---

## **Note importanti:**

- `IMAGE_NAME` deve essere `tuo-username/nome-repo` Docker Hub
- Tag = SHA commit → ogni commit = immagine unica
- `latest` tag = sempre ultima versione

---


Ora **prima di fare commit e push**, dobbiamo:

---

## **1. Aggiorna values.yaml per Docker Hub**

Apri `helm-chart/values.yaml` e modifica:

```yaml
image:
  repository: salvatorebarretta14/my-cats-app  # Era my-cats-app
  tag: latest  # Per ora latest, poi la pipeline aggiornerà
  pullPolicy: IfNotPresent  # Era Never, ora pull da Docker Hub
```

**Perché:**
- `pullPolicy: Never` funziona solo con immagini locali
- Ora K8s deve pullare da Docker Hub

---

## **2. Rimuovi deployment Helm attuale**

```bash
helm uninstall my-cats-app -n my-gitops-demo
```

**Perché:** ArgoCD lo gestirà, non più Helm manuale

---

## **3. Commit e push tutto**

```bash
git add .
git commit -m "Add CI pipeline and update values for Docker Hub"
git push origin main
```

---

**Dopo il push:**

- Vai su: `https://github.com/Torebarr85/my-gitops-demo/actions`
- Dovresti vedere la pipeline partire
- **Se completa → su Docker Hub vedrai l'immagine pushata!**
 
# 3. configurare ArgoCD


