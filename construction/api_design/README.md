# API Design — GPTFlow

## Base URL
```
Production: https://api.gptflow.app/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication
All endpoints (except auth) require: `Authorization: Bearer <jwt_token>`

## Response Format
```json
{
  "data": { ... },
  "meta": { "page": 1, "size": 20, "total": 100 }
}
```

## Error Format
```json
{
  "error": { "code": "CONTENT_NOT_FOUND", "message": "Content with id X not found" }
}
```

---

## Auth Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login, returns JWT |
| POST | /auth/refresh | Refresh access token |
| POST | /auth/logout | Invalidate refresh token |

### POST /auth/login
```json
// Request
{ "email": "user@example.com", "password": "secret" }

// Response 200
{ "data": { "access_token": "eyJ...", "refresh_token": "eyJ...", "expires_in": 900 } }
```

---

## Content Endpoints

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | /content/generate | AI generate content | creator+ |
| GET | /content | List contents (filtered) | creator+ |
| GET | /content/{id} | Get content detail | creator+ |
| PUT | /content/{id} | Update content | owner |
| DELETE | /content/{id} | Delete draft | owner |
| POST | /content/{id}/submit | Submit for approval | owner |
| POST | /content/{id}/approve | Approve content | manager+ |
| POST | /content/{id}/reject | Reject content | manager+ |

### POST /content/generate
```json
// Request
{
  "account_id": "uuid",
  "topic": "Public Speaking untuk Pemula",
  "audience": "Mahasiswa 18-25 tahun",
  "tone": "casual_edukatif",
  "content_type": "carousel",
  "additional_context": "Fokus tips praktis, max 7 slide"
}

// Response 200
{
  "data": {
    "id": "uuid",
    "content_type": "carousel",
    "status": "draft",
    "hook": "90% orang takut ngomong di depan umum...",
    "caption": "...",
    "slides": [
      {"number": 1, "heading": "...", "body": "..."}
    ],
    "hashtags": ["#publicspeaking", "..."],
    "cta": "Save & tag teman kamu!"
  }
}
```

### GET /content?status=draft&type=carousel&page=1&size=20
```json
{
  "data": [ { "id": "...", "topic": "...", "status": "...", "content_type": "..." } ],
  "meta": { "page": 1, "size": 20, "total": 45 }
}
```

---

## Schedule Endpoints

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | /schedule | Schedule a post | creator+ |
| GET | /schedule | List scheduled posts | creator+ |
| GET | /schedule/calendar | Calendar view (month) | creator+ |
| PUT | /schedule/{id} | Reschedule | owner |
| DELETE | /schedule/{id} | Cancel scheduled post | owner |

### POST /schedule
```json
// Request
{
  "content_id": "uuid",
  "scheduled_at": "2026-05-25T09:00:00+07:00"
}

// Response 201
{
  "data": {
    "id": "uuid",
    "content_id": "uuid",
    "scheduled_at": "2026-05-25T09:00:00+07:00",
    "status": "queued"
  }
}
```

---

## Analytics Endpoints

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | /analytics/overview | Dashboard metrics | manager+ |
| GET | /analytics/posts | Per-post metrics | creator+ |
| GET | /analytics/posts/{id} | Single post metrics | creator+ |
| GET | /analytics/trends | Engagement trends | manager+ |

### GET /analytics/overview?account_id=uuid&period=30d
```json
{
  "data": {
    "total_posts": 28,
    "avg_engagement_rate": 4.2,
    "total_reach": 15000,
    "follower_growth": 187,
    "top_content_type": "carousel",
    "best_posting_time": "18:00"
  }
}
```

---

## Recommendation Endpoints

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | /recommendations | Get AI recommendations | creator+ |
| POST | /recommendations/generate | Force new recommendation | manager+ |

### GET /recommendations?account_id=uuid
```json
{
  "data": {
    "topics": ["Time Management", "Study Tips", "Career Prep"],
    "recommended_format": "carousel",
    "best_time": "18:00",
    "reasoning": "Carousel posts mendapat 3x saves dibanding feed...",
    "trending_hashtags": ["#studytips", "#mahasiswa2026"],
    "generated_at": "2026-05-23T10:00:00Z"
  }
}
```

---

## Account Endpoints

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | /accounts | List connected accounts | admin |
| POST | /accounts/connect | Start OAuth flow | admin |
| GET | /accounts/callback | OAuth callback | system |
| DELETE | /accounts/{id} | Disconnect account | admin |

---

## User Endpoints

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | /users | List users | admin |
| POST | /users/invite | Invite user | admin |
| PUT | /users/{id}/role | Change role | admin |
| DELETE | /users/{id} | Deactivate user | admin |

---

## Webhook Endpoints (for n8n integration)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /webhooks/content-approved | Trigger on approval |
| POST | /webhooks/post-published | Trigger on publish |
| POST | /webhooks/post-failed | Trigger on failure |
