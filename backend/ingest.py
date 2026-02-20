"""Document ingestion pipeline for chunking, embedding, and storage."""

from pathlib import Path
from typing import List
from uuid import uuid4

import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader

from config import settings


class IngestService:
    """Handle loading knowledge documents and writing chunks into Chroma."""

    def load_document(self, file_path: str) -> str:
        """Load text from a PDF or TXT document."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            reader = PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages).strip()

        if suffix == ".txt":
            return path.read_text(encoding="utf-8").strip()

        raise ValueError("Unsupported file type. Only PDF and TXT files are allowed.")

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into fixed-size chunks with character overlap."""
        if not text:
            return []

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def embed_and_store(self, chunks: List[str]) -> int:
        """Embed chunk list and store it in ChromaDB using native client APIs."""
        if not chunks:
            return 0

        client = chromadb.PersistentClient(path="./chroma_store")
        # Use Chroma's default embedding function for lighter CPU-only deployments.
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embedding_fn,
        )

        ids = [f"chunk_{uuid4().hex}" for _ in chunks]
        metadatas = [{"source": "uploaded"} for _ in chunks]
        collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        return len(chunks)


ingest_service = IngestService()
