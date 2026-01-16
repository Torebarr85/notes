+++
title = "PROGETTO da zero CI/CD + GitOps ArgoCD + Helm parte 0"
date = 2026-01-14
draft = false
tags = ["cicd"]
+++

# PROGETTO da zero Con ArgoCD + Helm:

## **Flusso completo**

```
Modifichi app/index.html
  ↓ git push
GitHub Actions builda + pusha immagine
  ↓ commit automatico values.yaml
ArgoCD rileva cambio
  ↓ helm upgrade
App aggiornata su localhost:30080
```

---
 
**Analisi:**

# Recap Progetto GitOps Demo

---

## **Componenti**

**1. App:** Frontend HTML statico servito da nginx

**2. Docker:** Immagine custom con app buildabile, pushata su Docker Hub

**3. Helm Chart:** Package K8s con deployment + service NodePort per esporre l'app

**4. GitHub Actions (CI):** Pipeline che builda immagine, genera tag univoco (commit SHA), pusha su Docker Hub, aggiorna `values.yaml` automaticamente

**5. ArgoCD (GitOps):** Watcha il repo GitHub, rileva cambi in `values.yaml`, fa `helm upgrade` automatico nel cluster

**6. Rancher Desktop:** Cluster Kubernetes locale dove gira tutto

---


```bash
# Tu modifichi Git:
git commit -m "Update eobi-fe to 1.2.3"
git push

# ArgoCD vede il cambio ed esegue automaticamente:
helm upgrade eobi-fe ./charts --set image.tag=1.2.3
# E K8S monitora che i pod siano healthy


# K8s controlla sempre:
- Liveness probe: pod vivo?
- Readiness probe: pod pronto?
- Restart policy: riavvia se crashato
```

## Differenza: Chi VEDE lo stato

**Kubernetes (sempre):**
```bash
kubectl get pods
NAME            READY   STATUS
eobi-fe-xxx     0/1     CrashLoopBackOff
                ↑
            K8s lo sa e tenta restart
```
 
**ArgoCD:**
```bash
# Legge lo stato da K8s e te lo mostra:
ArgoCD UI → Pods: Degraded ❌
            Status: CrashLoopBackOff
            
# ArgoCD non "monitora", legge da K8s API
```

## In pratica

**K8s:** Fa il lavoro (monitora, riavvia, scala)  
**ArgoCD:** Dashboard che legge da K8s e mostra lo stato in UI

**Quindi:** K8s monitora, ArgoCD ti fa VEDERE quello che K8s vede.



 