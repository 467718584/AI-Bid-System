"""向量检索测试脚本"""
import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from com.aidbid.knowledge.chroma_client import ChromaClient
from com.aidbid.knowledge.config import embed_text, embed_texts


async def test_embedding():
    """测试嵌入功能"""
    print("=" * 60)
    print("测试1: 嵌入功能")
    print("=" * 60)

    test_texts = [
        "人工智能是计算机科学的一个分支",
        "机器学习是人工智能的一个子领域",
        "深度学习使用神经网络进行特征学习"
    ]

    try:
        embeddings = await embed_texts(test_texts)
        print(f"✓ 成功嵌入 {len(test_texts)} 条文本")
        print(f"✓ 向量维度: {len(embeddings[0])}")

        # 测试单文本嵌入
        single_emb = await embed_text("测试文本")
        print(f"✓ 单文本嵌入维度: {len(single_emb)}")

        return True
    except Exception as e:
        print(f"✗ 嵌入失败: {e}")
        return False


async def test_chroma():
    """测试ChromaDB"""
    print("\n" + "=" * 60)
    print("测试2: ChromaDB向量存储")
    print("=" * 60)

    try:
        client = ChromaClient(persist_directory="/tmp/test_chroma_db")

        # 测试数据
        test_ids = ["doc1", "doc2", "doc3"]
        test_embeddings = await embed_texts([
            "人工智能技术正在改变世界",
            "机器学习算法可以从数据中学习",
            "自然语言处理让机器理解人类语言"
        ])
        test_docs = [
            "人工智能技术正在改变世界",
            "机器学习算法可以从数据中学习",
            "自然语言处理让机器理解人类语言"
        ]
        test_metas = [{"source": "test", "index": i} for i in range(3)]

        # 添加文档
        result = client.add_documents(
            collection_name="test_collection",
            ids=test_ids,
            embeddings=test_embeddings,
            documents=test_docs,
            metadatas=test_metas
        )
        print(f"✓ 添加文档: {result}")

        # 检索
        query_emb = await embed_text("人工智能 机器学习")
        results = client.query(
            collection_name="test_collection",
            query_embedding=query_emb,
            n_results=3
        )
        print(f"✓ 检索到 {len(results['ids'])} 条结果")

        for i, doc in enumerate(results["documents"]):
            dist = results["distances"][i] if i < len(results["distances"]) else 0
            sim = 1.0 - dist / 2.0 if dist else 0.5
            print(f"  [{i + 1}] 相似度: {sim:.4f} - {doc[:50]}...")

        # 清理
        client.delete_collection("test_collection")
        print("✓ 清理测试数据")

        return True
    except Exception as e:
        print(f"✗ ChromaDB测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hybrid_search():
    """测试混合检索"""
    print("\n" + "=" * 60)
    print("测试3: 混合检索")
    print("=" * 60)

    try:
        client = ChromaClient(persist_directory="/tmp/test_chroma_db")

        # 准备测试数据
        test_docs = [
            "招标投标是企业采购的重要方式",
            "政府采购必须遵循公开透明原则",
            "工程建设项目需要公开招标",
            "供应商资格审查是招标的重要环节",
            "评标委员会负责评审投标文件"
        ]

        embeddings = await embed_texts(test_docs)
        client.add_documents(
            collection_name="test_hybrid",
            ids=[f"doc{i}" for i in range(5)],
            embeddings=embeddings,
            documents=test_docs,
            metadatas=[{"source": "bid"} for _ in test_docs]
        )

        # 混合检索
        query_emb = await embed_text("招标采购流程")
        results = client.hybrid_search(
            collection_name="test_hybrid",
            query_embedding=query_emb,
            query_text="招标采购",
            n_results=3,
            alpha=0.7
        )

        print(f"✓ 混合检索到 {len(results)} 条结果")
        for i, r in enumerate(results):
            print(f"  [{i + 1}] 混合分数: {r.get('similarity', 0):.4f} "
                  f"(向量:{r.get('vector_score', 0):.4f}, 关键词:{r.get('keyword_score', 0):.4f})")
            print(f"      内容: {r['content'][:40]}...")

        # 重排序
        reranked = client.rerank_results(results, "招标采购", top_k=3)
        print(f"✓ 重排序后 {len(reranked)} 条结果")

        # 清理
        client.delete_collection("test_hybrid")

        return True
    except Exception as e:
        print(f"✗ 混合检索测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("向量嵌入深度修复测试")
    print("=" * 60)

    results = {}

    # 测试1: 嵌入
    results["embedding"] = await test_embedding()

    # 测试2: ChromaDB
    results["chroma"] = await test_chroma()

    # 测试3: 混合检索
    results["hybrid"] = await test_hybrid_search()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {name}: {status}")

    all_passed = all(results.values())
    print(f"\n总体结果: {'✓ 全部通过' if all_passed else '✗ 存在失败'}")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)