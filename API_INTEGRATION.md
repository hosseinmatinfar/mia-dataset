# راهنمای ادغام Mia RAG با پروژه Flutter

## 📋 فهرست

1. [روش‌های ادغام](#روش‌های-ادغام)
2. [راه‌اندازی API Server](#راه‌اندازی-api-server)
3. [استفاده در Flutter](#استفاده-در-flutter)
4. [استفاده از Prescription ها](#استفاده-از-prescription-ها)
5. [نکات مهم](#نکات-مهم)

---

## روش‌های ادغام

### روش 1: REST API (پیشنهادی ⭐)
- بهترین روش برای production
- مناسب برای Flutter/Mobile
- قابل استفاده از هر پلتفرمی

### روش 2: Direct Python Call
- فقط برای تست و توسعه
- کندتر از API
- محدودیت‌های امنیتی

---

## راه‌اندازی API Server

### نصب پکیج‌های اضافی:

```bash
pip install flask flask-cors
```

### اجرای API Server:

```bash
# مطمئن شو که API key تنظیم شده
source ~/.zshrc

# اجرای سرور
python3 api_server.py
```

سرور روی `http://localhost:5000` اجرا میشه.

### تست API با curl:

```bash
# Health check
curl http://localhost:5000/health

# پرسیدن سوال
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is aspirin?",
    "language": "en",
    "top_k": 5
  }'

# جستجو در اسناد
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "prescription",
    "top_k": 3
  }'
```

---

## استفاده در Flutter

### 1. اضافه کردن dependency:

در `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
```

### 2. کپی کردن کد نمونه:

فایل `flutter_example.dart` رو به پروژه‌ات اضافه کن.

### 3. تنظیم آدرس API:

```dart
final String baseUrl = 'http://YOUR_IP:5000';

// مثال‌ها:
// iOS Simulator: http://localhost:5000
// Android Emulator: http://10.0.2.2:5000
// Real Device در شبکه محلی: http://192.168.1.100:5000
```

### 4. استفاده در کد:

```dart
final miaService = MiaRagService();

// پرسیدن سوال
final response = await miaService.askQuestion(
  question: "What is aspirin used for?",
  language: "en",
);

print(response.answer);
print(response.sources);

// سوال فارسی
final faResponse = await miaService.askQuestion(
  question: "آسپرین برای چی استفاده میشه؟",
  language: "fa",
);
```

---

## استفاده از Prescription ها

فایل‌های prescription الان داخل دیتابیس هستند و می‌تونی ازشون استفاده کنی:

### نمونه سوالات:

```python
# Python
python3 query_rag.py "Show me prescription examples"
python3 query_rag.py "نمونه نسخه دارویی برای فشار خون"
python3 query_rag.py "What medications are commonly prescribed?"
```

### در Flutter:

```dart
// جستجو برای prescription ها
final results = await miaService.searchDocuments(
  query: "prescription",
  topK: 5,
);

for (var result in results.results) {
  print("Source: ${result.source}");
  print("Content: ${result.content}");
}

// پرسیدن سوال در مورد prescription
final response = await miaService.askQuestion(
  question: "What are common prescription patterns for hypertension?",
);
```

---

## نکات مهم

### امنیت 🔒

1. **Never expose API key در کد Flutter**
   - API key فقط در server (Python) باشه
   - Flutter فقط با API صحبت می‌کنه

2. **برای production:**
   - از HTTPS استفاده کن
   - Authentication اضافه کن
   - Rate limiting فعال کن

### عملکرد ⚡

1. **کش کردن:**
   ```dart
   // کش کردن سوالات متداول
   Map<String, MiaResponse> _cache = {};
   ```

2. **Loading state:**
   ```dart
   // همیشه loading state نشون بده
   setState(() { _isLoading = true; });
   ```

3. **Timeout:**
   ```dart
   final response = await http.post(...)
     .timeout(Duration(seconds: 30));
   ```

### دیپلوی 🚀

#### روش 1: Local Server (برای توسعه)
```bash
python3 api_server.py
```

#### روش 2: Deploy روی سرور (production)

**با Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

**با Docker:**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

#### روش 3: Serverless (AWS Lambda, Google Cloud Functions)
- نیاز به تنظیمات بیشتر
- مناسب برای scale بالا

---

## مثال کامل: ادغام با Mia Voice Assistant

```dart
class MiaVoiceController {
  final MiaRagService _ragService = MiaRagService();

  Future<String> processVoiceInput(String transcribedText) async {
    // 1. شناسایی intent (از prompt شما)
    final intent = _detectIntent(transcribedText);

    // 2. اگه نیاز به RAG داره
    if (intent.needsKnowledgeBase) {
      final response = await _ragService.askQuestion(
        question: transcribedText,
        language: intent.language,
      );

      // 3. ترکیب با JSON output Mia
      return _formatMiaResponse(
        answer: response.answer,
        intent: intent,
        sources: response.sources,
      );
    }

    // 4. اگه نیازی به RAG نداره، پاسخ مستقیم
    return _getDirectResponse(intent);
  }

  String _formatMiaResponse({
    required String answer,
    required Intent intent,
    required List<DocumentSource> sources,
  }) {
    // Format مطابق با mia_prompt_v6_3b.txt
    final jsonOutput = {
      "intent": intent.name,
      "channel": "medical_drug",
      "ui_action": "show_result",
      "screen_id": "chat",
      "speech": answer,
      "meta": {
        "confidence": 0.95,
        "input_mode": "voice",
        "sources": sources.map((s) => s.file).toList(),
      }
    };

    return "$answer\n${jsonEncode(jsonOutput)}";
  }
}
```

---

## سوالات متداول

### Q: چطور سرعت رو بهتر کنم?
A:
- از model کوچکتر استفاده کن (`gpt-4o-mini` به جای `gpt-4`)
- top_k رو کاهش بده (3 به جای 5)
- کش فعال کن

### Q: چطور offline کار کنه?
A:
- باید از local LLM استفاده کنی (Ollama, LLaMA)
- یا پاسخ‌های متداول رو کش کنی

### Q: چطور فارسی بهتر کار کنه?
A:
- model بهتر برای فارسی (gpt-4)
- از embedding فارسی استفاده کن
- prompt engineering بهتر

---

## پشتیبانی

اگه مشکلی داشتی:
1. چک کن که API server در حال اجراست
2. API key تنظیم شده باشه
3. Network connectivity رو چک کن
4. Log های server رو بررسی کن

برای گزارش باگ: Issues در GitHub
