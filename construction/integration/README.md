# Integration — GPTFlow

## Integration Map

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   OpenAI     │         │  Instagram   │         │   Facebook   │
│   API        │         │  Graph API   │         │   Login      │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ Content Generation     │ Publish + Insights     │ OAuth 2.0
       │                        │                        │
┌──────▼────────────────────────▼────────────────────────▼───────┐
│                         GPTFlow Backend                          │
└──────▲────────────────────────▲────────────────────────────────┘
       │                        │
┌──────┴───────┐         ┌──────┴───────┐
│   Groq API   │         │   Unsplash   │
│  (primary)   │         │  (images)    │
└──────────────┘         └──────────────┘
```

## 5. Unsplash Integration (v1.1.0)

### Image Search
```python
GET https://api.unsplash.com/search/photos
  ?query={topic_keyword}
  &per_page=4
  &orientation=squarish
Headers: Authorization: Client-ID {access_key}
```

### File Upload
- Endpoint: `POST /api/upload`
- Storage: `static/uploads/{uuid}_{filename}`
- Served via FastAPI StaticFiles mount

### Image Flow
```
Generate content → Auto-search Unsplash (by topic) → User picks image OR uploads
→ PUT /api/content/{id}/image → Saved in DB → Shown in IG preview
```

## 1. OpenAI Integration

### Client Wrapper
```python
class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, messages: list[dict], **kwargs) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1500),
        )
        return json.loads(response.choices[0].message.content)
```

### Error Handling
| Error | Action |
|-------|--------|
| 429 Rate Limit | Retry with exponential backoff |
| 500 Server Error | Retry 2x, then fail gracefully |
| Invalid JSON response | Retry 1x with stricter prompt |
| Token limit exceeded | Truncate input, retry |

## 2. Instagram Graph API Integration

### OAuth Flow
```
1. User clicks "Connect Instagram"
2. Redirect to: https://www.facebook.com/v18.0/dialog/oauth
   ?client_id={app_id}
   &redirect_uri={callback_url}
   &scope=instagram_basic,instagram_content_publish,instagram_manage_insights,pages_show_list
3. User authorizes
4. Callback receives code
5. Exchange code for access_token
6. Get long-lived token (60 days)
7. Store encrypted token
```

### Publishing Client
```python
class InstagramPublisher:
    BASE_URL = "https://graph.facebook.com/v18.0"

    async def publish_single(self, account: IGAccount, caption: str, image_url: str) -> str:
        # Step 1: Create media container
        container = await self._create_container(account.ig_user_id, {
            "image_url": image_url,
            "caption": caption,
            "access_token": account.decrypted_token
        })
        # Step 2: Publish
        result = await self._publish(account.ig_user_id, container["id"], account.decrypted_token)
        return result["id"]

    async def publish_carousel(self, account: IGAccount, items: list, caption: str) -> str:
        # Step 1: Create item containers
        item_ids = []
        for item in items:
            container = await self._create_container(account.ig_user_id, {
                "image_url": item["url"],
                "is_carousel_item": True,
                "access_token": account.decrypted_token
            })
            item_ids.append(container["id"])
        # Step 2: Create carousel container
        carousel = await self._create_container(account.ig_user_id, {
            "media_type": "CAROUSEL",
            "children": ",".join(item_ids),
            "caption": caption,
            "access_token": account.decrypted_token
        })
        # Step 3: Publish
        result = await self._publish(account.ig_user_id, carousel["id"], account.decrypted_token)
        return result["id"]
```

### Insights Client
```python
class InstagramInsights:
    async def fetch_post_metrics(self, ig_post_id: str, token: str) -> dict:
        url = f"{self.BASE_URL}/{ig_post_id}/insights"
        params = {
            "metric": "engagement,impressions,reach,saved,shares",
            "access_token": token
        }
        response = await self._get(url, params)
        return self._parse_metrics(response)
```

## 3. Facebook Login Integration

### App Configuration
- App Type: Business
- Products: Facebook Login, Instagram Graph API
- Permissions: instagram_basic, instagram_content_publish, instagram_manage_insights
- Valid OAuth Redirect URIs: `https://app.gptflow.com/api/v1/accounts/callback`

### Token Management
```python
class TokenManager:
    async def exchange_short_token(self, short_token: str) -> str:
        """Exchange short-lived token (1h) for long-lived (60 days)"""
        response = await self._get("/oauth/access_token", {
            "grant_type": "fb_exchange_token",
            "client_id": settings.ig_app_id,
            "client_secret": settings.ig_app_secret,
            "fb_exchange_token": short_token
        })
        return response["access_token"]

    async def refresh_token(self, token: str) -> str:
        """Refresh before expiry (called by cron)"""
        response = await self._get("/oauth/access_token", {
            "grant_type": "fb_exchange_token",
            "client_id": settings.ig_app_id,
            "client_secret": settings.ig_app_secret,
            "fb_exchange_token": token
        })
        return response["access_token"]
```

## 4. n8n Webhook Integration

### Outgoing Webhooks (GPTFlow → n8n)
```python
class WebhookDispatcher:
    async def dispatch(self, event: str, payload: dict):
        webhooks = await self.get_registered_webhooks(event)
        for webhook in webhooks:
            await httpx.post(webhook.url, json={
                "event": event,
                "timestamp": now().isoformat(),
                "data": payload
            }, headers={"X-Webhook-Secret": webhook.secret})
```

### Events Emitted
| Event | Trigger | Payload |
|-------|---------|---------|
| content.submitted | Creator submits for approval | content_id, topic, creator |
| content.approved | Manager approves | content_id, approver |
| post.published | Successfully posted | post_id, ig_post_id |
| post.failed | All retries exhausted | post_id, error |
| analytics.fetched | Metrics updated | account_id, summary |
