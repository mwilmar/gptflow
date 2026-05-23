# Business Flow — GPTFlow

## Main Workflow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  INPUT   │───▶│GENERATE  │───▶│ APPROVE  │───▶│ SCHEDULE │───▶│  POST    │
│  Topic   │    │AI Content│    │ Manager  │    │ Calendar │    │Instagram │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                                       │
┌──────────┐    ┌──────────┐                                           │
│RECOMMEND │◀───│ ANALYZE  │◀──────────────────────────────────────────┘
│Next Topic│    │Engagement│
└──────────┘    └──────────┘
```

## Flow 1: Content Generation

```
User Input                    AI Processing                Output
─────────────────────────────────────────────────────────────────
Topic: "Public Speaking"  →   1. Analyze topic         →  Caption
Audience: "Mahasiswa"     →   2. Research trends       →  Hook
Style: "Casual edukatif"  →   3. Generate content      →  CTA
Type: "Carousel"          →   4. Add hashtags          →  Hashtags
                              5. Format per-slide      →  Slides[1..10]
```

## Flow 2: Approval Workflow

```
Creator                    System                     Manager
───────                    ──────                     ───────
Submit draft          →    Status: pending       →    Notification
                           Queue approval             Review content
                                                     │
                      ←    Status: approved     ←    Approve ✓
                           OR                        OR
                      ←    Status: rejected     ←    Reject ✗ + notes
                           Notify creator
```

## Flow 3: Publishing Pipeline

```
Scheduler Check (every 1 min)
│
├─ Find posts WHERE status=approved AND scheduled_at <= NOW()
│
├─ For each post:
│   ├─ Fetch Instagram access token
│   ├─ Upload media container (if image)
│   ├─ Publish via Graph API
│   ├─ Success → status=posted, save ig_post_id
│   └─ Failure → retry (max 3x, exponential backoff)
│       └─ All retries failed → status=failed, notify admin
│
└─ Log all operations
```

## Flow 4: Analytics & Learning

```
Cron Job (every 6 hours)
│
├─ For each posted content (last 7 days):
│   ├─ Fetch metrics from Instagram Graph API
│   ├─ Store: likes, comments, shares, saves, reach
│   └─ Calculate engagement rate
│
├─ AI Analysis (daily):
│   ├─ Identify top performing content patterns
│   ├─ Analyze: topic, format, time, hashtags
│   └─ Generate recommendations
│
└─ Output: AI Recommendation for next content
```

## Flow 5: Multi-Account Connection

```
Admin                      System                    Instagram
─────                      ──────                    ─────────
Add account           →    Redirect OAuth       →    Facebook Login
                      ←    Receive token         ←    Auth callback
                           Store encrypted token
                           Fetch IG Business ID
                           Verify permissions
                      ←    Account connected ✓
```

## State Machine: Content Lifecycle

```
         ┌─────────┐
         │  DRAFT  │
         └────┬────┘
              │ submit
         ┌────▼────┐
    ┌────│ PENDING │────┐
    │    └─────────┘    │
    │ reject            │ approve
┌───▼───┐         ┌────▼─────┐
│REJECTED│         │ APPROVED │
└───┬───┘         └────┬─────┘
    │ edit              │ schedule
    │              ┌────▼─────┐
    └──→ DRAFT     │SCHEDULED │
                   └────┬─────┘
                        │ publish
                   ┌────▼─────┐
                   │  POSTED  │
                   └────┬─────┘
                        │ fetch metrics
                   ┌────▼─────┐
                   │ ANALYZED │
                   └──────────┘
```
