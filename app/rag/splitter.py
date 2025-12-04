"""
splitter.py
-----------
Compatible with LangChain 1.x

Splits long news articles into chunks for RAG.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text_into_chunks(text_list):
    """
    Input: list[str] (raw article strings)
    Output: list[str] (chunk strings)
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )

    all_chunks = []

    for txt in text_list:
        chunks = splitter.split_text(txt)    # <-- CORRECT API
        all_chunks.extend(chunks)

    return all_chunks
