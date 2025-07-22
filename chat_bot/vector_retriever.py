from chromadb import PersistentClient
from openai import AsyncAzureOpenAI


class VectorRetriever:
    def __init__(
        self,
        chroma_client: PersistentClient,
        embedding_client: AsyncAzureOpenAI,
        embedding_model: str,
        collection_name: str = "items",
    ):
        self.chroma_client = chroma_client
        self.embedding_client = embedding_client
        self.embedding_model = embedding_model
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

    async def get_combined_context(
        self, query: str, k: int = 5, max_distance: float = 0.3
    ) -> str:
        response = await self.embedding_client.embeddings.create(
            model=self.embedding_model,
            input=[query],
        )
        embedding = response.data[0].embedding
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "distances", "metadatas"],
        )
        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        combined = []
        for doc, meta, dist in zip(documents, metadatas, distances, strict=True):
            if dist <= max_distance:
                combined.append(f"{meta['title']} ({meta['artist']}):\n{doc}")
        if not combined:
            return "No similar items could be found in the database."
        return (
                "Here are relevant products related to the customer's question. "
                "Mention the following products and briefly explain at the end how they are similar to the current inquiry:\n\n"
                + "\n\n".join(combined)
        )

