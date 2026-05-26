"""标书模板管理服务"""
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """模板类型"""
    TECHNICAL = "technical"           # 技术标模板
    COMMERCIAL = "commercial"        # 商务标模板
    QUALIFICATION = "qualification"  # 资质标模板
    PROJECT_PROPOSAL = "project_proposal"  # 项目建议书模板
    CUSTOM = "custom"                # 自定义模板


class TemplateStatus(Enum):
    """模板状态"""
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"


# ============================================================
# 数据模型
# ============================================================

@dataclass
class TemplateVersion:
    """模板版本"""
    version_id: str
    version_number: str
    content: str
    changelog: str = ""
    created_at: str = ""
    created_by: str = "system"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BidTemplate:
    """标书模板"""
    template_id: str
    name: str
    description: str = ""
    template_type: TemplateType = TemplateType.TECHNICAL
    status: TemplateStatus = TemplateStatus.ACTIVE
    category: str = ""               # 模板分类/行业
    tags: List[str] = field(default_factory=list)
    current_version: str = "1.0.0"
    versions: List[TemplateVersion] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    created_by: str = "system"
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["template_type"] = self.template_type.value
        result["status"] = self.status.value
        return result


@dataclass
class ApplyResult:
    """模板应用结果"""
    success: bool
    applied_content: str
    template_id: str
    template_name: str
    variables_filled: int = 0
    warnings: List[str] = field(default_factory=list)


# ============================================================
# 内置模板
# ============================================================

BUILTIN_TEMPLATES = [
    {
        "template_id": "tpl_technical_std",
        "name": "技术标标准模板",
        "description": "标准施工组织设计模板，适用于一般工程项目投标",
        "template_type": "technical",
        "category": "施工组织设计",
        "tags": ["标准", "施工", "技术标"],
        "current_version": "1.0.0",
        "content": """# {project_name} 施工组织设计

## 第一章 项目概况

### 1.1 项目基本信息
- 项目名称：{project_name}
- 项目地址：{project_location}
- 建设单位：{client_name}
- 工期要求：{duration}天

### 1.2 工程范围
{project_scope}

### 1.3 编制依据
{reference_docs}

---

## 第二章 施工总体部署

### 2.1 施工总体思路
{overall_approach}

### 2.2 项目组织机构
{organization_structure}

### 2.3 施工总平面布置
{site_layout}

---

## 第三章 施工进度计划

### 3.1 工期目标
{schedule_target}

### 3.2 施工进度计划
{schedule_plan}

---

## 第四章 施工方案

### 4.1 主要施工工艺
{construction_technology}

### 4.2 质量保证措施
{quality_assurance}

### 4.3 安全文明施工措施
{safety_measures}

---

## 第五章 资源配置计划

### 5.1 劳动力计划
{manpower_plan}

### 5.2 机械设备计划
{equipment_plan}

### 5.3 材料供应计划
{material_plan}

---

## 第六章 售后服务
{after_sales_service}
""",
    },
    {
        "template_id": "tpl_commercial_std",
        "name": "商务标标准模板",
        "description": "标准商务投标文件模板",
        "template_type": "commercial",
        "category": "商务投标",
        "tags": ["标准", "商务", "报价"],
        "current_version": "1.0.0",
        "content": """# {project_name} 商务投标文件

## 一、投标函

尊敬的{client_name}：

我公司已认真阅读并充分理解贵方{project_name}的招标文件，愿以人民币{bid_amount}元的价格，按招标文件要求承担本项目施工。

## 二、投标总价

| 序号 | 项目名称 | 金额（元） |
|------|----------|-----------|
| 1 | {project_scope} | {bid_amount} |
| **合计** | **投标总价** | **{bid_amount}** |

## 三、报价说明
{price_notes}

## 四、工期承诺
我方承诺工期为{-duration}天。

## 五、付款方式
{payment_terms}

## 六、公司资质
{qualifications}

## 七、业绩案例
{experience_cases}
""",
    },
    {
        "template_id": "tpl_qualification_std",
        "name": "资质标标准模板",
        "description": "企业资质证明材料模板",
        "template_type": "qualification",
        "category": "资质证明",
        "tags": ["标准", "资质", "证明材料"],
        "current_version": "1.0.0",
        "content": """# 企业资质证明材料

## 一、企业基本情况

- 企业名称：{company_name}
- 法定代表人：{legal_representative}
- 注册地址：{registered_address}
- 注册资本：{registered_capital}万元

## 二、资质证书

### 2.1 营业执照
{business_license_info}

### 2.2 资质等级证书
{qualification_certificates}

### 2.3 安全生产许可证
{safety_permit_info}

## 三、项目经理及主要人员

### 3.1 项目经理简历
{project_manager_resume}

### 3.2 技术负责人简历
{technical_leader_resume}

## 四、类似项目业绩

{experience_section}

## 五、财务状况

{financial_info}
""",
    },
]


# ============================================================
# 模板服务
# ============================================================

class TemplateService:
    """标书模板管理服务"""

    def __init__(self):
        """初始化模板服务"""
        self._templates: Dict[str, BidTemplate] = {}
        self._load_builtin_templates()

    def _load_builtin_templates(self):
        """加载内置模板"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for tpl_data in BUILTIN_TEMPLATES:
            template = BidTemplate(
                template_id=tpl_data["template_id"],
                name=tpl_data["name"],
                description=tpl_data["description"],
                template_type=TemplateType(tpl_data["template_type"]),
                category=tpl_data["category"],
                tags=tpl_data["tags"],
                current_version=tpl_data["current_version"],
                created_at=now,
                updated_at=now,
            )
            # 添加初始版本
            version = TemplateVersion(
                version_id=str(uuid.uuid4()),
                version_number=tpl_data["current_version"],
                content=tpl_data["content"],
                changelog="初始版本",
                created_at=now
            )
            template.versions.append(version)
            self._templates[template.template_id] = template
            logger.info(f"Loaded template: {template.name}")

    def list_templates(
        self,
        template_type: Optional[TemplateType] = None,
        status: Optional[TemplateStatus] = None,
        tags: Optional[List[str]] = None,
        keyword: Optional[str] = None
    ) -> List[BidTemplate]:
        """
        列出可用模板

        Args:
            template_type: 模板类型筛选
            status: 状态筛选
            tags: 标签筛选（满足任一标签）
            keyword: 关键词搜索（名称/描述）

        Returns:
            模板列表
        """
        results = list(self._templates.values())

        # 按类型筛选
        if template_type:
            results = [t for t in results if t.template_type == template_type]

        # 按状态筛选
        if status:
            results = [t for t in results if t.status == status]

        # 按标签筛选
        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]

        # 按关键词搜索
        if keyword:
            kw = keyword.lower()
            results = [
                t for t in results
                if kw in t.name.lower() or kw in t.description.lower()
            ]

        # 只返回活跃模板
        results = [t for t in results if t.status == TemplateStatus.ACTIVE]

        return results

    def get_template(self, template_id: str) -> Optional[BidTemplate]:
        """获取模板详情"""
        return self._templates.get(template_id)

    def preview_template(
        self,
        template_id: str,
        variables: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        预览模板

        Args:
            template_id: 模板ID
            variables: 预览变量（可选，用于填充占位符）

        Returns:
            预览内容，未找到模板返回None
        """
        template = self._templates.get(template_id)
        if not template:
            return None

        # 获取最新版本内容
        content = template.versions[-1].content if template.versions else ""

        if variables:
            try:
                content = content.format(**variables)
            except KeyError as e:
                logger.warning(f"Missing variable in template preview: {e}")

        return content

    def apply_template(
        self,
        content: str,
        template_id: str,
        variables: Optional[Dict[str, str]] = None,
        merge_strategy: str = "replace"
    ) -> ApplyResult:
        """
        应用模板到内容

        Args:
            content: 待处理的内容
            template_id: 模板ID
            variables: 模板变量
            merge_strategy: 合并策略
                - "replace": 替换整个内容为模板
                - "prepend": 在内容前添加模板结构
                - "append": 在内容后添加模板结构
                - "wrap": 用模板包装内容

        Returns:
            应用结果
        """
        template = self._templates.get(template_id)
        if not template:
            return ApplyResult(
                success=False,
                applied_content=content,
                template_id=template_id,
                template_name="",
                warnings=[f"Template not found: {template_id}"]
            )

        # 获取模板内容
        template_content = template.versions[-1].content if template.versions else ""

        # 填充变量
        variables_filled = 0
        if variables:
            try:
                template_content = template_content.format(**variables)
                variables_filled = len(variables)
            except KeyError as e:
                logger.warning(f"Missing template variable: {e}")

        # 根据合并策略处理内容
        if merge_strategy == "replace":
            applied_content = template_content
        elif merge_strategy == "prepend":
            applied_content = template_content + "\n\n" + content
        elif merge_strategy == "append":
            applied_content = content + "\n\n" + template_content
        elif merge_strategy == "wrap":
            applied_content = template_content.format(
                **{"content": content}
            )
        else:
            applied_content = template_content

        # 更新使用统计
        template.usage_count += 1

        return ApplyResult(
            success=True,
            applied_content=applied_content,
            template_id=template_id,
            template_name=template.name,
            variables_filled=variables_filled
        )

    def create_template(
        self,
        name: str,
        content: str,
        template_type: TemplateType = TemplateType.CUSTOM,
        description: str = "",
        category: str = "",
        tags: Optional[List[str]] = None,
        created_by: str = "system"
    ) -> BidTemplate:
        """
        创建新模板

        Args:
            name: 模板名称
            content: 模板内容
            template_type: 模板类型
            description: 模板描述
            category: 模板分类
            tags: 标签列表
            created_by: 创建人

        Returns:
            创建的模板
        """
        template_id = f"tpl_{uuid.uuid4().hex[:12]}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        template = BidTemplate(
            template_id=template_id,
            name=name,
            description=description,
            template_type=template_type,
            category=category,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            created_by=created_by,
            status=TemplateStatus.DRAFT
        )

        # 添加初始版本
        version = TemplateVersion(
            version_id=str(uuid.uuid4()),
            version_number="1.0.0",
            content=content,
            changelog="初始版本",
            created_at=now,
            created_by=created_by
        )
        template.versions.append(version)
        template.current_version = "1.0.0"

        self._templates[template_id] = template
        logger.info(f"Created template: {name} ({template_id})")

        return template

    def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[TemplateStatus] = None
    ) -> Optional[BidTemplate]:
        """更新模板元信息"""
        template = self._templates.get(template_id)
        if not template:
            return None

        if name is not None:
            template.name = name
        if description is not None:
            template.description = description
        if tags is not None:
            template.tags = tags
        if status is not None:
            template.status = status

        template.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return template

    def add_template_version(
        self,
        template_id: str,
        content: str,
        changelog: str = "",
        created_by: str = "system"
    ) -> Optional[TemplateVersion]:
        """为模板添加新版本"""
        template = self._templates.get(template_id)
        if not template:
            return None

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 计算新版本号
        current = template.current_version
        parts = current.split(".")
        if len(parts) == 2:
            major, minor = int(parts[0]), int(parts[1])
            new_version = f"{major}.{minor + 1}"
        else:
            new_version = "1.1"

        version = TemplateVersion(
            version_id=str(uuid.uuid4()),
            version_number=new_version,
            content=content,
            changelog=changelog,
            created_at=now,
            created_by=created_by
        )

        template.versions.append(version)
        template.current_version = new_version
        template.updated_at = now

        return version

    def delete_template(self, template_id: str) -> bool:
        """删除模板（标记为归档）"""
        template = self._templates.get(template_id)
        if not template:
            return False

        template.status = TemplateStatus.ARCHIVED
        template.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def get_template_versions(self, template_id: str) -> List[TemplateVersion]:
        """获取模板的所有版本"""
        template = self._templates.get(template_id)
        if not template:
            return []
        return template.versions

    def export_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """导出具柄板为字典"""
        template = self._templates.get(template_id)
        if not template:
            return None
        return template.to_dict()


# ============================================================
# 单例模式
# ============================================================

_template_service_instance: Optional[TemplateService] = None


def get_template_service() -> TemplateService:
    """获取模板服务单例"""
    global _template_service_instance
    if _template_service_instance is None:
        _template_service_instance = TemplateService()
    return _template_service_instance