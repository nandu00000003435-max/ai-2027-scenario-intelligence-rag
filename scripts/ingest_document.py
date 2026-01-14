"""
One-time ingestion script: Parse PDF and build vector store
"""
import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    OPENAI_API_KEY, EMBEDDING_MODEL, CHROMA_PERSIST_DIR,
    AI_2027_PDF_PATH, PROCESSED_DATA_DIR
)
from src.ingestion.pdf_parser import AI2027Parser


def ingest_document(force: bool = False):
    """
    Ingest AI 2027 document into vector store
    
    Args:
        force: If True, rebuild vector store even if it exists
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║  AI 2027 Document Ingestion                                  ║
║  This will parse the PDF and build the vector store          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Step 1: Check if PDF exists
    if not AI_2027_PDF_PATH.exists():
        print(f"❌ PDF not found at {AI_2027_PDF_PATH}")
        print(f"💡 Run: python scripts/download_pdf.py")
        return
    
    # Step 2: Parse PDF
    print("\n📄 Step 1/3: Parsing PDF...")
    parser = AI2027Parser()
    parsed_data = parser.parse_full_document()
    
    # Step 3: Build vector store
    print("\n🔢 Step 2/3: Building vector store...")
    
    # Initialize ChromaDB
    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_PERSIST_DIR),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Delete existing collection if force=True
    if force:
        try:
            chroma_client.delete_collection("ai_2027_chunks")
            print("🗑️  Deleted existing collection")
        except:
            pass
    
    # Create collection
    try:
        collection = chroma_client.create_collection(
            name="ai_2027_chunks",
            metadata={"description": "AI 2027 scenario document chunks"}
        )
        print("✅ Created new collection")
    except:
        collection = chroma_client.get_collection("ai_2027_chunks")
        print("✅ Using existing collection")
    
    # Step 4: Generate embeddings and add to vector store
    print("\n🧮 Step 3/3: Generating embeddings...")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    chunks = parsed_data['chunks']
    
    # Batch process embeddings
    batch_size = 100
    for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding chunks"):
        batch = chunks[i:i + batch_size]
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in batch]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        
        # Add to ChromaDB
        embeddings = [item.embedding for item in response.data]
        ids = [chunk['id'] for chunk in batch]
        metadatas = [
            {
                "page": chunk['page'],
                "branch": chunk['branch'],
                "source": chunk['metadata']['source'],
                "url": chunk['metadata']['url']
            }
            for chunk in batch
        ]
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    print(f"\n✅ Ingestion complete!")
    print(f"📊 Summary:")
    print(f"   - Total chunks: {len(chunks)}")
    print(f"   - Timeline events: {len(parsed_data['timeline_events'])}")
    print(f"   - Appendices: {len(parsed_data['appendices'])}")
    print(f"   - Vector store: {CHROMA_PERSIST_DIR}")
    print(f"\n🚀 Ready to query! Run: python src/api/main.py")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest AI 2027 document")
    parser.add_argument("--force", action="store_true", help="Force rebuild vector store")
    args = parser.parse_args()
    
    ingest_document(force=args.force)
