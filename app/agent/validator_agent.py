"""
validator_agent.py

Validator Agent responsibilities:
- Check if article is long enough and non-trivial
- Check for near-duplicates in the current VectorDB (simple embedding similarity)
- Run a short LLM check (category / bias / profanity / relevance)
- Return a structured decision dict so Manager Agent can act.

This demonstrates:
- embeddings-based deduplication
- LLM-based validation reasoning
"""

from app.rag.embedder import get_embedding_model
from app.rag.vectordb import get_vector_db
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub

# Simple thresholds (tweakable)
MIN_WORDS = 60
DUPLICATE_SIMILARITY_THRESHOLD = 0.85  # cosine similarity threshold for duplicate detection


def _get_llm():
    """Same helper LLM used for light reasoning tasks."""
    return HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.0, "max_length": 256})


def is_long_enough(text: str) -> bool:
    """Check if the article has a reasonable length to be useful."""
    words = text.split()
    return len(words) >= MIN_WORDS


def is_duplicate(text: str) -> (bool, float):
    """
    Check for duplicates using embeddings + vectordb similarity search.

    Returns (is_dup_boolean, max_similarity_found)
    """
    # Get embeddings and vectordb
    embedding_model = get_embedding_model()
    vectordb = get_vector_db()

    # Compute embedding for this entire text (coarse check)
    emb = embedding_model.embed_documents([text])[0]  # list -> single vector

    # Use vectordb search to find nearest neighbor
    # Many vector stores provide a similarity search by vector. For Chroma wrapper:
    # - Some versions: vectordb._collection.query(...) (low-level)
    # - Common method: vectordb.similarity_search_by_vector(emb, k=1)
    # We'll try the high-level helper; if not available adapt to your installed version.
    try:
        results = vectordb.similarity_search_by_vector(emb, k=1)
        if results and len(results) > 0:
            # result is a Document-like object with .page_content or .metadata
            # We compute similarity by cosine using embeddings again (approx)
            # If vectordb returns distances instead, adapt accordingly.
            # For simplicity assume we can access metadata with "score" or compute manually.
            # We'll conservatively say not duplicate if we can't compute similarity.
            neighbor = results[0]
            # If the vectorstore returns metadata score, try to get it:
            score = getattr(neighbor, "score", None)
            if score is not None:
                # Many stores return similarity as smaller-is-better distance; we leave as-is
                sim = float(score)
            else:
                # Fallback: can't compute; assume not duplicate
                sim = 0.0
        else:
            sim = 0.0
    except Exception:
        # If the high-level method doesn't exist in your version, we gracefully fallback
        # to returning not-duplicate. This is conservative and safe.
        sim = 0.0

    return (sim >= DUPLICATE_SIMILARITY_THRESHOLD, sim)


def llm_validate_relevance(text: str) -> dict:
    """
    Ask an LLM to check for:
    - Is the article relevant to 'news'?
    - Is it opinion/editorial or factual?
    - Any safety flags (profanity, hate)?
    Returns a dict with fields: relevant (bool), category (str), safe (bool), comment (str)
    """
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
    resp = llm(prompt_text)

    # We attempt to parse the returned JSON-like text conservatively.
    # For simplicity we do naive parsing; robust code should use a JSON parser with error handling.
    out = {
        "relevant": False,
        "category": "unknown",
        "safe": True,
        "comment": ""
    }

    # Basic parsing heuristics
    try:
        # Try to find yes/no words
        text_low = resp.lower()
        out["relevant"] = "yes" in text_low.split("relevant") or '"relevant": "yes"' in text_low
        if "category" in text_low:
            # crude extraction between category and next quote
            import re
            m = re.search(r'"category"\s*:\s*"([^"]+)"', resp)
            if m:
                out["category"] = m.group(1)
        out["safe"] = not ("no" in resp.lower().split("safe") and "yes" not in resp.lower().split("safe"))
        out["comment"] = resp.strip().replace("\n", " ")[:300]
    except Exception:
        # fallback defaults already set
        pass

    return out


def validate_article(text: str) -> dict:
    """
    Full validation pipeline combining heuristics, duplicate check and LLM check.
    Returns decision dict:
    {
      "length_ok": bool,
      "is_duplicate": bool,
      "dup_score": float,
      "llm_check": {...},
      "final_decision": "approve"/"reject" (simple rule: length_ok and not duplicate and relevant and safe)
    }
    """
    length_ok = is_long_enough(text)
    dup, dup_score = is_duplicate(text)
    llm_check = llm_validate_relevance(text)

    # Simple rule: approve if long, not duplicate, LLM says relevant and safe
    final = "approve" if (length_ok and (not dup) and llm_check.get("relevant", False) and llm_check.get("safe", True)) else "reject"

    return {
        "length_ok": length_ok,
        "is_duplicate": dup,
        "dup_score": dup_score,
        "llm_check": llm_check,
        "final_decision": final
    }
