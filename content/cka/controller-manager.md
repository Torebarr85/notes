+++
title = "kube-controller-manager"
date = 2026-01-22
draft = false 
tags = ["kubernetes","cka"]
+++


# kube-controller-manager - Il Cervello Operativo

## Cosa Fa il Controller Manager?

lavora continuamente per **correggere** le discrepanze tra lo stato attuale e quello desiderato.

## Il Concetto di Controller

Un controller è un **processo che loop infinito** che fa sempre la stessa cosa:

```
1. Guarda lo stato attuale (via kube-apiserver)
2. Lo confronta con lo stato desiderato
3. Se sono diversi, agisce per correggerlo
4. Ripeti ogni X secondi
```

**Principio fondamentale**: I controller non "eseguono comandi", ma continuamente **riconciliano lo stato** del cluster.

## Esempi di Controller Principali

### 1. Node Controller - Il Guardiano dei Nodi

Monitora la salute dei nodi worker e prende decisioni quando qualcosa va storto.

**Timing critici per l'esame** ⏱️:
```
Heartbeat check: ogni 5 secondi
                    ↓
Nodo non risponde
                    ↓
Aspetta: 40 secondi → marca "Unreachable"
                    ↓
Grace period: 5 minuti
                    ↓
Se ancora down → Evacua i pod su nodi sani
```

**Parametri configurabili**:
```bash
--node-monitor-period=5s           # Ogni quanto controlla
--node-monitor-grace-period=40s    # Prima di marcarlo unreachable
--pod-eviction-timeout=5m          # Prima di evacuare i pod
```

### 2. Replication Controller

Assicura che il numero desiderato di pod sia sempre in esecuzione.

**Esempio pratico**:
```
Stato desiderato: 3 repliche
Stato attuale: 2 repliche (1 pod è crashato)
                    ↓
Replication Controller vede la differenza
                    ↓
Crea 1 nuovo pod per arrivare a 3
```

Loop continuo: "Quanti pod ci sono? Quanti ne servono? Agisco!"

### 3. Altri Controller Importanti

Il controller manager include TANTI controller, ognuno con una responsabilità:

```
┌─────────────────────────────────────┐
│   kube-controller-manager           │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Node Controller             │    │
│  │ Replication Controller      │    │
│  │ Deployment Controller       │    │
│  │ StatefulSet Controller      │    │
│  │ DaemonSet Controller        │    │
│  │ Job Controller              │    │
│  │ CronJob Controller          │    │
│  │ Service Account Controller  │    │
│  │ Endpoint Controller         │    │
│  │ Namespace Controller        │    │
│  │ PersistentVolume Controller │    │
│  │ ...e molti altri            │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**Tutti questi controller** girano in un **singolo processo**!

## Come Comunicano i Controller

**Importante**: Nessun controller parla direttamente con etcd o con altri componenti.

```
Controller → kube-apiserver → etcd
              ↑
              └─── (unico punto di accesso)
```

Questo design mantiene tutto centralizzato e controllato.

## Configurazione e Setup

### Setup con kubeadm
```bash
# Controller manager come pod statico
kubectl get pods -n kube-system | grep controller-manager

# Vedi configurazione
cat /etc/kubernetes/manifests/kube-controller-manager.yaml
```

### Setup manuale
```bash
# Download binario
wget https://storage.googleapis.com/.../kube-controller-manager

# File servizio systemd
/etc/systemd/system/kube-controller-manager.service

# Avvia servizio
systemctl start kube-controller-manager
```

## Opzioni Importanti

**Timing del Node Controller** (ricorda per l'esame!):
```bash
--node-monitor-period=5s
--node-monitor-grace-period=40s
--pod-eviction-timeout=5m0s
```

**Scegliere quali controller abilitare**:
```bash
--controllers=*                    # Tutti (default)
--controllers=deployment,job       # Solo alcuni
--controllers=*,-cloud-node        # Tutti tranne cloud-node
```

**Leader election** (per HA):
```bash
--leader-elect=true  # Solo un'istanza attiva alla volta
```

## Troubleshooting

**Problema comune**: Un controller non sembra funzionare

```bash
# 1. Controlla se il controller manager è running
kubectl get pods -n kube-system | grep controller  # (kubeadm)
systemctl status kube-controller-manager           # (manual)

# 2. Vedi i log
kubectl logs kube-controller-manager-master -n kube-system
journalctl -u kube-controller-manager

# 3. Controlla quali controller sono abilitati
# Guarda l'opzione --controllers nel file di configurazione

# 4. Controlla se riesce a comunicare con apiserver
# Guarda i certificati e l'URL dell'apiserver nelle opzioni
```

## Esempio di Reconciliation Loop in Azione

**Scenario**: Elimini manualmente un pod che fa parte di un ReplicaSet

```
1. ReplicaSet desidera: 3 pod
2. Tu elimini 1 pod manualmente
3. Stato attuale: 2 pod
4. Replication Controller (ogni ~15 sec):
   "Dovrebbero essere 3, ne vedo 2"
5. Replication Controller → apiserver:
   "Crea 1 nuovo pod"
6. apiserver → etcd (salva richiesta)
7. Scheduler vede nuovo pod → assegna nodo
8. kubelet crea il pod
9. Stato attuale: 3 pod ✓
10. Controller: "Tutto ok!" (fino al prossimo check)
```

Ecco perché non puoi "ingannare" Kubernetes eliminando pod - i controller li ricreano!

## Punti Chiave per CKA 🎯

✅ **Tutti i controller** in **un unico processo**  
✅ **Node Controller timing**: 5s / 40s / 5m - **impara questi numeri!**  
✅ **Reconciliation loop**: stato desiderato vs stato attuale  
✅ **Comunicazione**: Solo via kube-apiserver  
✅ **Leader election**: In HA, solo uno attivo alla volta  
✅ **Namespace**: `kube-system` (con kubeadm)  
✅ **Opzione --controllers**: Per debug se un controller non funziona

## Metafora Finale

Il controller manager è come un **team di ispettori qualità** in una fabbrica:
- Ispettore A controlla i macchinari ogni 5 secondi
- Ispettore B conta i prodotti finiti
- Ispettore C verifica gli ordini aperti
- Se trovano discrepanze, mandano istruzioni per correggere
- Non aspettano che qualcuno gli dica cosa fare - **lavorano continuamente in loop**

**Pro tip esame**: Se un pod/deployment non si comporta come dovrebbe (es. pod non ricreato dopo eliminazione), il primo sospettato è il controller manager. Controlla i suoi log!