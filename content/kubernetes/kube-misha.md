
+++
title = "Kubernetes: misha CKA"
date = 2025-12-24
draft = false
tags = ["kubernetes"]
+++

### let's start
install rancher-desktop
it creates a VM on your local device and it deploys both a kubernetes cluster
and also a container environment (like docker-desktop)
infact if you launch "docker run -it ubuntu" it will start a container like docker-desktop do.

# POD - introduction

```
kubectl config current-context
kubectl config use-context rancher-desktop
cd .kube
cat config


kubectl -h | less

kubectl run nginx-tore-pod --image=nginx
kubectl get pods -o wide
```


- is the smallest element on a k8s cluster
- pod of whales 
- pod is not a container!
- pod is a collection of container + other resources
- pod contains: networking and storage
- init container
- single or multi container


### what happen when you run kubectl get pods?

parli con l'api server inside the control plane
api server dice allo scheduler di schedulare il pod


# POD as Code - YAML
evertything is a yaml obejct (technically a json object)

### how too see the yaml definition of a pod manifest:
```
kubectl get pod <nomepod> -o yaml | less

```
### How create a pod from yaml:
con dry-run=client genera solo lo yaml minimo senza far nessuna azione.
con dry-run=server genera yaml + apply to a k8s cluster e poi verrà delete afterwards = ottimo per test 

```
kubectl run nginx-tore-yaml-ex --image=nginx --dry-run=client -o yaml
```

- PS se vuoi fare redirect direttamente su un file fai: > nomefile.yaml)cosi puoi fare vim nginx.yaml ed editarlo ed hai già indentazione fatta bene:
  
```
kubectl run nginx-tore-yaml-ex --image=nginx --dry-run=client -o yaml > nginx.yaml 

kubectl apply -f nginx.yaml
```


### come incollare correttamente uno yaml preso da docs su internet di k8s su terminale senza sputtanare l'indentazione?

- apri vim
- insert mode
- :set paste
