# Mia RAG System - دستیار هوشمند پزشکی

سیستم RAG (Retrieval Augmented Generation) برای پاسخگویی به سوالات پزشکی/دارویی بر اساس اسناد آموزشی

## نصب

```bash
pip install -r requirements.txt
```

## تنظیمات

1. API Key OpenAI رو تنظیم کن:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## استفاده

### ساخت دیتاست (فقط یکبار):
```bash
python3 dataset.py
```

### حالت تعاملی (پرسش و پاسخ):
```bash
python3 query_rag.py
```

### تک سوال:
```bash
python3 query_rag.py "What is the mechanism of action of aspirin?"
```

### مثال فارسی:
```bash
python3 query_rag.py "آسپرین چطور کار می‌کنه؟"
```

## ساختار پروژه

```
.
├── data/                  # فایل‌های PDF و TXT
├── vector_db/            # دیتابیس وکتور (Chroma)
├── dataset.py            # ساخت دیتاست
├── query_rag.py          # سیستم پرسش و پاسخ
├── mia_prompt_v6_3b.txt  # هویت و شخصیت Mia
└── requirements.txt      # وابستگی‌ها
```

## فایل‌های موجود در دیتاست

- Pharmaceutical Technology.pdf
- Rang and Dales Pharmacology
- Technology guides
- Prescription guides
- mia_prompt_v6_3b.txt (هویت Mia)

## ویژگی‌های سیستم

✅ جستجو در اسناد با Semantic Search
✅ پاسخ با OpenAI GPT-4
✅ پشتیبانی از زبان فارسی و انگلیسی
✅ حفظ تاریخچه مکالمه
✅ شخصیت Mia (empathetic medical assistant)
✅ منابع استفاده شده در پاسخ

## نکات ایمنی

⚠️ Mia هرگز تشخیص یا نسخه نمی‌دهد
⚠️ تصمیم نهایی با پزشک یا داروساز است
⚠️ فقط برای آموزش و پشتیبانی بالینی
