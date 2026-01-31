+++
title = "Nginx: <titolo>"
date = 2025-10-14
draft = false
tags = ["nginx"]
+++

# **NGINX**
“Reverse-proxy to an app on localhost”
NGINX riceve le richieste e le inoltra a un’app che gira sulla stessa macchina, di solito su 127.0.0.1:PORT. Così:

l’app non espone porte pubbliche

TLS, compressione, rate limit li fa NGINX

puoi fare routing e bilanciamento

**NGINX Explained - What is Nginx**
[x]  https://www.youtube.com/watch?v=iInUBOVeBCc&t=484s

- NGINX = piece of software on a server that handles HTTP requests.
- NGINX once when internet was easy was only a high performance webserver but now with millions of http requests can also act as a load balancer: distributes incoming traffic acrosso multiple backend servers (with others nginx)
- PROXY = Acting on behalf of another, proxy server: intermediaty servers that forwards client requests to other servers with the fewest active connections.
- NGINX configurations….
- NGINX in KUBERNETES: nginx as K8S Ingress Controller→ essentially a proxy , specialized load balancer for managing ingress (incoming) traffic in kubernetes.
- perché se già i cloud platform come AWS hanno i loro load balancer, dovremmo usare nginx? perché lavorano insieme.
    - NGINX ingress controller act as load balancer inside the k8s cluster. Not public accessibile.
    - while the cloud load balancer (AWS ELB) is accessibile from public.
    - super security! so the cluster is never directly exposed to public access
        
![alt text](../attachments/elbnginx.png)

**NGINX VS APACHE web server**

are pretty much the same thing. 

![alt text](../attachments/nginxvsapache.png)



# **IT FUNDAMENTALS:**
- [ ]  https://www.youtube.com/playlist?list=PLy7NrYWoggjzDAxOxWazuVSsndW3fUinz



# OSI MODEL on k8s
```bash 
- Layer 4 load balancer lavora a livello TCP/UDP - guarda solo IP e porta, non sa cosa c'è dentro. È veloce ma 'cieco' al contenuto. 
- Layer 7 ingress lavora a livello HTTP - legge header, URL, cookie. Può fare routing intelligente tipo 'tutte le richieste /api vanno a backend API, /static a server file statici'. È più lento ma più flessibile. 

Su Kubernetes: 
Service di default -> Layer 4
Ingress -> Layer 7

```

# LOAD BALANCER - Cos'è
```bash 
In parole semplici:
Hai 3 server che fanno la stessa cosa (es. 3 pod con la tua app). 
Le richieste degli utenti devono essere distribuite tra questi 3 server per non sovraccaricare uno solo.

Il load balancer fa:

- Riceve richiesta utente
- Sceglie quale server usare (round-robin, least connections, ecc.)
- Invia richiesta a quel server
- Se un server è down, lo esclude automaticamente

Esempio concreto K8s:
User → Service (LoadBalancer type) → 3 Pod replica
Kubernetes Service FA da load balancer automaticamente tra i pod.
```

# REVERSE PROXY - Cos'è
```bash 
Differenza con load balancer:

Load balancer = distribuisce carico tra **server** identici
Reverse proxy = instrada richieste a **servizi**  DIVERSI in base a regole


Fa anche:

- SSL termination (gestisce HTTPS, backend può essere HTTP)
- Caching
- Compressione
- Header manipulation
```

# Nginx - Cosa devi sapere
```bash 
# Cos'è: Web server + reverse proxy + load balancer. Molto versatile.
Usi comuni:

- Web server: serve file HTML/CSS/JS statici
- Reverse proxy: instrada richieste a backend (come Ingress controller in K8s)
- Load balancer: distribuisce tra server multipli
- SSL termination: gestisce certificati HTTPS

Esempio K8s:
Nginx Ingress Controller usa Nginx per gestire routing HTTP verso servizi K8s.
```



