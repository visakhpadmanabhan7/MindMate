from app.core.openai_utils import run_classification_prompt
from app.prompts.prompt_texts import JOURNAL_PROMPT_GENERATOR

async def generate_prompt(user_input: str) -> str:
    """
    Generates a reflective journaling question based on user input.

    Parameters:
        user_input (str): The user's message or journal request.

    Returns:
        str: A reflective question generated by the journaling coach.
    """
    return await run_classification_prompt(JOURNAL_PROMPT_GENERATOR, user_input)



