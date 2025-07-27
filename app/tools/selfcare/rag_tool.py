import os
from collections import defaultdict

from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings

from app.core.openai_utils import run_classification_prompt
from app.prompts.prompt_texts import RAG_SUPPORT_QUERY_REPHRASER
from app.core.openai_client import OPENAI_MODEL

from langchain.vectorstores.pgvector import PGVector
from langchain.chains import RetrievalQA
from langchain.schema import Document

DB_URL = os.getenv("DATABASE_URL").replace("asyncpg", "psycopg2")


async def get_cbt_recommendation(raw_input: str, debug: bool = False) -> str:
    query_prompt = RAG_SUPPORT_QUERY_REPHRASER.format(input=raw_input)

    # Await the rephrasing step
    refined_query = await run_classification_prompt(query_prompt, "")

    embedding_model = OpenAIEmbeddings()

    retriever = PGVector(
        collection_name="cbt_docs",
        connection_string=DB_URL,
        embedding_function=embedding_model
    ).as_retriever(search_kwargs={"k": 8})

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.0)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
    )

    # Use invoke instead of deprecated call
    result = qa_chain.invoke(refined_query)

    answer = result["result"]
    sources: list[Document] = result["source_documents"]

    citation_map = defaultdict(set)
    for doc in sources:
        meta = doc.metadata
        docname = meta.get("source_doc", "unknown")
        page = meta.get("page_number") or (meta.get("page", 0) + 1)
        citation_map[docname].add(page)

    citation_lines = [
        f"- {doc} (page {', '.join(str(p) for p in sorted(pages))})"
        for doc, pages in citation_map.items()
    ]
    citation_text = "\n".join(citation_lines) if citation_lines else "No sources found."

    if debug:
        debug_chunks = "\n\n---\n".join(
            f"📄 {doc.metadata.get('source_doc', 'unknown')} (page {doc.metadata.get('page_number') or (doc.metadata.get('page', 0) + 1)}):\n{doc.page_content.strip()}"
            for doc in sources
        )
        return f"🔍 **RAG Debug Mode**\n\n**Rephrased Query:** {refined_query}\n\n{answer}\n\n📖 **Sources:**\n{citation_text}\n\n🧠 **Retrieved Chunks:**\n{debug_chunks}"

    return f"{answer}\n\n📖 **Sources:**\n{citation_text}"
