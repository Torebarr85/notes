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




# Risposte alle tue domande

## 1. Service vs Ingress - Esempio pratico

**Non sono la stessa cosa** - lavorano a **livelli diversi**:

**Service = Layer 4 (TCP/UDP)**
- Distribuisce traffico TCP/UDP verso i pod
- Identifica destinazione per **IP:porta**
- Esempio: `10.96.0.1:8080` → pod backend

**Ingress = Layer 7 (HTTP/HTTPS)**  
- Analizza le **richieste HTTP** (host, path, headers)
- Routing intelligente basato su URL
- Esempio: `api.mioapp.com/users` → service users

### Esempio concreto

Hai 3 microservizi:
```
frontend-service (porta 3000)
api-service (porta 8080) 
database-service (porta 5432)
```

**Con solo Service LoadBalancer** avresti:
```
http://52.10.1.1:3000  → frontend
http://52.10.1.2:8080  → api
http://52.10.1.3:5432  → database
```
3 IP diversi, poco pratico!

**Con Ingress** hai:
```
https://mioapp.com/         → frontend-service:3000
https://mioapp.com/api/     → api-service:8080
```
Un solo dominio, routing intelligente. L'Ingress **usa i service sotto** per raggiungere i pod.

## 2. ClusterIP - Quando lo usi

**ClusterIP è una best practice** per comunicazione **interna** tra microservizi!

**Scenario reale**: 
- Frontend (esposto via Ingress/LoadBalancer)
- API backend (ClusterIP, solo interno)
- Database (ClusterIP, solo interno)

Il frontend chiama `http://api-service:8080` dall'interno. Database chiama solo l'API. **Nessuno dall'esterno può raggiungere API o DB direttamente** - sicurezza!

**Regola**: esponi con LoadBalancer/Ingress **solo ciò che serve dall'esterno**.

## 3. Due LoadBalancer nei cloud - Perché?

Sì, ci sono **due load balancer con scopi diversi**:

**Service LoadBalancer** (Layer 4):
- Creato dal **cloud provider** (AWS ELB, Azure LB)
- Un LoadBalancer **per ogni service** esposto
- Costa denaro per ognuno!
- Esempio: 5 app = 5 LoadBalancer = €€€

**Ingress Controller LoadBalancer** (Layer 7):
- **Un solo** LoadBalancer
- Tutto il traffico HTTP/HTTPS passa qui
- Routing intelligente interno basato su URL
- Esempio: 5 app = 1 LoadBalancer = €

**Best practice cloud**: usa Ingress per HTTP/HTTPS (più economico, più flessibile). Usa Service LoadBalancer solo per protocolli non-HTTP (es. database TCP diretto, se necessario).