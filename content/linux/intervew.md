
# Domanda 1 (Linux – servizi)

1) “How do you check if a service is running on a Linux system?”
- systemctl status <service>

# Domanda 2 (processi)

2) “A server is slow. What’s the first thing you check?”

- ps è utile ma statico → non ti mostra il consumo in tempo reale.
- In produzione la prima cosa è vedere chi sta mangiando CPU/RAM.
- Lo strumento standard è top (o htop se installato).

# Domanda 3 (servizi + log)

3) “A service is failing to start. What do you do to understand the cause?”
- I check systemctl status to see the error 
- and then journalctl -u <service> -f to read the logs.

# Domanda 4 (network troubleshooting)
4) How do you verify if a machine can reach an external host?

🧠 Cos’è “la macchina”?

È il server dove sei collegato via SSH.
Esempio: ti colleghi a ssh dev@10.0.0.12 → quella è la macchina.

🧠 Cos’è “l’host esterno”?

È qualcosa fuori da quella macchina che vuoi raggiungere:

un dominio (google.com)

un altro server (10.0.0.20)

un’API (api.mycompany.com)

🧠 Quale comando usare?

Dipende da cosa devi verificare:

✔️ Raggiungibilità di base (livello IP)

ping
Verifica se l’host risponde → rete ok.

✔️ Raggiungibilità HTTP (livello applicazione)

curl http://host:porta
Verifica se l’applicazione risponde → servizio ok.

Quindi in un colloquio DevOps la risposta giusta è:

💬 Risposta completa perfetta:

- “I usually check reachability with ping, and if it’s a web service I use curl -v to test the endpoint.”

# Domanda 5 (file system + log)

5) “A disk is getting full. What commands do you use to find what’s consuming space?”

Per capire cosa riempie un disco non guardi i processi → guardi le directory.

I due comandi chiave sono:

- df -h → spazio totale usato/ disponibile
- du -sh * → quanto spazio consumano le directory

# Domanda 6 (permessi)

6) “How do you make a script executable on Linux?”

- chmod +x <nomeFileScript>

# Domanda 7 (DNS + troubleshooting)

7) “How do you check if a DNS resolution is working correctly?”
- I check DNS resolution with:  dig nomeDomain.com.”

# Domanda 8 (processi)

8) “How do you find which process is using port 8080?”
- Quando vuoi sapere chi sta usando una porta, hai due strumenti:

✔️ 1) lsof → il più chiaro

- sudo lsof -i :8080

✔️ 2) ss → più moderno, già installato ovunque

- ss -tulnp | grep 8080

# Domanda 9 (file search)

9) “How do you search for a file named config.yaml in the entire filesystem?”

- find / -name "config.yaml"

# Domanda 10 (log)

10) “How do you follow a log file in real time?”

“I use tail -f <logfile> to follow logs in real time.”

Se vuoi essere top:

“For systemd services I also use journalctl -u <service> -f.”

# Domanda 13 (SSH)

13) “How do you copy a file from your local machine to a remote server?”
Hai usato cp, ma quello funziona solo in locale, NON tra due macchine diverse.
Il recruiter lo nota subito.

La copia locale → remoto richiede SSH, quindi scp o rsync.

🔍 Spiegazione semplice

Per copiare file su un server remoto:

✔️ Comando corretto
scp localfile user@server:/path/


scp = secure copy (usa SSH)

richiede user, host e path remoto

💬 Risposta corretta e da colloquio

“I use scp localfile user@server:/path to transfer files to a remote machine.”


# Domanda 15 (tar / archivi)

15) “How do you extract a .tar.gz file in Linux?”

- tar -xvzf archivio.tar.gz

# Domanda 16 (systemd – restart)

16) “How do you restart a systemd service?”

- sudo systemctl restart <service>


# Domanda 17 (system logs)

17) “How do you view recent system errors?”

- journalctl -xe

# Domanda 18 (rete – routing)

18) “How do you check the routing table on a Linux machine?”

-“ip route gives me all the active routes and the default gateway.”

# Domanda 19 (grep)

19) “How do you search for a keyword inside all files in a directory?”

- grep -R "keyword" /path

-R = ricorsivo → entra nelle cartelle

cerca nel contenuto dei file, non nei nomi

