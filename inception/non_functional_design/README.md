# Non-Functional Design — GPTFlow

## Performance Design

### Response Time Targets
| Operation | Target | Strategy |
|-----------|--------|----------|
| Page load | < 2s | CDN, code splitting, lazy load |
| API (CRUD) | < 500ms | DB indexing, connection pooling |
| AI generation | < 15s | Streaming response, async |
| Scheduler check | < 1s | Indexed queries, batch processing |
| Analytics fetch | < 5s | Background job, cached results |

### Caching Strategy
```
Layer 1: Browser cache (static assets, 1 day)
Layer 2: Redis cache (API responses, 5 min)
Layer 3: DB query cache (analytics aggregates, 1 hour)
```

## Scalability Design

### Horizontal Scaling
```
                    ┌─── API Server 1 ───┐
Load Balancer ──────┼─── API Server 2 ───┼──── PostgreSQL (primary)
                    └─── API Server 3 ───┘         │
                                                   └── Read Replica
Celery Workers: auto-scale 2-10 based on queue depth
```

### Capacity Planning
| Resource | MVP | Growth | Scale |
|----------|-----|--------|-------|
| API servers | 1 | 2 | 3+ (auto) |
| Celery workers | 2 | 4 | 2-10 (auto) |
| PostgreSQL | 1 (4GB) | 1 (8GB) + replica | Cluster |
| Redis | 1 (1GB) | 1 (2GB) | Cluster |

## Security Design

### Authentication & Authorization
```
Client → JWT Access Token (15 min) → API
         JWT Refresh Token (7 days) → /auth/refresh
         
RBAC Matrix:
┌──────────────┬───────┬─────────┬─────────┐
│ Resource     │ Admin │ Manager │ Creator │
├──────────────┼───────┼─────────┼─────────┤
│ Users        │ CRUD  │ Read    │ -       │
│ Accounts     │ CRUD  │ Read    │ Read    │
│ Content      │ CRUD  │ R+Approve│ CRUD own│
│ Schedule     │ CRUD  │ Read    │ CRU own │
│ Analytics    │ Full  │ Full    │ Own     │
│ Settings     │ Full  │ -       │ -       │
└──────────────┴───────┴─────────┴─────────┘
```

### Data Protection
- Passwords: bcrypt (cost 12)
- API keys: AES-256 encrypted at rest
- Instagram tokens: encrypted + rotated
- PII: minimal collection, encrypted
- Logs: no sensitive data in logs

### API Security
- Rate limiting: 100 req/min per user, 1000 req/min global
- Input validation: Pydantic schemas
- SQL injection: SQLAlchemy ORM (parameterized)
- XSS: React auto-escaping + CSP headers
- CORS: whitelist origins only

## Reliability Design

### Retry Strategy
```python
# Exponential backoff for Instagram API
retry_delays = [30s, 120s, 300s]  # 30s, 2min, 5min
max_retries = 3
```

### Circuit Breaker
```
Instagram API: trip after 5 failures in 60s, reset after 300s
OpenAI API: trip after 3 failures in 30s, reset after 120s
```

### Graceful Degradation
| Failure | Fallback |
|---------|----------|
| OpenAI down | Queue request, retry later, notify user |
| Instagram API down | Keep in scheduled, retry next cycle |
| Redis down | Direct DB queries (slower) |
| Celery down | Manual posting alert to admin |

## Observability Design

### Logging
```json
{
  "timestamp": "2026-05-23T12:00:00Z",
  "level": "INFO",
  "service": "publisher",
  "trace_id": "abc-123",
  "event": "post_published",
  "account_id": "uuid",
  "post_id": "uuid",
  "ig_post_id": "17890...",
  "duration_ms": 2340
}
```

### Metrics (Prometheus)
- `gptflow_api_requests_total{method, endpoint, status}`
- `gptflow_ai_generation_duration_seconds`
- `gptflow_posts_published_total{status}`
- `gptflow_scheduler_queue_depth`
- `gptflow_instagram_api_errors_total`

### Alerting Rules
| Alert | Condition | Severity |
|-------|-----------|----------|
| API down | 0 successful requests in 2 min | Critical |
| High error rate | > 5% 5xx in 5 min | High |
| Scheduler stuck | Queue depth > 50 for 10 min | High |
| Post failed | 3 consecutive failures | Medium |
| OpenAI budget | > 80% monthly budget | Low |

## Deployment Design

### Container Architecture
```yaml
services:
  api:        # FastAPI (2+ replicas)
  worker:     # Celery worker (2-10 auto)
  beat:       # Celery beat (1 only)
  redis:      # Cache + message broker
  postgres:   # Primary database
  nginx:      # Reverse proxy + static
  prometheus: # Metrics collection
  grafana:    # Dashboard
```

### CI/CD Pipeline
```
Push → Lint → Test → Build Image → Push Registry → Deploy Staging → E2E Test → Deploy Prod
```
