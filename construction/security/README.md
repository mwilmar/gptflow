# Security — GPTFlow

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│ L1: Network     │ TLS 1.3, CORS whitelist, rate limiting    │
│ L2: Auth        │ JWT + refresh token, bcrypt passwords     │
│ L3: Authorization│ RBAC, resource ownership validation      │
│ L4: Data        │ AES-256 encryption at rest, input sanitize│
│ L5: API Keys    │ Encrypted vault, rotation policy          │
│ L6: Monitoring  │ Audit log, anomaly detection              │
└─────────────────────────────────────────────────────────────┘
```

## Authentication
- JWT access token: 15 min expiry, RS256 signed
- Refresh token: 7 days, stored hashed in DB, single-use
- Password: bcrypt cost 12, min 8 chars
- Rate limit login: 5 attempts/15 min per IP

## Authorization (RBAC)
```python
PERMISSIONS = {
    "admin": ["*"],
    "manager": ["content.read", "content.approve", "analytics.read", "schedule.read"],
    "creator": ["content.create", "content.read_own", "content.edit_own", "schedule.create_own"],
}
```

## Data Encryption
| Data | Method | Key Storage |
|------|--------|-------------|
| Instagram tokens | AES-256-GCM | Environment variable |
| OpenAI API key | Environment variable | Docker secrets / K8s secrets |
| User passwords | bcrypt (one-way) | N/A |
| DB connection | TLS | Certificate |

## API Security Checklist
- [x] Input validation (Pydantic strict mode)
- [x] SQL injection prevention (SQLAlchemy ORM)
- [x] XSS prevention (React auto-escape + CSP)
- [x] CSRF protection (SameSite cookies + token)
- [x] Rate limiting (100 req/min/user)
- [x] Request size limit (10MB max)
- [x] Dependency scanning (pip-audit, npm audit)
- [x] Secrets never in logs
- [x] HTTPS only (HSTS header)
