+++
title = "Kubernetes: misha CKA - recap networking"
date = 2025-12-29
draft = false
tags = ["kubernetes"]
+++



# Recap Completo: Kubernetes Networking

## 1. Fondamenti: Pod e CNI

Il **networking in Kubernetes avviene a livello di Pod** ed è implementato dal **CNI plugin** (Container Network Interface). Ogni pod ha il proprio IP sulla rete del cluster.

## 2. Services: l'astrazione chiave

Invece di fare routing manuale verso singoli pod, usiamo i **Services** come **endpoint unico** che distribuisce automaticamente il traffico verso i pod disponibili.

**Vantaggio**: puoi aggiornare/eliminare/ricreare pod senza preoccuparti - il service continua a funzionare e trova sempre un pod attivo.

## 3. Tipi di Service

### ClusterIP (default)
- Espone il service solo **all'interno del cluster**
- È quello che ottieni con `kubectl expose` senza specificare altro
- IP accessibile solo da dentro Kubernetes

### NodePort
- Espone il service sugli **IP dei nodi** stessi
- Generalmente **poco usato** in produzione
- Apre una porta specifica su ogni nodo del cluster

### LoadBalancer
- Crea un **IP esterno indipendente dai nodi**
- **Consigliato per Rancher Desktop** quando vuoi esporre app
- Comune nei cluster cloud (AWS, Azure, GCP)

## 4. Ingress: routing basato su URL

Invece di usare solo IP, l'**Ingress** permette di:
- Usare **domini** (FQDN): `app.example.com`
- **Path-based routing**: `/frontend`, `/api`, `/database`
- Gestire **SSL/TLS** con certificati HTTPS

### Flusso completo
```
Browser (URL) 
  → DNS 
    → LoadBalancer (80/443)
      → Ingress Controller (Traefik/Nginx)
        → Ingress Resource (regole routing)
          → Service
            → Pod
```

### Implementazione
- Ingress è **solo YAML** (definizione delle regole)
- Serve un **Ingress Controller** installato (Traefik, Nginx, Cilium...)
- Configurazione più complessa, "frustrante le prime volte"

## Raccomandazione pratica

Per **Rancher Desktop**: usa il **LoadBalancer service** per esporre le tue app durante l'apprendimento. Usa il file YAML `service.yaml` con `type: LoadBalancer`.