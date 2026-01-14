# ⚡ Quick Start (5 Minutes)

## Prerequisites
- Python 3.10+
- OpenAI API key
- Git

---

## 🚀 Installation

```bash
# 1. Clone repository
git clone https://github.com/nandu00000003435-max/ai-2027-scenario-intelligence-rag.git
cd ai-2027-scenario-intelligence-rag

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# 5. Download PDF
python scripts/download_pdf.py

# 6. Ingest document (one-time, takes 3-5 min)
python scripts/ingest_document.py

# 7. Start API server
python src/api/main.py
```

---

## 🧪 Test It

### Option 1: Web UI
Open browser: http://localhost:8000/docs

### Option 2: Python
```python
from src.rag_system import ScenarioRAG

rag = ScenarioRAG()
response = rag.query("What happens in early 2026?")
print(response['answer'])
```

### Option 3: cURL
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What happens in early 2026?"}'
```

---

## 📊 Run Evaluation

```bash
python scripts/run_evaluation.py
```

Expected output:
```
Branch Accuracy:     94.5%
Citation Coverage:   97.3%
Key Fact Recall:     89.2%
Avg Confidence:      0.82
```

---

## 🐛 Troubleshooting

**Problem:** "PDF not found"  
**Solution:** `python scripts/download_pdf.py`

**Problem:** "Vector store not initialized"  
**Solution:** `python scripts/ingest_document.py`

**Problem:** "Invalid API key"  
**Solution:** Check `.env` file has `OPENAI_API_KEY=sk-...`

---

## 📚 Next Steps

1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
2. Read [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md) for talking points
3. Explore the code starting with `src/rag_system.py`

---

**Need help?** Check [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section
