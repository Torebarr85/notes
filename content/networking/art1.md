+++
title = "Networking: <titolo>"
date = 2025-10-14
draft = false
tags = ["networking"]
+++


# **NETWORKING**

**what is an IP Address? // You SUCK at Subnetting // EP 1**
THE ENTIRE PLAYLIST:
[ ] https://www.youtube.com/watch?v=5WfiTHiU4x8&list=PLIhvC56v63IKrRHh3gvZZBAGvsvOhwrRF


- ip address like a phone number to identify devices. 192.168.1.204
**MR. SUBNET MASK aka NETMASK**
Tells what ip addresses start with. he tells the street we live on.. 
- subnet aka netmask 255.255.255.0

**MR. DEFAULT GATEWAY aka ROUTER**
He does it all. give ip addresses to our devices in our network and could help us to get outside our network. if you wanna visit netflix for instance.

- default gateway aka router aka default router 192.168.1.1
- router (by DHCP) gives your devices an IP address
![alt text](attachments/network_portion.png)
- device is a HOST
- host number can change. but the network portion don't
  
![alt text](attachments/subnets.png)
![alt text](attachments/_.png)

- if my computer wants to call netflix (another ip address not in his neighborhood) needs "ups" aka default gateway aka router. he knows everything related others ip address.

- whenever any device in a network (home network or     business network etc...)  wants to talk to something outside it's network it has to talk to it's router. it's default gateway to get out.


**UNtouchable IP address**
- 192.168.1.0 -> network address
- 192.168.1.255 -> broadcast address
- and that one associated to the default gateway aka router (for example: 192.168.1.1)

so from 0 to 255 = 256 ip addresses and you can use just 253


# **we ran OUT of IP Addresses!!**
https://www.youtube.com/watch?v=tcae4TSSMo8&t=613s

**Cosa contiene una subnet**

- Network ID: il primo indirizzo del blocco. Identifica la rete.
- Host: gli indirizzi usabili dai dispositivi.
- Broadcast: l’ultimo indirizzo. Serve per inviare a “tutti” nella subnet.
  
**Idee chiave**

- IPv4 = 4 numeri (ottetti). Esempio: 192.168.1.130
- Maschera: 255.255.255.0
- 255 = parte “rete” (quartiere)
- 0 = parte “host” (case)

**Quindi: 255.255.255.0 = /24**

- primi 3 numeri fissi = rete
- ultimo numero variabile = host

**Esempio pratico con /24:**

- Rete: 192.168.1.0/24
- Network ID: 192.168.1.0 (nome del quartiere)
- Broadcast: 192.168.1.255 (megafono a tutti)
- Host usabili: 192.168.1.1–192.168.1.254 (254 case)

**Regola lampo**

- Più 255 = rete più grande, subnet più “stretta” per gli host
- Più 0 (o numeri piccoli tipo 128,192,224…) = più spazio agli host



**Procedura chiara per passare da maschera a numero di host**

Conta i bit di rete (prefisso) dalla maschera.
Usa questa mappa per ogni ottetto:

255 → 8 bit

254 → 7

252 → 6

248 → 5

240 → 4

224 → 3

192 → 2

128 → 1

0 → 0

Host bits = 32 − prefisso.

Indirizzi totali = 2host bits
.

Usabili = totali − 2

**Trucco calcolo quanti subnet usabili ho**
![alt text](attachments/trucco-calcolo-hosts.png) 



Esempio visivo
![alt text](attachments/esempio.png) 
Subnet: 192.168.1.0/24 ↔ maschera 255.255.255.0
Chiave pratica:

Primo indirizzo = Network ID → non si usa per i device

Ultimo indirizzo = Broadcast → messaggi a tutti

In mezzo = Host → indirizzi assegnabili ai device


Sintesi chiara con metafora + nome tecnico.
* **Subnet (sottorete) = “quartiere”**

  * Tecnico: **Subnet**. È un gruppo di indirizzi IP che stanno nella stessa rete logica.

* **Network ID (indirizzo di rete) = “nome del quartiere”**

  * Tecnico: **Network ID**. È il **primo** indirizzo del blocco. Non si assegna ai dispositivi.

* **Broadcast address = “megafono del quartiere”**

  * Tecnico: **Broadcast**. È l’**ultimo** indirizzo del blocco. Messaggi a tutti gli host della subnet.

* **Host = “case del quartiere”**

  * Tecnico: **Host addresses**. Gli indirizzi **tra** Network ID e Broadcast che puoi assegnare a PC, telefoni, stampanti.

* **CIDR / prefisso = “taglia del quartiere”**

  * Tecnico: **Prefisso CIDR** (es. **/24**, **/26**). Più grande il numero, **più piccolo** il quartiere.

* **Subnet mask (maschera) = “stampo del quartiere”**

  * Tecnico: **Maschera** (es. **255.255.255.0**). Dice quali bit sono “rete” e quali “host”.
  * Equivalenze comuni:

    * **/24** ↔ **255.255.255.0**
    * **/26** ↔ **255.255.255.192**
    * **/28** ↔ **255.255.255.240**

* **Esempio base**

  * Subnet: **192.168.1.0/24**

    * **Network ID**: 192.168.1.0 → “nome quartiere”
    * **Broadcast**: 192.168.1.255 → “megafono”
    * **Host usabili**: 192.168.1.1–192.168.1.254 → “case” (254 case)

* **Esempio quartiere più piccolo**

  * Subnet: **192.168.1.128/26**

    * **Network ID**: 192.168.1.128
    * **Broadcast**: 192.168.1.191
    * **Host**: 192.168.1.129–190 (62 case)

* **Tabellino “taglie del quartiere”**

  * **/24** → 256 indirizzi totali → **254 host**
  * **/26** → 64 totali → **62 host**
  * **/28** → 16 totali → **14 host**




**SPIEGAZIONE BROADCAST PARLA CON TUTTI**
Significa: se mandi un messaggio all’indirizzo di broadcast, lo ricevono tutti i dispositivi della stessa subnet.

Dove si manda: all’ultimo indirizzo della subnet. Esempio /24: 192.168.1.255.

Chi lo riceve: tutti gli host di quel “quartiere” (.1–.254).

Fin dove arriva: solo dentro la subnet. Fuori non passa.

Mini-scena “rete di casa 192.168.1.0/24” Telefono si collega al Wi-Fi Invia DHCP Discover → 192.168.1.255. Il router risponde con un IP, es. 192.168.1.23. PC vuole parlare con la stampante 192.168.1.60 PC invia ARP in broadcast: “Chi ha 192.168.1.60?” Solo la stampante risponde con il suo MAC → poi comunicano.

# **we’re out of IP Addresses….but this saved us (Private IP Addresses)**
https://www.youtube.com/watch?v=8bhvn9tQk8o&list=PLIhvC56v63IKrRHh3gvZZBAGvsvOhwrRF&index=3 

NAT and private ip addresses

