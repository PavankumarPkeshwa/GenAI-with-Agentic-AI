#!/usr/bin/env python3
"""
Quick verification that dependencies are installed correctly.
"""

print("=" * 70)
print("🔍 GenAI-with-Agentic-AI - Dependency Check")
print("=" * 70)
print()

# Check imports
checks = {
    "FastAPI": False,
    "LangChain Core": False,
    "LangChain Community": False,
    "ChromaDB": False,
    "Sentence Transformers": False,
    "Transformers": False,
    "BeautifulSoup4": False,
}

try:
    import fastapi
    checks["FastAPI"] = True
    print(f"✅ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI: {e}")

try:
    import langchain_core
    checks["LangChain Core"] = True
    print(f"✅ LangChain Core {langchain_core.__version__}")
except ImportError as e:
    print(f"❌ LangChain Core: {e}")

try:
    import langchain_community
    checks["LangChain Community"] = True
    print(f"✅ LangChain Community {langchain_community.__version__}")
except ImportError as e:
    print(f"❌ LangChain Community: {e}")

try:
    import chromadb
    checks["ChromaDB"] = True
    print(f"✅ ChromaDB {chromadb.__version__}")
except ImportError as e:
    print(f"❌ ChromaDB: {e}")

try:
    import sentence_transformers
    checks["Sentence Transformers"] = True
    print(f"✅ Sentence Transformers {sentence_transformers.__version__}")
except ImportError as e:
    print(f"❌ Sentence Transformers: {e}")

try:
    import transformers
    checks["Transformers"] = True
    print(f"✅ Transformers {transformers.__version__}")
except ImportError as e:
    print(f"❌ Transformers: {e}")

try:
    import bs4
    checks["BeautifulSoup4"] = True
    print(f"✅ BeautifulSoup4 {bs4.__version__}")
except ImportError as e:
    print(f"❌ BeautifulSoup4: {e}")

print()
print("=" * 70)
passed = sum(1 for v in checks.values() if v)
total = len(checks)
print(f"📊 Result: {passed}/{total} core dependencies installed")

if passed == total:
    print("🎉 All dependencies are correctly installed!")
else:
    print("⚠️  Some dependencies are missing")

print("=" * 70)
