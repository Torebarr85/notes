+++
title = "Networking in Linux e Docker — Guida Step by Step"
date = 2026-03-02
draft = false
tags = ["networking","docker","linux","CKA"]
+++

# Networking in Linux e Docker

Capire il networking di Kubernetes richiede di partire dalle fondamenta.
Questo articolo costruisce la comprensione **dal basso verso l'alto**:
prima Linux, poi Docker, poi (nel prossimo articolo) Kubernetes.

---

## Parte 1 — Come si parlano due macchine?

Tutto il networking nasce da un problema semplice: hai due computer, vuoi farli comunicare.

La risposta cambia a seconda di **dove si trovano** queste macchine.

---

### Caso 1: stessa rete

Se le macchine sono sulla stessa rete, basta uno **switch**.

```
[Machine A: 192.168.1.5]
          |
        [SWITCH]
          |
[Machine B: 192.168.1.6]
```

Lo switch è come un hub dell'ufficio: tutti i device connessi si vedono direttamente.

Per connettersi allo switch, ogni macchina usa una **network interface** — tipicamente `eth0`.
Poi le si assegna un IP sulla stessa subnet:

```bash
ip addr add 192.168.1.5/24 dev eth0   # su Machine A
ip addr add 192.168.1.6/24 dev eth0   # su Machine B
```

A questo punto A e B si parlano. Fine del caso semplice.

---

### Caso 2: reti diverse

Aggiungi una seconda rete separata:

```
[Rete 1: 192.168.1.0]       [Rete 2: 192.168.2.0]
  Machine A: .1.5              Machine C: .2.5
  Machine B: .1.6              Machine D: .2.6
```

Machine A vuole parlare con Machine C.
**Non può** — lo switch non instrada traffico tra reti diverse.

Lo switch dice: *"Il pacchetto per 192.168.2.5? Non è nella mia rete. Non so dove mandarlo. Scarto."*

Serve un **router**: un device con un "piede" in entrambe le reti.

```
[Rete 1: 192.168.1.0] ←→ [ROUTER] ←→ [Rete 2: 192.168.2.0]
                           .1.1 / .2.1
```

Il router dice: *"192.168.2.5? Conosco quella rete — ce l'ho su eth1. Te lo passo io."*

---

## Parte 2 — Gateway e Routing Table

Avere un router fisicamente connesso non basta.
Le macchine devono **sapere che esiste** e come usarlo.

Questa istruzione si chiama **gateway** — la porta verso l'esterno.

```bash
# Su Machine A: "per raggiungere la rete .2.0, passa dal router"
ip route add 192.168.2.0/24 via 192.168.1.1
```

Senza questa configurazione, Machine A dice:
*"Pacchetto per 192.168.2.5? Non ho nessuna route per quella rete. Network unreachable."*

Con il gateway configurato, invece:
*"Pacchetto per 192.168.2.5? Non è nella mia rete locale, ma so che devo passare da 192.168.1.1. Inoltro lì."*

> ⚠️ Va configurato su **ogni macchina**. Se Machine C non sa come tornare verso A,
> i pacchetti partono ma non tornano mai — e la connessione non funziona.

---

### La Routing Table

Ogni macchina Linux mantiene una **routing table**: una lista ordinata di regole
che dice dove mandare i pacchetti in base alla destinazione.

```bash
ip route    # visualizza la routing table
```

Output tipico:

```
Destination     Gateway         Iface
192.168.1.0     0.0.0.0         eth0    ← rete locale, esco diretto
192.168.2.0     192.168.1.1     eth0    ← rete remota, passa dal router
```

La voce `0.0.0.0` nel campo Gateway significa *"non serve gateway, sono già nella rete giusta"*.

---

### Default Gateway

Non puoi aggiungere una route per ogni IP di Internet.
Usi il **default gateway**: *"per tutto quello che non conosco, passa da qui."*

```bash
ip route add default via 192.168.1.1
# equivalente a:
ip route add 0.0.0.0/0 via 192.168.1.1
```

`0.0.0.0/0` = qualsiasi destinazione.

Quando arriva un pacchetto per un IP sconosciuto, Linux scorre la routing table dall'alto verso il basso e dice:
*"Non ho una route specifica per questo IP... non ce l'ho... non ce l'ho... ah, c'è il default gateway. Mando tutto lì."*

---

## Parte 3 — Linux come Router

Punto chiave: **non serve hardware dedicato per fare routing**.

Un host Linux con due network interfaces può sostituire un router.

```
[Rete A: 192.168.1.0]                    [Rete B: 192.168.2.0]
  Machine A: .1.5                           Machine C: .2.5
        |                                         |
       eth0 — [ HOST B: .1.6 / .2.6 ] — eth1
```

Host B ha:
- `eth0` con IP `192.168.1.6` → connesso alla Rete A
- `eth1` con IP `192.168.2.6` → connesso alla Rete B

Essere connesso a due reti però **non basta**.
Linux di default **non forwarda pacchetti** tra interfaces.

Linux dice: *"Ho ricevuto un pacchetto su eth0 destinato a 192.168.2.5. Quella non sono io.
Per sicurezza, lo scarto. Non è compito mio girarlo su eth1 — potrebbe essere traffico malevolo."*

Questo comportamento è controllato da un singolo file:

```bash
cat /proc/sys/net/ipv4/ip_forward
# 0 → "Sono una macchina normale, non un router. Scarto."
```

Per abilitarlo:

```bash
# Temporaneo (si perde al reboot)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Persistente → modifica /etc/sysctl.conf
# net.ipv4.ip_forward = 1
```

Con `ip_forward = 1`, Linux cambia personalità:
*"Pacchetto su eth0 per 192.168.2.5? Ho una route per quella rete su eth1. Lo giro."*

---

## Parte 4 — Docker Networking

Ora che hai le basi di Linux networking, Docker diventa molto più comprensibile.
Usa esattamente gli stessi meccanismi — solo in modo automatizzato.

Quando lanci un container, hai tre modalità di networking:

---

### `none` — isolamento totale

```
[container] ✗  (nessuna rete)
```

Il container non ha nessuna network interface. Non parla con nessuno.

Il container dice: *"Non ho nessuna eth0. Non so nemmeno cosa sia una rete. Faccio solo il mio job."*

```bash
docker run --network none nginx
```

Use case: batch jobs, task che non hanno bisogno di rete.

---

### `host` — zero isolamento

```
[HOST: eth0 192.168.1.5]
         |
    [container]   ← stesso network stack
```

Il container condivide direttamente la network stack dell'host.

Il container dice: *"La mia eth0? È la stessa dell'host. Il mio IP? Stesso dell'host.
Porto 80? È direttamente il porto 80 dell'host — nessuno strato in mezzo."*

```bash
docker run --network host nginx
```

> ⚠️ Non puoi avviare due container sulla stessa porta.
> Il secondo container direbbe: *"Voglio aprire la porta 80... ma è già occupata! Non posso."*

---

### `bridge` — la modalità default ← la più importante

```
[container A]   [container B]   [container C]
 172.17.0.2      172.17.0.3      172.17.0.4
     |               |               |
  vethAAA         vethBBB         vethCCC
     |               |               |
  [======= docker0 bridge: 172.17.0.1 =======]
                     |
                   [HOST]
                     |
                  [Internet]
```

Docker crea una **rete privata interna**.
Ogni container riceve il suo IP in questa rete (`172.17.0.x`).

---

## Parte 5 — Come funziona il Bridge in dettaglio

Quando installi Docker, lui crea automaticamente una virtual network interface
sull'host chiamata `docker0`.

```bash
ip link   # vedrai: docker0
ip addr   # docker0 ha IP: 172.17.0.1
```

`docker0` dice: *"Sono il punto di raccolta di tutti i container.
Per loro sono uno switch virtuale. Per l'host sono una normale network interface."*

---

### Cosa succede ad ogni `docker run`

Docker esegue questi step in automatico:

**Step 1** — Crea un **network namespace** isolato per il container

> Il network namespace dice: *"Io sono il mio universo di rete.
> Ho la mia routing table, la mia eth0, il mio IP. Non vedo nulla fuori da me."*

**Step 2** — Crea un **veth pair**: due virtual interfaces collegate come i due capi di un cavo

**Step 3** — Un'estremità va dentro il namespace del container (diventa `eth0`)

**Step 4** — L'altra estremità rimane sull'host, agganciata al bridge `docker0`

```
┌─────────────────────────┐              ┌──────────────────────────┐
│   container namespace   │              │          HOST            │
│                         │              │                          │
│   eth0: 172.17.0.3      │◄────────────►│  vethXXX                 │
│                         │  veth pair   │      │                   │
└─────────────────────────┘              │  docker0: 172.17.0.1     │
                                         │      │                   │
                                         │    [eth0] → Internet     │
                                         └──────────────────────────┘
```

Il veth pair dice: *"Siamo un cavo virtuale. Tutto quello che entra da un lato
esce dall'altro — esattamente come un cavo fisico Ethernet."*

I veth pairs si riconoscono dagli indici numerici: `9↔10` sono una coppia, `11↔12` un'altra.

```bash
ip link                        # vedi le veth sull'host
ip -n <namespace> link         # vedi eth0 dentro il container
docker inspect <c> | grep IP   # IP assegnato al container
```

---

## Parte 6 — Port Mapping

I container nella bridge network sono raggiungibili **solo dall'host** o da altri container nella stessa rete.

Il container dice: *"Il mio IP è 172.17.0.3 — sono in una rete privata.
Da fuori l'host nessuno sa che esisto. Sono invisibile."*

Per esporre un container al mondo esterno usi il **port mapping**:

```bash
docker run -p 8080:80 nginx
# "traffico sulla porta 8080 dell'host → porta 80 del container"
```

Come lo implementa Docker? Con **iptables**.

Docker aggiunge una regola nella **NAT table** che fa **DNAT**
(Destination NAT — riscrive l'IP/porta di destinazione del pacchetto):

```bash
iptables -t nat -L
# DNAT tcp → destination 172.17.0.3:80
```

iptables dice: *"Arriva un pacchetto sulla porta 8080? Fermo tutto.
Riscrivo la destinazione: non più HOST:8080, ma 172.17.0.3:80. Poi lo lascio passare."*

Il flusso completo di una request esterna:

```
[Client esterno]
       |
       ▼
HOST porta :8080
       |
       ▼
iptables: "DNAT → 172.17.0.3:80"
       |
       ▼
container 172.17.0.3:80
```

---

## Riepilogo — Building Blocks

| Concetto Linux | Ruolo |
|---|---|
| **network interface** | connessione fisica o virtuale alla rete |
| **routing table** | mappa delle regole di instradamento |
| **gateway** | porta verso reti esterne |
| **ip_forward** | abilita Linux a fare routing tra interfaces |

| Concetto Docker | Cos'è |
|---|---|
| `docker0` | bridge interface sull'host (switch virtuale) |
| **network namespace** | isolamento di rete per ogni container |
| **veth pair** | cavo virtuale namespace ↔ bridge |
| **iptables NAT** | meccanismo del port mapping |

---

## Comandi Chiave

```bash
# Linux networking
ip link                           # lista network interfaces
ip addr                           # mostra IP assegnati
ip addr add X dev ethX            # assegna IP
ip route                          # visualizza routing table
ip route add X via Y              # aggiunge una route
cat /proc/sys/net/ipv4/ip_forward # verifica forwarding

# Docker networking
docker network ls                 # lista reti Docker
docker inspect <c> | grep IP      # IP del container
ip link                           # vedi veth pairs sull'host
iptables -t nat -L                # vedi regole NAT (port mapping)
```

> ⚠️ Le modifiche con `ip` sono **temporanee** — spariscono al reboot.
> Per renderle persistenti modifica i file di configurazione di sistema.

---

*Il prossimo articolo collegherà questi concetti a **Kubernetes CNI**:
come i Pod comunicano tra loro e perché Kubernetes ha bisogno di un plugin di rete dedicato.*