# 🏥 Mia RAG System - Complete Guide

> **Medical Intelligence Assistant** with RAG (Retrieval Augmented Generation)
>
> University of Pécs | Faculty of Pharmacy | Version 6.3b

---

## 📚 فهرست

1. [درباره پروژه](#درباره-پروژه)
2. [ساختار پروژه](#ساختار-پروژه)
3. [نصب و راه‌اندازی Local](#نصب-و-راه‌اندازی-local)
4. [استفاده](#استفاده)
5. [Deploy Production](#deploy-production)
6. [ادغام با Flutter](#ادغام-با-flutter)
7. [API Documentation](#api-documentation)
8. [هزینه‌ها](#هزینه‌ها)

---

## درباره پروژه

**Mia** یک دستیار هوشمند پزشکی است که:
- از RAG استفاده می‌کنه برای پاسخ دقیق بر اساس مستندات دارویی
- پشتیبانی از زبان فارسی و انگلیسی
- طراحی شده برای دانشجویان و متخصصین داروسازی
- امنیت بالا: هرگز تشخیص یا نسخه نمی‌دهد

### تکنولوژی‌ها

- **Backend:** Python, Flask, LangChain
- **Vector DB:** ChromaDB
- **Embeddings:** HuggingFace Sentence Transformers
- **LLM:** OpenAI GPT-4o-mini
- **Frontend:** Flutter (جداگانه)

---

## ساختار پروژه

```
docs/
├── data/                              # مستندات پزشکی (16 فایل PDF)
│   ├── Pharmaceutical Technology.pdf
│   ├── Rang_and_Dales_Pharmacology.pdf
│   ├── Week 1-6 materials
│   ├── Prescriptions
│   └── mia_prompt_v6_3b.txt
│
├── vector_db/                         # دیتابیس وکتور (5022 chunks)
│
├── dataset.py                         # ساخت دیتابیس
├── query_rag.py                       # CLI interface
├── api_server.py                      # Development API
├── api_server_production.py           # Production API ⭐
│
├── flutter_example.dart               # کد نمونه Flutter
├── API_INTEGRATION.md                 # راهنمای ادغام
├── DEPLOYMENT.md                      # راهنمای deploy ⭐
│
├── requirements.txt                   # Python dependencies
├── Procfile                          # Railway/Heroku config
├── railway.json                      # Railway config
├── build.sh                          # Build script
├── .env.example                      # Environment variables template
└── .gitignore                        # Git ignore rules
```

---

## نصب و راه‌اندازی Local

### پیش‌نیازها

- Python 3.10+
- pip
- OpenAI API Key

### قدم‌ها

```bash
# 1. کلون یا دانلود پروژه
cd /Users/mrbna/StudioProjects/mia_dataset/docs

# 2. نصب dependencies
pip install -r requirements.txt

# 3. تنظیم API key
export OPENAI_API_KEY='your-api-key-here'
# یا اضافه کن به ~/.zshrc برای دائمی شدن

# 4. ساخت دیتابیس (اگه نساختی)
python3 dataset.py

# 5. تست CLI
python3 query_rag.py "What is aspirin?"

# 6. اجرای API server
python3 api_server.py
```

---

## استفاده

### 1. Command Line Interface

**سوال تکی:**
```bash
python3 query_rag.py "What are suppositories?"
```

**سوال فارسی:**
```bash
python3 query_rag.py "آسپرین چطور کار می‌کنه؟"
```

**حالت تعاملی:**
```bash
python3 query_rag.py
# بعد چند تا سوال پشت سر هم بپرس
```

### 2. API Server (Local)

```bash
# اجرا
python3 api_server.py

# تست
curl http://localhost:5000/health

# سوال
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is aspirin?",
    "language": "en"
  }'
```

---

## Deploy Production

### روش پیشنهادی: Railway.app

**چرا Railway؟**
- ✅ Deploy با git push
- ✅ $5-20/ماه
- ✅ Auto-scaling
- ✅ SSL رایگان
- ✅ مناسب برای 1000 کاربر

**مراحل کامل در:** `DEPLOYMENT.md`

**خلاصه:**
```bash
# 1. Push به GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# 2. در Railway.app:
#    - New Project → Deploy from GitHub
#    - Set environment variables
#    - Deploy!

# 3. تست production
curl https://your-app.railway.app/health
```

---

## ادغام با Flutter

### قدم 1: کپی کردن Service

فایل `flutter_example.dart` رو به پروژه Flutter کپی کن.

### قدم 2: نصب Dependencies

```yaml
# pubspec.yaml
dependencies:
  http: ^1.1.0
```

### قدم 3: استفاده

```dart
final miaService = MiaRagService(
  baseUrl: 'https://your-app.railway.app',
);

// پرسیدن سوال
final response = await miaService.askQuestion(
  question: "What is aspirin used for?",
  language: "en",
);

print(response.answer);
print(response.sources);
```

### مثال کامل Widget

```dart
class MiaChatScreen extends StatefulWidget {
  @override
  _MiaChatScreenState createState() => _MiaChatScreenState();
}

class _MiaChatScreenState extends State<MiaChatScreen> {
  final MiaRagService _mia = MiaRagService();
  String _answer = '';
  bool _loading = false;

  Future<void> _ask(String question) async {
    setState(() => _loading = true);

    final response = await _mia.askQuestion(
      question: question,
      language: "en",
    );

    setState(() {
      _answer = response.answer;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Mia Assistant')),
      body: Column(
        children: [
          if (_loading) CircularProgressIndicator(),
          if (_answer.isNotEmpty) Text(_answer),
          TextField(
            onSubmitted: _ask,
            decoration: InputDecoration(hintText: 'Ask Mia...'),
          ),
        ],
      ),
    );
  }
}
```

جزئیات بیشتر در: `API_INTEGRATION.md`

---

## API Documentation

### Endpoints

#### `GET /health`
بررسی سلامت سیستم

**Response:**
```json
{
  "status": "healthy",
  "version": "6.3b",
  "database": "loaded",
  "openai": "ready"
}
```

#### `POST /query`
پرسیدن سوال از Mia

**Request:**
```json
{
  "question": "What is aspirin?",
  "language": "en",
  "top_k": 5,
  "use_cache": true
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Aspirin is a medication...",
  "sources": [
    {"file": "Pharmacology.pdf", "page": 45}
  ],
  "question": "What is aspirin?",
  "language": "en",
  "cached": false
}
```

#### `POST /search`
جستجو در اسناد (بدون OpenAI)

**Request:**
```json
{
  "query": "aspirin",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "content": "Text content...",
      "source": "file.pdf",
      "page": 10
    }
  ],
  "count": 5
}
```

### Rate Limits

- **General:** 100 requests/hour per IP
- **Query:** 30 requests/minute per IP
- **Search:** 60 requests/minute per IP

---

## هزینه‌ها

### برای 1000 کاربر (با 10 سوال/روز/کاربر)

**Hosting (Railway.app):**
- Starter: $5/ماه
- Pro: $20/ماه (پیشنهادی)

**OpenAI API:**
- 10,000 سوال/روز
- با 50% cache hit: ~5,000 API calls/روز
- GPT-4o-mini: ~$0.15 per 1M tokens
- **تخمین:** $30-50/ماه

**جمع کل:** $35-70/ماه

### کاهش هزینه

1. **Caching:** در production API فعاله (50% کاهش)
2. **Rate Limiting:** جلوگیری از abuse
3. **Model کوچکتر:** استفاده از gpt-4o-mini به جای gpt-4
4. **Batch Processing:** group کردن سوالات مشابه

---

## 🔒 امنیت

- ✅ API key فقط روی server
- ✅ Rate limiting فعال
- ✅ CORS configured
- ✅ Input validation
- ✅ Error handling
- ⚠️ Authentication: برای production اضافه کن

---

## 📊 آمار پروژه

- **📄 اسناد:** 16 فایل PDF
- **🧩 Chunks:** 5,022 تکه متنی
- **📚 موضوعات:** Pharmacology, Technology, Prescriptions
- **🌍 زبان‌ها:** English + Persian
- **🎯 کاربران هدف:** دانشجویان و pharmacist ها

---

## 🛠️ Troubleshooting

### مشکل: "OPENAI_API_KEY not found"
```bash
export OPENAI_API_KEY='your-key'
source ~/.zshrc
```

### مشکل: Vector DB load نمیشه
```bash
rm -rf vector_db/
python3 dataset.py
```

### مشکل: Out of memory
- Upgrade hosting plan
- یا کاهش embedding model size

### مشکل: Slow responses
- چک کن cache کار می‌کنه
- افزایش workers در gunicorn
- استفاده از Redis cache

---

## 📈 Roadmap

- [ ] Redis cache برای production
- [ ] Authentication system
- [ ] Admin dashboard
- [ ] Usage analytics
- [ ] Voice input integration
- [ ] Multi-language embeddings
- [ ] Fine-tuned model
- [ ] Mobile offline mode

---

## 👥 Contributors

- **Author:** H.M. (University of Pécs)
- **Supervisor:** K.P.
- **Version:** 6.3b - "Voice-Aware Clinical Assistant"

---

## 📄 License

Educational use only - University of Pécs

---

## 🆘 پشتیبانی

- **Documentation:** این فایل + `DEPLOYMENT.md` + `API_INTEGRATION.md`
- **Issues:** GitHub Issues
- **Email:** [your-email]

---

**موفق باشی! 🚀**
