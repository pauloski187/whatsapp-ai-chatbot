"""ChromaDB helper functions and singleton client access."""

from typing import List

try:
    import chromadb
    from chromadb.api.models.Collection import Collection
    from chromadb.utils import embedding_functions

    _client = chromadb.PersistentClient(path="./chroma_store")
    _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
except Exception:
    chromadb = None
    Collection = object  # type: ignore[assignment]
    _client = None
    _embedding_fn = None


def get_collection(name: str) -> Collection:
    """Return an existing ChromaDB collection or create it if missing."""
    if _client is None:
        return object()  # type: ignore[return-value]
    return _client.get_or_create_collection(name=name, embedding_function=_embedding_fn)


def query_similar(collection: Collection, query_text: str, n: int = 4) -> List[str]:
    """Query a collection for similar chunks and return their text values."""
    if _client is None:
        return []
    if not query_text.strip():
        return []

    results = collection.query(query_texts=[query_text], n_results=n)
    docs = results.get("documents", [])
    if not docs:
        return []
    return [item for item in docs[0] if isinstance(item, str)]
