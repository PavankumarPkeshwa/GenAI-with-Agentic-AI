"""
news_agent.py

Scraper Agent:
- Fetches a URL (news page)
- Extracts main article text (using BeautifulSoup)
- Calls a small LLM prompt to "clean" the extracted text (remove nav, ads, captions)
- Returns a dictionary with cleaned text + metadata

Why use an LLM here?
- Real-world articles have noise (ads, captions, embedded tweets). LLM makes extraction robust.
- This demonstrates practical GenAI usage for data ingestion.
"""

import requests
from bs4 import BeautifulSoup
from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate

# small helper that loads the same LLM config we used elsewhere
def _get_llm():
    """
    Returns a lightweight HuggingFace LLM wrapper.
    We use the same model pattern as the RAG pipeline (flan-t5-large or similar).
    For heavier extraction you can swap to a stronger model later.
    """
    return HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.0, "max_length": 512})


def fetch_url(url: str, timeout: int = 10) -> str:
    """
    Fetch raw HTML for the given URL. Basic error handling included.
    Returns raw HTML string (or raises requests exceptions upward).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GenAI-Scraper/1.0; +https://example.com/bot)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_main_text_from_html(html: str) -> str:
    """
    Quick HTML -> text extraction using BeautifulSoup.
    This is a heuristic best-effort extractor: finds <article> tags, or falls back to main <div>.
    We keep this lightweight because the LLM will perform final cleaning.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try common article selectors first
    article = soup.find("article")
    if article:
        text = article.get_text(separator="\n", strip=True)
        if len(text) > 200:
            return text

    # Fallback: look for big <div> with many <p>
    paragraphs = soup.find_all("p")
    if paragraphs:
        pts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        # naive join; LLM will refine
        return "\n\n".join(pts)

    # If nothing found, return the body text
    body = soup.body
    return body.get_text(separator="\n", strip=True) if body else ""


def clean_text_with_llm(raw_text: str) -> str:
    """
    Uses an LLM to clean the extracted text:
    - remove navigation, ads, 'read more' text
    - join broken lines
    - ensure the output has a short title (if available) + body

    Returns cleaned text string.
    """
    llm = _get_llm()

    # Very explicit prompt: instruct the model to return a JSON-like output.
    prompt = PromptTemplate(
        input_variables=["raw"],
        template=(
            "You are a helpful text-cleaner. Input is raw extracted news HTML text that may contain nav, ads,"
            " captions, timestamps, and broken sentences. Produce a clean output with two fields:\n\n"
            "TITLE: <a concise title or empty if none>\n\n"
            "CONTENT: <cleaned article content, full sentences, no ads, no 'read more' fragments>\n\n"
            "Only output the TITLE and CONTENT blocks (no extra commentary).\n\nRAW:\n\n{raw}\n\n"
            "CLEAN OUTPUT:"
        )
    )

    # Call the LLM; the HuggingFaceHub wrapper is expected to be callable like llm(prompt_text)
    prompt_text = prompt.format(raw=raw_text)
    raw_resp = llm(prompt_text)  # returns full text
    # Simple heuristic parse: look for TITLE: and CONTENT:
    title = ""
    content = raw_resp

    # Attempt to split by our markers if present
    if "TITLE:" in raw_resp and "CONTENT:" in raw_resp:
        try:
            # naive split — the model output format should follow the instruction
            after_title = raw_resp.split("TITLE:", 1)[1]
            title_part, content_part = after_title.split("CONTENT:", 1)
            title = title_part.strip().splitlines()[0].strip()
            content = content_part.strip()
        except Exception:
            # parsing fallback: keep entire text as content
            content = raw_resp.strip()

    return {"title": title, "content": content}
