+++
title = "Kubernetes Networking - Dal Pod all'Ingress"
date = 2026-01-18
draft = false
tags = ["kubernetes","networking","ingress"]
+++


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
1. Kubernetes crea DNS: `my-app.namespace.svc.cluster.local`
2. Assegna ClusterIP virtuale: `10.96.5.10`
3. **kube-proxy** crea regole iptables per distribuire traffico ai pod

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

---

## 5. Ingress - Il reverse proxy per HTTP

### Il problema che risolve

Con NodePort hai limitazioni:
- Ogni Service occupa una porta diversa (30080, 30081, 30082...)
- Con 50 applicazioni = 50 porte diverse
- Gli utenti vogliono URL normali: `myapp.com/api`, `myapp.com/frontend`

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

---

## 6. Ingress Controller vs Ingress Resource

### CRITICO: Sono DUE cose separate!

#### Ingress Controller
- È un **pod** (deployment) che gira nel cluster
- Solitamente è Nginx (ma esistono altri: Traefik, HAProxy, ecc.)
- Esposto tramite Service **NodePort** o LoadBalancer
- **Legge** le Ingress resources e configura il reverse proxy di conseguenza

```bash
# Verificare il controller
k -n ingress-nginx get pods
# nginx-ingress-controller-xyz

k -n ingress-nginx get svc
# ingress-nginx-controller  NodePort  ...  80:30080/TCP
#                                            ↑     ↑
#                                    porta interna  porta NodePort
```

#### Ingress Resource
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

