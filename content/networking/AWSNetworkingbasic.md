+++
title = "AWS Networking Basics For Programmers | Hands On"
date = 2026-02-25
draft = false
tags = ["networking","aws","vpc","subnet"]
+++



# AWS Networking: capire VPC, Subnet e Route Tables (una volta per tutte)

*Un'introduzione pratica per chi viene dalla programmazione o dal web dev — senza teoria inutile.*

---

Quando ho iniziato a lavorare sul cloud, tutti intorno a me disegnavano diagrammi di architettura e parlavano di VPC, subnet, route table, NAT gateway... e io annuivo facendo finta di seguire.

Se ti riconosci in questa scena, questo articolo è per te.

Niente PowerPoint. Niente teoria pura. Solo la struttura reale di come funziona il networking su AWS, spiegata in modo che resti in testa.

---

## La struttura: cosa stiamo costruendo

Alla fine di questo articolo avrai capito questo schema:

```
┌─────────────────────── AWS Cloud ───────────────────────────┐
│                                                             │
│  ┌──────────────────── VPC (10.0.0.0/16) ────────────────┐  │
│  │                                                       │  │
│  │  ┌─── Public Subnet ───┐   ┌─── Private Subnet ────┐  │  │
│  │  │   10.0.0.0/24       │   │   10.0.1.0/24         │  │  │
│  │  │                     │   │                       │  │  │
│  │  │  ┌──────────────┐   │   │  ┌──────────────┐     │  │  │
│  │  │  │  EC2 Public  │   │   │  │  EC2 Private │     │  │  │
│  │  │  └──────────────┘   │   │  └──────────────┘     │  │  │
│  │  │                     │   │         │             │  │  │
│  │  │  ┌──────────────┐   │   │         ▼             │  │  │
│  │  │  │ NAT Gateway  │◄──┼───┼─── Route Table        │  │  │
│  │  │  └──────┬───────┘   │   └───────────────────────┘  │  │
│  │  └─────────┼───────────┘                              │  │
│  │            │        Route Table (public)              │  │
│  └────────────┼──────────────────────────────────────────┘  │  
│               │                                             │  
│  ┌────────────▼────────────┐                                │  
│  │   Internet Gateway      │                                │  
└──┴─────────────┬───────────┴────────────────────────────────┘  
                 │
              🌐 Internet
```

Costruiamolo pezzo per pezzo.

---

## 1. VPC — Virtual Private Cloud

Una **VPC** è una rete privata isolata dentro AWS. Pensa a una recinzione intorno alle tue risorse: tutto ciò che metti dentro è separato dal resto del mondo (e da altri VPC).

Quando crei una VPC, le assegni un **CIDR block** — cioè un range di indirizzi IP che puoi usare al suo interno.

### Come funziona il CIDR (versione umana)

`10.0.0.0/16` — cosa significa quel `/16`?

```
Indirizzo IP:   10  .  0  .  0  .  0
Ottetti:        [1]    [2]    [3]    [4]
Bits:            8     16     24     32

/16 → i primi 16 bit (= i primi 2 ottetti) sono FISSI
      puoi cambiare solo il 3° e il 4° ottetto

Quindi: da 10.0.0.1 a 10.0.255.254 → ~65.000 indirizzi
```

| CIDR       | Ottetti fissi | Ottetti liberi | Indirizzi disponibili |
|------------|---------------|----------------|-----------------------|
| /8         | primo         | ultimi 3       | ~16 milioni           |
| /16        | primi due     | ultimi 2       | ~65.000               |
| /24        | primi tre     | ultimo         | 254                   |

Per un VPC di sviluppo, `/16` è una scelta comoda: hai spazio per tante subnet.

---

## 2. Subnet — dividere la rete

Dentro il VPC puoi creare delle **subnet**: sottoreti con range IP più piccoli.

La distinzione fondamentale:

```
┌─────────────────────────────────────────────┐
│                VPC 10.0.0.0/16              │
│                                             │
│  ┌─────────────────┐  ┌──────────────────┐  │
│  │  Public Subnet  │  │  Private Subnet  │  │
│  │  10.0.0.0/24    │  │  10.0.1.0/24     │  │
│  │                 │  │                  │  │
│  │  Web server     │  │  Database        │  │
│  │  Load balancer  │  │  Backend API     │  │
│  │  NAT Gateway    │  │  Microservices   │  │
│  └─────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────┘
```

> ⚠️ Chiamare una subnet "public" non la rende pubblica automaticamente. È solo un nome. Quello che la rende davvero pubblica è la **route table** — lo vediamo tra poco.

---

## 3. Internet Gateway

Un **Internet Gateway** è il collegamento tra il tuo VPC e internet. Senza di esso, sei completamente isolato.

```
VPC  ←──→  Internet Gateway  ←──→  🌐 Internet
```

Si crea in due passi:
1. Crei l'Internet Gateway
2. Lo **attacchi** al VPC (un gateway = un VPC)

Ma anche dopo averlo attaccato, le tue istanze non hanno ancora accesso a internet. Manca ancora un pezzo.

---

## 4. Route Tables — il vero cuore del routing

Una **route table** è una lista di regole che dice: *"se il traffico va verso X, mandalo a Y"*.

Ogni VPC nasce con una route table di default che permette solo il traffico interno:

```
Destination     Target
──────────────────────────
10.0.0.0/16     local      ← tutto il traffico interno al VPC
```

Per dare accesso a internet alla subnet pubblica, aggiungi:

```
Destination     Target
────────────────────────────────────────
10.0.0.0/16     local
0.0.0.0/0       igw-xxxxxxxx   ← tutto il resto → Internet Gateway
```

`0.0.0.0/0` significa **"qualsiasi IP"** — cioè tutto il traffico non locale viene instradato verso l'Internet Gateway.

> La subnet **privata** non ha questa regola. Ci arriveremo con il NAT Gateway.

---

## 5. NAT Gateway — uscire senza essere raggiungibili

Il problema della subnet privata: le tue istanze hanno bisogno di aggiornarsi, scaricare dipendenze, fare chiamate API verso l'esterno. Ma non vuoi che qualcuno dall'esterno possa connettersi direttamente a loro.

La soluzione è il **NAT Gateway** (Network Address Translation):

```
EC2 privata  →  NAT Gateway (in public subnet)  →  Internet
                       ↑
               Può uscire, ma nessuno
               può entrare direttamente
```

Il NAT Gateway vive nella subnet **pubblica** (che ha già accesso a internet), e la route table della subnet privata lo usa come uscita:

```
Route table PRIVATA:
Destination     Target
────────────────────────────────────
10.0.0.0/16     local
0.0.0.0/0       nat-xxxxxxxx   ← tutto il resto → NAT Gateway
```

---

## 6. Security Groups e NACLs — i firewall

Due livelli di protezione, con una differenza importante:

```
Internet
    │
    ▼
┌──────────────────────────────────┐
│  NACL (Network Access Control)   │  ← Protegge la SUBNET
│  • Stateless                     │     Stateless = devi definire
│  • Inbound + Outbound rules      │     sia regole IN che OUT
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Security Group                  │  ← Protegge l'EC2 INSTANCE
│  • Stateful                      │     Stateful = se permetti
│  • Solo Inbound (outbound auto)  │     l'ingresso, il ritorno
└──────────────────────────────────┘     è automatico
```

Nella pratica, i **Security Groups** sono quelli che configuri quasi sempre. I NACL si usano principalmente per bloccare IP specifici a livello di subnet.

---

## Riepilogo visivo finale

```
🌐 Internet
     │
     ▼
Internet Gateway
     │
     ▼
┌── VPC (10.0.0.0/16) ──────────────────────────────┐
│                                                   │
│  Public Subnet (10.0.0.0/24)                      │
│  Route: 0.0.0.0/0 → IGW                           │
│  ┌────────────┐   ┌────────────┐                  │
│  │ EC2 Public │   │ NAT Gateway│                  │
│  │ [SG]       │   └─────┬──────┘                  │
│  └────────────┘         │                         │
│                         │(route from subnet priv) │
│  Private Subnet (10.0.1.0/24)                     │
│  Route: 0.0.0.0/0 → NAT Gateway                   │
│  ┌────────────────┐                               │
│  │ EC2 Private    │                               │
│  │ [SG]           │ ← raggiungibile solo dall'    │
│  └────────────────┘   interno del VPC             │
└───────────────────────────────────────────────────┘
```

---

## I concetti in 6 righe

| Componente        | Cosa fa                                          |
|-------------------|--------------------------------------------------|
| **VPC**           | Rete isolata. Il recinto.                        |
| **Subnet**        | Sotto-rete dentro il VPC. Pubblica o privata.    |
| **Internet GW**   | Porta verso internet. Bidirezionale.             |
| **Route Table**   | Regole di instradamento del traffico.            |
| **NAT Gateway**   | Uscita verso internet per subnet private.        |
| **Security Group**| Firewall per singola istanza EC2. Stateful.      |

---

credits: https://www.youtube.com/watch?v=2doSoMN2xvI&t=390s 