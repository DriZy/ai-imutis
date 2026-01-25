#!/bin/bash
# AI-IMUTIS Quick Reference - Common kubectl commands

# ============================================================
# POD MANAGEMENT
# ============================================================

# List all pods
kubectl get pods -n ai-imutis

# Get pod details
kubectl describe pod api-0 -n ai-imutis

# View pod logs
kubectl logs api-0 -n ai-imutis
kubectl logs api-0 -n ai-imutis -c migrations  # Specific container
kubectl logs -l app=api -n ai-imutis -f  # All API pods, follow

# Execute command in pod
kubectl exec -it api-0 -n ai-imutis -- /bin/bash
kubectl exec api-0 -n ai-imutis -- python -c "print('Hello')"

# Port forward
kubectl port-forward -n ai-imutis svc/api 8000:80

# ============================================================
# DEPLOYMENT MANAGEMENT
# ============================================================

# Check deployment status
kubectl get deployments -n ai-imutis
kubectl describe deployment api -n ai-imutis

# Scale replicas
kubectl scale deployment api --replicas=5 -n ai-imutis

# Update image
kubectl set image deployment/api api=gcr.io/project/api:v1.0 -n ai-imutis

# Rollout status
kubectl rollout status deployment/api -n ai-imutis

# Rollout history
kubectl rollout history deployment/api -n ai-imutis

# Rollback to previous version
kubectl rollout undo deployment/api -n ai-imutis
kubectl rollout undo deployment/api --to-revision=3 -n ai-imutis

# ============================================================
# STATEFULSET MANAGEMENT (DATABASE/CACHE)
# ============================================================

# Get StatefulSets
kubectl get statefulsets -n ai-imutis

# Scale database
kubectl scale statefulset postgres --replicas=3 -n ai-imutis

# Delete pod (StatefulSet auto-recreates)
kubectl delete pod postgres-0 -n ai-imutis

# ============================================================
# SERVICE & NETWORKING
# ============================================================

# List services
kubectl get svc -n ai-imutis

# Get service details
kubectl describe svc api -n ai-imutis

# Get Ingress
kubectl get ingress -n ai-imutis
kubectl describe ingress api-ingress -n ai-imutis

# Get external IP
kubectl get svc -n ai-imutis -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}'

# ============================================================
# RESOURCE MANAGEMENT
# ============================================================

# View resource usage
kubectl top pods -n ai-imutis
kubectl top nodes

# Check resource requests/limits
kubectl describe node node-1

# View HPA status
kubectl get hpa -n ai-imutis
kubectl describe hpa api-hpa -n ai-imutis
kubectl get hpa -n ai-imutis -w  # Watch

# ============================================================
# CONFIGURATION & SECRETS
# ============================================================

# List ConfigMaps
kubectl get configmaps -n ai-imutis

# View ConfigMap data
kubectl get configmap api-config -n ai-imutis -o yaml

# Edit ConfigMap
kubectl edit configmap api-config -n ai-imutis

# List Secrets
kubectl get secrets -n ai-imutis

# Update Secret
kubectl create secret generic api-secrets \
  --from-literal=key=value \
  --dry-run=client -o yaml | kubectl apply -f -

# ============================================================
# STORAGE & PERSISTENCE
# ============================================================

# List PersistentVolumeClaims
kubectl get pvc -n ai-imutis

# Check PVC status
kubectl describe pvc postgres-storage-postgres-0 -n ai-imutis

# List PersistentVolumes
kubectl get pv

# List StorageClasses
kubectl get storageclass

# ============================================================
# EVENTS & MONITORING
# ============================================================

# Get cluster events
kubectl get events -n ai-imutis
kubectl get events -n ai-imutis --sort-by='.lastTimestamp'

# View resource quotas
kubectl describe resourcequota -n ai-imutis

# Check network policies
kubectl get networkpolicies -n ai-imutis

# ============================================================
# DATABASE OPERATIONS
# ============================================================

# Connect to PostgreSQL
kubectl port-forward -n ai-imutis svc/postgres 5432:5432
# In another terminal:
psql postgresql://app_user:password@localhost:5432/ai_imutis

# Run migration
kubectl exec -it postgres-0 -n ai-imutis -- \
  psql -U app_user -d ai_imutis -c "SELECT version();"

# Backup database
kubectl exec postgres-0 -n ai-imutis -- \
  pg_dump -U app_user ai_imutis > backup.sql

# Restore database
kubectl cp backup.sql ai-imutis/postgres-0:/tmp/
kubectl exec postgres-0 -n ai-imutis -- \
  psql -U app_user ai_imutis < /tmp/backup.sql

# ============================================================
# REDIS OPERATIONS
# ============================================================

# Connect to Redis
kubectl port-forward -n ai-imutis svc/redis 6379:6379
# In another terminal:
redis-cli -h localhost -p 6379

# Monitor Redis commands
kubectl exec -it redis-0 -n ai-imutis -- \
  redis-cli MONITOR

# Get Redis info
kubectl exec redis-0 -n ai-imutis -- \
  redis-cli INFO server

# ============================================================
# APPLICATION HEALTH
# ============================================================

# Check API health
kubectl exec api-0 -n ai-imutis -- \
  curl -s localhost:8000/health | jq

# Check metrics endpoint
kubectl exec api-0 -n ai-imutis -- \
  curl -s localhost:8000/metrics | head -50

# Run API in debug mode
kubectl exec -it api-0 -n ai-imutis -- \
  python -c "import app.main; print(app.main.__file__)"

# ============================================================
# HELM OPERATIONS
# ============================================================

# Install Helm chart
helm install ai-imutis ./helm/ai-imutis \
  --namespace ai-imutis \
  --create-namespace \
  --values helm/ai-imutis/values-prod.yaml

# Upgrade Helm release
helm upgrade ai-imutis ./helm/ai-imutis \
  --namespace ai-imutis \
  --values helm/ai-imutis/values-prod.yaml

# Get Helm values
helm get values ai-imutis -n ai-imutis

# Check Helm release status
helm status ai-imutis -n ai-imutis
helm history ai-imutis -n ai-imutis

# Rollback Helm release
helm rollback ai-imutis <revision> -n ai-imutis

# Dry-run before deploy
helm install ai-imutis ./helm/ai-imutis \
  --namespace ai-imutis \
  --dry-run --debug

# ============================================================
# DEBUGGING & TROUBLESHOOTING
# ============================================================

# Get detailed pod events
kubectl describe pod api-0 -n ai-imutis | grep Events -A 10

# Get pod YAML
kubectl get pod api-0 -n ai-imutis -o yaml

# Check init container logs
kubectl logs api-0 -n ai-imutis -c migrations --previous

# Port forward and test
kubectl port-forward -n ai-imutis svc/api 8000:80
curl http://localhost:8000/health

# Check pod scheduling
kubectl get pods -n ai-imutis -o wide

# Inspect resource requests
kubectl describe pod api-0 -n ai-imutis | grep -A 5 "Requests"

# ============================================================
# COMMON PATTERNS
# ============================================================

# Watch deployment
watch kubectl get deployment -n ai-imutis

# Get all resources in namespace
kubectl get all -n ai-imutis

# Apply all manifests
kubectl apply -f k8s/ -n ai-imutis

# Delete all resources
kubectl delete -f k8s/ -n ai-imutis

# Tail logs from multiple pods
kubectl logs -l app=api -n ai-imutis -f --max-log-requests=10

# JSON output for scripting
kubectl get pods -n ai-imutis -o json

# Filter by label
kubectl get pods -n ai-imutis -l app=api
kubectl get pods -n ai-imutis --selector=app=api,version=v1

# ============================================================
# USEFUL ALIASES (Add to ~/.bashrc)
# ============================================================

# alias k=kubectl
# alias kg='kubectl get'
# alias kd='kubectl describe'
# alias kl='kubectl logs'
# alias kex='kubectl exec -it'
# alias kaf='kubectl apply -f'
# alias kdel='kubectl delete'
# alias kgpo='kubectl get pods'
# alias kgsvc='kubectl get svc'
# alias kgdep='kubectl get deployment'
# alias kgst='kubectl get statefulset'
# alias kgpvc='kubectl get pvc'

# ============================================================
# ADVANCED OPERATIONS
# ============================================================

# List API resources
kubectl api-resources

# Validate YAML before apply
kubectl apply -f k8s/api-deployment.yaml --dry-run=client

# Get API group versions
kubectl api-versions

# Explain resource fields
kubectl explain deployment.spec

# Interactive debugging pod
kubectl debug pod/api-0 -it -n ai-imutis

# Get pod shell (create ephemeral container)
kubectl debug pod/api-0 -it --image=busybox -n ai-imutis
