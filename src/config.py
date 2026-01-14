"""
Configuration management for the RAG system
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EVAL_DATA_DIR = DATA_DIR / "eval"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EVAL_DATA_DIR, VECTOR_STORE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

# Vector Store Configuration
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chromadb")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(VECTOR_STORE_DIR))

# Retrieval Configuration
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "5"))
MIN_CITATION_CONFIDENCE = float(os.getenv("MIN_CITATION_CONFIDENCE", "0.85"))

# Chunking Configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Document metadata
AI_2027_PDF_PATH = RAW_DATA_DIR / "ai-2027.pdf"
AI_2027_URL = "https://www.genspark.ai/api/files/s/7G4S0Nj3"

# Branch definitions
BRANCHES = ["shared", "race", "slowdown", "appendix", "unknown"]

# Entity definitions
ENTITIES = {
    "organizations": [
        "OpenBrain", "DeepCent", "Oversight Committee",
        "OpenAI", "Anthropic", "Google DeepMind", "TSMC",
        "RAND Corporation", "National Security Council", "Department of Defense"
    ],
    "ai_systems": [
        "Agent-0", "Agent-1", "Agent-2", "Agent-3", "Agent-4", "Agent-5",
        "Safer-1", "Safer-2", "Safer-3", "Safer-4", "Safer-∞",
        "Consensus-1", "DeepCent-1", "DeepCent-2"
    ],
    "concepts": [
        "alignment", "mechanistic interpretability", "neuralese",
        "IDA", "faithful chain of thought", "model specification",
        "intelligence explosion", "AI R&D multiplier", "superalignment"
    ]
}

# Appendix mapping (page ranges)
APPENDICES = {
    "A": {"title": "Training process and LLM psychology", "page_start": 44},
    "B": {"title": "AI R&D progress multiplier", "page_start": 44},
    "C": {"title": "Why uncertainty increases beyond 2026", "page_start": 45},
    "D": {"title": "Theft of Agent-2 model weights", "page_start": 46},
    "E": {"title": "Neuralese recurrence and memory", "page_start": 46},
    "F": {"title": "Iterated distillation and amplification", "page_start": 48},
    "G": {"title": "Why superhuman coder in early 2027", "page_start": 49},
    "H": {"title": "The alignment plan", "page_start": 51},
    "I": {"title": "Managing a corporation of AIs", "page_start": 53},
    "J": {"title": "Capability progression beyond superhuman coders", "page_start": 53},
    "K": {"title": "Alignment over time", "page_start": 55},
    "L": {"title": "Our uncertainty continues to increase", "page_start": 59},
    "M": {"title": "Slowdown ending is not a recommendation", "page_start": 60},
    "N": {"title": "Superintelligent mechanistic interpretability", "page_start": 60},
    "O": {"title": "Superpersuasion", "page_start": 61},
    "P": {"title": "Superintelligence-enabled coordination technology", "page_start": 62},
    "Q": {"title": "Robot economy doubling times", "page_start": 62},
    "R": {"title": "Power grabs", "page_start": 64},
    "S": {"title": "Verification mechanisms for international agreement", "page_start": 65},
    "T": {"title": "OpenBrain's new alignment strategy", "page_start": 67},
    "U": {"title": "Robot economy doubling times", "page_start": 67},
    "V": {"title": "So who rules the future?", "page_start": 69},
    "W": {"title": "Reminder this scenario is a forecast", "page_start": 70}
}
