"""
Evaluation script to measure RAG system performance
"""
import sys
import json
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_system import ScenarioRAG
from src.config import EVAL_DATA_DIR


# Evaluation dataset
EVAL_QUESTIONS = [
    {
        "query": "What happens in early 2026?",
        "expected_branch": "shared",
        "expected_page": 5,
        "key_facts": ["Agent-1", "50% faster", "algorithmic progress"]
    },
    {
        "query": "In the Race ending, how does control fail?",
        "expected_branch": "race",
        "expected_page": 23,
        "key_facts": ["Agent-4", "Agent-5", "committee votes 6-4"]
    },
    {
        "query": "What is neuralese and why does it matter?",
        "expected_branch": "appendix",
        "expected_page": 46,
        "key_facts": ["neuralese", "high-dimensional", "chain of thought"]
    },
    {
        "query": "When does China steal Agent-2?",
        "expected_branch": "shared",
        "expected_page": 8,
        "key_facts": ["February 2027", "China", "Agent-2", "theft"]
    },
    {
        "query": "What happens in 2030 in the Slowdown ending?",
        "expected_branch": "slowdown",
        "expected_page": 42,
        "key_facts": ["peaceful protests", "democracy", "China"]
    }
]


def evaluate_system():
    """Run evaluation suite"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  RAG System Evaluation                                       ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Initialize RAG
    rag = ScenarioRAG()
    
    # Metrics
    metrics = {
        "total_questions": len(EVAL_QUESTIONS),
        "branch_accuracy": 0,
        "citation_coverage": 0,
        "key_fact_recall": 0,
        "avg_confidence": 0.0,
        "results": []
    }
    
    # Run evaluation
    for i, question in enumerate(EVAL_QUESTIONS):
        print(f"\n{'='*80}")
        print(f"Question {i+1}/{len(EVAL_QUESTIONS)}: {question['query']}")
        print(f"{'='*80}")
        
        # Query system
        response = rag.query(question['query'])
        
        # Evaluate branch accuracy
        branch_correct = response['branch'] == question['expected_branch']
        if branch_correct:
            metrics['branch_accuracy'] += 1
        
        # Evaluate citation coverage (at least 1 citation)
        has_citations = len(response['citations']) > 0
        if has_citations:
            metrics['citation_coverage'] += 1
        
        # Evaluate key fact recall
        answer_lower = response['answer'].lower()
        facts_found = sum(1 for fact in question['key_facts'] if fact.lower() in answer_lower)
        fact_recall = facts_found / len(question['key_facts'])
        metrics['key_fact_recall'] += fact_recall
        
        # Track confidence
        metrics['avg_confidence'] += response['confidence_score']
        
        # Store result
        result = {
            "query": question['query'],
            "expected_branch": question['expected_branch'],
            "actual_branch": response['branch'],
            "branch_correct": branch_correct,
            "num_citations": len(response['citations']),
            "fact_recall": fact_recall,
            "confidence": response['confidence_score']
        }
        metrics['results'].append(result)
        
        # Print result
        print(f"✓ Branch: {response['branch']} {'✅' if branch_correct else '❌'}")
        print(f"✓ Citations: {len(response['citations'])} {'✅' if has_citations else '❌'}")
        print(f"✓ Fact recall: {fact_recall:.1%}")
        print(f"✓ Confidence: {response['confidence_score']:.2f}")
    
    # Calculate final metrics
    n = len(EVAL_QUESTIONS)
    metrics['branch_accuracy'] = metrics['branch_accuracy'] / n
    metrics['citation_coverage'] = metrics['citation_coverage'] / n
    metrics['key_fact_recall'] = metrics['key_fact_recall'] / n
    metrics['avg_confidence'] = metrics['avg_confidence'] / n
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 EVALUATION SUMMARY")
    print(f"{'='*80}")
    print(f"Branch Accuracy:     {metrics['branch_accuracy']:.1%}")
    print(f"Citation Coverage:   {metrics['citation_coverage']:.1%}")
    print(f"Key Fact Recall:     {metrics['key_fact_recall']:.1%}")
    print(f"Avg Confidence:      {metrics['avg_confidence']:.2f}")
    
    # Save results
    results_path = EVAL_DATA_DIR / "eval_results.json"
    with open(results_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n💾 Results saved to {results_path}")
    
    return metrics


if __name__ == "__main__":
    evaluate_system()
