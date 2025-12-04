#!/bin/bash
# Quick Start Script for GenAI-with-Agentic-AI

set -e  # Exit on error

echo "========================================================================"
echo "🚀 GenAI-with-Agentic-AI - Quick Start"
echo "========================================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "📝 To use LLM features, you need a HuggingFace token:"
    echo "   1. Visit: https://huggingface.co/settings/tokens"
    echo "   2. Create a free token"
    echo "   3. Create .env file:"
    echo "      cp .env.example .env"
    echo "   4. Edit .env and add your token"
    echo ""
    read -p "Continue without token? (server will start but LLM features won't work) [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Please set up .env file first."
        exit 1
    fi
else
    echo "✅ Found .env file"
    source .env
    
    if [ -z "$HUGGINGFACEHUB_API_TOKEN" ] || [ "$HUGGINGFACEHUB_API_TOKEN" = "hf_your_token_here" ]; then
        echo "⚠️  HuggingFace token not configured in .env"
        echo "   LLM features will not work!"
        echo ""
    else
        echo "✅ HuggingFace token configured"
    fi
fi

echo ""
echo "📦 Checking dependencies..."

if ! python3 -c "import fastapi, langchain, chromadb" 2>/dev/null; then
    echo "⚠️  Dependencies not installed!"
    echo ""
    read -p "Install dependencies now? [Y/n] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "Installing dependencies..."
        pip install -r requirements.txt
        echo "✅ Dependencies installed"
    else
        echo "❌ Cannot start without dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies installed"
fi

echo ""
echo "========================================================================"
echo "🎯 Starting Server..."
echo "========================================================================"
echo ""
echo "Server will be available at:"
echo "  📍 http://localhost:8000"
echo "  📍 http://0.0.0.0:8000"
echo ""
echo "API Documentation:"
echo "  📚 http://localhost:8000/docs (Swagger UI)"
echo "  📚 http://localhost:8000/redoc (ReDoc)"
echo ""
echo "Available endpoints:"
echo "  GET  /                      - Health check"
echo "  GET  /scraper/scrape?url=   - Scrape article"
echo "  GET  /scraper/cron          - Batch scrape"
echo "  POST /rag/ask?question=     - Ask questions"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================================================"
echo ""

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
