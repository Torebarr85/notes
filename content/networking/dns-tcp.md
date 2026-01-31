+++
title = "osi model dns tcp"
date = 2026-01-31
draft = false
tags = ["networking","osi-model"]
+++

## DNS - Dove Sta e Come Funziona
Sei a casa tua, davanti al PC.
Digiti `https://myapp.com/login` nel browser e premi invio.

Il browser guarda quella stringa e pensa: "myapp.com... questo è un **nome a dominio**, non un indirizzo IP. Io per connettermi ho bisogno di un IP numerico tipo `203.0.113.50`."

**Dove chiede?**

Il browser fa una richiesta al **DNS server** configurato sul tuo PC.

Apri il terminale e fai:
```bash
# Su Linux/Mac
cat /etc/resolv.conf

# Output esempio:
nameserver 192.168.1.1
nameserver 8.8.8.8
```

Oppure su Windows:
```bash
ipconfig /all

# Trovi:
DNS Servers: 192.168.1.1
             8.8.8.8
```

**Cosa sono questi IP?**

- `192.168.1.1`: è il tuo **router di casa**. Il router fa anche da DNS resolver locale
- `8.8.8.8`: è il DNS pubblico di Google (alternativa famosa: `1.1.1.1` di Cloudflare)

**Come fa la richiesta?**

Il browser (o meglio, il sistema operativo per conto del browser) apre una connessione UDP sulla porta 53 verso uno di questi DNS server.

```
Il tuo PC (192.168.1.100) → Router (192.168.1.1:53)
```

Manda un pacchetto UDP che contiene:
```
Query: Qual è l'IP di myapp.com?
Type: A (IPv4 address)
```

**Il router cosa fa?**

Se il router ha già fatto questa query di recente, ha l'IP in cache e risponde subito.

Se non ce l'ha, il router fa a sua volta una richiesta ai **DNS autoritativi** su internet. Questa è una catena:

1. Router chiede al **Root DNS** (ci sono 13 root server nel mondo): "Chi gestisce i domini .com?"
2. Root risponde: "Chiedi ai server TLD per .com"
3. Router chiede ai **TLD server .com**: "Chi gestisce myapp.com?"
4. TLD risponde: "Chiedi a ns1.cloudflare.com" (esempio, se usi Cloudflare per DNS)
5. Router chiede a **ns1.cloudflare.com**: "Qual è l'IP di myapp.com?"
6. Cloudflare risponde: **"203.0.113.50"**

Tutta questa catena avviene in millisecondi.

Il router ti risponde:
```
myapp.com → 203.0.113.50
```

Il browser salva questo IP e può procedere.

---

## La Connessione TCP - Da Dove Parte, Dove Arriva

Ora il browser sa che deve connettersi a `203.0.113.50` sulla porta `443` (HTTPS).

**Da dove parte questa connessione?**

Parte dal tuo PC, dalla tua **interfaccia di rete**.

Fai:
```bash
# Linux/Mac
ifconfig
# o
ip addr

# Windows
ipconfig
```

Vedi qualcosa tipo:
```
eth0 (o wlan0 se sei in WiFi):
  inet 192.168.1.100
  netmask 255.255.255.0
  gateway 192.168.1.1
```

Il tuo PC ha:
- **IP locale**: `192.168.1.100` (IP privato della tua rete domestica)
- **Gateway**: `192.168.1.1` (il router)

**Cosa succede fisicamente?**

Il browser dice al sistema operativo: "Voglio connettermi a 203.0.113.50:443"

Il sistema operativo:

1. **Apre un socket** (un canale di comunicazione di rete)
2. **Sceglie una porta sorgente random** sul tuo PC - esempio `54321`
3. **Crea un pacchetto TCP SYN**:
   ```
   Source IP: 192.168.1.100
   Source Port: 54321
   Destination IP: 203.0.113.50
   Destination Port: 443
   Flags: SYN
   ```

4. **Controlla la routing table**: "203.0.113.50 è sulla mia rete locale? No. Allora devo mandare il pacchetto al gateway (router)."

5. **Manda il pacchetto** attraverso la tua scheda di rete (WiFi o Ethernet) verso il router `192.168.1.1`

---

## Il Viaggio Attraverso Internet

**Il router riceve il pacchetto.**

Il router fa **NAT (Network Address Translation)**. Perché? Perché `192.168.1.100` è un IP privato, non valido su internet.

Il router:
- Ha un **IP pubblico** assegnato dal tuo ISP (provider internet) - esempio `85.20.30.40`
- Sostituisce il tuo IP privato con il suo IP pubblico
- Tiene traccia della connessione in una **NAT table**

Il pacchetto diventa:
```
Source IP: 85.20.30.40 (IP pubblico del tuo router)
Source Port: 54321 (può essere cambiata dal router, ma diciamo che rimane)
Destination IP: 203.0.113.50
Destination Port: 443
```

Il router manda questo pacchetto al **gateway del tuo ISP**.

**Il pacchetto viaggia su internet.**

Passa attraverso decine di router (puoi vederli con `traceroute 203.0.113.50`):
- Router del tuo ISP
- Router di backbone provider (tipo Level3, Cogent)
- Router del datacenter AWS/GCP dove sta il tuo cluster

Ogni router guarda l'IP di destinazione e decide: "Questo va di là" finché il pacchetto arriva fisicamente al datacenter.

---

## Arrivo al LoadBalancer

Il pacchetto arriva all'**IP pubblico `203.0.113.50`**.

Questo IP è configurato sul **LoadBalancer del cloud provider**. È una macchina fisica (o virtuale) nel datacenter AWS/GCP.

Il LoadBalancer riceve il pacchetto SYN:
```
Source IP: 85.20.30.40:54321 (il tuo router)
Destination IP: 203.0.113.50:443
```

Il LoadBalancer risponde con un **SYN-ACK** (secondo step del three-way handshake):
```
Source IP: 203.0.113.50:443
Destination IP: 85.20.30.40:54321
Flags: SYN-ACK
```

Questo pacchetto rifà tutto il viaggio a ritroso:
- Internet
- Router del tuo ISP
- Il tuo router (che fa reverse NAT: cambia destination IP da 85.20.30.40 a 192.168.1.100)
- Arriva al tuo PC

Il browser manda l'**ACK** finale:
```
Source IP: 192.168.1.100:54321
Destination IP: 203.0.113.50:443
Flags: ACK
```

**La connessione TCP è aperta.**

---

## TLS Handshake (HTTPS)

Ora che la connessione TCP è stabilita, il browser inizia il **TLS handshake** per crittografare la comunicazione.

**Step 1: Client Hello**

Il browser manda:
```
Client Hello:
- Versioni TLS supportate: TLS 1.3, TLS 1.2
- Cipher suites supportate: AES-256-GCM, ChaCha20...
- Random data per generare chiavi
```

**Step 2: Server Hello**

Il LoadBalancer (o meglio, l'Ingress Controller che sta dietro) risponde:
```
Server Hello:
- Versione scelta: TLS 1.3
- Cipher scelta: AES-256-GCM
- Certificato SSL: ecco la mia identità (contiene la chiave pubblica)
```

Il certificato dice: "Io sono myapp.com, fidati di me. Firmato da Let's Encrypt (o altra CA)."

**Step 3: Verifica Certificato**

Il browser controlla:
- Il certificato è firmato da una CA fidata? (Chrome ha una lista di CA)
- Il certificato è valido per `myapp.com`?
- Non è scaduto?

Se tutto ok, il browser e il server negoziano le **chiavi di sessione** usando Diffie-Hellman.

**Risultato:**

Da questo momento, tutti i dati sono **crittografati**. Anche il tuo ISP non può leggere cosa stai mandando, vede solo traffico crittografato verso 203.0.113.50:443.

---

## La Richiesta HTTP Vera e Propria

Ora il browser finalmente manda la richiesta HTTP, **dentro il tunnel crittografato TLS**:

```
GET /login HTTP/1.1
Host: myapp.com
User-Agent: Chrome/123.0
Accept: text/html
Connection: keep-alive
```

Questo è il contenuto **applicativo** (Layer 7).

Il pacchetto è incapsulato così:
```
[Ethernet Header]
  [IP Header: 85.20.30.40 → 203.0.113.50]
    [TCP Header: porta 54321 → porta 443]
      [TLS Encrypted Data]
        [HTTP GET /login...]
```

**Il LoadBalancer cosa fa?**

Il LoadBalancer **termina la connessione TLS**. Decritta il traffico.

Perché? Perché il certificato SSL è configurato sul LoadBalancer (o sull'Ingress Controller). Il LoadBalancer ha la **chiave privata** necessaria per decrittare.

Dopo aver decrittato, il LoadBalancer vede la richiesta HTTP in chiaro e la inoltra al cluster Kubernetes.

---

## Dentro il Datacenter - Rete Privata

Ora siamo **dentro il datacenter AWS/GCP**. La rete è privata.

Il LoadBalancer fa un inoltro verso i **Worker Nodes** del tuo cluster:
- Node1: `10.0.1.5`
- Node2: `10.0.1.6`
- Node3: `10.0.1.7`

Questi sono **IP privati** della VPC (Virtual Private Cloud). Non sono raggiungibili da internet.

Il LoadBalancer apre una nuova connessione TCP verso `10.0.1.5:30080` (esempio, sceglie Node1):

```
Source IP: 203.0.113.50 (LoadBalancer interno)
Destination IP: 10.0.1.5:30080 (Node1)
```

Il traffico viaggia sulla **rete interna del datacenter**. È una rete fisica (cavi Ethernet, switch) all'interno del datacenter AWS.

---

## Ricapitolando il Viaggio Fisico

```
[Il tuo PC] 192.168.1.100:54321
    ↓ WiFi/Ethernet
[Router di casa] 192.168.1.1
    ↓ NAT (cambia IP a 85.20.30.40)
[Cavo fibra ottica ISP]
    ↓ Internet (decine di router)
[Datacenter AWS - Ingresso]
    ↓ 
[LoadBalancer] 203.0.113.50:443
    ↓ Termina TLS, decritta
[Switch del datacenter]
    ↓ Rete privata VPC
[Worker Node1] 10.0.1.5:30080
    ↓ kube-proxy + iptables
[Worker Node2] (dove gira il pod Ingress)
    ↓ Rete overlay CNI (VXLAN)
[Ingress Controller Pod] 10.244.1.10:80
    ↓ Legge HTTP, consulta regole Ingress
[Service] 10.96.0.50:80 (IP virtuale)
    ↓ iptables DNAT
[Pod Frontend] 10.244.1.15:8080
    ↓ Container nginx
[Applicazione] Genera risposta HTML
```

---

## Cosa Succede Fisicamente al Tuo PC

Quando il browser apre la connessione, a livello hardware:

1. La **CPU** del tuo PC esegue il codice del browser
2. Il browser fa una **system call** al kernel Linux/Windows: `connect(203.0.113.50, 443)`
3. Il **kernel** crea un socket e mette in coda il pacchetto SYN
4. Il **driver della scheda di rete** (WiFi o Ethernet) prende il pacchetto
5. La **scheda di rete fisica** (chip WiFi o scheda Ethernet) converte i bit in segnali elettrici/onde radio
6. I segnali viaggiano sul cavo/onde WiFi verso il router

Quando arriva la risposta, il processo è inverso:
- Scheda di rete riceve segnali
- Driver li converte in pacchetti
- Kernel TCP/IP stack processa il pacchetto
- Browser riceve i dati nel suo buffer

---

 