from fastapi import APIRouter, Query
from app.agent.manager_agent import ingest_url

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.get("/ingest")
def ingest(url: str = Query(...)):
    return ingest_url(url)
