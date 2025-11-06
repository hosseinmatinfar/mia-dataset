#!/usr/bin/env python3
"""
Production-ready REST API Server for Mia RAG System
Optimized for Railway/Render deployment with caching and rate limiting
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import lru_cache
import os
import hashlib
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Rate limiting: 100 requests per hour per IP
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Configuration
DB_PATH = os.getenv("DB_PATH", "vector_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Mia's Identity
MIA_IDENTITY = """Mia (Medical Intelligence Assistant) — Version 6.3 b

Description:
Mia is a multilingual, empathetic, and safety-focused AI agent developed for pharmaceutical, pharmacological, and medical education and clinical support.

Safety & Ethics:
- Never diagnose or prescribe.
- Always add: "Final decisions must be made by a doctor or pharmacist."
"""

# Simple in-memory cache for responses
response_cache = {}
MAX_CACHE_SIZE = 100

def get_cache_key(question, language):
    """Generate cache key from question"""
    content = f"{question}_{language}"
    return hashlib.md5(content.encode()).hexdigest()

# Load vector DB once at startup
try:
    logger.info("🔄 Loading vector database...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    logger.info("✅ Vector database loaded successfully!")
except Exception as e:
    logger.error(f"❌ Failed to load vector database: {e}")
    db = None

# OpenAI client
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✅ OpenAI client initialized")
else:
    logger.warning("⚠️ OPENAI_API_KEY not set!")
    client = None

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "name": "Mia RAG API",
        "version": "6.3b",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST)",
            "search": "/search (POST)"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Railway/Render"""
    status = {
        "status": "healthy",
        "message": "Mia RAG API is running",
        "version": "6.3b",
        "database": "loaded" if db else "not loaded",
        "openai": "ready" if client else "not configured",
        "cache_size": len(response_cache)
    }

    if not db or not client:
        return jsonify(status), 503  # Service Unavailable

    return jsonify(status), 200

@app.route('/query', methods=['POST'])
@limiter.limit("30 per minute")  # More strict limit for query endpoint
def query():
    """
    Main query endpoint with caching

    Request body:
    {
        "question": "What is aspirin?",
        "language": "en",
        "top_k": 5,
        "use_cache": true
    }
    """
    try:
        if not db or not client:
            return jsonify({
                "success": False,
                "error": "Service not fully initialized"
            }), 503

        data = request.json
        question = data.get('question')
        language = data.get('language', 'en')
        top_k = data.get('top_k', 5)
        use_cache = data.get('use_cache', True)

        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Check cache
        cache_key = get_cache_key(question, language)
        if use_cache and cache_key in response_cache:
            logger.info(f"✅ Cache hit for question: {question[:50]}...")
            cached = response_cache[cache_key]
            cached['cached'] = True
            return jsonify(cached)

        logger.info(f"🔍 Processing question: {question[:50]}...")

        # Search for relevant documents
        docs = db.similarity_search(question, k=top_k)

        if not docs:
            return jsonify({
                "success": False,
                "error": "No relevant documents found"
            }), 404

        # Prepare context
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])

        # Prepare sources
        sources = [
            {
                "file": os.path.basename(doc.metadata.get('source', 'Unknown')),
                "page": doc.metadata.get('page', None)
            }
            for doc in docs
        ]

        # Prepare system prompt
        system_prompt = f"""{MIA_IDENTITY}

You are answering questions based on pharmaceutical and medical educational materials.

Instructions:
- Use the provided context to answer questions accurately
- If the answer is not in the context, say so clearly
- Always maintain Mia's empathetic and safety-focused tone
- Include the disclaimer about final decisions being made by doctors/pharmacists
- Respond in {"Persian/Farsi" if language == "fa" else "English"}
"""

        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Context from documents:
{context}

---

Question: {question}

Please answer based on the context provided above."""}
        ]

        # Query OpenAI
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        answer = response.choices[0].message.content

        # Prepare response
        result = {
            "success": True,
            "answer": answer,
            "sources": sources,
            "question": question,
            "language": language,
            "cached": False
        }

        # Cache the response
        if len(response_cache) >= MAX_CACHE_SIZE:
            # Remove oldest entry
            response_cache.pop(next(iter(response_cache)))
        response_cache[cache_key] = result

        logger.info(f"✅ Successfully answered question")
        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error processing query: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/search', methods=['POST'])
@limiter.limit("60 per minute")
def search():
    """
    Search for relevant documents only (no OpenAI call)

    Request body:
    {
        "query": "aspirin",
        "top_k": 5
    }
    """
    try:
        if not db:
            return jsonify({
                "success": False,
                "error": "Database not loaded"
            }), 503

        data = request.json
        query_text = data.get('query')
        top_k = data.get('top_k', 5)

        if not query_text:
            return jsonify({"error": "Query is required"}), 400

        logger.info(f"🔍 Searching for: {query_text[:50]}...")

        # Search for relevant documents
        docs = db.similarity_search(query_text, k=top_k)

        # Prepare results
        results = [
            {
                "content": doc.page_content[:500] + "...",
                "source": os.path.basename(doc.metadata.get('source', 'Unknown')),
                "page": doc.metadata.get('page', None)
            }
            for doc in docs
        ]

        logger.info(f"✅ Found {len(results)} documents")
        return jsonify({
            "success": True,
            "results": results,
            "query": query_text,
            "count": len(results)
        })

    except Exception as e:
        logger.error(f"❌ Error searching: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear response cache"""
    response_cache.clear()
    logger.info("🗑️ Cache cleared")
    return jsonify({
        "success": True,
        "message": "Cache cleared"
    })

@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    return jsonify({
        "cache_size": len(response_cache),
        "max_cache_size": MAX_CACHE_SIZE
    })

@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit error handler"""
    logger.warning(f"⚠️ Rate limit exceeded: {request.remote_addr}")
    return jsonify({
        "success": False,
        "error": "Rate limit exceeded. Please try again later."
    }), 429

if __name__ == '__main__':
    if not OPENAI_API_KEY:
        logger.error("❌ Error: OPENAI_API_KEY not set")
        exit(1)

    logger.info("\n" + "="*60)
    logger.info("🏥 Mia RAG API Server (Production)")
    logger.info("="*60)
    logger.info(f"📍 Server starting on port: {PORT}")
    logger.info(f"🤖 Using model: {MODEL}")
    logger.info(f"💾 Database path: {DB_PATH}")
    logger.info(f"🔒 Rate limiting: Enabled")
    logger.info(f"📦 Caching: Enabled (max {MAX_CACHE_SIZE} items)")
    logger.info("="*60 + "\n")

    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
