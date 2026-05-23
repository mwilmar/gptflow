# Domain Design — GPTFlow (DDD Approach)

## Strategic Design

### Bounded Contexts

```
┌─────────────────────────────────────────────────────────────┐
│                      GPTFlow Domain                          │
├───────────────┬───────────────┬──────────────┬─────────────┤
│   Identity    │    Content    │  Publishing  │Intelligence │
│   Context     │    Context    │   Context    │  Context    │
│               │               │              │             │
│ • User        │ • Content     │ • Schedule   │ • Metric    │
│ • Role        │ • Generation  │ • Post       │ • Insight   │
│ • Account     │ • Approval    │ • Job        │ • Recommend │
│ • Permission  │ • Template    │ • Calendar   │ • Trend     │
└───────────────┴───────────────┴──────────────┴─────────────┘
```

### Context Map

```
Identity ──[Conformist]──▶ Content (user creates content)
Content ──[Customer-Supplier]──▶ Publishing (approved → scheduled)
Publishing ──[Published Language]──▶ Intelligence (post metrics)
Intelligence ──[Open Host]──▶ Content (recommendations)
```

## Tactical Design

### Identity Context — Entities & Value Objects

```python
# Aggregate Root
class User:
    id: UserId
    email: Email                    # Value Object
    password_hash: str
    name: str
    role: Role                      # Value Object (enum)
    accounts: List[AccountAccess]
    created_at: datetime

# Value Objects
class Email:
    value: str  # validated format

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CREATOR = "creator"

# Entity
class InstagramAccount:
    id: AccountId
    ig_user_id: str
    ig_username: str
    access_token: EncryptedToken    # Value Object
    token_expires_at: datetime
    fb_page_id: str
    owner_id: UserId
```

### Content Context — Entities & Value Objects

```python
# Aggregate Root
class Content:
    id: ContentId
    account_id: AccountId
    creator_id: UserId
    content_type: ContentType       # Value Object (enum)
    status: ContentStatus           # Value Object (enum)
    topic: str
    audience: str
    tone: Tone                      # Value Object
    generated_result: GeneratedContent  # Value Object
    approval: Approval              # Entity
    versions: List[ContentVersion]
    created_at: datetime
    updated_at: datetime

# Value Objects
class ContentType(Enum):
    FEED = "feed"
    CAROUSEL = "carousel"
    REELS = "reels"
    STORY = "story"

class ContentStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"

class GeneratedContent:
    hook: str
    body: str
    cta: str
    hashtags: List[str]
    caption: str
    slides: Optional[List[Slide]]   # for carousel
    script: Optional[ReelsScript]   # for reels

# Entity
class Approval:
    id: ApprovalId
    content_id: ContentId
    reviewer_id: Optional[UserId]
    status: ApprovalStatus
    notes: Optional[str]
    reviewed_at: Optional[datetime]
```

### Publishing Context — Entities

```python
# Aggregate Root
class ScheduledPost:
    id: PostId
    content_id: ContentId
    account_id: AccountId
    scheduled_at: datetime
    timezone: str
    status: PostStatus
    ig_post_id: Optional[str]       # after published
    retry_count: int
    last_error: Optional[str]
    published_at: Optional[datetime]

class PostStatus(Enum):
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### Intelligence Context — Entities

```python
# Aggregate Root
class PostMetric:
    id: MetricId
    post_id: PostId
    ig_post_id: str
    likes: int
    comments: int
    shares: int
    saves: int
    reach: int
    impressions: int
    engagement_rate: float
    fetched_at: datetime

# Entity
class Recommendation:
    id: RecommendationId
    account_id: AccountId
    topics: List[str]
    format: ContentType
    best_time: str
    reasoning: str
    confidence: float
    generated_at: datetime
```

## Domain Events

| Event | Published By | Consumed By |
|-------|-------------|-------------|
| ContentCreated | Content | - |
| ContentSubmitted | Content | Notification |
| ContentApproved | Content | Publishing |
| ContentRejected | Content | Notification |
| PostScheduled | Publishing | Calendar |
| PostPublished | Publishing | Intelligence |
| PostFailed | Publishing | Notification |
| MetricsFetched | Intelligence | Recommendation |
| RecommendationGenerated | Intelligence | Dashboard |

## Domain Services

```python
class ContentGenerationService:
    """Orchestrates AI content generation"""
    def generate(self, request: GenerationRequest) -> GeneratedContent

class PublishingService:
    """Orchestrates posting to Instagram"""
    def publish(self, post: ScheduledPost) -> PublishResult

class RecommendationService:
    """Generates AI recommendations from analytics"""
    def analyze_and_recommend(self, account_id: AccountId) -> Recommendation
```
