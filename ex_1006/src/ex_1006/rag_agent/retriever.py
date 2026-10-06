from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).resolve().parent / "chroma_db"

vectorstore = Chroma(
    persist_directory= str(DB_PATH),
    embedding_function= OpenAIEmbeddings(model= "text-embedding-3-small"),
)

vectorstore.get()

retriever = vectorstore.as_retriever(search_kwargs= {"k":3})

retriever_tool = create_retriever_tool(
    retriever,
    name="pdf_search",
    description="use this tool to search information form the korean Spelling Rules PDF document",

)

def run():
    response = retriever_tool.invoke("부엌 이 들어간 경우 어떻게 발음하나요?")
    print(response)

if __name__ == "__main__":
    run()