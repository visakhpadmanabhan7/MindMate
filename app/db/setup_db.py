import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
import os

from app.db.models import metadata

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
import glob

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)


async def setup():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(metadata.create_all)
        print(" Database setup complete")


async def vectorize_pdfs():
    #print current working directory
    pdf_paths = glob.glob("app/data/*.pdf")
    if not pdf_paths:
        print("❗ No PDFs found in /data folder.")
        return

    documents = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_doc"] = os.path.basename(path)
            doc.metadata["page_number"] = doc.metadata["page"] + 1
        documents.extend(docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    print(f"Loaded and split {len(chunks)} chunks from {len(pdf_paths)} PDFs.")

    db_url_sync = DATABASE_URL.replace("asyncpg", "psycopg2")

    PGVector.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        collection_name="cbt_docs",
        connection_string=db_url_sync,
    )

    print("PDF embeddings stored in pgvector.")


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    await vectorize_pdfs()
    return {"status": "reset_successful"}


if __name__ == "__main__":
    asyncio.run(setup())
    asyncio.run(vectorize_pdfs())
