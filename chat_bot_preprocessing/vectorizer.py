import logging
import uuid

import pandas as pd

logger = logging.getLogger(__name__)


class VectorDBBuilder:
    def __init__(
        self,
        embedding_client: object,
        embedding_model: str,
        chroma_client: object,
    ) -> None:
        self.embedding_client = embedding_client
        self.embedding_model = embedding_model
        self.chroma_client = chroma_client

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of text entries using the given embedding client."""
        response = self.embedding_client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        return [e.embedding for e in response.data]

    def build_vector_db(self, df: pd.DataFrame, collection_name: str = "artefacts") -> None:
        """Build a vector database from artefact data."""
        df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]

        texts = df["long_description"].tolist()
        ids = df["id"].tolist()
        embeddings = self.get_embeddings(texts)

        try:
            self.chroma_client.delete_collection(collection_name)
        except Exception:
            logger.exception("Could not delete collection '%s'", collection_name)

        collection = self.chroma_client.get_or_create_collection(name=collection_name)

        metadatas = df[["title", "artist", "category", "price_in_euro", "year_created"]].to_dict(orient="records")

        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        logger.info("Artefact vector database has been successfully built.")
