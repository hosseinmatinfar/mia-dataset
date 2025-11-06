#!/usr/bin/env python3
"""
REST API Server for Mia RAG System
Use this to integrate with Flutter/Mobile apps
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # برای استفاده از Flutter

# Configuration
DB_PATH = "vector_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

# Mia's Identity
MIA_IDENTITY = """Mia (Medical Intelligence Assistant) — Version 6.3 b

Description:
Mia is a multilingual, empathetic, and safety-focused AI agent developed for pharmaceutical, pharmacological, and medical education and clinical support.

Safety & Ethics:
- Never diagnose or prescribe.
- Always add: "Final decisions must be made by a doctor or pharmacist."
"""

# Load vector DB once at startup
print("🔄 Loading vector database...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
print("✅ Vector database loaded!")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Mia RAG API is running",
        "version": "6.3b"
    })

@app.route('/query', methods=['POST'])
def query():
    """
    Main query endpoint

    Request body:
    {
        "question": "What is aspirin?",
        "language": "en",  // optional: "en" or "fa"
        "top_k": 5,        // optional: number of docs to retrieve
        "conversation_history": []  // optional: previous messages
    }
    """
    try:
        data = request.json
        question = data.get('question')
        language = data.get('language', 'en')
        top_k = data.get('top_k', 5)
        conversation_history = data.get('conversation_history', [])

        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Search for relevant documents
        docs = db.similarity_search(question, k=top_k)

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
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current question with context
        user_message = f"""Context from documents:
{context}

---

Question: {question}

Please answer based on the context provided above."""

        messages.append({"role": "user", "content": user_message})

        # Query OpenAI
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        answer = response.choices[0].message.content

        # Return response
        return jsonify({
            "success": True,
            "answer": answer,
            "sources": sources,
            "question": question,
            "language": language
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/search', methods=['POST'])
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
        data = request.json
        query_text = data.get('query')
        top_k = data.get('top_k', 5)

        if not query_text:
            return jsonify({"error": "Query is required"}), 400

        # Search for relevant documents
        docs = db.similarity_search(query_text, k=top_k)

        # Prepare results
        results = [
            {
                "content": doc.page_content[:500] + "...",  # First 500 chars
                "source": os.path.basename(doc.metadata.get('source', 'Unknown')),
                "page": doc.metadata.get('page', None)
            }
            for doc in docs
        ]

        return jsonify({
            "success": True,
            "results": results,
            "query": query_text,
            "count": len(results)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not set")
        exit(1)

    print("\n" + "="*60)
    print("🏥 Mia RAG API Server")
    print("="*60)
    print("📍 Server will run on: http://localhost:5000")
    print("\n📋 Available endpoints:")
    print("  GET  /health       - Health check")
    print("  POST /query        - Ask Mia a question")
    print("  POST /search       - Search documents only")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
