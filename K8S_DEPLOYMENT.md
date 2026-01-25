# Kubernetes Deployment Guide for AI-IMUTIS

## Overview

This guide covers deploying the AI-IMUTIS backend to a Kubernetes cluster using both direct manifests and Helm charts.

## Prerequisites

- Kubernetes 1.26+ cluster
- `kubectl` configured to access your cluster
- `helm` 3.12+
- Docker registry access (GCR, Docker Hub, etc.)
- PostgreSQL storage support (StorageClass configured)
- Ingress controller installed (nginx-ingress recommended)
- cert-manager for TLS/SSL (optional but recommended)

### Recommended Storage Classes

```bash
kubectl create storageclass fast-ssd --provisioner=ebs.csi.aws.com --parameters=volumeType=gp3,iops=3000,throughput=125
kubectl create storageclass standard --provisioner=ebs.csi.aws.com --parameters=volumeType=gp2
```

## Quick Start with Manifests

### 1. Create Namespace and Network Policies

```bash
kubectl apply -f k8s/namespace.yaml
```

This creates:
- `ai-imutis` namespace with resource quotas
- Default deny network policies
- API-specific network policies

### 2. Set Up Secrets

Create secrets for sensitive data:

```bash
# PostgreSQL credentials
kubectl create secret generic postgres-secret \
  --from-literal=username=app_user \
  --from-literal=password=<secure-password> \
  --from-literal=postgres-password=<secure-postgres-password> \
  -n ai-imutis

# API configuration secrets
kubectl create secret generic api-secrets \
  --from-literal=database-url="postgresql+asyncpg://app_user:<password>@postgres-0.postgres-headless:5432/ai_imutis" \
  --from-literal=redis-url="redis://redis-0.redis-headless:6379/0" \
  --from-literal=firebase-project-id=<firebase-project-id> \
  --from-file=firebase-service-account=path/to/serviceAccountKey.json \
  --from-literal=sentry-dsn=<sentry-dsn> \
  -n ai-imutis

# Docker registry (if using private registry)
kubectl create secret docker-registry docker-registry \
  --docker-server=gcr.io \
  --docker-username=_json_key \
  --docker-password="$(cat key.json)" \
  -n ai-imutis
```

### 3. Deploy ConfigMaps

```bash
kubectl apply -f k8s/configmap.yaml
```

### 4. Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres-statefulset.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n ai-imutis --timeout=300s
```

### 5. Deploy Redis

```bash
kubectl apply -f k8s/redis-statefulset.yaml

# Wait for Redis to be ready
kubectl wait --for=condition=ready pod -l app=redis -n ai-imutis --timeout=300s
```

### 6. Deploy API Service

```bash
# Update image tag in api-deployment.yaml if needed
sed -i 's|gcr.io/PROJECT_ID/ai-imutis-api:latest|gcr.io/YOUR-PROJECT/ai-imutis-api:YOUR-TAG|g' k8s/api-deployment.yaml

kubectl apply -f k8s/api-deployment.yaml

# Wait for API pods to be ready
kubectl wait --for=condition=ready pod -l app=api -n ai-imutis --timeout=600s
```

### 7. Deploy Monitoring (Optional)

```bash
kubectl apply -f k8s/prometheus.yaml
```

### 8. Deploy Ingress and SSL

```bash
# Update domain in ingress.yaml
sed -i 's|api.example.com|api.your-domain.com|g' k8s/ingress.yaml

kubectl apply -f k8s/ingress.yaml
```

### 9. Set Up Auto-scaling

```bash
kubectl apply -f k8s/hpa.yaml
```

## Deployment with Helm

Helm provides a templated, reusable approach to deployment.

### 1. Install Helm Chart

```bash
# Development environment
helm install ai-imutis ./helm/ai-imutis \
  --namespace ai-imutis \
  --create-namespace \
  --set postgres.auth.password=<password> \
  --set api.secrets.databaseUrl="postgresql+asyncpg://..." \
  --set api.secrets.redisUrl="redis://..." \
  --set api.secrets.firebaseProjectId=<id> \
  --set api.secrets.sentryDsn=<dsn>

# Production environment
helm install ai-imutis ./helm/ai-imutis \
  --namespace ai-imutis \
  --values helm/ai-imutis/values-prod.yaml \
  --set global.domain=api.imutis.io \
  --set api.secrets.databaseUrl="postgresql+asyncpg://..." \
  --set api.secrets.redisUrl="redis://..." \
  --set api.secrets.firebaseProjectId=<id> \
  --set api.secrets.sentryDsn=<dsn>
```

### 2. Upgrade Deployment

```bash
helm upgrade ai-imutis ./helm/ai-imutis \
  --namespace ai-imutis \
  --values helm/ai-imutis/values-prod.yaml \
  --set api.image.tag=<new-version>
```

### 3. Rollback on Issues

```bash
helm rollback ai-imutis <revision>
```

### 4. Check Chart Values

```bash
helm get values ai-imutis -n ai-imutis
```

## Management Tasks

### Scale Replicas

```bash
# Manual scaling
kubectl scale deployment api --replicas=5 -n ai-imutis

# View HPA status
kubectl get hpa -n ai-imutis
kubectl describe hpa api-hpa -n ai-imutis
```

### Run Database Migrations

```bash
# Migrations run automatically via init container on deployment
# Manual migration if needed:
kubectl exec -it postgres-0 -n ai-imutis -- \
  psql -U app_user -d ai_imutis \
  -c "SELECT * FROM alembic_version;"
```

### Access PostgreSQL

```bash
# Port forward
kubectl port-forward -n ai-imutis svc/postgres 5432:5432

# Connect from local machine
psql postgresql://app_user:password@localhost:5432/ai_imutis
```

### Monitor Redis

```bash
# Port forward
kubectl port-forward -n ai-imutis svc/redis 6379:6379

# Connect
redis-cli -h localhost -p 6379
```

### View Application Logs

```bash
# Real-time logs
kubectl logs -n ai-imutis -l app=api --tail=100 -f

# Logs from specific pod
kubectl logs -n ai-imutis pod/api-0

# Previous container logs (if crashed)
kubectl logs -n ai-imutis pod/api-0 --previous
```

### Prometheus & Metrics

```bash
# Port forward to Prometheus
kubectl port-forward -n ai-imutis svc/prometheus 9090:9090

# Access at http://localhost:9090

# View API metrics directly
kubectl exec -n ai-imutis pod/api-0 -- curl localhost:8000/metrics
```

### Execute Commands in Pods

```bash
# Interactive shell
kubectl exec -it -n ai-imutis pod/api-0 -- /bin/bash

# Run single command
kubectl exec -n ai-imutis pod/api-0 -- python -c "from app.seed import seed_data; import asyncio; asyncio.run(seed_data())"
```

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod api-0 -n ai-imutis

# Check events
kubectl get events -n ai-imutis --sort-by='.lastTimestamp'

# Check init container logs
kubectl logs api-0 -n ai-imutis -c migrations
```

### Database connection failures

```bash
# Check PostgreSQL is running
kubectl get pods -l app=postgres -n ai-imutis
kubectl logs -l app=postgres -n ai-imutis --tail=50

# Test connection from API pod
kubectl exec -it api-0 -n ai-imutis -- \
  psql $DATABASE_URL -c "SELECT 1"
```

### High CPU/Memory usage

```bash
# Check resource usage
kubectl top pods -n ai-imutis
kubectl top nodes

# Check HPA status
kubectl describe hpa api-hpa -n ai-imutis

# View recent scaling events
kubectl get events -n ai-imutis --field-selector involvedObject.kind=HorizontalPodAutoscaler
```

### Persistence issues

```bash
# Check PVCs
kubectl get pvc -n ai-imutis

# Check storage class
kubectl get storageclass

# Describe PVC for issues
kubectl describe pvc postgres-storage-postgres-0 -n ai-imutis
```

## Backup and Disaster Recovery

### Backup PostgreSQL

```bash
# Create backup
kubectl exec -n ai-imutis postgres-0 -- \
  pg_dump -U app_user ai_imutis > backup.sql

# Compress
gzip backup.sql
```

### Restore from Backup

```bash
# Copy backup to pod
kubectl cp backup.sql ai-imutis/postgres-0:/tmp/

# Restore
kubectl exec -n ai-imutis postgres-0 -- \
  psql -U app_user ai_imutis < /tmp/backup.sql
```

### Backup Persistent Volumes

For production, use your cloud provider's backup solutions:

**AWS:**
```bash
aws ec2 create-snapshot --volume-id <volume-id> --description "AI-IMUTIS backup"
```

**GCP:**
```bash
gcloud compute disks snapshot <disk-name> --snapshot-names=<snapshot-name>
```

**Azure:**
```bash
az snapshot create --resource-group <group> --name <snapshot-name> --source <disk-id>
```

## Security Considerations

### Network Policies

- Default deny ingress/egress is configured
- API pods can receive traffic from ingress controller
- Database and Redis traffic restricted to internal pods only

### Pod Security

- Non-root user (UID 1000)
- Read-only filesystem where possible
- Dropped capabilities (NET_BIND_SERVICE, etc.)
- Security context constraints applied

### Secrets Management

For production:
1. Use AWS Secrets Manager, GCP Secret Manager, or Azure Key Vault
2. Integrate with cert-manager for automatic certificate rotation
3. Use sealed-secrets or Vault for encrypted secrets in Git

```bash
# Install sealed-secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Create sealed secret
echo -n mypassword | kubectl create secret generic mysecret --dry-run=client --from-file=/dev/stdin -o yaml | kubeseal > mysealedsecret.yaml
```

## Performance Tuning

### Database Connection Pool

Adjust in `k8s/configmap.yaml`:
```yaml
DB_POOL_SIZE: "30"  # Increase for more connections
DB_MAX_OVERFLOW: "20"  # Allow temporary overflow
```

### Redis Optimization

```yaml
maxmemory: 2gb  # In redis-statefulset.yaml
maxmemory-policy: allkeys-lru  # Eviction policy
```

### API Tuning

```yaml
api:
  resources:
    requests:
      cpu: "500m"  # Increase minimum CPU
    limits:
      cpu: "2000m"  # Increase maximum CPU
```

## CI/CD Integration

### GitHub Actions Example

See `.github/workflows/ci.yml` for:
1. Python linting and syntax check
2. Docker image build and push to GCR
3. Kubernetes manifest validation
4. Automatic deployment to GKE on main branch push
5. Load testing on tagged releases

Set these GitHub secrets:
- `GCP_PROJECT_ID`: Your GCP project
- `GKE_CLUSTER_NAME`: Your GKE cluster name
- `GKE_REGION`: GKE cluster region
- `WIF_PROVIDER`: Workload Identity Federation provider
- `WIF_SERVICE_ACCOUNT`: Service account for CI/CD

## Cleanup

### Remove Deployment

```bash
# Remove Helm release
helm uninstall ai-imutis -n ai-imutis

# Or remove manifests
kubectl delete -f k8s/
```

### Delete Namespace

```bash
# This will delete all resources in the namespace
kubectl delete namespace ai-imutis
```

### Delete Persistent Volumes

```bash
# List PVs
kubectl get pv -n ai-imutis

# Delete specific PV
kubectl delete pv <pv-name>
```

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs)
- [Helm Documentation](https://helm.sh/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment)
- [PostgreSQL on Kubernetes](https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
