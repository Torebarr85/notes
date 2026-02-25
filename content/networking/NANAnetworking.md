+++
title = "Every Networking Concept Explained In 20 Minutes"
date = 2026-02-25
draft = false
tags = ["networking","dns","ipaddress","subnet","routing","firewall"]
+++

# I 5 concetti di networking che ogni sviluppatore deve capire

*Seguiamo l'evoluzione di una startup immaginaria — da un singolo server a un cluster Kubernetes — e impariamo ogni concetto esattamente quando serve.*

---

Invece di partire dalla teoria, facciamo una cosa diversa: seguiamo **TravelBody**, un sito immaginario di prenotazione viaggi, mentre cresce. Ogni problema che incontra introduce esattamente il concetto di networking che serve per risolverlo.

---

## 1. IP address e DNS — "come mi trovi?"

Quando TravelBody parte, ha un solo server. Primo problema: come ci trovano i clienti?

Ogni dispositivo connesso a una rete ha bisogno di un identificatore univoco. Questo è l'**IP address**. Funziona come l'indirizzo di casa: senza di esso, nessuno sa dove mandare i dati.

Il nostro server ottiene un IP pubblico tipo `203.0.113.10`. Tecnicamente, chiunque su internet può raggiungere quel numero. Ma nessuno vuole digitare `203.0.113.10` nel browser.

Qui entra il **DNS** (Domain Name System): traduce nomi leggibili in IP address.

```
Utente digita:   travelbody.com
       │
       ▼
    DNS lookup
       │
       ▼
  203.0.113.10  →  server raggiunto
```

È esattamente come la rubrica del telefono. Non digiti il numero, digiti "mamma" e il telefono trova il numero in background. Stessa cosa: scrivi `google.com` e il DNS trova l'IP dietro quel nome.

---

## 2. Ports — "chi risponde alla porta?"

Il server ora gira tre cose insieme: il sito web, un database MySQL e un servizio di pagamento. Tutti e tre condividono lo stesso IP address. Come sa il server a chi mandare ogni richiesta?

Qui entrano le **ports**: canali numerati da 1 a 65.535. Ogni applicazione "ascolta" su una porta diversa.

```
┌────────────────────────────────────────┐
│   Server  203.0.113.10                 │
│                                        │
│   :80   →  sito web (HTTP)             │
│   :443  →  sito web (HTTPS)            │
│   :3306 →  MySQL database              │
│   :9090 →  servizio pagamento          │
└────────────────────────────────────────┘
```

Quando un cliente visita TravelBody, il browser si connette automaticamente alla porta 80 o 443. Il server sa già che il traffico su quella porta appartiene al web server, non al database.

È come un palazzo con un solo indirizzo stradale — l'IP — ma con appartamenti diversi dentro — le ports.

---

## 3. Subnet e routing — "separiamo le stanze"

TravelBody cresce. Ora gestisce carte di credito e dati personali. Avere tutto su un server è un rischio: se un attaccante entra, prende tutto.

Soluzione: **network segmentation** con le **subnet**.

```
┌──────────────────────────────────────────────────────┐
│  Rete TravelBody                                     │
│                                                      │
│  Subnet A — Frontend pubblico  (192.168.1.0/24)     │
│  ┌──────────────────────────────┐                    │
│  │ Web server   Web server      │                    │
│  └──────────────────────────────┘                    │
│                                                      │
│  Subnet B — Application servers (192.168.2.0/24)    │
│  ┌──────────────────────────────┐                    │
│  │ App server   App server      │                    │
│  └──────────────────────────────┘                    │
│                                                      │
│  Subnet C — Database            (192.168.3.0/24)    │
│  ┌──────────────────────────────┐                    │
│  │ MySQL        MySQL           │                    │
│  └──────────────────────────────┘                    │
└──────────────────────────────────────────────────────┘
```

È come un ospedale diviso per reparti: maternità da un lato, chirurgia dall'altro. Le cose rimangono separate.

Ma adesso: se il sito web è in Subnet A e il database in Subnet C, come comunicano? Serve un **router**. Il routing è il GPS della rete: capisce come arrivare da un punto a un altro tra subnet diverse.

---

## 4. Firewall — "le porte sono aperte, ma non per tutti"

Abbiamo separato le stanze, ma tutte le porte sono spalancate. Separare fisicamente non basta: serve controllare chi può passare.

Un **firewall** è come un addetto alla sicurezza che controlla ogni pacchetto di traffico e decide se lasciarlo passare in base a regole che definisci tu.

Due livelli:

**Host firewall** — protegge il singolo server:
```
Regola sul database server:
  ALLOW  porta 3306  DA  subnet frontend
  BLOCK  tutto il resto
```

**Network firewall** — si mette tra subnet:
```
Regola tra internet e subnet frontend:
  ALLOW  porta 80   DA  ovunque
  ALLOW  porta 443  DA  ovunque
  BLOCK  tutto il resto
```

La sicurezza è sempre a strati. Un attaccante deve superare prima il network firewall, poi l'host firewall. Due checkpoint, non uno.

---

## 5. NAT — "esco senza farmi trovare"

TravelBody ha ora 50 server backend in una subnet privata, con IP privati tipo `10.0.2.5`, `10.0.2.6`, `10.0.2.7`. Gli IP privati funzionano dentro la rete interna, ma non comunicano direttamente con internet.

È come un interno telefonico aziendale: puoi chiamare il collega al numero 205, ma non puoi chiamare quel numero da casa tua.

Il problema: questi server devono comunque raggiungere internet — per scaricare aggiornamenti, chiamare API esterne, inviare dati a servizi di terze parti. Dare a ognuno un IP pubblico costerebbe soldi e significherebbe gestirne 50.

Soluzione: **NAT** (Network Address Translation).

```
Server 10.0.2.5  ──┐
Server 10.0.2.6  ──┤──→  NAT device  ──→  203.0.113.10  →  🌐 Internet
Server 10.0.2.7  ──┘       │
                            └── ricorda: "questa risposta
                                 è per 10.0.2.5"
```

Il NAT sostituisce l'IP privato con il suo IP pubblico, manda la richiesta fuori, e quando arriva la risposta la smista al server giusto. Tutti e 50 i server escono con un solo IP pubblico, rimangono nascosti, ma raggiungono quello che serve.

È come la receptionist in ufficio: quando un dipendente deve fare una chiamata esterna, la receptionist usa il numero principale dell'azienda e poi smista la risposta alla scrivania giusta.

---

## Nel cloud: stessi concetti, strumenti diversi

Quando TravelBody migra al cloud, non cambia nulla di concettuale. Cambiano solo gli strumenti:

```
Fisico                  →   Cloud (es. AWS)
─────────────────────────────────────────────
Rete privata isolata    →   VPC
Subnet                  →   Subnet (identiche)
Router fisico           →   Route table
Firewall di rete        →   Security Group / NACL
NAT device              →   NAT Gateway
Accesso a internet      →   Internet Gateway
```

Stessa architettura, stessa logica. Il cloud la espone come servizi gestiti invece che come hardware da installare.

---

## Containers e Docker: networking in miniatura

Con i microservizi, TravelBody containerizza tutto con **Docker**. I container introducono un nuovo livello di networking, ma i concetti sono gli stessi.

Docker crea una **bridge network** privata sul server: tutti i container sulla stessa bridge network comunicano tra loro usando il nome del container.

Ma il container ha la sua rete interna. Se il servizio pagamento gira sulla porta 9090 *dentro* il container, come raggiunge le richieste esterne?

**Port mapping** — la stessa logica del NAT:

```
docker run -p 1990:9090 payment

traffico arriva sul server :1990
         │
         ▼
forwarded a :9090 dentro il container
```

Per far comunicare container su server diversi, Docker usa una **overlay network**: una rete virtuale che si estende su più host, facendo sembrare che tutti i container siano sulla stessa rete locale.

---

## Kubernetes: orchestrazione su scala

Quando TravelBody gestisce centinaia di container su decine di server, entra in gioco **Kubernetes**.

L'unità base è il **pod**: uno o più container che lavorano insieme, con un IP address condiviso. Pensa a un appartamento con un solo indirizzo — tutti gli inquilini dentro condividono quello stesso indirizzo.

Il problema: i pod sono temporanei. Kubernetes li crea, li distrugge, li sposta. Ogni volta che un pod viene ricreato, riceve un nuovo IP address. Se il sito web si connette direttamente al pod del database e quel pod viene ricreato, la connessione si rompe.

Soluzione: i **Kubernetes services**.

```
Website pod  →  connette a "database-service"  ←  stabile, sempre lì
                        │
              ┌─────────┴──────────┐
              │                    │
          DB pod A             DB pod B
       (può sparire)        (può sparire)
```

Un service fornisce un IP stabile e un nome DNS che non cambiano mai, anche mentre i pod dietro vengono ricreati continuamente. È come il numero del reparto vendite: le persone cambiano scrivania, ma il numero rimane lo stesso e qualcuno risponde sempre.

Per esporre l'intera applicazione a internet, si usa l'**Ingress**: una reception che smista il traffico in entrata al service giusto in base alle regole configurate.

```
Ingress rules:
  travelbody.com          →  website-service
  travelbody.com/booking  →  booking-service
  travelbody.com/payment  →  payment-service
```

---

## Riepilogo: i 5 concetti che non cambiano mai

Che tu stia lavorando con server fisici, cloud, Docker o Kubernetes, questi cinque concetti restano sempre gli stessi. Cambiano gli strumenti, non i principi.

```
┌────────────────┬───────────────────────────────────────────────────┐
│ Concetto       │ Cosa risolve                                       │
├────────────────┼───────────────────────────────────────────────────┤
│ IP + DNS       │ Come ci trovano gli altri in rete                  │
│ Ports          │ Come il server smista il traffico all'applicazione  │
│                │ giusta                                             │
│ Subnet +       │ Come isoli parti della rete e colleghi le sezioni  │
│ Routing        │ tra loro                                           │
│ Firewall       │ Come controlli quale traffico è permesso           │
│ NAT            │ Come i server privati raggiungono internet         │
│                │ senza essere esposti                               │
└────────────────┴───────────────────────────────────────────────────┘
```

Capire questi fondamentali significa capire qualsiasi sistema di rete — e fare troubleshooting su qualsiasi scala.

---

credits: https://www.youtube.com/watch?v=xj_GjnD4uyI&t=896s