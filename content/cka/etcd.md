+++
title = "ETCD"
date = 2026-01-22
draft = false 
tags = ["kubernetes","cka"]
+++



# Recap: etcd in Kubernetes - La Memoria del Cluster

## Cos'è e Perché è Cruciale

Quando esegui `kubectl get pods`, ti sei mai chiesto da dove arrivano quelle info? **Tutto viene da etcd**.

Pensa a etcd come al **diario di bordo** della nave: ogni evento nel cluster (pod creato, nodo offline, secret aggiornato) viene scritto qui. È il **database distribuito** che contiene lo stato dell'intero cluster.

**Regola d'oro per l'esame**: Una modifica è completa SOLO quando è scritta in etcd!

```
User → kubectl → apiserver → etcd ✓ (salvato!)
                           ↓
                    controller legge
                           ↓
                    esegue azioni
```

## Cosa Contiene etcd

**Tutto lo stato del cluster**:
- Nodi, Pod, ReplicaSet, Deployments
- Secrets, ConfigMaps, ServiceAccounts
- Roles, RoleBindings
- Configurazioni e policies

## Due Metodi di Deploy

### 1. Setup Manuale (Hard Way)
Quando costruisci il cluster da zero:

```bash
# etcd come servizio systemd
--advertise-client-urls=https://192.168.1.10:2379  # ⚠️ Critico!
--cert-file=/path/to/cert
--initial-cluster controller-0=https://...
```

**Porta standard**: `2379` (ricordala!)  
Questo è l'URL che kube-apiserver usa per parlare con etcd.

### 2. Con kubeadm (Easy Way) ⭐
```bash
# etcd come pod statico in kube-system
kubectl get pods -n kube-system | grep etcd
# Output: etcd-master    1/1    Running
```

## Esplorare etcd (Skill per Troubleshooting!)

```bash
# Entra nel pod
kubectl exec -it etcd-master -n kube-system -- sh

# Vedi tutte le chiavi
etcdctl get / --prefix --keys-only
```

**Struttura organizzata**:
```
/registry/
  ├── minions/      # Nodi worker
  ├── pods/
  ├── replicasets/
  ├── deployments/
  ├── secrets/
  └── ...
```

È come un filesystem - ogni risorsa nella sua "cartella"!

## Alta Disponibilità (HA)

In produzione: **3 o 5 istanze etcd** su master diversi.

```
Master-1          Master-2          Master-3
┌─────┐          ┌─────┐          ┌─────┐
│etcd1│◄────────►│etcd2│◄────────►│etcd3│
└─────┘          └─────┘          └─────┘
```

**Configurazione peer**:
```bash
--initial-cluster=master-1=https://IP:2380,master-2=...
```

**Due porte**:
- `2379` → comunicazione client (apiserver)
- `2380` → comunicazione peer (tra istanze etcd)

## Architettura Importante

**Solo kube-apiserver scrive in etcd!**

Tutti gli altri componenti (controller, scheduler, kubelet) passano attraverso l'apiserver. Questo garantisce validazione e sicurezza - è un design pulito e controllato.

## Punti Chiave per CKA 🎯

✅ **Backup cluster** = backup di etcd (è il cervello!) Quando nell'esame ti chiedono di fare backup del cluster, significa fare backup di etcd!
✅ **Porta 2379** - impara a memoria  
✅ **Namespace**: `kube-system` (con kubeadm)  
✅ **Se etcd è down** → cluster praticamente morto  
✅ **Comando**: `etcdctl` per interrogare il DB  
✅ **Troubleshooting**: "La verità è in etcd" - se qualcosa non torna, guarda cosa c'è memorizzato.

**Pro tip esame**: Se ti chiedono dove sono memorizzate le info del cluster o come fare backup, la risposta è sempre etcd!