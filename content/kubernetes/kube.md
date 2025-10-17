+++
title = "Kubernetes: <titolo>"
date = 2025-10-14
draft = false
tags = ["kubernetes"]
+++


# Kubernetes

**Cluster**
![alt text](./attachments/cluster.jpeg)
- Cluster = l’intero datacenter Kubernetes
- Cos’è il cluster EKS:  composto da Control plane + Worker nodes

*Control plane:* API server, scheduler, controller manager, etcd. In EKS è gestito da AWS. Non c’è un tuo “master node” su EC2.

*Worker nodes:* le istanze dove girano i Pod. Sono EC2 (providerID AWS), pronte, v1.33.4-eks-…

- Comando utile: kubectl get nodes -o wide

**Namespace**
- Namespace = “stanze” dentro quel datacenter. Più namespace convivono nello stesso cluster.

L’isolamento è solo logico: per isolare rete serve NetworkPolicy.

Quote/limiti si applicano a livello di namespace, non di cluster.

Cos’è un namespace

Partizione logica dentro un singolo cluster.

Contiene risorse “namespaced” (Pod, Service, Deployment, ConfigMap, Secret, …).

Non contiene risorse “cluster-scoped” (Node, PersistentVolume, ClusterRole, CRD, …).

Serve per isolamento logico, quote/limiti, RBAC e naming.

Comandi tipici:

kubectl get ns

kubectl get pods -n <ns>

kubectl get all -n <ns>

**Deployment**
![alt text](attachments/deployaml.jpeg)

**Service**
![alt text](attachments/serviceyaml.jpeg)


**Worker Node**

in EKS un worker node tipicamente corrisponde a una istanza EC2.
- Ogni EC2 registrata al cluster = 1 nodo Kubernetes.
- I nodi stanno in node group (ASG o managed node groups).
- Alternative: con Fargate non gestisci EC2; i Pod girano su infrastruttura gestita e non amministri nodi.

Note utili:
- Un nodo può eseguire più Pod. Il limite dipende da vCPU/RAM e dai limiti Pod-per-nodo dell’istanza.
- Control plane EKS è separato e gestito da AWS, non è nelle tue EC2.

 



 



**Kubectl**




**multi-tenancy**
Condivisione di risorse: Invece che avere un'infrastruttura separata per ogni cliente, diversi tenant utilizzano la stessa istanza software, lo stesso sistema operativo e la stessa infrastruttura hardware sottostante





# ** 🧠 CPU vs Memoria in Kubernetes — spiegato facile **
Tipo risorsa	A cosa serve	Se sbagli cosa succede
CPU	Quante istruzioni può eseguire il container nel tempo → calcolo	Se è troppo poca: il pod viene rallentato (throttling), ma NON crasha
Memoria	Quanta RAM può usare per dati in uso, heap, cache ecc.	Se è troppa poca: il pod va in crash (OOMKilled)

🧠 Trucco per ricordare (con analogia semplice):
Immagina un cuoco (container) che cucina in una cucina (pod):

🔹 CPU = mani del cuoco

Più mani ha → più può lavorare in parallelo. Se ha solo 1 mano → lavora lentamente (throttling), ma non muore.

🔹 Memoria = tavolo da lavoro (RAM)

Se il tavolo è troppo piccolo e non ci sta la roba → il piatto cade per terra → crash (OOMKilled).



CONSUMI RISORSE KUBE

Verifica richieste/limiti dichiarati nei Pod

kubectl get pod -n prov-ippv2-svts-platform-namespace -o=custom-columns='NAME:.metadata.name,CPU_REQUEST:.spec.containers[*].resources.requests.cpu,CPU_LIMIT:.spec.containers[*].resources.limits.cpu,MEM_REQUEST:.spec.containers[*].resources.requests.memory,MEM_LIMIT:.spec.containers[*].resources.limits.memory'



Oppure un esempio più leggibile (usa kubectl describe):

kubectl describe pod <POD_NAME> -n <NAMESPACE>





**🧠 STEP 1: Capire cosa stai guardando**

Questa tabella mostra:

Campo	Cosa significa
NAME	Il nome del pod
CPU_REQUEST	CPU minima garantita dal cluster
CPU_LIMIT	CPU massima che il pod può usare
MEM_REQUEST	RAM minima garantita
MEM_LIMIT	RAM massima prima di essere OOMKilled (crash)

✅ Se il pod consuma meno di request → tutto ok.
⚠️ Se consuma più della request ma meno del limite → rischi throttling o crash in caso di picchi.
🔥 Se consuma più del limite → crash immediato (OOM per RAM, throttling per CPU).



**kubectl top pod -n prov-ippv2-svts-platform-namespace**

🧪 A cosa servono requests e limits?
Campo	        Significato	                                Esempio
requests.cpu	Quanta CPU viene prenotata per il container	Garantisce che il container abbia almeno questa quantità
limits.cpu	    Quanta CPU può usare al massimo	            Se la supera → throttling
requests.memory	Quanta RAM prenotata	                    Il scheduler cerca un nodo con questa RAM
limits.memory	Quanta RAM può usare al massimo	            Se la supera → OOMKilled 💥



Ottima domanda. Fermiamoci a **capire bene come si leggono questi dati**, così la prossima volta potrai **fare le analisi in autonomia**, esattamente come ho fatto per SVTS e CL.

Ti insegno passo per passo **come leggere questi dati** e valutare quando c’è **spreco, rischio o tutto va bene**.

---

## 🧠 STEP 1: Capire cosa stai guardando

Questa tabella mostra:

| Campo         | Cosa significa                                |
| ------------- | --------------------------------------------- |
| `NAME`        | Il nome del pod                               |
| `CPU_REQUEST` | CPU minima garantita dal cluster              |
| `CPU_LIMIT`   | CPU massima che il pod può usare              |
| `MEM_REQUEST` | RAM minima garantita                          |
| `MEM_LIMIT`   | RAM massima prima di essere OOMKilled (crash) |

> ✅ Se il pod **consuma meno di request** → tutto ok.
> ⚠️ Se **consuma più della request ma meno del limite** → rischi throttling o crash in caso di picchi.
> 🔥 Se **consuma più del limite** → crash immediato (OOM per RAM, throttling per CPU).

---

## 🧪 STEP 2: Cerca i valori **anomali o sbilanciati**

Ecco cosa cerchi **a colpo d’occhio**:

### 🟡 Pattern 1: CPU richiesta molto più alta di quanto serve

* Se un pod ha `CPU_REQUEST=400m` ma **consuma 5m**, sta **sprecando risorse prenotate**.

### 🔴 Pattern 2: `MEM_REQUEST` o `MEM_LIMIT` in formato errato

* Come `256M` invece di `256Mi` → Kubernetes potrebbe **non capirlo bene**, comportamento imprevedibile.

### 🔥 Pattern 3: RAM limite altissima senza motivo

* Se `LIMIT=4Gi` ma `USE=500Mi` → stai riservando **RAM che nessuno usa**, ma che nessun altro pod può toccare.

### ⚠️ Pattern 4: MEM uso vicino al limite

* Se `MEM_USE ≈ MEM_LIMIT`, sei **a rischio crash** per picchi minimi.

---

## 👁️ STEP 3: Confronta coppie di valori

Fai questo:

| Cosa guardi                | Cosa significa                                                    |
| -------------------------- | ----------------------------------------------------------------- |
| `CPU_REQUEST vs CPU_LIMIT` | Quanto è elastico il pod? Se troppo vicino, può subire throttling |
| `CPU_REQUEST vs USO`       | Se uso è molto basso → stai prenotando troppa CPU                 |
| `MEM_REQUEST vs MEM_USE`   | Se uso > request → potresti andare in OOM se i nodi sono stretti  |
| `MEM_LIMIT vs MEM_USE`     | Se uso << limite → puoi abbassare limite                          |

---

## 🧰 Esempio pratico: analizziamo una riga

```
prov-ippv2-pr-platform-ippv2-backend-7747c84bc5-2w6sw
CPU_REQUEST=400m
CPU_LIMIT=2
MEM_REQUEST=2Gi
MEM_LIMIT=4Gi
```

**Domande da porti:**

1. ⚙️ **CPU**

   * 400m è 0.4 core garantiti → bene se backend fa lavoro intenso.
   * Limite a 2 core → elastico.
   * **Se uso reale è basso (es. 5m)** → stai **prenotando risorse inutili**.

2. 🧠 **Memoria**

   * 2Gi richiesti → schedulazione solo su nodi con molta RAM.
   * 4Gi limite → se non li usa, stai buttando RAM.
   * Se uso è tipo **200Mi**, hai 10x di spreco.

---

## 📌 STEP 4: Riconosci i contesti

L’ambiente `prod` è diverso da `dev` o `collaudo`:

| Ambiente     | Obiettivo       | Strategia                                 |
| ------------ | --------------- | ----------------------------------------- |
| **dev**      | fare test       | tutto minimo, anche se crasha             |
| **collaudo** | test realistici | risorse ridotte ma coerenti               |
| **prod**     | stabilità       | richieste **accurate**, limiti ben tarati |

Quindi in **PROD**:

* **Requests vanno tarati bene** (non troppo bassi)
* **Limiti vanno bilanciati**: né troppo stretti, né 10x inutili
* I pod non devono essere "overkill", altrimenti saturano il cluster

---

## 🧠 TRUCCHETTO VISIVO

Per ogni riga della tabella, **pensa in questi 3 livelli:**

```
[ MEM USE ] < [ MEM REQUEST ] < [ MEM LIMIT ]
     OK          OK (schedulabile)    OK (non crasha)

Se invece:
[ MEM USE ] > [ MEM REQUEST ] → può andare in OOM se non ha risorse libere nel nodo
[ MEM USE ] ≈ [ MEM LIMIT ] → rischia crash!
```

---

## 🔚 Ricapitolando: Come leggere la tabella

| Cosa cerchi          | Azione                                |
| -------------------- | ------------------------------------- |
| `CPU_REQUEST >> uso` | Abbassa la request                    |
| `MEM_LIMIT >> uso`   | Abbassa il limite                     |
| `MEM_REQUEST < uso`  | Alza la request                       |
| `Formato = 256M`     | Correggi → `256Mi`                    |
| `kestra = 4Gi`       | Da valutare: se uso è < 1Gi, è troppo |

---

✅ Appena mi dai anche `kubectl top pod -n prov-ippv2-pr-platform-namespace`, ti faccio l’analisi completa in stile SVTS e CL, **ma ora potrai anche capirla da solo leggendo i dati come sopra**.

Vuoi procedere?
