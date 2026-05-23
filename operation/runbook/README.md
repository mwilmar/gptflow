# Runbook — GPTFlow Operation

## RB-01: Restart API Service

```bash
# Check status
kubectl get pods -l app=gptflow-api

# Restart (rolling)
kubectl rollout restart deployment/api

# Verify
kubectl rollout status deployment/api
curl -s https://app.gptflow.app/health | jq .
```

## RB-02: Restart Celery Workers

```bash
# Check worker status
kubectl get pods -l app=gptflow-worker

# Restart
kubectl rollout restart deployment/worker

# Verify queue is being processed
kubectl logs -l app=gptflow-worker --tail=20
```

## RB-03: Clear Stuck Scheduled Posts

```bash
# Connect to DB
kubectl exec -it deploy/api -- python -c "
from app.shared.database import get_session
from app.publishing.models import ScheduledPost

# Find stuck posts (publishing > 10 min)
stuck = session.query(ScheduledPost).filter(
    ScheduledPost.status == 'publishing',
    ScheduledPost.updated_at < now() - interval('10 minutes')
).all()

for post in stuck:
    post.status = 'queued'  # re-queue
    post.retry_count += 1
session.commit()
print(f'Reset {len(stuck)} stuck posts')
"
```

## RB-04: Refresh Instagram Token Manually

```bash
kubectl exec -it deploy/api -- python -c "
from app.identity.service import TokenManager
import asyncio

async def refresh(account_id):
    tm = TokenManager()
    await tm.force_refresh(account_id)
    print('Token refreshed')

asyncio.run(refresh('ACCOUNT_UUID_HERE'))
"
```

## RB-05: Scale Workers for High Load

```bash
# Scale up
kubectl scale deployment/worker --replicas=8

# Monitor queue depth
kubectl exec -it deploy/redis -- redis-cli llen celery

# Scale back down after load
kubectl scale deployment/worker --replicas=2
```

## RB-06: Database Emergency

```bash
# Check connections
kubectl exec -it deploy/postgres -- psql -U gptflow -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
kubectl exec -it deploy/postgres -- psql -U gptflow -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE state = 'idle' AND query_start < now() - interval '30 minutes';
"

# Emergency: read-only mode
kubectl exec -it deploy/api -- python -c "
# Set maintenance mode flag in Redis
import redis
r = redis.from_url('redis://redis:6379/0')
r.set('maintenance_mode', '1')
print('Maintenance mode ON')
"
```

## RB-07: Rollback Deployment

```bash
# View history
kubectl rollout history deployment/api

# Rollback to previous
kubectl rollout undo deployment/api

# Rollback to specific revision
kubectl rollout undo deployment/api --to-revision=3

# Verify
kubectl rollout status deployment/api
```
