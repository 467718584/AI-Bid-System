"""
企业资料库服务

提供企业基本信息、资质证书、业绩案例的查询和搜索功能。
"""
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class EnterpriseInfo:
    """企业信息数据模型"""
    enterprise_id: int
    name: str
    unified_credit_code: str = ""
    type: str = ""
    industry: str = ""
    registered_capital: float = 0.0
    legal_person: str = ""
    contact_phone: str = ""
    address: str = ""
    description: str = ""
    qualification_count: int = 0
    status: str = "ACTIVE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enterpriseId": self.enterprise_id,
            "name": self.name,
            "unifiedCreditCode": self.unified_credit_code,
            "type": self.type,
            "industry": self.industry,
            "registeredCapital": self.registered_capital,
            "legalPerson": self.legal_person,
            "contactPhone": self.contact_phone,
            "address": self.address,
            "description": self.description,
            "qualificationCount": self.qualification_count,
            "status": self.status,
        }


@dataclass
class Certificate:
    """资质证书数据模型"""
    certificate_id: int
    name: str
    certificate_no: str = ""
    type: str = ""
    level: str = ""
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    issuing_authority: str = ""
    image_path: str = ""
    status: str = "ACTIVE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificateId": self.certificate_id,
            "name": self.name,
            "certificateNo": self.certificate_no,
            "type": self.type,
            "level": self.level,
            "validFrom": self.valid_from.isoformat() if self.valid_from else None,
            "validUntil": self.valid_until.isoformat() if self.valid_until else None,
            "issuingAuthority": self.issuing_authority,
            "imagePath": self.image_path,
            "status": self.status,
        }

    def is_expired(self) -> bool:
        """检查证书是否已过期"""
        if self.valid_until is None:
            return False
        return datetime.now() > self.valid_until

    def is_expiring_soon(self, days: int = 30) -> bool:
        """检查证书是否即将过期"""
        if self.valid_until is None:
            return False
        delta = self.valid_until - datetime.now()
        return timedelta(days=0) < delta < timedelta(days=days)


@dataclass
class Experience:
    """业绩案例数据模型"""
    experience_id: int
    project_name: str
    bid_amount: float = 0.0
    bid_date: Optional[datetime] = None
    client: str = ""
    project_type: str = ""
    scale: str = ""
    quality_rating: str = ""
    description: str = ""
    contract_file: str = ""
    acceptance_file: str = ""
    is_archived: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experienceId": self.experience_id,
            "projectName": self.project_name,
            "bidAmount": self.bid_amount,
            "bidDate": self.bid_date.isoformat() if self.bid_date else None,
            "client": self.client,
            "projectType": self.project_type,
            "scale": self.scale,
            "qualityRating": self.quality_rating,
            "description": self.description,
            "contractFile": self.contract_file,
            "acceptanceFile": self.acceptance_file,
            "isArchived": self.is_archived,
        }


class EnterpriseService:
    """
    企业资料库服务

    提供企业信息查询、证书列表、业绩搜索等企业资料管理功能。
    支持与后端Java服务API交互。
    """

    def __init__(self, base_url: str = "http://localhost:8082"):
        """
        初始化企业资料库服务

        Args:
            base_url: 后端API基础URL，默认为项目服务端口
        """
        self.base_url = base_url.rstrip("/")
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """懒加载异步HTTP客户端"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self):
        """关闭HTTP客户端"""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    # ========== 企业信息 ==========

    async def get_enterprise_info(self, enterprise_id: int) -> Optional[EnterpriseInfo]:
        """
        获取企业基本信息

        Args:
            enterprise_id: 企业ID

        Returns:
            企业信息对象，查询失败返回None
        """
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/project/0/qualification/enterprise",
                params={"enterpriseId": enterprise_id}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200 and data.get("data"):
                    d = data["data"]
                    return EnterpriseInfo(
                        enterprise_id=d.get("id", enterprise_id),
                        name=d.get("name", ""),
                        unified_credit_code=d.get("unifiedCreditCode", ""),
                        type=d.get("type", ""),
                        industry=d.get("industry", ""),
                        registered_capital=float(d.get("registeredCapital") or 0),
                        legal_person=d.get("legalPerson", ""),
                        contact_phone=d.get("contactPhone", ""),
                        address=d.get("address", ""),
                        description=d.get("description", ""),
                        qualification_count=int(d.get("qualificationCount") or 0),
                        status=d.get("status", "ACTIVE"),
                    )
        except Exception as e:
            logger.warning(f"获取企业信息失败 enterprise_id={enterprise_id}: {e}")
        return None

    async def get_default_enterprise(self) -> Optional[EnterpriseInfo]:
        """获取默认企业的基本信息（用于自动填充）"""
        try:
            resp = await self.http_client.post(
                f"{self.base_url}/project/0/qualification/auto-fill"
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200 and data.get("data", {}).get("enterpriseInfo"):
                    d = data["data"]["enterpriseInfo"]
                    return EnterpriseInfo(
                        enterprise_id=d.get("enterpriseId", 0),
                        name=d.get("name", ""),
                        unified_credit_code=d.get("unifiedCreditCode", ""),
                        type=d.get("type", ""),
                        legal_person=d.get("legalPerson", ""),
                        contact_phone=d.get("contactPhone", ""),
                        address=d.get("address", ""),
                        qualification_count=int(d.get("qualificationCount") or 0),
                    )
        except Exception as e:
            logger.warning(f"获取默认企业信息失败: {e}")
        return None

    # ========== 资质证书 ==========

    async def list_certificates(
        self,
        enterprise_id: int,
        status: Optional[str] = None,
        cert_type: Optional[str] = None,
    ) -> List[Certificate]:
        """
        获取企业资质证书列表

        Args:
            enterprise_id: 企业ID
            status: 可选，证书状态过滤（ACTIVE/EXPIRED/REVOKED）
            cert_type: 可选，证书类型过滤

        Returns:
            证书列表
        """
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/project/0/qualification/list",
                params={"enterpriseId": enterprise_id}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200 and data.get("data"):
                    certificates = []
                    for item in data["data"]:
                        cert = Certificate(
                            certificate_id=item.get("id", 0),
                            name=item.get("name", ""),
                            certificate_no=item.get("certificateNo", ""),
                            type=item.get("type", ""),
                            level=item.get("level", ""),
                            valid_from=_parse_datetime(item.get("validFrom")),
                            valid_until=_parse_datetime(item.get("validUntil")),
                            issuing_authority=item.get("issuingAuthority", ""),
                            image_path=item.get("certificateImage", ""),
                            status=item.get("status", "ACTIVE"),
                        )
                        if status and cert.status != status:
                            continue
                        if cert_type and cert.type != cert_type:
                            continue
                        certificates.append(cert)
                    return certificates
        except Exception as e:
            logger.warning(f"获取证书列表失败 enterprise_id={enterprise_id}: {e}")
        return []

    async def get_expiring_certificates(
        self, enterprise_id: int, days: int = 30
    ) -> List[Certificate]:
        """获取即将过期的证书列表"""
        certificates = await self.list_certificates(enterprise_id)
        return [c for c in certificates if c.is_expiring_soon(days) and not c.is_expired()]

    async def get_expired_certificates(self, enterprise_id: int) -> List[Certificate]:
        """获取已过期的证书列表"""
        certificates = await self.list_certificates(enterprise_id)
        return [c for c in certificates if c.is_expired()]

    async def get_active_certificates(self, enterprise_id: int) -> List[Certificate]:
        """获取有效的证书列表"""
        certificates = await self.list_certificates(enterprise_id)
        return [c for c in certificates if not c.is_expired()]

    # ========== 业绩案例 ==========

    async def list_experiences(
        self,
        enterprise_id: int,
        scale: Optional[str] = None,
        project_type: Optional[str] = None,
        recent_years: Optional[int] = None,
    ) -> List[Experience]:
        """
        获取企业业绩案例列表

        Args:
            enterprise_id: 企业ID
            scale: 可选，规模过滤（大型/中型/小型）
            project_type: 可选，项目类型过滤
            recent_years: 可选，近N年的业绩

        Returns:
            业绩案例列表
        """
        try:
            resp = await self.http_client.get(
                f"{self.base_url}/project/0/qualification/experiences",
                params={"enterpriseId": enterprise_id}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200 and data.get("data"):
                    experiences = []
                    cutoff = None
                    if recent_years:
                        cutoff = datetime.now().replace(
                            year=datetime.now().year - recent_years
                        )
                    for item in data["data"]:
                        exp = Experience(
                            experience_id=item.get("id", 0),
                            project_name=item.get("projectName", ""),
                            bid_amount=float(item.get("bidAmount") or 0),
                            bid_date=_parse_datetime(item.get("bidDate")),
                            client=item.get("client", ""),
                            project_type=item.get("projectType", ""),
                            scale=item.get("scale", ""),
                            quality_rating=item.get("qualityRating", ""),
                            description=item.get("description", ""),
                            contract_file=item.get("contractFile", ""),
                            acceptance_file=item.get("acceptanceFile", ""),
                            is_archived=bool(item.get("isArchived")),
                        )
                        if scale and exp.scale != scale:
                            continue
                        if project_type and exp.project_type != project_type:
                            continue
                        if cutoff and exp.bid_date and exp.bid_date < cutoff:
                            continue
                        experiences.append(exp)
                    return experiences
        except Exception as e:
            logger.warning(f"获取业绩列表失败 enterprise_id={enterprise_id}: {e}")
        return []

    async def search_experience(
        self,
        enterprise_id: int,
        keyword: str,
        limit: int = 10,
    ) -> List[Experience]:
        """
        搜索企业业绩案例

        Args:
            enterprise_id: 企业ID
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            匹配的业绩案例列表
        """
        experiences = await self.list_experiences(enterprise_id)
        kw = keyword.lower()
        matched = [
            e for e in experiences
            if kw in e.project_name.lower()
            or kw in e.client.lower()
            or kw in e.description.lower()
            or kw in e.project_type.lower()
        ]
        return matched[:limit]

    async def get_experience_stats(self, enterprise_id: int) -> Dict[str, Any]:
        """获取企业业绩统计信息"""
        experiences = await self.list_experiences(enterprise_id)
        if not experiences:
            return {"total": 0, "totalBidAmount": 0.0, "large": 0, "medium": 0}

        total_amt = sum(e.bid_amount for e in experiences)
        return {
            "total": len(experiences),
            "totalBidAmount": total_amt,
            "large": sum(1 for e in experiences if e.scale == "大型"),
            "medium": sum(1 for e in experiences if e.scale == "中型"),
            "small": sum(1 for e in experiences if e.scale == "小型"),
            "excellent": sum(1 for e in experiences if e.quality_rating == "优良"),
        }

    # ========== 资质匹配 ==========

    async def match_qualifications(
        self, requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        匹配资质要求

        Args:
            requirements: 资质要求列表，每项包含type/level/required

        Returns:
            匹配结果
        """
        try:
            resp = await self.http_client.post(
                f"{self.base_url}/project/0/qualification/match",
                json={"requirements": requirements}
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"资质匹配请求失败: {e}")
        return {"code": 500, "message": "匹配失败", "data": None}

    async def validate_qualifications(
        self, enterprise_id: int
    ) -> List[Dict[str, Any]]:
        """
        验证企业资质有效性

        Args:
            enterprise_id: 企业ID

        Returns:
            验证结果列表
        """
        try:
            resp = await self.http_client.post(
                f"{self.base_url}/project/0/qualification/validate",
                params={"enterpriseId": enterprise_id}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return data.get("data", [])
        except Exception as e:
            logger.warning(f"资质验证请求失败 enterprise_id={enterprise_id}: {e}")
        return []


# ========== 同步包装器 ==========

class SyncEnterpriseService:
    """同步包装器，用于同步上下文调用异步服务"""

    def __init__(self, base_url: str = "http://localhost:8082"):
        self._service = EnterpriseService(base_url=base_url)

    def get_enterprise_info(self, enterprise_id: int) -> Optional[EnterpriseInfo]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._service.get_enterprise_info(enterprise_id))

    def list_certificates(
        self, enterprise_id: int, status: Optional[str] = None, cert_type: Optional[str] = None
    ) -> List[Certificate]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._service.list_certificates(enterprise_id, status, cert_type)
        )

    def search_experience(self, enterprise_id: int, keyword: str, limit: int = 10) -> List[Experience]:
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._service.search_experience(enterprise_id, keyword, limit)
        )


# ========== 全局单例 ==========

_enterprise_service: Optional[EnterpriseService] = None


def get_enterprise_service() -> EnterpriseService:
    """获取全局企业资料库服务单例"""
    global _enterprise_service
    if _enterprise_service is None:
        _enterprise_service = EnterpriseService(
            base_url=os.getenv("PROJECT_SERVICE_URL", "http://localhost:8082")
        )
    return _enterprise_service


# ========== 工具函数 ==========

def _parse_datetime(value: Any) -> Optional[datetime]:
    """解析日期时间字符串"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None