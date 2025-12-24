
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
