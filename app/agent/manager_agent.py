"""
manager_agent.py
Manager: scrape -> clean -> validate -> persist to vectordb
"""

from app.agent.news_agent import fetch_url, extract_main_text_from_html, clean_text_with_llm
from app.agent.validator_agent import validate_article
from app.rag.vectordb import get_vector_db
from app.rag.embedder import get_embedding_model
from langchain_core.documents import Document
  # langchain 1.x

def ingest_url(url: str) -> dict:
    result = {"url": url, "status": "error", "reason": None, "metadata": {}}

    try:
        # 1) Fetch HTML
        html = fetch_url(url)

        # 2) Extract main text heuristically
        raw_text = extract_main_text_from_html(html)
        if not raw_text or len(raw_text) < 20:
            result["status"] = "error"
            result["reason"] = "no_text_extracted"
            return result

        # 3) Clean text via LLM to improve quality
        cleaned = clean_text_with_llm(raw_text)
        title = cleaned.get("title", "") or ""
        content = cleaned.get("content", "").strip()

        if not content:
            result["status"] = "error"
            result["reason"] = "empty_after_cleaning"
            return result

        # 4) Validate article
        validation = validate_article(content)
        result["metadata"]["validation"] = validation

        if validation["final_decision"] != "approve":
            result["status"] = "rejected"
            result["reason"] = validation["final_decision"]
            return result

        # 5) Persist to vector DB
        vectordb = get_vector_db()
        embedding_model = get_embedding_model()

        # Build Document (langchain_core.Document)
        doc = Document(page_content=content, metadata={"source": url, "title": title})

        # Try different add APIs depending on installed wrapper
        add_succeeded = False
        try:
            # Preferred: add_documents (many wrappers implement this)
            vectordb.add_documents([doc])
            add_succeeded = True
        except Exception:
            try:
                # Fallback: add_texts + metadatas
                vectordb.add_texts([content], metadatas=[doc.metadata])
                add_succeeded = True
            except Exception as ex:
                result["status"] = "error"
                result["reason"] = f"vectordb_add_failed: {ex}"
                return result

        # Persist DB if supported
        try:
            vectordb.persist()
        except Exception:
            # some wrappers persist automatically
            pass

        result["status"] = "ingested"
        result["metadata"]["title"] = title
        result["metadata"]["length"] = len(content.split())
        return result

    except Exception as e:
        result["status"] = "error"
        result["reason"] = str(e)
        return result
