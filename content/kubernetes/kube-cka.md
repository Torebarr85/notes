+++
title = "CKA - design a k8s cluster"
date = 2026-01-13
draft = false
tags = ["kubernetes","cka"]
+++


# kube apiserver
  
- is a pod running on kube-system


```bash
kubectl get pods -n kube-system

# where find yaml
cat /etc/kubernetes/manifest/kube-apiserver.yaml

ps -aux | grep kube-apiserver

```