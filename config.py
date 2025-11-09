# config.py
from pathlib import Path

# Model Config
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY = "AIzaSyBWrEvuL2r1AqBLCRvk3Jct-5rtYUVIFVY"

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHROMA_PERSIST_DIR = BASE_DIR / "vector_db"
COLLECTION_NAME = "hr_knowledge_base"

QUESTIONS_BANK_FILE = DATA_DIR / "q_bank.json"
JOB_ROLES_FILE = DATA_DIR / "job_roles.json"
GUIDELINES_FILE = DATA_DIR / "interview_guidelines.json"

# Retrieval Settings
TOP_K_RESULTS = 5
MIN_QUESTIONS = 8
MAX_QUESTIONS = 12
QUESTION_TYPES = {"technical": 0.6, "behavioral": 0.25, "situational": 0.15}
