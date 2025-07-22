from chromadb import PersistentClient
from openai import AsyncAzureOpenAI

from .bot import Bot
from .config import config
from .data_mcp_client import MCPClient
from .vector_retriever import VectorRetriever

embedding_model = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT

embedding_client = AsyncAzureOpenAI(
    api_key=config.AZURE_OPENAI_API_KEY,
    azure_endpoint=config.AZURE_OPENAI_API_ENDPOINT,
    api_version=config.AZURE_OPENAI_API_VERSION_EMBEDDING,
)

chroma_client = PersistentClient(path="./vector_db")

async_gpt_client = AsyncAzureOpenAI(
    api_key=config.AZURE_OPENAI_API_KEY,
    azure_endpoint=config.AZURE_OPENAI_API_ENDPOINT,
    api_version=config.AZURE_OPENAI_API_VERSION_GPT,
)

mcp_client = MCPClient()

vector_retriever = VectorRetriever(
    chroma_client=chroma_client,
    embedding_client=embedding_client,
    embedding_model=embedding_model,
)

bot = Bot(
    mcp_client=mcp_client,
    gpt_client=async_gpt_client,
    vector_retriever=vector_retriever,
)
