from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class KnowledgeBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    kb_type: str = "DOCUMENT"
    chunk_strategy: str = "recursive"
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "m3e"
    vector_dimension: int = 1536
    retrieval_type: str = "similarity"
    top_k: int = 5
    min_similarity: float = 0.7
    status: int = 1
    document_count: int = 0
    chunk_count: int = 0
    created_at: datetime = None

    class Config:
        from_attributes = True

class KnowledgeChunk(BaseModel):
    id: str
    kb_id: str
    doc_id: Optional[str] = None
    content: str
    chunk_index: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime = None

    class Config:
        from_attributes = True

class RetrieveRequest(BaseModel):
    query: str
    topK: int = 5
    minSimilarity: float = 0.7
    filters: Optional[Dict] = {}

class RetrieveResponse(BaseModel):
    results: List[Dict]
    total: int
    query: str

class DocumentCreateRequest(BaseModel):
    docName: str
    content: str
    metadata: Optional[Dict] = {}

class ChunkCreateRequest(BaseModel):
    kbId: str
    docId: str
    content: str
    metadata: Optional[Dict] = {}