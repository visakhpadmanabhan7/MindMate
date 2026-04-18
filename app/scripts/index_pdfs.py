"""Index CBT PDF documents into ChromaDB vector store.

Run this script once (or after adding new PDFs) to vectorize documents:
    python -m app.scripts.index_pdfs
"""

import glob
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.core.vectorstore import get_embedding_model

settings = get_settings()


def index_pdfs():
    pdf_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    pdf_paths = glob.glob(os.path.join(pdf_dir, "*.pdf"))

    if not pdf_paths:
        print("No PDFs found in app/data/")
        return

    documents = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_doc"] = os.path.basename(path)
            doc.metadata["page_number"] = doc.metadata.get("page", 0) + 1
        documents.extend(docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    print(f"Loaded {len(chunks)} chunks from {len(pdf_paths)} PDFs.")

    Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        collection_name="cbt_docs",
        persist_directory=settings.CHROMA_PATH,
    )

    print(f"Embeddings stored in ChromaDB at {settings.CHROMA_PATH}")


if __name__ == "__main__":
    index_pdfs()
