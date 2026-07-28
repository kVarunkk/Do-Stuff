from abc import ABC, abstractmethod
import chromadb
from helpers.memory.resolve_memory_operation import resolve_memory_operation

class MemoryStore(ABC):
    @abstractmethod
    async def add(self, user_id: str, facts: list[dict]) -> None: ...

    @abstractmethod
    async def query(self, user_id: str, query_text: str, top_k: int = 5) -> list[str]: ...


class ChromaMemoryStore(MemoryStore):
    def __init__(self, persist_path: str = "./chroma_data"):
        self._client = chromadb.PersistentClient(path=persist_path)
        self._collection = self._client.get_or_create_collection(name="long_term_memory", metadata={"hnsw:space": "cosine"})

    async def add(self, user_id: str, facts: list[dict]) -> None:
        if not facts:
            return

        for fact in facts:
            await resolve_memory_operation(user_id, fact, self)

    async def upsert_fact(self, user_id: str, fact: dict) -> None:
        """Low-level write — used by resolve_memory_operation, not called directly elsewhere."""
        self._collection.upsert(
            ids=[f"{user_id}:{fact['key']}"],
            documents=[fact["value"]],
            metadatas=[{"user_id": user_id, "key": fact["key"]}],
        )

    async def query_raw(self, user_id: str, query_text: str, top_k: int = 3) -> list[dict]:
        """Returns raw key+value pairs for similar memories — used for conflict resolution,
        not the same as query() which returns plain strings for injection into system_instruction."""
        results = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where={"user_id": user_id},
        )

        raw_docs = results.get("documents") or [[]]
        raw_metas = results.get("metadatas") or [[]]

        documents = raw_docs[0] if raw_docs and raw_docs[0] is not None else []
        metadatas = raw_metas[0] if raw_metas and raw_metas[0] is not None else []

        return [
            {"key": meta.get("key"), "value": doc}
            for doc, meta in zip(documents, metadatas)
        ]    


    async def query(self, user_id: str, query_text: str, top_k: int = 5, min_similarity: float = 0.3) -> list[str]:
        # print(f"INSIDE QUERY: {user_id}, {query_text}")

        results = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where={"user_id": user_id},
        )

        # print(f"QUERY RESULTS: {results}")

        raw_docs = results.get("documents") or [[]]
        raw_dists = results.get("distances") or [[]]
        
        documents = raw_docs[0] if raw_docs and raw_docs[0] is not None else []
        distances = raw_dists[0] if raw_dists and raw_dists[0] is not None else []

        # print(f"QUERY DOCUMENTS: {documents}")
        # print(f"QUERY DISTANCES: {distances}")


        return [
            doc for doc, dist in zip(documents, distances)
            if (1 - dist) >= min_similarity  
        ]