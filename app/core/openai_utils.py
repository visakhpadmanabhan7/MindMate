from app.core.llm import get_llm


async def run_classification_prompt(system_prompt: str, user_input: str) -> str:
    llm = get_llm()
    return await llm.classify(system_prompt, user_input)


async def run_extraction_prompt(system_prompt: str, user_input: str) -> str:
    llm = get_llm()
    return await llm.extract(system_prompt, user_input)
