# Logging — GPTFlow Operation

## Logging Architecture

```
App (structlog) → stdout → Docker → Loki → Grafana (query/view)
```

## Log Format (Structured JSON)

```json
{
  "timestamp": "2026-05-23T12:00:00.123Z",
  "level": "INFO",
  "service": "gptflow-api",
  "module": "publishing.publisher",
  "trace_id": "abc-123-def",
  "user_id": "uuid",
  "event": "post_published",
  "data": {
    "post_id": "uuid",
    "account_id": "uuid",
    "ig_post_id": "17890...",
    "duration_ms": 2340
  }
}
```

## Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| ERROR | Unrecoverable failures | Instagram API 500, DB connection lost |
| WARNING | Recoverable issues | Retry triggered, rate limit approaching |
| INFO | Business events | Post published, content generated, user login |
| DEBUG | Technical detail | API request/response, query execution |

## Sensitive Data Policy
- NEVER log: passwords, tokens, API keys, PII
- MASK: email (u***@domain.com), phone
- OK to log: user_id, post_id, account_id, status codes

## Log Retention
| Environment | Retention | Storage |
|-------------|-----------|---------|
| Development | 1 day | Local stdout |
| Staging | 7 days | Loki |
| Production | 30 days | Loki + S3 archive (90 days) |

## Implementation
```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()
logger.info("post_published", post_id=post.id, ig_post_id=result.id, duration_ms=elapsed)
```
