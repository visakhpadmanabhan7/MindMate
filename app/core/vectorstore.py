import logging

from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_embedding_model = None
_vectorstore = None


def get_embedding_model() -> FastEmbedEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        # fastembed normalizes BGE embeddings by default
        _embedding_model = FastEmbedEmbeddings(model_name=settings.EMBEDDING_MODEL)
    return _embedding_model


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name="cbt_docs",
            persist_directory=settings.CHROMA_PATH,
            embedding_function=get_embedding_model(),
        )
    return _vectorstore


def delete_document_vectors(source_doc: str) -> int:
    """Delete all vectors for a specific source document from ChromaDB."""
    vs = get_vectorstore()
    collection = vs._collection

    # Find all IDs with this source_doc
    results = collection.get(where={"source_doc": source_doc})
    ids = results.get("ids", [])

    if ids:
        collection.delete(ids=ids)
        logger.info("Deleted %d vectors for %s", len(ids), source_doc)

    return len(ids)


def search_knowledge_base(query: str, k: int = 5) -> list[dict]:
    """Search the vector store and return relevant chunks with metadata."""
    vs = get_vectorstore()
    results = vs.similarity_search_with_score(query, k=k)

    chunks = []
    for doc, score in results:
        chunks.append({
            "content": doc.page_content.strip(),
            "source_doc": doc.metadata.get("source_doc", "unknown"),
            "page_number": doc.metadata.get("page_number", None),
            # Chroma returns squared L2 distance; embeddings are unit-normalized,
            # so d2 = 2 - 2*cos_sim and cosine similarity = 1 - d2/2
            "relevance": round(max(0.0, 1 - score / 2), 3),
        })
    return chunks


def get_document_chunk_count(source_doc: str) -> int:
    """Get the number of indexed chunks for a document."""
    vs = get_vectorstore()
    collection = vs._collection
    results = collection.get(where={"source_doc": source_doc})
    return len(results.get("ids", []))
