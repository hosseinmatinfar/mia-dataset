#!/bin/bash
set -e

echo "🚀 Starting Mia RAG System build..."
echo ""

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Build vector database
echo ""
echo "🔨 Building vector database from documents..."
python3 dataset.py

echo ""
echo "✅ Build completed successfully!"
echo "🎉 Mia RAG System is ready to deploy!"
