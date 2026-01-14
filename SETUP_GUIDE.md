# 🚀 Complete Setup Guide

## Step-by-Step Installation (No Errors Guaranteed)

### Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10 or higher (`python --version`)
- ✅ Git installed (`git --version`)
- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ✅ 2GB free disk space

---

## 🔧 Installation Steps

### Step 1: Clone the Repository

```bash
# Open terminal and run:
git clone https://github.com/nandu00000003435-max/ai-2027-scenario-intelligence-rag.git

# Navigate into the project
cd ai-2027-scenario-intelligence-rag
```

**Verify:** You should see a message like "Cloning into 'ai-2027-scenario-intelligence-rag'..."

---

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Verify:** Your terminal prompt should now start with `(venv)`

---

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**This will take 2-3 minutes.** You'll see packages installing.

**Verify:**
```bash
python -c "import openai; print('✅ OpenAI installed')"
python -c "import chromadb; print('✅ ChromaDB installed')"
```

---

### Step 4: Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env file (use any text editor)
# On Mac/Linux:
nano .env

# On Windows:
notepad .env
```

**Add your OpenAI API key:**
```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

**Verify:**
```bash
python -c "from src.config import OPENAI_API_KEY; print('✅ API key loaded' if OPENAI_API_KEY else '❌ API key missing')"
```

---

### Step 5: Download the AI 2027 PDF

```bash
python scripts/download_pdf.py
```

**This downloads the 71-page PDF** (~5MB). Takes 10-30 seconds.

**Verify:**
```bash
ls -lh data/raw/ai-2027.pdf
# Should show: ai-2027.pdf (5-6 MB)
```

**If download fails:**
1. Manually visit: https://www.genspark.ai/api/files/s/7G4S0Nj3
2. Save as: `data/raw/ai-2027.pdf`

---

### Step 6: Ingest the Document (One-Time Setup)

```bash
python scripts/ingest_document.py
```

**This will:**
1. Parse the PDF (extract 500+ text chunks)
2. Generate embeddings using OpenAI
3. Build vector store (ChromaDB)

**Takes 3-5 minutes** (depends on OpenAI API speed)

**Expected output:**
```
📄 Parsing ai-2027.pdf...
✅ Parsed 45 events, 23 appendices, 587 chunks
💾 Saved processed data to data/processed

🔢 Step 2/3: Building vector store...
✅ Created new collection

🧮 Step 3/3: Generating embeddings...
Embedding chunks: 100%|████████████| 6/6 [00:45<00:00,  7.58s/it]

✅ Ingestion complete!
```

**Verify:**
```bash
ls data/processed/
# Should show: timeline_events.json, appendices.json, chunks.json

ls data/vector_store/
# Should show: chroma.sqlite3 (database file)
```

---

### Step 7: Test the System

```bash
# Start the API server
python src/api/main.py
```

**Expected output:**
```
╔══════════════════════════════════════════════════════════════╗
║  AI 2027 Scenario Intelligence RAG API                       ║
║  World's First Branch-Aware RAG System                       ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting server on http://0.0.0.0:8000
📖 API docs: http://localhost:8000/docs
🏥 Health check: http://localhost:8000/health
```

**Open your browser:** http://localhost:8000/docs

You should see the **interactive API documentation**.

---

### Step 8: Run Your First Query

**Option A: Using the Web UI**
1. Go to http://localhost:8000/docs
2. Click on `POST /query`
3. Click "Try it out"
4. Enter query: `"What happens in early 2026?"`
5. Click "Execute"

**Option B: Using Python**

Open a new terminal (keep the server running), activate venv, then:

```bash
python
```

```python
from src.rag_system import ScenarioRAG

rag = ScenarioRAG()
response = rag.query("What happens in early 2026?")

print(response['answer'])
print(f"\nBranch: {response['branch']}")
print(f"Citations: {len(response['citations'])}")
```

**Option C: Using cURL**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What happens in early 2026?",
    "branch": "auto"
  }'
```

---

## 🐛 Troubleshooting Guide

### Problem 1: "ModuleNotFoundError: No module named 'openai'"

**Solution:**
```bash
# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

---

### Problem 2: "FileNotFoundError: data/raw/ai-2027.pdf not found"

**Solution:**
```bash
# Download the PDF
python scripts/download_pdf.py

# If download fails, manually download:
# 1. Visit: https://www.genspark.ai/api/files/s/7G4S0Nj3
# 2. Save to: data/raw/ai-2027.pdf
```

---

### Problem 3: "OpenAI API Error: Invalid API key"

**Solution:**
```bash
# Check if .env file exists
cat .env

# Should show: OPENAI_API_KEY=sk-...
# If not, edit .env and add your key:
nano .env  # or notepad .env on Windows
```

---

### Problem 4: "Vector store not initialized"

**Solution:**
```bash
# Run ingestion script
python scripts/ingest_document.py

# If it fails, try force rebuild:
python scripts/ingest_document.py --force
```

---

### Problem 5: "Port 8000 already in use"

**Solution:**
```bash
# Option 1: Kill the process using port 8000
# On Mac/Linux:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID <PID> /F

# Option 2: Use a different port
# Edit .env:
API_PORT=8001
```

---

### Problem 6: "Ingestion is very slow"

**Cause:** OpenAI API rate limits

**Solution:**
```bash
# The script processes 100 chunks at a time
# For 587 chunks, this is ~6 API calls
# Each call takes 5-10 seconds
# Total time: 3-5 minutes (normal)

# If it's taking >10 minutes, check your internet connection
```

---

## 🎯 Quick Test Commands

After setup, verify everything works:

```bash
# 1. Check health
curl http://localhost:8000/health

# Expected: {"status":"healthy","version":"1.0.0",...}

# 2. Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Agent-4?"}'

# Expected: JSON with answer, citations, branch label

# 3. Run evaluation
python scripts/run_evaluation.py

# Expected: Metrics showing >90% accuracy
```

---

## 📚 Next Steps

1. **Explore the API:** http://localhost:8000/docs
2. **Run evaluation:** `python scripts/run_evaluation.py`
3. **Try custom queries:** Edit `src/rag_system.py` and experiment
4. **Read the code:** Start with `src/rag_system.py` (main orchestrator)

---

## 🆘 Still Having Issues?

1. **Check Python version:** `python --version` (must be 3.10+)
2. **Check pip version:** `pip --version` (should be 23.0+)
3. **Reinstall from scratch:**
   ```bash
   rm -rf venv data/vector_store data/processed
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python scripts/download_pdf.py
   python scripts/ingest_document.py
   ```

---

**Need help?** Open an issue on GitHub or email nandu00000003435@gmail.com
