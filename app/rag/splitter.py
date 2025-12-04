"""
splitter.py
-----------
Splits long news articles into smaller chunks.

Why?
- Long documents are hard to embed
- RAG works best with chunks (300–800 tokens)
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text_into_chunks(documents):
    """
    Takes list of long text documents → returns list of small chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,     # each chunk = 800 characters
        chunk_overlap=100,  # little overlap improves context
        separators=["\n\n", "\n", ".", " "]  # logical breakpoints
    )

    chunks = splitter.split_documents(documents)
    return chunks
