import logging
from pathlib import Path

from tqdm.asyncio import tqdm_asyncio

from .azure_doc_service import AzureDocumentParser
from .azure_open_ai import AzureOpenAIService
from .artefact_models import Artefact, ArtefactWithFullText
from .prompts import SUMMARIZE_ARTEFACT_PROMPT  # Make sure you define this prompt accordingly

logger = logging.getLogger(__name__)


class ItemSummarizer:
    def __init__(
        self,
        azure_doc_service: AzureDocumentParser,
        azure_openai_service: AzureOpenAIService
    ):
        self.azure_doc_service = azure_doc_service
        self.azure_openai_service = azure_openai_service

    async def summarize_doc(self, path: str) -> ArtefactWithFullText | None:
        """Summarizes a single artefact document into a structured ArtefactWithFullText model."""
        text = self.azure_doc_service.parse_document_from_file(path)
        summary = await self.azure_openai_service.completion(
            sys_prompt=SUMMARIZE_ARTEFACT_PROMPT,
            user_prompt=text,
            json_format=Artefact,
        )
        if not isinstance(summary, Artefact):
            return None

        return ArtefactWithFullText(
            **summary.model_dump(),
            full_text=text,
        )

    async def summarize_docs_from_folder(self, folder_path: str) -> list[ArtefactWithFullText]:
        """Processes all PDFs in a folder and returns structured artefact summaries."""
        folder = Path(folder_path)
        all_pdf_file_paths = [f for f in folder.iterdir() if f.suffix == ".pdf"]
        summaries = []
        for file_path in tqdm_asyncio(all_pdf_file_paths, desc="Processing PDF files"):
            try:
                summary = await self.summarize_doc(str(file_path))
                if summary is not None:
                    summaries.append(summary)
            except Exception:
                logger.exception("Error processing %s", file_path)
                continue
        return summaries
