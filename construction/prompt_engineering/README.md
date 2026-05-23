# Prompt Engineering — GPTFlow

## Strategy

### Model Configuration
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | gpt-4o-mini | Cost-effective, fast, good quality |
| Temperature | 0.7 | Creative but consistent |
| Max tokens | 1500 | Sufficient for carousel (longest) |
| Response format | JSON | Structured, parseable |
| Top-p | 0.9 | Balanced diversity |

### Prompt Architecture
```
┌─────────────────────────────────┐
│ SYSTEM PROMPT                   │  ← Role + rules + output format
├─────────────────────────────────┤
│ CONTEXT (few-shot examples)     │  ← 1-2 examples of ideal output
├─────────────────────────────────┤
│ USER PROMPT                     │  ← Topic + audience + tone + type
└─────────────────────────────────┘
```

### Implementation
```python
class PromptBuilder:
    def build(self, request: GenerationRequest) -> list[dict]:
        system = self._get_system_prompt(request.content_type)
        examples = self._get_few_shot(request.content_type)
        user = self._build_user_prompt(request)
        
        return [
            {"role": "system", "content": system},
            *examples,
            {"role": "user", "content": user}
        ]
    
    def _get_system_prompt(self, content_type: str) -> str:
        return PROMPTS[content_type]["system"]
    
    def _get_few_shot(self, content_type: str) -> list[dict]:
        example = PROMPTS[content_type]["example"]
        return [
            {"role": "user", "content": example["input"]},
            {"role": "assistant", "content": json.dumps(example["output"])}
        ]
```

### Output Validation
```python
class ContentOutputValidator:
    def validate_caption(self, output: dict) -> bool:
        assert "hook" in output and len(output["hook"]) > 10
        assert "caption" in output and len(output["caption"]) < 2200  # IG limit
        assert "hashtags" in output and 5 <= len(output["hashtags"]) <= 30
        return True
    
    def validate_carousel(self, output: dict) -> bool:
        assert "slides" in output and 5 <= len(output["slides"]) <= 10
        for slide in output["slides"]:
            assert len(slide["body"]) < 150  # readable per slide
        return True
```

### Prompt Versioning & A/B Testing
- Store prompts in DB with version number
- A/B test: randomly assign prompt version per generation
- Track: which version → which engagement rate
- Promote winning version after 50+ samples

## Token Cost Estimation

| Content Type | Input Tokens | Output Tokens | Cost (4o-mini) |
|-------------|-------------|---------------|----------------|
| Caption | ~500 | ~400 | ~$0.0003 |
| Carousel | ~600 | ~800 | ~$0.0005 |
| Reels | ~500 | ~600 | ~$0.0004 |
| Recommendation | ~2000 | ~500 | ~$0.0009 |

Monthly estimate (200 generations): ~$0.10-0.20
