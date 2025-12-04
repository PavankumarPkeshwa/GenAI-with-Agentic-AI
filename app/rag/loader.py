"""
loader.py
---------
Loads raw text/data for the RAG pipeline.

Right now this loads text files from a local folder.
Later you can replace this with MongoDB fetch logic.
"""

import os

DATA_DIR = "data"


def load_documents():
    """
    Reads every .txt file inside /data folder and returns list of strings.
    Each file = one news article.
    """
    docs = []

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(DATA_DIR, filename)

            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())

    return docs
