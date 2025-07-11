from app.core.openai_utils import run_classification_prompt
from app.prompts.prompt_texts import JOURNAL_INPUT_CLASSIFIER
async def classify_journal_input(user_input: str) -> str:
    """
    Classifies input as either 'prompt_request' or 'entry'.
    """

    return await run_classification_prompt(JOURNAL_INPUT_CLASSIFIER, user_input)

