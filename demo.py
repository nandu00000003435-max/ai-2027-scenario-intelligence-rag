"""
Interactive demo script - Test the RAG system with example queries
"""
from src.rag_system import ScenarioRAG
import json


def print_response(response: dict):
    """Pretty print response"""
    print(f"\n{'='*80}")
    print(f"📝 ANSWER")
    print(f"{'='*80}")
    print(response['answer'])
    
    print(f"\n🏷️  BRANCH: {response['branch']}")
    print(f"📊 CONFIDENCE: {response['confidence_score']:.2%}")
    
    print(f"\n📚 CITATIONS ({len(response['citations'])}):")
    for i, cit in enumerate(response['citations'], 1):
        print(f"\n  [{i}] {cit['locator']}")
        print(f"      \"{cit['quote'][:150]}...\"")
    
    if response['assumptions_or_limits']:
        print(f"\n⚠️  ASSUMPTIONS:")
        for assumption in response['assumptions_or_limits']:
            print(f"  • {assumption}")
    
    if response['followup_questions']:
        print(f"\n💡 FOLLOW-UP QUESTIONS:")
        for q in response['followup_questions']:
            print(f"  • {q}")
    
    print(f"\n{'='*80}\n")


def main():
    """Run interactive demo"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  AI 2027 Scenario Intelligence RAG - Interactive Demo        ║
║  World's First Branch-Aware RAG System                       ║
╚══════════════════════════════════════════════════════════════╝

Initializing system...
""")
    
    # Initialize RAG
    rag = ScenarioRAG()
    
    # Demo queries
    demo_queries = [
        {
            "title": "Timeline Query (Shared Timeline)",
            "query": "What happens in early 2026?",
            "description": "Tests retrieval from shared timeline before branch point"
        },
        {
            "title": "Branch-Specific Query (Race Ending)",
            "query": "In the Race ending, how does control fail?",
            "description": "Tests branch-aware retrieval and filtering"
        },
        {
            "title": "Appendix Query (Technical Concept)",
            "query": "What is neuralese and why does it matter?",
            "description": "Tests appendix retrieval and technical explanation"
        },
        {
            "title": "Temporal Query (Specific Event)",
            "query": "When does China steal Agent-2 and what happens?",
            "description": "Tests temporal reasoning and event extraction"
        },
        {
            "title": "Comparison Query (Both Branches)",
            "query": "What happens in 2030 in both endings?",
            "description": "Tests multi-branch retrieval and comparison"
        }
    ]
    
    print("\n🎯 Running 5 demo queries...\n")
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{'#'*80}")
        print(f"DEMO {i}/5: {demo['title']}")
        print(f"{'#'*80}")
        print(f"Query: {demo['query']}")
        print(f"Purpose: {demo['description']}")
        
        # Query the system
        response = rag.query(demo['query'], include_debug=False)
        
        # Print response
        print_response(response)
        
        # Pause between queries
        if i < len(demo_queries):
            input("Press Enter to continue to next demo...")
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Demo Complete!                                              ║
║                                                              ║
║  Try your own queries:                                       ║
║  >>> from src.rag_system import ScenarioRAG                  ║
║  >>> rag = ScenarioRAG()                                     ║
║  >>> response = rag.query("Your question here")              ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
