#!/usr/bin/env python3
"""验证图表/表格/重新排序 - 优化版"""

import asyncio
import subprocess
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(20000)

        print("=== 验证图表/表格/重新排序 ===\n")

        # 1. 直接导航到编辑器的正确路由
        print("--- 1. 进入标书列表 ---")
        await page.goto(f"{BASE}/bid/list", wait_until="networkidle")
        await asyncio.sleep(2)

        url_before = page.url
        print(f"   当前URL: {url_before}")

        # 2. 找到有数据的行，获取bid ID
        print("\n--- 2. 查找标书ID ---")
        try:
            # 等待表格加载
            await page.wait_for_selector("tr", timeout=5000)
            rows = page.locator("tr")
            count = await rows.count()
            print(f"   表格行数: {count}")

            if count > 1:  # 有表头+数据
                # 获取第一行数据的ID（通常在第一个td或data属性）
                first_row = rows.first
                # 尝试获取data-id或id属性
                row_html = await first_row.inner_html()
                print(f"   第一行HTML片段: {row_html[:200]}")

                # 点击第一行数据（跳过表头）
                await rows.nth(1).click()
                await asyncio.sleep(3)
                url_after = page.url
                print(f"   点击后URL: {url_after}")
        except Exception as e:
            print(f"   查找失败: {str(e)[:100]}")

        # 3. 检查当前页面元素
        print("\n--- 3. 页面元素分析 ---")
        all_buttons = await page.locator("button").all()
        btn_info = []
        for b in all_buttons:
            try:
                text = (await b.inner_text()).strip()
                visible = await b.is_visible()
                if text:
                    btn_info.append(f"{text}(可见:{visible})")
            except:
                pass
        print(f"   所有按钮: {btn_info}")

        # 4. 检查工具栏
        toolbar = page.locator(".toolbar, [class*='toolbar'], header, nav")
        toolbar_count = await toolbar.count()
        print(f"   工具栏元素: {toolbar_count}个")

        # 5. 检查编辑器区域
        editor_selectors = [
            ".ProseMirror",
            "[class*='ProseMirror']",
            "[class*='editor']",
            "[class*='content']",
            "textarea",
            "[contenteditable='true']"
        ]
        for sel in editor_selectors:
            c = await page.locator(sel).count()
            if c > 0:
                print(f"   编辑器元素 {sel}: {c}个")

        # 6. 截图看真相
        print("\n--- 4. 截图 ---")
        screenshot_path = "/home/zzy/.openclaw/workspace/workspace-bid/docs/debug_editor.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"   截图已保存: {screenshot_path}")
        print(f"   当前URL: {page.url}")
        print(f"   页面title: {await page.title()}")

        await browser.close()
        print("\n=== 完成 ===")

if __name__ == "__main__":
    asyncio.run(main())