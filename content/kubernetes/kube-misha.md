
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

# Interacting with PODs

- more info on pods like ip-address, node...
```
kubectl get pods -o wide

kubectl exec -it nginx-tore -- /bin/bash

dentro al pod puoi vedere che OS sta usando:
cat /etc/os-release 

```

- se crei 2 pod uno nginx per esempio e l'altro httpd.
- in httpd entri con exec -it httpd-tore -- /bin/bash 
- puoi installare curl o ping con: sudo apt install iputils-ping
- poi con get pods -o wide vedi ip-address e lo chiami 
- ping 10.42.0.14 oppure curl perché nginx ha qualcosa da mostrare 


# Interacting with PODs

## Viewing detailed pod information
```bash
# Show pods with additional details (IP address, node, status)
kubectl get pods -o wide
```

## Accessing a pod's shell
```bash
# -i = interactive (keeps STDIN open)
# -t = tty (allocates a pseudo-terminal for interactive shell)
kubectl exec -it nginx-pod -- /bin/bash
```

**Why `-it`?**
- `-i` keeps the connection open so you can type commands
- `-t` gives you a proper terminal interface (colors, cursor movement, etc.)
- Together they create an interactive shell session, like SSH

## Checking the OS inside a pod
```bash
cat /etc/os-release
```

## Testing connectivity between pods

### Scenario: Two pods (nginx and httpd)

1. **Enter the httpd pod:**
```bash
kubectl exec -it httpd-pod -- /bin/bash
```

2. **Install network tools (if needed):**
```bash
apt update
apt install curl iputils-ping
```

3. **Get target pod's IP:**
```bash
kubectl get pods -o wide
# Example output: nginx-pod has IP 10.42.0.14
```

4. **Test connectivity:**
```bash
# Test basic network connectivity
ping 10.42.0.14

# Test HTTP service (nginx serves a default welcome page)
curl 10.42.0.14
```

---

## FAQ

### What is httpd?
**httpd** = HTTP Daemon, the Apache web server process name. It's an alternative to nginx - both serve web pages but with different architectures and features.

### Why can we install tools on httpd but not nginx?
This depends on the **base image** used:

- **httpd official image**: Usually based on Debian/Ubuntu → has `apt` package manager
- **nginx official image**: Often uses Alpine Linux → minimal OS with `apk` instead of `apt`, or might be built with a read-only filesystem

**What you can do:**
- httpd pod: `apt install curl`
- nginx pod (if Alpine): `apk add curl`
- Some images have package managers disabled for security

### Why use curl on nginx specifically?
Nginx is configured to serve content (static files, reverse proxy, etc.). By default:
- Nginx serves a welcome page on port 80
- When you `curl <nginx-pod-ip>`, you get an HTTP response (HTML content)
- httpd does the same, but Misha used nginx as the example target

**The key concept:** You're testing that:
1. Network connectivity works (pod-to-pod communication)
2. The web server is running and responding to HTTP requests

---

## Summary

| Command | Purpose |
|---------|---------|
| `kubectl get pods -o wide` | View pod IPs and nodes |
| `kubectl exec -it <pod> -- /bin/bash` | Access pod shell interactively |
| `ping <ip>` | Test network connectivity (Layer 3) |
| `curl <ip>` | Test HTTP service (Layer 7) |

**Best practice for troubleshooting:**
1. Check pod is running: `kubectl get pods`
2. Get pod details: `kubectl get pods -o wide`
3. Check logs: `kubectl logs <pod>`
4. Access shell if needed: `kubectl exec -it <pod> -- /bin/bash`
```