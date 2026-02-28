+++
title = "Dockerfile"
date = 2026-02-28
draft = false
tags = ["docker"]
+++


# Docker COPY: La Guida Definitiva per Capire il Punto (.)

*Quando ho iniziato con Docker, una delle cose che più mi confondeva era il comando `COPY`. Perché a volte si usa `./` e altre volte `.`? Cosa significa esattamente quel punto? In questo articolo ti spiego tutto quello che ho imparato, con esempi pratici.*

## Il Problema che Avevo

Guardando i Dockerfile, vedevo comandi come:
```dockerfile
COPY package*.json ./
COPY . .
```

E mi chiedevo: "Ma il punto cosa copia esattamente? Un file? Una cartella? E perché a volte c'è `./` e altre solo `.`?"

## La Risposta Semplice

Il comando `COPY` ha sempre **due argomenti**:
```dockerfile
COPY <sorgente> <destinazione>
     ↑          ↑
   dal PC    nel container
```

Il punto `.` cambia significato a seconda di DOVE si trova.

## Sorgente vs Destinazione

### Quando il punto è SORGENTE (primo argomento)
```dockerfile
COPY . /app/
     ↑
   sorgente
```

**Significa:** "Copia TUTTO dalla directory corrente (del mio PC)"

**Cosa include:**
- Tutti i file
- Tutte le sottocartelle  
- Tutto il contenuto

### Quando il punto è DESTINAZIONE (secondo argomento)
```dockerfile
COPY file.txt .
              ↑
         destinazione
```

**Significa:** "Copia nella directory corrente del container"

Se hai fatto `WORKDIR /app`, allora `.` = `/app/`

## Gli Esempi Che Mi Hanno Salvato

### Esempio 1: Copiare package.json
```dockerfile
WORKDIR /app
COPY package*.json ./
```

**Cosa fa:**
- Sorgente: `package.json` e `package-lock.json` (dal mio PC)
- Destinazione: `./` = `/app/` (nel container)

**Risultato:**
```
/app/package.json
/app/package-lock.json
```

### Esempio 2: Copiare tutto
```dockerfile
WORKDIR /app
COPY . .
```

**Cosa fa:**
- Sorgente: `.` = tutto dalla cartella corrente (frontend/)
- Destinazione: `.` = `/app/`

**Risultato:**
```
/app/src/
/app/public/
/app/package.json
/app/README.md
... tutto
```

### Esempio 3: L'errore che facevo
```dockerfile
COPY package.json .
                  ↑ problema!
```

**Cosa succedeva:**
Docker creava un FILE chiamato `.` invece di copiare nella directory.

**Soluzione:**
```dockerfile
COPY package.json ./
                  ↑ directory!
```

## La Differenza tra `./` e `.`

| Destinazione | Cosa significa | Consiglio |
|--------------|----------------|-----------|
| `./` | Directory corrente (esplicito) | ✅ Usa sempre |
| `.` | Funziona ma ambiguo | ⚠️ Solo in `COPY . .` |

**Best practice:** usa sempre `./` tranne quando fai `COPY . .`

## Come Verificare Cosa Viene Copiato

Questa è la parte che mi ha aiutato di più. Invece di indovinare, HO GUARDATO:

### Metodo 1: Aggiungi ls nel Dockerfile
```dockerfile
COPY . .
RUN ls -la  # ← Mostra tutto
```

Poi:
```bash
docker build -t test .
```

Vedrai nell'output esattamente cosa c'è.

### Metodo 2: Entra nel container
```bash
# Build
docker build -t test .

# Entra dentro
docker run -it --rm test sh

# Guarda cosa c'è
ls -la /app/
```

### Metodo 3: Ispeziona un layer specifico
```bash
docker run --rm test ls -la /usr/share/nginx/html
```

## Il Caso Reale: Multi-stage Build

Ecco dove tutto si è chiarito per me:
```dockerfile
# Stage BUILD
FROM node:24-alpine AS builder
WORKDIR /app
COPY package*.json ./           # Solo dipendenze
RUN npm install
COPY . .                        # Tutto il codice
RUN npm run build               # Crea /app/build/

# Stage PRODUCTION  
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
                    ↑          ↑
                 sorgente    destinazione
                (da builder) (in nginx)
```

**Cosa succede:**
1. Stage builder: copia tutto in `/app/`, compila
2. Stage production: copia SOLO `/app/build/` (risultato compilato)
3. Immagine finale: solo nginx + file statici (leggera!)

## Errori Comuni (che ho fatto)

### Errore 1: Usare `..` per salire
```dockerfile
COPY ../file.txt .  # ❌ NON funziona
```

**Perché:** Docker ha un "build context". Non può accedere a file fuori.

**Soluzione:** Sposta Dockerfile nella directory giusta.

### Errore 2: Confondere punto finale
```dockerfile
COPY package.json .   # ⚠️ Crea file chiamato "."
COPY package.json ./  # ✅ Copia in directory
```

### Errore 3: Non usare .dockerignore

Senza `.dockerignore`, `COPY . .` copia ANCHE:
- `node_modules/` (pesante e inutile)
- `.git/` (non serve in container)
- File temporanei

**Soluzione:** crea `.dockerignore`:
```
node_modules
.git
*.log
.env
```

## Conclusione

Il punto `.` in Docker non è magico:
- Come sorgente = "tutto qui"
- Come destinazione = "qui dentro"

La chiave è capire che Docker lavora con due contesti:
- **Build context** (il tuo PC)
- **Container** (filesystem isolato)

`COPY` è il ponte tra questi due mondi.

 

---
 


 # Perché Docker Multi-Stage Build Ti Fa Risparmiare 400MB (E Come Funziona Davvero)

*Quando ho iniziato a dockerizzare la mia prima app React, l'immagine pesava 410MB. Dopo aver capito i multi-stage build, è scesa a 15MB. Stessa app, stesso funzionamento, 27 volte più leggera. Ti spiego come.*

## Il Problema Che Probabilmente Hai Anche Tu

Hai scritto il tuo primo Dockerfile per un'app React. Qualcosa tipo:
```dockerfile
FROM node:24-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
```

Fai il build, tutto funziona. Poi guardi la dimensione:
```bash
docker images
# REPOSITORY   TAG      SIZE
# my-app       latest   410MB
```

**410MB per servire qualche file HTML/CSS/JS?** 

E ti chiedi: "Ma non era Docker che doveva rendere tutto più leggero?"

## Cosa C'è Dentro Quei 410MB

Facciamo un'autopsia dell'immagine:
```dockerfile
FROM node:24-alpine           # 200MB - Node.js completo
COPY . .                      # 50MB  - Codice sorgente (src/)
RUN npm install               # 150MB - node_modules/
RUN npm run build             # 10MB  - build/ (output finale)
```

**Totale: 410MB**

Il problema? **L'immagine finale contiene TUTTO**, anche quello che serviva solo per compilare:

- ❌ Node.js (serviva per `npm run build`, ora inutile)
- ❌ node_modules/ (serviva per compilare, ora inutile)
- ❌ src/ (codice sorgente, ora inutile)
- ✅ build/ (QUESTO è l'unico che serve!)

**È come consegnare una casa con tutto il cantiere ancora attaccato.**

## La Domanda Che Mi Sono Fatto

> "Ma se serve solo `build/`, perché devo copiare anche `src/`?"

Risposta breve: **perché `npm run build` ha BISOGNO del codice sorgente per funzionare**.

Vediamo cosa succede quando esegui `npm run build`:
```bash
npm run build

# Internamente fa:
# 1. Legge src/App.js
# 2. Legge src/index.js
# 3. Legge public/index.html
# 4. Compila tutto
# 5. Ottimizza
# 6. Genera build/static/js/main.abc123.js
```

**Senza `src/`** → npm non ha niente da compilare → build fallisce.

**È come chiedere a un pasticcere di fare una torta senza dargli gli ingredienti.**

## La Soluzione: Multi-Stage Build

L'idea geniale: **usiamo DUE immagini invece di una**.

### Stage 1: Il Cantiere (Builder)

Qui facciamo tutto il lavoro sporco:
```dockerfile
# ============ STAGE 1 - BUILDER ============
FROM node:24-alpine AS builder
WORKDIR /app

# Installa dipendenze
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copia codice sorgente e compila
COPY . .              # ← Serve TUTTO per compilare
RUN npm run build     # ← Genera /app/build/

# A questo punto abbiamo:
# /app/src/          ← Serviva per compilare
# /app/node_modules/ ← Serviva per compilare  
# /app/build/        ← QUESTO è il risultato ✅
```

### Stage 2: La Casa Finita (Production)

Qui prendiamo SOLO il risultato:
```dockerfile
# ============ STAGE 2 - PRODUCTION ============
FROM nginx:alpine AS production

# Copia SOLO build/ dallo stage precedente
COPY --from=builder /app/build /usr/share/nginx/html

# Immagine finale contiene:
# - nginx (5MB)
# - build/ (10MB)
# TOTALE: 15MB 🎉
```

**La magia:** Docker butta via automaticamente lo stage `builder` dopo aver copiato `build/`.

## Il Trucco: --from=builder
```dockerfile
COPY --from=builder /app/build /usr/share/nginx/html
     ↑              ↑           ↑
     da stage    path stage   path finale
     builder     builder      production
```

Questo comando dice:
1. Prendi il filesystem dallo stage chiamato `builder`
2. Copia la cartella `/app/build/` 
3. Mettila in `/usr/share/nginx/html` (dove nginx serve i file)

**Tutto il resto (node_modules, src/, Node.js) viene scartato.**

## Confronto Visivo

### Single-Stage (Cantiere + Casa)
```
Immagine finale:
├── Node.js (200MB)          ❌ Serviva solo per compilare
├── node_modules/ (150MB)    ❌ Serviva solo per compilare
├── src/ (50MB)              ❌ Serviva solo per compilare
└── build/ (10MB)            ✅ L'unico che serve davvero

TOTALE: 410MB
```

### Multi-Stage (Solo Casa)
```
Stage Builder (buttato via):
├── Node.js
├── node_modules/
├── src/
└── build/ → copiato ↓

Immagine finale:
├── nginx (5MB)
└── build/ (10MB)

TOTALE: 15MB
```

## I Vantaggi Reali

### 1. Dimensione
```bash
# Prima
docker images
my-app    latest    410MB

# Dopo  
docker images
my-app    latest    15MB
```

**27x più leggera** → deploy più veloce, meno banda, meno storage.

### 2. Sicurezza

**Immagine single-stage contiene:**
- Codice sorgente completo
- Tutte le dev dependencies
- Node.js (superficie d'attacco)

**Immagine multi-stage contiene:**
- Solo file statici compilati
- Solo nginx (minimo necessario)

**Meno codice = meno vulnerabilità.**

### 3. Chiarezza
```dockerfile
# Stage BUILDER
# "Qui compilo"

# Stage PRODUCTION  
# "Qui servo"
```

Separazione chiara tra build-time e runtime.

## Quando Usare Multi-Stage

### ✅ Usa sempre per:

- **App React/Vue/Angular** (build → file statici)
- **App Go** (compila → binario)
- **App Java** (compila → JAR)
- **Qualsiasi cosa che "compila"**

### ❌ Non serve per:

- **Script Python/Node semplici** (nessuna compilazione)
- **Dockerfile già minimali** (es: solo nginx con file statici)

## Il Pattern Completo

Ecco il pattern che uso per ogni app frontend:
```dockerfile
# ============ STAGE 1: BUILD ============
FROM node:24-alpine AS builder
WORKDIR /app

# Layer cache-friendly (dipendenze separate)
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Compila app
COPY . .
RUN npm run build

# ============ STAGE 2: PRODUCTION ============
FROM nginx:alpine AS production

# Copia solo output compilato
COPY --from=builder /app/build /usr/share/nginx/html

# Config runtime (opzionale)
COPY --from=builder /app/public/config.js /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Come Verificare il Risparmio
```bash
# Build
docker build -t my-app .

# Vedi dimensione finale
docker images my-app

# Entra e guarda cosa c'è dentro
docker run -it --rm my-app sh
ls -la /usr/share/nginx/html/
# Solo build/, niente src/ o node_modules/
```

## Errori Comuni

### Errore 1: Copiare da stage sbagliato
```dockerfile
# ❌ SBAGLIATO
COPY --from=production /app/build /usr/share/nginx/html

# ✅ GIUSTO
COPY --from=builder /app/build /usr/share/nginx/html
```

### Errore 2: Nome stage non corrisponde
```dockerfile
FROM node:24-alpine AS build    # ← Nome: "build"

# Poi:
COPY --from=builder /app/build  # ❌ Cerca "builder" che non esiste

# ✅ GIUSTO
COPY --from=build /app/build
```

### Errore 3: Dimenticare AS
```dockerfile
FROM node:24-alpine            # ❌ Senza nome
RUN npm run build

FROM nginx:alpine
COPY --from=??? /app/build    # Come lo chiamo?

# ✅ GIUSTO
FROM node:24-alpine AS builder
```

## Conclusione

Multi-stage build non è una feature avanzata di Docker.

**È il modo STANDARD di fare build in Docker.**

Il pattern è sempre lo stesso:

1. **Stage builder**: fai tutto il lavoro sporco (compila, testa, genera)
2. **Stage production**: prendi SOLO il risultato finale
3. Docker butta via automaticamente gli stage intermedi

**Risultato:**
- Immagini 20-40x più leggere
- Più sicure (meno codice)
- Più veloci da deployare

La prossima volta che scrivi un Dockerfile, chiediti:

> "Cosa serve DAVVERO per far girare questa app in produzione?"

Tutto il resto? rimane nello stage builder.

---
 