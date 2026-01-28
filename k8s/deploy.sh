##!/bin/bash
## Kubernetes deployment script for AI-IMUTIS backend
#
#set -e
#
#NAMESPACE="ai-imutis"
#PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project}"
#IMAGE_TAG="${IMAGE_TAG:-latest}"
#
#echo "========================================"
#echo "AI-IMUTIS Kubernetes Deployment"
#echo "========================================"
#
## Step 1: Create namespace and RBAC
#echo "Step 1: Creating namespace and network policies..."
#kubectl apply -f k8s/namespace.yaml
#sleep 5
#
## Step 2: Create ConfigMaps
#echo "Step 2: Creating ConfigMaps..."
#kubectl apply -f k8s/configmap.yaml
#
## Step 3: Create secrets (must be done manually or via CI/CD secret management)
#echo "Step 3: Checking for secrets..."
#if kubectl get secret api-secrets -n $NAMESPACE 2>/dev/null; then
#    echo "✓ API secrets already exist"
#else
#    echo "⚠ API secrets not found. Please create them using:"
#    echo "  kubectl apply -f k8s/secrets.yaml"
#    echo "  (Update values in secrets.yaml first!)"
#    read -p "Continue anyway? (y/n) " -n 1 -r
#    echo
#    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
#        echo "Aborting deployment"
#        exit 1
#    fi
#fi
#
## Step 4: Deploy PostgreSQL
#echo "Step 4: Deploying PostgreSQL..."
#kubectl apply -f k8s/postgres-statefulset.yaml
#echo "Waiting for PostgreSQL to be ready..."
#kubectl wait --for=condition=ready pod \
#  -l app=postgres \
#  -n $NAMESPACE \
#  --timeout=300s || true
#
## Step 5: Deploy Redis
#echo "Step 5: Deploying Redis..."
#kubectl apply -f k8s/redis-statefulset.yaml
#echo "Waiting for Redis to be ready..."
#kubectl wait --for=condition=ready pod \
#  -l app=redis \
#  -n $NAMESPACE \
#  --timeout=300s || true
#
## Step 6: Update image tag in deployment
#echo "Step 6: Updating API deployment image..."
#sed -i.bak "s|gcr.io/PROJECT_ID/ai-imutis-api:latest|gcr.io/${PROJECT_ID}/ai-imutis-api:${IMAGE_TAG}|g" k8s/api-deployment.yaml
#kubectl apply -f k8s/api-deployment.yaml
#
## Step 7: Deploy HPA
#echo "Step 7: Creating Horizontal Pod Autoscalers..."
#kubectl apply -f k8s/hpa.yaml
#
## Step 8: Deploy Prometheus
#echo "Step 8: Deploying Prometheus..."
#kubectl apply -f k8s/prometheus.yaml
#
## Step 9: Deploy Ingress
#echo "Step 9: Setting up Ingress..."
#sed -i.bak 's|api.example.com|api.'"${DOMAIN:-example.com}"'|g' k8s/ingress.yaml
#kubectl apply -f k8s/ingress.yaml
#
## Step 10: Wait for API deployment
#echo "Step 10: Waiting for API pods to be ready..."
#kubectl wait --for=condition=ready pod \
#  -l app=api \
#  -n $NAMESPACE \
#  --timeout=600s || true
#
## Step 11: Verify deployment
#echo ""
#echo "========================================"
#echo "Deployment Status"
#echo "========================================"
#echo "Namespace: $NAMESPACE"
#echo ""
#
#echo "Pods:"
#kubectl get pods -n $NAMESPACE
#
#echo ""
#echo "Services:"
#kubectl get svc -n $NAMESPACE
#
#echo ""
#echo "HPA:"
#kubectl get hpa -n $NAMESPACE
#
#echo ""
#echo "Ingress:"
#kubectl get ingress -n $NAMESPACE
#
#echo ""
#echo "========================================"
#echo "Next Steps:"
#echo "========================================"
#echo "1. Port-forward to Prometheus:"
#echo "   kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090"
#echo ""
#echo "2. Get Ingress IP:"
#echo "   kubectl get ingress -n $NAMESPACE"
#echo ""
#echo "3. Check logs:"
#echo "   kubectl logs -n $NAMESPACE -l app=api --tail=100 -f"
#echo ""
#echo "4. View metrics:"
#echo "   kubectl exec -n $NAMESPACE -it svc/api -- curl localhost:8000/metrics"
#echo ""
#echo "5. Scale replicas:"
#echo "   kubectl scale deployment api --replicas=5 -n $NAMESPACE"
#echo ""
#echo "========================================"
