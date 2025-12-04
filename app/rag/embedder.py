"""
embedder.py
-----------
Loads embedding model used to convert text → vectors.

We use a FREE HuggingFace Model:
- all-MiniLM-L6-v2  (small, fast, accurate)
"""

from langchain_community.embeddings import HuggingFaceEmbeddings


def get_embedding_model():
    """
    Returns a FREE encoder model that can embed text chunks.
    """

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embedding_model
