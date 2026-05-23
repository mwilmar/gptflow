# DevOps — GPTFlow

## CI/CD Pipeline (GitHub Actions)

```yaml
name: CI/CD
on:
  push: {branches: [main, develop]}
  pull_request: {branches: [main]}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff mypy
      - run: ruff check app/
      - run: mypy app/

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/org/gptflow-api:${{ github.sha }}

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - run: kubectl set image deployment/api api=ghcr.io/org/gptflow-api:${{ github.sha }}

  deploy-prod:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: kubectl set image deployment/api api=ghcr.io/org/gptflow-api:${{ github.sha }}
```

## Docker Configuration

### Dockerfile.api
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Environment Strategy

| Environment | Branch | Auto-deploy | URL |
|-------------|--------|-------------|-----|
| Development | feature/* | No | localhost:8000 |
| Staging | develop | Yes | staging.gptflow.app |
| Production | main | Yes (with approval) | app.gptflow.app |

## Infrastructure as Code
- Kubernetes manifests in `/k8s/` directory
- Helm chart for parameterized deployment
- Terraform for cloud resources (future)
