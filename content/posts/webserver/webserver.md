
# **WEB SERVER**

https://www.youtube.com/watch?v=9J1nJOivdyw

just a piece of software that serves web content.

- listen on a port
- for a request
- transport protocol
- response containing the resource
- resource


🔹 1. Ogni frontend ha bisogno di un web server

Il browser non legge “file dal disco”, ha bisogno di qualcuno che glieli dia via HTTP.

Quel qualcuno è un web server: Nginx, Apache, Caddy, S3+CloudFront… o anche un serverino Node come serve.

🔹 2. Angular, React, Vue in dev mode

Quando fai ng serve (Angular) o npm run dev (React/Vite):

Parte un dev server scritto in Node.

È pensato solo per sviluppo (hot reload, watch dei file, debugging).

Non è ottimizzato per produzione (niente caching, niente compressione seria, meno stabile).

🔹 3. In produzione

Dopo npm run build ottieni una cartella (dist/ o build/) con solo file statici.

Questi file vanno serviti da un vero web server:

Nginx → leggero, veloce, fa bene caching + gzip + headers.

Apache → più pesante ma fa il suo.

Caddy → minimal + HTTPS automatico.

Cloud-native → metti i file in S3 e li distribuisci via CloudFront (zero server da gestire).

🔹 4. Perché non usare il dev server in prod?

Non è fatto per reggere carico, non scala, non ottimizza asset.

Non gestisce bene HTTPS, headers di sicurezza, fallback puliti.

In pratica: funziona, ma è un anti-pattern.



🔹 TL;DR

✅ Sviluppo → Angular/React hanno già un mini server integrato (comodo).
✅ Produzione → sempre dietro un vero web server (Nginx, Apache, Caddy o CDN).
👉 Il framework JS non è un web server, produce solo file che qualcuno deve consegnare via HTTP

**Regole d’oro per ricordarlo**

- Backend = già un server (parla da solo su una porta).
- Nginx = opzionale ma utile:
- serve i file del frontend,
- fa da ponte verso il backend su /api,
- ti dà ordine e controllo all’ingresso.

2) Quando metti Nginx davanti anche al backend?

Non per farlo parlare, ma per organizzare meglio l’ingresso.

A Unico entrypoint (stesso dominio/porta)
. vuoi unico entrypoint

- Frontend (SPA): i file statici (index.html, JS, CSS) devono essere serviti da qualcuno → qui Nginx è perfetto.
- Backend (API): vogliamo che le chiamate siano su /api/... sullo stesso dominio.

Browser → http://localhost/
           ├─ /           → Nginx serve lo SPA (file statici)
           └─ /api/...    → Nginx fa da “ponte” al backend (proxy → backend:8080)

1) “Non ti serve Nginx per far parlare il backend”
- Un backend (es. Quarkus, Node/Express, Spring Boot) è già un server.
- Quando lo avvii, lui ascolta su una porta (es. :8080) e risponde alle richieste HTTP.
- Quindi se apri il browser su http://localhost:8080/hello, il backend risponde da solo.
Non serve Nginx per “dargli voce”: la voce ce l’ha già.



