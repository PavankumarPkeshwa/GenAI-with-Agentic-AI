"""
rag_chain.py
------------
Fully compatible with LangChain 1.1.0
Manual RAG pipeline without deprecated RetrievalQA class.
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from app.utils.local_llm import LocalLLM

from app.rag.vectordb import get_vector_db


def get_llm():
    """
    Loads a local HuggingFace model for Q&A.
    Model is downloaded and cached locally (no API token needed).
    """
    return LocalLLM(
        model_name="google/flan-t5-base",
        max_length=512
    )


def build_prompt():
    """
    Custom RAG prompt
    """
    return PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are a factual News QA Agent.\n"
            "Use ONLY the context provided.\n\n"
            "CONTEXT:\n{context}\n\n"
            "QUESTION: {question}\n\n"
            "Answer concisely and do not hallucinate."
        )
    )


def format_docs(docs):
    """
    Combine retrieved documents into a single context string.
    For LangChain 1.x Document objects.
    """
    texts = []
    for d in docs:
        content = getattr(d, "page_content", None) or getattr(d, "content", None)
        if content:
            texts.append(content)
    return "\n\n".join(texts)


def get_rag_chain():
    """
    Creates a complete RAG chain that:
    - retrieves documents
    - formats them
    - injects into prompt
    - generates answer with LLM
    """

    vectordb = get_vector_db()
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    llm = get_llm()
    prompt = build_prompt()

    # RAG pipeline:
    # question -> {"context": retriever(question), "question": question} -> prompt -> llm
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
    )

    return rag_chain
