from openai import AsyncOpenAI

client = AsyncOpenAI()
#load_dotenv()
from dotenv import load_dotenv
load_dotenv()

async def classify_journal_input(user_input: str) -> str:
    """
    Classifies input as either 'prompt_request' or 'entry'.
    """
    system_prompt = (
        "Classify the user's input strictly as either 'prompt_request' or 'entry'. "
        "Only return one of those two words. Do not explain."
    )

    response = await client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content.strip().lower()
