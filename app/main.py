from fastapi import FastAPI

# Importing our route modules
# Each route file will contain endpoints for RAG, Agents, Scraper
from app.routes import rag_routes, agent_routes, scraper_routes

# Create FastAPI instance
app = FastAPI(
    title="GenAI News Intelligence API",
    description="RAG + Agentic AI + Scraper + VectorDB",
    version="1.0.0"
)

# Include all API routes
app.include_router(rag_routes.router)
app.include_router(agent_routes.router)
app.include_router(scraper_routes.router)


# Root sanity check
@app.get("/")
def home():
    return {"status": "GenAI Service Running 🚀"}
