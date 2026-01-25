+++
title = "Port Redirect con iptables"
date = 2026-01-25
draft = false
tags = ["linux"]
+++

# iptables Explained: Port Forwarding, Firewall e NAT per Junior SysAdmin

### descrizione esercizio:
```bash
# - un'app Python che fornisce dati bancari simulati viene eseguita come root e rimane in ascolto sulla porta 20280. 
# - L'app è gestita dal supervisore e non può essere arrestata o riconfigurata per utilizzare una porta diversa per motivi di sicurezza e legacy. 
# - Però un sistema di monitoraggio legacy interno prevede che il servizio sia disponibile sulla porta 80, ma l'app è hardcoded sulla porta 20280 per motivi di sicurezza e legacy. 
# - Il tuo compito è rendere il servizio accessibile localmente sulla porta 80

App Python:
├─ Gira come root
├─ Managed by supervisor (non puoi fermarla)
├─ Ascolta SOLO su porta 20280 (hardcoded)
└─ Non può essere riconfigurata

Sistema monitoring legacy:
└─ Si aspetta il servizio su porta 80
```

# Il comando per Creare la Regola iptables:
```bash
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 20280

# Pattern 1: Port Forwarding Locale
iptables -t nat -A OUTPUT -p tcp --dport <OLD> -j REDIRECT --to-port <NEW>
# Pattern 2: Port Forwarding Esterno
iptables -t nat -A PREROUTING -p tcp --dport <OLD> -j REDIRECT --to-port <NEW>
```

## 🔗 COLLEGAMENTO CON KUBERNETES
Questo è esattamente quello che fa kube-proxy!
```bash
Service ha IP virtuale (es. 10.96.0.1)
kube-proxy crea regole iptables
Traffico verso Service IP → rediretto → Pod IP
 
```

 


# 🏰 Cos'è un Firewall Linux?

```markdown
Immagina il tuo computer come un **castello medievale** con mura e porte.

┌─────────────────────────────────────┐
│       CASTELLO (il tuo server)      │
│                                     │
│  🏠 App Web (porta 80)              │
│  🏪 Database (porta 3306)           │
│  🏛️ SSH (porta 22)                  │
│                                     │
│  MURA (firewall):                   │
│  Porta 22: 🌉 SSH (ponte aperto)    │
│  Porta 80: 🚪 HTTP (porta aperta)   │
│  Altre: 🔒 CHIUSE                   │
└─────────────────────────────────────┘
           ↑
    👤 Visitatori (traffico)

Il firewall è il **ponte levatoio** che decide chi entra/esce:
````

```bash
# Ponte abbassato (traffico accettato)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Ponte alzato (traffico bloccato)
sudo iptables -A INPUT -p tcp --dport 23 -j DROP
```

**iptables** è lo strumento per configurare il firewall (integrato nel kernel Linux).
```
```
 
---

# TCP | Traffico TCP: Il Corriere Affidabile

```markdown
## 📦 Traffico TCP: Il Corriere Affidabile

Hai due modi per inviare dati tra computer:

**UDP (cartoline)**: Veloce ma senza garanzie - usato per streaming/gaming
**TCP (pacco con ricevuta)**: Affidabile e ordinato - usato per web/database

### Three-Way Handshake
Prima di comunicare, TCP "si saluta":

```
Client → "Posso parlare?" (SYN)
Server → "Pronto anch'io!" (SYN-ACK)  
Client → "Ok, iniziamo!" (ACK)
        ↓
   Connessione ✓
```

### Porte TCP = Numeri Civici
```
porta 80   = Web (HTTP)
porta 22   = SSH
porta 3306 = MySQL
porta 20280 = La tua app
```

`curl localhost:80` = "vai nella mia città (localhost), casa numero 80 (porta)"
```


---

# NAT: Il Portiere che Reindirizza
 
```markdown
Immagina un condominio con portiere:

```
Postino (traffico) → Portiere (NAT) → Appartamento 5B
                         ↓
                   Tabella NAT:
                   "Porta 80 → Apt 20280"
```

**Esempio reale - Router di casa**:
```
Internet (IP pubblico: 93.45.12.8)
    ↓
Router NAT ─→ PC (192.168.1.5)
           ├→ Phone (192.168.1.6)
           └→ Tablet (192.168.1.7)
```

Il router tiene una **tabella** per sapere quale pacchetto va a quale dispositivo.

**Nel nostro caso (Port Forwarding)**:
```
Client → Porta 80 → [Tabella NAT] → Porta 20280 ✓
                    ↓
            ┌───────────────┬────────┐
            │ Richiesta     │ Vai a  │
            ├───────────────┼────────┤
            │ porta 80      │ 20280  │
            └───────────────┴────────┘
```
```