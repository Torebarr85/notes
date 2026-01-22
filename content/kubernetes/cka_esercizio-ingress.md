+++
title = "Kubernetes Networking - tuts creare service e ingress"
date = 2026-01-18
draft = false
tags = ["kubernetes","networking","ingress"]
+++



## Terminologia **Deployment** e **Pod** sono due cose diverse:

- **Deployment**: la "ricetta" che dice "voglio 2 repliche di questa app"
- **Pod**: l'istanza effettiva che gira (il Deployment ne crea 2)

Quando esponi con un Service, punti al **Deployment** (tecnicamente ai suoi pod tramite i label selector).

# Modi per creare Service

**1. Imperativo - da Deployment**
```bash
kubectl expose deployment asia -n world --port=80 --target-port=80
```
Crea automaticamente un Service ClusterIP che seleziona i pod del deployment `asia`.

**2. Imperativo - specificando tipo**
```bash
kubectl expose deployment asia -n world --port=80 --type=NodePort
```
Opzioni tipo: `ClusterIP` (default), `NodePort`, `LoadBalancer`

**3. Dichiarativo - YAML minimo**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: asia-service
  namespace: world
spec:
  selector:
    app: asia    # deve matchare label del pod
  ports:
  - port: 80
    targetPort: 80
```

**4. Dichiarativo - con tipo specifico**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: asia-service
  namespace: world
spec:
  type: NodePort
  selector:
    app: asia
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080  # opzionale, altrimenti K8s assegna random
```

## Quale usare per l'esercizio?

Per un esercizio Ingress tipicamente usi:
```bash
kubectl expose deployment asia -n world --port=80
kubectl expose deployment europe -n world --port=80
```

Questo crea due Service ClusterIP. Poi l'Ingress li usa come backend.

## Verifica rapida

Dopo aver creato il service:
```bash
kubectl get svc -n world
# Vedi IP clusterIP assegnato

kubectl get endpoints -n world
# Vedi IP dei pod effettivi dietro il service
```

Il **selector** `app: asia` è la chiave: deve corrispondere al label che vedi nel pod template del deployment.


