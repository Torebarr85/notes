
+++
title = "Kubernetes: misha CKA - section 3"
date = 2025-12-25
draft = false
tags = ["kubernetes"]
+++
 

# DEPLOYMENTS 


```
kubectl create deployment -h | less

kubectl create deploy test --image=httpd --replicas=3

kubectl get deployments.apps

NAME   READY   UP-TO-DATE   AVAILABLE   AGE
test   3/3     3            3           52s

kubectl describe deployments.apps <nomeDeployment>

kubectl delete deployments.apps <nomeDeployment>
and all the 3 pods will vanish immediately! 
```


ovviamente tutto sarà automatizzato non dobbiamo fare a mano
coome possiamo fare in code questo?

### creaimo yaml senza applicarlo quindi usando dry run client e -o yaml per visualizzarlo

```
~> kubectl create deploy test2 --image=httpd --replicas=10 --dry-run=client -o yaml > deploytest.yaml


~> cat deploytest.yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: test2
  name: test2
spec:
  replicas: 10
  selector:
    matchLabels:
      app: test2
  template:
    metadata:
      labels:
        app: test2
    spec:
      containers:
      - image: httpd
        name: httpd
status: {}

~> kubectl apply -f deploytest.yaml 
deployment.apps/test2 created

~> kubectl get pods -o wide
NAME                     READY   STATUS    RESTARTS   AGE    IP           NODE                   NOMINATED NODE   READINESS GATES
httpd-tore               1/1     Running   1          22h    10.42.0.20   lima-rancher-desktop   <none>           <none>
nginx-tore               1/1     Running   3          2d3h   10.42.0.21   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-5hq28   1/1     Running   0          12s    10.42.0.34   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-652bw   1/1     Running   0          12s    10.42.0.36   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-jvnnr   1/1     Running   0          12s    10.42.0.35   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-njngl   1/1     Running   0          13s    10.42.0.29   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-phsps   1/1     Running   0          12s    10.42.0.37   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-t7985   1/1     Running   0          12s    10.42.0.33   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-tkg7g   1/1     Running   0          12s    10.42.0.30   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-tlp6m   1/1     Running   0          12s    10.42.0.31   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-twcw5   1/1     Running   0          13s    10.42.0.28   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-w66pr   1/1     Running   0          12s    10.42.0.32   lima-rancher-desktop   <none>           <none>


~> kubectl get deployments.apps
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
test2   10/10   10           10          48s

```
- sotto il cofano il deployments non serve a creare i pods realmente ma a creare/controllare i replicaset object.
infatti se facciamo get replicaset vedremo che nel cluster ora c'è un replicaset creato:

```
~> kubectl get replicasets.apps 
NAME               DESIRED   CURRENT   READY   AGE
test2-858c9c4dbf   10        10        10      2m54s
```
- NB K8s manage replicaset for you. don't touch replicaset object.
- K8s di default keep until last 10 old replicaset around 
### Strategy 
- .spec.strategy specifies the strategy used to replace old Pods by new ones. .spec.strategy.type can be "Recreate" or "RollingUpdate". "RollingUpdate" is the default value. RollingUpdate = quando kill un pod viene fatto one by one non tutti assieme


```
questo comando "watch -n 1" è come se lanciassi ogni 1sec il comando dopo quindi get pods:
watch -n 1 kubectl get pods

```
se un pod va in errore k8s capisce che non deve fare rolling anche degli altri.


# Deployments - Namespaces

- Purpose of NAMESPACES: isolating groups of resources within a single cluster
- logical grouping
- name unique
- 
```
~> kubectl get namespaces
NAME              STATUS   AGE
default           Active   2d9h
kube-node-lease   Active   2d9h
kube-public       Active   2d9h
kube-system       Active   2d9h

~> kubectl get namespace pippo -o yaml --dry-run=client > namespace.yaml
kubectl apply -f namespace pippo
```

se non diamo indicazioni dove creo il pod lo mette nel default-namespace, diversamente aggiungiamo --namespace oppure -n ed il <nomeNamespace>
 
per mettere default namespace pippo:
```
kubectl config set-context --current --namespace=pippo
```

# Deployments - Our First Application
# Tutorial: Deploy Mealie su Kubernetes (Step by Step)

## Overview
Deployiamo Mealie (app di ricette) su K8s usando deployment → replicaset → pods.

---

## Step 1: Crea Namespace

```bash
kubectl create namespace mealie
```

Verifica:
```bash
kubectl get namespaces
```

---

## Step 2: Genera il Deployment (template)

```bash
kubectl create deployment mealie \
  --image=nginx \
  --dry-run=client -o yaml > deployment.yaml
```

**Cosa fa**: crea un file YAML senza applicarlo (`--dry-run`).

---

## Step 3: Modifica il Deployment

Apri il file:
```bash
vim deployment.yaml
```

### Cosa modificare:

**a) Aggiungi il namespace**
```yaml
metadata:
  name: mealie
  namespace: mealie  # <-- aggiungi questa riga
```

**b) Modifica l'immagine e la porta**
```yaml
spec:
  containers:
  - name: mealie
    image: ghcr.io/mealie-recipes/mealie:v1.3.2  # sostituisci nginx con l'immagine vera
    ports:
    - containerPort: 9000  # porta su cui risponde il container
```

**Perché 9000?** È la porta dove Mealie ascolta le richieste HTTP.

---

## Step 4: Applica il Deployment

```bash
kubectl apply -f deployment.yaml
```

Verifica che il pod sia running:
```bash
kubectl get pods -n mealie -o wide
```

Output atteso:
```
NAME                      READY   STATUS    IP
mealie-1c23b45678-abcd    1/1     Running   10.244.1.5
```

---

## Step 5: Testa con Port-Forward (solo per debug locale)

```bash
kubectl port-forward pods/mealie-1c23b45678-abcd 9000:9000 -n mealie
```

**Importante**: il terminale deve rimanere aperto!

Ora vai su **localhost:9000** nel browser → vedi l'app Mealie.

### Quando usare port-forward?
- ✅ Test rapidi in locale
- ❌ NON per produzione (usa Service + Ingress)

---

## Prossimi passi (non in questo tutorial)

1. **Creare un Service**: espone il pod stabilmente
2. **Configurare Ingress**: rende l'app accessibile da fuori del cluster
3. **Persistent Volume**: salva i dati anche se il pod si riavvia

---

## Riepilogo comandi

```bash
# 1. Namespace
kubectl create namespace mealie

# 2. Template deployment
kubectl create deployment mealie --image=nginx --dry-run=client -o yaml > deployment.yaml

# 3. Edita e applica
vim deployment.yaml
kubectl apply -f deployment.yaml

# 4. Verifica
kubectl get pods -n mealie -o wide

# 5. Test locale
kubectl port-forward pods/<POD_NAME> 9000:9000 -n mealie
```

---
