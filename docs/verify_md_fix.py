#!/usr/bin/env python3
"""验证MD表格修复"""

import asyncio
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        print("=== 验证MD表格修复 ===\n")

        # 1. 进入标书列表
        await page.goto(f"{BASE}/bid/list", wait_until="networkidle")
        await asyncio.sleep(2)
        print(f"URL: {page.url}")

        # 2. 点击进入"测试更新标题"
        rows = page.locator("tr")
        count = await rows.count()
        print(f"找到{count}行")

        target_found = False
        for i in range(min(count, 10)):
            row = rows.nth(i)
            text = await row.inner_text()
            if "测试更新标题" in text:
                print(f"点击第{i}行")
                await row.click()
                await asyncio.sleep(3)
                target_found = True
                break

        if not target_found:
            print("未找到目标标书")
            await browser.close()
            return

        print(f"当前URL: {page.url}")

        # 3. 检查表格
        await asyncio.sleep(2)

        # 查找HTML表格
        tables = await page.locator("table").count()
        print(f"\nHTML表格数量: {tables}")

        if tables > 0:
            # 检查表格内容
            first_table = page.locator("table").first
            headers = await first_table.locator("th").all_inner_texts()
            print(f"表头: {headers[:5]}")
            rows_count = await first_table.locator("tr").count()
            print(f"行数: {rows_count}")

        # 4. 检查是否还有MD格式
        html = await page.content()
        md_pattern_count = html.count('<p>|') - html.count('<table')
        print(f"\nMD表格残留 (<p>|): {md_pattern_count}")

        # 5. 检查编辑器的ProseMirror内容
        editor = page.locator(".ProseMirror, [contenteditable='true']").first
        if await editor.count() > 0:
            editor_html = await editor.inner_html()
            has_table_in_editor = '<table' in editor_html
            has_md_table_in_editor = '<p>|' in editor_html and '|' in editor_html
            print(f"编辑器含HTML表格: {has_table_in_editor}")
            print(f"编辑器含MD表格: {has_md_table_in_editor}")

        # 6. 截图
        await page.screenshot(path="/home/zzy/.openclaw/workspace/workspace-bid/docs/verify_table_fix.png", full_page=True)
        print("\n截图已保存")

        print("\n=== 验证结果 ===")
        if tables > 0 and md_pattern_count < 3:
            print("✅ MD表格转换成功!")
        elif tables == 0:
            print("❌ 未找到HTML表格")
        else:
            print("⚠️ 部分转换成功")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())