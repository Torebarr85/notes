
+++
title = "Kubernetes: misha CKA - section 3"
date = 2025-12-25
draft = false
tags = ["kubernetes"]
+++
 

# DEPLOYMENTS 


```
kubectl create deployment -h | less

kubectl create deploy test --image=httpd --replicas=3

kubectl get deployments.apps

NAME   READY   UP-TO-DATE   AVAILABLE   AGE
test   3/3     3            3           52s

kubectl describe deployments.apps <nomeDeployment>

kubectl delete deployments.apps <nomeDeployment>
and all the 3 pods will vanish immediately! 
```


ovviamente tutto sarà automatizzato non dobbiamo fare a mano
coome possiamo fare in code questo?

### creaimo yaml senza applicarlo quindi usando dry run client e -o yaml per visualizzarlo

```
~> kubectl create deploy test2 --image=httpd --replicas=10 --dry-run=client -o yaml > deploytest.yaml


~> cat deploytest.yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: test2
  name: test2
spec:
  replicas: 10
  selector:
    matchLabels:
      app: test2
  template:
    metadata:
      labels:
        app: test2
    spec:
      containers:
      - image: httpd
        name: httpd
status: {}

~> kubectl apply -f deploytest.yaml 
deployment.apps/test2 created

~> kubectl get pods -o wide
NAME                     READY   STATUS    RESTARTS   AGE    IP           NODE                   NOMINATED NODE   READINESS GATES
httpd-tore               1/1     Running   1          22h    10.42.0.20   lima-rancher-desktop   <none>           <none>
nginx-tore               1/1     Running   3          2d3h   10.42.0.21   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-5hq28   1/1     Running   0          12s    10.42.0.34   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-652bw   1/1     Running   0          12s    10.42.0.36   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-jvnnr   1/1     Running   0          12s    10.42.0.35   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-njngl   1/1     Running   0          13s    10.42.0.29   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-phsps   1/1     Running   0          12s    10.42.0.37   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-t7985   1/1     Running   0          12s    10.42.0.33   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-tkg7g   1/1     Running   0          12s    10.42.0.30   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-tlp6m   1/1     Running   0          12s    10.42.0.31   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-twcw5   1/1     Running   0          13s    10.42.0.28   lima-rancher-desktop   <none>           <none>
test2-858c9c4dbf-w66pr   1/1     Running   0          12s    10.42.0.32   lima-rancher-desktop   <none>           <none>


~> kubectl get deployments.apps
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
test2   10/10   10           10          48s

```
- sotto il cofano il deployments non serve a creare i pods realmente ma a creare/controllare i replicaset object.
infatti se facciamo get replicaset vedremo che nel cluster ora c'è un replicaset creato:

```
~> kubectl get replicasets.apps 
NAME               DESIRED   CURRENT   READY   AGE
test2-858c9c4dbf   10        10        10      2m54s
```
- NB K8s manage replicaset for you. don't touch replicaset object.
- K8s di default keep until last 10 old replicaset around 
### Strategy 
- .spec.strategy specifies the strategy used to replace old Pods by new ones. .spec.strategy.type can be "Recreate" or "RollingUpdate". "RollingUpdate" is the default value. RollingUpdate = quando kill un pod viene fatto one by one non tutti assieme


```
questo comando "watch -n 1" è come se lanciassi ogni 1sec il comando dopo quindi get pods:
watch -n 1 kubectl get pods

```
se un pod va in errore k8s capisce che non deve fare rolling anche degli altri.


# Deployments - Namespaces
 
# Deployments - Our First Application