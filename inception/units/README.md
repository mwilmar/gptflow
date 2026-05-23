# Units — Domain Module Decomposition

## Principle: High Cohesion, Low Coupling

Setiap unit adalah bounded context yang independen, berkomunikasi via well-defined interface.

## Module Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         GPTFlow System                           │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│   Identity  │   Content    │  Publishing  │    Intelligence    │
│   Context   │   Context    │   Context    │      Context       │
├─────────────┼──────────────┼──────────────┼────────────────────┤
│ • Auth      │ • Generation │ • Scheduler  │ • Analytics        │
│ • User      │ • Management │ • Publisher  │ • Recommendation   │
│ • Role      │ • Approval   │ • Calendar   │ • Learning         │
│ • Account   │ • Template   │ • Queue      │ • Trend            │
└─────────────┴──────────────┴──────────────┴────────────────────┘
```

## Unit 1: Identity Context

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| Auth | Login, register, JWT, refresh token | - |
| User | User CRUD, profile | Auth |
| Role | RBAC, permissions | User |
| Account | Instagram account connection, OAuth | Auth |

## Unit 2: Content Context

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| Generation | AI content creation (caption, carousel, reels, story) | Account, OpenAI |
| Management | CRUD content, versioning, status lifecycle | Generation |
| Approval | Workflow approval/reject, notifications | Management, User |
| Template | Content templates, presets | - |

## Unit 3: Publishing Context

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| Scheduler | Schedule posts, manage queue | Content, Account |
| Publisher | Execute posting via Instagram Graph API | Scheduler, Account |
| Calendar | Calendar view, drag-drop reschedule | Scheduler |
| Queue | Job queue (Celery/Redis), retry logic | Publisher |

## Unit 4: Intelligence Context

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| Analytics | Fetch & store engagement metrics | Account, Instagram API |
| Recommendation | AI-powered content suggestions | Analytics, OpenAI |
| Learning | Pattern recognition, model improvement | Analytics |
| Trend | Trending topics, hashtag analysis | OpenAI |

## Cross-Cutting Concerns

| Concern | Implementation |
|---------|---------------|
| Logging | Structured JSON logging (all modules) |
| Monitoring | Health checks, metrics export |
| Security | Input validation, rate limiting, encryption |
| Notification | Email + in-app (approval, failures) |
| Configuration | Environment-based, secrets vault |

## Communication Pattern

```
Identity ←→ Content: User creates content, role determines access
Content ←→ Publishing: Approved content enters scheduler
Publishing ←→ Intelligence: Posted content triggers analytics fetch
Intelligence ←→ Content: Recommendations feed into generation
```
