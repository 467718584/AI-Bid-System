# AI智能投标系统 - 核心成果知识库

## 项目概述
- 项目名称：AI智能投标文件智能编制管理系统
- 开发时间：2026年5月26日启动
- 技术栈：Spring Boot 3.2 + Vue3 + FastAPI + PostgreSQL

## 核心架构

### 服务架构
```
Gateway(8090) 
├── ai-bid-user(8081) - 用户服务
├── ai-bid-project(8082) - 项目服务
├── ai-bid-material(8083) - 素材服务
├── ai-bid-document(8084) - 文档服务
├── ai-bid-bid(8085) - 标书服务
├── ai-bid-knowledge(8086) - 知识库服务
├── ai-bid-ai(8087) - AI服务
└── ai-bid-enterprise(8088) - 企业资料服务
```

### 前端架构
- Vue3 + Element Plus + Pinia
- 路由：/bid, /workflow, /material, /knowledge, /enterprise, /project

## 核心成果

### Phase 1 ✅ 完成
- 8个Java微服务 + 2个Python AI服务
- Gateway统一路由配置
- 数据库PostgreSQL + Redis
- 素材库、企业资料库CRUD
- 技术标目录生成

### Phase 2 ✅ 完成
- AI大纲生成(/api/ai/bid/outline)
- AI章节内容生成(/api/ai/bid/content)  
- RAG知识检索服务
- Pipeline流水线框架
- 文档解析与导出

### Phase 3 🔄 进行中
- 前后端联调
- 标书编辑/预览功能
- 工作流可视化

## 问题解决记录

### 已知问题模式
1. Gateway路由StripPrefix需要根据后端Controller实际路径调整
2. MyBatis-Plus 3.5.x与Spring Boot 3.x兼容性问题 → 替换为mybatis-spring-boot-starter
3. 前端el-tree组件data格式与API返回不匹配 → 需要computed转换
4. 飞书消息限制4096字符
5. SOUL.md过大导致bootstrap截断48%

### 修复经验
- AI内容包含<think>标签 → 在main.py中添加正则清理
- BidController create返回格式 → 返回完整list而非单个对象
- 工作流创建后ID获取 → 从response.list中查找

## API端点清单

### 标书管理
- GET /api/bid/list - 标书列表
- GET /api/bid/{id} - 标书详情
- POST /api/bid - 创建标书
- PUT /api/bid/{id} - 更新标书

### AI生成
- POST /api/ai/bid/outline - 生成目录
- POST /api/ai/bid/content - 生成章节内容

### 知识库
- GET /api/knowledge/categories - 分类列表
- GET /api/knowledge/search - 搜索

## 下一步计划
1. 完善标书编辑/预览功能
2. 实现Word导出
3. 实现RAG完整检索
4. 实现资信标编制
5. 实现标书改写功能