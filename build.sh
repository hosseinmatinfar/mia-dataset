#!/bin/bash
set -e

echo "🚀 Starting Mia RAG System build..."
echo ""

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Build completed successfully!"
echo "📦 Vector database included in repository"
echo "🎉 Mia RAG System is ready to deploy!"
