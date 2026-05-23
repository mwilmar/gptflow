# Testing — GPTFlow

## Testing Strategy

```
Unit Tests (80%) → Integration Tests (15%) → E2E Tests (5%)
```

## Unit Tests (pytest)

| Module | Test Focus | Example |
|--------|-----------|---------|
| Content Service | Generation logic, status transitions | `test_content_status_draft_to_pending` |
| Approval Service | Approve/reject rules, permissions | `test_only_manager_can_approve` |
| Scheduler | Due post detection, retry logic | `test_find_due_posts_returns_correct` |
| Publisher | API call construction, error handling | `test_publish_retries_on_failure` |
| Prompt Builder | Prompt assembly, template selection | `test_carousel_prompt_includes_slides` |
| Auth | JWT creation, validation, expiry | `test_expired_token_rejected` |

### Example
```python
@pytest.mark.asyncio
async def test_generate_content_returns_valid_carousel():
    service = ContentGenerationService(mock_openai_client)
    result = await service.generate(GenerationRequest(
        topic="Study Tips", content_type="carousel", audience="Mahasiswa"
    ))
    assert result.slides is not None
    assert 5 <= len(result.slides) <= 10
    assert result.hook and len(result.hook) > 10
```

## Integration Tests

| Test | Validates |
|------|-----------|
| API → DB | Endpoints correctly persist/retrieve data |
| API → OpenAI | Content generation end-to-end (mocked) |
| Scheduler → Publisher | Scheduled posts get published |
| OAuth flow | Token exchange and storage |

## AI Validation Tests

| Test | Criteria |
|------|----------|
| Caption quality | Has hook, body, CTA, hashtags; < 2200 chars |
| Carousel structure | 5-10 slides, each < 150 chars |
| Reels script | Has timing, hook < 3s, total < 60s |
| Out-of-scope rejection | Doesn't hallucinate unrelated content |
| Language consistency | Output matches requested language |

## Test Configuration
```ini
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    ai: AI validation tests
```

## Coverage Target: > 80%
```bash
pytest --cov=app --cov-report=html --cov-fail-under=80
```
