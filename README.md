<div id="top"></div>

## 💻 About the project
This project run prerequisites checks for robusta installation on any k8s cluster
To use it, connect to your cluster and run:
```commandline
kubectl apply -f helm/pre-req-service-account.yaml 
kubectl apply -f helm/pre-req-job.yaml
```

This will create a `namespace` named "robusta-pre-req", will create a `service-account` and a `job`
To view the checks output open the logs of the `pod` with a name prefix of "pre-req-runner" on the "robusta-pre-req" namespace.


To clean everything up run:
```commandline
kubectl delete -f helm/pre-req-service-account.yaml 
```


