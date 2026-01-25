# Monitoring and Observability Guide for AI-IMUTIS

## Architecture Overview

The AI-IMUTIS backend includes a comprehensive observability stack:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application (FastAPI)                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Prometheus Metrics | Structured JSON Logs | Sentry      ││
│  │ OpenTelemetry Traces                                    ││
│  └─────────────────────────────────────────────────────────┘│
└────────┬──────────────────────────────────────────┬─────────┘
         │                                          │
    ┌────▼────────────┐              ┌─────────────▼─────┐
    │  Prometheus     │              │    Jaeger Tracing │
    │  (Metrics)      │              │    (Traces)       │
    └────┬────────────┘              └────────┬──────────┘
         │                                    │
    ┌────▼─────────────────────────────────────────┐
    │           Grafana Dashboards                  │
    │      (Real-time visualization)               │
    └─────────────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │      Alert Manager / PagerDuty         │
    │      (Incident response)               │
    └────────────────────────────────────────┘
```

## Metrics

### Prometheus Metrics Collected

**HTTP Metrics:**
- `http_requests_total`: Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds`: Request latency histogram (p50, p95, p99)

**Database Metrics:**
- `db_queries_total`: Total database queries by operation type
- `db_query_duration_seconds`: Query latency histogram
- `db_connection_pool_size`: Active connection pool size

**Redis Metrics:**
- `redis_commands_total`: Total Redis commands by operation type
- `redis_command_duration_seconds`: Command latency histogram

**Business Metrics:**
- `bookings_total`: Total bookings by status (success/failed)
- `booking_duration_seconds`: Booking completion time
- `rate_limit_rejections_total`: Rate limit rejections by identifier
- `auth_failures_total`: Authentication failures by error type
- `websocket_connections`: Active WebSocket connections
- `websocket_messages_total`: Total WebSocket messages sent

### Accessing Metrics

**Local (Development):**
```bash
curl http://localhost:8000/metrics
```

**Kubernetes:**
```bash
# Port forward
kubectl port-forward -n ai-imutis svc/api 8000:80

# Access Prometheus directly
kubectl port-forward -n ai-imutis svc/prometheus 9090:9090
# Visit http://localhost:9090
```

**Prometheus Queries:**

```promql
# API request rate (requests/sec)
rate(http_requests_total[5m])

# Error rate (5xx responses)
rate(http_requests_total{status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Database connection pool utilization
db_connection_pool_size / 20  # Assuming pool size of 20

# Booking success rate
rate(bookings_total{status="success"}[5m]) / rate(bookings_total[5m])

# Redis command latency
histogram_quantile(0.99, rate(redis_command_duration_seconds_bucket[5m]))

# Authentication failure rate
rate(auth_failures_total[5m])
```

## Structured Logging

### Log Format

All logs are output as JSON for easy parsing and analysis:

```json
{
  "timestamp": "2024-01-16T10:30:45.123456",
  "level": "INFO",
  "logger": "app.routers.travels",
  "message": "Booking created successfully",
  "pathname": "app/routers/travels.py",
  "lineno": 156,
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "device_ip": "192.168.1.100",
  "exception": null,
  "extra": {
    "booking_id": "booking456",
    "route_id": "route789"
  }
}
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors requiring immediate attention

### Viewing Logs

**Local:**
```bash
# Watch real-time logs
tail -f logs/api.log | grep -E "ERROR|CRITICAL"

# Parse JSON logs
cat logs/api.log | jq '.[] | select(.level == "ERROR")'
```

**Kubernetes:**
```bash
# Stream logs
kubectl logs -n ai-imutis -l app=api -f

# Logs from specific pod
kubectl logs -n ai-imutis pod/api-0 --tail=200

# Search for errors
kubectl logs -n ai-imutis -l app=api | grep ERROR

# Export to file for analysis
kubectl logs -n ai-imutis -l app=api > logs.json
```

**CloudWatch (AWS):**
```bash
# Install aws-cli
aws logs tail /aws/eks/ai-imutis/api --follow
```

**Stackdriver (GCP):**
```bash
# Using gcloud CLI
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=ai-imutis" --limit=100
```

## Distributed Tracing

### OpenTelemetry Configuration

Traces are automatically collected from:
- FastAPI request handlers
- SQLAlchemy database operations
- Redis client commands

**Jaeger Integration:**

```bash
# Port forward Jaeger UI
kubectl port-forward -n ai-imutis svc/jaeger-collector 16686:16686

# Visit http://localhost:16686
```

**Trace Analysis:**
1. Filter by service (ai-imutis-api)
2. Filter by operation (GET /api/travels, POST /api/bookings, etc.)
3. View latency distribution
4. Identify slow operations

## Alert Configuration

### Pre-configured Alerts

**Critical (immediate page):**
- API error rate > 5% for 5 minutes
- Database connection pool > 18/20
- PostgreSQL down

**Warning (email/Slack):**
- API latency p95 > 1 second
- High rate limit rejections
- WebSocket connection drops

**Info (logging):**
- High booking volume
- Authorization failures
- Rate limit warnings

### Alerting Rules (Prometheus)

Located in `k8s/prometheus.yaml`, examples:

```yaml
- alert: APIHighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "API high error rate (>5%)"
```

### Integration with Notification Systems

**Slack Integration:**
```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK'
route:
  receiver: 'slack'
receivers:
- name: 'slack'
  slack_configs:
  - channel: '#alerts'
```

**PagerDuty Integration:**
```yaml
receivers:
- name: 'pagerduty'
  pagerduty_configs:
  - service_key: 'YOUR_SERVICE_KEY'
```

## Grafana Dashboards

### Creating Custom Dashboards

**1. Access Grafana:**
```bash
kubectl port-forward -n ai-imutis svc/grafana 3000:3000
# Default: admin/admin
```

**2. Key Metric Groups to Monitor:**

**API Performance:**
- Request rate (req/s)
- Error rate (%)
- Latency percentiles (p50, p95, p99)
- Endpoint-specific metrics

**Database Health:**
- Query rate
- Query latency
- Connection pool usage
- Transaction rate

**Cache Performance:**
- Redis command rate
- Cache hit/miss ratio
- Eviction rate
- Memory usage

**Business KPIs:**
- Bookings per hour
- Booking success rate
- Average booking value
- User growth rate

### Sample Dashboard JSON

```json
{
  "dashboard": {
    "title": "AI-IMUTIS API",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

## Health Checks

### Liveness Probe

Endpoint: `GET /health`

Indicates if the application is running and responsive.

**Kubernetes Configuration:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 10
  failureThreshold: 3
```

### Readiness Probe

Checks if the application is ready to accept traffic.

**Kubernetes Configuration:**
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

### Startup Probe

Verifies application initialization on startup.

**Kubernetes Configuration:**
```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8000
  failureThreshold: 30
  periodSeconds: 10
```

## Performance Monitoring

### Key Performance Indicators (KPIs)

**Application Level:**
- Requests per second
- Average response time
- Error rate
- P99 latency

**Infrastructure Level:**
- CPU utilization
- Memory usage
- Network I/O
- Disk I/O

**Business Level:**
- Bookings per hour
- User signups
- Revenue per booking
- Route popularity

### Capacity Planning

Monitor these trends over time:

```bash
# Get historical data from Prometheus
curl 'http://prometheus:9090/api/v1/query_range?query=http_requests_total&start=<start_time>&end=<end_time>&step=60'
```

**Scaling Decisions:**
- API: Scale at 70% CPU utilization
- Database: Read replicas when 80% CPU
- Redis: Cluster when 80% memory

## Sentry Integration

### Error Tracking

Errors are automatically captured and sent to Sentry.

**Access Sentry Dashboard:**
1. Visit https://sentry.io
2. Navigate to project: AI-IMUTIS
3. Filter by environment, release, user

**Error Analysis:**
- Exception frequency
- Affected user count
- Stack traces with source maps
- Breadcrumbs (events leading to error)

**Release Tracking:**
```python
# In app/config.py
sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=API_ENVIRONMENT,
    release=API_VERSION,
    traces_sample_rate=0.1,
)
```

## Load Testing

### Running Load Tests

```bash
# Using Locust
locust -f locustfile.py --host=http://api.example.com --users=100 --spawn-rate=10 --run-time=10m --headless

# Results saved to CSV
```

### Analyzing Results

```bash
# View response time distribution
grep "Type" locust_stats.csv | head -20

# Calculate percentiles
python3 << 'EOF'
import csv
import statistics

with open('locust_stats.csv') as f:
    reader = csv.DictReader(f)
    latencies = [float(row['Median Response Time (ms)']) for row in reader]
    print(f"P50: {statistics.median(latencies)}")
    print(f"P95: {statistics.quantiles(latencies, n=20)[18]}")
EOF
```

## Best Practices

### Monitoring Setup
- ✓ Collect metrics from all critical services
- ✓ Log structured data with request context
- ✓ Implement distributed tracing
- ✓ Configure alerts with appropriate thresholds
- ✓ Create dashboards for operations team

### Alerting Strategy
- ✓ Alert on business metrics, not just infrastructure
- ✓ Avoid alert fatigue (tune thresholds)
- ✓ Include runbook links in alerts
- ✓ Implement alert routing (severity-based)

### Log Management
- ✓ Use structured logging (JSON)
- ✓ Include request IDs for tracing
- ✓ Implement log rotation
- ✓ Centralize logs (ELK, Loki, etc.)
- ✓ Set appropriate retention policies

### Retention Policies
- Prometheus metrics: 15 days (adjust for storage)
- Application logs: 30 days (archive older logs)
- Traces: 7 days (sample at 10%)
- Sentry: Keep all errors, auto-delete after 90 days

## Tools and Integrations

### Recommended Tools

| Category | Tool | Usage |
|----------|------|-------|
| Metrics | Prometheus | Real-time metric collection |
| Visualization | Grafana | Dashboard and alerting |
| Logs | Loki / ELK | Log aggregation |
| Traces | Jaeger / Tempo | Distributed tracing |
| Errors | Sentry | Error tracking |
| APM | DataDog / New Relic | Complete observability |

### Cloud Provider Integrations

**AWS:**
- CloudWatch (logs, metrics)
- X-Ray (tracing)
- SNS (alerting)

**GCP:**
- Cloud Logging
- Cloud Trace
- Cloud Monitoring

**Azure:**
- Application Insights
- Log Analytics
- Azure Monitor

## Troubleshooting

### No metrics appearing in Prometheus

1. Check Prometheus is scraping: `http://prometheus:9090/targets`
2. Verify pod has metrics annotation: `prometheus.io/scrape: "true"`
3. Check pod logs for errors: `kubectl logs -l app=api`
4. Verify metrics endpoint: `kubectl exec -it api-0 -- curl localhost:8000/metrics`

### High latency in traces

1. Check database query performance
2. Review slow query logs: `SHOW log_statement = 'all';`
3. Check Redis command latencies
4. Profile with application profiler

### Alert storms

1. Increase alert thresholds
2. Extend evaluation period (e.g., 10m instead of 5m)
3. Add alert routing rules to reduce noise
4. Implement alert silencing for known issues

## Next Steps

1. **Set up Grafana** for team visibility
2. **Configure notification channels** (Slack, PagerDuty)
3. **Document runbooks** for common alerts
4. **Establish on-call rotation**
5. **Review metrics weekly** with the team
6. **Optimize thresholds** based on actual behavior
