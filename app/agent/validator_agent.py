"""
validator_agent.py
Checks length, duplicate via embeddings + vectordb, and LLM quick check.
"""

from app.rag.embedder import get_embedding_model
from app.rag.vectordb import get_vector_db
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
import math
import numpy as np

MIN_WORDS = 60
DUPLICATE_SIMILARITY_THRESHOLD = 0.85  # cosine threshold

def _get_llm():
    return HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.0, "max_length": 256})

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
    llm = _get_llm()
    prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "You are a short expert validator. Read the article below and answer in JSON form with fields:\n"
            '{"relevant": "yes/no", "category": "one-word-category", "safe": "yes/no", "comment": "short reason"}\n\n'
            "Article:\n\n{text}\n\n"
            "Answer now:"
        )
    )
    prompt_text = prompt.format(text=text)
    try:
        resp = llm.invoke(prompt_text)
    except Exception:
        try:
            resp = llm(prompt_text)
        except Exception:
            resp = ""

    out = {"relevant": False, "category": "unknown", "safe": True, "comment": ""}

    try:
        low = resp.lower()
        out["relevant"] = '"relevant": "yes"' in low or "relevant" in low and "yes" in low.split("relevant",1)[-1][:10]
        import re
        m = re.search(r'"category"\s*:\s*"([^"]+)"', resp)
        if m:
            out["category"] = m.group(1)
        out["safe"] = not ('"safe": "no"' in low or "safe" in low and "no" in low.split("safe",1)[-1][:10])
        out["comment"] = resp.strip().replace("\n", " ")[:500]
    except Exception:
        pass

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
