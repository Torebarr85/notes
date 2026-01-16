+++
title = "VIM"
date = 2025-12-28
draft = false
tags = ["linux"]
+++


# VIM

#### sostituisco una parola globalmente in tutto il file
```yaml
:%s/parola-da-sostituire/parola-nuova/g 
```
Spiegazione:

: - entra in command mode
% - applica su tutto il file (tutte le righe)
s - substitute (sostituisci)
/vecchia-parola/ - cosa cercare
/nuova-parola/ - con cosa sostituire
g - global (tutte le occorrenze nella riga, non solo la prima)



#### incolla correttamente yaml:
```yaml
:set paste 

```

#### come fare replace di un value senza usare i di insert 
```
r + valore col quale vuoi fare replace


```



### may you got a secret from k8s and you have to decode from base64 to real password
```bash
kubectl get secret argocd-initial-admin-secret -n argocd -o yaml


echo T325dshsGDS8340DSBdjds== | base64 --decode

```