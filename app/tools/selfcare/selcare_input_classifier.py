from app.core.openai_utils import run_classification_prompt
from app.prompts.prompt_texts import SELFCARE_INPUT_CLASSIFIER
async def classify_selfcare_input(user_input: str) -> str:
    """
    Classifies input as one of: 'mood', 'reminder', or 'advice'.
    Only returns one word. Used by SelfCareAgent.
    """

    return await run_classification_prompt(SELFCARE_INPUT_CLASSIFIER, user_input)


