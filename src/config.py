import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "subagents"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Models
LLM_MODEL = "gpt-4o-mini"
IMAGE_GEN_MODEL = "gemini-2.5-flash-image"

# Firebase
# Using the same credentials file as v1, located in v1's core folder or we can copy it.
# For now, let's assume we use the one in v1 if it exists, or expect it in v2/core.
# The user said "created new service account firebase admin json and replaced it" in v1.
# Let's point to a local one in v2/core to be safe and self-contained.
FIREBASE_CREDENTIALS_PATH = BASE_DIR / "core/firebase-admin.json"
FIREBASE_STORAGE_BUCKET = "outfit-formulas-develop.appspot.com"

# Memory
MEMORY_FILE_PATH = BASE_DIR / "memory.json"
