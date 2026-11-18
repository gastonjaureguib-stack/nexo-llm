from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_DIRECTORY / "data"
PERSIST_DIRECTORY = PROJECT_DIRECTORY / "vectorstore"
ENV_FILE = PROJECT_DIRECTORY / ".env"

CHUNK_SIZE = 800
MIN_CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 4
EMBEDDING_MODEL = "text-embedding-3-small"
TOKEN_ENCODING = "cl100k_base"
COLLECTION_NAME = "nexo_knowledge"
DEFAULT_CHAT_MODEL = "gpt-4o-mini"
