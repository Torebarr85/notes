
+++
title = "Kubernetes: misha CKA - section 4"
date = 2025-12-28
draft = false
tags = ["kubernetes"]
+++
 

# NETWORKING 

PODS:
- each pod has its own IP Address
- every container has a own port on pod
- networking at pod level not container
- by default pods can connect to all pods on all nodes but it's best practice to set network policy / namespaces
- Can communicate each other through localhost -> - you can see pod as VM can have multiple containers, so they will be able to reach other through localhost (localhost=the machine you are on currently)


### how pods can connect to all pods on all nodes? 

because of CNI Plugin = Container Networking Interface. k8S Under the hood use CNI.
![alt text](../attachments/nic.png)
- imagine as the docker container has the physical NIC (network interface card) with a ethernet wire :)  
(use **ifconfig or ipconfig** to display MAC and other networking informations about your PC or VM)

- provides newtork connectivity to containers
- configures network interfaces in containers
- assign IP addresses and sets up routes -> IPTables on nodes

When you set up a CLuster from scratch you have to choose your own CNI plugin:
- CILIUM
- CALICO
- FLANNEL



## RancherDesktop:
RancherDesktop ha una sua CLI 
- "rdctl -h" = help
- rdctl shell bash => entri dentro la VM di rancher-desktop! come nelle macchine linux
- se vuoi vedere quale CNI is running in rancher desktop vai-> cd /etc/cni e vedrai FLANNEL


# SERVICES

## what problem solve? 
it's difficoult tracking all pods. you can have 1000 pods for 1 application right? 
non posso preoccuparmi di quale pod riceverà la request, ma il service riceve e la gira.
quindi punteremo l'app al service e il service will handle it
## why whe need  service?
- pods are ephemeral. because they update and scaling

### il comando per generare service è expose:

```bash
kubectl get service
kubectl expose -h | less

kubectl expose deployment pippo --port 8080
service/pippo exposed

```

- ## ClusterIP
  - the default 
- ## NodePort
  - expose a port on each node allowing direct access to the service through any node's IP address
- ## Load Balancer
  - used for cloud providers. to route traffic into the cluster. (can also use it in k3s/rancher-desktop)