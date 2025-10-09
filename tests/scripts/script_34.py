# Monitoring and Observability
import logging
import time
import random
import json
from datetime import datetime, timedelta
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import structlog
import traceback
import psutil
import socket

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

def application_metrics():
    """Application metrics collection with Prometheus"""
    try:
        # Define metrics
        REQUEST_COUNT = Counter('http_requests_total', 
                              'Total HTTP requests', 
                              ['method', 'endpoint', 'status'])
        
        REQUEST_LATENCY = Histogram('http_request_duration_seconds',
                                  'HTTP request latency',
                                  ['method', 'endpoint'])
        
        ACTIVE_CONNECTIONS = Gauge('active_connections',
                                 'Number of active connections')
        
        MEMORY_USAGE = Gauge('memory_usage_bytes',
                           'Memory usage in bytes')
        
        ERROR_RATE = Summary('error_rate',
                           'Application error rate')
        
        # Simulate application metrics
        endpoints = ['/api/users', '/api/orders', '/api/products', '/health', '/metrics']
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        status_codes = [200, 201, 400, 404, 500]
        
        # Simulate metric collection over time
        metrics_data = []
        
        for i in range(1000):  # Simulate 1000 requests
            endpoint = random.choice(endpoints)
            method = random.choice(methods)
            
            # Status code distribution (mostly successful)
            if random.random() < 0.85:
                status = random.choice([200, 201])
            elif random.random() < 0.95:
                status = random.choice([400, 404])
            else:
                status = 500
            
            # Simulate request latency
            if endpoint == '/health':
                latency = random.uniform(0.001, 0.010)  # Fast health check
            elif status == 500:
                latency = random.uniform(1.0, 5.0)      # Slow errors
            else:
                latency = random.uniform(0.010, 0.500)  # Normal requests
            
            # Record metrics
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
            
            metrics_data.append({
                'timestamp': datetime.utcnow().isoformat(),
                'method': method,
                'endpoint': endpoint,
                'status': status,
                'latency': latency
            })
        
        # Update gauges
        ACTIVE_CONNECTIONS.set(random.randint(10, 100))
        MEMORY_USAGE.set(psutil.virtual_memory().used)
        
        # Calculate error rate
        error_count = len([m for m in metrics_data if m['status'] >= 400])
        error_rate = error_count / len(metrics_data)
        ERROR_RATE.observe(error_rate)
        
        # Generate metrics summary
        status_distribution = {}
        for metric in metrics_data:
            status = metric['status']
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        avg_latency_by_endpoint = {}
        for endpoint in endpoints:
            endpoint_metrics = [m for m in metrics_data if m['endpoint'] == endpoint]
            if endpoint_metrics:
                avg_latency = sum(m['latency'] for m in endpoint_metrics) / len(endpoint_metrics)
                avg_latency_by_endpoint[endpoint] = avg_latency
        
        return {
            'total_requests': len(metrics_data),
            'error_rate': error_rate,
            'endpoints_monitored': len(endpoints),
            'status_distribution': status_distribution,
            'avg_latency_by_endpoint': avg_latency_by_endpoint,
            'metrics_types': ['counter', 'histogram', 'gauge', 'summary'],
            'memory_usage_mb': psutil.virtual_memory().used / (1024 * 1024)
        }
        
    except Exception as e:
        return {'error': str(e)}

def structured_logging():
    """Structured logging implementation"""
    try:
        # Get structured logger
        logger = structlog.get_logger("application")
        
        # Simulate various log events
        log_events = []
        
        # Info logs
        logger.info("Application started", version="1.2.3", port=8080)
        log_events.append({'level': 'info', 'event': 'app_start'})
        
        logger.info("User authenticated", user_id=12345, username="alice", ip="192.168.1.100")
        log_events.append({'level': 'info', 'event': 'user_auth'})
        
        # Warning logs
        logger.warning("High memory usage detected", 
                      memory_percent=85.5, 
                      threshold=80.0,
                      service="order-processor")
        log_events.append({'level': 'warning', 'event': 'high_memory'})
        
        # Error logs
        try:
            # Simulate an error
            raise ValueError("Database connection failed")
        except ValueError as e:
            logger.error("Database error occurred",
                        error=str(e),
                        database="orders_db",
                        connection_pool="primary",
                        exc_info=True)
            log_events.append({'level': 'error', 'event': 'db_error'})
        
        # Business logic logs
        logger.info("Order processed",
                   order_id="ORD-2024-001",
                   customer_id=67890,
                   amount=129.99,
                   payment_method="credit_card",
                   processing_time_ms=250)
        log_events.append({'level': 'info', 'event': 'order_processed'})
        
        # Performance logs
        logger.info("Query execution",
                   query="SELECT * FROM products WHERE category = ?",
                   execution_time_ms=45,
                   rows_returned=156,
                   cache_hit=False)
        log_events.append({'level': 'info', 'event': 'query_execution'})
        
        # Security logs
        logger.warning("Failed login attempt",
                      ip_address="10.0.0.15",
                      username="admin",
                      attempt_count=3,
                      user_agent="Mozilla/5.0...")
        log_events.append({'level': 'warning', 'event': 'failed_login'})
        
        # Audit logs
        logger.info("Configuration changed",
                   setting="max_connections",
                   old_value=100,
                   new_value=150,
                   changed_by="admin_user",
                   change_reason="increased_load")
        log_events.append({'level': 'info', 'event': 'config_change'})
        
        # Calculate log level distribution
        level_distribution = {}
        for event in log_events:
            level = event['level']
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        return {
            'logging_framework': 'structlog',
            'total_log_events': len(log_events),
            'log_levels': list(level_distribution.keys()),
            'level_distribution': level_distribution,
            'structured_fields': ['user_id', 'order_id', 'execution_time_ms', 'ip_address'],
            'log_format': 'JSON'
        }
        
    except Exception as e:
        return {'error': str(e)}

def health_checks():
    """Application health check implementation"""
    health_checks = {
        'database': {
            'status': 'healthy',
            'response_time_ms': 15,
            'last_check': datetime.utcnow().isoformat(),
            'details': {
                'connection_pool_size': 20,
                'active_connections': 8,
                'query_success_rate': 0.998
            }
        },
        'redis_cache': {
            'status': 'healthy',
            'response_time_ms': 2,
            'last_check': datetime.utcnow().isoformat(),
            'details': {
                'memory_usage_percent': 65,
                'hit_rate': 0.89,
                'evicted_keys': 125
            }
        },
        'external_api': {
            'status': 'degraded',
            'response_time_ms': 800,
            'last_check': datetime.utcnow().isoformat(),
            'details': {
                'success_rate': 0.92,
                'timeout_rate': 0.08,
                'circuit_breaker': 'half_open'
            }
        },
        'message_queue': {
            'status': 'healthy',
            'response_time_ms': 5,
            'last_check': datetime.utcnow().isoformat(),
            'details': {
                'queue_depth': 150,
                'processing_rate': 450,  # messages per minute
                'dead_letter_queue': 3
            }
        },
        'file_system': {
            'status': 'healthy',
            'response_time_ms': 1,
            'last_check': datetime.utcnow().isoformat(),
            'details': {
                'disk_usage_percent': 72,
                'available_space_gb': 45.2,
                'inode_usage_percent': 15
            }
        }
    }
    
    # Calculate overall health
    healthy_services = len([s for s in health_checks.values() if s['status'] == 'healthy'])
    degraded_services = len([s for s in health_checks.values() if s['status'] == 'degraded'])
    unhealthy_services = len([s for s in health_checks.values() if s['status'] == 'unhealthy'])
    
    if unhealthy_services > 0:
        overall_status = 'unhealthy'
    elif degraded_services > 0:
        overall_status = 'degraded'
    else:
        overall_status = 'healthy'
    
    # Calculate average response time
    avg_response_time = sum(check['response_time_ms'] for check in health_checks.values()) / len(health_checks)
    
    return {
        'overall_status': overall_status,
        'services_checked': len(health_checks),
        'healthy_services': healthy_services,
        'degraded_services': degraded_services,
        'unhealthy_services': unhealthy_services,
        'average_response_time_ms': avg_response_time,
        'health_checks': health_checks
    }

def distributed_tracing():
    """Distributed tracing simulation"""
    # Simulate a distributed trace
    trace_id = "trace-" + "-".join([f"{random.randint(1000, 9999)}" for _ in range(4)])
    
    # Define services in the trace
    services = [
        {'name': 'api-gateway', 'duration_ms': 5},
        {'name': 'auth-service', 'duration_ms': 25},
        {'name': 'order-service', 'duration_ms': 150},
        {'name': 'inventory-service', 'duration_ms': 80},
        {'name': 'payment-service', 'duration_ms': 200},
        {'name': 'notification-service', 'duration_ms': 30},
        {'name': 'database', 'duration_ms': 45}
    ]
    
    # Generate spans
    spans = []
    current_time = datetime.utcnow()
    cumulative_time = 0
    
    for i, service in enumerate(services):
        span_id = f"span-{i+1:03d}"
        parent_span_id = f"span-{i:03d}" if i > 0 else None
        
        # Add some jitter to duration
        actual_duration = service['duration_ms'] + random.randint(-10, 30)
        
        span = {
            'trace_id': trace_id,
            'span_id': span_id,
            'parent_span_id': parent_span_id,
            'service_name': service['name'],
            'operation_name': f"{service['name']}_operation",
            'start_time': (current_time + timedelta(milliseconds=cumulative_time)).isoformat(),
            'duration_ms': actual_duration,
            'status': 'ok' if random.random() > 0.05 else 'error',
            'tags': {
                'http.method': 'POST' if 'service' in service['name'] else 'N/A',
                'http.url': f"/api/{service['name'].replace('-service', '')}" if 'service' in service['name'] else 'N/A',
                'component': service['name']
            }
        }
        
        # Add service-specific tags
        if service['name'] == 'database':
            span['tags']['db.statement'] = 'SELECT * FROM orders WHERE id = ?'
            span['tags']['db.type'] = 'postgresql'
        elif service['name'] == 'payment-service':
            span['tags']['payment.method'] = 'credit_card'
            span['tags']['payment.amount'] = '129.99'
        
        spans.append(span)
        cumulative_time += actual_duration
    
    # Calculate trace statistics
    total_duration = sum(span['duration_ms'] for span in spans)
    error_spans = [span for span in spans if span['status'] == 'error']
    
    # Identify bottlenecks
    slowest_span = max(spans, key=lambda x: x['duration_ms'])
    
    # Service dependency map
    service_dependencies = []
    for i, span in enumerate(spans[1:], 1):
        parent_service = next(s['service_name'] for s in spans if s['span_id'] == span['parent_span_id'])
        service_dependencies.append({
            'from': parent_service,
            'to': span['service_name'],
            'duration_ms': span['duration_ms']
        })
    
    return {
        'trace_id': trace_id,
        'total_spans': len(spans),
        'total_duration_ms': total_duration,
        'services_involved': len(set(span['service_name'] for span in spans)),
        'error_count': len(error_spans),
        'slowest_service': slowest_span['service_name'],
        'slowest_duration_ms': slowest_span['duration_ms'],
        'service_dependencies': len(service_dependencies),
        'trace_complete': all(span['status'] == 'ok' for span in spans)
    }

def alerting_system():
    """Alerting system implementation"""
    # Define alert rules
    alert_rules = [
        {
            'name': 'HighErrorRate',
            'condition': 'error_rate > 0.05',
            'severity': 'critical',
            'description': 'Error rate exceeded 5%'
        },
        {
            'name': 'HighLatency',
            'condition': 'p99_latency > 1000',
            'severity': 'warning',
            'description': '99th percentile latency > 1s'
        },
        {
            'name': 'LowDiskSpace',
            'condition': 'disk_usage > 0.9',
            'severity': 'critical',
            'description': 'Disk usage > 90%'
        },
        {
            'name': 'HighMemoryUsage',
            'condition': 'memory_usage > 0.85',
            'severity': 'warning',
            'description': 'Memory usage > 85%'
        },
        {
            'name': 'DatabaseConnectionFailure',
            'condition': 'db_connection_success_rate < 0.95',
            'severity': 'critical',
            'description': 'Database connection success rate < 95%'
        }
    ]
    
    # Simulate current system metrics
    current_metrics = {
        'error_rate': 0.08,  # 8% - triggers HighErrorRate
        'p99_latency': 1200,  # 1.2s - triggers HighLatency
        'disk_usage': 0.75,   # 75% - OK
        'memory_usage': 0.88, # 88% - triggers HighMemoryUsage
        'db_connection_success_rate': 0.92  # 92% - triggers DatabaseConnectionFailure
    }
    
    # Evaluate alerts
    active_alerts = []
    for rule in alert_rules:
        # Simple evaluation (in practice, this would be more sophisticated)
        if rule['name'] == 'HighErrorRate' and current_metrics['error_rate'] > 0.05:
            active_alerts.append({
                'rule': rule['name'],
                'severity': rule['severity'],
                'description': rule['description'],
                'current_value': current_metrics['error_rate'],
                'threshold': 0.05,
                'triggered_at': datetime.utcnow().isoformat()
            })
        elif rule['name'] == 'HighLatency' and current_metrics['p99_latency'] > 1000:
            active_alerts.append({
                'rule': rule['name'],
                'severity': rule['severity'],
                'description': rule['description'],
                'current_value': current_metrics['p99_latency'],
                'threshold': 1000,
                'triggered_at': datetime.utcnow().isoformat()
            })
        elif rule['name'] == 'HighMemoryUsage' and current_metrics['memory_usage'] > 0.85:
            active_alerts.append({
                'rule': rule['name'],
                'severity': rule['severity'],
                'description': rule['description'],
                'current_value': current_metrics['memory_usage'],
                'threshold': 0.85,
                'triggered_at': datetime.utcnow().isoformat()
            })
        elif rule['name'] == 'DatabaseConnectionFailure' and current_metrics['db_connection_success_rate'] < 0.95:
            active_alerts.append({
                'rule': rule['name'],
                'severity': rule['severity'],
                'description': rule['description'],
                'current_value': current_metrics['db_connection_success_rate'],
                'threshold': 0.95,
                'triggered_at': datetime.utcnow().isoformat()
            })
    
    # Alert routing
    notification_channels = {
        'critical': ['pagerduty', 'slack', 'email'],
        'warning': ['slack', 'email'],
        'info': ['email']
    }
    
    # Count alerts by severity
    severity_counts = {}
    for alert in active_alerts:
        severity = alert['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return {
        'total_alert_rules': len(alert_rules),
        'active_alerts': len(active_alerts),
        'critical_alerts': severity_counts.get('critical', 0),
        'warning_alerts': severity_counts.get('warning', 0),
        'notification_channels': len(set(sum(notification_channels.values(), []))),
        'alert_details': active_alerts,
        'system_health_score': 1 - (len(active_alerts) / len(alert_rules))
    }

def monitoring_dashboard():
    """Generate monitoring dashboard data"""
    # Dashboard widgets
    widgets = {
        'system_overview': {
            'cpu_usage': random.uniform(20, 80),
            'memory_usage': random.uniform(50, 90),
            'disk_usage': random.uniform(30, 95),
            'network_io': random.uniform(10, 100)
        },
        'application_metrics': {
            'requests_per_minute': random.randint(500, 2000),
            'error_rate': random.uniform(0.01, 0.1),
            'average_response_time': random.uniform(100, 500),
            'active_users': random.randint(50, 500)
        },
        'database_metrics': {
            'connections': random.randint(10, 50),
            'queries_per_second': random.randint(100, 1000),
            'slow_queries': random.randint(0, 10),
            'replication_lag': random.uniform(0, 100)
        },
        'cache_metrics': {
            'hit_rate': random.uniform(0.7, 0.95),
            'memory_usage': random.uniform(40, 85),
            'operations_per_second': random.randint(1000, 10000),
            'evictions_per_minute': random.randint(0, 50)
        }
    }
    
    # Generate time series data (last 24 hours)
    time_series = {
        'timestamps': [],
        'cpu_usage': [],
        'memory_usage': [],
        'request_count': [],
        'error_count': []
    }
    
    base_time = datetime.utcnow() - timedelta(hours=24)
    for i in range(24):  # Hourly data points
        timestamp = base_time + timedelta(hours=i)
        time_series['timestamps'].append(timestamp.isoformat())
        time_series['cpu_usage'].append(random.uniform(20, 80))
        time_series['memory_usage'].append(random.uniform(50, 90))
        time_series['request_count'].append(random.randint(1000, 5000))
        time_series['error_count'].append(random.randint(10, 100))
    
    # Top N lists
    top_endpoints = [
        {'endpoint': '/api/users', 'requests': 15420, 'avg_latency': 145},
        {'endpoint': '/api/orders', 'requests': 12350, 'avg_latency': 220},
        {'endpoint': '/api/products', 'requests': 9870, 'avg_latency': 180},
        {'endpoint': '/health', 'requests': 2880, 'avg_latency': 5},
        {'endpoint': '/api/payments', 'requests': 5670, 'avg_latency': 350}
    ]
    
    error_breakdown = [
        {'error_type': '404 Not Found', 'count': 245},
        {'error_type': '500 Internal Server Error', 'count': 89},
        {'error_type': '400 Bad Request', 'count': 156},
        {'error_type': '401 Unauthorized', 'count': 78},
        {'error_type': '503 Service Unavailable', 'count': 23}
    ]
    
    return {
        'dashboard_widgets': len(widgets),
        'time_series_points': len(time_series['timestamps']),
        'top_endpoints': len(top_endpoints),
        'error_types': len(error_breakdown),
        'current_metrics': widgets,
        'historical_data': time_series,
        'performance_data': top_endpoints,
        'error_analysis': error_breakdown
    }

if __name__ == "__main__":
    print("Monitoring and observability operations...")
    
    # Application metrics
    metrics_result = application_metrics()
    if 'error' not in metrics_result:
        print(f"Metrics: {metrics_result['total_requests']} requests, {metrics_result['error_rate']:.2%} error rate")
    
    # Structured logging
    logging_result = structured_logging()
    if 'error' not in logging_result:
        print(f"Logging: {logging_result['total_log_events']} events, {len(logging_result['log_levels'])} levels")
    
    # Health checks
    health_result = health_checks()
    print(f"Health: {health_result['overall_status']}, {health_result['healthy_services']}/{health_result['services_checked']} services healthy")
    
    # Distributed tracing
    tracing_result = distributed_tracing()
    print(f"Tracing: {tracing_result['total_spans']} spans, {tracing_result['services_involved']} services, {tracing_result['total_duration_ms']}ms total")
    
    # Alerting system
    alerting_result = alerting_system()
    print(f"Alerting: {alerting_result['active_alerts']} active alerts ({alerting_result['critical_alerts']} critical)")
    
    # Monitoring dashboard
    dashboard_result = monitoring_dashboard()
    print(f"Dashboard: {dashboard_result['dashboard_widgets']} widgets, {dashboard_result['time_series_points']} time series points")