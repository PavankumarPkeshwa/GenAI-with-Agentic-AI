"""
agent_routes.py

Expose two endpoints:
- POST /agent/ingest?url=...  -> starts ingestion flow for a single URL
- POST /agent/process_text    -> manually send content to validator/ingest pipeline

These are synchronous endpoints for demo/testing. In production you would queue ingestion jobs.
"""

from fastapi import APIRouter, Query, Body
from app.agent.manager_agent import ingest_url
from app.agent.validator_agent import validate_article

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/ingest")
def ingest(url: str = Query(..., description="News article URL to ingest")):
    """
    Ingest a URL end-to-end: scrape, validate, and store.
    Returns a JSON with status and metadata.
    """
    result = ingest_url(url)
    return result


@router.post("/validate_text")
def validate_text(payload: dict = Body(...)):
    """
    Validate a text payload directly (bypass scraper). Useful for testing.
    Body should be JSON: { "text": "...article text..." }
    """
    text = payload.get("text", "")
    if not text:
        return {"error": "empty_text"}
    decision = validate_article(text)
    return decision
