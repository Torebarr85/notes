+++
title = "Switching, Routing e Gateway"
date = 2026-02-07
draft = false
tags = ["networking"]
+++

```markdown
# Kubernetes Networking Fundamentals: Switching, Routing e Gateway

## Introduzione

In questa serie di lezioni, affrontiamo le basi del networking necessarie per comprendere Kubernetes.

Analizzeremo concetti fondamentali come switching, routing, gateway, DNS e network namespaces in Linux. Non ci perderemo in teorie sui modelli OSI o sui layer di rete - ci concentreremo solo su ciò che serve per comprendere il resto del corso.

Vedremo come questi concetti sono configurati sui sistemi, specificamente da una prospettiva Linux. Ci saranno molti comandi. Li esamineremo dal punto di vista di un system admin e di uno sviluppatore applicativo, non necessariamente da quello di un network engineer.

In questo modo, quando discuteremo questi argomenti nel contesto di Kubernetes, saprai di cosa stiamo parlando, dove cercare informazioni, dove sono configurate le cose, come fare troubleshooting, ecc.

Se questi argomenti ti sembrano troppo basilari o se sei già esperto di networking in Linux, sentiti libero di saltare queste lezioni e passare direttamente a quelle su Kubernetes.

## Cos'è una Rete?

Abbiamo due computer A e B: laptop, desktop, VM sul cloud, ovunque. Come fa il sistema A a raggiungere B?

Li colleghiamo a uno **switch**, e lo switch crea una rete contenente i due sistemi.

```
┌─────────┐                    ┌─────────┐
│  Host A │                    │  Host B │
│         │                    │         │
└────┬────┘                    └────┬────┘
     │                              │
     │         ┌──────────┐         │
     └─────────│  Switch  │─────────┘
               └──────────┘
```

### Interfacce di Rete

Per connetterli allo switch, abbiamo bisogno di un'interfaccia su ogni host (fisica o virtuale, a seconda dell'host).

Per vedere le interfacce dell'host, usiamo il comando:

```bash
ip link
```

In questo caso, esaminiamo l'interfaccia chiamata `eth0` che useremo per connetterci allo switch.

### Assegnazione degli IP

Assumiamo che sia una rete con indirizzo `192.168.1.0`. Assegniamo quindi ai sistemi degli indirizzi IP sulla stessa rete usando il comando:

```bash
ip addr add 192.168.1.10/24 dev eth0  # Host A # Cosa fa: Dice "questa interfaccia eth0 HA questo indirizzo IP"
ip addr add 192.168.1.11/24 dev eth0  # Host B
```

Una volta che i link sono attivi e gli indirizzi IP sono assegnati, i computer possono ora comunicare tra loro attraverso lo switch.
 

### Limiti dello Switch

Lo switch può solo abilitare la comunicazione **all'interno di una rete**, il che significa che può ricevere pacchetti da un host sulla rete e consegnarli ad altri sistemi all'interno della stessa rete.

## Connettere Reti Diverse: Il Router

Supponiamo di avere un'altra rete contenente i sistemi C e D all'indirizzo `192.168.2.0`. I sistemi hanno indirizzi IP `192.168.2.10` e `192.168.2.11` rispettivamente.

```
┌─────────┐     ┌──────────┐     ┌─────────┐
│  Host A │─────│  Switch  │─────│  Host B │
│192.168  │     │          │     │192.168  │
│  .1.10  │     └──────────┘     │  .1.11  │
└─────────┘                      └─────────┘
    Network: 192.168.1.0


┌─────────┐     ┌──────────┐     ┌─────────┐
│  Host C │─────│  Switch  │─────│  Host D │
│192.168  │     │          │     │192.168  │
│  .2.10  │     └──────────┘     │  .2.11  │
└─────────┘                      └─────────┘
    Network: 192.168.2.0
```

Come fa un sistema in una rete a raggiungere un sistema nell'altra? Come fa il sistema B con IP `192.168.1.11` a raggiungere il sistema C con IP `192.168.2.10` sull'altra rete?

È qui che entra in gioco un **router**.

### Cos'è un Router

Un router aiuta a connettere due reti insieme. È un dispositivo intelligente - pensalo come un altro server con molte porte di rete.

Poiché si connette a due reti separate, gli vengono assegnati due IP, uno su ciascuna rete:
- Nella prima rete: `192.168.1.1`
- Nella seconda rete: `192.168.2.1`

```
Network 1: 192.168.1.0              Network 2: 192.168.2.0
┌─────────┐                         ┌─────────┐
│  Host A │                         │  Host C │
│  .1.10  │                         │  .2.10  │
└────┬────┘                         └────┬────┘
     │                                   │
     │    ┌──────────────────┐          │
     └────│  Router          │──────────┘
          │  eth0      eth1  │
          │  .1.1       .2.1 │
          └──────────────────┘
```

Ora abbiamo un router connesso alle due reti che può abilitare la comunicazione tra loro.

## Gateway: La Porta d'Uscita

Quando il sistema B prova a inviare un pacchetto al sistema C, come fa a sapere dove si trova il router sulla rete per inviare il pacchetto?

Il router è semplicemente un altro dispositivo sulla rete. Potrebbero esserci molti altri dispositivi simili.

È qui che configuriamo i sistemi con un **gateway** o una **route**.

> **Metafora**: Se la rete fosse una stanza, il gateway è la porta verso il mondo esterno, verso le altre reti o verso internet. I sistemi devono sapere dove si trova quella porta per attraversarla.

## Ricapitolo:

**Gateway è un RUOLO, non una proprietà automatica**
```
┌──────────────────────────────────────────┐
│  Assegnare IP con ip addr add            │
│           ↓                              │
│  Il computer HA un indirizzo             │
│           ↓                              │
│  NON diventa automaticamente gateway     │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  Per DIVENTARE un gateway serve:         │
│                                          │
│  1. Avere 2+ interfacce con IP           │
│  2. Attivare ip_forward = 1              │
│  3. Altri host devono CONFIGURARLO       │
│     nella loro routing table             │
└──────────────────────────────────────────┘
```
### Visualizzare la Routing Table

Per vedere la configurazione di routing esistente su un sistema, esegui:

```bash
route
# oppure
ip route
```

Questo comando visualizza la routing table del kernel. Inizialmente, non ci saranno configurazioni di routing.

In questa condizione, il tuo sistema B non sarà in grado di raggiungere il sistema C - può solo raggiungere altri sistemi all'interno della stessa rete nell'intervallo `192.168.1.0`.

### Configurare un Gateway

Per configurare un gateway sul sistema B per raggiungere i sistemi sulla rete `192.168.2.0`, esegui:

```bash
ip route add 192.168.2.0/24 via 192.168.1.1 # Configura una strada verso un'altra rete
# Cosa fa: Dice "per raggiungere la rete 192.168.2.0, passa dall'indirizzo 192.168.1.6"
# È come dire: "Per andare a Milano, prendi l'uscita dell'autostrada A1"
# Effetto: Quando devi mandare un pacchetto a 192.168.2.x, lo mandi prima a 192.168.1.6 (il router)

```

Questo comando specifica che puoi raggiungere la rete `192.168.2.0` attraverso la "porta" o gateway all'indirizzo `192.168.1.1`.

Eseguendo nuovamente il comando `route`, vedrai che è stata aggiunta una route per raggiungere la rete `192.168.2.0` attraverso il router.
 


### Configurazione Bidirezionale

**Ricorda**: questo deve essere configurato su tutti i sistemi.

Per esempio, se il sistema C deve inviare un pacchetto al sistema B, allora devi aggiungere una route nella routing table del sistema C per accedere alla rete `192.168.1.0` attraverso il router configurato con l'indirizzo IP `192.168.2.1`:

```bash
# Sul sistema C
ip route add 192.168.1.0/24 via 192.168.2.1
```

## Default Gateway: Accesso a Internet

Supponiamo che questi sistemi necessitino accesso a internet. Diciamo che devono accedere a Google sulla rete `172.217.194.0` su internet.

Quindi colleghi il router a internet e poi aggiungi una nuova route nella tua routing table per instradare tutto il traffico verso quella rete attraverso il tuo router.

### Il Problema della Scalabilità

Ci sono così tanti siti diversi su reti diverse su internet. Invece di aggiungere un'entry nella routing table per l'indirizzo IP dello stesso router per ciascuna di quelle reti, puoi semplicemente dire: **"per qualsiasi rete di cui non conosci una route, usa questo router come default gateway"**.

In questo modo, qualsiasi richiesta a qualsiasi rete al di fuori della tua rete esistente va a questo particolare router.

### Configurare il Default Gateway

In un setup semplice come questo, tutto ciò di cui hai bisogno è una singola entry nella routing table con il default gateway impostato sull'indirizzo IP del router:

```bash
ip route add default via 192.168.1.1
# oppure equivalentemente
ip route add 0.0.0.0/0 via 192.168.1.1
```

**Nota**: Invece della parola `default`, potresti anche dire `0.0.0.0`. Significa "qualsiasi destinazione IP". Entrambe queste righe significano la stessa cosa.

### Interpretare la Routing Table

Un'entry `0.0.0.0` nel campo gateway indica che non hai bisogno di un gateway.

Per esempio, in questo caso, perché il sistema C acceda a qualsiasi dispositivo nella rete `192.168.2.0`, non ha bisogno di un gateway perché è nella sua stessa rete.

```bash
ip route
```

Output esempio:
```
Destination     Gateway         Iface
192.168.1.0     0.0.0.0         eth0    # Rete locale, no gateway
192.168.2.0     192.168.1.1     eth0    # Altra rete, via router
0.0.0.0         192.168.1.1     eth0    # Default: tutto il resto
```

### Router Multipli

Ma diciamo che hai router multipli nella tua rete: uno per internet, un altro per la rete privata interna. Allora avrai bisogno di avere due entry separate per ciascuna rete:
- Una entry per la rete privata interna
- Un'altra entry con il default gateway per tutte le altre reti, incluse le reti pubbliche

**Troubleshooting tip**: Se hai problemi a raggiungere internet dai tuoi sistemi, questa routing table e la configurazione del default gateway sono un buon punto di partenza.

## Linux come Router

Vediamo ora come possiamo configurare un host Linux come router.

### Setup Iniziale

Partiamo con un setup semplice. Ho tre host A, B e C:
- A e B sono connessi a una rete `192.168.1.0`
- B e C sono connessi a un'altra rete `192.168.2.0`

Quindi l'host B è connesso a entrambe le reti usando due interfacce: `eth0` e `eth1`.

```
Host A: 192.168.1.5
Host B: 192.168.1.6 (eth0) e 192.168.2.6 (eth1)
Host C: 192.168.2.5
```

```
┌─────────┐                         ┌─────────┐
│  Host A │                         │  Host C │
│ .1.5    │                         │ .2.5    │
└────┬────┘                         └────┬────┘
     │                                   │
     │    ┌──────────────────┐          │
     └────│  Host B (Router) │──────────┘
          │ eth0       eth1  │
          │ .1.6        .2.6 │
          └──────────────────┘
```

### Il Problema

Come facciamo A a parlare con C?

Se provo a fare `ping 192.168.2.5` da A, direbbe "network is unreachable". E ormai sappiamo perché: l'host A non ha idea di come raggiungere una rete a `192.168.2.0`.

### Configurare le Routes

Dobbiamo dire all'host A che la "porta" o gateway verso la rete 2 è attraverso l'host B. Lo facciamo aggiungendo un'entry nella routing table:

```bash
# Su Host A
ip route add 192.168.2.0/24 via 192.168.1.6
```

Se i pacchetti devono arrivare all'host C, l'host C dovrà inviare risposte all'host A. Quando l'host C prova a raggiungere l'host A sulla rete `192.168.1.0`, affronterà lo stesso problema.

Quindi dobbiamo far sapere all'host C che può raggiungere l'host A attraverso l'host B, che sta agendo come router:

```bash
# Su Host C
ip route add 192.168.1.0/24 via 192.168.2.6
```

### IP Forwarding: Il Pezzo Mancante

Quando proviamo il ping ora, non otteniamo più il messaggio di errore "network unreachable". Questo significa che le nostre entry di routing sono corrette, ma ancora non otteniamo alcuna risposta.

**Perché?** Di default in Linux, i pacchetti non vengono inoltrati da un'interfaccia all'altra.

Per esempio, i pacchetti ricevuti su `eth0` sull'host B non vengono inoltrati altrove attraverso `eth1`. Questo è fatto per ragioni di sicurezza.

Per esempio, se avessi `eth0` connesso alla tua rete privata ed `eth1` a una rete pubblica, non vorremmo che chiunque dalla rete pubblica possa facilmente inviare messaggi alla rete privata, a meno che tu non lo permetta esplicitamente.

Ma in questo caso, dato che sappiamo che entrambe sono reti private ed è sicuro abilitare la comunicazione tra loro, possiamo permettere all'host B di inoltrare pacchetti da una rete all'altra.

### Abilitare IP Forwarding

Se un host può inoltrare pacchetti tra interfacce è governato da un'impostazione in questo file di sistema:

```bash
cat /proc/sys/net/ipv4/ip_forward
```

Di default, il valore in questo file è impostato a `0`, che significa "nessun forwarding".

Imposta questo valore a `1` e dovresti vedere i ping andare a buon fine:

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
```

**Importante**: Semplicemente impostare questo valore non rende persistenti le modifiche dopo un riavvio. Per farlo, devi modificare lo stesso valore nel file `/etc/sysctl.conf`:

```bash
# In /etc/sysctl.conf
net.ipv4.ip_forward = 1
```

Poi applica le modifiche:

```bash
sysctl -p
```

## Comandi Chiave da Ricordare

Ecco i comandi principali da questa lezione, che saranno utili nelle lezioni successive:

### Gestione Interfacce

```bash
ip link                          # Lista e modifica interfacce sull'host
ip addr                          # Vedi gli IP assegnati alle interfacce
ip addr add 192.168.1.10/24 dev eth0  # Imposta IP su un'interfaccia
```

**Nota**: Le modifiche fatte usando questi comandi sono valide solo fino a un riavvio. Se vuoi rendere persistenti queste modifiche, devi impostarle nel file delle interfacce di rete.

### Gestione Routing

```bash
ip route                         # Visualizza la routing table
route                            # Comando alternativo per visualizzare routing
ip route add 192.168.2.0/24 via 192.168.1.1  # Aggiungi entry alla routing table
ip route add default via 192.168.1.1         # Imposta default gateway
```

### IP Forwarding

```bash
cat /proc/sys/net/ipv4/ip_forward     # Verifica se IP forwarding è abilitato
echo 1 > /proc/sys/net/ipv4/ip_forward  # Abilita temporaneamente
# Per rendere permanente: modifica /etc/sysctl.conf
```

**Ricorda**: Verifica sempre il comando per controllare se IP forwarding è abilitato su un host se stai lavorando con un host configurato come router.
 
```