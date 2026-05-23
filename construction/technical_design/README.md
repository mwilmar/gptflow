# Technical Design — GPTFlow

## Project Structure (Clean Architecture)

```
gptflow/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory
│   ├── config.py                   # Settings (pydantic-settings)
│   ├── dependencies.py             # DI container
│   │
│   ├── identity/                   # Identity Bounded Context
│   │   ├── router.py              # /api/auth/*, /api/users/*
│   │   ├── schemas.py            # Pydantic request/response
│   │   ├── service.py            # Business logic
│   │   ├── repository.py         # DB access
│   │   └── models.py             # SQLAlchemy models
│   │
│   ├── content/                    # Content Bounded Context
│   │   ├── router.py             # /api/content/*
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── generation_service.py  # AI generation logic
│   │   ├── approval_service.py    # Approval workflow
│   │   ├── repository.py
│   │   └── models.py
│   │
│   ├── publishing/                 # Publishing Bounded Context
│   │   ├── router.py             # /api/schedule/*
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── publisher.py          # Instagram API client
│   │   ├── repository.py
│   │   ├── models.py
│   │   └── tasks.py              # Celery tasks
│   │
│   ├── intelligence/               # Intelligence Bounded Context
│   │   ├── router.py             # /api/analytics/*, /api/recommendations/*
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── recommendation_service.py
│   │   ├── repository.py
│   │   ├── models.py
│   │   └── tasks.py              # Celery tasks
│   │
│   ├── shared/                     # Cross-cutting concerns
│   │   ├── database.py           # DB session factory
│   │   ├── security.py           # JWT, hashing, encryption
│   │   ├── openai_client.py      # OpenAI wrapper
│   │   ├── instagram_client.py   # Instagram Graph API wrapper
│   │   ├── notifications.py      # Email + in-app
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── middleware.py         # Logging, CORS, rate limit
│   │
│   └── worker/                     # Celery configuration
│       ├── celery_app.py
│       ├── beat_schedule.py
│       └── tasks.py
│
├── migrations/                     # Alembic migrations
│   ├── alembic.ini
│   └── versions/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── frontend/                       # React app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/             # API client
│   │   ├── store/                # State management
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
│
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Python framework | FastAPI | Async, type-safe, auto-docs |
| ORM | SQLAlchemy 2.0 (async) | Mature, async support |
| Database | PostgreSQL + asyncpg | Reliable, JSON support |
| Auth | JWT (python-jose) | Stateless, scalable |
| AI (primary) | Groq API (Llama 3.3 70B) | Free, fast (~300 tok/s) |
| AI (fallback) | OpenAI GPT-4o-mini | High quality, reliable JSON |
| AI mode | Hybrid (Groq first → OpenAI fallback) | Cost-effective + reliable |
| Password hashing | passlib + bcrypt | Industry standard |
| Validation | Pydantic v2 | Fast, integrated with FastAPI |
| Frontend | Vanilla HTML/CSS/JS SPA | Zero build step, fast iteration |
| UI theme | Dark mode (Instagram-like) | Modern, matches IG aesthetic |
| Config | pydantic-settings + .env | Simple, secure |
| Deployment | localhost (uvicorn --reload) | MVP/development phase |

## API Design Principles

1. RESTful resource naming (`/api/content`, `/api/schedule`)
2. Consistent response envelope: `{"data": ..., "meta": ...}`
3. Pagination: `?page=1&size=20`
4. Filtering: `?status=draft&type=carousel`
5. Error format: `{"error": {"code": "...", "message": "..."}}`
6. Versioning: `/api/v1/...` (future-proof)

## Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_name: str = "GPTFlow"
    debug: bool = False
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Auth
    jwt_secret: str
    jwt_expire_minutes: int = 15
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    # Instagram
    ig_app_id: str
    ig_app_secret: str
    
    class Config:
        env_file = ".env"
```

## Error Handling Strategy

```python
# Hierarchy
AppException
├── AuthenticationError (401)
├── AuthorizationError (403)
├── NotFoundError (404)
├── ValidationError (422)
├── ExternalServiceError (502)
│   ├── OpenAIError
│   └── InstagramAPIError
└── InternalError (500)
```

## Async Pattern

```python
# All I/O operations are async
async def generate_content(self, request: GenerationRequest) -> Content:
    # Async OpenAI call
    result = await self.openai_client.generate(prompt)
    # Async DB write
    content = await self.repository.create(result)
    return content
```
