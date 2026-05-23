# Requirements — GPTFlow

## Functional Requirements

### FR-01: AI Content Generation
- Generate caption Instagram (hook + body + CTA + hashtag)
- Generate carousel content (judul + 5-10 slides)
- Generate reels script (hook + body + CTA dengan timing)
- Generate story content (teks + interactive element suggestion)
- Support regenerate dan edit hasil AI
- Input: topik, audiens, gaya bahasa, jenis konten

### FR-02: Content Management
- CRUD konten (draft, edit, delete)
- Content status lifecycle: draft → pending_approval → approved → scheduled → posted
- Content versioning (simpan history edit)
- Content template library

### FR-03: Scheduling & Auto Posting
- Schedule konten ke tanggal/jam spesifik (timezone WIB)
- Auto posting via Instagram Graph API
- Support: single image feed, carousel, reels (cover + caption)
- Retry mechanism (3x dengan exponential backoff)
- Cancel/reschedule scheduled post

### FR-04: Approval Workflow
- Submit draft untuk approval
- Approve/reject dengan catatan
- Notifikasi (in-app + email) ke approver dan creator
- Approval history log

### FR-05: Analytics
- Fetch engagement metrics dari Instagram Graph API
- Metrics: likes, comments, shares, saves, reach, impressions, profile visits
- Dashboard: trend chart, top posts, engagement rate
- Per-post dan aggregate analytics

### FR-06: AI Recommendation
- Analisis top performing content (engagement pattern)
- Recommend: topik, format, waktu posting optimal, hashtag trending
- Learning dari historical data (improve over time)

### FR-07: Multi-Account
- Connect multiple Instagram Business Accounts
- Per-account content management
- Per-account analytics
- Account switching di UI

### FR-08: User & Role Management
- Roles: admin, manager, creator
- RBAC (Role-Based Access Control)
- User invitation via email
- Session management (JWT)

### FR-09: Content Calendar
- Monthly/weekly calendar view
- Color-coded per content type
- Drag-and-drop reschedule
- Filter per account, status, type

### FR-10: Dashboard
- Overview: total posts, engagement rate, follower growth
- Upcoming scheduled posts
- Pending approvals count
- AI recommendations summary
- Quick actions (generate, schedule, approve)

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-01 | Performance | API response time | < 500ms (non-AI), < 15s (AI generation) |
| NFR-02 | Availability | System uptime | 99.5% |
| NFR-03 | Scalability | Concurrent users | 100 users |
| NFR-04 | Scalability | Instagram accounts | 50 accounts |
| NFR-05 | Security | Authentication | JWT + refresh token |
| NFR-06 | Security | Data encryption | AES-256 at rest, TLS 1.3 in transit |
| NFR-07 | Security | API keys storage | Encrypted vault |
| NFR-08 | Reliability | Scheduler accuracy | ±1 menit dari jadwal |
| NFR-09 | Reliability | Auto-posting retry | 3x exponential backoff |
| NFR-10 | Observability | Logging | Centralized, structured (JSON) |
| NFR-11 | Observability | Monitoring | Health check, metrics, alerting |
| NFR-12 | Maintainability | Code coverage | > 80% |
| NFR-13 | Deployment | Container | Docker + K8s ready |
| NFR-14 | Compliance | Instagram | Graph API ToS compliant |

## Constraints

- **Budget**: OpenAI API ~$50-100/bulan (GPT-4o-mini)
- **Instagram API**: Rate limit 200 calls/hour per user
- **Posting limit**: Instagram max 25 posts/day per account
- **Image**: Sistem hanya generate text/script, bukan visual
- **Timeline**: MVP 2 bulan, full production 6 bulan
