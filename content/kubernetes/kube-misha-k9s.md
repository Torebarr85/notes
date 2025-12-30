+++
title = "Kubernetes: misha CKA - K9S"
date = 2025-12-30
draft = false
tags = ["kubernetes"]
+++

# K9S basic commands & managing clusters with k9s

## Concetti base
K9s funziona come VIM, usa gli stessi pattern di navigazione e shortcuts.

**Vedere tutti i comandi disponibili:** premi `?`

---

## Navigazione e sorting

**Ordinamento:**
- `Shift + A` → ordina per age (età)
- `Shift + S` → ordina per status

**Ricerca:**
- `/` + keyword → cerca nella lista corrente (pods, namespaces, etc.)

---

## Gestione dei pod

**Comandi principali:**
- `S` → apre shell nel pod (equivalente di `kubectl exec`)
- `Ctrl + K` → elimina/riavvia il pod
- `D` → mostra `kubectl describe` (funziona su qualsiasi risorsa selezionata: pod, service, deployment, etc.)
- `Y` → visualizza lo YAML della risorsa
- `Shift + F` → mostra il port-forwarding attivo (se configurato)

---

## Log management

**Visualizzare i log:**
1. Posizionati su un pod
2. Premi `L` per aprire i log
3. Navigazione nei log:
   - `J` / `K` → scroll riga per riga
   - `Ctrl + D` → scroll giù di una pagina
   - `0` → vai in tail mode (ultimi log)

**Ricerca nei log:**
- `/` + keyword → cerca una parola specifica nei log

**Tip:** Se apri l'app e a fianco tieni k9s aperto, vedi i log in streaming real-time mentre interagisci con l'applicazione.

---

## Filtri per resource type

Usa `:` seguito dal tipo di risorsa per filtrare la vista:

- `:pod` → visualizza solo i pod
- `:deploy` → visualizza solo i deployment (puoi anche scalarli da qui)
- `:service` → visualizza i service
- `:ingress` → visualizza gli ingress
- `:pvc` → visualizza i persistent volume claims

---

**Workflow tip:** Parti da `:pod` per vedere i pod, usa `/` per trovare quello che ti serve, poi `L` per i log o `S` per entrare in shell.