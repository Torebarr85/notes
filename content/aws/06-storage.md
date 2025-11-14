+++
title = "6 - Storage"
date = 2025-10-18
draft = false
tags = ["aws"]
+++

# Module 6 - Storage

### Prerequisites: **Differenze tra Block, File e Object Storage**

#### **1. Block-based storage**

* È il tipo di archiviazione usato nei **dischi rigidi (HDD)** e negli **SSD**.
* I dati sono salvati in **blocchi** che il sistema operativo può leggere e scrivere direttamente.
* Tipico di sistemi locali o infrastrutture on-premise.
* Permette di creare **volumi, partizioni e file system** (es. NTFS su Windows).
* Può essere anche collegato in rete tramite protocolli come **iSCSI** o **Fibre Channel**.
* Offre **alte prestazioni**, ma è meno flessibile e scalabile rispetto al cloud object storage.

#### **2. File-based storage**

* Si basa su un **file system condiviso in rete**, come in un **NAS (Network Attached Storage)**.
* I file vengono salvati in **cartelle e sottocartelle** e condivisi tramite la rete (es. SMB, NFS).
* Più utenti e dispositivi possono accedere contemporaneamente allo stesso file system.
* È ancora molto usato in ambito aziendale per la condivisione di dati.
* L’OS vede le cartelle remote come **unità di rete** (es. “Z:\”).

#### **3. Object-based storage**

* Utilizzato principalmente nel **cloud** (es. **Amazon S3**).
* I dati vengono salvati come **oggetti** dentro **bucket**, accessibili tramite **API REST (HTTP)**.
* Ogni oggetto ha **metadati** e un **ID univoco**, ma **non esiste una struttura gerarchica reale** (le “cartelle” sono simulate).
* Altamente **scalabile**, **economico** e **ideale per backup, log, media, archiviazione dati e integrazione con app**.
* Non serve montarlo come un’unità: si accede tramite **web o applicazioni**.

---

### **In sintesi**

* **Block storage** → prestazioni elevate, usato per database e dischi virtuali.
* **File storage** → condivisione di file tra utenti via rete.
* **Object storage** → scalabilità, costo basso, accesso via API, perfetto per il cloud.

---

 
## 🔹 Key Ideas
Brief summary of what this module covers.

## 🔸 Main Concepts
- Concept 1
- Concept 2
- Concept 3

## 🔹 Example
```bash
# Example AWS CLI command
aws --version
```

## 🔹 Exam Tips
> Add exam-specific reminders here.


