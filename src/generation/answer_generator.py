"""
Answer generation with citation validation and structured output
"""
import json
from typing import List, Dict
from openai import OpenAI

from src.config import OPENAI_API_KEY, GENERATION_MODEL, TEMPERATURE
from src.api.models import QueryResponse, Citation


class AnswerGenerator:
    """Generate answers with citations using LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = self._build_system_prompt()
    
    def generate(
        self, 
        query: str, 
        retrieved_passages: List[Dict],
        branch_hint: str = "auto"
    ) -> QueryResponse:
        """
        Generate structured answer from retrieved passages
        
        Args:
            query: User question
            retrieved_passages: List of retrieved passages with metadata
            branch_hint: Branch context ("auto", "shared", "race", "slowdown")
        
        Returns:
            QueryResponse with answer, citations, and metadata
        """
        if not retrieved_passages:
            return self._create_refusal_response(
                "No relevant passages found in the document.",
                branch="unknown"
            )
        
        # Format passages for prompt
        formatted_passages = self._format_passages(retrieved_passages)
        
        # Build user prompt
        user_prompt = self._build_user_prompt(query, formatted_passages, branch_hint)
        
        # Call LLM with JSON mode
        try:
            response = self.client.chat.completions.create(
                model=GENERATION_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Validate and convert to QueryResponse
            return self._validate_and_convert(result, retrieved_passages)
        
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return self._create_refusal_response(
                f"Error generating answer: {str(e)}",
                branch="unknown"
            )
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with strict rules"""
        return """You are an expert scenario intelligence analyst specializing in the AI 2027 document.

CRITICAL RULES:
1. ONLY use information from the RETRIEVED PASSAGES provided below
2. EVERY factual claim must cite a passage using [Citation N] format
3. If evidence is weak/missing, say "Evidence unclear" or "Not addressed in document"
4. Distinguish timeline branches explicitly:
   - "In the shared timeline (pre-Oct 2027)..."
   - "In the Race ending..."
   - "In the Slowdown ending..."
5. When citing appendices, explain their relevance
6. Be concise but complete (max 500 words for answer)

OUTPUT FORMAT:
You must return a valid JSON object with this exact structure:
{
  "answer": "Your answer here with [Citation 1], [Citation 2] inline",
  "branch": "shared|race|slowdown|both|unknown",
  "citations": [
    {
      "source": "ai-2027.pdf",
      "url": "https://www.genspark.ai/api/files/s/7G4S0Nj3",
      "locator": "page N or Appendix X",
      "quote": "verbatim quote from passage (max 200 chars)",
      "context": "why this supports the claim"
    }
  ],
  "assumptions_or_limits": ["list of caveats or appendix assumptions"],
  "followup_questions": ["suggested next question 1", "question 2", "question 3"],
  "confidence_score": 0.0-1.0
}

BRANCH CLASSIFICATION RULES:
- "shared": Events before October 2027 branch point
- "race": Events in Race ending (Oct 2027-2030) where committee continues Agent-4
- "slowdown": Events in Slowdown ending (Oct 2027-2030) where committee slows down
- "both": Question applies to both branches (provide separate answers)
- "unknown": Insufficient context to determine branch

CONFIDENCE SCORE RULES:
- 0.9-1.0: Multiple direct citations, clear evidence
- 0.7-0.9: Good evidence but some inference required
- 0.5-0.7: Partial evidence, significant uncertainty
- Below 0.5: Weak evidence, should refuse to answer
"""
    
    def _build_user_prompt(self, query: str, passages: str, branch_hint: str) -> str:
        """Build user prompt with query and passages"""
        branch_context = ""
        if branch_hint != "auto":
            branch_context = f"\nBRANCH CONTEXT: User is asking about the '{branch_hint}' branch.\n"
        
        return f"""{branch_context}
RETRIEVED PASSAGES:
{passages}

USER QUERY:
{query}

Generate a JSON response following the system prompt rules."""
    
    def _format_passages(self, passages: List[Dict]) -> str:
        """Format retrieved passages for prompt"""
        formatted = []
        for i, p in enumerate(passages):
            formatted.append(
                f"[Passage {i+1}]\n"
                f"Page: {p['page']}\n"
                f"Branch: {p['branch']}\n"
                f"Content: {p['text']}\n"
            )
        return "\n".join(formatted)
    
    def _validate_and_convert(self, result: Dict, passages: List[Dict]) -> QueryResponse:
        """Validate LLM output and convert to QueryResponse"""
        # Ensure required fields exist
        if "answer" not in result or "branch" not in result:
            return self._create_refusal_response(
                "Invalid response format from LLM",
                branch="unknown"
            )
        
        # Validate citations
        citations = []
        for i, cit in enumerate(result.get("citations", [])):
            # Verify quote exists in passages (fuzzy match)
            if self._verify_quote(cit.get("quote", ""), passages):
                citations.append(Citation(
                    source=cit.get("source", "ai-2027.pdf"),
                    url=cit.get("url", "https://www.genspark.ai/api/files/s/7G4S0Nj3"),
                    locator=cit.get("locator", f"page {passages[i]['page']}"),
                    quote=cit.get("quote", "")[:300],  # Truncate if too long
                    context=cit.get("context")
                ))
        
        # If no valid citations, refuse
        if not citations:
            return self._create_refusal_response(
                "Could not verify citations in source passages",
                branch=result.get("branch", "unknown")
            )
        
        return QueryResponse(
            answer=result["answer"],
            branch=result["branch"],
            citations=citations,
            assumptions_or_limits=result.get("assumptions_or_limits", []),
            followup_questions=result.get("followup_questions", [])[:3],
            confidence_score=result.get("confidence_score", 0.7)
        )
    
    def _verify_quote(self, quote: str, passages: List[Dict]) -> bool:
        """Verify quote exists in retrieved passages (fuzzy match)"""
        from rapidfuzz import fuzz
        
        if not quote or len(quote) < 10:
            return False
        
        # Check each passage
        for passage in passages:
            # Fuzzy match (allows minor differences)
            similarity = fuzz.partial_ratio(quote.lower(), passage['text'].lower())
            if similarity >= 85:  # 85% similarity threshold
                return True
        
        return False
    
    def _create_refusal_response(self, reason: str, branch: str) -> QueryResponse:
        """Create refusal response when evidence is insufficient"""
        return QueryResponse(
            answer=f"I cannot answer this question with confidence. Reason: {reason}",
            branch=branch,
            citations=[],
            assumptions_or_limits=[reason],
            followup_questions=[],
            confidence_score=0.0
        )
    
    def get_stats(self) -> Dict:
        """Get generator statistics"""
        return {
            "model": GENERATION_MODEL,
            "temperature": TEMPERATURE,
            "system_prompt_length": len(self.system_prompt)
        }


if __name__ == "__main__":
    from src.retrieval.hybrid_retriever import HybridRetriever
    
    retriever = HybridRetriever()
    generator = AnswerGenerator()
    
    # Test query
    query = "What happens in early 2026?"
    passages = retriever.retrieve(query, branch_filter="shared")
    response = generator.generate(query, passages, branch_hint="shared")
    
    print(f"\n📝 Answer:\n{response.answer}")
    print(f"\n🏷️  Branch: {response.branch}")
    print(f"\n📚 Citations: {len(response.citations)}")
    for i, cit in enumerate(response.citations):
        print(f"  [{i+1}] {cit.locator}: \"{cit.quote[:100]}...\"")
