# 🚀 Deployment Guide

## Local Development (Current Setup)

```
Your Machine
├─ FastAPI server (localhost:8000)
├─ ChromaDB (local vector store)
└─ OpenAI API (cloud embeddings/generation)
```

**Pros:**
- ✅ Free (except OpenAI API costs)
- ✅ Full control
- ✅ Fast iteration

**Cons:**
- ❌ Not accessible from internet
- ❌ Stops when you close laptop

---

## Production Deployment Options

### Option 1: Docker + Cloud VM (Recommended)

**1. Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download and ingest document on build
RUN python scripts/download_pdf.py && \
    python scripts/ingest_document.py

EXPOSE 8000

CMD ["python", "src/api/main.py"]
```

**2. Build and run:**
```bash
docker build -t ai2027-rag .
docker run -p 8000:8000 --env-file .env ai2027-rag
```

**3. Deploy to cloud:**
```bash
# AWS EC2, Google Cloud Run, or DigitalOcean
# Push image to registry
docker tag ai2027-rag your-registry/ai2027-rag
docker push your-registry/ai2027-rag

# Deploy (example: Google Cloud Run)
gcloud run deploy ai2027-rag \
  --image your-registry/ai2027-rag \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Cost:** ~$10-20/month (small VM)

---

### Option 2: Serverless (AWS Lambda + API Gateway)

**Pros:**
- ✅ Pay per request
- ✅ Auto-scaling
- ✅ No server management

**Cons:**
- ❌ Cold start latency (~5s first request)
- ❌ More complex setup

**Setup:**
```bash
# Use Mangum adapter for FastAPI
pip install mangum

# Create handler
from mangum import Mangum
from src.api.main import app
handler = Mangum(app)

# Deploy with AWS SAM or Serverless Framework
```

---

### Option 3: Managed Platform (Railway, Render, Fly.io)

**Easiest option for beginners**

**Railway.app example:**
1. Connect GitHub repo
2. Add environment variables (OPENAI_API_KEY)
3. Click "Deploy"
4. Done! Get public URL

**Cost:** Free tier available, then ~$5-10/month

---

## 🔐 Security Considerations

### API Key Management

**Development:**
```bash
# .env file (gitignored)
OPENAI_API_KEY=sk-...
```

**Production:**
```bash
# Use environment variables (never commit keys)
# AWS: Secrets Manager
# GCP: Secret Manager
# Railway: Environment variables UI
```

### Rate Limiting

Add to `src/api/main.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("10/minute")  # Max 10 queries per minute
async def query_rag(request: QueryRequest):
    # ...
```

### Authentication

Add API key authentication:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_SECRET_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/query")
async def query_rag(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    # ...
```

---

## 📊 Monitoring & Logging

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# In your code:
logger.info(f"Query received: {query}")
logger.error(f"Retrieval failed: {error}")
```

### Add Metrics

```python
from prometheus_client import Counter, Histogram

query_counter = Counter('queries_total', 'Total queries')
query_duration = Histogram('query_duration_seconds', 'Query duration')

@app.post("/query")
async def query_rag(request: QueryRequest):
    query_counter.inc()
    with query_duration.time():
        response = rag.query(request.query)
    return response
```

---

## 💰 Cost Estimation

### OpenAI API Costs

**Ingestion (one-time):**
- Embeddings: 587 chunks × 512 tokens = ~300K tokens
- Cost: $0.13 per 1M tokens = **$0.04**

**Per Query:**
- Embedding: 1 query × 20 tokens = ~20 tokens
- Generation: 10 passages × 512 tokens + answer = ~6K tokens
- Cost: ~$0.001 per query

**Monthly (1000 queries):**
- Embeddings: $0.02
- Generation: $1.00
- **Total: ~$1-2/month**

### Infrastructure Costs

**Local:** Free  
**Cloud VM:** $10-20/month  
**Serverless:** $0-5/month (free tier)  
**Managed (Railway):** $5-10/month

**Total monthly cost: $5-25** (mostly infrastructure)

---

## 🔄 CI/CD Pipeline (Future)

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test RAG System

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/
      - run: python scripts/run_evaluation.py
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

**Current:** Single server  
**Future:** Load balancer + multiple servers

```
                    ┌─→ Server 1 (ChromaDB replica)
Load Balancer ──────┼─→ Server 2 (ChromaDB replica)
                    └─→ Server 3 (ChromaDB replica)
```

### Caching Layer

```python
import redis

cache = redis.Redis(host='localhost', port=6379)

def query_with_cache(query: str):
    # Check cache
    cached = cache.get(query)
    if cached:
        return json.loads(cached)
    
    # Query RAG
    response = rag.query(query)
    
    # Cache for 1 hour
    cache.setex(query, 3600, json.dumps(response))
    
    return response
```

**Speedup:** 100x for repeated queries

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Add authentication (API keys)
- [ ] Add rate limiting (prevent abuse)
- [ ] Add logging (track errors)
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Add caching (Redis)
- [ ] Add tests (pytest suite)
- [ ] Add CI/CD (GitHub Actions)
- [ ] Add error handling (graceful failures)
- [ ] Add documentation (API docs)
- [ ] Add backup (vector store snapshots)

---

**For now, local deployment is perfect for development and demos.**
