# Database Design — GPTFlow

## ERD Overview

```
┌──────────┐     ┌───────────────────┐     ┌──────────────┐
│  users   │────▶│ instagram_accounts│◀────│  contents    │
└──────────┘     └───────────────────┘     └──────┬───────┘
                                                   │
                          ┌────────────────────────┼────────────────┐
                          │                        │                │
                   ┌──────▼───────┐    ┌───────────▼──┐   ┌────────▼─────┐
                   │  approvals   │    │scheduled_posts│   │content_versions│
                   └──────────────┘    └───────┬──────┘   └──────────────┘
                                               │
                                       ┌───────▼──────┐
                                       │ post_metrics │
                                       └──────────────┘
                                       
                   ┌──────────────────┐
                   │ recommendations  │
                   └──────────────────┘
```

## Tables

### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'creator',  -- admin, manager, creator
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```

### instagram_accounts
```sql
CREATE TABLE instagram_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id),
    ig_user_id VARCHAR(50) NOT NULL,
    ig_username VARCHAR(100) NOT NULL,
    access_token_encrypted TEXT NOT NULL,
    token_expires_at TIMESTAMPTZ,
    fb_page_id VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_ig_accounts_owner ON instagram_accounts(owner_id);
```

### contents
```sql
CREATE TABLE contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES instagram_accounts(id),
    creator_id UUID NOT NULL REFERENCES users(id),
    content_type VARCHAR(20) NOT NULL,  -- feed, carousel, reels, story
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    topic VARCHAR(500) NOT NULL,
    audience VARCHAR(200),
    tone VARCHAR(50),
    hook TEXT,
    body TEXT,
    cta TEXT,
    caption TEXT,
    hashtags JSONB DEFAULT '[]',
    slides JSONB,           -- carousel slides array
    reels_script JSONB,     -- reels script object
    story_frames JSONB,     -- story frames array
    media_urls JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_contents_account ON contents(account_id);
CREATE INDEX idx_contents_status ON contents(status);
CREATE INDEX idx_contents_creator ON contents(creator_id);
CREATE INDEX idx_contents_type ON contents(content_type);
```

### content_versions
```sql
CREATE TABLE content_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    snapshot JSONB NOT NULL,  -- full content state at this version
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_versions_content ON content_versions(content_id);
```

### approvals
```sql
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, approved, rejected
    notes TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);
CREATE INDEX idx_approvals_content ON approvals(content_id);
CREATE INDEX idx_approvals_status ON approvals(status);
```

### scheduled_posts
```sql
CREATE TABLE scheduled_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES contents(id),
    account_id UUID NOT NULL REFERENCES instagram_accounts(id),
    scheduled_at TIMESTAMPTZ NOT NULL,
    timezone VARCHAR(50) DEFAULT 'Asia/Jakarta',
    status VARCHAR(20) NOT NULL DEFAULT 'queued',  -- queued, publishing, published, failed, cancelled
    ig_post_id VARCHAR(100),
    retry_count INT DEFAULT 0,
    last_error TEXT,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_scheduled_status_time ON scheduled_posts(status, scheduled_at);
CREATE INDEX idx_scheduled_account ON scheduled_posts(account_id);
```

### post_metrics
```sql
CREATE TABLE post_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES scheduled_posts(id),
    ig_post_id VARCHAR(100) NOT NULL,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    shares INT DEFAULT 0,
    saves INT DEFAULT 0,
    reach INT DEFAULT 0,
    impressions INT DEFAULT 0,
    engagement_rate DECIMAL(5,2),
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_metrics_post ON post_metrics(post_id);
CREATE INDEX idx_metrics_fetched ON post_metrics(fetched_at);
```

### recommendations
```sql
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES instagram_accounts(id),
    topics JSONB NOT NULL,
    recommended_format VARCHAR(20),
    best_time VARCHAR(10),
    reasoning TEXT,
    confidence DECIMAL(3,2),
    trending_hashtags JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_recommendations_account ON recommendations(account_id);
```

### notifications
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT false,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
```

## Migration Strategy

- Tool: Alembic
- Naming: `{timestamp}_{description}.py`
- All migrations reversible (upgrade + downgrade)
- Run in CI/CD before deployment
