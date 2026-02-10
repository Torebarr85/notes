+++
title = "prerequisites 2: DNS"
date = 2026-02-09
draft = false
tags = ["networking","dns"]
+++


Basically, you want to tell system A that system B at IP address 1921681.17 11 has a name DB.

We want to tell system A that when I say db, I mean the IP 192.168.1.11:

```bash
cat >> /etc/hosts
192.168.1.11 db
```

All'interno di una piccola rete di pochi sistemi, è possibile gestire facilmente le voci nel file /etc/hosts

Su ogni sistema, specifico quali sono gli altri sistemi nell'ambiente, ed è così che si faceva

in passato.

Finché l'ambiente non è cresciuto e questi file si sono riempiti di troppe voci, rendendo la loro gestione

troppo difficile.

Se l'IP di uno dei server cambiava, era necessario modificare le voci in tutti questi host.

Ed è qui che abbiamo deciso di spostare tutte queste voci in un unico server DNS SERVER che le gestirà centralmente.


## Come possiamo puntare il nostro host a un server DNS?

Il nostro server DNS ha l'IP 192.1681.100.

Ogni host ha un file di configurazione della risoluzione DNS su /etc/resolv.conf 
Aggiungiamo una voce che specifica l'indirizzo del server DNS.


```bash
cat >> /etc/resolv.conf
nomeDNSserver 192.1681.100
```
 

 
 # DNS Resolution: I Concetti Chiave 🎯

## La Gerarchia DNS (L'albero al contrario)

Il DNS funziona come un **organigramma aziendale al contrario**, partendo dal CEO (root) fino all'impiegato specifico:

```
. (root)
└── .com (top-level domain)
    └── google (domain name)
        └── maps (subdomain)
```

**Termini tecnici:**
- **Root (.)**: il punto di partenza universale
- **TLD (Top Level Domain)**: .com, .net, .org, .edu
- **Domain**: il nome della tua organizzazione
- **Subdomain**: i "reparti" della tua org

---

## Il Flusso di Risoluzione (maps.google.com)

**Step by step:**

1. **Richiesta iniziale** → il tuo PC chiede al DNS aziendale "chi è maps.google.com?"

2. **DNS aziendale non sa** → fa da "postino" verso Internet

3. **Processo a cascata:**
   - Root DNS → "per .com vai da questo server"
   - TLD DNS (.com) → "per google vai da quest'altro"
   - Google DNS → "maps è questo IP: x.x.x.x"

4. **Caching intelligente** → il DNS aziendale **memorizza** l'IP per secondi/minuti per non rifare tutto il giro

**Metafora:** È come chiedere indicazioni a cascata - chiedi al vigile della tua città, lui ti dice di andare in autostrada, lì c'è un cartello che ti indica l'uscita, poi trovi il GPS locale che ti porta a destinazione.

---

## Search Domain: Lo "Shortcut" Aziendale

**Problema:** Devi scrivere `web.mycompany.com` ogni volta? Noioso!

**Soluzione:** Entry `search` in `/etc/resolv.conf`

```
search mycompany.com prod.mycompany.com
```

**Cosa fa:**
- Digiti `ping web` 
- Il sistema **automaticamente prova**: 
  - `web.mycompany.com`
  - `web.prod.mycompany.com`

**Analogia:** Come avere il prefisso telefonico salvato - chiami "123456" invece del numero completo "+39-02-123456"

---

## Record Types Essenziali

| Tipo | Cosa fa | Esempio |
|------|---------|---------|
| **A** | IPv4 → hostname | `web → 192.168.1.10` |
| **AAAA** | IPv6 → hostname | IPv6 addresses |
| **CNAME** | Alias (nome→nome) | `eat → food.com`<br>`hungry → food.com` |

---

## Tool di Troubleshooting

**`ping`** → usa `/etc/hosts` + DNS  
**`nslookup`** → solo DNS (ignora /etc/hosts)  
**`dig`** → come nslookup ma più verboso

**Quando usarli:**
- `ping` per test rapidi
- `nslookup/dig` per debug DNS puro
