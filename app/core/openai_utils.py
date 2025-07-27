from app.core.openai_client import client, OPENAI_MODEL

async def run_classification_prompt(system_prompt: str, user_input: str) -> str:
    """
    Reusable helper for classification-style prompts.
    Returns stripped, lowercase content.
    """
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip().lower()


async def run_extraction_prompt(system_prompt: str, user_input: str) -> str:
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()