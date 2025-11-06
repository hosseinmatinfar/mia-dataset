#!/usr/bin/env python3
"""
RAG Query System for Mia (Medical Intelligence Assistant)
Uses OpenAI API to answer questions based on pharmaceutical/medical documents
"""

import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from openai import OpenAI
import sys

# Configuration
DB_PATH = "vector_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"  # یا "gpt-4" اگر دسترسی داری

# Mia's Identity - این متن از فایل mia_prompt خونده میشه
MIA_IDENTITY = """Mia (Medical Intelligence Assistant) — Version 6.3 b

Description:
Mia is a multilingual, empathetic, and safety-focused AI agent developed for pharmaceutical, pharmacological, and medical education and clinical support. She combines natural conversational ability with structured, JSON-based reasoning.

Core Capabilities:
- Conversational understanding of pharmaceutical technology, pharmacology, and clinical reasoning.
- Safe, empathetic communication that avoids diagnosis or direct prescribing.

Safety & Ethics:
- Never diagnose or prescribe.
- Always add: "Final decisions must be made by a doctor or pharmacist."
- If confidence is low, ask clarifying questions instead of guessing.
"""

def load_vector_db():
    """بارگذاری دیتابیس وکتور"""
    print("📂 Loading vector database...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )
    print("✅ Vector database loaded successfully")
    return db

def retrieve_context(db, query, k=5):
    """پیدا کردن مرتبط‌ترین اسناد"""
    print(f"🔍 Searching for relevant documents (top {k})...")
    docs = db.similarity_search(query, k=k)

    # نمایش نتایج پیدا شده
    print(f"📚 Found {len(docs)} relevant documents:")
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'Unknown')
        print(f"  {i}. {os.path.basename(source)}")

    # ترکیب محتوای اسناد
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    return context, docs

def query_openai(question, context, conversation_history=None):
    """ارسال سوال به OpenAI با context از RAG"""
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY environment variable not set!")

    client = OpenAI(api_key=OPENAI_API_KEY)

    # ساخت system prompt با هویت Mia
    system_prompt = f"""{MIA_IDENTITY}

You are answering questions based on pharmaceutical and medical educational materials.

Instructions:
- Use the provided context to answer questions accurately
- If the answer is not in the context, say so clearly
- Always maintain Mia's empathetic and safety-focused tone
- Include the disclaimer about final decisions being made by doctors/pharmacists
- Respond in the same language as the question (English or Persian/Farsi)
"""

    # ساخت user message با context
    user_message = f"""Context from documents:
{context}

---

Question: {question}

Please answer based on the context provided above."""

    # آماده‌سازی messages
    messages = [{"role": "system", "content": system_prompt}]

    # اضافه کردن تاریخچه مکالمه اگر وجود داشته باشد
    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": user_message})

    print("🤖 Querying OpenAI...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )

    answer = response.choices[0].message.content
    return answer

def interactive_mode():
    """حالت تعاملی برای پرسش و پاسخ"""
    print("\n" + "="*60)
    print("🏥 Mia RAG System - Interactive Mode")
    print("="*60)
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'clear' to clear conversation history")
    print("="*60 + "\n")

    db = load_vector_db()
    conversation_history = []

    while True:
        try:
            question = input("\n💬 Your question: ").strip()

            if not question:
                continue

            if question.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! Stay safe and healthy.")
                break

            if question.lower() == 'clear':
                conversation_history = []
                print("🗑️  Conversation history cleared")
                continue

            # جستجو در دیتابیس
            context, docs = retrieve_context(db, question, k=5)

            # دریافت پاسخ از OpenAI
            answer = query_openai(question, context, conversation_history)

            # ذخیره در تاریخچه
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": answer})

            # نمایش پاسخ
            print("\n" + "-"*60)
            print("🏥 Mia's Response:")
            print("-"*60)
            print(answer)
            print("-"*60)

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def single_query_mode(question):
    """حالت تک سوال"""
    db = load_vector_db()
    context, docs = retrieve_context(db, question, k=5)
    answer = query_openai(question, context)

    print("\n" + "="*60)
    print("🏥 Mia's Response:")
    print("="*60)
    print(answer)
    print("="*60 + "\n")

    print("📚 Sources used:")
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'Unknown')
        print(f"  {i}. {os.path.basename(source)}")

if __name__ == "__main__":
    # بررسی وجود API key
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)

    # اگر آرگومان داده شده، در حالت تک سوال اجرا شود
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        single_query_mode(question)
    else:
        # در غیر این صورت حالت تعاملی
        interactive_mode()
