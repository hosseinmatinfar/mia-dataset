from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model_name="gpt-4o-mini"),  # مدل سبک و سریع
    retriever=db.as_retriever(),
)

query = "Explain emulsion types in pharmaceutical technology."
result = qa.run(query)
print(result)
