import logging
from pathlib import Path
from typing import BinaryIO

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from .config import config

logger = logging.getLogger(__name__)

class AzureDocumentParser:
    document_intelligence_client: DocumentIntelligenceClient

    def __init__(self):
        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=config.DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(config.DOCUMENT_INTELLIGENCE_API_KEY),
        )

    def parse_document(self, document: BinaryIO, model_name: str = "prebuilt-layout") -> str:
        try:
            result = self.document_intelligence_client.begin_analyze_document(
                model_name,
                body=document,
                content_type="application/pdf",
                output_content_format="markdown",
            )
        except HttpResponseError:
            logger.exception("Error while parsing document with azure document intelligence")
            return ""

        result = result.result()
        return result.content

    def parse_document_from_file(self, filepath: str, model_name: str = "prebuilt-layout") -> str:
        path = Path(filepath)
        if not path.exists():
            logger.warning("File does not exist: %s", filepath)
            return ""

        with path.open("rb") as f:
            return self.parse_document(document=f, model_name=model_name)
