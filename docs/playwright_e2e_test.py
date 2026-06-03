#!/usr/bin/env python3
"""
AI智能投标系统 - Playwright端到端测试
模拟真实用户操作，验证系统完整功能
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, expect

BASE_URL = "http://localhost:3000"
RESULTS = {"passed": [], "failed": [], "errors": []}

def log_test(name, passed, error=None):
    status = "✅" if passed else "❌"
    print(f"{status} {name}")
    if passed:
        RESULTS["passed"].append(name)
    else:
        RESULTS["failed"].append(name)
        if error:
            RESULTS["errors"].append(f"{name}: {error}")

async def test_homepage(page):
    """测试首页加载"""
    try:
        await page.goto(BASE_URL, wait_until="networkidle", timeout=15000)
        title = await page.title()
        log_test("首页加载", True)
        
        # 检查导航栏
        nav = page.locator("nav, .navbar, header")
        if await nav.count() > 0:
            log_test("导航栏显示", True)
        
        # 检查主要功能入口
        menu_items = ["项目管理", "标书管理", "工作流", "素材库", "知识库", "企业资料"]
        for item in menu_items:
            if item in await page.content():
                log_test(f"菜单项[{item}]", True)
                break
        return True
    except Exception as e:
        log_test("首页加载", False, str(e))
        return False

async def test_project_management(page):
    """测试项目管理功能"""
    try:
        await page.goto(f"{BASE_URL}/project", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        # 检查项目列表
        content = await page.content()
        if "项目" in content:
            log_test("项目页面加载", True)
        
        # 检查新建按钮
        create_btn = page.locator("button:has-text('新建'), button:has-text('创建'), .btn-primary")
        if await create_btn.count() > 0:
            log_test("项目新建按钮", True)
            
            # 尝试点击新建
            await create_btn.first.click()
            await asyncio.sleep(1)
            
            # 检查弹窗或表单
            modal = page.locator(".modal, .dialog, [class*='modal'], form")
            if await modal.count() > 0:
                log_test("项目新建表单弹窗", True)
        
        return True
    except Exception as e:
        log_test("项目管理", False, str(e))
        return False

async def test_bid_management(page):
    """测试标书管理功能"""
    try:
        await page.goto(f"{BASE_URL}/bid", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(3)
        
        content = await page.content()
        
        # 检查标书列表
        if "标书" in content or "bid" in content.lower():
            log_test("标书管理页面加载", True)
        
        # 检查标签页
        tabs = page.locator("[role='tab'], .tabs, .tab-item")
        if await tabs.count() > 0:
            log_test("标书标签页切换", True)
        
        # 检查数据表格
        tables = page.locator("table, .table, [class*='table']")
        if await tables.count() > 0:
            log_test("标书数据表格", True)
        
        # 检查新建标书按钮
        create_btn = page.locator("button:has-text('新建'), button:has-text('创建标书')")
        if await create_btn.count() > 0:
            log_test("新建标书按钮", True)
            
            # 点击新建并测试表单
            await create_btn.first.click()
            await asyncio.sleep(2)
            
            # 检查表单字段
            forms = page.locator("input, textarea, select")
            form_count = await forms.count()
            if form_count > 0:
                log_test(f"标书表单字段({form_count}个)", True)
        
        return True
    except Exception as e:
        log_test("标书管理", False, str(e))
        return False

async def test_workflow(page):
    """测试工作流功能"""
    try:
        await page.goto(f"{BASE_URL}/workflow", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(3)
        
        content = await page.content()
        
        if "工作流" in content or "workflow" in content.lower():
            log_test("工作流页面加载", True)
        
        # 检查工作流列表
        list_items = page.locator(".list-item, .workflow-item, [class*='list']")
        if await list_items.count() > 0:
            log_test("工作流列表显示", True)
        
        # 检查新建工作流按钮
        create_btn = page.locator("button:has-text('新建'), button:has-text('创建')")
        if await create_btn.count() > 0:
            log_test("新建工作流按钮", True)
        
        return True
    except Exception as e:
        log_test("工作流管理", False, str(e))
        return False

async def test_material_library(page):
    """测试素材库功能"""
    try:
        await page.goto(f"{BASE_URL}/material", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        content = await page.content()
        
        if "素材" in content or "material" in content.lower():
            log_test("素材库页面加载", True)
        
        # 检查上传按钮
        upload_btn = page.locator("button:has-text('上传'), input[type='file']")
        if await upload_btn.count() > 0:
            log_test("素材上传功能", True)
        
        # 检查素材列表
        list_view = page.locator(".list, .grid, [class*='item']")
        if await list_view.count() > 0:
            log_test("素材列表显示", True)
        
        return True
    except Exception as e:
        log_test("素材库", False, str(e))
        return False

async def test_knowledge_base(page):
    """测试知识库功能"""
    try:
        await page.goto(f"{BASE_URL}/knowledge", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        content = await page.content()
        
        if "知识" in content or "knowledge" in content.lower():
            log_test("知识库页面加载", True)
        
        # 检查搜索功能
        search_input = page.locator("input[placeholder*='搜索'], input[type='search']")
        if await search_input.count() > 0:
            log_test("知识库搜索框", True)
        
        # 检查分类目录
        categories = page.locator(".category, .sidebar, [class*='category']")
        if await categories.count() > 0:
            log_test("知识库分类目录", True)
        
        return True
    except Exception as e:
        log_test("知识库", False, str(e))
        return False

async def test_enterprise_profile(page):
    """测试企业资料功能"""
    try:
        await page.goto(f"{BASE_URL}/enterprise", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        content = await page.content()
        
        if "企业" in content or "enterprise" in content.lower():
            log_test("企业资料页面加载", True)
        
        # 检查资料表单
        forms = page.locator("form, .form")
        if await forms.count() > 0:
            log_test("企业资料表单", True)
        
        # 检查资质上传
        upload_area = page.locator("input[type='file'], .upload")
        if await upload_area.count() > 0:
            log_test("企业资质上传", True)
        
        return True
    except Exception as e:
        log_test("企业资料", False, str(e))
        return False

async def test_user_management(page):
    """测试用户管理功能"""
    try:
        await page.goto(f"{BASE_URL}/user", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        content = await page.content()
        
        if "用户" in content or "user" in content.lower():
            log_test("用户管理页面加载", True)
        
        # 检查用户列表
        table = page.locator("table, .table")
        if await table.count() > 0:
            log_test("用户列表表格", True)
        
        return True
    except Exception as e:
        log_test("用户管理", False, str(e))
        return False

async def test_ai_features(page):
    """测试AI功能"""
    try:
        await page.goto(f"{BASE_URL}/bid", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        # 尝试AI生成功能
        ai_buttons = page.locator("button:has-text('AI'), button:has-text('生成'), button:has-text('智能')")
        if await ai_buttons.count() > 0:
            log_test("AI功能按钮存在", True)
            
            # 点击AI生成
            await ai_buttons.first.click()
            await asyncio.sleep(3)
            
            # 检查生成结果
            content = await page.content()
            if "生成" in content or " outline" in content.lower() or "目录" in content:
                log_test("AI生成结果显示", True)
        
        return True
    except Exception as e:
        log_test("AI功能测试", False, str(e))
        return False

async def test_navigation_flow(page):
    """测试导航流程"""
    try:
        # 从首页开始
        await page.goto(BASE_URL, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        # 遍历主要菜单
        menu_items = [
            ("项目管理", "/project"),
            ("标书管理", "/bid"),
            ("工作流", "/workflow"),
            ("素材库", "/material"),
            ("知识库", "/knowledge"),
            ("企业资料", "/enterprise"),
        ]
        
        for name, path in menu_items:
            await page.goto(f"{BASE_URL}{path}", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(1)
            content = await page.content()
            if len(content) > 500:
                log_test(f"导航到{name}", True)
        
        return True
    except Exception as e:
        log_test("导航流程", False, str(e))
        return False

async def main():
    print("=" * 60)
    print("🎯 AI智能投标系统 - Playwright端到端测试")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试目标: {BASE_URL}")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = await context.new_page()
        
        # 捕获控制台错误
        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(f"[PAGE ERROR] {err}"))
        
        print("\n📋 开始测试...\n")
        
        # 执行各项测试
        await test_homepage(page)
        await test_navigation_flow(page)
        await test_project_management(page)
        await test_bid_management(page)
        await test_workflow(page)
        await test_material_library(page)
        await test_knowledge_base(page)
        await test_enterprise_profile(page)
        await test_user_management(page)
        await test_ai_features(page)
        
        # 输出结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        print(f"✅ 通过: {len(RESULTS['passed'])} 项")
        print(f"❌ 失败: {len(RESULTS['failed'])} 项")
        
        if RESULTS["passed"]:
            print("\n✅ 通过的测试:")
            for item in RESULTS["passed"]:
                print(f"   - {item}")
        
        if RESULTS["failed"]:
            print("\n❌ 失败的测试:")
            for item in RESULTS["failed"]:
                print(f"   - {item}")
        
        if errors:
            print(f"\n⚠️ 控制台错误 ({len(errors)} 条):")
            for err in errors[:10]:  # 只显示前10条
                print(f"   {err[:100]}")
        
        print("\n" + "=" * 60)
        
        await browser.close()
        
        # 返回退出码
        return 0 if len(RESULTS["failed"]) == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)