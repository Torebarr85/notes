
+++
title = "Core Concepts"
date = 2026-01-22
draft = false 
tags = ["kubernetes","cka"]
+++


 
# CLUSTER ARCHITECTURE:

# Recap: Architettura Kubernetes per CKA

## L'Analogia delle Navi 🚢

**Kubernetes = Porto con navi da carico + navi di controllo**

```
┌─────────────────────────────────────────────────────┐
│            CONTROL PLANE (Master Node)              │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐     │
│  │  etcd    │  │Scheduler │  │  Controllers   │     │
│  │(Database)│  │ (Crane)  │  │ (Departments)  │     │
│  └──────────┘  └──────────┘  └────────────────┘     │
│         ┌────────────────────────┐                  │
│         │   kube-apiserver       │                  │
│         │  (Communication Hub)   │                  │
│         └────────────────────────┘                  │
└─────────────────────────────────────────────────────┘
              │              │
              ▼              ▼
    ┌─────────────┐    ┌─────────────┐
    │ Worker Node │    │ Worker Node │
    │    (Ship)   │    │    (Ship)   │
    │             │    │             │
    │  kubelet    │    │  kubelet    │
    │  (Captain)  │    │  (Captain)  │
    │             │    │             │
    │  kube-proxy │    │  kube-proxy │
    │  (Comms)    │    │  (Comms)    │
    │             │    │             │
    │ Containers  │    │ Containers  │
    │  🐳🐳🐳     │    │  🐳🐳🐳     │
    └─────────────┘    └─────────────┘
```

## Componenti Master Node (Control Plane) 🎛️

### 1. **etcd** - Il Database
- Key-value store altamente disponibile
- Memorizza **TUTTO** lo stato del cluster
- Chi è dove, quanti replica, configurazioni
- **Per l'esame**: sai dove trovare i dati del cluster

### 2. **kube-scheduler** - La Gru
- Decide **dove** mettere i nuovi pod
- Valuta: risorse, affinity, taints/tolerations
- Non crea pod, solo decide il posizionamento

### 3. **Controllers** - I Dipartimenti
**Esempi chiave**:
- **Node Controller**: monitora salute dei nodi
- **Replication Controller**: mantiene N repliche attive
- Ognuno ha una responsabilità specifica
- Guardano etcd e correggono discrepanze

### 4. **kube-apiserver** - Il Centro Comando ⭐
- **Cervello del cluster**
- Tutti parlano con lui (kubectl, kubelet, controllers)
- Unico che scrive in etcd
- Espone REST API

## Componenti Worker Node 🔧

### 1. **kubelet** - Il Capitano
- Agente su ogni worker
- Comunica con kube-apiserver
- **Crea/distrugge** i container effettivamente
- Invia status report al master

### 2. **kube-proxy** - Le Comunicazioni
- Gestisce network rules sui nodi
- Permette ai pod di comunicare tra loro
- Implementa i **Services**

### 3. **Container Runtime** - Il Motore
- Docker, containerd, CRI-O
- Esegue i container effettivamente
- Serve su **tutti** i nodi (anche master)

## Flusso Tipico: "Voglio 3 pod nginx"

```
1. kubectl → kube-apiserver
2. apiserver → salva in etcd
3. scheduler → vede nuovo pod, decide nodo
4. apiserver → informa kubelet del nodo scelto
5. kubelet → chiama container runtime
6. container runtime → crea container
7. kubelet → report status → apiserver → etcd
```

## Punti Chiave per CKA 📝

**Master Node**:
- ✅ etcd = database (porta 2379)
- ✅ kube-apiserver = hub centrale (porta 6443)
- ✅ kube-scheduler = assegna nodi
- ✅ controller-manager = corregge lo stato

**Worker Node**:
- ✅ kubelet = gestisce pod sul nodo (porta 10250)
- ✅ kube-proxy = networking
- ✅ container runtime = esegue container

## Domanda Trabocchetto Esame 🎓

**Q: Se kube-apiserver è down, i pod esistenti continuano a funzionare?**
A: **SÌ!** Kubelet e container runtime sono indipendenti. Ma non puoi fare modifiche al cluster.

**Q: Dove sono i componenti master?**
A: Possono essere **processi** o **pod statici** in namespace `kube-system`

---

**Memory tip**: Master = cervello (decide), Worker = muscoli (eseguono). Apiserver è l'unico che parla con tutti.
