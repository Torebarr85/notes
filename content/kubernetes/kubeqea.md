+++
title = "Kubernetes: networking & ports"
date = 2025-12-12
draft = false
tags = ["kubernetes"]
+++

# Networking e le porte in Kubernetes. 

Hai questo scenario:

yaml# Pod con container
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app
    image: my-app:latest
    ports:
    - containerPort: 8080

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        backend:
          service:
            name: my-app-service
            port:
              number: 80


Domande:

L'applicazione nel container ascolta sulla porta 8080. Perché nel Service c'è port: 80 e targetPort: 8080? Qual è la differenza?
Un altro Pod nello stesso namespace vuole chiamare questo servizio. Su quale porta fa la richiesta?
Un utente esterno visita http://myapp.example.com. Traccia il flusso completo con tutte le porte coinvolte.
---

**1. port vs targetPort ✅ CORRETTO**

- `port: 80` → porta su cui il Service ascolta (porta "pubblica" del Service)
- `targetPort: 8080` → porta del container dove inoltra il traffico

Perfetto!

---

**2. Pod-to-Pod communication ✅ QUASI CORRETTO**

Il Pod chiama: `http://my-app-service:80`

**Precisazioni:**
- Usa il **nome del Service** (my-app-service)
- Sulla porta del **Service** (80, non 8080!)
- ❌ Non usi direttamente il ClusterIP (potresti, ma non è la pratica standard)
- Il DNS risolve `my-app-service` → ClusterIP automaticamente

**Esempio pratico:**
```bash
# Dentro un altro Pod
curl http://my-app-service:80/api/health
```

Kubernetes DNS risolve il nome → ClusterIP → Service inoltra al Pod:8080

---

**3. Flusso esterno ✅ BUONO, aggiungo dettagli**

**Flusso completo con porte:**

```
Utente browser
    ↓
http://myapp.example.com:80 (HTTP default)
    ↓
[DNS pubblico] → IP del LoadBalancer AWS
    ↓
AWS LoadBalancer :80 (o :443 se HTTPS)
    ↓
Ingress Controller (nginx) Pod :80
    ↓
[Legge regole Ingress: host + path]
    ↓
Chiama Service: my-app-service:80
    ↓
Service (ClusterIP) :80
    ↓
[Selector trova Pod con label app=my-app]
    ↓
Inoltra a Pod container :8080 (targetPort)
    ↓
Applicazione ascolta su :8080
```

---

**Correzioni importanti:**

**Frontend vs Backend - non c'è differenza di porte:**
- ❌ Non è vero che frontend ha nginx dentro il container
- Il container può essere qualsiasi cosa: nginx, Java/Quarkus, Node.js, Python
- La porta `containerPort: 8080` è semplicemente dove **la tua applicazione ascolta**

**Esempi:**
- Frontend React: nginx ascolta porta 80
  ```yaml
  containerPort: 80
  ```
  
- Backend Quarkus: app Java ascolta porta 8080
  ```yaml
  containerPort: 8080
  ```
  
- Backend Node.js: potrebbe essere porta 3000
  ```yaml
  containerPort: 3000
  ```

**La porta è definita dall'applicazione nel container, non dal tipo (frontend/backend).**

---

**Riepilogo porte:**

| Componente | Porta | Significato |
|------------|-------|-------------|
| Browser | 80/443 | HTTP/HTTPS standard |
| LoadBalancer | 80/443 | Esposto pubblicamente |
| Ingress Controller | 80/443 | Riceve da LB |
| Service `port` | 80 | Porta "pubblica" del Service |
| Service `targetPort` | 8080 | Porta del Pod |
| Container `containerPort` | 8080 | App ascolta qui |

Nel mio caso Quarkus ascolta sulla 8080 

 
---


# SPIEGAZIONE FLUSSO WEB FOR DUMMIES
---

## **1. Utente digita nel browser**

```
http://myapp.example.com
```

Il browser automaticamente aggiunge `:80` (porta HTTP di default):
```
http://myapp.example.com:80
```

Se fosse HTTPS:
```
https://myapp.example.com:443
```

---

## **2. DNS pubblico - "Traduttore di nomi"**

Il browser non sa dove si trova `myapp.example.com`. Deve tradurre il nome in un **indirizzo IP**.

**Processo:**
1. Browser chiede al **DNS pubblico**: "Dove trovo myapp.example.com?"
2. DNS risponde: "È all'IP `52.123.45.67`"
3. Browser ora sa dove andare

**Analogia:** È come cercare "Pizzeria Da Mario" su Google Maps che ti dice l'indirizzo fisico "Via Roma 10".

---

## **3. Cosa c'è a quell'IP? Il LoadBalancer AWS**

Quando hai creato il cluster EKS, AWS ha creato un **LoadBalancer** (tipo un ALB o NLB).

**Il LoadBalancer è:**
- Un componente AWS **fuori dal cluster Kubernetes**
- Ha un IP pubblico (quello che il DNS restituisce)
- Ascolta sulle porte 80 e 443
- Riceve tutto il traffico da Internet

**Configurazione DNS (fatta una volta):**
```
myapp.example.com → CNAME → my-lb-123.elb.amazonaws.com
my-lb-123.elb.amazonaws.com → A record → 52.123.45.67
```

---

## **4. LoadBalancer AWS riceve la richiesta**

```
Richiesta arriva a: 52.123.45.67:80
LoadBalancer riceve: "GET / HTTP/1.1 Host: myapp.example.com"
```

Il LoadBalancer AWS adesso deve **inoltrare questa richiesta dentro il cluster Kubernetes**.

**Dove la inoltra?** All'**Ingress Controller** (nginx che gira come Pod dentro Kubernetes).

---

## **Flusso visivo completo:**

```
┌─────────────────┐
│  Browser        │
│  "Voglio andare │
│  su myapp..."   │
└────────┬────────┘
         │ http://myapp.example.com:80
         ↓
┌─────────────────┐
│  DNS pubblico   │
│  "myapp è qui:  │
│  52.123.45.67"  │
└────────┬────────┘
         │ Risolve nome → IP
         ↓
┌─────────────────────────┐
│  LoadBalancer AWS       │  ← FUORI Kubernetes
│  IP: 52.123.45.67       │
│  Ascolta su :80, :443   │
└────────┬────────────────┘
         │ Inoltra traffico
         ↓
┌─────────────────────────┐
│  Ingress Controller     │  ← DENTRO Kubernetes
│  (nginx Pod)            │
│  Legge regole Ingress   │
└────────┬────────────────┘
         │
         ↓ (Service → Pod)
```

---

## **In pratica nel tuo lavoro EKS:**

Quando fai deploy con Helm e abiliti Ingress:

```yaml
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: alb  # Usa AWS ALB
  hosts:
    - host: myapp.example.com
```

Helm crea:
1. **Ingress resource** dentro Kubernetes
2. AWS crea automaticamente un **ALB** (Application Load Balancer)
3. ALB ottiene un indirizzo tipo `my-alb-123.elb.amazonaws.com`
4. Tu configuri DNS: `myapp.example.com` → punta a `my-alb-123.elb.amazonaws.com`

**Dopo la configurazione iniziale, tutto è automatico.**

---

 Perfetto! Continuiamo dal LoadBalancer AWS che ha ricevuto la richiesta.

---

## **5. LoadBalancer inoltra all'Ingress Controller**

```
AWS LoadBalancer :80
    ↓ Inoltra a
Ingress Controller Pod (nginx) :80
```

**Cosa succede:**
- Il LoadBalancer AWS sa che deve inoltrare il traffico ai **nodi del cluster EKS**
- Su questi nodi gira l'**Ingress Controller** (un Pod nginx)
- Il traffico arriva al Pod nginx sulla porta 80

**Dettaglio tecnico:**
L'Ingress Controller è esposto tramite un Service di tipo **LoadBalancer** o **NodePort**, così il LoadBalancer AWS sa dove inoltrare.

```yaml
# Service dell'Ingress Controller
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
spec:
  type: LoadBalancer  # Questo crea il LoadBalancer AWS
  ports:
  - port: 80
    targetPort: 80  # Porta del Pod nginx
```

---

## **6. Ingress Controller legge le regole**

Ora il Pod nginx (Ingress Controller) ha ricevuto:
```
GET / HTTP/1.1
Host: myapp.example.com
```

**Cosa fa:**
1. Guarda l'header `Host: myapp.example.com`
2. Cerca tra tutte le **Ingress resources** del cluster
3. Trova la regola che matcha `myapp.example.com`

```yaml
# Ingress resource (configurazione)
rules:
- host: myapp.example.com    # ← Matcha questo!
  http:
    paths:
    - path: /
      backend:
        service:
          name: my-app-service  # ← Inoltra qui
          port:
            number: 80
```

**Decisione:** "Questa richiesta va al Service `my-app-service` porta 80"

---

## **7. Ingress Controller chiama il Service**

```
Ingress Controller (nginx Pod)
    ↓ Fa richiesta HTTP interna
Service: my-app-service:80
```

**Come funziona:**
- Ingress Controller fa una chiamata HTTP **dentro il cluster**
- Usa il DNS interno di Kubernetes
- Chiama: `http://my-app-service:80/`

È come se fosse un Pod normale che chiama un altro Service (come abbiamo visto prima nella comunicazione pod-to-pod).

---

## **8. Service riceve e cerca i Pod**

```
Service my-app-service
    ↓ Guarda selector
    ↓ Trova Pod con label app=my-app
Pod container :8080
```

**Cosa fa il Service:**
1. Riceve richiesta sulla sua porta 80
2. Guarda il suo `selector: app=my-app`
3. Chiede a Kubernetes: "Quali Pod hanno questa label?"
4. Kubernetes risponde: "Pod `my-app-xyz123` IP 10.244.1.5"
5. Service inoltra a `10.244.1.5:8080` (targetPort)

**Load balancing:**
Se ci sono 3 repliche del Pod, il Service fa round-robin:
- Richiesta 1 → Pod A
- Richiesta 2 → Pod B
- Richiesta 3 → Pod C
- Richiesta 4 → Pod A (ricomincia)

---

## **9. Pod riceve e risponde**

```
Pod container :8080
    ↓ Applicazione processa richiesta
    ↓ Genera risposta (HTML, JSON, etc.)
Risposta ritorna indietro
```

**Dentro il container:**
- La tua applicazione Quarkus ascolta su porta 8080
- Riceve: `GET / HTTP/1.1`
- Esegue il codice (controller, service, DB query, etc.)
- Genera risposta: `HTTP 200 OK` + body

---

## **10. Risposta torna indietro (stesso percorso al contrario)**

```
Pod :8080
    ↓ Risposta HTTP
Service :80
    ↓
Ingress Controller :80
    ↓
LoadBalancer AWS :80
    ↓
Internet
    ↓
Browser utente
```

**Ogni componente passa la risposta al precedente finché non arriva al browser.**

---

## **Flusso completo visivo con porte:**

```
┌──────────────────────────────────────────────┐
│ Browser                                      │
│ http://myapp.example.com:80                  │
└────────────────┬─────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────┐
│ DNS: myapp.example.com → 52.123.45.67        │
└────────────────┬─────────────────────────────┘
                 │
                 ↓
         ╔═══════════════╗
         ║ FUORI K8S     ║
         ╚═══════════════╝
┌──────────────────────────────────────────────┐
│ AWS LoadBalancer                             │
│ IP pubblico: 52.123.45.67                    │
│ Porta: 80                                    │
└────────────────┬─────────────────────────────┘
                 │
         ╔═══════════════╗
         ║ DENTRO K8S    ║
         ╚═══════════════╝
                 ↓
┌──────────────────────────────────────────────┐
│ Ingress Controller (nginx Pod)               │
│ Porta: 80                                    │
│ Legge: Host header = myapp.example.com       │
│ Regola Ingress: → my-app-service:80          │
└────────────────┬─────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────┐
│ Service: my-app-service                      │
│ Port: 80 (riceve qui)                        │
│ TargetPort: 8080 (inoltra qui)               │
│ Selector: app=my-app                         │
└────────────────┬─────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────┐
│ Pod: my-app-xyz123                           │
│ IP interno: 10.244.1.5                       │
│ Container porta: 8080                        │
│ Applicazione Quarkus ascolta su :8080        │
└──────────────────────────────────────────────┘
```

---

## **Riepilogo porte nel flusso:**

| Step | Componente | Porta IN | Porta OUT |
|------|------------|----------|-----------|
| 1 | Browser | - | 80 |
| 2 | LoadBalancer AWS | 80 | 80 |
| 3 | Ingress Controller | 80 | 80 |
| 4 | Service | 80 | 8080 |
| 5 | Pod/Container | 8080 | - |

**Le "traduzioni" di porta avvengono solo al Service** (80 → 8080).

---
 