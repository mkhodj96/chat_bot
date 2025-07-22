import asyncio
import logging

import pandas as pd
from chromadb import PersistentClient
from openai import AzureOpenAI

from .item_summarizer import ItemSummarizer
from .azure_doc_service import AzureDocumentParser
from .azure_open_ai import AzureOpenAIService
from .config import config
from .vectorizer import VectorDBBuilder

logger = logging.getLogger(__name__)

embedding_model: str = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT

embedding_client = AzureOpenAI(
    api_key=config.AZURE_OPENAI_API_KEY,
    azure_endpoint=config.AZURE_OPENAI_API_ENDPOINT,
    api_version=config.AZURE_OPENAI_API_VERSION_EMBEDDING,
)

openai_service = AzureOpenAIService(
    api_key=config.AZURE_OPENAI_API_KEY,
    endpoint=config.AZURE_OPENAI_API_ENDPOINT,
    api_version=config.AZURE_OPENAI_API_VERSION_GPT,
    model_name=config.AZURE_OPENAI_API_DEPLOYMENT_NAME,
)

doc_parser = AzureDocumentParser()

chroma_client = PersistentClient(path="./vector_db")

vector_db_builder = VectorDBBuilder(
    embedding_client=embedding_client,
    embedding_model=embedding_model,
    chroma_client=chroma_client,
)

item_summarizer = ItemSummarizer(
    azure_doc_service=doc_parser,
    azure_openai_service=openai_service,
)

def run_pipeline() -> None:
    summaries = asyncio.run(item_summarizer.summarize_docs_from_folder("./data"))
    df = pd.DataFrame([summary.model_dump() for summary in summaries])

    try:
        df.to_parquet("data.parquet", index=False)
    except Exception:
        logger.exception("Could not save parquet.")

    try:
        df.to_csv("output.csv", index=False)
    except Exception:
        logger.exception("Could not save csv.")

    vector_db_builder.build_vector_db(df)
