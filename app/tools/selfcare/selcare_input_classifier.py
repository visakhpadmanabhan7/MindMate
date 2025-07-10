from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = AsyncOpenAI()

async def classify_selfcare_input(user_input: str) -> str:
    """
    Classifies input as one of: 'mood', 'reminder', or 'advice'.
    Only returns one word. Used by SelfCareAgent.
    """
    system_prompt = (
        "Classify the user's input strictly as one of the following types:\n"
        "- 'mood' → if they are expressing a feeling (e.g., 'I feel low')\n"
        "- 'reminder' → if they ask for a recurring check-in or nudge\n"
        "- 'advice' → if they ask a question about mental health or self-care\n\n"
        "Only return one of these three words: 'mood', 'reminder', or 'advice'. Do not explain."
    )

    response = await client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content.strip().lower()
