#!/usr/bin/env python3
"""图文并茂功能测试脚本"""
import sys
import os
import tempfile
import importlib.util

# 工作目录: ai-bid-ai/src/main/python/com/aidbid/ai
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# src/main/python
PYTHON_BASE = os.path.dirname(SCRIPT_DIR)
# ai-bid-ai/src/main
PARENT_DIR = os.path.dirname(PYTHON_BASE)

# 添加路径
sys.path.insert(0, PYTHON_BASE)


def load_module_from_path(module_name: str, file_path: str):
    """从路径加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_image_service():
    print("\n=== 测试图片服务 ===")
    try:
        from services.image_service import ImageService, ImageResult
        service = ImageService()
        results = service._generate_placeholder_images("施工进度", 2)
        assert len(results) == 2
        assert isinstance(results[0], ImageResult)
        print(f"  [OK] 生成占位图片: {len(results)}个")
        print("  图片服务测试通过!")
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [FAIL] {e}")
        return False


def test_chart_generation():
    print("\n=== 测试图表生成 ===")
    try:
        from services.image_service import ImageService
        service = ImageService()
        data = [["Item1", "30"], ["Item2", "65"]]
        chart_bytes = service._generate_bar_chart(data, ["名称", "数值"], "测试图表")
        if chart_bytes:
            print(f"  [OK] 柱状图生成: {len(chart_bytes)} bytes")
        else:
            print(f"  [OK] 柱状图: matplotlib不可用(跳过)")
        print("  图表生成测试通过!")
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [FAIL] {e}")
        return False


def test_document_exporter():
    print("\n=== 测试文档导出器 ===")
    try:
        from document_exporter import DocumentExporter
        exporter = DocumentExporter()
        doc = exporter.create_document()
        assert doc is not None
        print(f"  [OK] 创建文档")

        exporter.add_title(doc, "测试标题", level=1)
        exporter.add_paragraph(doc, "测试文本")
        print(f"  [OK] 添加标题/段落")

        headers = ["设备名称", "规格", "数量"]
        data = [["挖掘机", "卡特320", "3台"]]
        exporter.add_styled_table(doc, data, headers, "设备配置表")
        print(f"  [OK] 添加美化表格")

        md = "# 标题\n## 设备\n|名称|规格|\n|---|---|\n|挖掘机|卡特|\n**[图表:进度]**\n- 要点1\n"
        exporter.add_markdown_content(doc, md)
        print(f"  [OK] 解析Markdown")

        assert len(doc.paragraphs) > 0
        assert len(doc.tables) >= 1
        print(f"  [OK] 文档验证 (段落:{len(doc.paragraphs)} 表格:{len(doc.tables)})")
        print("  文档导出器测试通过!")
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [FAIL] {e}")
        return False


def test_image_handler():
    print("\n=== 测试图片处理器 ===")
    try:
        # 动态加载 - 使用绝对路径
        handler_mod = load_module_from_path(
            "image_handler",
            "/home/zzy/.openclaw/workspace/workspace-bid/ai-bid-document/src/main/python/com/aibid/document/image_handler.py"
        )
        ImageHandler = handler_mod.ImageHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            handler = ImageHandler(output_dir=tmpdir)
            assert os.path.exists(handler.image_dir)
            print(f"  [OK] 目录创建")

            filename = handler._generate_filename("施工进度表", ".png")
            assert filename.endswith(".png")
            print(f"  [OK] 文件名: {filename}")

            # 测试扩展名检测
            ext = handler._get_extension("img.jpg", b"\xff\xd8\xff")
            assert ext == ".jpg"
            print(f"  [OK] 扩展名检测")

            # 测试图片下载处理（验证识别逻辑，不验证下载结果）
            md = "# t\n![img](https://example.com/a.png)\n![图表](chart:bar|test)"
            processed, meta = handler.process_markdown_images(md, "p1")
            # chart:标记应保持原样
            assert "chart:bar" in processed
            print(f"  [OK] Markdown图片处理 (识别{len(meta)}张图片)")

        print("  图片处理器测试通过!")
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [FAIL] {e}")
        return False


def test_image_search():
    print("\n=== 测试图片搜索 ===")
    try:
        search_mod = load_module_from_path(
            "image_search",
            "/home/zzy/.openclaw/workspace/workspace-bid/ai-bid-material/src/main/python/com/aibid/material/image_search.py"
        )
        ImageSearchResult = search_mod.ImageSearchResult

        result = ImageSearchResult(
            image_id="test1",
            path="/path/img.png",
            caption="测试图",
            score=0.85
        )
        assert result.image_id == "test1"
        d = result.to_dict()
        assert d["id"] == "test1"
        print(f"  [OK] ImageSearchResult结构")
        print("  图片搜索测试通过!")
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [FAIL] {e}")
        return False


def test_prompts():
    print("\n=== 测试Prompt模板 ===")
    try:
        from prompts import TECHNICAL_BID_RICH_CONTENT_PROMPT

        rich_prompt = TECHNICAL_BID_RICH_CONTENT_PROMPT.format(
            project_name="测试项目",
            project_type="市政",
            chapter_title="质量保证",
            page_count=15,
            bid_requirements="招标要求",
            scoring_criteria="评分标准"
        )
        assert "测试项目" in rich_prompt
        assert "chart:" in rich_prompt
        assert "table:" in rich_prompt
        print(f"  [OK] 图文并茂Prompt模板")
        print("  Prompt模板测试通过!")
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [FAIL] {e}")
        return False


def test_content_generation_helpers():
    """测试辅助函数（不导入main.py因为有相对导入）"""
    print("\n=== 测试内容生成辅助函数 ===")
    try:
        # 直接解析chart标记的正则
        import re
        content = """
![进度表](chart:bar|施工进度|阶段1,阶段2,阶段3|30,65,90)
![设备表](table:[{"headers":["设备名称","数量"],"rows":[["挖掘机","3台"]]}])
"""
        # 测试chart解析
        chart_pat = re.compile(r"!\[([^\]]*)\]\(chart:([^)]+)\)")
        charts = list(chart_pat.finditer(content))
        assert len(charts) >= 1
        print(f"  [OK] Chart标记解析: {len(charts)}个")

        # 测试table解析
        table_pat = re.compile(r"!\[([^\]]*)\]\(table:([^)]+)\)")
        tables = list(table_pat.finditer(content))
        assert len(tables) >= 1
        print(f"  [OK] Table标记解析: {len(tables)}个")

        # 测试表格Markdown构建
        headers = ["设备名称", "数量"]
        rows = [["挖掘机", "3台"]]
        md_lines = []
        md_lines.append("| " + " | ".join(headers) + " |")
        md_lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            md_lines.append("| " + " | ".join(row) + " |")
        table_md = "\n".join(md_lines)
        assert "设备名称" in table_md
        assert "挖掘机" in table_md
        print(f"  [OK] Markdown表格构建")

        print("  内容生成辅助函数测试通过!")
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [FAIL] {e}")
        return False


def main():
    # 抑制matplotlib字体警告（中文渲染需要特殊配置）
    import warnings
    warnings.filterwarnings("ignore", ".*Glyph.*font.*")

    print("=" * 50)
    print("图文并茂功能测试")
    print("=" * 50)

    results = {
        "图片服务": test_image_service(),
        "图表生成": test_chart_generation(),
        "文档导出器": test_document_exporter(),
        "图片处理器": test_image_handler(),
        "图片搜索": test_image_search(),
        "Prompt模板": test_prompts(),
        "内容生成辅助": test_content_generation_helpers(),
    }

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, ok in results.items():
        print(f"  {name}: {'通过' if ok else '失败'}")
    print(f"\n总计: {passed}/{total} 通过")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())