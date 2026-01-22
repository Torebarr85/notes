+++
title = "Kube ApiServer"
date = 2026-01-22
draft = false 
tags = ["kubernetes","cka"]
+++

# Recap: kube-apiserver - Il Centro di Comando

## Il Componente Più Importante di Kubernetes

L'apiserver è:
- Un **Pod** (dal punto di vista Kubernetes)
- Che contiene **un container** (dal punto di vista del runtime)
  
Se Kubernetes fosse una città, il **kube-apiserver** sarebbe il municipio dove tutti devono andare per fare qualsiasi cosa ufficiale. È letteralmente il **centro nevralgico** del cluster.

Quando esegui `kubectl get pods`, dietro le quinte stai parlando con il kube-apiserver. Quando lo scheduler decide dove mettere un pod, comunica con il kube-apiserver. Quando kubelet aggiorna lo stato di un container, indovina? Parla con il kube-apiserver!

**Concetto chiave**: Nessun componente parla direttamente con etcd tranne il kube-apiserver. Tutti gli altri passano da lui.

## Il Flusso di Creazione di un Pod (Step by Step)

Vediamo cosa succede quando crei un pod - questo diagramma è fondamentale per capire come lavora Kubernetes:

```
1. kubectl create pod
        ↓
2. kube-apiserver
   ├─ Autentica
   ├─ Valida
   └─ Crea oggetto Pod (senza nodo)
        ↓
3. Scrive in etcd → "Pod xyz creato, stato: Pending"
        ↓
4. Scheduler monitora apiserver
   └─ Vede nuovo pod senza nodo
   └─ Decide: "va sul node-2"
   └─ Comunica ad apiserver
        ↓
5. apiserver aggiorna etcd → "Pod xyz assegnato a node-2"
        ↓
6. kubelet su node-2 monitora apiserver
   └─ Vede nuovo pod per lui
   └─ Chiama container runtime
   └─ Crea il container
        ↓
7. kubelet → apiserver → "Pod running!"
        ↓
8. apiserver → etcd (aggiorna stato finale)
```

**Il pattern**: Tutti comunicano ATTRAVERSO l'apiserver, non direttamente tra loro!

## Responsabilità Principali

**4 compiti fondamentali**:

1. **Autenticare** - Chi sei? (certificati, token)
2. **Validare** - La tua richiesta ha senso? (YAML corretto, permessi)
3. **Recuperare dati** - Legge da etcd
4. **Aggiornare dati** - Scrive in etcd

**Unico componente con accesso diretto a etcd** ⭐

## Due Modi per Interagire

### 1. Via kubectl (più comune)
```bash
kubectl get pods
# kubectl → apiserver → etcd → risposta
```

### 2. Via API REST diretta
```bash
curl -X POST https://kube-apiserver:6443/api/v1/namespaces/default/pods \
  -H "Authorization: Bearer $TOKEN" \
  -d @pod.json
```

Stesso risultato, ma kubectl è più comodo!

## Architettura e Connessioni

```
┌────────────────────────────────────────┐
│         kube-apiserver                 │
│         (Port 6443)                   │
│                                        │
│  ┌──────────┐  ┌──────────────────┐    │
│  │  Auth    │  │   Validation     │    │
│  └──────────┘  └──────────────────┘    │
└────────┬───────────────────┬───────────┘
         │                   │
         ▼                   ▼
    ┌────────┐          ┌────────┐
    │  etcd  │          │ Other  │
    │ (2379) │          │ comps  │
    └────────┘          └────────┘
         ▲                   │
         │                   │
         └───────────────────┘
    (unico che scrive in etcd)
```

**Componenti che parlano con apiserver**:
- kubectl (utenti)
- kube-scheduler
- kube-controller-manager
- kubelet (da ogni nodo)
- kube-proxy

## Configurazione del Servizio

### Setup con kubeadm (easy)
Cosa significa: Usi un tool chiamato kubeadm che fa quasi tutto il lavoro sporco per te.
```bash
# Installi kubeadm
sudo apt-get install kubeadm kubelet kubectl

# Inizializzi il master
sudo kubeadm init

# E voilà! Il cluster è pronto

# apiserver come pod statico
kubectl get pods -n kube-system | grep apiserver

# Vedi le opzioni
cat /etc/kubernetes/manifests/kube-apiserver.yaml

```

### Setup manuale (hard way)
Cosa significa: Fai tutto a mano, passo dopo passo. Scarichi i binari, crei i certificati, scrivi i file di configurazione, configuri i servizi systemd.
```bash
# File servizio systemd
/etc/systemd/system/kube-apiserver.service

# Vedi processo in esecuzione
ps aux | grep kube-apiserver

# dove trovi i componenti? I componenti girano come servizi systemd
systemctl status kube-apiserver
systemctl status etcd
systemctl status kube-scheduler
```
Perché è Importante per l'Esame?
Nell'esame CKA potrebbero darti un cluster fatto in uno dei due modi, e devi saper lavorare con entrambi.
Esempio Pratico - Debug kube-apiserver
Se è setup kubeadm:
```bash
# Vedi se il pod è running
kubectl get pods -n kube-system

# Leggi i log
kubectl logs kube-apiserver-master -n kube-system

# Modifica configurazione
vim /etc/kubernetes/manifests/kube-apiserver.yaml
# (kubelet ricarica automaticamente)
Se è setup manuale:
bash# Vedi se il servizio è attivo
systemctl status kube-apiserver

# Leggi i log
journalctl -u kube-apiserver

# Modifica configurazione
vim /etc/systemd/system/kube-apiserver.service
systemctl daemon-reload
systemctl restart kube-apiserver
```

## Opzioni Importanti da Conoscere

Il kube-apiserver ha **tantissime** opzioni (non devi ricordarle tutte!), ma alcune sono cruciali:

**Connessione a etcd**:
```bash
--etcd-servers=https://127.0.0.1:2379
```
Dove trovare etcd - fondamentale!

**Certificati** (approfondiremo più avanti):
```bash
--client-ca-file=/path/to/ca.crt
--tls-cert-file=/path/to/apiserver.crt
--tls-private-key-file=/path/to/apiserver.key
```

**Porta**:
```bash
--secure-port=6443  # Porta standard HTTPS
```

## Troubleshooting per l'Esame

**Scenario comune**: apiserver non parte

```bash
# 1. Controlla lo stato del servizio
systemctl status kube-apiserver  # (setup manuale)

# 2. Controlla il pod
kubectl get pods -n kube-system  # (kubeadm)

# 3. Vedi i log
journalctl -u kube-apiserver  # (setup manuale)
kubectl logs kube-apiserver-master -n kube-system  # (kubeadm)

# 4. Errore comune: non riesce a connettersi a etcd
# Controlla --etcd-servers nelle opzioni
```

## Punti Chiave per CKA 🎯

✅ **Porta**: `6443` (HTTPS secure port)  
✅ **Namespace**: `kube-system` (come pod con kubeadm)  
✅ **Unico writer di etcd**: Nessun altro componente tocca etcd direttamente  
✅ **Hub centrale**: Tutti i componenti comunicano attraverso lui  
✅ **Autenticazione**: Prima controlla chi sei, poi cosa puoi fare  
✅ **File config**: `/etc/kubernetes/manifests/kube-apiserver.yaml` (kubeadm)

## Metafora Finale

Il kube-apiserver è come il **centralino** di un'azienda:
- Riceve tutte le chiamate (richieste)
- Verifica l'identità del chiamante (autenticazione)
- Controlla se può fare quella richiesta (autorizzazione)
- Indirizza la chiamata al reparto giusto
- Tiene traccia di tutto in un registro (etcd)

**Pro tip esame**: Se un componente non funziona, controlla SEMPRE se riesce a raggiungere l'apiserver. È la prima cosa da debuggare!