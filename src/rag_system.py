"""
Main RAG system orchestrator - combines retrieval and generation
"""
from typing import Dict
from src.retrieval.hybrid_retriever import HybridRetriever
from src.generation.answer_generator import AnswerGenerator
from src.api.models import QueryResponse


class ScenarioRAG:
    """
    Main RAG system for AI 2027 scenario intelligence
    
    This is the primary interface for querying the system.
    """
    
    def __init__(self):
        print("🚀 Initializing Scenario Intelligence RAG...")
        self.retriever = HybridRetriever()
        self.generator = AnswerGenerator()
        print("✅ RAG system ready!")
    
    def query(
        self, 
        query: str, 
        branch: str = "auto",
        include_debug: bool = False
    ) -> Dict:
        """
        Query the RAG system
        
        Args:
            query: User question about AI 2027
            branch: Timeline branch filter ("auto", "shared", "race", "slowdown", "both")
            include_debug: Whether to include retrieval metadata in response
        
        Returns:
            Dictionary with answer, citations, and metadata
        
        Example:
            >>> rag = ScenarioRAG()
            >>> response = rag.query("What happens in early 2026?")
            >>> print(response['answer'])
        """
        # Step 1: Detect branch from query if auto
        if branch == "auto":
            branch = self._detect_branch_from_query(query)
        
        # Step 2: Retrieve relevant passages
        print(f"🔍 Retrieving passages (branch: {branch})...")
        passages = self.retriever.retrieve(query, branch_filter=branch)
        
        if not passages:
            return self._format_response(
                QueryResponse(
                    answer="No relevant information found in the document.",
                    branch="unknown",
                    citations=[],
                    assumptions_or_limits=["Query may be outside document scope"],
                    followup_questions=[],
                    confidence_score=0.0
                ),
                include_debug=include_debug
            )
        
        # Step 3: Generate answer
        print(f"💡 Generating answer from {len(passages)} passages...")
        response = self.generator.generate(query, passages, branch_hint=branch)
        
        # Step 4: Format and return
        return self._format_response(response, passages if include_debug else None)
    
    def _detect_branch_from_query(self, query: str) -> str:
        """Detect timeline branch from query text"""
        query_lower = query.lower()
        
        # Explicit branch mentions
        if "race ending" in query_lower or "race scenario" in query_lower:
            return "race"
        if "slowdown ending" in query_lower or "slowdown scenario" in query_lower:
            return "slowdown"
        if "shared timeline" in query_lower or "before the branch" in query_lower:
            return "shared"
        
        # Date-based detection
        if any(year in query_lower for year in ["2025", "2026"]):
            return "shared"
        if "early 2027" in query_lower or "mid 2027" in query_lower:
            return "shared"
        if "late 2027" in query_lower or "2028" in query_lower or "2029" in query_lower or "2030" in query_lower:
            return "both"  # Could be either branch
        
        # Entity-based detection
        if "agent-5" in query_lower or "consensus-1" in query_lower:
            return "both"  # These appear in both branches differently
        
        # Default: search all branches
        return "auto"
    
    def _format_response(
        self, 
        response: QueryResponse, 
        debug_passages: list = None
    ) -> Dict:
        """Format QueryResponse as dictionary"""
        result = {
            "answer": response.answer,
            "branch": response.branch,
            "citations": [cit.model_dump() for cit in response.citations],
            "assumptions_or_limits": response.assumptions_or_limits,
            "followup_questions": response.followup_questions,
            "confidence_score": response.confidence_score
        }
        
        if debug_passages:
            result["retrieval_metadata"] = {
                "num_passages": len(debug_passages),
                "passages": [
                    {
                        "page": p['page'],
                        "branch": p['branch'],
                        "score": p['score'],
                        "preview": p['text'][:200]
                    }
                    for p in debug_passages[:5]
                ]
            }
        
        return result
    
    def health_check(self) -> Dict:
        """Check system health"""
        retriever_stats = self.retriever.get_stats()
        generator_stats = self.generator.get_stats()
        
        return {
            "status": "healthy" if retriever_stats.get("status") == "ready" else "unhealthy",
            "version": "1.0.0",
            "retriever": retriever_stats,
            "generator": generator_stats
        }


if __name__ == "__main__":
    # Demo usage
    rag = ScenarioRAG()
    
    # Test queries
    test_queries = [
        "What happens in early 2026?",
        "In the Race ending, how does control fail?",
        "What is neuralese and why does it matter?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"❓ Query: {query}")
        print(f"{'='*80}")
        
        response = rag.query(query, include_debug=True)
        
        print(f"\n📝 Answer:\n{response['answer']}")
        print(f"\n🏷️  Branch: {response['branch']}")
        print(f"\n📊 Confidence: {response['confidence_score']:.2f}")
        print(f"\n📚 Citations ({len(response['citations'])}):")
        for i, cit in enumerate(response['citations'][:3]):
            print(f"  [{i+1}] {cit['locator']}")
            print(f"      \"{cit['quote'][:100]}...\"")
