# Architecture — GPTFlow v2.0.0

## System Architecture Diagram

```
                         ┌──────────────┐
                         │   Browser    │
                         │  React SPA   │
                         └──────┬───────┘
                                │ HTTPS
                         ┌──────▼───────┐
                         │    Nginx     │
                         │  (reverse    │
                         │   proxy)     │
                         └──────┬───────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
          ┌──────▼──────┐      │       ┌──────▼──────┐
          │  FastAPI     │      │       │   Static    │
          │  (API)       │      │       │   Assets    │
          │  Port 8010   │      │       │   (React)   │
          └──────┬───────┘      │       └─────────────┘
                 │              │
    ┌────────────┼────────────┐ │
    │            │            │ │
┌───▼───┐  ┌────▼────┐  ┌───▼─▼──┐
│OpenAI │  │Instagram│  │  Redis  │
│  API  │  │Graph API│  │(broker +│
└───────┘  └─────────┘  │ cache)  │
                         └───┬────┘
                             │
                    ┌────────▼────────┐
                    │  Celery Workers  │
                    │  • scheduler    │
                    │  • publisher    │
                    │  • analytics    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   PostgreSQL    │
                    │   (primary DB)  │
                    └─────────────────┘
```

## Deployment Architecture (Docker)

```yaml
# docker-compose.yml
version: "3.8"

services:
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    depends_on: [api, frontend]

  api:
    build: {context: ., dockerfile: docker/Dockerfile.api}
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/gptflow
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on: [postgres, redis]
    deploy: {replicas: 2}

  worker:
    build: {context: ., dockerfile: docker/Dockerfile.worker}
    command: celery -A app.worker.celery_app worker -l info -c 4
    depends_on: [postgres, redis]
    deploy: {replicas: 2}

  beat:
    build: {context: ., dockerfile: docker/Dockerfile.worker}
    command: celery -A app.worker.celery_app beat -l info
    depends_on: [redis]
    deploy: {replicas: 1}

  frontend:
    build: {context: ./frontend, dockerfile: ../docker/Dockerfile.frontend}

  postgres:
    image: postgres:16-alpine
    volumes: [pg_data:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: gptflow
      POSTGRES_USER: gptflow
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    volumes: [redis_data:/data]

  prometheus:
    image: prom/prometheus:latest
    volumes: [./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml]

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]

volumes:
  pg_data:
  redis_data:
```

## Kubernetes Architecture (Production)

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                     │
│                                                          │
│  ┌─── Namespace: gptflow ────────────────────────────┐  │
│  │                                                    │  │
│  │  Ingress (nginx-ingress)                          │  │
│  │       │                                           │  │
│  │  ┌────▼─────┐  ┌──────────┐  ┌──────────────┐   │  │
│  │  │ API Pods │  │ Worker   │  │ Beat Pod     │   │  │
│  │  │ (HPA     │  │ Pods     │  │ (1 replica)  │   │  │
│  │  │  2-10)   │  │ (HPA 2-8)│  └──────────────┘   │  │
│  │  └──────────┘  └──────────┘                       │  │
│  │                                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │  │
│  │  │PostgreSQL│  │  Redis   │  │  Prometheus  │   │  │
│  │  │(StatefulS│  │(StatefulS│  │  + Grafana   │   │  │
│  │  │   et)    │  │   et)    │  └──────────────┘   │  │
│  │  └──────────┘  └──────────┘                       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Secrets: openai-key, ig-credentials, db-password        │
│  ConfigMaps: app-config, nginx-config                    │
└─────────────────────────────────────────────────────────┘
```

## Scalability Strategy

| Component | Strategy | Trigger |
|-----------|----------|---------|
| API | HPA (horizontal pod autoscaler) | CPU > 70% |
| Workers | HPA | Queue depth > 100 |
| PostgreSQL | Read replicas | Read queries > 1000/s |
| Redis | Cluster mode | Memory > 80% |
| Frontend | CDN (CloudFlare) | Static, always |

## Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│           Presentation Layer             │  Routers, Schemas
├─────────────────────────────────────────┤
│           Application Layer              │  Services, Use Cases
├─────────────────────────────────────────┤
│             Domain Layer                 │  Entities, Value Objects, Events
├─────────────────────────────────────────┤
│          Infrastructure Layer            │  Repositories, External APIs
└─────────────────────────────────────────┘

Dependency Rule: Inner layers NEVER depend on outer layers
```
