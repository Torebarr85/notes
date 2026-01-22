+++
title = "kubelet"
date = 2026-01-22
draft = false 
tags = ["kubernetes","cka"]
+++


# kubelet - Il Capitano del Nodo

## Il Ruolo di kubelet - Finalmente Qualcuno che Fa il Lavoro Vero!

Dopo aver visto componenti che "decidono", "monitorano" e "coordinano", finalmente arriviamo a quello che **fa effettivamente il lavoro**: il **kubelet**.

Se ricordi l'analogia delle navi, kubelet è il **capitano sulla nave worker**. È lui che:
- Gestisce l'equipaggio (container runtime)
- Riceve ordini dalla nave master (apiserver)
- Carica/scarica container
- Invia report sullo stato della nave
- È l'unico punto di contatto con il comando centrale

**Differenza cruciale con altri componenti**: Mentre scheduler e controller-manager decidono "cosa fare", kubelet è quello che **esegue materialmente** le azioni sul nodo.

## Le Responsabilità del Kubelet

### 1. Registrazione del Nodo

Quando un nodo worker si avvia, kubelet è il primo a dire:

```
kubelet → kube-apiserver:
"Ciao! Sono node-worker-1, ho 8 CPU e 16GB RAM.
 Voglio unirmi al cluster!"
```

Senza kubelet, un nodo non può entrare nel cluster - è letteralmente il "passaporto" del nodo.

### 2. Gestione dei Pod

**Il flusso completo**:

```
1. Scheduler decide: "Pod X va su node-2"
           ↓
2. apiserver aggiorna etcd
           ↓
3. kubelet su node-2 (polling ogni ~20s):
   "Vedo che ho un nuovo pod assegnato!"
           ↓
4. kubelet → Container Runtime (Docker/containerd):
   "Scarica immagine nginx:latest e avvia container"
           ↓
5. Container Runtime: Crea il container
           ↓
6. kubelet → apiserver:
   "Pod X ora è Running su node-2"
           ↓
7. apiserver → etcd: Aggiorna stato del pod
```

**Kubelet è l'unico che parla direttamente con il container runtime!**

### 3. Monitoraggio Continuo

Kubelet è come un medico che controlla continuamente i suoi pazienti:

```
Ogni 10 secondi:
├─ I container sono ancora running?
├─ I pod sono healthy? (liveness probes)
├─ I pod sono pronti? (readiness probes)
└─ Reporting → apiserver
```

Se un container crasha, kubelet lo rileva e lo riavvia automaticamente (se configurato).

## L'Architettura del Nodo Worker

```
┌─────────────────────────────────────────┐
│          WORKER NODE                    │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │         kubelet                   │ │
│  │  (Captain - Porto 10250)          │ │
│  │                                   │ │
│  │  • Registra nodo                 │ │
│  │  • Gestisce pod                  │ │
│  │  • Monitora health               │ │
│  │  • Report a apiserver            │ │
│  └──────────┬────────────────────────┘ │
│             │                           │
│             ▼                           │
│  ┌─────────────────────────┐          │
│  │  Container Runtime      │          │
│  │  (Docker/containerd)    │          │
│  └────────┬────────────────┘          │
│           │                            │
│           ▼                            │
│    🐳 🐳 🐳 🐳 (Containers)           │
└─────────────────────────────────────────┘
         ▲
         │ (Comunica con)
         │
┌────────┴────────┐
│  kube-apiserver │
│  (Master Node)  │
└─────────────────┘
```

## La Grande Differenza: kubelet e kubeadm ⚠️

**ATTENZIONE - Questo è importante per l'esame!**

```
┌──────────────────────┬─────────────────────┐
│  Componente          │  Installato da      │
│                      │  kubeadm?           │
├──────────────────────┼─────────────────────┤
│ kube-apiserver       │  ✓ SÌ (come pod)   │
│ etcd                 │  ✓ SÌ (come pod)   │
│ kube-scheduler       │  ✓ SÌ (come pod)   │
│ kube-controller-mgr  │  ✓ SÌ (come pod)   │
│ kubelet              │  ✗ NO! Manuale!    │
│ kube-proxy           │  ✓ SÌ (DaemonSet)  │
└──────────────────────┴─────────────────────┘
```

**Perché kubelet è diverso?**

Kubelet è un po' come "l'uovo o la gallina": serve per far girare i pod, ma è proprio kubelet che fa girare i pod! Non può installare se stesso come pod. Quindi deve essere installato come **servizio systemd nativo** sul sistema operativo.

## Installazione Manuale di kubelet

```bash
# 1. Download binario
wget https://storage.googleapis.com/.../kubelet

# 2. Rendi eseguibile
chmod +x kubelet
sudo mv kubelet /usr/bin/

# 3. Crea file di configurazione
sudo mkdir -p /var/lib/kubelet
sudo vim /var/lib/kubelet/kubelet-config.yaml

# 4. Crea servizio systemd
sudo vim /etc/systemd/system/kubelet.service

# 5. Avvia servizio
sudo systemctl daemon-reload
sudo systemctl start kubelet
sudo systemctl enable kubelet
```

## Opzioni Importanti di kubelet

```bash
# Configurazione kubelet
--config=/var/lib/kubelet/kubelet-config.yaml

# Dove trovare kube-apiserver
--kubeconfig=/etc/kubernetes/kubelet.conf

# Container runtime endpoint
--container-runtime-endpoint=unix:///var/run/containerd/containerd.sock

# Certificati TLS
--tls-cert-file=/var/lib/kubelet/pki/kubelet.crt
--tls-private-key-file=/var/lib/kubelet/pki/kubelet.key

# Porta su cui ascolta (health checks)
--port=10250
```

## Interazione con Container Runtime

**Evoluzione storica**:

```
Prima (deprecated):
kubelet → Docker API direttamente

Adesso:
kubelet → CRI (Container Runtime Interface)
           ├─ containerd
           ├─ CRI-O
           └─ Docker (tramite dockershim, deprecato)
```

**Tool utile per debug**: `crictl` (CLI per CRI)

```bash
# Vedi container (simile a docker ps)
sudo crictl ps

# Vedi immagini
sudo crictl images

# Logs di un container
sudo crictl logs <container-id>
```

## Troubleshooting kubelet

**Scenario comune**: Nodo mostra "NotReady"

```bash
# 1. Controlla stato kubelet
sudo systemctl status kubelet

# 2. Vedi i log
sudo journalctl -u kubelet -f

# 3. Errori comuni nei log:
# - "Unable to connect to apiserver" → Problema rete/certificati
# - "Container runtime not ready" → containerd/docker down
# - "Failed to get node" → Problema registrazione nodo

# 4. Controlla il container runtime
sudo systemctl status containerd
sudo systemctl status docker

# 5. Verifica connettività con apiserver
curl -k https://<master-ip>:6443/healthz
```

**Pro tip**: Se kubelet è down, TUTTO sul nodo è down - nessun pod può essere gestito!

## Health Checks e Probes

Kubelet esegue anche le health checks sui container:

```yaml
# Esempio pod con probes
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app
    image: nginx
    livenessProbe:      # kubelet controlla se è "vivo"
      httpGet:
        path: /healthz
        port: 8080
      periodSeconds: 10  # Ogni 10 secondi
    readinessProbe:     # kubelet controlla se è "pronto"
      httpGet:
        path: /ready
        port: 8080
      periodSeconds: 5
```

Kubelet esegue queste probe e aggiorna lo stato del pod di conseguenza.

## Certificati e TLS Bootstrap

Nel corso approfondirai:
- Come generare certificati per kubelet
- TLS bootstrapping (processo automatico di certificazione)
- Rotazione automatica dei certificati

Per ora basta sapere che kubelet usa certificati per autenticarsi con l'apiserver.

## Punti Chiave per CKA 🎯

✅ **Unico che crea pod materialmente** sul nodo  
✅ **NON installato da kubeadm** - sempre manuale!  
✅ **Gira come servizio systemd**, non come pod  
✅ **Porta 10250** per API e health checks  
✅ **Parla con**: apiserver (sopra) e container runtime (sotto)  
✅ **Registra il nodo** nel cluster  
✅ **Esegue health probes** (liveness, readiness)  
✅ **Se kubelet è down** → nodo NotReady → nessun pod funziona

## Metafora Finale

**kubelet = Caposquadra in cantiere**

- Riceve i progetti dall'architetto (apiserver)
- Coordina gli operai (container runtime)
- Costruisce effettivamente le cose (crea container)
- Controlla che tutto funzioni (health checks)
- Manda report al capo progetto (status updates)
- Senza di lui, il cantiere è fermo!

**Differenza cruciale con scheduler**: 
- Scheduler = Architetto (decide dove costruire)
- kubelet = Caposquadra (costruisce materialmente)

**Pro tip esame**: Se un nodo mostra "NotReady", la prima cosa da controllare è sempre kubelet. Usa `systemctl status kubelet` e `journalctl -u kubelet` per il debug!