#!/usr/bin/env python3
"""验证表格MD转HTML修复"""

import asyncio
import subprocess
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)

        print("=== 验证表格MD转HTML修复 ===\n")

        # 1. 进入标书列表
        await page.goto(f"{BASE}/bid/list", wait_until="networkidle")
        await asyncio.sleep(2)

        # 2. 找"测试更新标题"点击进入
        print("--- 1. 进入标书 ---")
        rows = page.locator("tr")
        count = await rows.count()
        print(f"   找到{count}行")

        target_found = False
        for i in range(min(count, 20)):
            row = rows.nth(i)
            text = await row.inner_text()
            if "测试更新标题" in text:
                print(f"   点击第{i}行: {text[:60]}")
                await row.click()
                await asyncio.sleep(3)
                target_found = True
                break

        if not target_found:
            print("   未找到'测试更新标题'，尝试其他方式进入")
            await rows.first.click()
            await asyncio.sleep(3)

        print(f"   当前URL: {page.url}")

        # 3. 检查编辑器内容
        print("\n--- 2. 编辑器表格检查 ---")
        await asyncio.sleep(2)

        # 等待编辑器加载
        try:
            await page.wait_for_selector(".ProseMirror", timeout=5000)
            print("   编辑器已加载")
        except:
            print("   编辑器等待超时")

        # 检查页面中是否有<p>|格式
        html = await page.content()
        md_table_pattern = '<p>|' in html or '|<p>' in html
        print(f"   页面含MD表格符号: {md_table_pattern}")

        # 检查是否有HTML表格
        table_count = await page.locator("table").count()
        print(f"   HTML表格数量: {table_count}")

        # 检查表格内是否有数据
        if table_count > 0:
            first_table = page.locator("table").first
            rows_in_table = await first_table.locator("tr").count()
            print(f"   第一个表格行数: {rows_in_table}")
            # 获取表头
            headers = await first_table.locator("th").all_inner_texts()
            print(f"   表头: {headers}")

        # 4. 截图
        screenshot_path = "/home/zzy/.openclaw/workspace/workspace-bid/docs/verify_table_fix.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n--- 截图: {screenshot_path} ---")

        # 5. 结果判定
        print("\n=== 验证结果 ===")
        if table_count > 0 and rows_in_table >= 2:
            print("✅ 表格MD转HTML修复成功！")
        elif md_table_pattern:
            print("❌ 仍存在MD格式表格，未转换成功")
        else:
            print("⚠️ 无法确定，可能没有表格数据")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())