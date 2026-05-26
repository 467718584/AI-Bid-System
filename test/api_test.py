#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能投标系统 - Python API测试脚本
AI Bid System - Python API Test Script

依赖安装:
    pip install requests colorama

用法:
    python api_test.py [选项]
    -h, --help       显示帮助
    -v, --verbose    详细输出
    -s, --service    仅测试指定服务
    --skip-auth      跳过认证测试
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False


def color(text: str, color_code: str = "") -> str:
    """返回带颜色的文本"""
    if not COLOR_ENABLED:
        return text
    return f"{color_code}{text}{Style.RESET_ALL}"


def green(text: str) -> str:
    return color(text, Fore.GREEN)


def red(text: str) -> str:
    return color(text, Fore.RED)


def yellow(text: str) -> str:
    return color(text, Fore.YELLOW)


def blue(text: str) -> str:
    return color(text, Fore.BLUE)


def cyan(text: str) -> str:
    return color(text, Fore.CYAN)


# ============================================
# 配置
# ============================================

@dataclass
class Config:
    """服务配置"""
    GATEWAY_URL: str = "http://localhost:8080"
    USER_URL: str = "http://localhost:8081"
    PROJECT_URL: str = "http://localhost:8082"
    MATERIAL_URL: str = "localhost:8083"
    DOCUMENT_URL: str = "http://localhost:8084"
    KNOWLEDGE_URL: str = "http://localhost:8086"
    AI_URL: str = "http://localhost:8087"

    # 默认测试用户
    TEST_USERNAME: str = "admin"
    TEST_PASSWORD: str = "admin123"

    # 超时设置
    REQUEST_TIMEOUT: int = 30


config = Config()


# ============================================
# API客户端
# ============================================

class APIClient:
    """API测试客户端"""

    def __init__(self, base_url: str, token: str = None, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def set_token(self, token: str):
        """设置认证Token"""
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(self, method: str, path: str, data: Any = None,
                headers: Dict = None) -> Tuple[int, Dict]:
        """
        发送HTTP请求

        Returns:
            Tuple[int, Dict]: (HTTP状态码, 响应JSON)
        """
        url = urljoin(self.base_url + "/", path.lstrip('/'))

        req_headers = self._get_headers()
        if headers:
            req_headers.update(headers)

        if self.verbose:
            print(f"  {cyan('→')} {method} {url}")
            if data:
                print(f"  {cyan('Data:')} {json.dumps(data, ensure_ascii=False)[:200]}")

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data, headers=req_headers,
                                          timeout=config.REQUEST_TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers,
                                             timeout=config.REQUEST_TIMEOUT)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers,
                                            timeout=config.REQUEST_TIMEOUT)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers,
                                              timeout=config.REQUEST_TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")

            try:
                body = response.json()
            except json.JSONDecodeError:
                body = {"raw": response.text[:500]}

            if self.verbose:
                print(f"  {cyan('←')} HTTP {response.status_code}")
                print(f"  {cyan('Response:')} {json.dumps(body, ensure_ascii=False)[:300]}")

            return response.status_code, body

        except requests.exceptions.ConnectionError as e:
            return 0, {"error": f"Connection error: {str(e)}"}
        except requests.exceptions.Timeout as e:
            return 0, {"error": f"Timeout: {str(e)}"}
        except Exception as e:
            return 0, {"error": str(e)}

    def get(self, path: str, params: Dict = None) -> Tuple[int, Dict]:
        return self.request("GET", path, params)

    def post(self, path: str, data: Any = None) -> Tuple[int, Dict]:
        return self.request("POST", path, data)

    def put(self, path: str, data: Any = None) -> Tuple[int, Dict]:
        return self.request("PUT", path, data)

    def delete(self, path: str) -> Tuple[int, Dict]:
        return self.request("DELETE", path)


# ============================================
# 测试结果收集器
# ============================================

@dataclass
class TestResult:
    """测试结果"""
    name: str
    passed: bool
    status_code: int
    message: str
    duration: float = 0


class TestRunner:
    """测试运行器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.gateway_client = APIClient(config.GATEWAY_URL, verbose=verbose)
        self.user_client = APIClient(config.USER_URL, verbose=verbose)
        self.project_client = APIClient(config.PROJECT_URL, verbose=verbose)
        self.material_client = APIClient(config.MATERIAL_URL, verbose=verbose)
        self.document_client = APIClient(config.DOCUMENT_URL, verbose=verbose)
        self.knowledge_client = APIClient(config.KNOWLEDGE_URL, verbose=verbose)
        self.ai_client = APIClient(config.AI_URL, verbose=verbose)
        self.token: str = ""
        self.test_project_id: str = ""

    def add_result(self, name: str, passed: bool, status_code: int,
                   message: str = "", duration: float = 0):
        """添加测试结果"""
        self.results.append(TestResult(name, passed, status_code, message, duration))
        symbol = green("✓") if passed else red("✗")
        status_str = green(f"HTTP {status_code}") if passed else red(f"HTTP {status_code}")
        print(f"  {symbol} {name} - {status_str}")
        if message and self.verbose:
            print(f"    {message}")

    def run_test(self, name: str, func) -> bool:
        """运行单个测试"""
        start_time = time.time()
        try:
            result = func()
            duration = time.time() - start_time
            if isinstance(result, tuple):
                passed, status_code, message = result
                self.add_result(name, passed, status_code, message, duration)
                return passed
            else:
                self.add_result(name, result, 200, "", duration)
                return result
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(name, False, 0, str(e), duration)
            return False

    # ============================================
    # 健康检查测试
    # ============================================

    def test_health_checks(self) -> int:
        """测试所有服务健康检查"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('1. 健康检查测试')}")
        print(f"{blue('═' * 50}")

        services = [
            ("Gateway", self.gateway_client, "health"),
            ("User Service", self.user_client, "health"),
            ("Project Service", self.project_client, "health"),
            ("Material Service", self.material_client, "health"),
            ("Document Service", self.document_client, "health"),
            ("Knowledge Service", self.knowledge_client, "health"),
            ("AI Service", self.ai_client, "health"),
        ]

        all_passed = True
        for name, client, path in services:
            code, body = client.get(path)
            if code == 200:
                print(f"  {green('✓')} [{name}] OK")
            else:
                print(f"  {red('✗')} [{name}] HTTP {code}")
                all_passed = False

        return 0 if all_passed else 1

    # ============================================
    # 认证测试
    # ============================================

    def test_auth(self) -> int:
        """测试认证接口"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('2. 认证接口测试')}")
        print(f"{blue('═' * 50}")

        failed = 0

        # 登录测试
        code, body = self.gateway_client.post(
            "api/auth/login",
            {"username": config.TEST_USERNAME, "password": config.TEST_PASSWORD}
        )

        if code == 200 and "data" in body and "token" in body.get("data", {}):
            self.token = body["data"]["token"]
            self.gateway_client.set_token(self.token)
            self.user_client.set_token(self.token)
            self.project_client.set_token(self.token)
            self.material_client.set_token(self.token)
            self.document_client.set_token(self.token)
            self.knowledge_client.set_token(self.token)
            self.ai_client.set_token(self.token)
            print(f"  {green('✓')} 登录成功")
        else:
            print(f"  {yellow('⚠')} 登录失败 (HTTP {code}) - 使用模拟Token继续测试")
            self.token = "mock_token_for_testing"
            for client in [self.gateway_client, self.user_client, self.project_client,
                           self.material_client, self.document_client,
                           self.knowledge_client, self.ai_client]:
                client.set_token(self.token)

        # Token刷新测试
        if self.token and self.token != "mock_token_for_testing":
            code, body = self.gateway_client.post(
                "api/auth/refresh",
                {"refreshToken": self.token}
            )
            if code == 200:
                print(f"  {green('✓')} Token刷新成功")
            else:
                print(f"  {yellow('⚠')} Token刷新失败 (HTTP {code})")
                failed += 1
        else:
            print(f"  {yellow('⚠')} 跳过Token刷新测试")

        return failed

    # ============================================
    # 用户管理测试
    # ============================================

    def test_user_service(self) -> int:
        """测试用户管理接口"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('3. 用户管理接口测试')}")
        print(f"{blue('═' * 50}")

        failed = 0

        # 获取用户列表
        code, body = self.user_client.get("api/users")
        if code in [200, 401]:
            print(f"  {green('✓')} 获取用户列表 (HTTP {code})")
        else:
            print(f"  {red('✗')} 获取用户列表失败 (HTTP {code})")
            failed += 1

        # 获取角色列表
        code, body = self.user_client.get("api/roles")
        if code in [200, 401]:
            print(f"  {green('✓')} 获取角色列表 (HTTP {code})")
        else:
            print(f"  {red('✗')} 获取角色列表失败 (HTTP {code})")
            failed += 1

        return failed

    # ============================================
    # 项目管理测试
    # ============================================

    def test_project_service(self) -> int:
        """测试项目管理接口"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('4. 项目管理接口测试')}")
        print(f"{blue('═' * 50}")

        failed = 0

        # 获取项目列表
        code, body = self.project_client.get("api/projects")
        if code in [200, 401]:
            print(f"  {green('✓')} 获取项目列表 (HTTP {code})")
        else:
            print(f"  {red('✗')} 获取项目列表失败 (HTTP {code})")
            failed += 1

        # 创建项目
        code, body = self.project_client.post(
            "api/projects",
            {
                "projectName": "API测试项目",
                "bidAmount": 1000000,
                "projectType": "水利工程",
                "tenderer": "测试招标单位"
            }
        )
        if code in [200, 201, 401]:
            if code in [200, 201] and "data" in body:
                self.test_project_id = str(body["data"].get("id", ""))
                print(f"  {green('✓')} 创建项目成功 (HTTP {code}), ID: {self.test_project_id}")
            else:
                print(f"  {green('✓')} 创建项目 (HTTP {code}, 需要认证)")
        else:
            print(f"  {red('✗')} 创建项目失败 (HTTP {code})")
            failed += 1

        return failed

    # ============================================
    # 素材库测试
    # ============================================

    def test_material_service(self) -> int:
        """测试素材库接口"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('5. 素材库接口测试')}")
        print(f"{blue('═' * 50}")

        failed = 0

        # 获取分类树
        code, body = self.material_client.get("api/materials/categories")
        if code in [200, 401]:
            print(f"  {green('✓')} 获取素材分类树 (HTTP {code})")
        else:
            print(f"  {red('✗')} 获取素材分类树失败 (HTTP {code})")
            failed += 1

        # 获取素材列表
        code, body = self.material_client.get("api/materials")
        if code in [200, 401]:
            print(f"  {green('✓')} 获取素材列表 (HTTP {code})")
        else:
            print(f"  {red('✗')} 获取素材列表失败 (HTTP {code})")
            failed += 1

        return failed

    # ============================================
    # 文档管理测试
    # ============================================

    def test_document_service(self) -> int:
        """测试文档管理接口"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('6. 文档管理接口测试')}")
        print(f"{blue('═' * 50}")

        failed = 0

        # 获取文档列表
        code, body = self.document_client.get("api/documents")
        if code in [200, 401]:
            print(f"  {green('✓')} 获取文档列表 (HTTP {code})")
        else:
            print(f"  {red('✗')} 获取文档列表失败 (HTTP {code})")
            failed += 1

        return failed

    # ============================================
    # 知识库测试
    # ============================================

    def test_knowledge_service(self) -> int:
        """测试知识库接口"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('7. 知识库接口测试')}")
        print(f"{blue('═' * 50}")

        failed = 0

        # 获取知识库列表
        code, body = self.knowledge_client.get("api/knowledge/bases")
        if code in [200, 401]:
            print(f"  {green('✓')} 获取知识库列表 (HTTP {code})")
        else:
            print(f"  {red('✗')} 获取知识库列表失败 (HTTP {code})")
            failed += 1

        # 向量检索测试
        code, body = self.knowledge_client.post(
            "api/knowledge/bases/1/retrieve",
            {"query": "施工组织设计", "topK": 3, "minSimilarity": 0.7}
        )
        if code in [200, 401]:
            print(f"  {green('✓')} 向量检索 (HTTP {code})")
        else:
            print(f"  {yellow('⚠')} 向量检索 (HTTP {code}) - 知识库可能为空")
            failed += 1

        return failed

    # ============================================
    # AI服务测试
    # ============================================

    def test_ai_service(self) -> int:
        """测试AI服务接口"""
        print(f"\n{blue('═' * 50)}")
        print(f"{blue('8. AI服务接口测试')}")
        print(f"{blue('═' * 50}")

        failed = 0

        # 技术标目录生成
        code, body = self.ai_client.post(
            "api/ai/generate/outline",
            {
                "projectId": "test-id",
                "expectedPages": 50,
                "rule": "MIXED",
                "scoringPoints": ["施工方案", "质量保证"]
            }
        )
        if code in [200, 401]:
            print(f"  {green('✓')} 技术标目录生成 (HTTP {code})")
        else:
            print(f"  {red('✗')} 技术标目录生成失败 (HTTP {code})")
            failed += 1

        # 标书改写
        code, body = self.ai_client.post(
            "api/ai/rewrite",
            {
                "content": "原有标书内容",
                "strategy": "EXPAND",
                "multiplier": 1.5,
                "preserveKeywords": ["水库", "除险加固"]
            }
        )
        if code in [200, 401]:
            print(f"  {green('✓')} 标书改写 (HTTP {code})")
        else:
            print(f"  {red('✗')} 标书改写失败 (HTTP {code})")
            failed += 1

        # 合规检测
        code, body = self.ai_client.post(
            "api/ai/check/compliance",
            {
                "projectId": "test-id",
                "documentContent": "标书内容",
                "checkTypes": ["DISQUALIFICATION", "KEYWORD"]
            }
        )
        if code in [200, 401]:
            print(f"  {green('✓')} 合规检测 (HTTP {code})")
        else:
            print(f"  {red('✗')} 合规检测失败 (HTTP {code})")
            failed += 1

        return failed

    # ============================================
    # 运行所有测试
    # ============================================

    def run_all(self, service_filter: str = None, skip_auth: bool = False) -> int:
        """运行所有测试"""
        print(f"\n{'=' * 50}")
        print(f"  AI智能投标系统 - API自动化测试")
        print(f"{'=' * 50}")

        total_failed = 0

        # 健康检查
        total_failed += self.test_health_checks()

        # 认证测试
        if not skip_auth:
            total_failed += self.test_auth()

        # 业务服务测试
        if not service_filter or service_filter == "user":
            total_failed += self.test_user_service()

        if not service_filter or service_filter == "project":
            total_failed += self.test_project_service()

        if not service_filter or service_filter == "material":
            total_failed += self.test_material_service()

        if not service_filter or service_filter == "document":
            total_failed += self.test_document_service()

        if not service_filter or service_filter == "knowledge":
            total_failed += self.test_knowledge_service()

        if not service_filter or service_filter == "ai":
            total_failed += self.test_ai_service()

        # 总结
        print(f"\n{'=' * 50}")
        if total_failed == 0:
            print(f"  {green('✓ 所有测试完成!')}")
        else:
            print(f"  {red('✗ 测试完成，')} {red(str(total_failed))} {red('项测试失败')}")
        print(f"{'=' * 50}\n")

        return total_failed

    def print_summary(self):
        """打印测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print(f"\n测试摘要:")
        print(f"  总计: {total}")
        print(f"  通过: {green(str(passed))}")
        print(f"  失败: {red(str(failed))}")

        if failed > 0:
            print(f"\n失败测试:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.message or 'HTTP ' + str(r.status_code)}")


def main():
    parser = argparse.ArgumentParser(
        description="AI智能投标系统 - API测试脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细输出模式")
    parser.add_argument("-s", "--service",
                        choices=["gateway", "user", "project", "material",
                                "document", "knowledge", "ai"],
                        help="仅测试指定服务")
    parser.add_argument("--skip-auth", action="store_true",
                        help="跳过认证测试")

    args = parser.parse_args()

    runner = TestRunner(verbose=args.verbose)
    failed = runner.run_all(service_filter=args.service, skip_auth=args.skip_auth)

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()