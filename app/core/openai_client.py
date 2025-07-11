from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

# Load environment variables once
load_dotenv()

# Singleton async client
client = AsyncOpenAI()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
