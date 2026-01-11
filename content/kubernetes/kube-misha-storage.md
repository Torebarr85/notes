
+++
title = "Kubernetes: misha CKA - storage"
date = 2025-12-30
draft = false
tags = ["kubernetes"]
+++

# intro Volumes in Kubernetes - Concetti base

TL;DR: Volume is like a disk attached to the container or VM.

## Recap: perché servono i volumi

Se hai già lavorato con Docker o VM, il concetto di volume ti sarà familiare.

**Il problema dei container:**
- I container sono **ephemeral** (temporanei)
- Quando un container muore, tutti i dati al suo interno vengono persi
- Serve un modo per persistere i dati

**La soluzione:**
Un **volume** è necessario per salvare dati in modo permanente.

---

## Cos'è un volume

Un volume è semplicemente **un pezzo di file system** che vive separato dal container.

**Dove può trovarsi:**
- **Local storage:** disco della macchina dove gira il container
- **Cloud storage:** storage provisionato nel cloud (es. AWS EBS, Azure Disk, GCP Persistent Disk)
- **Network storage:** se il container è in cloud, puoi attaccare network storage per permettere al container di recuperare e inviare dati

---

## Concetto chiave: separazione

**Il principio fondamentale:**
- Lo storage **NON vive nel container stesso**
- Il volume è un'**entità separata** che esiste da qualche parte (locally o remotamente)
- Il container può **leggere e scrivere** su questo volume
- Anche se il container viene eliminato, **il volume e i suoi dati rimangono**
 
# Ephemeral Storage


# Persistent Storage