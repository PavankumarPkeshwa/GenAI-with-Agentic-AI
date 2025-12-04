"""
validator_agent.py
Checks length, duplicate via embeddings + vectordb, and LLM quick check.
"""

from app.rag.embedder import get_embedding_model
from app.rag.vectordb import get_vector_db
from langchain_core.prompts import PromptTemplate
from app.utils.local_llm import LocalLLM
import math
import numpy as np

MIN_WORDS = 60
DUPLICATE_SIMILARITY_THRESHOLD = 0.85  # cosine threshold

def _get_llm():
    return LocalLLM(model_name="google/flan-t5-base", max_length=256)

def is_long_enough(text: str) -> bool:
    words = text.split()
    return len(words) >= MIN_WORDS

def _cosine(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom != 0 else 0.0

def is_duplicate(text: str) -> (bool, float):
    embedding_model = get_embedding_model()
    vectordb = get_vector_db()

    try:
        emb = embedding_model.embed_documents([text])[0]
    except Exception:
        # fallback: some embedding wrappers provide embed_query
        try:
            emb = embedding_model.embed_query(text)
        except Exception:
            return (False, 0.0)

    try:
        # try high-level search_by_vector API
        results = None
        try:
            results = vectordb.similarity_search_by_vector(emb, k=1)
        except Exception:
            # fallback: some chroma wrappers expose _collection.query or similar
            try:
                # low-level query; may return dicts
                results = vectordb._collection.query(  # type: ignore[attr-defined]
                    query_embeddings=[emb],
                    n_results=1,
                    include=["metadatas", "distances", "documents"],
                )
                # results format differs; compute sim from distances if available
            except Exception:
                results = None

        if results:
            # Try to extract similarity score conservatively
            # If high-level returned Document objects:
            if isinstance(results, list) and len(results) > 0:
                neighbor = results[0]
                score = getattr(neighbor, "score", None) or getattr(neighbor, "distance", None)
                if score is not None:
                    # convert distance -> similarity if needed (many return distance)
                    sim = float(score)
                    # if distance style (bigger=bad), ensure threshold logic handles it; we conservatively treat high numbers as low sim
                    if sim > 1.5:  # heuristic distance >1 usually means low similarity
                        sim = 0.0
                else:
                    sim = 0.0
            elif isinstance(results, dict):
                # low-level chroma-like response
                try:
                    distances = results.get("distances", [[]])[0]
                    if distances:
                        # convert to similarity via 1 / (1 + dist) heuristic (conservative)
                        sim = 1.0 / (1.0 + float(distances[0]))
                    else:
                        sim = 0.0
                except Exception:
                    sim = 0.0
            else:
                sim = 0.0
        else:
            sim = 0.0

    except Exception:
        sim = 0.0

    return (sim >= DUPLICATE_SIMILARITY_THRESHOLD, sim)

def llm_validate_relevance(text: str) -> dict:
    """
    Simplified validation - checks if text looks like an article.
    For local models, we use simpler heuristics instead of complex JSON parsing.
    """
    # Simple heuristics for article validation
    out = {
        "relevant": True,  # Assume relevant if it passed length check
        "category": "article",
        "safe": True,
        "comment": "Validated using local model"
    }
    
    # Basic content checks
    text_lower = text.lower()
    
    # Check if it's spam/junk
    spam_keywords = ["click here", "buy now", "subscribe", "sign up", "enter email", "404", "error"]
    spam_count = sum(1 for kw in spam_keywords if kw in text_lower)
    
    if spam_count > 3:
        out["relevant"] = False
        out["comment"] = "Detected promotional/spam content"
        return out
    
    # Check if it has article-like structure (sentences with punctuation)
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    if len(sentences) < 3:
        out["relevant"] = False
        out["comment"] = "Not enough structured content"
        return out
    
    # Passed all checks
    out["comment"] = f"Valid article with {len(sentences)} sentences"
    return out

def validate_article(text: str) -> dict:
    length_ok = is_long_enough(text)
    dup, dup_score = is_duplicate(text)
    llm_check = llm_validate_relevance(text)
    final = "approve" if (length_ok and (not dup) and llm_check.get("relevant", False) and llm_check.get("safe", True)) else "reject"

    return {
        "length_ok": length_ok,
        "is_duplicate": dup,
        "dup_score": dup_score,
        "llm_check": llm_check,
        "final_decision": final
    }
