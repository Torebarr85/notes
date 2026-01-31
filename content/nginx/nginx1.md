+++
title = "Nginx, Architettura Web, web server vs application server"
date = 2025-10-14
draft = false
tags = ["nginx"]
+++

### Come funziona il browser
Il browser interpreta **nativamente** tre tecnologie:
- HTML (struttura)
- CSS (stile)
- JavaScript (logica)

Il browser può recuperare questi file in due modi:
- **Via HTTP/HTTPS**: da un server web (caso normale)
- **Via file://**: direttamente dal filesystem locale (senza server)

## Angular Build: Dal Codice al Browser

### Il problema del bundle
Quando fai il build di Angular:
1. Il codice TypeScript/Angular viene compilato in un **bundle JavaScript**
2. Questo bundle è un semplice file `.js`, ma **non può essere eseguito da solo**
3. Ha bisogno di essere **servito via HTTP** perché il browser possa scaricarlo

### Perché serve un web server
Il bundle da solo non basta perché:
- Il browser si aspetta di ricevere file via protocollo HTTP/HTTPS
- Serve qualcuno che "ascolti" su una porta (es. 80, 443, 8080) e risponda alle richieste
- Questo "qualcuno" è un **web server** (Nginx, Apache, ecc.)

## Architettura Tipica

```
Browser (interpreta HTML/CSS/JS; fetch JSON)
    │  
    │  HTTPS
    ▼
Web Server (Nginx/CDN)
    │  
    ├─→ Serve file statici (SPA: HTML, CSS, JS)
    │  
    └─→ Proxy /api → Application Server
                      │
                      └─→ Quarkus/Express/Spring
                          └─→ Logica + DB → Risponde con JSON
```

## Web Server vs Application Server

### Web Server (es. Nginx)
**Cosa fa:**
- Serve file statici (HTML, CSS, JS, immagini)
- Fa da proxy/reverse proxy verso altri server
- Gestisce HTTPS/certificati
- Load balancing

**Cosa NON fa:**
- Non esegue logica applicativa
- Non parla con database
- Non gestisce sessioni/autenticazione complessa

### Application Server (es. Quarkus, Spring Boot, Express)
**Cosa fa:**
- Espone API HTTP/REST
- Esegue logica di business
- Si connette a database
- Gestisce transazioni, security, job schedulati
- **Include già un server HTTP embedded** (Vert.x per Quarkus, Tomcat per Spring, ecc.)

**Differenza chiave:**
- In **sviluppo**: Quarkus ascolta su porta 8080 → il browser chiama direttamente `http://localhost:8080/api`
- In **produzione**: spesso si mette Nginx davanti come reverse proxy (non obbligatorio, ma comune)

## Frontend: Dev vs Prod

### In sviluppo
Angular CLI include un web server di sviluppo:
- Comando: `ng serve`
- Porta: di solito 4200
- Funzionalità: **hot reload** (ricarica automatica al cambio codice)

### In produzione
Il frontend diventa **solo file statici**:
1. Build: `ng build --configuration production`
2. Output: cartella `dist/` con HTML, CSS, JS
3. Deploy: copi questi file su un web server (Nginx, CDN, S3, ecc.)
4. **Non serve più il dev server di Angular**

## Nginx in Kubernetes (EKS)

### Deployment tipico
```
Pod Frontend (Deployment)
    └─→ Container Nginx
        └─→ File statici Angular dentro /usr/share/nginx/html
```

**Come funziona:**
1. Dockerfile copia il bundle Angular dentro l'immagine Nginx
2. Nginx serve questi file quando arrivano richieste HTTP
3. Il browser scarica `index.html`, che carica il bundle JS
4. Il bundle JS fa chiamate API al backend

### Configurazione Nginx tipica
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    
    # Serve file statici
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy alle API backend
    location /api {
        proxy_pass http://backend-service:8080;
    }
}
```

## Riepilogo Finale

| Componente | Dev | Prod |
|------------|-----|------|
| **Frontend Angular** | `ng serve` su porta 4200 (con hot reload) | File statici serviti da Nginx/CDN |
| **Backend Quarkus** | `quarkus dev` su porta 8080 (già HTTP embedded) | Stessa cosa, ma spesso dietro Nginx come proxy |
| **Nginx** | Non necessario | Serve statici + proxy API (opzionale ma comune) |

**Punti chiave:**
- Il browser può parlare direttamente con Quarkus (ha già HTTP embedded)
- Nginx NON è obbligatorio per "aprire la porta" del backend
- Nginx è utile in produzione per: servire statici, SSL, load balancing, separazione frontend/backend