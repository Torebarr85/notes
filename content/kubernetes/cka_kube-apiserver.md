+++
title = "kube-apiserver"
date = 2026-01-13
draft = false
tags = ["kubernetes","cka"]
+++


# CKA - Design a Kubernetes Cluster

## kube-apiserver

L'apiserver è un pod che gira nel namespace `kube-system`.

### Comandi base per ispezionare l'apiserver

```bash
# Vedere tutti i pod di sistema
kubectl get pods -n kube-system

# Trovare il file di configurazione
cat /etc/kubernetes/manifests/kube-apiserver.yaml

# Vedere il processo in esecuzione
ps -aux | grep kube-apiserver
```

---

## Pod vs Container: i due livelli di troubleshooting

**Concetto chiave:** Un Pod CONTIENE uno o più container.

L'apiserver è:
- Un **Pod** (dal punto di vista Kubernetes)
- Che contiene **un container** (dal punto di vista del runtime)

### I due livelli di analisi

```
Livello Kubernetes (alto livello)
└─ kubectl get pods → mostra i Pod

Livello Runtime (basso livello)  
└─ crictl ps → mostra i container dentro i Pod
```

---

## Cosa significa "ps"?

**ps = Process Status** (comando Unix storico per vedere i processi)

```bash
# Su Linux
ps aux  # mostra tutti i processi in esecuzione

# Con Docker
docker ps  # mostra i container in esecuzione

# Con crictl (stesso concetto)
crictl ps  # mostra i container in esecuzione
```

### L'opzione -a (all)

```bash
crictl ps     # solo container attivi
crictl ps -a  # tutti i container, anche quelli fermati/crashati
```

---

## Journalctl e kubelet

Kubelet è **il componente che gestisce tutto su ogni nodo**. Si occupa di:

- Leggere i manifest in `/etc/kubernetes/manifests/`
- Comunicare al container runtime: "avvia questo container"
- Monitorare lo stato dei Pod
- Comunicare con l'apiserver

**Quando qualcosa va storto**, kubelet scrive nei log messaggi tipo:
- "Non riesco ad avviare il container kube-apiserver"
- "Manifest malformato"
- "Container crashato 10 volte"

---

## Workflow di troubleshooting completo

```bash
# 1. Livello Kubernetes - il Pod esiste?
kubectl get pods -n kube-system | grep apiserver
# Se kubectl non funziona (apiserver down), scendi al livello sotto

# 2. Livello Container - il container è in esecuzione?
crictl ps -a | grep apiserver

# 3. Se il container c'è ma è crashato, leggi i suoi log
crictl logs <container-id>

# 4. Se il container non esiste, controlla cosa dice kubelet
journalctl -u kubelet -n 100
# Cerca errori tipo "failed to create container"
```

---

## Sintesi rapida

- **`ps`** = "fammi vedere cosa sta girando"
- **`crictl ps`** = per vedere i container a basso livello
- **`journalctl -u kubelet`** = per vedere cosa sta facendo/segnalando kubelet

### Regola d'oro
**Se kubectl non funziona → prima cosa controlla l'apiserver**