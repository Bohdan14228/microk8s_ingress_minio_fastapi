#!/bin/bash

set -e

TAG=$(date +%s)
IMAGE_NAME="localhost:32000/minio-api:$TAG"

echo "Build Docker image with tag: $TAG"
docker build -t $IMAGE_NAME .

echo "Push image"
docker push $IMAGE_NAME

echo "Updating manifest and deploying"
sed -i "s|image: localhost:32000/minio-api:.*|image: $IMAGE_NAME|g" manifests/deployment.yaml

microk8s kubectl apply -f manifests/.

echo "Check status"
microk8s kubectl rollout status deployment/minio-api -n minio-operator
