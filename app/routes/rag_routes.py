"""
rag_routes.py
-------------
API endpoints for the RAG pipeline.
"""

from fastapi import APIRouter
from app.rag.rag_chain import get_rag_chain

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask")
def ask_question(question: str):
    """
    User sends a question → RAG searches news DB → returns answer
    """
    rag = get_rag_chain()
    answer = rag.invoke(question)
    return {"question": question, "answer": answer}
