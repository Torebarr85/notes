+++
title = "Kubernetes: crash course"
date = 2025-11-15
draft = false
tags = ["kubernetes"]
+++

# VM, HYPERVISOR, CONTAINERS
Riepilogo super rapido:
- Hypervisor = gestore che crea VM
- VM = computer virtuale completo
- Container = processi isolati che condividono il kernel dell’host

Metafora:
- Pensa all’hypervisor come amministratore del condominio e gli appartamenti sono le VM
- VM = appartamenti completi, ognuno con il proprio impianto elettrico, idraulico, ecc.(il suo sistema operativo intero)
- Container = stanze nello stesso appartamento che condividono bagno e cucina (kernel dell'host)

**Kernel**
- È la parte che “parla” con l’hardware.
- il cuore del OS 
- gestisce CPU,RAM,storage, permessi, processi  

capire il kernel ti sblocca subito la differenza tra VM e container:
- VM: ognuna ha un proprio kernel dedicato
- Container: condividono lo stesso kernel dell’host

Quindi:
- VM = pesanti
- Container = leggeri

***Virtual Machine (VM)***
- Una VM è un computer completo dentro un altro computer.
Ogni VM ha:
- il suo sistema operativo (Linux, Windows…)
- le sue risorse “virtualizzate” (CPU, RAM, disco)

***Hypervisor***
È il software che crea e gestisce le VM macchine virtuali.
- L’hypervisor crea le VM.
- Permette di ospitare diversi virtual computer su un fisico computer. 
![alt text](../attachments/hypervisor.png)

***TYPE 1 hypervisor***
esempio: VMWare
- installato direttamente sull'hardware
- per big servers
- chiamato anche BARE METAL HYPERVISOR
- non deve chiedere in prestito risorse. le controlla direttamente = performance migliori, gli users possono scegliere any resource combinations

***TYPE 2 hypervisor***
esempio: virtual box
- installato sull'Host OS (operating system) che a sua volta è installato sull'hardware
- per uso personal
- chiamato anche HOSTED HYPERVISOR
- chiede in prestito all'host OS di dargli dell'hardware in prestito per gestire le virtual machines: crea virtual CPU, virtual RAM, virtual STORAGE per ogni virtual machine = le risorse hardware sono shared! puoi dare solo quelle che fisicamente esistono.

***Containers vs VM***
- virtualization and VM are virtualizing hardware → while Docker Docker virtualizza "l’ambiente OS", non il sistema operativo completo. Un container può farti sembrare di essere dentro un sistema Linux diverso (tipo Alpine, Ubuntu, ecc.), ma sotto usa sempre il kernel dell’host. Quindi se l’host è Windows, il kernel è Windows.
- VM → ognuna ha il suo sistema operativo intero
- Container → condividono lo stesso kernel dell’host


**************************

# KUBERNETES
Orchestra i containers

