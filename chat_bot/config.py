from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Dokumenten-Parser
    DOCUMENT_INTELLIGENCE_ENDPOINT: str = ""
    DOCUMENT_INTELLIGENCE_API_KEY: str = ""
    # gemeinsam
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_ENDPOINT: str
    # GPT
    AZURE_OPENAI_API_DEPLOYMENT_NAME: str
    AZURE_OPENAI_API_VERSION_GPT: str
    # Embedding
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str
    AZURE_OPENAI_API_VERSION_EMBEDDING: str

    #conversations directory
    BASE_DIR: Path = Path(__file__).resolve().parent
    CONV_DIR: Path = (BASE_DIR / "conversations").resolve()


config = Config()
config.CONV_DIR.mkdir(exist_ok=True)

