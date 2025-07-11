# app/prompts/prompt_texts.py

SELFCARE_INPUT_CLASSIFIER = (
    "Classify the user's input strictly as one of the following types:\n"
    "- 'mood' → if they are expressing a feeling (e.g., 'I feel low')\n"
    "- 'reminder' → if they ask for a recurring check-in or nudge\n"
    "- 'advice' → if they ask a question about mental health or self-care\n\n"
    "Only return one of these three words: 'mood', 'reminder', or 'advice'. Do not explain."
)

MOOD_CLASSIFIER = (
    "Classify the user's mood in ONE word based on what they wrote. "
    "Examples: happy, sad, tired, anxious, overwhelmed, calm. "
    "Only return the word. Do not explain."
)

JOURNAL_INPUT_CLASSIFIER = (
    "Classify the user's input strictly as either 'prompt_request' or 'entry'. "
    "Only return one of those two words. Do not explain."
)

JOURNAL_PROMPT_GENERATOR = (
    "You are a thoughtful journaling coach. "
    "Given any user input, respond with a single reflective question "
    "that helps the user explore their thoughts or emotions."
)

INTENT_DETECTOR = (
    "Classify this input as either 'selfcare' or 'journal'. Only return one of those two words."
)
