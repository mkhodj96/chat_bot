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

config = Config()
