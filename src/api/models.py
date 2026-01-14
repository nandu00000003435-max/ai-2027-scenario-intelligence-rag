"""
Pydantic models for API request/response validation
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation model with source verification"""
    source: str = Field(default="ai-2027.pdf", description="Source document name")
    url: str = Field(default="https://www.genspark.ai/api/files/s/7G4S0Nj3", description="Source URL")
    locator: str = Field(..., description="Page number or section (e.g., 'page 5' or 'Appendix E')")
    quote: str = Field(..., description="Verbatim quote from source (max 300 chars)", max_length=300)
    context: Optional[str] = Field(None, description="Why this passage supports the claim")


class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    query: str = Field(..., description="User question about AI 2027 scenario", min_length=5)
    branch: Literal["auto", "shared", "race", "slowdown", "both"] = Field(
        default="auto",
        description="Timeline branch filter (auto = system detects)"
    )
    include_assumptions: bool = Field(
        default=True,
        description="Whether to include appendix assumptions in response"
    )
    max_citations: int = Field(default=10, ge=1, le=20, description="Maximum citations to return")


class QueryResponse(BaseModel):
    """Response model with structured output"""
    answer: str = Field(..., description="Concise, branch-aware answer")
    branch: Literal["shared", "race", "slowdown", "both", "unknown"] = Field(
        ...,
        description="Timeline branch classification"
    )
    citations: List[Citation] = Field(..., description="Supporting citations (≥1 required)")
    assumptions_or_limits: List[str] = Field(
        default_factory=list,
        description="Caveats, uncertainties, or appendix assumptions"
    )
    followup_questions: List[str] = Field(
        default_factory=list,
        description="Suggested next questions (max 3)",
        max_items=3
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="System confidence in answer (0-1)"
    )
    retrieval_metadata: Optional[dict] = Field(
        None,
        description="Debug info: retrieved passages, scores, etc."
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    vector_store_status: str
    total_chunks: int
    branches_available: List[str]
