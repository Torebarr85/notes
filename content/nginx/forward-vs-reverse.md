
+++
title = "Forward Proxy vs Reverse Proxy"
date = 2026-02-10
draft = false
tags = ["nginx"]
+++

# Forward Proxy vs Reverse Proxy: Qual è la Differenza?

Quando digiti `netflix.com` e premi invio, non ti stai collegando direttamente ai server di Netflix. La tua richiesta passa prima attraverso un intermediario, qualcosa che Netflix ha deployato apposta. È un **reverse proxy**.

E se sei su una rete aziendale, la tua richiesta potrebbe essere passata attraverso un altro proxy prima ancora di uscire dall'edificio: un **forward proxy**.

Stessa parola, lavori opposti.

---

## La Distinzione Fondamentale

Sia forward che reverse proxy sono intermediari. Siedono tra client e server. L'intera distinzione si riduce a una domanda:

> **Chi ha assunto questo intermediario?**

---

## Forward Proxy: L'Agente del Client

Un forward proxy lavora **per il client**.

Immagina di voler contattare un'azienda, ma non vuoi che sappiano chi sei. Assumi un rappresentante che va a tuo nome. L'azienda tratta solo con il tuo rappresentante — non hanno idea che tu esista.

### Come funziona

1. Configuri il browser o il sistema per instradare il traffico attraverso il proxy
2. Le tue richieste vanno prima al proxy
3. Il proxy le inoltra alla destinazione
4. Il sito di destinazione vede solo l'indirizzo del proxy, non il tuo

### Casi d'uso comuni

- **Geoblocking**: un sito è bloccato nella tua regione? Instrada il traffico attraverso un proxy in un paese dove il contenuto è accessibile
- **Reti aziendali**: spesso instradano il traffico attraverso un forward proxy per monitorare, filtrare o cachare le richieste

---

## Reverse Proxy: La Reception del Server

Un reverse proxy lavora **per il server**.

Stessa idea della reception di un'azienda: i visitatori non girano per l'edificio cercando la persona giusta. Tutti si registrano prima, e la reception li indirizza al posto giusto.

I client pensano di parlare con un solo server. Non hanno idea che ci sia un'intera infrastruttura dietro quel singolo punto di ingresso.

### Setup tipico

```
[Client] → [Reverse Proxy] → [Server 1]
                          → [Server 2]
                          → [Server 3]
```

### Funzionalità chiave

| Funzione | Descrizione |
|----------|-------------|
| **Load Balancing** | Le richieste arrivano, il proxy le distribuisce su più server |
| **High Availability** | Un server fallisce? Il proxy lo rileva e reindirizza il traffico istantaneamente. Gli utenti non se ne accorgono |
| **Caching** | Stessa risorsa richiesta più volte? Il proxy la cacha e la serve direttamente. Il backend non viene toccato |
| **Security** | Traffico malevolo, rate limiting, blocking — tutto avviene al livello del proxy, prima che il tuo codice applicativo sia mai coinvolto |

---

## Il Percorso di una Richiesta

Vediamo una richiesta che attraversa entrambi i proxy:

1. Sei al lavoro. Clicchi un link
2. La richiesta colpisce il **forward proxy aziendale**
3. Viene loggata. Il tuo IP viene scambiato con quello del proxy prima che la richiesta lasci la rete
4. La richiesta raggiunge il sito web, ma atterra prima sul loro **reverse proxy**
5. Il proxy la instrada verso un server disponibile
6. La risposta torna per lo stesso percorso

**Due proxy, una richiesta.** Uno lavorava per la tua azienda, uno lavorava per il sito web. Nessuna delle due parti ha visto oltre il proprio proxy.

---

## Riassunto

| Tipo | Lavora per | Nasconde | Esempio |
|------|-----------|----------|---------|
| Forward Proxy | Client | Chi sta chiedendo | Proxy aziendale, VPN |
| Reverse Proxy | Server | Chi sta rispondendo | Load balancer, CDN |

---

## Nella Pratica

Ogni applicazione su larga scala che usi — Netflix, YouTube, la maggior parte dei sistemi in produzione — gira dietro un reverse proxy.

Load balancing, caching, security: tutto succede a quel livello.

Quando costruisci e deployi i tuoi sistemi, strumenti come **Nginx**, **HAProxy**, **Traefik**, o servizi cloud come **Cloudflare** e **AWS ALB** sono dove implementerai tutto questo.