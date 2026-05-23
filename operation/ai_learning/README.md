# AI Learning — GPTFlow Operation

## Learning Pipeline

```
Posts Published → Metrics Collected → Pattern Analysis → Model Update → Better Recommendations
```

## Learning Dimensions

| Dimension | What AI Learns | Data Source |
|-----------|---------------|-------------|
| Topic Performance | Which topics get highest engagement | post_metrics + content.topic |
| Format Effectiveness | carousel vs feed vs reels performance | post_metrics + content.content_type |
| Timing Optimization | Best day/hour to post | post_metrics.fetched_at + engagement |
| Hashtag Performance | Which hashtags drive reach | post_metrics + content.hashtags |
| Tone Effectiveness | Which tone resonates | post_metrics + content.tone |
| Hook Quality | Which hooks get most saves | post_metrics.saves + content.hook |

## Recommendation Generation (Daily Cron)

```python
async def generate_daily_recommendations(account_id: str):
    # 1. Fetch last 30 days metrics
    metrics = await get_metrics(account_id, days=30)
    
    # 2. Aggregate patterns
    patterns = {
        "top_topics": get_top_by(metrics, "topic", "engagement_rate"),
        "top_format": get_top_by(metrics, "content_type", "engagement_rate"),
        "best_times": get_best_posting_times(metrics),
        "top_hashtags": get_top_hashtags(metrics),
    }
    
    # 3. Call AI for recommendations
    recommendation = await openai_client.generate(
        messages=build_recommendation_prompt(patterns)
    )
    
    # 4. Store
    await save_recommendation(account_id, recommendation)
```

## Feedback Loop

```
Generate Content → Post → Measure → Learn → Improve Prompts → Generate Better Content
                                                    ↓
                                          Update prompt templates
                                          Adjust temperature
                                          Refine few-shot examples
```

## Prompt Evolution Strategy
1. Track engagement per prompt version
2. After 50 posts: compare versions statistically
3. Promote winning version, retire losing version
4. Introduce new variant for next A/B cycle

## AI Quality Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Content acceptance rate | > 90% | approved / generated |
| First-draft approval | > 70% | approved without edit |
| Engagement improvement | +10% MoM | avg engagement trend |
| Recommendation accuracy | > 60% | recommended topic → high engagement |
