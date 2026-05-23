# Monitoring — GPTFlow Operation

## Monitoring Stack

```
Application → Prometheus (scrape) → Grafana (visualize) → AlertManager (alert)
```

## Dashboards (Grafana)

### Dashboard 1: System Health
- API request rate & latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- CPU/Memory per pod
- Database connections (active/idle)
- Redis memory usage

### Dashboard 2: Business Metrics
- Content generated per day
- Posts published per day
- Approval queue depth
- Scheduler queue depth
- AI generation latency

### Dashboard 3: External APIs
- OpenAI API latency & error rate
- Instagram API latency & error rate
- Token refresh success rate
- Rate limit remaining

## Alerting Rules

| Alert | Condition | Severity | Channel |
|-------|-----------|----------|---------|
| API Down | 0 requests in 2 min | Critical | PagerDuty + Slack |
| High Error Rate | > 5% 5xx in 5 min | High | Slack |
| Scheduler Stuck | Queue > 50 for 10 min | High | Slack |
| Post Failed | 3 consecutive failures | Medium | Slack |
| DB Connection Pool | > 80% used | Medium | Slack |
| OpenAI Budget | > 80% monthly | Low | Email |
| Token Expiring | < 7 days to expiry | Low | Email |

## Health Check Endpoint

```python
@app.get("/health")
async def health():
    checks = {
        "database": await check_db(),
        "redis": await check_redis(),
        "celery": await check_celery_workers(),
    }
    status = "healthy" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
```

## Uptime Monitoring
- External: UptimeRobot (1 min interval)
- Internal: Prometheus blackbox exporter
- SLA target: 99.5% uptime
