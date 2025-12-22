# microk8s

🏗 Architecture & Tech Stack
  - Orchestration: MicroK8s
  - Storage Backend: MinIO
  - API Framework: FastAPI
  - Containerization: Docker
  - Registry: MicroK8s Built-in Registry (localhost:32000) for local image storage.
  - CI/CD: Custom Bash-based Pipeline 

📋 Project Roadmap  

Stage 1: Infrastructure Setup (MicroK8s)
```bash
sudo apt update && sudo apt install snapd -y         # Install snap package manager
sudo snap install microk8s --classic                 # Install MicroK8s cluster

sudo usermod -a -G microk8s $USER                    # Add current user to microk8s group
sudo chown -f -R $USER ~/.kube                       # Set ownership for kube config
sudo ln -s /snap/bin/microk8s /usr/local/bin/microk8s # Create symlink for global access
echo "alias kubectl='microk8s kubectl'" >> ~/.bashrc  # Set kubectl alias
source ~/.bashrc                                     # Reload bash configuration

microk8s enable hostpath-storage                     # Enable local persistent storage
microk8s enable registry                             # Enable local Docker registry (port 32000)
microk8s enable minio -c 15Gi -s microk8s-hostpath   # Install MinIO operator and tenant
```

Stage 2: MinIO Configuration & Security
```bash
# Install MinIO Client (mc)
wget https://dl.min.io/client/mc/release/linux-amd64/mc # Download client binary
chmod +x mc                                             # Make binary executable
sudo mv mc /usr/local/bin/                              # Move to system path

# Setup settings
kubectl port-forward -n minio-operator svc/minio 32509:80 --address 0.0.0.0
# or
kubectl patch svc minio -n minio-operator --type='json' -p='[{"op": "replace", "path": "/spec/ports/0/nodePort", "value": 32509}]'

# Connect to MinIO as Administrator
source <(kubectl get -n minio-operator secret microk8s-env-configuration -o jsonpath='{.data.config\.env}' | base64 -d)
mc alias set minioadm http://127.0.0.1:32509 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD # Set admin alias

# Create Application User and Policy
mc admin user add minioadm python YOUR_PASSWORD                     # Create user
mc admin policy create minioadm python-policy ./python_bucket.json  # Loadig policy
mc admin policy attach minioadm python-policy --user python         # Attach policy to user
```

Stage 3: Add credentials
```bash
mc admin accesskey create minioadm python  # Create S3 accesskey for user 

kubectl create secret generic minio-creds \
  --namespace=minio-operator \
  --from-literal=access-key='<pass>' \
  --from-literal=secret-key='<pass>'

kubectl get secret minio-creds -n minio-operator -o yaml # Checking secret
```

Stage 4: 
```bash
chmod +x deploy.sh

./deploy.sh  # Start CI
```

