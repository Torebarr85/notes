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

Ottime domande. Rispondo in ordine.

---

## Docker Compose vs k3s — sono la stessa cosa?

No, sono strumenti diversi per scopi diversi:

| | Docker Compose | k3s (Kubernetes) |
|---|---|---|
| Scopo | sviluppo locale, app semplici | produzione, orchestrazione |
| Scala | un singolo pc | più nodi/server |
| Complessità | bassa | alta |
| Networking | bridge locale | rete flat cluster |
| Healing | no (riavvia ma non ripianifica) | sì (ripianifica su altri nodi) |

**Analogia:** Compose è come gestire appartamenti in un palazzo. k3s è come gestire una città intera con urbanistica, semafori e ospedali.

---

## Dove vive Docker Compose sul tuo pc?

```bash
# I container in esecuzione
docker compose ps

# Le immagini
docker images

# I volumi (dati persistenti)
docker volume ls

# Tutto fisicamente sta in:
ls /var/lib/docker/
```

Il file `docker-compose.yml` invece vive nella cartella del tuo progetto — è solo testo.

---

## Esercizio base — da zero

```bash
# Crea una cartella di test
mkdir ~/compose-test && cd ~/compose-test

# Crea il file
nano docker-compose.yml
```

Incolla questo:

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"
  db:
    image: mongo:7
    volumes:
      - dati-mongo:/data/db

volumes:
  dati-mongo:
```

```bash
# Avvia
docker compose up -d

# Verifica
docker compose ps

# Apri nel browser
curl http://localhost:8080
```

---


---

##  Ecco cosa succede quando esegui `docker compose up -d`:


**1. Legge il `docker-compose.yml`**
Capisce che deve avviare due servizi: `web` (nginx) e `db` (mongo).

**2. Crea una rete dedicata**
Crea automaticamente una rete bridge chiamata `compose-test_default`. I due container si vedono per nome — `web` può raggiungere `db` semplicemente usando `db` come hostname.

**3. Avvia i container in ordine**
Prima `db`, poi `web` — rispettando le dipendenze se dichiarate.

**4. Monta il volume**
`dati-mongo` viene creato in `/var/lib/docker/volumes/` — i dati di MongoDB sopravvivono anche se il container viene cancellato.

**5. Mappa la porta**
`8080:80` significa: la porta 80 del container nginx è raggiungibile sulla porta 8080 del tuo pc.

---

## Il risultato finale

```
[Browser localhost:8080]
        ↓
   [container web - nginx]
        ↓ rete interna "compose-test_default"
   [container db - mongo]
        ↓
   [volume dati-mongo]
```

--- 
Buono studio! 🚀
