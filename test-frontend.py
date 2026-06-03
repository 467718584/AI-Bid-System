#!/usr/bin/env python3
"""前端页面Playwright测试"""

from playwright.sync_api import sync_playwright

def test_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        errors = []
        
        def handle_console(msg):
            if msg.type == 'error':
                errors.append(f"Console Error: {msg.text}")
        
        def handle_page_error(err):
            errors.append(f"Page Error: {err}")
        
        page.on('console', handle_console)
        page.on('pageerror', handle_page_error)
        
        base_url = 'http://localhost:3000'
        pages = [
            ('/', '首页'),
            ('/bid', '标书管理'),
            ('/workflow', '工作流'),
        ]
        
        print('=== 前端页面测试开始 ===\n')
        
        for path, name in pages:
            print(f'\n--- 测试: {name} ({path}) ---')
            try:
                response = page.goto(f'{base_url}{path}', wait_until='networkidle', timeout=15000)
                print(f'✅ 页面加载成功 (HTTP {response.status})')
                
                page.wait_for_timeout(2000)
                
                title = page.title()
                print(f'   标题: {title}')
                
                # 检查页面内容
                content = page.content()
                if 'Error' in content or 'error' in content:
                    print(f'   ⚠️ 页面包含error关键字')
                
            except Exception as e:
                print(f'❌ 加载失败: {e}')
        
        print('\n\n=== 错误汇总 ===')
        if not errors:
            print('✅ 没有控制台错误')
        else:
            for e in errors:
                print(f'❌ {e}')
        
        browser.close()
        print('\n=== 测试完成 ===')

if __name__ == '__main__':
    test_pages()