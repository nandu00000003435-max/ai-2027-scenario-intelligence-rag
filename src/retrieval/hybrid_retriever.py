"""
Hybrid retrieval combining dense (embeddings) + sparse (BM25) search
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from rank_bm25 import BM25Okapi

from src.config import (
    OPENAI_API_KEY, EMBEDDING_MODEL, CHROMA_PERSIST_DIR,
    TOP_K_RETRIEVAL, PROCESSED_DATA_DIR
)


class HybridRetriever:
    """Hybrid retrieval with branch-aware filtering"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection("ai_2027_chunks")
            print(f"✅ Loaded existing vector store ({self.collection.count()} chunks)")
        except:
            self.collection = None
            print("⚠️  Vector store not found. Run: python scripts/ingest_document.py")
        
        # Load chunks for BM25
        self.chunks = self._load_chunks()
        self.bm25 = self._build_bm25_index()
    
    def retrieve(
        self, 
        query: str, 
        branch_filter: Optional[str] = None,
        top_k: int = TOP_K_RETRIEVAL
    ) -> List[Dict]:
        """
        Hybrid retrieval with branch filtering
        
        Args:
            query: User question
            branch_filter: "shared", "race", "slowdown", or None (all branches)
            top_k: Number of results to return
        
        Returns:
            List of retrieved passages with metadata
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized. Run ingestion first.")
        
        # Step 1: Dense retrieval (semantic search)
        dense_results = self._dense_retrieval(query, branch_filter, top_k * 2)
        
        # Step 2: Sparse retrieval (BM25 keyword matching)
        sparse_results = self._sparse_retrieval(query, branch_filter, top_k * 2)
        
        # Step 3: Merge and deduplicate
        merged = self._merge_results(dense_results, sparse_results)
        
        # Step 4: Rerank (simple score-based for now)
        reranked = self._rerank(query, merged, top_k)
        
        return reranked
    
    def _dense_retrieval(self, query: str, branch_filter: Optional[str], top_k: int) -> List[Dict]:
        """Semantic search using embeddings"""
        # Generate query embedding
        embedding = self._embed_text(query)
        
        # Build filter
        where_filter = {}
        if branch_filter and branch_filter != "auto":
            if branch_filter == "shared":
                where_filter = {"branch": "shared"}
            elif branch_filter == "race":
                where_filter = {"branch": {"$in": ["shared", "race"]}}
            elif branch_filter == "slowdown":
                where_filter = {"branch": {"$in": ["shared", "slowdown"]}}
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where_filter if where_filter else None
        )
        
        # Format results
        passages = []
        for i in range(len(results['ids'][0])):
            passages.append({
                "id": results['ids'][0][i],
                "text": results['documents'][0][i],
                "page": results['metadatas'][0][i].get('page'),
                "branch": results['metadatas'][0][i].get('branch'),
                "score": 1.0 - results['distances'][0][i],  # Convert distance to similarity
                "source": "dense"
            })
        
        return passages
    
    def _sparse_retrieval(self, query: str, branch_filter: Optional[str], top_k: int) -> List[Dict]:
        """Keyword-based search using BM25"""
        if not self.bm25:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k * 3]
        
        # Filter by branch and format results
        passages = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            
            # Apply branch filter
            if branch_filter and branch_filter != "auto":
                if branch_filter == "shared" and chunk['branch'] != "shared":
                    continue
                elif branch_filter == "race" and chunk['branch'] not in ["shared", "race"]:
                    continue
                elif branch_filter == "slowdown" and chunk['branch'] not in ["shared", "slowdown"]:
                    continue
            
            passages.append({
                "id": chunk['id'],
                "text": chunk['text'],
                "page": chunk['page'],
                "branch": chunk['branch'],
                "score": float(scores[idx]),
                "source": "sparse"
            })
            
            if len(passages) >= top_k:
                break
        
        return passages
    
    def _merge_results(self, dense: List[Dict], sparse: List[Dict]) -> List[Dict]:
        """Merge and deduplicate results from dense and sparse retrieval"""
        seen_ids = set()
        merged = []
        
        # Interleave dense and sparse results
        max_len = max(len(dense), len(sparse))
        for i in range(max_len):
            if i < len(dense) and dense[i]['id'] not in seen_ids:
                merged.append(dense[i])
                seen_ids.add(dense[i]['id'])
            
            if i < len(sparse) and sparse[i]['id'] not in seen_ids:
                merged.append(sparse[i])
                seen_ids.add(sparse[i]['id'])
        
        return merged
    
    def _rerank(self, query: str, passages: List[Dict], top_k: int) -> List[Dict]:
        """Simple reranking based on combined scores"""
        # Normalize scores
        if not passages:
            return []
        
        max_score = max(p['score'] for p in passages)
        min_score = min(p['score'] for p in passages)
        score_range = max_score - min_score if max_score > min_score else 1.0
        
        for p in passages:
            p['normalized_score'] = (p['score'] - min_score) / score_range
        
        # Sort by normalized score
        reranked = sorted(passages, key=lambda x: x['normalized_score'], reverse=True)
        
        return reranked[:top_k]
    
    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def _load_chunks(self) -> List[Dict]:
        """Load processed chunks from JSON"""
        chunks_path = PROCESSED_DATA_DIR / "chunks.json"
        if not chunks_path.exists():
            return []
        
        with open(chunks_path, "r") as f:
            return json.load(f)
    
    def _build_bm25_index(self) -> Optional[BM25Okapi]:
        """Build BM25 index from chunks"""
        if not self.chunks:
            return None
        
        # Tokenize all chunks
        tokenized_corpus = [chunk['text'].lower().split() for chunk in self.chunks]
        return BM25Okapi(tokenized_corpus)
    
    def get_stats(self) -> Dict:
        """Get retriever statistics"""
        if not self.collection:
            return {"status": "not_initialized"}
        
        return {
            "status": "ready",
            "total_chunks": self.collection.count(),
            "branches": list(set(chunk['branch'] for chunk in self.chunks)),
            "bm25_enabled": self.bm25 is not None
        }


if __name__ == "__main__":
    retriever = HybridRetriever()
    print(f"📊 Retriever stats: {retriever.get_stats()}")
    
    # Test query
    results = retriever.retrieve("What happens in early 2026?", branch_filter="shared")
    print(f"\n🔍 Retrieved {len(results)} passages")
    for i, r in enumerate(results[:3]):
        print(f"\n[{i+1}] Page {r['page']}, {r['branch']} branch (score: {r['score']:.3f})")
        print(f"    {r['text'][:200]}...")
