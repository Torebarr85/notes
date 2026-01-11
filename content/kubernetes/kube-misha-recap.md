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

# Endpoint vs URL - La differenza

## Endpoint = Indirizzo di rete (IP:porta)

Un **endpoint** è semplicemente un **indirizzo tecnico** dove raggiungere qualcosa:

```
10.96.0.1:8080
192.168.1.50:3000
my-service:80
```

È solo **IP + porta** (o nome + porta). Nessuna informazione su "cosa" stai chiedendo.

## URL = Indirizzo semantico completo

Un **URL** ha una **struttura completa**:

```
https://api.mioapp.com:443/users/123?active=true

protocollo: https
dominio: api.mioapp.com  
porta: 443
path: /users/123
query: ?active=true
```

Contiene **informazioni sul cosa stai chiedendo**.

## Esempio pratico concreto

**Service (fornisce endpoint)**:
```bash
kubectl get svc api-service
NAME          TYPE        CLUSTER-IP     PORT
api-service   ClusterIP   10.96.0.15     8080
```

Endpoint = `10.96.0.15:8080`

Chiami così (dall'interno del cluster):
```bash
curl http://10.96.0.15:8080/users
```

**Ingress (fornisce URL)**:
```yaml
host: api.mioapp.com
paths:
  - path: /users
    service: api-service:8080
```

URL = `https://api.mioapp.com/users`

Chiami così (dal browser):
```bash
curl https://api.mioapp.com/users
```

## In sintesi

- **Service** ti dà un **endpoint stabile** (IP:porta) per raggiungere i pod
- **Ingress** ti dà **URL leggibili** (domini+path) che mappano agli endpoint dei service

L'Ingress "traduce" `api.mioapp.com/users` nell'endpoint `api-service:8080` usando le regole di routing.

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





# Recap Schematico: Kubernetes Networking

## Struttura Base

```
POD (effimero)
├─ Container 1 (porta 80)
├─ Container 2 (porta 3000)
└─ IP Pod: 10.1.2.1 (cambia se ricrei il pod)
```

**Nota**: I pod sono instabili, muoiono e rinascono con IP diversi. Servono i Service.

## Service: 3 Tipi

### 1. ClusterIP (default)
```
Service: frontend-service
├─ Type: ClusterIP
├─ IP interno: 192.10.8.1
└─ Raggiungibile: SOLO dentro cluster
```

**Quando**: microservizi interni (API, DB) che non devono essere esposti fuori.

### 2. LoadBalancer
```
Service: frontend-service
├─ Type: LoadBalancer
├─ ClusterIP: 192.10.8.1 (rete interna K8s)
└─ ExternalIP: 52.10.1.1 (rete pubblica)
```

**CHIAVE**: Ogni Service ha **sempre** un ClusterIP. Il LoadBalancer aggiunge IN PIÙ un ExternalIP.

**Quando**: esporre app singole direttamente (qualsiasi protocollo: HTTP, TCP, UDP).

### 3. NodePort
```
Service: frontend-service  
├─ Type: NodePort
├─ ClusterIP: 192.10.8.1
└─ Porta su ogni nodo: 30080
```

**Quando**: raramente, solo per test locali.

## Flussi Completi

### Flusso INTERNO (pod chiama service)
```
Pod A (10.1.1.5)
  → frontend-service:80 (nome DNS)
    → Service ClusterIP (192.10.8.1)
      → Pod B (10.1.2.1:80)
```

**Nota**: Usa sempre il nome del service, mai gli IP dei pod!

### Flusso ESTERNO con LoadBalancer
```
Browser (internet)
  → 52.10.1.1:80 (ExternalIP pubblico)
    → LoadBalancer (ponte tra reti)
      → Service ClusterIP (192.10.8.1)
        → Pod (10.1.2.1:80)
```

**Nota**: Il LoadBalancer ascolta su IP pubblico e inoltra alla rete interna cluster.

### Flusso ESTERNO con Ingress
```
Browser
  → https://myfrontend.com (URL)
    → DNS → 52.10.1.1
      → Ingress Controller LoadBalancer
        → Ingress Resource (legge regole: myfrontend.com → frontend-service)
          → Service ClusterIP (192.10.8.1)
            → Pod (10.1.2.1:80)
```

**Nota**: L'Ingress Controller è ANCHE un LoadBalancer, ma fa routing Layer 7 (HTTP). Usa le regole Ingress per decidere quale Service chiamare.

## Differenza LoadBalancer vs Ingress

**LoadBalancer Service**: un IP pubblico per ogni app
**Ingress**: un solo IP pubblico, routing intelligente per N app

**Esempio cloud**:
- 5 app con LoadBalancer = 5 IP pubblici = €€€€€
- 5 app con Ingress = 1 IP pubblico = €