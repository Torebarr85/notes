+++
title = "Kubernetes Networking - Dal Pod all'Ingress (theory)"
date = 2026-01-18
draft = false 
tags = ["kubernetes","networking","ingress"]
+++


## 0. Le Fondamenta - Come Funziona Sotto il Cofano

Prima di vedere Services e Ingress, capiamo come i pod possono parlarsi.

### Ogni Pod = Computer Isolato

Quando Kubernetes crea un pod:
1. **Crea un network namespace** (bolla di rete isolata)
2. **Assegna un IP univoco** al pod (es. 10.244.1.5)
3. **Configura routing** per raggiungere altri pod

Questo lavoro lo fa il **CNI Plugin** (Container Network Interface).

### CNI Plugin - Il Costruttore di Reti

**Ruolo:** Gestisce la connettività base tra pod.

**Cosa fa concretamente quando crei un pod:**
```bash
kubectl run nginx --image=nginx
```

Il CNI (es. Calico, Flannel, Cilium):
1. Crea namespace di rete isolato per il pod
2. Crea **veth pair** (cavo virtuale tra pod e nodo)
3. Assegna IP: `10.244.1.5`
4. Collega al **bridge** (switch virtuale sul nodo)
5. Configura routing per altri nodi

**Visualizzazione:**
```
┌────────────────────────────────────────┐
│          Nodo Kubernetes               │
│                                        │
│   Pod nginx (namespace isolato)        │
│   └─ eth0: 10.244.1.5                 │ ← CNI assegna
│          ↕ (veth pair = cavo)          │ ← CNI crea
│   cni0 (bridge = switch virtuale)     │ ← CNI gestisce
│   └─ IP: 10.244.1.1                   │
│          ↕                             │
│   eth0 (nodo): 192.168.1.10           │
└────────────────────────────────────────┘
```

### Il Bridge - Lo Switch Virtuale

Il **bridge** (`cni0`) è come uno switch fisico, ma software:
- Collega tutti i pod sullo stesso nodo
- Permette la comunicazione pod-to-pod locale
```bash
# Vedere il bridge sul nodo
ip link show cni0

# Vedere i veth collegati
bridge link show
```

### CNI Popolari

- **Calico:** Networking + Network Policies (il più usato)
- **Flannel:** Semplice, solo networking base  
- **Cilium:** Avanzato con eBPF
- **Weave:** Con encryption

**Prerequisito Kubernetes:** Il CNI deve essere installato prima che i pod possano comunicare.

### CNI vs Kube-Proxy - Ruoli Separati

| Componente | Cosa Fa |
|------------|---------|
| **CNI Plugin** | Connettività pod-to-pod diretta |
| **Kube-Proxy** | Gestisce i Services (load balancing) |

**Importante:** CNI assegna IP ai pod, kube-proxy gestisce i ClusterIP dei Services.

---

**Ora che sai come funziona sotto, vediamo come usare i Services...**


# Kubernetes Networking - Dal Pod all'Ingress

---

## 1. Comunicazione base tra Pod

### Il concetto fondamentale
Ogni pod ha un **IP proprio** nella rete del cluster (es. 10.244.1.5).

```bash
# Pod A può chiamare direttamente Pod B usando il suo IP
curl 10.244.2.8:80
```

### Il problema
Gli IP dei pod **cambiano continuamente**:
- Restart del pod
- Scaling (nuovi pod = nuovi IP)
- Aggiornamenti

**Soluzione:** Non usare direttamente gli IP dei pod → usare i Services
### Come Funziona Sotto

Quando fai `curl 10.244.2.8:80`, il pacchetto:
1. Esce dal namespace del pod sorgente
2. Passa attraverso il **veth pair** (cavo virtuale gestito dal CNI)
3. Arriva al **bridge cni0** sul nodo
4. Il bridge lo instrada verso il pod destinazione (stesso nodo) o verso la rete del cluster (altro nodo)

Tutto questo è trasparente grazie al CNI plugin.

---

## 2. Services - Nome stabile per pod instabili

### Cosa fa un Service
Crea un **nome DNS stabile** + **IP virtuale stabile** che punta a un gruppo di pod.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app    # Trova tutti i pod con questa label
  ports:
  - port: 80       # Porta del Service
    targetPort: 8080  # Porta del container nel pod
```

### Cosa succede dietro le quinte
1. Kubernetes crea DNS: `my-app.namespace.svc.cluster.local` = invece di usare IP, puoi chiamare il Service per nome
2. Assegna ClusterIP virtuale: `10.96.5.10` = rimane uguale anche se i pod dietro cambiano
3. **kube-proxy** crea regole iptables per distribuire traffico ai pod = **Load balancing** - se hai 3 repliche dello stesso pod, il Service distribuisce le richieste tra tutti e 3

## Come funziona il DNS

Quando crei un Service chiamato `pippo` nel namespace `default`, Kubernetes genera automaticamente questo nome DNS completo:

```
pippo.default.svc.cluster.local
```

Spiegazione dei pezzi:
- `pippo` = nome del Service
- `default` = namespace dove si trova
- `svc` = indica che è un Service (abbreviazione di "service")
- `cluster.local` = dominio del cluster

**Cosa significa in pratica?** Altri pod possono contattare il tuo Service semplicemente usando `pippo` (se sono nello stesso namespace) oppure `pippo.default` (da altri namespace).

## Il ruolo di kube-proxy

Quando crei un Service, il componente **kube-proxy** (che gira su ogni nodo) crea delle **regole iptables**.

**iptables** è un sistema Linux per gestire il traffico di rete. Le regole che crea kube-proxy dicono: "se arriva traffico per IP 10.96.5.10 porta 8080, mandalo a uno di questi pod: 172.17.0.3:80, 172.17.0.4:80, 172.17.0.5:80".

In pratica: kube-proxy **intercetta** il traffico destinato al ClusterIP e lo **redirige** verso uno dei pod reali, facendo load balancing.

---

## 3. I tre livelli di porta nel Service

### Struttura della configurazione
```yaml
spec:
  type: NodePort
  ports:
  - port: 80          # Porta del Service (ClusterIP interno)
    targetPort: 8080  # Porta del container nel pod
    nodePort: 30080   # Porta esposta sul nodo (per accesso esterno)
```

### Esempio pratico di flusso
```
Richiesta esterna → NodeIP:30080 
                         ↓
                    Service ClusterIP:80
                         ↓
                    Pod container:8080
```

### Punti chiave
- **targetPort** deve matchare la porta su cui il container **effettivamente ascolta**
- Non è detto che nginx ascolti su 80 - dipende dalla configurazione del container
- Il Service può avere porta diversa dalla targetPort

---

## 4. I tre tipi di Service

### ClusterIP (default)
```
Accessibile SOLO dall'interno del cluster

Pod A → Service my-app:80 → Pod B (targetPort 8080)
```

**Accesso dall'interno:**
- Via nome: `my-app:3000`
- Via IP: `10.96.x.x:3000`

### NodePort
```
Accessibile anche dall'esterno

Esterno → NodeIP:30080 
         ↓
      Service ClusterIP:80
         ↓
      Pod:8080
```

**Accesso:**
- **Interno:** `my-service:3000` o `10.96.x.x:3000`
- **Esterno:** `node-ip:30500` o `node-dns:30500`


# NodePort - Spiegazione Semplice

## Situazione di partenza

Hai un pod con nginx che ascolta sulla porta 80.

Il pod ha IP `172.17.0.5` - ma questo IP funziona **solo dentro il cluster**.

## Cosa fa ClusterIP (tipo Service di default)

Crei un Service ClusterIP:
- Kubernetes gli assegna IP `10.96.5.10`
- Questo IP funziona **solo dentro il cluster**
- Altri pod possono chiamare `10.96.5.10:8080` → arriva al pod porta 80

**Problema**: tu, dal tuo laptop, non puoi raggiungere né `172.17.0.5` né `10.96.5.10` perché sono IP interni al cluster.

## Cosa fa NodePort

Dici a Kubernetes: "voglio accedere a questo Service dall'esterno".

Kubernetes fa questo:
1. Crea comunque il ClusterIP (10.96.5.10)
2. **Apre una porta su ogni nodo fisico del cluster** (esempio: porta 30080)

Ora hai questa catena:

```
Il tuo browser → IP del nodo (192.168.1.100:30080) → Service (10.96.5.10:8080) → Pod (172.17.0.5:80)
```

## Esempio concreto

Cluster con 3 nodi:
- Nodo1: `192.168.1.101`
- Nodo2: `192.168.1.102`
- Nodo3: `192.168.1.103`

Crei NodePort su porta 30080.

Kubernetes apre porta 30080 su **tutti e 3 i nodi**.

Puoi accedere da:
- `192.168.1.101:30080` → funziona
- `192.168.1.102:30080` → funziona
- `192.168.1.103:30080` → funziona

Tutti e 3 ti portano allo stesso Service, che poi porta al pod.

## La parte chiave

NodePort **non sostituisce** ClusterIP. Lo **estende**.

Prima: solo comunicazione interna
Dopo: comunicazione interna + porta esposta sui nodi fisici

 
### LoadBalancer
```
Cloud Provider → Load Balancer esterno (IP pubblico)
                         ↓
                    NodePort (creato automaticamente)
                         ↓
                    Service ClusterIP
                         ↓
                       Pods
```

**Nota:** Funziona solo su cloud provider (AWS/GCP/Azure). Su bare-metal/killercoda non disponibile.


# LoadBalancer Service - L'ultimo tipo di Service

## Il problema che risolve

**Con NodePort:**
- Devi usare IP dei nodi: `192.168.1.100:30080`
- Se il nodo si rompe, quell'IP non funziona più
- Devi gestire tu il bilanciamento tra i nodi
- Non hai un singolo punto di ingresso stabile

**In produzione vuoi:**
- Un IP pubblico fisso (`203.0.113.50`)
- Alta disponibilità automatica
- Bilanciamento del carico tra i nodi

## La soluzione: LoadBalancer

Quando crei Service tipo LoadBalancer, Kubernetes chiede al **cloud provider** (AWS, GCP, Azure) di creare un load balancer esterno vero.

**Cosa succede:**

1. Crei Service tipo LoadBalancer
2. Kubernetes parla con le API del cloud (es. AWS)
3. AWS crea un Elastic Load Balancer
4. Ti assegna un IP pubblico fisso (o un hostname)
5. Il load balancer AWS distribuisce traffico ai tuoi nodi

## Come funziona

```
Internet → Load Balancer AWS (IP pubblico) → NodePort sui nodi → Service → Pod
```

**Nota importante**: LoadBalancer **include** anche NodePort e ClusterIP.

È una "cipolla" a strati:
- LoadBalancer (esterno)
  - NodePort (sui nodi)
    - ClusterIP (interno)
      - Pod

## Limiti

**Problema 1**: funziona **solo su cloud** (AWS, GCP, Azure, DigitalOcean)
- Su cluster locale (minikube, kind) non hai cloud provider
- Non crea il load balancer esterno, rimane "pending"

**Problema 2**: **un LoadBalancer per ogni Service**
- Costi: ogni load balancer AWS costa ~$20/mese
- Se hai 10 applicazioni = 10 load balancer = $200/mese

**Soluzione in produzione**: usi **1 LoadBalancer per l'Ingress Controller**, poi Ingress gestisce routing interno.

```
LoadBalancer → Ingress Controller → tanti Service (via regole Ingress)
```

Così paghi 1 load balancer per tutto il cluster.


---

## 5. Ingress - Il reverse proxy per HTTP ovvero Routing HTTP/HTTPS

### Il problema che risolve

Con NodePort hai limitazioni:
- Ogni Service occupa una porta diversa (30080, 30081, 30082...)
- Con 50 applicazioni = 50 porte diverse
- Gli utenti vogliono URL normali: `myapp.com/api`, `myapp.com/frontend`

esempio Hai 3 applicazioni nel cluster:
- Frontend
- API Backend  
- Dashboard admin

Con NodePort dovresti fare:
- `192.168.1.100:30080` → frontend
- `192.168.1.100:30081` → backend
- `192.168.1.100:30082` → dashboard

**Problemi:**
- Porte brutte da ricordare
- Non puoi usare domini (esempio.com)
- Non puoi fare routing per path (`/api`, `/admin`)
- Nessun SSL/HTTPS centralizzato
- In produzione vorresti: `esempio.com` → frontend, `esempio.com/api` → backend

## La soluzione: Ingress

Ingress ti permette di dire:

```
esempio.com/          → Service frontend (porta 80)
esempio.com/api/      → Service backend (porta 8080)  
esempio.com/admin/    → Service dashboard (porta 3000)
```

### La soluzione

**Ingress = reverse proxy HTTP(S) dentro Kubernetes**

```
User → http://world.universe.mine:30080/europe
              ↓
       Nginx Ingress Controller (pod che gira nel cluster)
              ↓ (legge le Ingress resources)
       Service europe:80
              ↓
       Pod europe:80
```

Tutto attraverso **una sola porta** (80 o 443) usando domini e path per instradare.

## Componenti necessari (importante!)

Ingress ha **2 parti**:

1. **Ingress Resource** - file YAML dove scrivi le regole di routing
2. **Ingress Controller** - pod che legge le regole e fa il lavoro vero (esempio: nginx, traefik)

**Analogia**: Ingress Resource è il "menu del ristorante", Ingress Controller è il "cameriere che porta i piatti".

## Come funziona
Il "doppio ruolo" dell'Ingress Controller
L'Ingress Controller (es. NGINX) ha bisogno di ricevere traffico dall'esterno per poterlo poi instradare ai tuoi servizi.
Ma come ci arriva il traffico all'Ingress Controller stesso?
Tramite un Service. E quel Service è di tipo LoadBalancer.


1. Installi Ingress Controller (es. nginx) → crea un pod nginx nel cluster
2. Questo pod nginx è esposto tramite LoadBalancer o NodePort
3. Crei Ingress Resource con le tue regole
4. Controller legge le regole e configura nginx automaticamente
5. Traffico arriva al Controller → lui decide dove mandarlo

**Flusso:**
```
Browser → Ingress Controller (nginx pod) → Service corretto → Pod
```

Il Controller fa da "smistatore intelligente" basandosi su dominio e path.

## Limiti

- Serve installare un Controller (non è incluso di default in tutti i cluster)
- Funziona solo per HTTP/HTTPS (non per database o altri protocolli)
- Configurazione più complessa rispetto a NodePort

 ---

## 6. Ingress Controller vs Ingress Resource

### CRITICO: Sono DUE cose separate!

# Ingress Controller è un pod nginx ma in modalità reverse proxy 
Kubernetes non include un Ingress Controller di default. Devi installarne uno.

## Cosa fa l'Ingress Controller

1. **Legge gli Ingress** che crei nel cluster
2. **Configura un reverse proxy** (tipo Nginx) in base alle tue regole
3. **Espone un service** (di solito LoadBalancer o NodePort) che riceve il traffico HTTP/HTTPS dall'esterno
4. **Instrada le richieste** ai Service giusti in base a host/path

```bash
# Verificare il controller
k -n ingress-nginx get pods
# nginx-ingress-controller-xyz

k -n ingress-nginx get svc
# ingress-nginx-controller  NodePort  ...  80:30080/TCP
#                                            ↑     ↑
#                                    porta interna  porta NodePort
```


# Ingress Controller - cos'è e perché serve

Sì, **devi avere un Ingress Controller** installato nel cluster. L'Ingress da solo è solo una configurazione, serve qualcosa che la legga e la applichi.

## Analogia pratica

- **Ingress** = file di configurazione di Nginx/Apache (le regole che scrivi tu)
- **Ingress Controller** = Nginx/Apache stesso (il software che fa girare quelle regole)


 

## Controller più comuni

- **Nginx Ingress Controller** (il più usato, stabile)
- **Traefik** (auto-discovery, dashboard)
- **Kong** (API Gateway features)
- **HAProxy**

## Installazione rapida (esempio Nginx)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```
 
 ---------------------
### spiegazione basic: 
## Nginx in due ruoli diversi

**Nginx per app frontend (quello che conosci):**
- **Problema**: il browser vuole file HTML/CSS/JS
- **Soluzione**: nginx **serve file statici** dalla cartella `/usr/share/nginx/html`
- **Ruolo**: web server

**Nginx come Ingress Controller:**
- **Problema**: devi instradare richieste HTTP a Service diversi in base a dominio/path
- **Soluzione**: nginx fa da **reverse proxy** 
- **Ruolo**: router/gateway

## Reverse proxy vs Web server

**Web server** (nginx classico):
```
Browser chiede index.html → nginx legge file dal disco → risponde con il file
```

**Reverse proxy** (Ingress Controller):
```
Browser chiede esempio.com/api → nginx **non ha file** → inoltra richiesta a Service backend → risponde con quello che riceve dal Service
```

## Quindi l'Ingress Controller...

**Non serve file** - fa da "postino intelligente":

1. Riceve richiesta HTTP
2. Guarda dominio e path
3. Consulta le regole nell'Ingress Resource
4. **Inoltra** la richiesta al Service corretto
5. Restituisce la risposta al browser

## Esempio concreto

```
esempio.com/         → Controller inoltra a → Service frontend → Pod nginx (questo sì che serve file!)
esempio.com/api/user → Controller inoltra a → Service backend → Pod con app Python
```

Il **Controller nginx** non serve niente, solo instrada.

I **pod dietro ai Service** fanno il lavoro vero (servire file, elaborare API, ecc).

 
 ---------------------

# Ingress Resource
- È la **configurazione YAML** che scrivi tu
- Dice al controller: "per host X e path Y, inoltra al service Z"
- Viene letta dal controller per configurarsi

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: world
  namespace: world
spec:
  ingressClassName: nginx  # Specifica quale controller usare
  rules:
  - host: world.universe.mine
    http:
      paths:
      - path: /europe
        pathType: Prefix
        backend:
          service:
            name: europe
            port:
              number: 80
```

---

## 7. Flusso completo del traffico Ingress

### Esempio pratico
Richiesta: `curl world.universe.mine:30080/europe`

```
1. DNS/hosts risolve world.universe.mine → 172.30.1.2 (Node IP)
                         ↓
2. Richiesta arriva a NodeIP:30080
                         ↓
3. NodePort inoltra al Service ingress-nginx-controller
                         ↓
4. Traffico arriva al pod Nginx Ingress Controller
                         ↓
5. Controller legge Ingress resource, matcha:
   - host: world.universe.mine ✓
   - path: /europe ✓
                         ↓
6. Inoltra al Service backend: europe:80
                         ↓
7. Service europe inoltra al pod con label app=europe
                         ↓
8. Pod risponde
```

### Punti chiave
- **Non inserisci mai il NodePort nell'Ingress resource** - quello è gestito dal Service del controller
- Il controller è già esposto, tu definisci solo le regole di routing
- L'Ingress resource deve essere nello **stesso namespace** dei Services backend

---

## 8. PathType in Ingress

### Prefix vs Exact

```yaml
pathType: Exact
# Matcha SOLO esattamente il path specificato
# path: /europe → matcha /europe, NON /europe/ o /europe/test

pathType: Prefix  
# Matcha tutto ciò che inizia con quel path
# path: /europe → matcha /europe, /europe/, /europe/test, ecc.
```

**Regola pratica:** Usa quasi sempre `Prefix` per applicazioni web.

---

## 9. Annotation rewrite-target

### Il problema
Quando il path dell'Ingress non corrisponde al path che l'app si aspetta:

```
Request: /europe/api
App si aspetta: /api
```

### La soluzione
```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
```

**Cosa fa:**
- Request in arrivo: `/europe/qualcosa`
- Path inoltrato al pod: `/qualcosa` (rimuove il prefisso)

Per `/europe` → diventa `/` (root)

### Quando serve
- L'app nel pod serve contenuto su `/` ma l'Ingress usa path come `/europe`
- Senza annotation: il pod riceve richiesta per `/europe` e non sa cosa rispondere

**Nota per l'esame:** Non si può generare automaticamente. Va aggiunta manualmente se l'Ingress non funziona.

---

## 10. Domande di verifica della comprensione

### Test 1: Service configuration
```yaml
Service:
  port: 3000
  targetPort: 80
  nodePort: 30500
```

**Domande:**
- Come raggiungo il pod dall'interno del cluster?
- Come raggiungo il pod dall'esterno?
- Su quale porta ascolta il container nel pod?

**Risposte:**
- Interno: `service-name:3000`
- Esterno: `node-ip:30500`
- Container: porta 80



---------------------------

# LoadBalancer vs Ingress - Due strade diverse

## Cosa succede con LoadBalancer Service

Quando fai `kubectl expose deploy pippo --type=LoadBalancer`:

1. Kubernetes crea il Service tipo LoadBalancer
2. **Se sei su cloud** (AWS/GCP/Azure):
   - Cloud provider crea load balancer esterno
   - Ti assegna IP pubblico (es. `203.0.113.50`)
   - **Hai già finito** - l'app è esposta su quell'IP pubblico
   
3. **Se sei locale** (minikube/kind):
   - Rimane in stato "pending" perché non c'è cloud provider
   - Non ottieni IP esterno

## NON serve Ingress dopo LoadBalancer

Se usi LoadBalancer Service, l'applicazione è **già esposta all'esterno**.

```
Internet → IP pubblico load balancer (203.0.113.50:80) → direttamente al tuo Service → Pod
```

Ingress non c'entra niente qui.

## Due approcci alternativi

**Approccio 1: LoadBalancer per ogni app** (semplice ma costoso)
```
App1 → LoadBalancer Service → IP pubblico 203.0.113.50
App2 → LoadBalancer Service → IP pubblico 203.0.113.51  
App3 → LoadBalancer Service → IP pubblico 203.0.113.52
```

**Approccio 2: Ingress + 1 solo LoadBalancer** (raccomandato)
```
Tutte le app → ClusterIP Service (interno)
               ↓
            Ingress (regole routing)
               ↓
         Ingress Controller (pod nginx)
               ↓
         LoadBalancer Service (1 solo!)
               ↓
         IP pubblico unico (203.0.113.50)
```

## Quando usi cosa

**LoadBalancer diretto:**
- Test veloce
- App singola
- Non ti importa del costo
- Non serve routing complesso

**Ingress:**
- Produzione
- Multiple app
- Vuoi routing per dominio/path
- Vuoi risparmiare (1 load balancer invece di 10)
- Vuoi gestire SSL centralizzato

Quindi: o LoadBalancer **o** Ingress, non entrambi per la stessa app!

 # Setup Standard in Produzione su Cloud

## Pattern raccomandato

**Per le tue applicazioni:**
- Service tipo **ClusterIP** (quello di default)
- Non esposti direttamente all'esterno

**Per l'ingresso al cluster:**
- 1 Ingress Controller (installato una volta)
- Esposto con LoadBalancer Service
- Ingress Resources per routing

## Come funziona in pratica

**Step 1: Crei i Service interni**
```bash
# Frontend
kubectl expose deploy frontend --port=80 --type=ClusterIP

# Backend  
kubectl expose deploy backend --port=8080 --type=ClusterIP

# Database
kubectl expose deploy database --port=5432 --type=ClusterIP
```

Questi Service hanno **solo ClusterIP** - non sono raggiungibili da internet.

**Step 2: Installi Ingress Controller** (una volta sola)
```bash
kubectl apply -f nginx-ingress-controller.yaml
```

Questo crea:
- Pod nginx che fa da Ingress Controller
- Service tipo **LoadBalancer** per esporre il Controller
- Cloud provider crea load balancer esterno con IP pubblico

**Step 3: Crei Ingress Resources** (regole di routing)
```yaml
# File ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
spec:
  rules:
  - host: esempio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8080
```

## Flusso finale

```
Internet 
  ↓
IP pubblico (203.0.113.50) ← Load Balancer AWS
  ↓
Ingress Controller (pod nginx)
  ↓
Routing basato su path/dominio
  ↓
Service ClusterIP (frontend o backend)
  ↓
Pod
```

## Vantaggi

- **1 solo IP pubblico** per tutte le app
- **1 solo load balancer** da pagare (~$20/mese invece di $200)
- **Routing flessibile** con domini e path
- **SSL centralizzato** sul Controller

## Riassunto

**In produzione:**
- App → ClusterIP Service ✓
- Ingress Controller → LoadBalancer Service ✓ (1 solo)
- Regole → Ingress Resources ✓

Database mai esposto - sempre ClusterIP interno.

 


 ----------------------

# TL;DR Recap Tutorial: Networking in Kubernetes

## 1. Service ClusterIP - Stabilità per i Pod

**Problema:** Pod hanno IP che cambiano ad ogni restart.

**Soluzione:** Service con ClusterIP fisso che:
- Fornisce IP stabile (es. `10.96.5.10`)
- Load balancing tra repliche
- DNS interno (`pippo.default.svc.cluster.local`)

**Dietro le quinte:** kube-proxy crea regole iptables che intercettano traffico al ClusterIP e lo redireggono ai pod reali.

**Limite:** Accessibile solo dall'interno del cluster.

---

## 2. NodePort - Primo accesso esterno

**Problema:** ClusterIP non raggiungibile da fuori cluster.

**Soluzione:** NodePort apre porta (30000-32767) su **tutti i nodi fisici**.

**Flusso:**
```
Browser → IP_nodo:30080 → ClusterIP:8080 → Pod:80
```

**Include:** ClusterIP + porta sui nodi.

**Limite:** Porte brutte, solo per test. Non produzione.

---

## 3. Ingress - Routing intelligente HTTP

**Problema:** Con NodePort hai porte strane, nessun routing per dominio/path.

**Soluzione:** Ingress permette:
```
esempio.com/      → Service frontend
esempio.com/api/  → Service backend
```

**Due componenti:**
- **Ingress Controller** = pod (nginx) che fa reverse proxy
- **Ingress Resource** = regole YAML di routing

**Controller:** non serve file, solo **inoltra** richieste ai Service corretti.

**Limite:** Solo HTTP/HTTPS, serve installare Controller.

---

## 4. LoadBalancer - IP pubblico su cloud

**Problema:** NodePort usa IP dei nodi, non stabile.

**Soluzione:** LoadBalancer chiede al cloud provider (AWS/GCP/Azure) di creare load balancer esterno con IP pubblico fisso.

**Include:** LoadBalancer → NodePort → ClusterIP (a cipolla).

**Limite:** 
- Funziona solo su cloud
- Costoso se ne usi uno per app

---

## 5. Pattern Produzione Standard

**Setup raccomandato:**

1. **App → ClusterIP Service** (interno)
```bash
kubectl expose deploy pippo --port=8080
```

2. **Ingress Controller → LoadBalancer** (installazione una volta)
```bash
kubectl apply -f ingress-nginx-controller.yaml
```
→ Crea automaticamente Service LoadBalancer con IP pubblico

3. **Ingress Resources** (regole routing)
```bash
kubectl create ingress pippoingress --rule="foo.com/bar=pippo:8080"
```

**Flusso completo:**
```
Internet → IP pubblico (LB) → Ingress Controller → Service ClusterIP → Pod
```

**Vantaggio:** 1 solo load balancer per tutte le app, routing flessibile, SSL centralizzato.

---

## 6. Flusso Deployment Completo

```
1. kubectl create deployment pippo --image=nginx
   → Crea Deployment → ReplicaSet → Pod

2. kubectl expose deploy pippo --port=8080
   → Service ClusterIP (interno)

3. kubectl apply -f ingress-controller.yaml  
   → Controller + LoadBalancer automatico

4. kubectl create ingress pippoingress --rule="..."
   → Regole routing

5. Traffico: Internet → LB → Controller → Service → Pod
```



## 8. Network Policies - Il Firewall tra Pod di Kubernetes 

### Il Problema
Default: tutti i pod si parlano. Se frontend compromesso → accesso diretto al database.

### La Soluzione
Policy basata su label:
```yaml
spec:
  podSelector:
    matchLabels:
      app: database  # Chi proteggere
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend  # Chi può accedere
    ports:
    - port: 5432
```

**Pattern:** Default deny (blocca tutto) + whitelist esplicito.

**Prerequisito:** CNI che supporta (Calico ✓, Flannel ✗)

**Quando:** Sempre in produzione per sicurezza e compliance.
 