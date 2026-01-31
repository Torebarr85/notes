+++
title = "osi model on k8s"
date = 2026-01-31
draft = false
tags = ["networking","osi-model"]
+++

# OSI Model attraverso Kubernetes
# Il Viaggio Completo - Versione Narrativa

Okay, rifacciamo tutto come se stessi raccontando una storia. Niente schemi, parliamoci.

---

## La Persona e il Browser

Immagina: sei seduto al computer, apri Chrome e digiti `https://myapp.com/login`. Premi invio.

**Cosa fa il browser in questo momento?**

Prima di tutto, il browser è completamente ignorante. Non sa dove diavolo sia `myapp.com`. È come se tu avessi un indirizzo scritto su un foglio ma non sai in che città si trova.

Quindi la **prima cosa** che fa è chiedere al DNS: "Ehi, questo myapp.com... dove sta di casa?". Il DNS risponde: "Ah sì, quello vive al numero `203.0.113.50`". Questo è l'**IP pubblico**.


## Dove chiede?
Il browser fa una richiesta al **DNS server** configurato sul tuo PC.
Apri il terminale e fai:
```bash
# Su Linux/Mac
cat /etc/resolv.conf

# Output esempio:
nameserver 192.168.1.1
nameserver 8.8.8.8
```

Adesso il browser sa dove andare. Apre una connessione TCP verso quell'indirizzo, sulla porta 443 (perché hai scritto https). Fa il "three-way handshake" - quella cosa del SYN, SYN-ACK, ACK che probabilmente hai visto studiando networking. Stabilisce la connessione crittografata con TLS.

A questo punto la connessione è aperta e sicura. Il browser manda la richiesta vera e propria:

```
GET /login HTTP/1.1
Host: myapp.com
User-Agent: Chrome/123.0
```

Questo pacchetto parte dal tuo computer e viaggia su internet.

---

## L'IP Pubblico - Il Primo Guardiano

Quel `203.0.113.50` non è il tuo cluster Kubernetes. È un **LoadBalancer del cloud provider**.

Se sei su AWS, è un Elastic Load Balancer. Se sei su GCP, è un Google Cloud Load Balancer. Questi aggeggi sono gestiti dal cloud provider, non da te. Li hai creati quando hai fatto il deploy del tuo Ingress Controller (ci arriviamo).

**Cosa fa questo LoadBalancer?**

Riceve la tua richiesta da internet e deve smistarla verso il cluster Kubernetes. Il cluster è fatto di 3 macchine virtuali (i **Worker Nodes**), ognuna con un suo IP privato tipo `10.0.1.5`, `10.0.1.6`, `10.0.1.7`.

Il LoadBalancer sceglie uno di questi nodi - diciamo `10.0.1.5` - e gli inoltra il traffico. Ma su che porta? Qui entra in gioco il **NodePort**.

---

## Il NodePort - La Porta d'Ingresso

Quando hai installato l'Ingress Controller nel cluster (tipo nginx-ingress con Helm), Kubernetes ha creato automaticamente un **Service di tipo NodePort**.

Questo significa che su **tutti i nodi** del cluster, Kubernetes ha aperto una porta specifica - esempio `30080` - e l'ha mappata all'Ingress Controller.

Quindi il LoadBalancer esterno punta a:
- `10.0.1.5:30080` (Node1)
- `10.0.1.6:30080` (Node2)  
- `10.0.1.7:30080` (Node3)

Tutti e tre i nodi ascoltano su quella porta, anche se l'Ingress Controller (il pod nginx) sta fisicamente girando solo su uno di loro.

**Come è possibile?**

Qui c'è la magia di `kube-proxy`. Su ogni nodo gira questo processo che configura delle regole di iptables. Quando un pacchetto arriva su `Node1:30080`, iptables dice: "Ah, questa porta è legata al Service ingress-nginx-controller. Devo redirigere il traffico al pod corretto."

Il pod dell'Ingress Controller ha un suo IP - diciamo `10.244.1.10` - e gira su `Node2`. Quindi iptables su Node1 fa un redirect:

```
Pacchetto arriva su 10.0.1.5:30080 (Node1)
→ iptables: "Questa porta va al pod 10.244.1.10:80"
→ Il pacchetto viene reinoltrato a Node2
```

**Come viaggia questo pacchetto da Node1 a Node2?**

Attraverso la **rete overlay** creata dal CNI plugin (Calico, Flannel, etc.). Questi plugin creano una rete virtuale che connette tutti i pod di tutti i nodi, come se fossero sulla stessa LAN. Usano tecniche tipo VXLAN o IP-in-IP per incapsulare i pacchetti.

---

## L'Ingress Controller - Il Cervello

Il pacchetto finalmente arriva al pod `nginx-ingress-controller` che gira su Node2.

Questo pod è un **normale nginx**, identico a quello che installeresti su un server Linux. Ma è configurato in modo speciale: Kubernetes gli passa automaticamente tutte le regole degli Ingress Resource che hai creato.

Nginx riceve la richiesta HTTP:
```
GET /login HTTP/1.1
Host: myapp.com
```

Nginx legge l'header `Host: myapp.com` e controlla la sua configurazione. Tu hai creato un Ingress Resource che diceva:

```yaml
rules:
- host: myapp.com
  http:
    paths:
    - path: /login
      backend:
        service:
          name: frontend-service
          port:
            number: 80
```

Nginx legge questa regola e pensa: "Okay, richiesta per myapp.com sul path /login... devo inoltrarla al Service chiamato `frontend-service` sulla porta 80."

**Perché nginx lavora a Layer 7?**

Perché sta leggendo dentro il contenuto del pacchetto HTTP. Guarda l'URL, gli headers, decide dove mandare la richiesta basandosi sul contenuto applicativo. Non si limita a guardare IP e porte (quello sarebbe Layer 4).

Nginx ora fa una nuova richiesta HTTP verso `frontend-service:80`.

---

## Il Service - L'Indirizzario Magico

`frontend-service` è un Service di tipo ClusterIP. Ha un IP virtuale - diciamo `10.96.0.50` - che esiste solo nella configurazione di Kubernetes. Non è un IP "vero" su nessuna interfaccia di rete.

**Come funziona?**

Quando hai creato il Deployment dei tuoi pod frontend:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 8080
```

Kubernetes ha creato 3 pod, ognuno con un suo IP unico:
- Pod 1: `10.244.1.15` su Node2
- Pod 2: `10.244.2.22` su Node3
- Pod 3: `10.244.3.18` su Node1

Poi hai creato il Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 8080
```

Kubernetes guarda il `selector: app=frontend` e trova i 3 pod che hanno quel label. Li registra come **Endpoints** del Service.

Puoi vederlo con:
```bash
kubectl get endpoints frontend-service
```

Output:
```
NAME               ENDPOINTS
frontend-service   10.244.1.15:8080,10.244.2.22:8080,10.244.3.18:8080
```

**Ora la parte interessante:**

Quando nginx fa la richiesta a `frontend-service:80` (cioè a `10.96.0.50:80`), il pacchetto passa attraverso le regole iptables configurate da kube-proxy.

Kube-proxy ha creato regole che dicono:

```
Se vedi un pacchetto destinato a 10.96.0.50:80
→ Scegli random uno di questi IP:
  - 10.244.1.15:8080
  - 10.244.2.22:8080
  - 10.244.3.18:8080
→ Cambia l'IP di destinazione (DNAT - Destination NAT)
```

Quindi iptables **riscrive il pacchetto**. Se sceglie il primo pod, l'IP di destinazione diventa `10.244.1.15` e la porta diventa `8080`.

**Perché Layer 4?**

Perché iptables guarda solo IP e porta. Non apre il pacchetto HTTP per leggere cosa c'è scritto dentro. Fa solo load balancing a livello TCP.

---

## Il Pod - Finalmente a Casa

Il pacchetto arriva al pod `frontend-xyz` con IP `10.244.1.15`.

Questo pod gira su Node2. Dentro il pod c'è un container che esegue nginx (o la tua applicazione). Nginx sta in ascolto sulla porta 8080.

**Cosa vede nginx dentro il pod?**

Vede la richiesta HTTP originale:
```
GET /login HTTP/1.1
Host: myapp.com
```

Nginx processa questa richiesta. Magari serve un file HTML statico, o fa da reverse proxy verso un backend Node.js che gira in un altro container nello stesso pod.

L'applicazione genera una risposta:
```
HTTP/1.1 200 OK
Content-Type: text/html

<html>
  <body>
    <h1>Login Page</h1>
    <form>...</form>
  </body>
</html>
```

---

## Il Ritorno - Stesso Percorso al Contrario

La risposta HTTP parte dal container nginx nel pod. Esce dalla porta 8080 del pod.

Iptables vede il pacchetto di ritorno. Ricorda la connessione (perché TCP è stateful) e fa il reverse NAT:

```
Pacchetto da 10.244.1.15:8080
→ iptables: "Questo era parte di una connessione verso frontend-service"
→ Cambia source IP a 10.96.0.50:80
```

Il pacchetto torna all'Ingress Controller nginx.

Nginx lo riceve e lo reinvia verso il client originale (il tuo browser), passando di nuovo attraverso:
- La rete CNI (da Node2 a Node1 dove era entrato)
- Il NodePort 30080
- Il LoadBalancer esterno 203.0.113.50
- Internet
- Il tuo browser

Il browser riceve la risposta HTML e renderizza la pagina di login.

---

## Ricapitolando con una Metafora Concreta

Pensa al cluster come a un **grande palazzo di uffici**.

- **LoadBalancer esterno**: il portone principale sulla strada (IP pubblico)
- **NodePort**: l'atrio con le porte d'ingresso (tutti e 3 i nodi hanno la stessa porta aperta)
- **Ingress Controller**: la Reception al primo piano che legge il tuo badge (Host header) e ti dice: "Lei deve andare all'ufficio Frontend-Service, piano 5"
- **Service**: il numero di telefono interno dell'ufficio Frontend (10.96.0.50:80). Non è una stanza fisica, è solo un numero che reindirizza a 3 scrivania diverse
- **Endpoints/iptables**: il centralino che squilla a una delle 3 scrivanie disponibili
- **Pod**: la scrivania vera dove lavora una persona (il container) che ti risponde

Il LoadBalancer del cloud provider (AWS ELB, etc.) non fa parte del cluster. È fuori. Kubernetes gli dice solo: "Ehi AWS, crea un LB che punti ai miei nodi su porta 30080."

---
 