# AI-IMUTIS Backend: Kubernetes & Deployment Documentation Index

## 📋 Documentation Files

### 🚀 Getting Started
1. **[K8S_SUMMARY.md](K8S_SUMMARY.md)** - Start here! Overview of Kubernetes implementation
   - What's new in the K8s setup
   - Quick start checklist
   - Architecture diagram
   - Key features implemented

### 📖 Comprehensive Guides

2. **[K8S_DEPLOYMENT.md](K8S_DEPLOYMENT.md)** - Complete deployment guide (520 lines)
   - Prerequisites and cluster setup
   - Step-by-step deployment with manifests
   - Helm chart deployment
   - Management tasks (scaling, backups, migrations)
   - Troubleshooting procedures
   - Security best practices

3. **[MONITORING.md](MONITORING.md)** - Observability & monitoring guide (580 lines)
   - Prometheus metrics collection and queries
   - Structured JSON logging
   - Distributed tracing (Jaeger/OpenTelemetry)
   - Alert configuration
   - Grafana dashboards
   - Sentry error tracking
   - Performance monitoring

4. **[K8S_QUICK_REFERENCE.sh](K8S_QUICK_REFERENCE.sh)** - Quick reference (220 lines)
   - Common kubectl commands
   - Database operations
   - Debugging techniques
   - Helm operations
   - Useful aliases

5. **[K8S_INFRASTRUCTURE.md](K8S_INFRASTRUCTURE.md)** - Infrastructure details
   - Complete file listing
   - File statistics and line counts
   - Technologies used
   - Deployment steps
   - File locations and organization

## 📁 Kubernetes Manifests (`/k8s/`)

### Core Infrastructure
| File | Size | Purpose |
|------|------|---------|
| **namespace.yaml** | 88 | Namespace, quotas, network policies |
| **configmap.yaml** | 137 | App config, DB init, nginx setup |
| **secrets.yaml** | 48 | Secret templates (fill in your values) |

### Data Services
| File | Size | Purpose |
|------|------|---------|
| **postgres-statefulset.yaml** | 177 | PostgreSQL 16 with PostGIS |
| **redis-statefulset.yaml** | 155 | Redis 7 cache with persistence |

### Application
| File | Size | Purpose |
|------|------|---------|
| **api-deployment.yaml** | 267 | FastAPI service (3 replicas → 10 with HPA) |

### Scaling & Ingress
| File | Size | Purpose |
|------|------|---------|
| **hpa.yaml** | 97 | Auto-scaling policies for all services |
| **ingress.yaml** | 69 | TLS/SSL, routing, rate limiting |
| **prometheus.yaml** | 258 | Monitoring setup with alerts |

### Automation
| File | Size | Purpose |
|------|------|---------|
| **deploy.sh** | 126 | Automated deployment script |

## 🐳 Helm Chart (`/helm/ai-imutis/`)

| File | Size | Purpose |
|------|------|---------|
| **Chart.yaml** | 29 | Chart metadata & dependencies |
| **values.yaml** | 275 | Default configuration |
| **values-prod.yaml** | 113 | Production overrides |

## 🔄 CI/CD Pipeline (`.github/workflows/`)

| File | Jobs | Purpose |
|------|------|---------|
| **ci.yml** | 5 | lint → docker → deploy → load-test → notify |

**Jobs:**
1. **lint** - Python/YAML validation
2. **docker** - Build & push to GCR
3. **deploy** - Auto-deploy to GKE (main branch only)
4. **load-test** - Performance testing (on version tags)
5. **notify** - Failure notifications

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│         Kubernetes Cluster (ai-imutis namespace)       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Ingress (TLS/SSL, Rate Limiting, Routing)     │ │
│  └──────┬────────────────────────────────────────┬─┘ │
│         │                                        │     │
│  ┌──────▼────────────────────────────────────────▼──┐ │
│  │  API Deployment (3-10 replicas via HPA)       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│  │  │ api-0    │  │ api-1    │  │ api-2... │    │ │
│  │  └──────────┘  └──────────┘  └──────────┘    │ │
│  │                                               │ │
│  │  ✓ Prometheus metrics (/metrics)             │ │
│  │  ✓ Health checks (/health)                   │ │
│  │  ✓ Structured JSON logging                   │ │
│  └──────────────────────────────────────────────┘ │
│                     ▼                              │
│  ┌──────────────────────────────────────────────┐ │
│  │  PostgreSQL StatefulSet (1-3 replicas)      │ │
│  │  └─────────────────────────────────────────┘ │
│  │  RedisStatefulSet (1-3 replicas)            │ │
│  │  └─────────────────────────────────────────┘ │
│  │  Prometheus Deployment (metrics & alerts)   │ │
│  │  └─────────────────────────────────────────┘ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │  Auto-scaling (HPA)                          │ │
│  │  API: 3-10 (70% CPU, 80% memory)            │ │
│  │  DB: 1-3 (80% CPU, 85% memory)              │ │
│  │  Cache: 1-3 (75% CPU, 80% memory)           │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
└─────────────────────────────────────────────────────┘
```

## ✨ Key Features

### Infrastructure
- ✅ Multi-replica deployments (rolling updates)
- ✅ StatefulSets for persistent data (PostgreSQL, Redis)
- ✅ Horizontal Pod Autoscaling (HPA)
- ✅ Network policies (default deny + specific rules)
- ✅ Pod disruption budgets (HA protection)
- ✅ Init containers (automatic migrations)
- ✅ Graceful shutdown handling

### Observability
- ✅ Prometheus metrics (13 metrics defined)
- ✅ Structured JSON logging
- ✅ Distributed tracing (OpenTelemetry + Jaeger)
- ✅ Sentry error tracking
- ✅ Pre-configured Prometheus alerts
- ✅ Grafana dashboard templates
- ✅ Health checks (liveness, readiness, startup)

### Security
- ✅ TLS/SSL with cert-manager
- ✅ Network policies
- ✅ Secret management
- ✅ RBAC (Service Accounts, Roles)
- ✅ Non-root user execution
- ✅ Dropped Linux capabilities
- ✅ Security headers

### DevOps
- ✅ Helm charts (dev & prod values)
- ✅ GitHub Actions CI/CD
- ✅ Automated Docker builds
- ✅ Automated deployments
- ✅ Load testing (Locust)
- ✅ Backup & disaster recovery

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install tools
kubectl v1.26+
helm 3.12+
docker
gcloud (for GKE)
```

### 2. Create Secrets
```bash
kubectl create secret generic api-secrets \
  --from-literal=database-url="..." \
  --from-literal=redis-url="..." \
  --from-literal=firebase-project-id="..." \
  --from-file=firebase-service-account=key.json \
  --from-literal=sentry-dsn="..." \
  -n ai-imutis
```

### 3. Deploy with Helm
```bash
helm install ai-imutis ./helm/ai-imutis \
  --namespace ai-imutis \
  --create-namespace \
  --values helm/ai-imutis/values-prod.yaml
```

### 4. Verify
```bash
kubectl get pods -n ai-imutis
kubectl get svc -n ai-imutis
curl http://api-endpoint/health
```

See [K8S_DEPLOYMENT.md](K8S_DEPLOYMENT.md) for detailed step-by-step instructions.

## 📊 Monitoring

### Access Prometheus
```bash
kubectl port-forward -n ai-imutis svc/prometheus 9090:9090
# Visit http://localhost:9090
```

### View Logs
```bash
kubectl logs -n ai-imutis -l app=api -f
```

### Check Metrics
```bash
kubectl exec -it api-0 -n ai-imutis -- curl localhost:8000/metrics
```

See [MONITORING.md](MONITORING.md) for comprehensive monitoring guide.

## 🛠️ Common Operations

### Scale Replicas
```bash
kubectl scale deployment api --replicas=5 -n ai-imutis
```

### View HPA Status
```bash
kubectl get hpa -n ai-imutis -w
```

### Port Forward to Services
```bash
# API
kubectl port-forward -n ai-imutis svc/api 8000:80

# PostgreSQL
kubectl port-forward -n ai-imutis svc/postgres 5432:5432

# Redis
kubectl port-forward -n ai-imutis svc/redis 6379:6379
```

### Run Migrations
```bash
# Automatic (via init container)
# Manual if needed:
kubectl exec -it postgres-0 -n ai-imutis -- psql -U app_user -d ai_imutis
```

See [K8S_QUICK_REFERENCE.sh](K8S_QUICK_REFERENCE.sh) for more commands.

## 🔍 Troubleshooting

### Pods not starting?
```bash
kubectl describe pod api-0 -n ai-imutis
kubectl logs api-0 -n ai-imutis -c migrations
```

### Database connection issues?
```bash
kubectl exec -it api-0 -n ai-imutis -- \
  psql $DATABASE_URL -c "SELECT 1"
```

### Check events
```bash
kubectl get events -n ai-imutis --sort-by='.lastTimestamp'
```

See [K8S_DEPLOYMENT.md#Troubleshooting](K8S_DEPLOYMENT.md) for detailed troubleshooting.

## 📚 Additional Resources

| Resource | URL |
|----------|-----|
| Kubernetes Docs | https://kubernetes.io/docs |
| Helm Docs | https://helm.sh/docs |
| FastAPI Deployment | https://fastapi.tiangolo.com/deployment |
| Prometheus | https://prometheus.io/docs |
| PostgreSQL K8s | https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application |

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Total K8s manifest files | 10 |
| Total helm chart files | 3 |
| Total CI/CD files | 1 |
| Total documentation | 5 |
| Total lines of infrastructure code | ~4,000 |
| Average deployment time | 5-15 minutes |

## ✅ Deployment Checklist

- [ ] Kubernetes cluster created (1.26+)
- [ ] kubectl configured and working
- [ ] helm installed (3.12+)
- [ ] Docker registry access configured
- [ ] StorageClass created (fast-ssd)
- [ ] Secrets created in cluster
- [ ] GitHub Actions secrets configured
- [ ] Deployment manifests reviewed
- [ ] Helm values customized
- [ ] CI/CD pipeline tested
- [ ] Monitoring configured
- [ ] Backup strategy documented
- [ ] Team trained on operations

## 🎯 Next Steps

1. **Review** [K8S_SUMMARY.md](K8S_SUMMARY.md) for overview
2. **Prepare** cluster and secrets (see Prerequisites)
3. **Deploy** using Helm or manifests (see [K8S_DEPLOYMENT.md](K8S_DEPLOYMENT.md))
4. **Monitor** with Prometheus/Grafana (see [MONITORING.md](MONITORING.md))
5. **Test** with load testing script (locustfile.py)
6. **Optimize** based on metrics and performance

## 📝 Notes

- All manifests are production-ready with security best practices
- Helm chart includes dependencies for PostgreSQL, Redis, Prometheus
- CI/CD pipeline automates Docker builds and Kubernetes deployments
- Monitoring stack includes metrics, logging, tracing, and error tracking
- Auto-scaling configured for all services based on CPU and memory
- Network policies enforce least-privilege access
- All deployments use non-root users with dropped capabilities

---

**Last Updated**: 2024-01-16
**Status**: ✅ Production-Ready
**Version**: 1.0.0
