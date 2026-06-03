const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(`Console Error: ${msg.text()}`);
    }
  });
  page.on('pageerror', err => {
    errors.push(`Page Error: ${err.message}`);
  });
  
  const baseUrl = 'http://localhost:3000';
  const pages = [
    { path: '/', name: '首页' },
    { path: '/bid', name: '标书管理' },
    { path: '/workflow', name: '工作流' },
  ];
  
  console.log('=== 前端页面测试开始 ===\n');
  
  for (const p of pages) {
    console.log(`\n--- 测试: ${p.name} (${p.path}) ---`);
    try {
      await page.goto(`${baseUrl}${p.path}`, { waitUntil: 'networkidle', timeout: 15000 });
      console.log(`✅ 页面加载成功`);
      
      // 检查页面标题
      const title = await page.title();
      console.log(`   标题: ${title}`);
      
      // 等待一下让Vue渲染
      await page.waitForTimeout(2000);
      
      // 检查是否有错误
      const body = await page.textContent('body');
      if (body.includes('Error') || body.includes('error')) {
        console.log(`   ⚠️ 页面内容包含error`);
      }
      
    } catch (e) {
      console.log(`❌ 加载失败: ${e.message}`);
    }
  }
  
  console.log('\n\n=== 错误汇总 ===');
  if (errors.length === 0) {
    console.log('✅ 没有控制台错误');
  } else {
    errors.forEach(e => console.log(`❌ ${e}`));
  }
  
  await browser.close();
  console.log('\n=== 测试完成 ===');
})();
