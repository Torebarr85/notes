+++
title = "kube-scheduler"
date = 2026-01-22
draft = false 
tags = ["kubernetes","cka"]
+++

# kube-scheduler 

## Il Ruolo dello Scheduler : Errore comune da evitare Lo scheduler **NON crea i pod**! 

```
Scheduler → Decide "pod X va sul node-2"
kubelet → Crea effettivamente il pod sul node-2
```

Pensa allo scheduler come a un **direttore logistico al porto**: guarda i container in arrivo, esamina le navi disponibili, e decide "questo container va su quella nave". Ma non è lui che carica fisicamente i container - quello lo fa il capitano (kubelet)!

## Perché Serve uno Scheduler?

Immagina di avere:
- 5 nodi worker con capacità diverse
- Pod che richiedono CPU/memoria diverse
- Nodi con etichette speciali (es. "SSD", "GPU")
- Vincoli di affinità ("questo pod deve stare vicino a quest'altro")

Senza uno scheduler, dove metteresti ogni pod? Lo scheduler risolve questo problema **automaticamente**.

## Il Processo Decisionale in 2 Fasi

Quando arriva un nuovo pod, lo scheduler segue sempre questi step:

### Fase 1: Filtering (Scartare i Nodi Inadatti)

```
Pod richiede: 4 CPU, 8GB RAM

Node-1: 2 CPU, 4GB RAM  → ❌ FILTRATO (troppo piccolo)
Node-2: 8 CPU, 16GB RAM → ✓ OK
Node-3: 2 CPU, 16GB RAM → ❌ FILTRATO (CPU insufficienti)
Node-4: 16 CPU, 32GB RAM → ✓ OK
```

**Filtri comuni**:
- Risorse insufficienti (CPU, memoria)
- Taints/Tolerations mismatch
- NodeSelector non corrisponde
- Pod affinity/anti-affinity non soddisfatta

### Fase 2: Ranking (Scegliere il Migliore)

Tra i nodi che hanno passato il filtro, lo scheduler assegna un **punteggio da 0 a 10**.

```
Dopo il filtering rimangono: Node-2 e Node-4

Calcolo: "Quante risorse rimarranno libere?"

Node-2: 8 CPU totali - 4 usate = 4 CPU libere  → Score: 5/10
Node-4: 16 CPU totali - 4 usate = 12 CPU libere → Score: 9/10

Vincitore: Node-4 ✓
```

**Funzioni di priorità** (priority functions):
- Risorse libere dopo il posizionamento
- Bilanciamento del carico tra nodi
- Vicinanza ai volumi persistenti richiesti
- Rispetto delle regole di affinity

## Il Flusso Completo

```
1. Utente: kubectl create pod my-app
           ↓
2. apiserver: Salva pod in etcd (status: Pending)
           ↓
3. Scheduler (loop ogni ~1s):
   "Vedo pod senza nodo assegnato!"
           ↓
4. Filtering: Scarta nodi inadatti
           ↓
5. Ranking: Calcola score per nodi rimasti
           ↓
6. Scheduler → apiserver:
   "Pod my-app va su node-3"
           ↓
7. apiserver: Aggiorna etcd (nodeName: node-3)
           ↓
8. kubelet su node-3:
   "Ho un nuovo pod assegnato a me!"
           ↓
9. kubelet: Crea il pod effettivamente
```

## Configurazione e Setup

### Setup con kubeadm
```bash
# Scheduler come pod statico
kubectl get pods -n kube-system | grep scheduler

# Output:
# kube-scheduler-master   1/1   Running

# Vedi configurazione
cat /etc/kubernetes/manifests/kube-scheduler.yaml
```

### Setup manuale
```bash
# Download binario
wget https://storage.googleapis.com/.../kube-scheduler

# File servizio systemd
/etc/systemd/system/kube-scheduler.service

# Opzione importante: file di configurazione
--config=/etc/kubernetes/scheduler-config.yaml
```

## Customizzazione (Avanzato)

Lo scheduler è **altamente customizzabile**:

**Puoi scrivere il tuo scheduler!** Kubernetes supporta:
- Multiple schedulers contemporaneamente
- Plugin custom per logica di scheduling personalizzata
- Policy files per modificare i pesi delle funzioni di priorità

```yaml
# Nel pod spec puoi specificare quale scheduler usare
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  schedulerName: my-custom-scheduler  # ← Scheduler custom!
  containers:
  - name: nginx
    image: nginx
```

## Argomenti Avanzati (Approfondiremo Dopo)

Il corso ha un'intera sezione sulla scheduling perché ci sono molti concetti:

**Resource Management**:
- Requests vs Limits
- ResourceQuotas

**Pod Placement**:
- NodeSelector
- Node Affinity/Anti-affinity
- Pod Affinity/Anti-affinity
- Taints & Tolerations

**Scheduling Policies**:
- Priority Classes
- PriorityQueues

Non preoccuparti se non li conosci ancora - sono tutti nella sezione dedicata!

## Troubleshooting

**Problema comune**: Pod rimane in stato "Pending"

```bash
# 1. Vedi perché non viene schedulato
kubectl describe pod my-pod

# Output possibile:
# Events:
#   Warning  FailedScheduling  pod has unbound PersistentVolumeClaims
#   Warning  FailedScheduling  0/3 nodes available: insufficient cpu

# 2. Controlla lo scheduler stesso
kubectl get pods -n kube-system | grep scheduler
kubectl logs kube-scheduler-master -n kube-system

# 3. Setup manuale: controlla il servizio
systemctl status kube-scheduler
journalctl -u kube-scheduler
```

**Debug tip**: Il `kubectl describe pod` nella sezione Events ti dice ESATTAMENTE perché lo scheduler non riesce a posizionare il pod!

## Punti Chiave per CKA 🎯

✅ **Scheduler DECIDE**, kubelet CREA  
✅ **Due fasi**: Filter (scarta) → Rank (punteggio)  
✅ **Pod Pending**: Usa `kubectl describe` per vedere il motivo  
✅ **Namespace**: `kube-system` (con kubeadm)  
✅ **Customizzabile**: Puoi avere multiple schedulers  
✅ **Opzione --config**: Specifica file di configurazione scheduler  
✅ **Loop continuo**: Controlla ogni ~1 secondo per nuovi pod

## Metafora Recap

**Scheduler = Tetris master**:
- Guarda i "pezzi" (pod) che arrivano
- Esamina il "campo di gioco" (nodi disponibili)
- Calcola la migliore posizione possibile
- Comunica la decisione
- Il "giocatore" (kubelet) piazza effettivamente il pezzo

**Differenza chiave**: Lo scheduler decide la strategia, kubelet esegue l'azione!

**Pro tip esame**: Se un pod è Pending, NON è colpa di kubelet (lui non ha ancora ricevuto il lavoro). È lo scheduler che non trova un nodo adatto - usa `describe` per capire perché!