# Workflow Automation — GPTFlow

## Automation Engine: Celery + n8n

### Celery Tasks (Core Automation)

```python
# Beat Schedule
beat_schedule = {
    "check-scheduled-posts": {
        "task": "publishing.tasks.process_scheduled_posts",
        "schedule": 60.0,  # every 60 seconds
    },
    "fetch-analytics": {
        "task": "intelligence.tasks.fetch_post_metrics",
        "schedule": crontab(minute=0, hour="*/6"),  # every 6 hours
    },
    "generate-recommendations": {
        "task": "intelligence.tasks.generate_recommendations",
        "schedule": crontab(minute=0, hour=2),  # daily at 2 AM
    },
    "cleanup-expired-sessions": {
        "task": "identity.tasks.cleanup_sessions",
        "schedule": crontab(minute=0, hour=0),  # daily midnight
    },
    "refresh-ig-tokens": {
        "task": "identity.tasks.refresh_expiring_tokens",
        "schedule": crontab(minute=0, hour=3),  # daily at 3 AM
    },
}
```

### Task: Process Scheduled Posts
```python
@celery_app.task(bind=True, max_retries=3)
def process_scheduled_posts(self):
    posts = get_due_posts()  # status=queued, scheduled_at <= now
    for post in posts:
        try:
            publish_to_instagram.delay(post.id)
        except Exception as e:
            logger.error(f"Failed to dispatch post {post.id}: {e}")

@celery_app.task(bind=True, max_retries=3)
def publish_to_instagram(self, post_id: str):
    try:
        post = get_post(post_id)
        post.status = "publishing"
        result = instagram_client.publish(post)
        post.ig_post_id = result.id
        post.status = "published"
        post.published_at = now()
    except InstagramAPIError as e:
        post.retry_count += 1
        post.last_error = str(e)
        raise self.retry(exc=e, countdown=30 * (2 ** self.request.retries))
```

### n8n Workflows (Extended Automation)

#### Workflow 1: Content Approval Notification
```
Trigger: Webhook (POST /webhooks/content-submitted)
→ Slack/Email notification to manager
→ Wait for approval webhook
→ If approved: trigger schedule suggestion
→ If rejected: notify creator with notes
```

#### Workflow 2: Post-Publish Analytics
```
Trigger: Webhook (POST /webhooks/post-published)
→ Wait 24 hours
→ Fetch engagement metrics
→ If engagement > threshold: celebrate notification
→ If engagement < threshold: suggest improvement
```

#### Workflow 3: Weekly Report
```
Trigger: Cron (Monday 09:00)
→ Fetch weekly analytics
→ Generate AI summary
→ Send report email to manager
→ Store report in system
```

## Automation Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Celery Beat (Scheduler)                    │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Every 1m │ Every 6h │ Daily 2AM│ Daily 3AM│ Daily midnight │
│ Post     │ Fetch    │ AI Reco  │ Token    │ Cleanup        │
│ Check    │ Metrics  │ Generate │ Refresh  │ Sessions       │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────────────────┘
     │          │          │          │
     ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers (2-10)                      │
│  • publish_to_instagram                                      │
│  • fetch_post_metrics                                        │
│  • generate_recommendations                                  │
│  • refresh_ig_token                                          │
│  • send_notification                                         │
└─────────────────────────────────────────────────────────────┘
```
