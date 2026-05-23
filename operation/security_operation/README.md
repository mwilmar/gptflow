# Security Operation — GPTFlow

## Operational Security Tasks

| Task | Frequency | Tool |
|------|-----------|------|
| Dependency vulnerability scan | Daily (CI) | pip-audit, npm audit |
| Container image scan | On build | Trivy |
| Secret rotation (API keys) | Quarterly | Manual + K8s secrets |
| Access review | Monthly | Manual audit |
| Penetration testing | Annually | External vendor |
| SSL certificate check | Daily (auto) | Certbot + monitoring |

## Secret Management

```
Production secrets stored in:
- Kubernetes Secrets (encrypted at rest via etcd encryption)
- Never in code, never in logs, never in error messages

Rotation schedule:
- JWT signing key: every 90 days
- Database password: every 90 days
- OpenAI API key: on compromise only
- Instagram tokens: auto-refresh (60 day lifecycle)
```

## Access Control

| Resource | Who | How |
|----------|-----|-----|
| Production K8s | DevOps only | kubectl + RBAC |
| Production DB | API service account only | Connection string in secrets |
| Grafana | All engineers (read), DevOps (admin) | SSO |
| GitHub repo | All team (write), main branch protected | Branch protection |

## Incident Security Response

```
1. Detect: automated alert or report
2. Contain: revoke compromised credentials immediately
3. Investigate: audit logs, determine scope
4. Remediate: patch vulnerability, rotate secrets
5. Notify: inform affected users if data breach
6. Document: post-mortem with security focus
```

## Audit Logging

All security-relevant events logged:
- Login success/failure
- Role changes
- Account connections/disconnections
- API key access
- Admin actions
