
# Recommendations Application Deployment Guide

This guide provides step-by-step instructions for building and deploying the `recommendations` application in a local Kubernetes cluster. We’ll use `make cluster` to create a cluster, build the Docker image, push it to a local registry, and finally deploy it in Kubernetes.

## Steps

### 1. Create a Local Kubernetes Cluster

Run the following command to create a Kubernetes cluster:

```bash
make cluster
```

Then, verify the cluster has started:

```bash
kubectl cluster-info
```

This command should display cluster information if the cluster was created successfully.

### 2. Build the Docker Image

Build the Docker image for the `recommendations` application using `.prodcontainer/Dockerfile`. Tag the image as `recommendations:1.0`:

```bash
docker build -t recommendations:1.0 -f .prodcontainer/Dockerfile .
```

### 3. Configure Local Registry

#### Check `/etc/hosts`

To ensure that images can be pushed to a local registry, check if `cluster-registry` is configured in `/etc/hosts`:

```bash
cat /etc/hosts
```

If there is no entry for `cluster-registry`, add it by running:

```bash
sudo bash -c "echo '127.0.0.1    cluster-registry' >> /etc/hosts"
```

### 4. Tag and Push the Image

Tag `recommendations:1.0` as `cluster-registry:5000/recommendations:1.0` and push it to the local registry:

Tag:

```bash
docker tag recommendations:1.0 cluster-registry:5000/recommendations:1.0
```

Push:

```bash
docker push cluster-registry:5000/recommendations:1.0
```

### 5. Create a Kubernetes Namespace

Create a `lab` namespace in Kubernetes to organize application resources:

```bash
kubectl create ns lab
```

Confirm the namespace was created successfully:

```bash
kubectl get ns
```

Switch to the `lab` namespace:

```bash
kubectl config set-context --current --namespace=lab
```

or

```bash
kns lab
```

### 6. Deploy the Application to Kubernetes

Apply the Kubernetes manifests in the `k8s` folder to deploy the `recommendations` application:

```bash
kubectl apply -f k8s/ --recursive
```

To check the status of all resources in the `default` namespace and confirm the Pods are running:

```bash
kubectl get all -n default
```

### 7. Test the Application

To verify that the application is running, check the status of the Pods:

```bash
kubectl get pods
```

To view logs from the application continuously, use the following command:

```bash
kubectl logs -f <pod-name>
```

Replace `<pod-name>` with the actual name of your Pod.

### 8. Remove the Application

To remove all resources associated with the application, run:

```bash
kubectl delete -f k8s/ --recursive
```

---
