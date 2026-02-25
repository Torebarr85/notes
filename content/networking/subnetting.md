+++
title = "Networking: what is an IP Address?"
date = 2026-02-21
draft = false
tags = ["networking","subnetting"]
+++
---

# Scenario AWS concreto

```
VPC: 10.0.0.0/16
├── Subnet pubblica:  10.0.1.0/24  → web server, load balancer
├── Subnet privata:   10.0.2.0/24  → database, backend
└── Subnet privata:   10.0.3.0/24  → altra zona di disponibilità

Internet
    ↓
Internet Gateway
    ↓
┌─────────────────────────────────┐
│  VPC 10.0.0.0/16                │
│                                 │
│  Subnet pubblica  10.0.1.0/24   │
│  [Load Balancer] [Web Server]   │
│           ↓                     │
│  Subnet privata   10.0.2.0/24   │
│  [Database] [Backend]           │
└─────────────────────────────────┘
```
### Perché subnet separate?

La subnet pubblica ha accesso a internet (via Internet Gateway)
La subnet privata no — il DB non deve essere raggiungibile da fuori
Terraform crea tutto questo, ma devi sapere cosa stai scrivendo

## Pensa a un palazzo

Immagina che gli indirizzi IP siano come indirizzi postali:

```
Italia = 10.x.x.x
  └── Milano = 10.0.x.x
        └── Via Rossi = 10.0.1.x
              └── Appartamento 5 = 10.0.1.5
```

Il numero dopo lo slash dice **quanto dell'indirizzo è fisso** e quanto è "libero" per assegnare a qualcuno.

---

## /16 — sei il proprietario del palazzo intero

```
10.0.0.0/16

Fisso:    10.0
Libero:   [0-255].[0-255]

→ Puoi avere 65.536 indirizzi
→ Da 10.0.0.0 fino a 10.0.255.255
```

In AWS: è la tua **VPC** — la tua rete privata intera nel cloud. Grande, con spazio per tutto.

---

## /24 — sei il proprietario di un piano

```
10.0.1.0/24

Fisso:    10.0.1
Libero:   [0-255]

→ Puoi avere 256 indirizzi
→ Da 10.0.1.0 fino a 10.0.1.255
```

In AWS: è una **subnet** — un pezzo della tua VPC. Ci metti dentro un gruppo di server.

---

## /32 — è un appartamento specifico

```
10.0.1.5/32

Fisso:    10.0.1.5
Libero:   niente

→ È esattamente quell'unico IP, nessun altro
```

In AWS: lo usi nei Security Group per dire "accetta connessioni solo da questo IP specifico."

```
# Esempio: SSH aperto solo dal tuo IP di casa
porta 22  da  87.14.22.5/32  ✅  solo tu entri
porta 22  da  0.0.0.0/0      ❌  tutto internet entra
```

---

## Riassunto visivo

```
/16  →  10.0.[????].[????]  →  65.536 IP  →  VPC intera
/24  →  10.0.1.[????]       →  256 IP     →  una subnet
/32  →  10.0.1.5            →  1 IP       →  un indirizzo esatto
```

Più il numero è alto, meno IP hai — più sei preciso.

---
 