# GenAI-with-Agentic-AI

**Building a GenAI News Intelligence System with Agentic AI + RAG**

[![Status](https://img.shields.io/badge/Status-Production_Ready-success)]()
[![Python](https://img.shields.io/badge/Python-3.12-blue)]()
[![LangChain](https://img.shields.io/badge/LangChain-1.1.0-green)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.123-red)]()

## 🎯 What is This?

An **intelligent news scraping & Q&A system** that:
- 🤖 **Autonomously scrapes** news articles from the web
- ✅ **Validates quality** using AI agents (checks length, duplicates, relevance)
- 💾 **Stores embeddings** in a vector database (ChromaDB)
- 🧠 **Answers questions** using RAG (Retrieval Augmented Generation)

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server (NO API TOKEN NEEDED! Uses local LLM)
./start.sh
# OR: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**That's it!** Visit http://localhost:8000/docs for API documentation.

> **✨ Zero Setup**: Uses google/flan-t5-base (local LLM, no API tokens required)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 WEB SCRAPING FLOW                   │
├─────────────────────────────────────────────────────┤
│  URL → News Agent → Clean → Validate → VectorDB    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   RAG Q&A FLOW                      │
├─────────────────────────────────────────────────────┤
│  Question → Search DB → Context → LLM → Answer     │
└─────────────────────────────────────────────────────┘
```

### **Components:**
- **News Agent**: Scrapes & cleans articles using LLM
- **Validator Agent**: Checks quality & prevents duplicates
- **Manager Agent**: Orchestrates the workflow
- **RAG Pipeline**: Semantic search + LLM Q&A
- **Vector DB**: ChromaDB for persistent storage

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/scraper/scrape?url=...` | GET | Scrape single article |
| `/scraper/cron` | GET | Batch scrape news sources |
| `/rag/ask?question=...` | POST | Ask questions about stored articles |

## 🧪 Testing

```bash
# Check dependencies
python3 check_deps.py

# Run core tests (no HF token needed)
python3 test_core.py

# Test server
curl http://localhost:8000/

# Scrape an article
curl "http://localhost:8000/scraper/scrape?url=https://www.bbc.com/news"

# Ask a question
curl -X POST "http://localhost:8000/rag/ask?question=What%20is%20AI"
```

## 📦 Tech Stack

- **Backend**: FastAPI + Uvicorn
- **AI Framework**: LangChain 1.1.0
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`) - 384-dim vectors
- **Vector DB**: ChromaDB (with SQLite backend)
- **LLM**: google/flan-t5-base (local, no API token needed!)
- **Scraper**: BeautifulSoup4 + Requests

## 📁 Project Structure

```
GenAI-with-Agentic-AI/
├── app/
│   ├── agent/          # AI agents (news, validator, manager)
│   ├── rag/            # RAG pipeline (embeddings, vectordb, chain)
│   ├── routes/         # API endpoints
│   ├── scraper/        # Web scraping logic
│   └── main.py         # FastAPI application
├── data/               # Local data storage
├── vector_store/       # ChromaDB persistent storage
├── requirements.txt    # Python dependencies
├── start.sh            # Quick start script
└── README.md           # This file
```

## 🚀 Features

✅ **Agentic AI Workflow** - Multi-agent system for autonomous operation  
✅ **Quality Validation** - Checks article length, duplicates, relevance  
✅ **Vector Search** - Semantic similarity using embeddings  
✅ **RAG Q&A** - Natural language question answering  
✅ **Persistent Storage** - ChromaDB for long-term storage  
✅ **REST API** - Easy integration with FastAPI  
✅ **Modern Stack** - LangChain 1.x compatible  
✅ **Zero API Tokens** - Uses local LLM (google/flan-t5-base)  

## 📖 Documentation

- **[FINAL_VERDICT.md](FINAL_VERDICT.md)** - Complete project assessment & testing results
- **[PROJECT_WALKTHROUGH.md](PROJECT_WALKTHROUGH.md)** - Deep code explanations (1073 lines)
- **[VISUAL_GUIDE.md](VISUAL_GUIDE.md)** - Flowcharts, diagrams & architecture pictures
- **[NO_TOKEN_NEEDED.md](NO_TOKEN_NEEDED.md)** - Local LLM implementation guide
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Detailed status report
- **API Docs**: http://localhost:8000/docs (when server is running)

## 🔧 Configuration

**No configuration needed!** The project uses sensible defaults:

```bash
# Optional: Customize in .env (if needed)
CHROMA_DIR=vector_store              # Vector DB location
COLLECTION_NAME=news_articles        # DB collection name
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Embeddings
LLM_MODEL=google/flan-t5-base       # Local LLM model
```

> **Note**: No HuggingFace API token needed - uses local LLM!

## 🐛 Troubleshooting

**Server won't start?**
- Check dependencies: `python3 check_deps.py`
- Install missing packages: `pip install -r requirements.txt`

**Model download slow?**
- First run downloads google/flan-t5-base (~990MB)
- Subsequent runs use cached model (~2-3 seconds inference)

**RAG returns empty results?**
- Scrape some articles first using `/scraper/scrape`
- Or use `/scraper/cron` for batch scraping
- Articles are stored in `vector_store/chroma.sqlite3`

## 🧪 Full Test Suite

```bash
# Check all dependencies (should show 7/7 ✅)
python3 check_deps.py

# Test local LLM (verify model downloads and works)
python3 test_local_llm.py

# Run comprehensive tests
python3 test_core.py
```

## 📊 Status

**✅ PRODUCTION READY** - Fully tested with no API token requirements

See [FINAL_VERDICT.md](FINAL_VERDICT.md) for complete assessment.

## 📄 License

MIT License - feel free to use for learning and projects!
