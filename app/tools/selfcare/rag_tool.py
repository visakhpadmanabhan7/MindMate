import os
import re
from collections import defaultdict

from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.core.openai_utils import run_classification_prompt
from app.core.vectorstore import get_vectorstore
from app.prompts.prompt_texts import RAG_SUPPORT_QUERY_REPHRASER

settings = get_settings()

# Clean document names for citations
_TITLE_MAP: dict[str, str] = {}


def _clean_title(filename: str) -> str:
    """Convert ugly filenames to readable titles."""
    if filename in _TITLE_MAP:
        return _TITLE_MAP[filename]
    name = os.path.splitext(filename)[0]
    name = re.sub(r"[-_]+", " ", name)
    name = re.sub(r"\s*\(z-lib\.org\)", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    if len(name) > 60:
        name = name[:57] + "..."
    _TITLE_MAP[filename] = name
    return name


QA_PROMPT = PromptTemplate.from_template(
    "You are a supportive mental health assistant grounded in evidence-based CBT techniques.\n"
    "Use the following context from mental health resources to answer the question.\n"
    "If the context is not relevant to the question, say: "
    "\"I don't have specific information on that in my knowledge base.\"\n"
    "Be concise (3-5 key points max), warm, and actionable.\n"
    "Include inline citations like [1], [2] referencing the sources.\n"
    "End with 2-3 follow-up questions the user might want to explore, "
    "formatted as a brief list under \"**You might also explore:**\"\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer (concise, with inline citations):"
)


def _get_langchain_llm():
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model=settings.OPENAI_MODEL, temperature=0.0, api_key=settings.OPENAI_API_KEY,
        )
    return ChatGroq(
        model=settings.GROQ_MODEL, temperature=0.0, api_key=settings.GROQ_API_KEY,
    )


async def get_cbt_recommendation(raw_input: str, debug: bool = False) -> str:
    query_prompt = RAG_SUPPORT_QUERY_REPHRASER.format(input=raw_input)
    refined_query = await run_classification_prompt(query_prompt, "")

    vectorstore = get_vectorstore()

    # Check relevance before full RAG chain
    top_results = vectorstore.similarity_search_with_score(refined_query, k=1)
    if not top_results or top_results[0][1] > 1.5:
        return (
            "I don't have specific information on that in my knowledge base. "
            "You might want to discuss this with a mental health professional "
            "who can provide personalized guidance."
        )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    llm = _get_langchain_llm()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={"prompt": QA_PROMPT},
    )

    result = await qa_chain.ainvoke(refined_query)

    answer = result["result"]
    sources = result["source_documents"]

    # Build numbered citation list
    citation_map: dict[str, set] = defaultdict(set)
    for doc in sources:
        meta = doc.metadata
        docname = meta.get("source_doc", "unknown")
        page = meta.get("page_number") or (meta.get("page", 0) + 1)
        citation_map[docname].add(page)

    citations = []
    for i, (doc, pages) in enumerate(citation_map.items(), 1):
        title = _clean_title(doc)
        page_str = ", ".join(str(p) for p in sorted(pages))
        citations.append(f"[{i}] *{title}*, p. {page_str}")

    citation_text = "\n".join(citations) if citations else ""

    if citation_text:
        return f"{answer}\n\n---\n**References:**\n{citation_text}"
    return answer


async def get_cbt_feedback_for_mood(mood_label: str, context: str = "") -> str:
    """Get brief CBT feedback for a specific mood."""
    query = f"What evidence-based techniques help with feeling {mood_label}?"
    if context:
        query += f" Context: {context[:200]}"
    return await get_cbt_recommendation(query)
