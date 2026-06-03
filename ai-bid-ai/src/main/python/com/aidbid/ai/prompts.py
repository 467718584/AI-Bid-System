"""Prompt模板定义"""

# ============================================================
# 技术标智能编制Prompt
# ============================================================

TECHNICAL_BID_OUTLINE_PROMPT = """
# 角色
你是一位资深的技术标编写专家，负责为投标项目编写高质量的施工组织设计。

# 项目信息
项目名称：{project_name}
项目类型：{project_type}
招标要求：{bid_requirements}
评分标准：{scoring_criteria}

# 要求
1. 紧扣招标要求和评分标准
2. 使用专业规范的技术语言
3. 总页数控制在 {page_count} 页以内
4. 目录结构清晰，层级分明

# 输出格式
请输出JSON格式的目录结构：
{{
  "title": "技术标",
  "totalPages": {page_count},
  "children": [
    {{"title": "第一章 项目概况", "pageCount": 3, "children": []}},
    {{"title": "第二章 施工方案", "pageCount": 15, "children": []}}
  ]
}}
"""

TECHNICAL_BID_CONTENT_PROMPT = """
# 角色
你是一位资深的技术标编写专家，负责为投标项目编写高质量的施工组织设计。

# 项目信息
项目名称：{project_name}
项目类型：{project_type}
章节标题：{chapter_title}
页数要求：{page_count}页

# 招标要求
{bid_requirements}

# 评分标准
{scoring_criteria}

# 要求
1. 内容要紧扣招标要求和评分标准
2. 使用专业、规范的技术语言，使用多级标题结构（## 章节号 ### 小节号）
3. 每500字左右考虑插入一个图表（使用图表标记）
4. 总页数控制在 {page_count} 页以内
5. 必须使用多级标题组织内容结构，禁止连续段落无标题分隔

# 输出格式
输出完整的章节正文内容，使用Markdown格式。

**重要**：必须包含多级标题（## 1.1, ### 1.1.1等），每个主要段落前必须有标题。
"""

TECHNICAL_BID_CONTENT_PROMPT = """
# 角色
你是一位资深的技术标编写专家，负责为投标项目编写高质量的施工组织设计。

# 项目信息
项目名称：{project_name}
项目类型：{project_type}
章节标题：{chapter_title}
页数要求：{page_count}页

# 招标要求
{bid_requirements}

# 评分标准
{scoring_criteria}

# 要求
1. 内容要紧扣招标要求和评分标准
2. 使用专业、规范的技术语言，使用多级标题结构（## 章节号 ### 小节号）
3. 图文并茂，适当插入图表
4. 总页数控制在 {page_count} 页以内
5. 每500字左右考虑插入一个图表（使用图表标记）
6. 必须使用多级标题组织内容结构，禁止连续段落无标题分隔

# 输出格式
输出完整的章节正文内容，使用Markdown格式，合理使用图表标记。

**重要**：必须包含多级标题（## 1.1, ### 1.1.1等），每个主要段落前必须有标题。
"""

# 图文并茂版本的技术标正文生成Prompt
TECHNICAL_BID_RICH_CONTENT_PROMPT = TECHNICAL_BID_CONTENT_PROMPT


BID_DOCUMENT_PARSE_PROMPT = """
# 角色
你是一位专业的招标文件解析专家，负责从招标文件中提取关键信息。

# 文件内容
{content}

# 任务
请从上述招标文件中提取以下信息，并以JSON格式输出：

1. basic_info（基本信息）
   - project_name: 项目名称
   - agency_name: 招标代理/业主
   - contact_person: 联系人
   - contact_phone: 联系电话
   - bid_deadline: 投标截止时间
   - submit_deadline: 提交截止时间
   - bid_amount: 招标金额（如有）

2. scoring_method（评标办法）
   - disqualification_items: 废标条款列表
   - preliminary_review: 初步评审条款
   - commercial_review: 商务评审条款
   - technical_review: 技术评审条款

3. compliance_items（合规项）
   - 各项资质要求、合规要求

4. keywords（关键词）
   - 自定义关键词出现位置
"""

PARAPHRASE_PROMPT = """
# 角色
你是一位专业的标书改写专家，负责提升标书的原创性和专业性。

# 原文
{original_content}

# 改写要求
- 改写策略：{strategy}
- 篇幅倍数：{multiplier}
- 保持关键词：{preserve_keywords}

# 要求
1. 保持原文的核心意思
2. 提升表达的专业性和原创性
3. {strategy}要自然流畅

# 输出
改写后的内容。
"""

COMPLIANCE_CHECK_PROMPT = """
# 角色
你是一位投标合规检查专家，负责检测标书中的合规问题。

# 招标文件要求
{requirements}

# 标书内容
{content}

# 任务
请检查标书内容是否满足招标文件中的各项要求，输出JSON格式：

{{
  "check_results": [
    {{
      "type": "COMPLIANCE|DISQUALIFICATION|KEYWORD",
      "severity": "HIGH|MEDIUM|LOW",
      "requirement": "具体要求",
      "status": "PASS|FAIL|WARN",
      "location": "位置",
      "description": "描述",
      "suggestion": "建议"
    }}
  ],
  "summary": {{
    "total": 10,
    "pass": 8,
    "fail": 1,
    "warn": 1
  }}
}}
"""

# ============================================================
# 标书生成Prompt（保留原有模板）
# ============================================================

TECHNICAL_BID_PROMPT = """你是专业的投标文档编写专家。请根据以下信息，生成高质量的技术投标文件。

## 项目信息
项目名称：{project_name}
采购单位：{procurement_unit}
投标截止时间：{deadline}

## 招标文件要求
{bidding_requirements}

## 投标人资质
{qualifications}

## 评分标准
{scoring_criteria}

## 知识库参考信息
{reference_docs}

## 输出要求
1. 结构清晰，使用Markdown格式
2. 包含以下章节：
   - 项目理解与响应
   - 技术方案设计
   - 实施计划与进度安排
   - 质量保证措施
   - 售后服务承诺
   - 风险控制方案
3. 内容专业、具体、可操作
4. 突出竞争优势

请生成完整的技术投标文件："""

CREDIT_BID_PROMPT = """你是专业的投标文档编写专家。请根据以下信息，生成高质量的资信投标文件。

## 项目信息
项目名称：{project_name}
采购单位：{procurement_unit}

## 投标人资质
{qualifications}

## 业绩案例
{case_studies}

## 财务状况
{financial_info}

## 荣誉资质
{honors_and_certifications}

## 输出要求
1. 结构清晰，使用Markdown格式
2. 包含以下章节：
   - 公司简介
   - 资质证书展示
   - 典型业绩案例
   - 财务状况说明
   - 团队介绍
3. 内容真实、突出优势

请生成完整的资信投标文件："""

# ============================================================
# 标书改写Prompt（保留原有模板）
# ============================================================

BID_REWRITE_PROMPT = """你是专业的投标文档改写专家。请对以下投标文档进行改写优化。

## 原始文档
{original_content}

## 改写要求
{rewrite_requirements}

## 目标风格
{target_style}

## 输出要求
1. 保持原文的核心信息和要点
2. 提升语言的专业性和说服力
3. 优化句式结构，增强可读性
4. 保持专业术语的准确性

请进行改写："""

COMPETITOR_ANALYSIS_PROMPT = """请分析以下投标文档与竞争对手的差异，并提供优化建议。

## 投标文档
{bid_content}

## 招标文件要求
{bidding_requirements}

## 评分标准
{scoring_criteria}

请分析：
1. 优势亮点
2. 不足之处
3. 优化建议
4. 差异化竞争策略"""

# ============================================================
# 合规检测Prompt（保留原有模板）
# ============================================================

LEGAL_COMPLIANCE_CHECK_PROMPT = """你是专业的投标合规审核专家。请对以下投标文档进行合规性检查。

## 投标文档
{bid_document}

## 招标文件要求
{bidding_requirements}

## 法律法规要求
{legal_requirements}

## 输出要求
1. 列出所有合规问题
2. 按严重程度分类（严重/一般/提示）
3. 提供修改建议
4. 给出合规评分（0-100）

请进行合规检查："""

# ============================================================
# 文档解析Prompt
# ============================================================

DOCUMENT_SUMMARY_PROMPT = """请总结以下文档的关键信息。

## 文档内容
{document_content}

## 文档类型
{document_type}

请提取：
1. 文档主题
2. 关键要点（3-5条）
3. 重要数据指标
4. 结论和建议"""

# ============================================================
# RAG检索Context构建Prompt
# ============================================================

CONTEXT_BUILDING_PROMPT = """请根据以下检索结果，构建回答用户问题所需的上下文。

## 用户问题
{user_question}

## 检索结果
{retrieval_results}

请按以下格式构建上下文：
1. 按相关性排序
2. 标注每个来源
3. 过滤无关信息
4. 提炼关键引用"""

# ============================================================
# 通用问答Prompt
# ============================================================

GENERAL_QA_PROMPT = """你是一个专业的投标咨询助手。请回答用户关于投标的问题。

## 用户问题
{question}

## 参考信息
{reference_info}

## 输出要求
1. 回答专业、准确
2. 如涉及重要信息，明确标注参考来源
3. 如信息不足，明确说明
4. 语气专业、友好

请回答："""


def build_prompt(template: str, **kwargs) -> str:
    """构建Prompt模板"""
    return template.format(**kwargs)