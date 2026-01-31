+++
title = "Linux: troubleshooting server"
date = 2026-01-31
draft = false
tags = ["linux"]
+++



# Dentro un pod puoi fare:
```bash
kubectl exec -it my-pod -- bash
ps aux              # vedi processi
netstat -tulpn      # vedi porte aperte
curl localhost:80   # testi connettività
```