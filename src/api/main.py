"""
FastAPI server for Scenario Intelligence RAG
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.rag_system import ScenarioRAG
from src.api.models import QueryRequest, QueryResponse, HealthResponse
from src.config import API_HOST, API_PORT

# Initialize FastAPI app
app = FastAPI(
    title="AI 2027 Scenario Intelligence RAG",
    description="World's first branch-aware RAG system for scenario forecasting",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system (singleton)
rag_system = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    try:
        rag_system = ScenarioRAG()
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        print("⚠️  Server will start but queries will fail until system is initialized")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info"""
    return {
        "message": "AI 2027 Scenario Intelligence RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "query_endpoint": "/query"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    health = rag_system.health_check()
    
    return HealthResponse(
        status=health["status"],
        version=health["version"],
        vector_store_status=health["retriever"]["status"],
        total_chunks=health["retriever"].get("total_chunks", 0),
        branches_available=health["retriever"].get("branches", [])
    )


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_rag(request: QueryRequest):
    """
    Query the RAG system
    
    Example request:
    ```json
    {
      "query": "What happens in early 2026?",
      "branch": "auto",
      "include_assumptions": true,
      "max_citations": 10
    }
    ```
    """
    if not rag_system:
        raise HTTPException(
            status_code=503, 
            detail="RAG system not initialized. Please check server logs."
        )
    
    try:
        # Query the system
        response = rag_system.query(
            query=request.query,
            branch=request.branch,
            include_debug=False
        )
        
        # Convert dict to QueryResponse
        return QueryResponse(**response)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/stats", tags=["Stats"])
async def get_stats():
    """Get system statistics"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    return rag_system.health_check()


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  AI 2027 Scenario Intelligence RAG API                       ║
║  World's First Branch-Aware RAG System                       ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting server on http://{API_HOST}:{API_PORT}
📖 API docs: http://localhost:{API_PORT}/docs
🏥 Health check: http://localhost:{API_PORT}/health

Press Ctrl+C to stop
""")
    
    uvicorn.run(
        "src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
