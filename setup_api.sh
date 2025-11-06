#!/bin/bash

echo "🔑 OpenAI API Key Setup"
echo "========================"
echo ""
echo "برای دریافت API key:"
echo "1. به https://platform.openai.com/api-keys برو"
echo "2. وارد حسابت شو (یا حساب بساز)"
echo "3. روی 'Create new secret key' کلیک کن"
echo "4. کلید رو کپی کن"
echo ""
echo "========================"
echo ""
read -p "API Key خودت رو اینجا paste کن: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API key خالی است!"
    exit 1
fi

# تشخیص shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# بررسی اینکه قبلا اضافه نشده باشه
if grep -q "OPENAI_API_KEY" "$SHELL_CONFIG" 2>/dev/null; then
    echo "⚠️  API key قبلا در $SHELL_CONFIG تنظیم شده"
    read -p "می‌خوای جایگزینش کنی؟ (y/n): " replace
    if [ "$replace" = "y" ]; then
        # حذف خط قدیمی
        sed -i.bak '/OPENAI_API_KEY/d' "$SHELL_CONFIG"
    else
        echo "✅ از API key موجود استفاده می‌شه"
        export OPENAI_API_KEY="$api_key"
        exit 0
    fi
fi

# اضافه کردن به فایل config
echo "" >> "$SHELL_CONFIG"
echo "# OpenAI API Key for Mia RAG System" >> "$SHELL_CONFIG"
echo "export OPENAI_API_KEY=\"$api_key\"" >> "$SHELL_CONFIG"

# تنظیم برای session فعلی
export OPENAI_API_KEY="$api_key"

echo "✅ API key با موفقیت تنظیم شد!"
echo "📝 ذخیره شد در: $SHELL_CONFIG"
echo ""
echo "برای استفاده در session فعلی:"
echo "  export OPENAI_API_KEY=\"$api_key\""
echo ""
echo "یا ترمینال رو restart کن"
echo ""
echo "برای تست کردن:"
echo "  python3 query_rag.py"
