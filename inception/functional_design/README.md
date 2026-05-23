# Functional Design — GPTFlow

## FD-01: AI Content Generation Engine

### Input Schema
```json
{
  "topic": "Public Speaking untuk Pemula",
  "audience": "Mahasiswa 18-25 tahun",
  "tone": "casual_edukatif",
  "content_type": "carousel",
  "language": "id",
  "account_id": "uuid",
  "additional_context": "Fokus tips praktis"
}
```

### Output Schema (Carousel)
```json
{
  "title": "5 Tips Public Speaking yang Bikin Kamu PD!",
  "hook": "90% orang takut ngomong di depan umum. Kamu salah satunya?",
  "slides": [
    {"slide_number": 1, "heading": "Kenali Audiensmu", "body": "..."},
    {"slide_number": 2, "heading": "Latihan di Depan Cermin", "body": "..."}
  ],
  "cta": "Save post ini & tag teman yang butuh! 🎯",
  "hashtags": ["#publicspeaking", "#tipskuliah", "#mahasiswa"],
  "caption": "Full caption text here..."
}
```

### Processing Steps
1. Validate input
2. Build prompt with context (audience, tone, type)
3. Call OpenAI API (GPT-4o-mini)
4. Parse structured response
5. Validate output (length, format)
6. Return to user

## FD-02: Scheduler Engine

### Scheduling Rules
- Minimum 15 menit dari sekarang
- Maximum 90 hari ke depan
- Timezone: WIB (UTC+7) default, configurable
- Conflict check: max 3 posts/day per account
- Optimal time suggestion dari AI

### Execution Flow
```
Celery Beat (every 60s)
  → Query: scheduled_at <= now() AND status = 'scheduled'
  → For each: dispatch to Celery worker
  → Worker: call Instagram Graph API
  → Update status + log result
```

## FD-03: Instagram Graph API Integration

### Required Permissions
- `instagram_basic`
- `instagram_content_publish`
- `instagram_manage_insights`
- `pages_show_list`
- `pages_read_engagement`

### Posting Flow (Single Image)
```
1. POST /v18.0/{ig-user-id}/media
   Body: { image_url, caption }
   Response: { creation_id }

2. POST /v18.0/{ig-user-id}/media_publish
   Body: { creation_id }
   Response: { id: ig_post_id }
```

### Posting Flow (Carousel)
```
1. POST /media (per item, is_carousel_item=true) → item_ids[]
2. POST /media (carousel_container, children=item_ids)→ creation_id
3. POST /media_publish (creation_id) → ig_post_id
```

### Insights Fetch
```
GET /v18.0/{media-id}/insights
  ?metric=engagement,impressions,reach,saved,shares
```

## FD-04: Approval Workflow

### States & Transitions
| From | Action | To | Actor | Side Effect |
|------|--------|----|-------|-------------|
| draft | submit | pending_approval | creator | Notify manager |
| pending_approval | approve | approved | manager | Notify creator |
| pending_approval | reject | rejected | manager | Notify creator + notes |
| rejected | edit+resubmit | pending_approval | creator | Notify manager |
| approved | schedule | scheduled | creator/system | Add to queue |

### Notification Triggers
- Submit → Email + in-app to all managers of account
- Approve/Reject → Email + in-app to creator
- Post failed → Email + in-app to admin

## FD-05: Analytics Dashboard

### Metrics Collected
| Metric | Source | Frequency |
|--------|--------|-----------|
| Likes | IG Insights API | Every 6h |
| Comments | IG Insights API | Every 6h |
| Shares | IG Insights API | Every 6h |
| Saves | IG Insights API | Every 6h |
| Reach | IG Insights API | Every 6h |
| Impressions | IG Insights API | Every 6h |
| Profile visits | IG Insights API | Daily |
| Follower count | IG Basic API | Daily |

### Calculated Metrics
- Engagement Rate = (likes + comments + shares + saves) / reach × 100
- Growth Rate = (followers_today - followers_7d_ago) / followers_7d_ago × 100
- Best posting time = time slot with highest avg engagement

## FD-06: AI Recommendation Engine

### Input
- Last 30 days of posted content + engagement metrics
- Account niche/category
- Audience demographics

### Output
```json
{
  "recommended_topics": ["Topic A", "Topic B", "Topic C"],
  "recommended_format": "carousel",
  "recommended_time": "18:00 WIB",
  "reasoning": "Carousel posts mendapat 3x lebih banyak saves...",
  "trending_hashtags": ["#hash1", "#hash2"]
}
```

### Learning Loop
```
Post → Metrics → Pattern Analysis → Update Recommendation Model → Better Posts
```
