#!/usr/bin/env python3
"""
Test script to verify core functionality without HuggingFace token.
Tests vector DB, embeddings, and document storage.
"""

import sys
sys.path.insert(0, '/workspaces/GenAI-with-Agentic-AI')

from app.rag.vectordb import get_vector_db
from app.rag.embedder import get_embedding_model
from langchain_core.documents import Document

def test_embeddings():
    """Test that embeddings work"""
    print("🧪 Testing Sentence Transformers Embeddings...")
    try:
        embedder = get_embedding_model()
        test_text = "This is a test article about artificial intelligence."
        embedding = embedder.embed_query(test_text)
        print(f"✅ Embeddings working! Vector dimension: {len(embedding)}")
        return True
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False

def test_vectordb():
    """Test that vector DB works"""
    print("\n🧪 Testing ChromaDB Vector Store...")
    try:
        vectordb = get_vector_db()
        print("✅ ChromaDB initialized successfully!")
        return vectordb
    except Exception as e:
        print(f"❌ VectorDB failed: {e}")
        return None

def test_document_storage(vectordb):
    """Test storing and retrieving documents"""
    print("\n🧪 Testing Document Storage & Retrieval...")
    try:
        # Add sample documents
        sample_docs = [
            Document(
                page_content="Python is a popular programming language used for AI and machine learning.",
                metadata={"source": "test1", "title": "Python Programming"}
            ),
            Document(
                page_content="Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
                metadata={"source": "test2", "title": "Machine Learning Basics"}
            ),
            Document(
                page_content="Neural networks are computing systems inspired by biological neural networks in animal brains.",
                metadata={"source": "test3", "title": "Neural Networks"}
            ),
        ]
        
        # Store documents
        vectordb.add_documents(sample_docs)
        print(f"✅ Stored {len(sample_docs)} test documents")
        
        # Try persisting
        try:
            vectordb.persist()
            print("✅ Database persisted")
        except:
            print("ℹ️  Persistence happens automatically")
        
        # Retrieve documents
        results = vectordb.similarity_search("What is machine learning?", k=2)
        print(f"✅ Retrieved {len(results)} similar documents")
        
        for i, doc in enumerate(results, 1):
            print(f"\n  📄 Result {i}:")
            print(f"     Title: {doc.metadata.get('title', 'N/A')}")
            print(f"     Content: {doc.page_content[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Document storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vectordb_stats(vectordb):
    """Check vector DB statistics"""
    print("\n📊 Vector Database Statistics:")
    try:
        # Try to get collection stats
        try:
            collection = vectordb._collection
            count = collection.count()
            print(f"  Total documents: {count}")
        except:
            print("  (Unable to get document count)")
        
        print(f"  Storage location: vector_store/")
        print(f"  Collection name: news_articles")
        return True
    except Exception as e:
        print(f"  (Stats unavailable: {e})")
        return False

def main():
    print("=" * 60)
    print("🚀 GenAI-with-Agentic-AI - Core Functionality Test")
    print("=" * 60)
    print("\nThis test verifies the project works WITHOUT HuggingFace token")
    print("(Embeddings + Vector DB only, no LLM required)\n")
    
    # Run tests
    results = {
        "embeddings": test_embeddings(),
        "vectordb": True,
        "storage": False,
        "stats": False
    }
    
    vectordb = test_vectordb()
    if vectordb:
        results["storage"] = test_document_storage(vectordb)
        results["stats"] = test_vectordb_stats(vectordb)
    else:
        results["vectordb"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.title():20s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Core functionality works perfectly.")
        print("\n📝 Next Steps:")
        print("   1. Get HuggingFace token: https://huggingface.co/settings/tokens")
        print("   2. Export token: export HUGGINGFACEHUB_API_TOKEN='your_token'")
        print("   3. Start server: uvicorn app.main:app --reload")
        print("   4. Scrape articles: curl 'http://localhost:8000/scraper/scrape?url=...'")
        print("   5. Ask questions: curl -X POST 'http://localhost:8000/rag/ask?question=...'")
        return 0
    else:
        print("⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
