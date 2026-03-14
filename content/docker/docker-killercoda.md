---
title: "Guida pratica ai comandi Docker essenziali"
date: 2026-03-14
draft: false
tags: ["docker"]
---

## Intro

Questo articolo raccoglie i comandi Docker fondamentali che uso più spesso in laboratorio: build, run, networking e volumi. Niente teoria pura — solo comandi, errori comuni e spiegazioni pratiche.

---

## Immagini e build

### Costruire un'immagine

```bash
docker build -t nome-immagine .
```

`-t` assegna un **tag** (nome) all'immagine. Senza, viene identificata solo dall'ID hash.

Con versione esplicita:

```bash
docker build -t nome-immagine:1.0 .
```

Se ometti la versione, Docker usa `latest` come default.

### Listare le immagini locali

```bash
docker images
```

### Ispezionare un'immagine

```bash
docker inspect nome-immagine
```

Utile per vedere `CMD`, `ENTRYPOINT`, variabili d'ambiente e altro. Per filtrare un campo specifico:

```bash
docker inspect nome-immagine | jq .[0].Config.Cmd
```

---

## Dockerfile: istruzioni fondamentali

### COPY vs ADD

Entrambe copiano file nel container, ma la best practice è:

- Usa **`COPY`** per copiare file locali — è esplicita e prevedibile
- Usa **`ADD`** solo quando serve estrarre archivi `.tar` o scaricare da URL

```dockerfile
FROM alpine
WORKDIR /app
COPY config.txt ./
ADD archivio.tar.gz ./
```

### RUN vs CMD vs ENTRYPOINT

| Istruzione | Quando viene eseguita | Sovrascrivibile |
|---|---|---|
| `RUN` | Durante il **build** dell'immagine | No |
| `CMD` | All'**avvio** del container | Sì, da CLI |
| `ENTRYPOINT` | All'**avvio** del container | Solo con `--entrypoint` |

**Esempio pratico:**

```dockerfile
FROM alpine
ENTRYPOINT ["ping"]
CMD ["killercoda.com"]
```

```bash
docker run pinger                  # → ping killercoda.com
docker run pinger google.com       # → ping google.com (CMD sostituito)
docker run --entrypoint curl pinger https://example.com  # ENTRYPOINT sostituito
```

Regola: usa `ENTRYPOINT` per definire lo scopo fisso del container, `CMD` per i parametri di default modificabili.

---

## Avviare i container

### Opzioni di `docker run` più usate

```bash
docker run \
  -d \                          # detached: gira in background
  -it \                         # interattivo con terminale
  --name mio-container \        # nome leggibile
  --rm \                        # rimuovi il container alla chiusura
  -p 8080:80 \                  # port forward host:container
  -v /host/path:/container/path \ # mount volume
  nome-immagine
```

> **Importante:** tutte le opzioni vanno **prima** del nome dell'immagine. Dopo l'immagine, Docker si aspetta il comando da eseguire.

### Tenere vivo un container senza server

Se l'immagine non ha un processo persistente (tipo un server), il container si chiude subito. Soluzione:

```bash
docker run -d -it --name mio-container alpine sh
```

`sh` rimane in ascolto e il container non muore.

### Entrare in un container in esecuzione

```bash
docker exec -it nome-container sh
```

### `--rm`: pulizia automatica

```bash
docker run --rm nome-immagine comando
```

Elimina il container non appena si ferma. Utile per test rapidi. **Non usarlo** se hai bisogno di ispezionare i log dopo un crash.

---

## Monitoraggio e debug

```bash
docker ps           # container in esecuzione
docker ps -a        # tutti i container (anche fermi)
docker logs nome    # log del container
docker inspect nome # dettagli completi in JSON
```

---

## Volumi: condividere file tra host e container

Il mount collega una directory dell'host a una del container:

```bash
docker run -d \
  -v /root/myapp:/usr/share/nginx/html \
  --name web \
  nginx:alpine
```

Modifiche sull'host → visibili subito nel container. File scritti dal container → persistono sull'host anche dopo la morte del container.

Caso d'uso tipico: serve una build statica di React o Angular tramite nginx senza rebuildarla dentro il container.

---

## Networking

### Bridge network di default

Ogni container lanciato senza specificare una rete finisce nella rete `bridge` di default. I container si vedono tra loro **solo per IP**.

```bash
# Trovare l'IP di un container
docker inspect app-2 | grep IPAddress

# Fare una richiesta da un container all'altro
docker exec app-1 sh -c 'curl -sS 172.17.0.3'
```

### Bridge network custom

Con una rete custom, Docker attiva un **DNS interno**: i container si raggiungono per nome.

```bash
# Crea la rete
docker network create bridge-network

# Collega i container
docker network connect bridge-network app-1
docker network connect bridge-network app-2

# Ora funziona anche per hostname
docker exec app-1 sh -c 'curl -sS app-2'
```

Per scollegare dalla rete di default:

```bash
docker network disconnect bridge app-1
```

### Confronto reti

| | Bridge default | Bridge custom |
|---|---|---|
| Comunicazione per IP | ✅ | ✅ |
| Comunicazione per hostname | ❌ | ✅ |
| DNS interno | ❌ | ✅ |

---

## Pulizia

```bash
docker stop nome-container
docker rm nome-container
docker rmi nome-immagine

# Rimuovere tutto il non usato
docker system prune
```

---

## Riferimenti

- [Docker CLI reference](https://docs.docker.com/engine/reference/commandline/cli/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/instructions/)
- [Docker networking](https://docs.docker.com/network/)