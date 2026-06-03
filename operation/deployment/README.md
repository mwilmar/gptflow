# Deployment — GPTFlow Operation

## Deployment Environments

| Env | Infra | Trigger | URL |
|-----|-------|---------|-----|
| Dev | Docker Compose (local) | Manual | localhost:8010 |
| Staging | K8s cluster | Push to develop | staging.gptflow.app |
| Production | K8s cluster | Push to main + approval | app.gptflow.app |

## Production Deployment Checklist

- [ ] All tests pass (CI green)
- [ ] Code review approved
- [ ] Database migration tested on staging
- [ ] Environment variables set in K8s secrets
- [ ] Health check endpoints responding
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Load test passed (staging)

## Deployment Steps

```bash
# 1. Build & push image
docker build -t ghcr.io/org/gptflow-api:v1.2.0 -f docker/Dockerfile.api .
docker push ghcr.io/org/gptflow-api:v1.2.0

# 2. Run migrations
kubectl exec -it deploy/api -- alembic upgrade head

# 3. Rolling update
kubectl set image deployment/api api=ghcr.io/org/gptflow-api:v1.2.0
kubectl rollout status deployment/api

# 4. Verify
kubectl get pods -l app=gptflow-api
curl -s https://app.gptflow.app/health
```

## Rollback Procedure

```bash
# Immediate rollback to previous version
kubectl rollout undo deployment/api

# Rollback DB migration if needed
kubectl exec -it deploy/api -- alembic downgrade -1

# Verify rollback
kubectl rollout status deployment/api
```

## Zero-Downtime Strategy
- Rolling update (maxSurge: 1, maxUnavailable: 0)
- Readiness probe: `/health` must return 200
- Liveness probe: `/health` every 30s
- Pre-stop hook: 10s grace period for in-flight requests
