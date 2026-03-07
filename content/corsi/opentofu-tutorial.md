+++
title: "OpenTofu: From 0 to Basic"
date: 2026-03-07
draft: false
tags: ["opentofu","terraform","iac","devops"]
+++

## Cos'è OpenTofu?

OpenTofu è un tool **Infrastructure as Code (IaC)** — ti permette di descrivere infrastruttura (server, reti, database, DNS...) in file di testo, e poi crearla, modificarla o distruggerla con un comando.

È il fork open source di Terraform, nato nel 2023 quando HashiCorp ha cambiato licenza. Sintassi identica, compatibile al 100%.

**Idea chiave:** invece di cliccare su una console AWS/GCP/Azure, scrivi cosa vuoi in un file `.tf` e OpenTofu lo crea per te. Sempre riproducibile, sempre versionabile con git.

---

## Installazione su Fedora

```bash
sudo dnf install opentofu
tofu version
# → OpenTofu v1.x.x
```

---

## Concetti fondamentali

### Provider
Il "driver" che parla con un servizio specifico. Esempi: `aws`, `google`, `kubernetes`, `local`.

### Resource
La cosa concreta che vuoi creare: un file, un bucket S3, un Pod Kubernetes.

### State
OpenTofu tiene traccia di cosa ha creato in un file `terraform.tfstate`. È la "memoria" di OpenTofu.

### I 3 comandi principali

```bash
tofu init     # scarica i provider necessari
tofu plan     # mostra cosa farà (senza fare niente)
tofu apply    # esegue le modifiche
tofu destroy  # distrugge tutto quello che ha creato
```

---

## Primo progetto — provider local (offline)

Il provider `local` crea file sul tuo filesystem. Perfetto per capire il workflow senza cloud.

### Setup

```bash
mkdir ~/tofu-base && cd ~/tofu-base
```

Crea `main.tf`:

```hcl
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

resource "local_file" "ciao" {
  filename = "${path.module}/output/ciao.txt"
  content  = "Hello from OpenTofu!"
}
```

### Esegui

```bash
# Inizializza — scarica il provider local
tofu init

# Vedi cosa farà
tofu plan

# Crea il file
tofu apply
# → digita "yes" quando chiede conferma

# Verifica
cat output/ciao.txt
# → Hello from OpenTofu!
```

### Modifica e riapplica

Cambia `content` in `main.tf`:

```hcl
content = "OpenTofu aggiornato!"
```

```bash
tofu plan
# → mostra: 1 to change

tofu apply
cat output/ciao.txt
# → OpenTofu aggiornato!
```

### Distruggi

```bash
tofu destroy
# Il file viene cancellato — lo state torna vuoto
```

---

## Variabili

Invece di valori fissi nel codice, usa variabili:

```hcl
variable "messaggio" {
  description = "Testo da scrivere nel file"
  type        = string
  default     = "Valore di default"
}

resource "local_file" "ciao" {
  filename = "${path.module}/output/ciao.txt"
  content  = var.messaggio
}
```

```bash
# Passa il valore da terminale
tofu apply -var="messaggio=Ciao da variabile!"

# Oppure crea un file terraform.tfvars
echo 'messaggio = "Ciao da tfvars!"' > terraform.tfvars
tofu apply
```

---

## Output

Gli output espongono valori dopo l'apply — utili per passare dati tra moduli o semplicemente leggere risultati:

```hcl
output "percorso_file" {
  value = local_file.ciao.filename
}
```

```bash
tofu apply
# → Outputs:
# percorso_file = "/home/salbar/tofu-base/output/ciao.txt"

# Leggi gli output in qualsiasi momento
tofu output
```

---

## Lo State — la memoria di OpenTofu

Dopo ogni `apply`, OpenTofu aggiorna `terraform.tfstate`:

```bash
cat terraform.tfstate
# → JSON con tutto quello che OpenTofu ha creato
```

**Regola importante:** non modificare mai `terraform.tfstate` a mano. OpenTofu lo gestisce lui.

```bash
# Vedi le risorse nello state
tofu state list

# Dettaglio di una risorsa
tofu state show local_file.ciao
```

---

## Struttura tipica di un progetto

```
mio-progetto/
├── main.tf           # risorse principali
├── variables.tf      # dichiarazione variabili
├── outputs.tf        # output
├── terraform.tfvars  # valori delle variabili (non committare se contiene segreti)
└── terraform.tfstate # stato (non committare — aggiungi a .gitignore)
```

---

## Prossimi passi

Una volta capito il workflow con il provider `local`, la logica è identica per qualsiasi cloud:

```hcl
# Stesso identico pattern — cambia solo il provider e le risorse
provider "aws" {
  region = "eu-west-1"
}

resource "aws_s3_bucket" "mio_bucket" {
  bucket = "mio-bucket-unico-123"
}
```

`tofu init` → `tofu plan` → `tofu apply` — sempre uguale.