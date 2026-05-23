# Incident Management — GPTFlow Operation

## Severity Levels

| Level | Definition | Response Time | Example |
|-------|-----------|---------------|---------|
| SEV-1 | System down, all users affected | 15 min | API completely unresponsive |
| SEV-2 | Major feature broken | 1 hour | Posting fails for all accounts |
| SEV-3 | Minor feature degraded | 4 hours | Analytics fetch delayed |
| SEV-4 | Cosmetic/low impact | Next business day | UI glitch |

## Incident Response Flow

```
1. DETECT    → Alert fires (automated) or user reports
2. TRIAGE    → On-call determines severity
3. MITIGATE  → Immediate action (rollback, restart, scale)
4. RESOLVE   → Fix root cause, deploy patch
5. POSTMORTEM→ Document within 48 hours
```

## On-Call Rotation
- Primary: 1 engineer (weekly rotation)
- Escalation: Team lead → CTO
- Tools: PagerDuty (SEV-1/2), Slack (SEV-3/4)

## Common Incidents & Playbooks

### Instagram API Failure
```
Symptom: Posts failing to publish
Check: curl Instagram API status page
Action: 
  1. Check IG API status (developers.facebook.com/status)
  2. If IG down → pause scheduler, notify users
  3. If our issue → check token expiry, refresh tokens
  4. If rate limit → reduce posting frequency
```

### OpenAI API Timeout
```
Symptom: Content generation hanging/failing
Action:
  1. Check OpenAI status page
  2. If OpenAI down → show "temporarily unavailable" to users
  3. If our issue → check prompt size, reduce max_tokens
  4. Circuit breaker should auto-trip after 3 failures
```

### Database Connection Exhaustion
```
Symptom: 500 errors, "connection pool exhausted"
Action:
  1. Check active connections: SELECT count(*) FROM pg_stat_activity
  2. Kill idle connections: SELECT pg_terminate_backend(pid)
  3. Scale up connection pool or add read replica
  4. Investigate: long-running queries, connection leaks
```

## Post-Mortem Template

```markdown
# Incident: [Title]
- Date: YYYY-MM-DD
- Duration: X hours
- Severity: SEV-X
- Impact: [who/what was affected]

## Timeline
- HH:MM - Alert fired
- HH:MM - On-call acknowledged
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Confirmed resolved

## Root Cause
[What actually broke and why]

## Action Items
- [ ] Fix: [immediate fix]
- [ ] Prevent: [how to prevent recurrence]
- [ ] Detect: [improve detection]
```
