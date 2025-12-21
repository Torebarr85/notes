+++
title = "Dockerfile"
date = 2025-12-21
draft = false
tags = ["docker"]
+++

```
# ========================================
# STAGE 1: Build Angular app
# ========================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies (production only)
RUN npm ci --only=production

# Copy source code
COPY . .

# Build for production
RUN npm run build -- --configuration production


# **SPIEGAZIONE:**
# - COSA: **NUOVA immagine** da zero (scarta stage 1!)
# - `nginx:alpine`: Nginx su Linux Alpine (25 MB)
# - PERCHÉ: Stage 1 aveva Node.js (600 MB) che non serve più

# **MAGIA MULTI-STAGE:**
# ```
# Stage 1 (builder): 600 MB → SCARTATO ✅
# Stage 2 (nginx):    25 MB → VA IN K8S ✅

# ========================================
# STAGE 2: Nginx production server
# ========================================
FROM nginx:alpine

COPY --from=builder /app/dist/my-app-fe /usr/share/nginx/html

# SPIEGAZIONE:
# --from=builder

# COSA: Copia file da Stage 1 (non dal tuo PC!)
# DA DOVE: /app/dist/frontend dentro container builder
# VERSO DOVE: /usr/share/nginx/html (default Nginx)

# PERCHÉ /usr/share/nginx/html?

# È la directory dove Nginx cerca file da servire
# Configurazione default Nginx:

# location / {
#       root /usr/share/nginx/html;
#   }


# Expose port
EXPOSE 80
# Documentazione che container usa porta 80
# ⚠️ NON apre la porta! (è solo un'etichetta)
# Kubernetes leggerà questo per sapere su che porta connettersi

# Start nginx
CMD ["nginx", "-g", "daemon off;"]


# **SPIEGAZIONE:**

# **`CMD`**: Comando di default quando container parte

# **`nginx -g "daemon off;"`**
# - COSA: Avvia Nginx in foreground (non background)
# - PERCHÉ: Docker richiede processo in foreground, altrimenti container si ferma

# **SENZA `daemon off;`:**
# ```
# Container parte → Nginx va in background → Container pensa "finito!" → Si ferma ❌
# ```

# **CON `daemon off;`:**
# ```
# Container parte → Nginx resta in foreground → Container resta attivo ✅    

```


# app/frontend/.dockerignore
node_modules
dist
.git
.gitignore
*.md
.vscode

### 📊 VISUALIZZAZIONE COMPLETA
```
STEP 1: WORKDIR /app
Container: /app/ (vuota)

STEP 2: COPY package*.json ./
Container: /app/
           ├── package.json
           └── package-lock.json

STEP 3: RUN npm ci
Container: /app/
           ├── package.json
           ├── package-lock.json
           └── node_modules/ (5000+ file)

STEP 4: COPY . .
Container: /app/
           ├── src/
           ├── angular.json
           ├── package.json
           ├── package-lock.json
           ├── Dockerfile
           └── node_modules/

STEP 5: RUN npm run build
Container: /app/
           ├── src/
           ├── dist/
           │   └── frontend/  ← NUOVO!
           │       ├── index.html
           │       └── main.js
           ├── node_modules/
           └── ...