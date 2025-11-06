# 🏥 Mia RAG System

> Medical Intelligence Assistant with Retrieval Augmented Generation
>
> **University of Pécs** | Faculty of Pharmacy | Version 6.3b

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)

---

## 📖 Overview

**Mia** is an AI-powered medical assistant for pharmaceutical education and clinical support. Uses RAG (Retrieval Augmented Generation) to provide accurate answers based on pharmaceutical textbooks and lecture materials.

### Features

- 🤖 RAG-powered responses using LangChain + ChromaDB
- 📚 5,000+ document chunks from pharmaceutical literature
- 🌍 Multilingual support (English & Persian)
- 🔒 Safety-first - never diagnoses or prescribes
- ⚡ Production-ready API with caching & rate limiting
- 📱 Flutter integration ready

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API Key
- 2GB RAM

### Installation

```bash
# Clone repository
git clone git@github.com:hosseinmatinfar/mia-dataset.git
cd mia-dataset

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='your-api-key-here'

# Build vector database
python3 dataset.py

# Run server
python3 api_server.py
```

### Test

```bash
# Health check
curl http://localhost:5000/health

# Query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is aspirin?", "language": "en"}'
```

---

## 🌐 Deployment

### Railway.app (Recommended)

1. Go to [railway.app](https://railway.app/)
2. New Project → Deploy from GitHub
3. Select `hosseinmatinfar/mia-dataset`
4. Add environment variable: `OPENAI_API_KEY`
5. Deploy!

**Full guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

### Other Platforms

- ✅ Render.com
- ✅ Heroku
- ✅ AWS/GCP
- ✅ DigitalOcean

---

## 📱 Flutter Integration

```dart
final miaService = MiaRagService(
  baseUrl: 'https://your-app.railway.app',
);

final response = await miaService.askQuestion(
  question: "What is aspirin?",
);

print(response.answer);
```

**Full guide:** [API_INTEGRATION.md](API_INTEGRATION.md)

---

## 🔌 API Endpoints

### `GET /health`
Health check

### `POST /query`
Ask question

**Request:**
```json
{
  "question": "What is aspirin?",
  "language": "en"
}
```

### `POST /search`
Search documents

---

## 💰 Cost (1000 users)

| Service | Cost/month |
|---------|------------|
| Railway Pro | $20 |
| OpenAI API | $30-50 |
| **Total** | **$50-70** |

---

## 📂 Project Structure

```
├── api_server_production.py    # Production API
├── api_server.py                # Development API
├── query_rag.py                 # CLI
├── dataset.py                   # Vector DB builder
├── flutter_example.dart         # Flutter example
├── data/                        # Documents
├── DEPLOYMENT.md               # Deploy guide
└── requirements.txt            # Dependencies
```

---

## 🔒 Security

- ✅ Environment variables for secrets
- ✅ Rate limiting
- ✅ Input validation
- ✅ CORS configured

---

## 📊 Dataset

- **Documents:** 16 PDFs
- **Chunks:** 5,022 segments
- **Topics:** Pharmacology, Technology, Prescriptions
- **Languages:** English + Persian

---

## 📖 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [API_INTEGRATION.md](API_INTEGRATION.md) - Flutter integration
- [README_COMPLETE.md](README_COMPLETE.md) - Full docs (Persian)

---

## 👥 Authors

- **Author:** H.M.
- **Supervisor:** K.P.
- **University of Pécs** | Faculty of Pharmacy

---

## 📄 License

Educational use only

---

**Made for pharmaceutical education** ❤️
