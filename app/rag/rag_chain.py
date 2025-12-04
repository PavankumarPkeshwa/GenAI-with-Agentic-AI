"""
rag_chain.py
------------
Creates the full Retrieval-Augmented Generation pipeline:
1. Retrieve relevant chunks
2. Feed them into LLM with a custom prompt
3. Generate clean factual answers
"""

from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub

from app.rag.vectordb import get_vector_db


def get_llm():
    """
    Loads a FREE HuggingFace model for Q&A.
    Model: flan-t5-large
    """
    llm = HuggingFaceHub(
        repo_id="google/flan-t5-large",
        model_kwargs={"temperature": 0.1, "max_length": 400}
    )

    return llm


def get_rag_chain():
    """
    Builds a complete RAG pipeline:
    - Retrieve context
    - Inject into prompt
    - Generate answer using LLM
    """

    vectordb = get_vector_db()
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # Custom RAG prompt
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are a News QA Agent. Use ONLY the context below.\n\n"
            "CONTEXT:\n{context}\n\n"
            "QUESTION: {question}\n\n"
            "Give a clean factual answer. No hallucination."
        )
    )

    llm = get_llm()

    rag = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    return rag
