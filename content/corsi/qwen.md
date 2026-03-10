Con 16GB RAM e solo CPU (Intel Iris Xe senza VRAM dedicata), la scelta giusta è **Qwen3.5:4b** — non il 9B.

---

## Perché il 4B e non il 9B?

Il 9B pesa **6.6GB** e con solo CPU lascerebbe pochissima RAM libera per il sistema operativo, rendendolo lento e instabile. Per il 4B sono sufficienti 8-16GB di RAM, quindi giri comodo. Pesa circa **3.4GB**, risposte decenti, qualità buona per uso quotidiano.

---

## Installazione completa

```bash
# 1. Installa Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Scarica il modello (~3.4 GB)
ollama pull qwen3.5:4b

# 3. Avvia chat interattiva
ollama run qwen3.5:4b
```

---

## Come si usa — tre modalità

**Modalità 1 — Chat nel terminale (subito dopo `ollama run`)**
```
>>> Spiega cosa fa un Ingress in Kubernetes
>>> /bye   ← per uscire
```

**Modalità 2 — Da un'altra finestra terminale via curl**
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3.5:4b",
  "messages": [{"role": "user", "content": "Cosa fa un Dockerfile multi-stage?"}],
  "stream": false
}'
```

**Modalità 3 — Open WebUI (interfaccia grafica tipo ChatGPT)**
```bash
# Richiede Docker installato
docker run -d -p 3000:80 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```
Poi apri `http://localhost:3000` nel browser.

---

## Tips d'uso

- Aggiungi `/think` al prompt per attivare ragionamento più profondo, `/no_think` per risposte veloci
- Ollama rimane in ascolto su `localhost:11434` — utile per integrarlo con script Python mentre studi
- Se vuoi testare qualcosa di più pesante temporaneamente, prova `qwen3.5:2b` (2.7GB, molto reattivo)

---

**Consiglio pratico per te:** usalo come assistente offline mentre studi Docker/Terraform — puoi incollare YAML e Dockerfile direttamente e chiedergli spiegazioni, senza mandare codice nel cloud.

Vuoi che ti mostro come configurare **Open WebUI** passo passo?

Per Open WebUI su Fedora senza Docker, il metodo più pulito è usare **Podman** (già installato di default su Fedora).Perfetto. Su Fedora il metodo consigliato è usare **Podman** con `--network=host` — è già installato di default e non richiede un daemon root come Docker.

---

## Step 1 — Assicurati che Ollama sia attivo

```bash
ollama serve
```
Lascia questo terminale aperto (o avvialo in background).

---

## Step 2 — Avvia Open WebUI con Podman

Esegui questo comando per deployare Open WebUI via Podman:

```bash
podman run -d \
  --network=host \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://127.0.0.1:11434 \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

La prima volta scarica l'immagine (~1GB), aspetta qualche minuto.

---

## Step 3 — Apri il browser

```
http://localhost:8080
```

Open WebUI ti chiederà di creare un account Admin la prima volta — è solo locale, nessun dato va nel cloud.

---

## Come si usa l'interfaccia

Una volta dentro:

- **Seleziona il modello** — dropdown in alto, scegli `qwen3.5:4b`
- **Nuova chat** — pulsante `+` in alto a sinistra
- **Carica file** — puoi allegare testi, PDF, codice direttamente nella chat
- **System prompt** — nelle impostazioni puoi definire un prompt di sistema fisso (es. "Rispondi sempre in italiano")
- **Cronologia** — tutte le chat vengono salvate localmente

---

## Comandi utili Podman

```bash
podman ps                  # container attivi
podman stop open-webui     # ferma
podman start open-webui    # riavvia
podman logs open-webui     # debug se non si apre
```

---

**Problema frequente:** se il browser mostra "Cannot connect to Ollama" dopo il login, vai in Settings → Admin Settings → Connections e imposta l'URL a `http://host.containers.internal:11434`.

Fammi sapere se ti blocchi su qualche step!