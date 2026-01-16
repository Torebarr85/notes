+++
title = "PROGETTO da zero CI/CD + GitOps ArgoCD + Helm"
date = 2026-01-14
draft = false
tags = ["cicd"]
+++

# PROGETTO da zero Con ArgoCD + Helm:

**In Sintesi**
- Helm: "Come" pacchettizzare/installare/upgradare
- ArgoCD: "Quando" e "automaticamente"

ArgoCD usa Helm, non lo sostituisce.

**Analisi:**


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