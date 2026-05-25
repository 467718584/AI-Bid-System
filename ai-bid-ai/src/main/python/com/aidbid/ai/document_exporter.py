"""Word文档导出模块"""
import io
from typing import Dict, Any, Optional, List
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE


class DocumentExporter:
    """Word文档导出器"""

    def __init__(self):
        self.default_font = "宋体"
        self.default_size = 12

    def create_document(self) -> Document:
        """创建新文档"""
        doc = Document()
        # 设置默认样式
        style = doc.styles["Normal"]
        style.font.name = self.default_font
        style.font.size = Pt(self.default_size)
        return doc

    def add_title(self, doc: Document, title: str, level: int = 1):
        """添加标题"""
        heading = doc.add_heading(title, level=level)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_paragraph(self, doc: Document, text: str, bold: bool = False,
                      font_size: Optional[int] = None, alignment: str = "LEFT"):
        """添加段落"""
        para = doc.add_paragraph()
        para.add_run(text).bold = bold

        if font_size:
            para.runs[0].font.size = Pt(font_size)

        if alignment == "CENTER":
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif alignment == "RIGHT":
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT

        return para

    def add_table(self, doc: Document, data: List[List[str]],
                  headers: Optional[List[str]] = None):
        """添加表格"""
        if not data:
            return

        rows = len(data) + (1 if headers else 0)
        cols = len(data[0]) if data else 0

        table = doc.add_table(rows=rows, cols=cols)
        table.style = "Table Grid"

        # 添加表头
        if headers:
            header_row = table.rows[0]
            for i, header in enumerate(headers):
                cell = header_row.cells[i]
                cell.text = header
                cell.paragraphs[0].runs[0].bold = True
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加数据
        start_idx = 1 if headers else 0
        for i, row_data in enumerate(data):
            row = table.rows[i + start_idx]
            for j, cell_text in enumerate(row_data):
                row.cells[j].text = str(cell_text)

    def export_analysis_report(self, analysis_result: Dict[str, Any]) -> bytes:
        """导出分析报告为Word文档"""
        doc = self.create_document()

        # 标题
        self.add_title(doc, "招标文件智能分析报告", level=0)

        # 基本信息
        if "basic_info" in analysis_result:
            self.add_title(doc, "一、基本信息", level=1)
            basic_info = analysis_result["basic_info"]
            for key, value in basic_info.items():
                self.add_paragraph(doc, f"{key}: {value}")

        # 评分方法
        if "scoring_method" in analysis_result:
            self.add_title(doc, "二、评分方法", level=1)
            scoring = analysis_result["scoring_method"]
            if "preliminary_review" in scoring:
                self.add_paragraph(doc, "初步评审:", bold=True)
                for item in scoring["preliminary_review"]:
                    self.add_paragraph(doc, f"  - {item}")

        # 合规检查项
        if "compliance_items" in analysis_result:
            self.add_title(doc, "三、合规检查项", level=1)
            for item in analysis_result["compliance_items"]:
                status = item.get("status", "UNKNOWN")
                self.add_paragraph(doc, f"[{status}] {item.get('requirement', '')}")

        # 废标条款
        if "disqualification_items" in analysis_result:
            self.add_title(doc, "四、废标条款", level=1)
            for item in analysis_result["disqualification_items"]:
                self.add_paragraph(doc, f"- {item.get('item', '')}")

        # AI分析结论
        if "analysis" in analysis_result:
            self.add_title(doc, "五、AI分析结论", level=1)
            self.add_paragraph(doc, analysis_result["analysis"])

        # 保存到字节流
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()

    def export_compliance_report(self, compliance_data: Dict[str, Any]) -> bytes:
        """导出合规检查报告"""
        doc = self.create_document()

        self.add_title(doc, "投标合规性检查报告", level=0)

        if "project_name" in compliance_data:
            self.add_paragraph(doc, f"项目名称: {compliance_data['project_name']}")

        if "check_items" in compliance_data:
            self.add_title(doc, "检查项目明细", level=1)

            table_data = []
            for item in compliance_data["check_items"]:
                table_data.append([
                    item.get("name", ""),
                    item.get("status", ""),
                    item.get("suggestion", "")
                ])

            if table_data:
                self.add_table(doc, table_data,
                               headers=["检查项", "状态", "建议"])

        # 保存
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()

    def export_bid_summary(self, summary_data: Dict[str, Any]) -> bytes:
        """导出投标摘要"""
        doc = self.create_document()

        self.add_title(doc, "投标文件摘要", level=0)

        # 项目信息
        self.add_title(doc, "项目信息", level=1)
        project_info = summary_data.get("project_info", {})
        for key, value in project_info.items():
            self.add_paragraph(doc, f"{key}: {value}")

        # 资质匹配
        self.add_title(doc, "资质匹配情况", level=1)
        qualifications = summary_data.get("qualifications", [])
        for q in qualifications:
            status = "通过" if q.get("matched") else "不通过"
            self.add_paragraph(doc, f"[{status}] {q.get('name', '')}")

        # 保存
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()