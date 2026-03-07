+++
title: "Kubernetes Networking — Esercizi Pratici Offline"
date: 2026-03-07
draft = false
tags: ["kubernetes","networking","CKA","devops"]
+++

> Prerequisiti: k3s running (`kubectl get nodes` → Ready), immagini nginx e busybox già importate
> Tempo stimato: 3-4 ore
> Tutto funziona **completamente offline**

---

## Prima di iniziare


 1. Avvia k3s con internet
sudo systemctl start k3s

# 2. Verifica che il nodo sia Ready
kubectl get nodes

# 3. Importa le immagini che userai
docker pull nginx
docker pull busybox
docker save nginx | sudo k3s ctr images import -
docker save busybox | sudo k3s ctr images import -

# 4. Verifica che k3s le veda
sudo k3s ctr images list | grep -E "nginx|busybox"

```bash
# Verifica che k3s sia up
sudo systemctl start k3s
kubectl get nodes
# → fedora   Ready   control-plane
```

---

## LIVELLO 1 — Pod Networking Base

### Concetto
Ogni Pod in Kubernetes riceve un IP univoco dalla rete interna del cluster. I Pod possono comunicare direttamente tra loro per IP — senza NAT, senza configurazioni extra.

Questa è la **rete flat di Kubernetes**: tutti i Pod si vedono, indipendentemente su quale nodo girano.

### Esercizio 1.1 — Avvia due Pod e falli comunicare

```bash
# Pod A — server nginx
kubectl run pod-a --image=nginx

# Pod B — client busybox (sleep per tenerlo vivo)
kubectl run pod-b --image=busybox --command -- sleep 3600

# Aspetta che siano Running
kubectl get pods -w
# Ctrl+C quando entrambi sono Running
```

```bash
# Trova l'IP di pod-a
kubectl get pod pod-a -o wide
# Nota la colonna IP — es. 10.42.0.15
```

```bash
# Da pod-b, pinga pod-a per IP
kubectl exec -it pod-b -- ping -c 3 <IP_di_pod-a>
```

✅ Il ping funziona — i Pod si parlano direttamente per IP.

```bash
# Da pod-b, fai una richiesta HTTP a pod-a
kubectl exec -it pod-b -- wget -qO- http://<IP_di_pod-a>
# Dovresti vedere l'HTML di benvenuto di nginx
```

### Esercizio 1.2 — Ispeziona la rete dal dentro

```bash
# Vedi le interfacce di rete di pod-a
kubectl exec -it pod-a -- ip addr show
# Nota eth0 con il suo IP — è l'interfaccia virtuale del Pod

# Vedi la routing table di pod-a
kubectl exec -it pod-a -- ip route
```

**Domanda da porsi:** Da dove viene quell'IP? È assegnato da k3s tramite il suo CNI (Container Network Interface) — in k3s si chiama **Flannel**.

---

## LIVELLO 2 — Service e DNS Interno

### Concetto
I Pod sono **effimeri** — muoiono e rinascono con IP diversi. Il **Service** è un oggetto stabile che:
1. Mantiene un IP fisso (ClusterIP)
2. Fa da load balancer verso i Pod selezionati
3. Registra un nome DNS interno risolvibile da tutti i Pod del cluster

### Esercizio 2.1 — Crea un Service

```bash
# Esponi pod-a sulla porta 80
kubectl expose pod pod-a --port=80 --name=servizio-web

# Vedi il Service creato
kubectl get service servizio-web
# Nota la colonna CLUSTER-IP — es. 10.43.0.45
```

```bash
# Da pod-b, raggiungi pod-a per NOME (non per IP)
kubectl exec -it pod-b -- wget -qO- http://servizio-web
# Funziona! Il DNS interno risolve "servizio-web" automaticamente
```

### Esercizio 2.2 — Ispeziona il DNS interno

```bash
# Vedi la configurazione DNS di pod-b
kubectl exec -it pod-b -- cat /etc/resolv.conf
# Vedrai qualcosa come: nameserver 10.43.0.10
# Quello è CoreDNS — il DNS interno di Kubernetes
```

```bash
# Risolvi il nome del service manualmente
kubectl exec -it pod-b -- nslookup servizio-web
# Risponde con il ClusterIP del Service

# Il nome completo è: servizio-web.default.svc.cluster.local
kubectl exec -it pod-b -- nslookup servizio-web.default.svc.cluster.local
```

**Struttura del nome DNS:**
```
<nome-service>.<namespace>.svc.cluster.local
     servizio-web . default . svc.cluster.local
```

### Esercizio 2.3 — Il Service sopravvive alla morte del Pod

```bash
# Cancella pod-a
kubectl delete pod pod-a

# L'IP è sparito — ma il Service esiste ancora
kubectl get service servizio-web

# Ricrea pod-a con la stessa label
kubectl run pod-a --image=nginx --labels=run=pod-a

# Aspetta che sia Running
kubectl get pods -w

# Il nuovo pod-a ha un IP DIVERSO
kubectl get pod pod-a -o wide

# Ma il Service funziona ancora per nome!
kubectl exec -it pod-b -- wget -qO- http://servizio-web
```

✅ **Questo è il motivo per cui esistono i Service** — astraggono l'IP effimero del Pod.

---

## LIVELLO 3 — Deployment + Service (pattern reale)

### Concetto
In produzione non si usano Pod nudi — si usano **Deployment** che gestiscono repliche. Il Service fa da load balancer tra le repliche.

### Esercizio 3.1 — Deployment con più repliche

```bash
# Crea un Deployment con 3 repliche
kubectl create deployment web-app --image=nginx --replicas=3

# Vedi i Pod creati
kubectl get pods -o wide
# Nota che hanno tutti IP diversi

# Esponi il Deployment con un Service
kubectl expose deployment web-app --port=80 --name=web-service
```

```bash
# Da pod-b, fai più richieste — il Service bilancia tra le repliche
kubectl exec -it pod-b -- sh -c "for i in \$(seq 1 5); do wget -qO- http://web-service | grep -o 'nginx'; done"
```

### Esercizio 3.2 — Vedi gli Endpoints

Il Service tiene traccia dei Pod attivi tramite gli **Endpoints**.

```bash
# Vedi gli endpoint del Service (= gli IP dei Pod attivi)
kubectl get endpoints web-service

# Ora scala il Deployment
kubectl scale deployment web-app --replicas=5
kubectl get endpoints web-service
# Gli endpoint aumentano automaticamente

# Scala a 1
kubectl scale deployment web-app --replicas=1
kubectl get endpoints web-service
# Gli endpoint diminuiscono
```

---

## LIVELLO 4 — Debugging Networking (skill CKA)

### Esercizio 4.1 — Pod irraggiungibile: diagnosi

```bash
# Crea un Service che punta a niente (selector sbagliato)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: servizio-rotto
spec:
  selector:
    app: non-esiste
  ports:
  - port: 80
EOF

# Prova a raggiungerlo
kubectl exec -it pod-b -- wget -qO- --timeout=5 http://servizio-rotto
# Timeout! Non risponde
```

**Metodologia di debug:**

```bash
# Step 1 — Il Service esiste?
kubectl get service servizio-rotto

# Step 2 — Ha Endpoints?
kubectl get endpoints servizio-rotto
# → Endpoints: <none>  ← PROBLEMA TROVATO

# Step 3 — Perché non ha Endpoints?
kubectl describe service servizio-rotto
# Guarda "Selector" — punta a label che non esiste su nessun Pod

# Step 4 — Quali label hanno i Pod disponibili?
kubectl get pods --show-labels
```

**Conclusione:** Service senza Endpoints = selector che non matcha nessun Pod. Errore comunissimo in produzione.

```bash
# Cleanup
kubectl delete service servizio-rotto
```

### Esercizio 4.2 — Troubleshooting con un pod di debug

Tecnica fondamentale per il CKA: avviare un pod temporaneo per diagnosticare problemi di rete.

```bash
# Pod di debug usa-e-getta
kubectl run debug --image=busybox --rm -it --restart=Never -- sh

# Dentro il pod, puoi:
wget -qO- http://web-service      # testa HTTP
ping <IP>                          # testa connettività
nslookup web-service               # testa DNS
cat /etc/resolv.conf               # vedi configurazione DNS
exit
```

Il flag `--rm` cancella il pod automaticamente quando esci.

---

## LIVELLO 5 — NodePort (accesso dall'esterno)

### Concetto
Il **ClusterIP** è raggiungibile solo dall'interno del cluster. Il **NodePort** espone il Service su una porta del nodo host — accessibile anche dal tuo browser.

```bash
# Crea un Service NodePort
kubectl expose deployment web-app --port=80 --type=NodePort --name=web-nodeport

# Vedi la porta assegnata
kubectl get service web-nodeport
# Colonna PORT(S): 80:32xxx/TCP — il 32xxx è la NodePort
```

```bash
# Accedi dal browser del tuo pc (fuori dal cluster)
curl http://localhost:<NodePort>
# oppure apri http://localhost:<NodePort> nel browser
```

✅ Ora il servizio è accessibile dall'esterno del cluster!

---

## Riepilogo — Mappa Concettuale

```
[Browser/curl]
      ↓ NodePort (porta sul nodo host)
[Service] ← DNS interno (CoreDNS)
      ↓ ClusterIP + load balancing
[Pod A] [Pod B] [Pod C]  ← rete flat, IP univoci
      ↓
[CNI - Flannel in k3s]
      ↓
[Nodo fisico - il tuo pc]
```

---

## Comandi di Riferimento Rapido

| Obiettivo | Comando |
|---|---|
| IP di un Pod | `kubectl get pod <nome> -o wide` |
| Endpoints di un Service | `kubectl get endpoints <nome>` |
| DNS interno | `kubectl exec <pod> -- nslookup <service>` |
| Shell dentro un Pod | `kubectl exec -it <pod> -- sh` |
| Pod debug temporaneo | `kubectl run debug --image=busybox --rm -it --restart=Never -- sh` |
| Dettaglio Service | `kubectl describe service <nome>` |
| Tutti i Pod con IP | `kubectl get pods -o wide` |

---

## Cleanup Finale

```bash
kubectl delete deployment web-app
kubectl delete service web-service web-nodeport servizio-web
kubectl delete pod pod-a pod-b 2>/dev/null; true
```

---

> **Prossimo passo:** Ingress Controller — come esporre più servizi su un solo IP con routing per path e hostname.


> Prerequisiti: esercizi di networking base completati, k3s running con Traefik
> Tempo stimato: 2-3 ore
> Tutto funziona **completamente offline**

---

## Prima di iniziare

```bash
# Verifica k3s e Traefik
kubectl get nodes
kubectl get pods -n kube-system | grep traefik
# → traefik-xxx   1/1   Running
```

---

## Concetto — Perché Ingress?

Senza Ingress, per esporre due servizi diversi hai bisogno di due NodePort su porte diverse:

```
http://localhost:32001  → frontend
http://localhost:32002  → backend
```

Con Ingress, un solo punto di ingresso su porta 80, routing per path:

```
http://mio-sito.local/        → frontend
http://mio-sito.local/api     → backend
```

L'**Ingress Controller** (Traefik in k3s) è il componente che legge le regole Ingress e smista il traffico.

```
[Browser]
    ↓ porta 80
[Traefik - Ingress Controller]
    ↓ routing per path/hostname
[Service frontend]  [Service backend]
    ↓                    ↓
[Pod frontend]      [Pod backend]
```

---

## Setup — Configura /etc/hosts per i domini locali

Ingress lavora con hostname. Per simulare domini reali in locale:

```bash
# Trova l'IP del nodo
kubectl get nodes -o wide
# Nota la colonna INTERNAL-IP — es. 192.168.1.x oppure 127.0.0.1

# Aggiungi i domini finti al file hosts
sudo nano /etc/hosts
```

Aggiungi questa riga in fondo:

```
127.0.0.1   mio-sito.local api.mio-sito.local
```

Salva e verifica:

```bash
ping -c 1 mio-sito.local
# → risponde da 127.0.0.1
```

---

## LIVELLO 1 — Ingress base con path routing

### Esercizio 1.1 — Crea due servizi da esporre

```bash
# Deployment frontend
kubectl create deployment frontend --image=nginx --replicas=2
kubectl expose deployment frontend --port=80 --name=frontend-service

# Deployment backend (usiamo un'immagine diversa per distinguerli)
kubectl create deployment backend --image=httpd --replicas=2
kubectl expose deployment backend --port=80 --name=backend-service

# Verifica
kubectl get deployments
kubectl get services
```

### Esercizio 1.2 — Crea l'Ingress

```bash
# Genera il manifest con dry-run
kubectl create ingress mio-ingress \
  --rule="mio-sito.local/=frontend-service:80" \
  --rule="mio-sito.local/api=backend-service:80" \
  --dry-run=client -o yaml
```

Salva e applica:

```bash
kubectl create ingress mio-ingress \
  --rule="mio-sito.local/=frontend-service:80" \
  --rule="mio-sito.local/api=backend-service:80" \
  --dry-run=client -o yaml > mio-ingress.yaml

kubectl apply -f mio-ingress.yaml
```

Verifica:

```bash
kubectl get ingress
kubectl describe ingress mio-ingress
```

### Esercizio 1.3 — Testa il routing

```bash
# Frontend (path /)
curl http://mio-sito.local
# → HTML di nginx

# Backend (path /api)
curl http://mio-sito.local/api
# → HTML di Apache httpd
```

✅ Un solo hostname, due servizi diversi per path!

---

## LIVELLO 2 — Ingress con hostname multipli

### Concetto
Invece di distinguere per path, puoi usare **hostname diversi** per servizi diversi.

```
http://mio-sito.local      → frontend
http://api.mio-sito.local  → backend
```

### Esercizio 2.1 — Ingress multi-host

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-multihost
spec:
  rules:
  - host: mio-sito.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  - host: api.mio-sito.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
EOF
```

```bash
# Testa
curl http://mio-sito.local
# → nginx (frontend)

curl http://api.mio-sito.local
# → httpd (backend)
```

---

## LIVELLO 3 — pathType: Exact vs Prefix

### Concetto

| pathType | Comportamento |
|---|---|
| `Prefix` | `/api` matcha `/api`, `/api/users`, `/api/v1/...` |
| `Exact` | `/api` matcha SOLO `/api` — nient'altro |

### Esercizio 3.1 — Sperimenta la differenza

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-pathtype
spec:
  rules:
  - host: mio-sito.local
    http:
      paths:
      - path: /exact
        pathType: Exact
        backend:
          service:
            name: backend-service
            port:
              number: 80
      - path: /prefix
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
EOF
```

```bash
# Exact — solo questo path esatto funziona
curl http://mio-sito.local/exact          # ✅ risponde
curl http://mio-sito.local/exact/altro    # ❌ 404

# Prefix — tutto quello che inizia con /prefix funziona
curl http://mio-sito.local/prefix         # ✅ risponde
curl http://mio-sito.local/prefix/altro   # ✅ risponde
curl http://mio-sito.local/prefix/a/b/c   # ✅ risponde
```

---

## LIVELLO 4 — Annotations Traefik

### Concetto
Le **annotations** sono metadati che passano istruzioni specifiche all'Ingress Controller. Traefik le usa per comportamenti avanzati.

### Esercizio 4.1 — Redirect HTTP → HTTPS

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-redirect
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  rules:
  - host: mio-sito.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
EOF
```

### Esercizio 4.2 — Ispeziona le annotations esistenti

```bash
# Vedi tutte le annotations degli ingress attivi
kubectl get ingress -o yaml | grep -A5 annotations

# Descrivi un ingress specifico
kubectl describe ingress mio-ingress
# Sezione "Annotations" mostra cosa Traefik ha applicato
```

---

## LIVELLO 5 — Debug Ingress (skill CKA)

### Metodologia quando Ingress non funziona

```bash
# Step 1 — L'Ingress esiste e ha regole?
kubectl get ingress
kubectl describe ingress <nome>
# Controlla: Rules, Backend, Address

# Step 2 — I Service esistono?
kubectl get services
# I nomi devono corrispondere esattamente a quelli nell'Ingress

# Step 3 — I Service hanno Endpoints?
kubectl get endpoints
# Se Endpoints: <none> → i Pod non matchano il selector

# Step 4 — I Pod sono Running?
kubectl get pods -o wide

# Step 5 — Traefik sta vedendo l'Ingress?
kubectl logs -n kube-system deployment/traefik
# Cerca errori relativi al tuo hostname o service
```

### Esercizio 5.1 — Ingress rotto da diagnosticare

```bash
# Crea un Ingress con service name sbagliato
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-rotto
spec:
  rules:
  - host: mio-sito.local
    http:
      paths:
      - path: /rotto
        pathType: Prefix
        backend:
          service:
            name: servizio-che-non-esiste
            port:
              number: 80
EOF

# Testa
curl http://mio-sito.local/rotto
# → 404 o 502

# Debug
kubectl describe ingress ingress-rotto
# → vedrai che il backend non è raggiungibile

kubectl get service servizio-che-non-esiste
# → Error: not found ← PROBLEMA TROVATO
```

```bash
# Cleanup
kubectl delete ingress ingress-rotto
```

---

## Riepilogo — Struttura YAML Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nome-ingress
  annotations:               # opzionale — istruzioni per l'Ingress Controller
    chiave: valore
spec:
  rules:
  - host: hostname.locale    # dominio
    http:
      paths:
      - path: /percorso
        pathType: Prefix     # o Exact
        backend:
          service:
            name: nome-service
            port:
              number: 80
```

---

## Comandi di Riferimento Rapido

| Obiettivo | Comando |
|---|---|
| Lista Ingress | `kubectl get ingress` |
| Dettaglio Ingress | `kubectl describe ingress <nome>` |
| YAML Ingress | `kubectl get ingress <nome> -o yaml` |
| Log Traefik | `kubectl logs -n kube-system deployment/traefik` |
| Genera Ingress | `kubectl create ingress nome --rule="host/path=service:porta" --dry-run=client -o yaml` |
| Endpoints service | `kubectl get endpoints <nome>` |

---

## Cleanup Finale

```bash
kubectl delete ingress mio-ingress ingress-multihost ingress-pathtype ingress-redirect 2>/dev/null; true
kubectl delete deployment frontend backend
kubectl delete service frontend-service backend-service

# Rimuovi le righe da /etc/hosts
sudo nano /etc/hosts
# Cancella la riga con mio-sito.local
```

---

> **Prossimo passo:** NetworkPolicy — come controllare quale Pod può parlare con quale altro Pod (firewall interno del cluster).



> Prerequisiti: esercizi Ingress completati, k3s running
> Tempo stimato: 2-3 ore
> Tutto funziona **completamente offline**

---

## Prima di iniziare

```bash
kubectl get nodes
# → fedora   Ready
```

---

## Concetto — Cos'è una NetworkPolicy?

Per default in Kubernetes **tutti i Pod si parlano liberamente** — nessun firewall interno.

NetworkPolicy è il firewall del cluster: definisce **chi può parlare con chi**, a livello di Pod, namespace e porta.

```
Senza NetworkPolicy:
[pod-a] ←→ [pod-b] ←→ [pod-c]   # tutto aperto

Con NetworkPolicy:
[pod-a] → [pod-b]                 # solo questa direzione
[pod-a] ✗ [pod-c]                 # bloccato
```

### Due tipi di regole

| Tipo | Significato |
|---|---|
| `ingress` | Traffico **in entrata** verso il Pod |
| `egress` | Traffico **in uscita** dal Pod |

---

## Setup — Crea i Pod di test

```bash
# Namespace separati per simulare ambienti reali
kubectl create namespace frontend
kubectl create namespace backend
kubectl create namespace database

# Pod in ogni namespace
kubectl run web --image=nginx -n frontend
kubectl run api --image=nginx -n backend
kubectl run db --image=nginx -n database

# Esponi i pod con service
kubectl expose pod web --port=80 -n frontend
kubectl expose pod api --port=80 -n backend
kubectl expose pod db --port=80 -n database

# Aspetta che siano Running
kubectl get pods -A
```

---

## LIVELLO 1 — Default Deny (blocca tutto)

### Concetto
Il pattern più comune in produzione: **blocca tutto per default**, poi apri solo quello che serve.

### Esercizio 1.1 — Verifica che ora tutto è aperto

```bash
# Trova l'IP del pod db
kubectl get pod db -n database -o wide

# Dal pod web, raggiungi db (dovrebbe funzionare — tutto aperto)
kubectl exec -it web -n frontend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local
# → HTML nginx ✅ (ora funziona)
```

### Esercizio 1.2 — Applica Default Deny al namespace database

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: database
spec:
  podSelector: {}       # seleziona TUTTI i pod nel namespace
  policyTypes:
  - Ingress
  - Egress
EOF
```

```bash
# Ora prova di nuovo dal pod web
kubectl exec -it web -n frontend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local
# → timeout ❌ — bloccato!
```

✅ Il namespace database è ora isolato. Nessun Pod può entrare o uscire.

---

## LIVELLO 2 — Apri solo il traffico necessario

### Esercizio 2.1 — Permetti solo al backend di parlare con il database

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-db
  namespace: database
spec:
  podSelector: {}           # si applica a tutti i pod in database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: backend
    ports:
    - port: 80
EOF
```

```bash
# Dal pod api (namespace backend) → db: deve funzionare
kubectl exec -it api -n backend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local
# → HTML nginx ✅

# Dal pod web (namespace frontend) → db: deve essere bloccato
kubectl exec -it web -n frontend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local
# → timeout ❌
```

✅ Solo il backend può raggiungere il database — esattamente come in produzione.

---

## LIVELLO 3 — podSelector: regole per Pod specifici

### Concetto
Finora abbiamo selezionato interi namespace. Con `podSelector` puoi essere più preciso — solo certi Pod con certe label.

### Esercizio 3.1 — Aggiungi label ai Pod

```bash
# Aggiungi label al pod api
kubectl label pod api -n backend role=api

# Crea un secondo pod nel backend senza label
kubectl run api-test --image=busybox -n backend --command -- sleep 3600
```

### Esercizio 3.2 — Permetti solo il pod con label role=api

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-only-api-pod
  namespace: database
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: backend
      podSelector:
        matchLabels:
          role: api
    ports:
    - port: 80
EOF
```

```bash
# Pod api (ha label role=api) → db: funziona
kubectl exec -it api -n backend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local
# → ✅

# Pod api-test (senza label) → db: bloccato
kubectl exec -it api-test -n backend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local
# → ❌
```

---

## LIVELLO 4 — Egress: controlla il traffico in uscita

### Concetto
`egress` controlla cosa un Pod può **raggiungere**, non chi può raggiungerlo.

### Esercizio 4.1 — Il backend può uscire solo verso il database

```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-egress
  namespace: backend
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: database
    ports:
    - port: 80
  - ports:                  # permetti sempre DNS (porta 53)
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
EOF
```

```bash
# Dal backend → database: funziona
kubectl exec -it api -n backend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local
# → ✅

# Dal backend → frontend: bloccato
kubectl exec -it api -n backend -- wget -qO- --timeout=3 http://web.frontend.svc.cluster.local
# → ❌
```

> **Nota importante:** Aggiungi sempre la porta 53 UDP/TCP alle regole egress — altrimenti il DNS interno smette di funzionare e il Pod non riesce a risolvere nessun hostname.

---

## LIVELLO 5 — Debug NetworkPolicy (skill CKA)

### Metodologia quando il traffico è bloccato inaspettatamente

```bash
# Step 1 — Quali NetworkPolicy esistono nel namespace?
kubectl get networkpolicy -n <namespace>
kubectl get networkpolicy -A   # tutti i namespace

# Step 2 — Cosa fanno esattamente?
kubectl describe networkpolicy <nome> -n <namespace>
# Controlla: PodSelector, PolicyTypes, Ingress/Egress rules

# Step 3 — I Pod hanno le label giuste?
kubectl get pods -n <namespace> --show-labels

# Step 4 — I namespace hanno le label giuste?
kubectl get namespace --show-labels
# La label kubernetes.io/metadata.name è aggiunta automaticamente da k8s

# Step 5 — Testa la connettività con un pod temporaneo
kubectl run debug --image=busybox -n <namespace> --rm -it --restart=Never -- sh
# Dentro: wget -qO- --timeout=3 http://<target>
```

### Esercizio 5.1 — NetworkPolicy rotta da diagnosticare

```bash
# Policy con label namespace sbagliata
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: policy-rotta
  namespace: database
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          nome-sbagliato: backend    # ← questa label non esiste
EOF

# Test — bloccato anche se dovrebbe funzionare
kubectl exec -it api -n backend -- wget -qO- --timeout=3 http://db.database.svc.cluster.local

# Debug
kubectl describe networkpolicy policy-rotta -n database
kubectl get namespace backend --show-labels
# → vedi che "nome-sbagliato" non esiste ← PROBLEMA TROVATO

# Fix
kubectl delete networkpolicy policy-rotta -n database
```

---

## Riepilogo — Struttura YAML NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nome-policy
  namespace: namespace-target      # namespace dove si applica
spec:
  podSelector:                     # a quali Pod si applica
    matchLabels:
      app: mia-app                 # {} = tutti i Pod del namespace
  policyTypes:
  - Ingress                        # controlla traffico in entrata
  - Egress                         # controlla traffico in uscita
  ingress:
  - from:
    - namespaceSelector:           # da quali namespace
        matchLabels:
          kubernetes.io/metadata.name: mio-namespace
    - podSelector:                 # da quali Pod (stesso namespace)
        matchLabels:
          role: api
    ports:
    - port: 80
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: database
    ports:
    - port: 5432
  - ports:                         # DNS — sempre necessario
    - port: 53
      protocol: UDP
```

---

## Pattern Comuni in Produzione

| Pattern | Uso |
|---|---|
| Default deny tutto | Baseline di sicurezza per ogni namespace |
| Permetti solo namespace specifici | Isolamento tra ambienti (dev/staging/prod) |
| Permetti solo pod con label | Controllo granulare dentro un namespace |
| Egress solo verso database | Il backend non può uscire su internet |
| Permetti DNS sempre | Necessario in ogni policy egress |

---

## Comandi di Riferimento Rapido

| Obiettivo | Comando |
|---|---|
| Lista policy | `kubectl get networkpolicy -A` |
| Dettaglio policy | `kubectl describe networkpolicy <nome> -n <ns>` |
| Label namespace | `kubectl get namespace --show-labels` |
| Label pod | `kubectl get pods --show-labels -n <ns>` |
| Test connettività | `kubectl run debug --image=busybox --rm -it --restart=Never -n <ns> -- wget -qO- --timeout=3 http://<target>` |

---

## Cleanup Finale

```bash
kubectl delete namespace frontend backend database
```

---

> **Prossimo passo:** RBAC — chi può fare cosa nel cluster (ruoli, serviceaccount, permessi).

---

## RBAC — Chi può fare cosa nel cluster

### Concetto

NetworkPolicy controlla il traffico di rete tra Pod. **RBAC** (Role-Based Access Control) controlla chi può **operare sul cluster** — creare Pod, leggere Secret, cancellare Deployment.

```
[Utente / ServiceAccount]
        ↓
    [RoleBinding]           # collega utente a ruolo
        ↓
      [Role]                # lista di permessi
        ↓
  [risorse + verbi]         # es. pods: get, list, create
```

### Componenti

| Oggetto | Scope | Uso |
|---|---|---|
| `Role` | namespace | permessi dentro un namespace |
| `ClusterRole` | cluster intero | permessi globali |
| `RoleBinding` | namespace | assegna Role a utente/SA |
| `ClusterRoleBinding` | cluster intero | assegna ClusterRole globalmente |

---

### Esercizio 1 — Crea un Role e assegnalo

```bash
# Crea namespace di test
kubectl create namespace rbac-test

# Crea un ServiceAccount (identità per un'app o utente)
kubectl create serviceaccount lettore -n rbac-test

# Crea un Role — può solo leggere i Pod
kubectl create role pod-reader \
  --verb=get,list,watch \
  --resource=pods \
  -n rbac-test \
  --dry-run=client -o yaml
```

```bash
# Applica
kubectl create role pod-reader \
  --verb=get,list,watch \
  --resource=pods \
  -n rbac-test

# Collega il Role al ServiceAccount
kubectl create rolebinding lettore-binding \
  --role=pod-reader \
  --serviceaccount=rbac-test:lettore \
  -n rbac-test
```

### Esercizio 2 — Verifica i permessi

```bash
# Può leggere i pod? ✅
kubectl auth can-i get pods \
  --as=system:serviceaccount:rbac-test:lettore \
  -n rbac-test

# Può cancellare i pod? ❌
kubectl auth can-i delete pods \
  --as=system:serviceaccount:rbac-test:lettore \
  -n rbac-test

# Può leggere i Secret? ❌
kubectl auth can-i get secrets \
  --as=system:serviceaccount:rbac-test:lettore \
  -n rbac-test
```

`kubectl auth can-i` è il comando più utile per debug RBAC — usalo sempre prima di cercare altrove.

### Esercizio 3 — ClusterRole per accesso globale

```bash
# ClusterRole — legge i nodi (risorsa cluster-scoped)
kubectl create clusterrole node-reader \
  --verb=get,list,watch \
  --resource=nodes

# Assegna globalmente
kubectl create clusterrolebinding node-reader-binding \
  --clusterrole=node-reader \
  --serviceaccount=rbac-test:lettore

# Verifica
kubectl auth can-i get nodes \
  --as=system:serviceaccount:rbac-test:lettore
# → yes ✅
```

### Verbi comuni

| Verbo | Operazione |
|---|---|
| `get` | leggi una risorsa specifica |
| `list` | elenca risorse |
| `watch` | osserva cambiamenti in tempo reale |
| `create` | crea nuove risorse |
| `update` | modifica risorse esistenti |
| `patch` | modifica parziale |
| `delete` | cancella risorse |
| `*` | tutto |

### Cleanup

```bash
kubectl delete namespace rbac-test
kubectl delete clusterrole node-reader
kubectl delete clusterrolebinding node-reader-binding
```

---

> **Prossimo passo:** Persistent Volumes — come i Pod gestiscono lo storage persistente.