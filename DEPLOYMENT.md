# 🚀 راهنمای Deploy کردن Mia RAG System

این راهنما برای deploy کردن سیستم RAG روی Railway.app یا Render.com

---

## 📋 پیش‌نیازها

1. حساب GitHub
2. حساب Railway.app یا Render.com
3. OpenAI API Key

---

## 🎯 روش 1: Deploy با Railway.app (پیشنهادی - ساده‌تر)

### قدم 1: آماده‌سازی Repository

```bash
# اگه git repository نداری
cd /Users/mrbna/StudioProjects/mia_dataset/docs
git init
git add .
git commit -m "Initial commit - Mia RAG System"

# ساخت repository در GitHub
# برو به github.com و یک repo جدید بساز
# بعد:
git remote add origin https://github.com/your-username/mia-rag.git
git push -u origin main
```

### قدم 2: Deploy در Railway

1. برو به https://railway.app/
2. ثبت‌نام کن با GitHub
3. کلیک کن روی "New Project"
4. انتخاب کن "Deploy from GitHub repo"
5. انتخاب کن repository که ساختی
6. Railway خودکار detect می‌کنه که Python هست

### قدم 3: تنظیم Environment Variables

در Railway dashboard:
1. برو به "Variables"
2. اضافه کن:
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   MODEL=gpt-4o-mini
   DB_PATH=vector_db
   ```

### قدم 4: Upload کردن Vector Database

**مشکل:** فایل‌های vector_db خیلی بزرگن برای git

**راه حل 1: Build کردن روی Railway** (پیشنهادی)

فایل `build.sh` بساز:
```bash
#!/bin/bash
echo "Building vector database..."
python3 dataset.py
echo "Done!"
```

در Railway settings:
- Build Command: `bash build.sh`
- Start Command: `gunicorn api_server_production:app`

**راه حل 2: Upload به Railway Volume**
1. در Railway dashboard به Variables برو
2. Mount یک Volume
3. فایل‌های vector_db رو با Railway CLI آپلود کن

### قدم 5: تست کن!

بعد از deploy، یک URL دریافت می‌کنی مثل:
```
https://mia-rag-production.up.railway.app
```

تست:
```bash
curl https://your-url.railway.app/health
```

---

## 🎯 روش 2: Deploy با Render.com

### قدم 1-2: مثل Railway (آماده‌سازی و push به GitHub)

### قدم 3: ساخت Web Service در Render

1. برو به https://render.com/
2. ثبت‌نام کن
3. "New" → "Web Service"
4. Connect کن GitHub repo رو
5. تنظیمات:
   - **Name:** mia-rag-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python3 dataset.py`
   - **Start Command:** `gunicorn api_server_production:app`
   - **Plan:** Free یا Starter ($7/ماه)

### قدم 4: Environment Variables

در Render dashboard:
```
OPENAI_API_KEY=your-key
MODEL=gpt-4o-mini
DB_PATH=vector_db
```

### قدم 5: Deploy!

Render خودکار شروع به deploy می‌کنه.

---

## 💰 مقایسه هزینه (برای 1000 کاربر)

### Railway.app
- **Starter Plan:** $5/ماه
- **Pro Plan:** $20/ماه (برای production پیشنهاد می‌شه)
- Includes: 512MB RAM, 1GB Storage

### Render.com
- **Free Tier:** $0 (محدودیت دارد، sleep بعد 15 دقیقه)
- **Starter:** $7/ماه (512MB RAM)
- **Standard:** $25/ماه (2GB RAM)

### هزینه OpenAI (مهم‌تر!)
با 1000 کاربر و 10 سوال/روز:
- 10,000 سوال/روز
- با cache 50%: ~5,000 OpenAI call/روز
- **هزینه:** ~$30-50/ماه

**جمع کل برای MVP:** $35-75/ماه

---

## 🔧 تنظیمات بهینه‌سازی

### 1. کاهش هزینه OpenAI

در `api_server_production.py` caching فعاله، اما می‌تونی:

```python
# افزایش cache size
MAX_CACHE_SIZE = 500  # از 100 به 500

# استفاده از Redis برای cache بهتر
# pip install redis
```

### 2. بهبود Performance

```python
# در api_server_production.py
# افزایش workers
# Procfile:
web: gunicorn --workers 4 --timeout 120 api_server_production:app
```

### 3. Monitoring

اضافه کردن Sentry برای error tracking:
```bash
pip install sentry-sdk[flask]
```

در کد:
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## 📱 اتصال Flutter به Production API

در Flutter:

```dart
class MiaRagService {
  // تغییر URL به production
  final String baseUrl = 'https://your-app.railway.app';
  // یا
  final String baseUrl = 'https://your-app.onrender.com';

  // بقیه کد مثل قبل...
}
```

---

## 🔒 امنیت

### 1. Rate Limiting (فعال شده)
- 100 request/hour per IP
- 30 request/minute برای /query

### 2. اضافه کردن Authentication (اختیاری برای MVP)

```python
# Simple API key authentication
@app.before_request
def check_api_key():
    if request.path not in ['/health', '/']:
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
```

در Flutter:
```dart
final response = await http.post(
  uri,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-secret-key',
  },
);
```

---

## 📊 Monitoring و Logs

### Railway Logs
```bash
# نصب Railway CLI
npm install -g @railway/cli

# Login
railway login

# دیدن logs
railway logs
```

### Render Logs
در dashboard → Logs tab

---

## 🐛 Troubleshooting

### مشکل: Vector DB load نمیشه
**راه حل:** مطمئن شو که `dataset.py` در build command اجرا شده

### مشکل: Memory Error
**راه حل:** Upgrade کن plan رو به 1GB RAM

### مشکل: Timeout Errors
**راه حل:** در `Procfile` timeout رو افزایش بده:
```
web: gunicorn --timeout 180 api_server_production:app
```

### مشکل: OpenAI API Errors
**راه حل:** چک کن environment variable درست set شده

---

## 📈 Scaling برای بیشتر از 1000 کاربر

اگه کاربرات زیاد شد:

1. **Horizontal Scaling:** افزایش تعداد instances
2. **Redis Cache:** برای cache بهتر
3. **CDN:** برای static files
4. **Load Balancer:** توزیع traffic
5. **Database Optimization:** استفاده از pgvector به جای Chroma

---

## ✅ Checklist قبل از Production

- [ ] OpenAI API key تنظیم شده
- [ ] Vector database ساخته شده
- [ ] Git repository ساخته شده
- [ ] Railway/Render account ساخته شده
- [ ] Environment variables set شده
- [ ] Health endpoint تست شده
- [ ] Flutter app به production URL متصل شده
- [ ] Rate limiting تست شده
- [ ] Error handling چک شده
- [ ] Monitoring راه‌اندازی شده

---

## 🆘 کمک بیشتر

- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs
- Mia Issues: GitHub repo issues

موفق باشی! 🚀
