"""
manager_agent.py

Manager Agent orchestrates:
1. Fetch and clean article using News Agent
2. Validate using Validator Agent
3. If approved: add to VectorDB (embedding + persist)
4. Return a summary object with status and metadata

This is the single endpoint to ingest a URL into the RAG dataset.
"""

from app.agent.news_agent import fetch_url, extract_main_text_from_html, clean_text_with_llm
from app.agent.validator_agent import validate_article
from app.rag.vectordb import get_vector_db
from app.rag.embedder import get_embedding_model
from langchain.schema import Document  # lightweight wrapper for text+metadata

def ingest_url(url: str) -> dict:
    """
    Full ingestion flow for a single URL.
    Returns a dict describing result and metadata.
    """
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

        # Save validation metadata for response
        result["metadata"]["validation"] = validation

        if validation["final_decision"] != "approve":
            result["status"] = "rejected"
            result["reason"] = validation["final_decision"]
            return result

        # 5) Persist to vector DB
        vectordb = get_vector_db()
        embedding_model = get_embedding_model()

        # We create a Document object (langchain.schema.Document) with page_content and metadata
        doc = Document(page_content=content, metadata={"source": url, "title": title})

        # Add document to vector store. Most high-level vectorstore wrappers have add_documents or add_texts.
        # We'll try add_documents first; if not available, adapt to your version (see notes below).
        try:
            vectordb.add_documents([doc])
        except Exception:
            # fallback: some versions use add_texts
            try:
                vectordb.add_texts([content], metadatas=[doc.metadata])
            except Exception as ex:
                # If both fail we surface the error (you may need to adjust to your installed Chroma wrapper API)
                result["status"] = "error"
                result["reason"] = f"vectordb_add_failed: {ex}"
                return result

        # Persist the DB (if the vectorstore requires explicit persist)
        try:
            vectordb.persist()
        except Exception:
            # if persist() is not available, ignore (some wrappers persist automatically)
            pass

        result["status"] = "ingested"
        result["metadata"]["title"] = title
        result["metadata"]["length"] = len(content.split())
        return result

    except Exception as e:
        result["status"] = "error"
        result["reason"] = str(e)
        return result
