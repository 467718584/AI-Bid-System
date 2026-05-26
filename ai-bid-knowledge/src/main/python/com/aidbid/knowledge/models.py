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


class SimpleEmbeddingModel:
    """简单的基于词频的嵌入模型（不需要网络）"""

    def __init__(self, dim: int = 384):
        self.dim = dim
        self.vocab = [
            "的", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
            "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看",
            "好", "自己", "这", "中", "大", "来", "为", "得", "之", "以", "于", "从",
            "人工智能", "机器", "学习", "深度", "网络", "神经", "模型", "数据", "算法",
            "系统", "技术", "方法", "应用", "招标", "投标", "采购", "工程", "项目",
            "建设", "施工", "监理", "设计", "咨询", "服务", "供应", "资格", "审查",
            "评审", "评分", "中标", "合同", "文件", "公告", "招标人", "投标人",
            "公开", "透明", "公平", "公正", "竞争", "市场", "价格", "质量", "工期"
        ]

    def _hash(self, text: str) -> int:
        h = hashlib.md5(text.encode('utf-8')).hexdigest()
        return int(h[:8], 16)

    def encode(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(text) for text in texts]

    def _text_to_vector(self, text: str) -> List[float]:
        vector = [0.0] * self.dim
        words = []
        current = ""
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                if current:
                    words.append(current)
                    current = ""
                words.append(char)
            elif char.isspace() or char in ',，。.!?':
                if current:
                    words.append(current)
                    current = ""
            else:
                current += char.lower()
        if current:
            words.append(current)

        word_freq = {}
        for w in words:
            if len(w) >= 1:
                word_freq[w] = word_freq.get(w, 0) + 1

        for word, freq in word_freq.items():
            hash_idx = self._hash(word) % self.dim
            vector[hash_idx] = freq * 0.1

        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        return vector

    def get_sentence_embedding_dimension(self) -> int:
        return self.dim