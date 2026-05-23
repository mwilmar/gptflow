# Logical Design — GPTFlow

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                     React SPA (Vite + TypeScript)                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ REST API (HTTPS)
┌────────────────────────────────▼────────────────────────────────────────┐
│                           API GATEWAY                                    │
│                    Nginx (rate limit, CORS, SSL)                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                         BACKEND (FastAPI)                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ Identity │  │ Content  │  │Publishing│  │   Intelligence       │   │
│  │  Module  │  │  Module  │  │  Module  │  │      Module          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘   │
│       │              │              │                    │               │
│  ┌────▼──────────────▼──────────────▼────────────────────▼───────────┐  │
│  │                    Service Layer                                    │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                    Repository Layer (SQLAlchemy)                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌────────▼───────┐  ┌───────────▼──────────┐  ┌────────▼────────┐
│  PostgreSQL    │  │       Redis           │  │  External APIs  │
│  (persistent)  │  │  (cache + broker)     │  │  • OpenAI       │
└────────────────┘  └───────────┬──────────┘  │  • Instagram    │
                                │              │  • Facebook     │
                    ┌───────────▼──────────┐  └─────────────────┘
                    │   Celery Workers      │
                    │  • Scheduler          │
                    │  • Publisher          │
                    │  • Analytics fetcher  │
                    └──────────────────────┘
```

## Module Relationships

```
┌──────────┐         ┌──────────┐
│ Identity │◀────────│ Content  │  Content needs user/account info
└──────────┘         └────┬─────┘
                          │
                          │ approved content
                          ▼
                    ┌──────────┐
                    │Publishing│  Publishing executes scheduled posts
                    └────┬─────┘
                         │
                         │ post metrics trigger
                         ▼
                  ┌──────────────┐
                  │Intelligence  │  Intelligence analyzes & recommends
                  └──────┬───────┘
                         │
                         │ recommendations
                         ▼
                    ┌──────────┐
                    │ Content  │  Feeds back into content generation
                    └──────────┘
```

## Layer Architecture (per Module)

```
┌─────────────────────────────────────┐
│         Router (API endpoints)       │  ← HTTP request/response
├─────────────────────────────────────┤
│         Schema (Pydantic models)     │  ← Validation & serialization
├─────────────────────────────────────┤
│         Service (Business logic)     │  ← Orchestration & rules
├─────────────────────────────────────┤
│         Repository (Data access)     │  ← DB queries
├─────────────────────────────────────┤
│         Model (SQLAlchemy ORM)       │  ← DB schema mapping
└─────────────────────────────────────┘
```

## Data Flow: Content Generation

```
1. User → POST /api/content/generate
2. Router → validates input (Pydantic schema)
3. Service → builds prompt from template + user input
4. Service → calls OpenAI API (async)
5. Service → parses JSON response
6. Service → creates Content entity (status=draft)
7. Repository → saves to PostgreSQL
8. Router → returns generated content to user
```

## Data Flow: Auto Posting

```
1. Celery Beat → triggers check every 60s
2. Scheduler Worker → queries posts WHERE scheduled_at <= now()
3. For each post:
   a. Publisher Service → fetches Instagram access token
   b. Publisher Service → calls Instagram Graph API
   c. Success → update status=published, save ig_post_id
   d. Failure → increment retry_count, schedule retry
   e. Max retries → status=failed, emit PostFailed event
4. Notification Service → alerts on failure
```

## Data Flow: Analytics

```
1. Celery Beat → triggers every 6 hours
2. Analytics Worker → fetches all posts (last 7 days, status=published)
3. For each post:
   a. Calls Instagram Insights API
   b. Stores metrics in PostMetric table
4. Daily: Recommendation Worker
   a. Aggregates metrics (last 30 days)
   b. Calls OpenAI with analytics data
   c. Stores recommendations
   d. Updates dashboard cache
```

## Integration Points

| System | Protocol | Auth | Rate Limit |
|--------|----------|------|------------|
| OpenAI API | HTTPS REST | Bearer token | 500 RPM (tier 1) |
| Instagram Graph API | HTTPS REST | OAuth 2.0 | 200 calls/hour/user |
| Facebook Login | OAuth 2.0 | App ID + Secret | - |
| Redis | TCP | Password | - |
| PostgreSQL | TCP | User/Pass + SSL | Connection pool (20) |
| n8n (future) | Webhook | API key | - |
