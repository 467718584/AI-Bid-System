#!/usr/bin/env python3
"""验证昨晚修复成果 - 图表/表格/重新排序/编辑器"""

import asyncio
import subprocess
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
RESULTS = []

def log(n, ok, detail=""):
    print(f"{'✅' if ok else '❌'} {n}")
    if detail:
        print(f"   {detail}")
    RESULTS.append(ok)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(15000)

        # === 1. 服务健康 ===
        print("\n=== 服务健康检查 ===")
        ports = {8081:"ai-bid-user",8082:"ai-bid-project",8083:"ai-bid-material",
                 8084:"ai-bid-document",8085:"ai-bid-bid",8086:"ai-bid-knowledge",
                 8087:"ai-bid-ai",8090:"Gateway"}
        for port, name in ports.items():
            try:
                r = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}",
                                   f"http://localhost:{port}/"], capture_output=True, text=True, timeout=3)
                log(f"{name}:{port}", r.stdout.strip() in ["200","404","302"], r.stdout.strip())
            except:
                log(f"{name}:{port}", False, "超时")

        # === 2. 标书列表页 ===
        print("\n=== 标书列表页 ===")
        await page.goto(f"{BASE}/bid/list", wait_until="networkidle")
        await asyncio.sleep(1)
        content = await page.content()
        log("标书列表页title", "标书" in await page.title())
        log("标书列表内容", len(content) > 100)

        # 检查按钮
        buttons = await page.locator("button").all()
        btn_texts = [await b.inner_text() for b in buttons]
        print(f"   页面按钮: {btn_texts[:10]}")
        log("有按钮", len(buttons) > 0, f"共{len(buttons)}个")

        # === 3. 创建标书流程 ===
        print("\n=== 创建标书流程 ===")
        try:
            create_btn = page.locator("button", has_text="创建").first
            await create_btn.click()
            await asyncio.sleep(1)
            modal = await page.locator(".modal, [class*='modal'], form").first
            log("创建弹窗打开", await modal.is_visible())
        except Exception as e:
            log("创建弹窗", False, str(e)[:80])

        # === 4. 进入编辑器 ===
        print("\n=== 编辑器页面 ===")
        # 先找一个已存在的标书
        try:
            rows = page.locator("tr, .row, [class*='item']")
            if await rows.count() > 0:
                await rows.first.click()
                await asyncio.sleep(2)
                editor_content = await page.content()
                log("编辑器加载", len(editor_content) > 500)
                has_edit_area = await page.locator("[class*='editor'], [class*='content'], textarea, .ProseMirror").count()
                log("编辑器区域存在", has_edit_area > 0, f"找到{has_edit_area}个")
            else:
                log("编辑器加载", False, "无标书数据")
        except Exception as e:
            log("编辑器加载", False, str(e)[:80])

        # === 5. Git提交验证 ===
        print("\n=== Git验证 ===")
        try:
            r = subprocess.run(["git","-C","/home/zzy/.openclaw/workspace/workspace-bid",
                               "log","--oneline","-3"], capture_output=True, text=True, timeout=5)
            commits = r.stdout.strip().split("\n")
            for c in commits:
                print(f"   {c}")
            # 验证昨晚的提交
            log("昨晚提交存在", any("排序" in c or "正则" in c or "图表" in c for c in commits),
                commits[0] if commits else "")
        except Exception as e:
            log("Git验证", False, str(e))

        # === 6. 代码逻辑验证 ===
        print("\n=== 代码逻辑验证 ===")
        try:
            with open("/home/zzy/.openclaw/workspace/workspace-bid/ai-bid-frontend/src/views/bid/Editor.vue","r") as f:
                editor_code = f.read()
            log("正则使用[\\s\\S]*?", "[\s\S]*?" in editor_code)
            log("图表URL解析逻辑", "chart:" in editor_code)
            log("表格HTML转换逻辑", "<table" in editor_code.lower() or "table>" in editor_code.lower())
        except Exception as e:
            log("代码验证", False, str(e))

        await browser.close()

        # 汇总
        print("\n" + "="*50)
        passed = sum(RESULTS)
        print(f"验证结果: {passed}/{len(RESULTS)} 通过")
        return passed == len(RESULTS)

if __name__ == "__main__":
    ok = asyncio.run(main())
    exit(0 if ok else 1)