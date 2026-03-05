+++
title = "Studio in volo"
date = 2026-03-05
draft = false
tags = ["corsi"]
+++

# Studio in volo ✈️ — Networking + Kubernetes Troubleshooting

> Prerequisiti: Docker installato, k3s running (`kubectl get nodes` → Ready)
> Tempo stimato: 3-4 ore

---

## PARTE 1 — Network Namespaces (la base di tutto)

### Concetto chiave
Ogni container Docker e ogni Pod Kubernetes vive in un **network namespace** isolato — una "bolla" di rete separata con le sue interfacce, routing table e regole firewall.

Capire questo ti spiega il 90% dei problemi di networking in Kubernetes.

### Esercizio 1.1 — Esplora i namespace esistenti

```bash
# Vedi i namespace di rete attivi sul sistema
ip netns list

# Vedi le interfacce di rete del tuo sistema host
ip addr show

# Nota l'interfaccia docker0 — è il bridge di Docker
ip addr show docker0
```

**Domanda:** Cosa rappresenta `docker0`? È un bridge virtuale che connette i container alla rete host.

---

### Esercizio 1.2 — Crea una mini-rete virtuale a mano

Questa è esattamente la stessa cosa che fa Docker quando avvia un container.

```bash
# Crea due network namespace
sudo ip netns add ns1
sudo ip netns add ns2

# Verifica
ip netns list
```

```bash
# Crea una coppia di interfacce virtuali collegate (veth pair)
# veth è come un cavo virtuale — quello che entra da un lato esce dall'altro
sudo ip link add veth1 type veth peer name veth2

# Assegna un'interfaccia a ciascun namespace
sudo ip link set veth1 netns ns1
sudo ip link set veth2 netns ns2
```

```bash
# Assegna indirizzi IP
sudo ip netns exec ns1 ip addr add 10.0.0.1/24 dev veth1
sudo ip netns exec ns2 ip addr add 10.0.0.2/24 dev veth2

# Attiva le interfacce
sudo ip netns exec ns1 ip link set veth1 up
sudo ip netns exec ns2 ip link set veth2 up
sudo ip netns exec ns1 ip link set lo up
sudo ip netns exec ns2 ip link set lo up
```

```bash
# Testa la connettività tra i due namespace
sudo ip netns exec ns1 ping -c 3 10.0.0.2
```

✅ Se il ping funziona, hai appena replicato manualmente quello che Docker fa automaticamente!

```bash
# Cleanup
sudo ip netns delete ns1
sudo ip netns delete ns2
```

---

### Esercizio 1.3 — Networking Docker in pratica

```bash
# Vedi le reti Docker disponibili
docker network ls

# Ispeziona la rete bridge di default
docker network inspect bridge
```

```bash
# Avvia due container
docker run -d --name container1 --rm nginx
docker run -d --name container2 --rm nginx

# Trova gli IP dei container
docker inspect container1 | grep IPAddress
docker inspect container2 | grep IPAddress
```

```bash
# Entra in container1 e pinga container2
docker exec -it container1 bash
# dentro il container:
apt-get install -y iputils-ping 2>/dev/null || ping <IP_container2> -c 3
exit
```

```bash
# Crea una rete custom (come fa Kubernetes con i Pod)
docker network create --driver bridge mia-rete

docker run -d --name app1 --network mia-rete --rm nginx
docker run -d --name app2 --network mia-rete --rm nginx

# Sulla rete custom puoi usare i nomi dei container come hostname!
docker exec app1 ping -c 3 app2

# Cleanup
docker stop app1 app2
docker network rm mia-rete
```

**Nota chiave:** Kubernetes usa lo stesso principio — ogni Pod ha un IP, i Service fanno da DNS interno.

---

## PARTE 2 — Kubernetes Troubleshooting

> Il cluster k3s deve essere running. Verifica con: `kubectl get nodes`

### Esercizio 2.1 — CrashLoopBackOff

Questo è l'errore più comune. Significa che il container crasha subito dopo l'avvio e Kubernetes continua a riavviarlo.

```bash
# Crea un pod rotto
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pod-rotto
spec:
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "echo 'partenza'; exit 1"]
EOF
```

```bash
# Osserva cosa succede
kubectl get pod pod-rotto -w
# (Ctrl+C per uscire dopo aver visto CrashLoopBackOff)
```

**Metodologia di debug:**

```bash
# Step 1 — Descrivi il pod (eventi, stato)
kubectl describe pod pod-rotto

# Step 2 — Leggi i log (dell'ultimo crash)
kubectl logs pod-rotto --previous

# Step 3 — Identifica il problema
# In questo caso: exit 1 = il processo termina con errore
```

```bash
# Cleanup
kubectl delete pod pod-rotto
```

---

### Esercizio 2.2 — ImagePullBackOff

```bash
# Pod con immagine inesistente
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pod-immagine-sbagliata
spec:
  containers:
  - name: app
    image: nginx:versione-che-non-esiste-mai
EOF
```

```bash
# Debug
kubectl get pod pod-immagine-sbagliata
kubectl describe pod pod-immagine-sbagliata
# Cerca nella sezione "Events" — vedrai il motivo esatto
```

```bash
# Cleanup
kubectl delete pod pod-immagine-sbagliata
```

---

### Esercizio 2.3 — Liveness Probe misconfiguration

Esattamente il tipo di problema che hai debuggato a InfoCert con Quarkus!

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pod-probe-rotta
spec:
  containers:
  - name: app
    image: nginx
    livenessProbe:
      httpGet:
        path: /endpoint-che-non-esiste
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 5
      failureThreshold: 2
EOF
```

```bash
# Osserva — il pod parte, poi Kubernetes lo uccide e riavvia
kubectl get pod pod-probe-rotta -w

# Debug
kubectl describe pod pod-probe-rotta
# Cerca: "Liveness probe failed"
```

```bash
# Fix: correggi il path
kubectl delete pod pod-probe-rotta

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: pod-probe-ok
spec:
  containers:
  - name: app
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
EOF

kubectl get pod pod-probe-ok -w
```

```bash
# Cleanup
kubectl delete pod pod-probe-rotta pod-probe-ok 2>/dev/null; true
```

---

### Esercizio 2.4 — Service + DNS interno

```bash
# Crea un deployment nginx
kubectl create deployment web --image=nginx --replicas=2

# Esponi con un Service
kubectl expose deployment web --port=80 --name=web-service

# Verifica
kubectl get pods
kubectl get service web-service
```

```bash
# Testa il DNS interno di Kubernetes
# Avvia un pod temporaneo e prova a raggiungere il service per nome
kubectl run test-dns --image=busybox --rm -it --restart=Never -- \
  wget -qO- http://web-service
```

Se risponde con l'HTML di nginx: il DNS interno funziona correttamente.

```bash
# Cleanup
kubectl delete deployment web
kubectl delete service web-service
```

---

## Riepilogo — Comandi di debug essenziali

| Problema | Comando |
|---|---|
| Stato generale | `kubectl get pods -A` |
| Dettaglio pod | `kubectl describe pod <nome>` |
| Log container | `kubectl logs <nome>` |
| Log crash precedente | `kubectl logs <nome> --previous` |
| Shell nel pod | `kubectl exec -it <nome> -- sh` |
| Eventi del cluster | `kubectl get events --sort-by=.lastTimestamp` |
| Rete pod | `kubectl exec <nome> -- ip addr` |

---

## Note finali

- Tutti gli esercizi funzionano **completamente offline** con k3s locale
- Se k3s si ferma, riavvialo con: `sudo systemctl start k3s`
- Il kubeconfig è in `~/.kube/config`

Buono studio! 🚀
