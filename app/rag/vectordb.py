"""
vectordb.py
-----------
Creates or loads a Chroma Vector Database.

Chroma stores:
- embeddings
- metadata
- document IDs
"""

import os
from langchain_community.vectorstores import Chroma
from app.rag.embedder import get_embedding_model

CHROMA_DIR = "vector_store"


def get_vector_db():
    """
    Returns a Chroma database object.
    If the folder doesn't exist, it creates one.
    """
    if not os.path.exists(CHROMA_DIR):
        os.makedirs(CHROMA_DIR)

    embedding_model = get_embedding_model()

    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model
    )

    return vectordb
