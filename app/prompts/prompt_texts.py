# app/prompts/prompt_texts.py

SELFCARE_INPUT_CLASSIFIER = (
    "Classify the user's input strictly as one of the following types:\n"
    "- 'mood' → if they are expressing a feeling (e.g., 'I feel low')\n"
    "- 'advice' → if they ask a question about mental health or self-care\n\n"
    "- 'reminder' → if they are setting a reminder or asking for one\n\n"
    "Only return one of these three words: 'mood', 'reminder' or 'advice'. Do not explain."
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

REMINDER_TIME_EXTRACTOR = """
You are a helpful assistant. Extract the **time of day** from a reminder request and return it in 24-hour format as HH:MM.

If the user doesn't mention a time, default to 20:00 (8 PM).

Examples:
"Remind me to journal every evening" → 20:00  
"Set a reminder at 9 AM" → 09:00  
"Ping me at 7 tonight" → 19:00  
"Check in daily" → 20:00
"""

RAG_SUPPORT_QUERY_REPHRASER = (
    "You are a helpful assistant for mental health.\n"
    "Rephrase the user's input into a clear question to look up in a self-care guide or CBT manual.\n"
    "Examples:\n"
    "Input: I feel anxious → Query: What can I do to manage anxiety?\n"
    "Input: I'm overwhelmed → Query: How can I handle overwhelming feelings?\n"
    "Input: How do I calm down fast? → Query: How do I calm down quickly?\n\n"
    "Now do the same for:\n"
    "Input: {input}\n"
    "Query:"
)