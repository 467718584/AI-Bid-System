#!/usr/bin/env python3
"""深入调试表格渲染问题"""

import asyncio
import subprocess
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        print("=== 深入调试表格渲染 ===\n")

        # 1. 登录并进入标书列表
        print("--- 1. 登录 ---")
        await page.goto(f"{BASE}/login", wait_until="networkidle")
        await asyncio.sleep(2)
        print(f"   URL: {page.url}")
        print(f"   Title: {await page.title()}")

        # 2. 进入标书列表
        print("\n--- 2. 进入标书列表 ---")
        await page.goto(f"{BASE}/bid/list", wait_until="networkidle")
        await asyncio.sleep(2)
        print(f"   URL: {page.url}")

        # 3. 找到"测试更新标题"并点击
        print("\n--- 3. 找到目标标书 ---")
        rows = page.locator("tr")
        count = await rows.count()
        print(f"   找到{count}行")

        for i in range(min(count, 10)):
            row = rows.nth(i)
            text = await row.inner_text()
            if "测试更新标题" in text or "测试" in text:
                print(f"   第{i}行包含测试: {text[:80]}")
                await row.click()
                await asyncio.sleep(3)
                break

        print(f"   当前URL: {page.url}")

        # 4. 获取编辑器内容
        print("\n--- 4. 编辑器内容分析 ---")

        # 等待编辑器加载
        try:
            await page.wait_for_selector(".ProseMirror, [contenteditable='true'], textarea", timeout=5000)
        except:
            print("   等待编辑器超时")

        await asyncio.sleep(2)

        # 获取页面HTML
        html = await page.content()

        # 查找包含|符号的内容（表格MD格式）
        if "|<p>" in html or "|<span" in html or "|</p>" in html:
            print("   ⚠️ 页面中存在MD表格符号|")
            # 找到相关内容
            import re
            table_patterns = re.findall(r'<p>\s*\|[^<]+\|\s*</p>', html)
            print(f"   找到{len(table_patterns)}个<p>|...|</p>格式")
            for p in table_patterns[:5]:
                print(f"     {p[:100]}")
        else:
            print("   ✅ 未发现<p>|格式")

        # 检查是否有已转换的表格
        table_count = await page.locator("table").count()
        print(f"   HTML表格数量: {table_count}")

        # 5. 查看具体内容区域的原始内容
        print("\n--- 5. 编辑器DOM内容 ---")
        editor = page.locator(".ProseMirror, [contenteditable='true']").first
        if await editor.count() > 0:
            editor_html = await editor.inner_html()
            print(f"   编辑器HTML长度: {len(editor_html)}")
            # 找|相关内容
            if "|" in editor_html:
                idx = editor_html.find("|")
                print(f"   包含|符号位置: {idx}")
                print(f"   前后内容: ...{editor_html[max(0,idx-50):idx+100]}...")
        else:
            print("   未找到编辑器元素")

        # 6. 截图
        screenshot_path = "/home/zzy/.openclaw/workspace/workspace-bid/docs/debug_table.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n--- 截图已保存: {screenshot_path} ---")

        await browser.close()
        print("\n=== 完成 ===")

if __name__ == "__main__":
    asyncio.run(main())