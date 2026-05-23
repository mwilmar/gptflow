# Analytics — GPTFlow Operation

## Analytics Pipeline

```
Instagram API → Fetch Worker (6h) → PostgreSQL → Aggregation (daily) → Dashboard Cache (Redis)
```

## Metrics Tracked

### Post-Level
| Metric | Source | Update Frequency |
|--------|--------|-----------------|
| Likes | IG Insights | Every 6h |
| Comments | IG Insights | Every 6h |
| Shares | IG Insights | Every 6h |
| Saves | IG Insights | Every 6h |
| Reach | IG Insights | Every 6h |
| Impressions | IG Insights | Every 6h |

### Account-Level
| Metric | Calculation | Update |
|--------|-------------|--------|
| Engagement Rate | (likes+comments+shares+saves)/reach × 100 | Daily |
| Follower Growth | delta followers / 7 days | Daily |
| Best Posting Time | time slot with highest avg engagement | Weekly |
| Top Content Type | format with highest avg engagement | Weekly |
| Posting Consistency | actual posts / planned posts | Weekly |

## Dashboard KPIs

```
┌─────────────────────────────────────────────────┐
│  This Month                                      │
│  Posts: 28  │  Eng Rate: 4.2%  │  Growth: +187  │
│  Reach: 15K │  Saves: 340      │  Best: 18:00   │
└─────────────────────────────────────────────────┘
```

## Data Retention
- Raw metrics: 1 year
- Aggregated (daily): 3 years
- Aggregated (monthly): Permanent
