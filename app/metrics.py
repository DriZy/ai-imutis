"""Prometheus metrics for AI-IMUTIS backend."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# Database metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation', 'table'],
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query latency',
    ['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Current database connection pool size',
)

# Redis metrics
redis_commands_total = Counter(
    'redis_commands_total',
    'Total Redis commands',
    ['command', 'status'],
)

redis_command_duration_seconds = Histogram(
    'redis_command_duration_seconds',
    'Redis command latency',
    ['command'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1),
)

# Business metrics
bookings_total = Counter(
    'bookings_total',
    'Total bookings',
    ['status'],
)

booking_duration_seconds = Histogram(
    'booking_duration_seconds',
    'Time to complete booking',
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
)

rate_limit_rejections_total = Counter(
    'rate_limit_rejections_total',
    'Total rate limit rejections',
    ['identifier_type'],
)

auth_failures_total = Counter(
    'auth_failures_total',
    'Total authentication failures',
    ['reason'],
)

# WebSocket metrics
websocket_connections = Gauge(
    'websocket_connections',
    'Active WebSocket connections',
    ['type'],
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total WebSocket messages sent',
    ['type'],
)

def metrics_view():
    """Expose Prometheus metrics."""
    return generate_latest()
