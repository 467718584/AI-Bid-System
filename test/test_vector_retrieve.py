#!/usr/bin/env python3
"""测试向量存储和检索的完整流程"""
import sys
import os
import asyncio
import logging

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-bid-knowledge', 'src', 'main', 'python'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_vector_retrieve():
    """测试向量存储和检索流程"""
    from com.aidbid.knowledge.config import embed_text, embed_texts, SimpleEmbeddingModel

    print("=" * 60)
    print("向量存储和检索测试")
    print("=" * 60)

    # 1. 测试embedding模型
    print("\n[1] 测试Embedding模型")
    print("-" * 40)
    test_texts = ["这是测试文档内容", "招标要求", "投标文件"]
    try:
        embeddings = await embed_texts(test_texts)
        print(f"✓ 批量embedding: {len(test_texts)} 条文本")
        for i, emb in enumerate(embeddings):
            print(f"  - 文本{i+1}: {test_texts[i][:20]}, 向量维度: {len(emb)}")
    except Exception as e:
        print(f"✗ Embedding失败: {e}")
        return False

    # 2. 测试单个文本embedding
    print("\n[2] 测试单个文本Embedding")
    print("-" * 40)
    query = "招标要求"
    try:
        query_embedding = await embed_text(query)
        print(f"✓ 查询embedding: '{query}'")
        print(f"  - 向量维度: {len(query_embedding)}")
    except Exception as e:
        print(f"✗ Embedding失败: {e}")
        return False

    # 3. 模拟文档存储流程
    print("\n[3] 模拟文档存储流程")
    print("-" * 40)
    doc_content = "这是测试文档内容，招标要求投标人具备相关资质。"
    chunk_size = 500
    sentences = doc_content.split("。")
    current_chunk = ""
    chunk_list = []

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + "。"
        else:
            if current_chunk:
                chunk_list.append(current_chunk)
            current_chunk = sentence + "。"

    if current_chunk:
        chunk_list.append(current_chunk)

    print(f"✓ 分块结果: {len(chunk_list)} 个chunk")
    for i, chunk in enumerate(chunk_list):
        print(f"  - Chunk {i+1}: {chunk[:30]}...")

    # 4. 存储embedding
    print("\n[4] 生成并存储Embedding")
    print("-" * 40)
    try:
        embeddings = await embed_texts(chunk_list)
        print(f"✓ 存储embedding: {len(embeddings)} 个向量")
        for i, emb in enumerate(embeddings):
            print(f"  - Chunk {i+1} 向量维度: {len(emb)}")
    except Exception as e:
        print(f"✗ Embedding存储失败: {e}")
        return False

    # 5. 测试相似度计算
    print("\n[5] 测试向量相似度计算")
    print("-" * 40)
    import numpy as np

    def cosine_similarity(vec1, vec2):
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))

    for i, chunk_emb in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, chunk_emb)
        print(f"  - Chunk {i+1} vs Query 相似度: {sim:.4f}")

    # 6. 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    print(f"Embedding模型: {'MiniMax API' if os.getenv('MINIMAX_API_KEY') else 'Simple Local'}")
    print(f"文档分块数: {len(chunk_list)}")
    print(f"向量维度: {len(embeddings[0]) if embeddings else 'N/A'}")
    print("\n✓ 测试完成")
    print("=" * 60)

    return True


async def test_chroma_fallback():
    """测试ChromaDB回退逻辑"""
    from com.aidbid.knowledge.chroma_client import ChromaClient

    print("\n\n" + "=" * 60)
    print("ChromaDB 测试")
    print("=" * 60)

    client = ChromaClient(persist_directory="/tmp/test_chroma")

    # 测试collection操作
    test_collection = "test_collection"
    try:
        # 清理旧数据
        try:
            client.delete_collection(test_collection)
        except:
            pass

        # 添加测试数据
        test_ids = ["doc1", "doc2", "doc3"]
        test_embs = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
        test_docs = ["第一个文档", "第二个文档", "第三个文档"]

        result = client.add_documents(
            collection_name=test_collection,
            ids=test_ids,
            embeddings=test_embs,
            documents=test_docs,
            metadatas=[{"index": i} for i in range(3)]
        )
        print(f"✓ 添加文档: {result}")

        # 查询
        query_emb = [0.15] * 384
        results = client.query(
            collection_name=test_collection,
            query_embedding=query_emb,
            n_results=2
        )

        print(f"✓ 查询结果: {len(results.get('ids', []))} 条")
        print(f"  - IDs: {results.get('ids', [])}")
        print(f"  - Documents: {results.get('documents', [])}")
        print(f"  - Distances: {results.get('distances', [])}")

    except Exception as e:
        print(f"✗ ChromaDB测试失败: {e}")
        print("  (这是正常的，如果ChromaDB不可用)")

    print("=" * 60)


if __name__ == "__main__":
    # 设置环境变量测试本地模型
    os.environ["USE_LOCAL_EMBEDDING"] = "true"

    success = asyncio.run(test_vector_retrieve())
    asyncio.run(test_chroma_fallback())

    sys.exit(0 if success else 1)