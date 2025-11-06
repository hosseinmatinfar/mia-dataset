from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma
import os

data_path = "data"
db_path = "vector_db"

os.makedirs(data_path, exist_ok=True)

docs = []

print("📂 Loading documents...")
for f in os.listdir(data_path):
    path = os.path.join(data_path, f)
    try:
        if f.endswith(".pdf"):
            loaded = PyPDFLoader(path).load()
        elif f.endswith(".txt"):
            loaded = TextLoader(path).load()
        elif f.endswith(".docx"):
            loaded = Docx2txtLoader(path).load()
        else:
            print(f"⚠️ Skipping unsupported file: {f}")
            continue

        if not loaded:
            print(f"⚠️ No text found in {f}")
        else:
            docs.extend(loaded)
    except Exception as e:
        print(f"❌ Error loading {f}: {e}")

print(f"📄 Loaded {len(docs)} documents")

# تقسیم متن‌ها
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)
chunks = [c for c in chunks if c.page_content.strip()]  # حذف تکه‌های خالی

print(f"🧩 Split into {len(chunks)} chunks after cleaning")

if not chunks:
    raise ValueError("❌ هیچ متنی برای embedding پیدا نشد. فایل‌هات رو بررسی کن.")

# ساخت embedding
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ساخت دیتابیس
db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=db_path
)

db.persist()
print("✅ دیتاست ساخته شد و در", db_path, "ذخیره شد.")
