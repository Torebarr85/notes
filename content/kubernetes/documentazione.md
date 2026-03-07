+++
title: "Kubernetes Offline — dry-run e kubectl explain"
date: 2026-03-07
tags: ["kubernetes","CKA","devops","cheatsheet"]
+++

> Questo documento funziona **completamente offline**.
> È la tecnica ufficiale usata all'esame CKA — niente YAML a memoria.

---

## La Regola d'Oro

**Mai scrivere YAML da zero.** Generalo sempre con:

```bash
kubectl <comando> --dry-run=client -o yaml
```

`--dry-run=client` = non applica nulla al cluster, simula solo localmente  
`-o yaml` = stampa il manifest YAML invece di eseguirlo

---

## Generare manifest — Casi Pratici

### Pod

```bash
kubectl run mio-pod --image=nginx --dry-run=client -o yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mio-pod
spec:
  containers:
  - image: nginx
    name: mio-pod
```

```bash
# Pod con variabili d'ambiente
kubectl run mio-pod --image=nginx \
  --env="ENV=production" \
  --env="PORT=3000" \
  --dry-run=client -o yaml

# Pod con porta esposta
kubectl run mio-pod --image=nginx \
  --port=80 \
  --dry-run=client -o yaml

# Pod con label
kubectl run mio-pod --image=nginx \
  --labels="app=web,env=prod" \
  --dry-run=client -o yaml
```

---

### Deployment

```bash
kubectl create deployment web --image=nginx --replicas=3 --dry-run=client -o yaml
```

```bash
# Salva su file e modifica
kubectl create deployment web --image=nginx --replicas=3 \
  --dry-run=client -o yaml > web-deployment.yaml

# Applica
kubectl apply -f web-deployment.yaml
```

---

### Service

```bash
# ClusterIP (default)
kubectl expose deployment web --port=80 --dry-run=client -o yaml

# NodePort
kubectl expose deployment web --port=80 --type=NodePort \
  --dry-run=client -o yaml

# Con nome custom
kubectl expose deployment web --port=80 --name=web-service \
  --dry-run=client -o yaml
```

---

### ConfigMap

```bash
# Da valori inline
kubectl create configmap mia-config \
  --from-literal=DB_HOST=localhost \
  --from-literal=DB_PORT=5432 \
  --dry-run=client -o yaml

# Da file
kubectl create configmap mia-config \
  --from-file=config.properties \
  --dry-run=client -o yaml
```

---

### Secret

```bash
kubectl create secret generic mio-secret \
  --from-literal=username=admin \
  --from-literal=password=s3cret \
  --dry-run=client -o yaml
```

---

### ServiceAccount

```bash
kubectl create serviceaccount mio-sa --dry-run=client -o yaml
```

---

### Job e CronJob

```bash
# Job
kubectl create job mio-job --image=busybox \
  --dry-run=client -o yaml -- sh -c "echo hello"

# CronJob
kubectl create cronjob mio-cron --image=busybox \
  --schedule="*/5 * * * *" \
  --dry-run=client -o yaml -- sh -c "echo hello"
```

---

## kubectl explain — Documentazione Offline

`kubectl explain` è la tua documentazione offline. Spiega ogni campo di ogni risorsa.

```bash
# Struttura base di una risorsa
kubectl explain pod
kubectl explain deployment
kubectl explain service

# Vai in profondità
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.resources
kubectl explain pod.spec.containers.livenessProbe

# Deployment
kubectl explain deployment.spec.strategy
kubectl explain deployment.spec.template.spec

# Service
kubectl explain service.spec.type
kubectl explain service.spec.selector
```

### Esempio pratico — non ricordi la sintassi delle probe?

```bash
kubectl explain pod.spec.containers.livenessProbe
```

Output (estratto):
```
livenessProbe     <Object>
  httpGet         <Object>
    path          <string>
    port          <integer>
  initialDelaySeconds  <integer>
  periodSeconds        <integer>
  failureThreshold     <integer>
```

Ora sai esattamente cosa scrivere nel YAML — senza internet.

---

## Workflow Completo in Volo

### Scenario: crea un Deployment con ConfigMap e liveness probe

**Step 1 — Genera il Deployment base**
```bash
kubectl create deployment myapp --image=nginx --replicas=2 \
  --dry-run=client -o yaml > myapp.yaml
```

**Step 2 — Genera la ConfigMap**
```bash
kubectl create configmap myapp-config \
  --from-literal=ENV=production \
  --dry-run=client -o yaml >> myapp.yaml
```

**Step 3 — Consulta la documentazione offline per la probe**
```bash
kubectl explain pod.spec.containers.livenessProbe.httpGet
```

**Step 4 — Modifica il file con vim o nano**
```bash
nano myapp.yaml
# oppure
vim myapp.yaml
```

Aggiungi la livenessProbe al container nel Deployment:
```yaml
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
```

**Step 5 — Applica**
```bash
kubectl apply -f myapp.yaml
kubectl get pods -w
```

---

## Modificare risorse esistenti

```bash
# Modifica direttamente (apre vim/nano)
kubectl edit deployment web

# Scala velocemente senza editare
kubectl scale deployment web --replicas=5

# Aggiorna l'immagine
kubectl set image deployment/web nginx=nginx:1.25

# Vedi la rollout history
kubectl rollout history deployment web

# Rollback all'ultima versione stabile
kubectl rollout undo deployment web
```

---

## Comandi di Output Utili

```bash
# YAML della risorsa esistente (per copiare e modificare)
kubectl get deployment web -o yaml

# JSON (più dettagliato)
kubectl get pod mio-pod -o json

# Solo i campi che ti servono con jsonpath
kubectl get pod mio-pod -o jsonpath='{.status.podIP}'
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# Formato tabella custom
kubectl get pods -o custom-columns=NAME:.metadata.name,IP:.status.podIP,STATUS:.status.phase
```

---

## Cheatsheet Rapido

| Cosa creare | Comando base |
|---|---|
| Pod | `kubectl run nome --image=X --dry-run=client -o yaml` |
| Deployment | `kubectl create deployment nome --image=X --replicas=N --dry-run=client -o yaml` |
| Service ClusterIP | `kubectl expose deployment nome --port=80 --dry-run=client -o yaml` |
| Service NodePort | `kubectl expose deployment nome --port=80 --type=NodePort --dry-run=client -o yaml` |
| ConfigMap | `kubectl create configmap nome --from-literal=KEY=VAL --dry-run=client -o yaml` |
| Secret | `kubectl create secret generic nome --from-literal=KEY=VAL --dry-run=client -o yaml` |
| Job | `kubectl create job nome --image=X --dry-run=client -o yaml -- <cmd>` |
| CronJob | `kubectl create cronjob nome --image=X --schedule="* * * * *" --dry-run=client -o yaml` |
| Namespace | `kubectl create namespace nome --dry-run=client -o yaml` |
| ServiceAccount | `kubectl create serviceaccount nome --dry-run=client -o yaml` |

---

> **Tip CKA:** All'esame hai accesso a `kubectl explain` e alla documentazione ufficiale su kubernetes.io. Allena questo workflow offline e all'esame sarai velocissimo.