"""
标书Word文档样式模板
定义多种专业标书样式配置
"""
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn

# 模板类型
class TemplateType:
    """模板枚举"""
    STANDARD = "standard"           # 标准政府投标
    TECHNICAL = "technical"          # 技术标专用
    COMMERCIAL = "commercial"        # 商务标专用
    PROFESSIONAL = "professional"   # 专业工程类
    SIMPLE = "simple"               # 简洁版

class BidTemplate:
    """标书模板基类"""
    
    def __init__(self):
        self.name = "默认模板"
        self.type = TemplateType.STANDARD
        
        # 页面设置
        self.page_width = Inches(8.5)      # A4宽度
        self.page_height = Inches(11)      # A4高度
        self.margin_top = Inches(1.0)
        self.margin_bottom = Inches(1.0)
        self.margin_left = Inches(1.25)
        self.margin_right = Inches(1.25)
        
        # 标题样式
        self.title_font = "黑体"
        self.title_size = Pt(22)
        self.title_color = RGBColor(0, 0, 0)
        self.title_bold = True
        self.title_alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 一级标题
        self.h1_font = "黑体"
        self.h1_size = Pt(16)
        self.h1_color = RGBColor(0, 0, 0)
        self.h1_bold = True
        self.h1_alignment = WD_ALIGN_PARAGRAPH.LEFT
        self.h1_space_before = Pt(12)
        self.h1_space_after = Pt(6)
        
        # 二级标题
        self.h2_font = "楷体"
        self.h2_size = Pt(14)
        self.h2_color = RGBColor(0, 0, 0)
        self.h2_bold = True
        self.h2_alignment = WD_ALIGN_PARAGRAPH.LEFT
        self.h2_space_before = Pt(10)
        self.h2_space_after = Pt(4)
        
        # 三级标题
        self.h3_font = "楷体"
        self.h3_size = Pt(12)
        self.h3_color = RGBColor(0, 0, 0)
        self.h3_bold = True
        self.h3_alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # 正文样式
        self.body_font = "宋体"
        self.body_size = Pt(12)
        self.body_color = RGBColor(0, 0, 0)
        self.body_alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self.body_line_spacing = 1.5
        self.body_first_line_indent = Pt(24)  # 首行缩进2字符
        
        # 表格样式
        self.table_header_bg = RGBColor(220, 230, 241)
        self.table_header_font = "黑体"
        self.table_header_size = Pt(10)
        self.table_body_font = "宋体"
        self.table_body_size = Pt(10)
        self.table_border_color = RGBColor(150, 150, 150)

class StandardTemplate(BidTemplate):
    """标准政府投标模板"""
    
    def __init__(self):
        super().__init__()
        self.name = "标准政府投标"
        self.type = TemplateType.STANDARD
        
        # 政府风格：蓝色主题
        self.title_color = RGBColor(0, 51, 102)
        self.h1_color = RGBColor(0, 51, 102)
        self.h2_color = RGBColor(0, 51, 102)
        
        # 表格表头蓝色背景
        self.table_header_bg = RGBColor(0, 51, 102)
        self.table_header_font_color = RGBColor(255, 255, 255)

class TechnicalTemplate(BidTemplate):
    """技术标专用模板"""
    
    def __init__(self):
        super().__init__()
        self.name = "技术标专用"
        self.type = TemplateType.TECHNICAL
        
        # 绿色专业风格
        self.title_color = RGBColor(0, 100, 0)
        self.h1_color = RGBColor(0, 100, 0)
        self.h2_color = RGBColor(0, 80, 0)
        
        self.table_header_bg = RGBColor(0, 100, 0)
        self.table_header_font_color = RGBColor(255, 255, 255)

class CommercialTemplate(BidTemplate):
    """商务标专用模板"""
    
    def __init__(self):
        super().__init__()
        self.name = "商务标专用"
        self.type = TemplateType.COMMERCIAL
        
        # 金色大气风格
        self.title_color = RGBColor(139, 69, 19)
        self.h1_color = RGBColor(139, 69, 19)
        
        self.table_header_bg = RGBColor(184, 134, 11)
        self.table_header_font_color = RGBColor(255, 255, 255)

class ProfessionalTemplate(BidTemplate):
    """专业工程类模板"""
    
    def __init__(self):
        super().__init__()
        self.name = "专业工程类"
        self.type = TemplateType.PROFESSIONAL
        
        # 深蓝专业
        self.title_color = RGBColor(25, 25, 112)
        self.h1_color = RGBColor(25, 25, 112)
        self.h2_color = RGBColor(25, 25, 112)
        
        self.table_header_bg = RGBColor(25, 25, 112)
        self.table_header_font_color = RGBColor(255, 255, 255)

class SimpleTemplate(BidTemplate):
    """简洁版模板"""
    
    def __init__(self):
        super().__init__()
        self.name = "简洁版"
        self.type = TemplateType.SIMPLE
        
        # 最小化装饰
        self.h1_space_before = Pt(6)
        self.h1_space_after = Pt(3)
        self.body_line_spacing = 1.0
        self.body_first_line_indent = Pt(24)

# 模板注册表
TEMPLATES = {
    TemplateType.STANDARD: StandardTemplate,
    TemplateType.TECHNICAL: TechnicalTemplate,
    TemplateType.COMMERCIAL: CommercialTemplate,
    TemplateType.PROFESSIONAL: ProfessionalTemplate,
    TemplateType.SIMPLE: SimpleTemplate,
}

def get_template(template_type: str) -> BidTemplate:
    """获取模板实例"""
    template_class = TEMPLATES.get(template_type, StandardTemplate)
    return template_class()

def list_templates():
    """列出所有可用模板"""
    return [
        {
            "type": TemplateType.STANDARD,
            "name": "标准政府投标",
            "description": "蓝色主题，适合政府采购类投标文件"
        },
        {
            "type": TemplateType.TECHNICAL,
            "name": "技术标专用",
            "description": "绿色专业风格，适合技术方案投标"
        },
        {
            "type": TemplateType.COMMERCIAL,
            "name": "商务标专用",
            "description": "金色大气风格，适合商务标书"
        },
        {
            "type": TemplateType.PROFESSIONAL,
            "name": "专业工程类",
            "description": "深蓝专业风格，适合工程类投标"
        },
        {
            "type": TemplateType.SIMPLE,
            "name": "简洁版",
            "description": "简洁清晰，适合快速生成"
        }
    ]
