# Maintenance — GPTFlow Operation

## Scheduled Maintenance

| Task | Frequency | Owner | Downtime |
|------|-----------|-------|----------|
| Security patches (OS/deps) | Weekly | DevOps | Zero (rolling) |
| Database vacuum/analyze | Weekly (auto) | PostgreSQL | Zero |
| Log rotation/cleanup | Daily (auto) | System | Zero |
| SSL certificate renewal | Auto (Let's Encrypt) | Certbot | Zero |
| Dependency updates | Monthly | Dev team | Staging first |
| Database backup verification | Monthly | DevOps | Zero |
| Load testing | Quarterly | QA | Staging only |
| Disaster recovery drill | Quarterly | Team | Staging only |

## Instagram Token Maintenance

```
Token lifecycle: 60 days
Auto-refresh: daily cron (3 AM) refreshes tokens expiring in < 14 days
Alert: if token expires in < 7 days and refresh fails
```

## Database Maintenance

```sql
-- Weekly (automated via pg_cron)
VACUUM ANALYZE contents;
VACUUM ANALYZE post_metrics;
VACUUM ANALYZE scheduled_posts;

-- Monthly: check index bloat
SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes WHERE idx_scan = 0;
```

## Dependency Update Policy
1. Security patches: apply within 48 hours
2. Minor versions: monthly batch update
3. Major versions: evaluate, test on staging, schedule
4. Pin all versions in requirements.txt (exact)

## Health Checks (automated)
- Every 1 min: API `/health` endpoint
- Every 5 min: Celery worker heartbeat
- Every 15 min: Instagram API connectivity
- Every 1 hour: OpenAI API connectivity
