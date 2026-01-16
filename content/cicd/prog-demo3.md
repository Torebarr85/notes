+++
title = "Progetto Demo CI/CD + GitOps + helm part 3"
date = 2026-01-16
draft = false
tags = ["cicd","argocd","helm"]
+++

# parte 3 goal: configurare ArgoCD


ArgoCD ha bisogno di sapere:
- Quale repo GitHub watchare
- Quale cartella (la nostra `helm-chart/`)
- Dove deployare (namespace `my-gitops-demo`)

---

## **Crea file ArgoCD Application**

```bash
# Crea file nella cartella infra
touch infra/argocd/application.yaml
```

---

## **Contenuto `infra/argocd/application.yaml`:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-cats-app
  namespace: argocd
spec:
  project: default
  
  source:
    repoURL: https://github.com/Torebarr85/my-gitops-demo.git
    targetRevision: master
    path: helm-chart
  
  destination:
    server: https://kubernetes.default.svc
    namespace: my-gitops-demo
  
  syncPolicy:
    automated:
      prune: true      # Rimuove risorse cancellate dal repo
      selfHeal: true   # Ripristina modifiche manuali
    syncOptions:
      - CreateNamespace=true
```

---

## **Cosa fa:**

- **source**: punta al tuo repo GitHub, branch main, cartella `helm-chart/`
- **destination**: deploya nel namespace `my-gitops-demo`
- **syncPolicy.automated**: sync automatico quando cambia il repo

---

## **applichiamo il file su ArgoCD**

```bash
#Applica l'Application:

kubectl apply -f infra/argocd/application.yaml

# Verifica che ArgoCD l'abbia rilevata
kubectl get applications -n argocd
```


### **Cosa fa `kubectl apply -f application.yaml`?**

**Non fa partire ArgoCD** - gli dà solo le istruzioni!

**Flusso:**
1. `kubectl apply` → crea risorsa "Application" in K8s
2. ArgoCD (già running) **rileva** la nuova Application
3. ArgoCD legge spec (repo GitHub, path helm-chart/)
4. ArgoCD **automaticamente** fa `helm install` per te
5. Da quel momento watcha il repo → ogni cambio = `helm upgrade`

---

## **Analogia:**

```
kubectl apply = "Hey ArgoCD, ti ho lasciato un biglietto con istruzioni"
ArgoCD = "Ok letto! Installo subito e da ora controllo ogni 3 minuti"
```

---

**Disinstalla prima Helm manuale, poi applica application.yaml e vediamo ArgoCD in azione!**