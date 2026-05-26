# AI智能投标文件智能编制管理系统

## 📖 项目概述

| 项目 | 说明 |
|------|------|
| 项目名称 | AI智能投标文件智能编制管理系统 |
| 项目代号 | `ai-bid-system` |
| 项目类型 | 企业级SaaS应用 |
| 核心功能 | 智能标书编制、投标管理、AI赋能 |
| 政策背景 | 响应国家"人工智能+"战略（发改法规〔2026〕195号）|

## 🎯 核心价值

```
┌─────────────────────────────────────────────────────────┐
│  痛点                    →     解决方案                 │
├─────────────────────────────────────────────────────────┤
│  标书编制效率低           →     AI智能生成，降本增效     │
│  文件质量不稳定           →     标准化模板+合规检查      │
│  知识资产散落             →     企业级知识库沉淀复用      │
│  合规风险难控             →     自动检测+预警            │
└─────────────────────────────────────────────────────────┘
```

## 📊 开发进度

> ⚠️ 最后更新：2026-05-26

| Phase | 内容 | 进度 | 状态 |
|-------|------|------|------|
| Phase 1 | 架构设计 + 基础设施 + 核心CRUD | 100% | ✅ 完成 |
| Phase 2 | AI能力层 + 技术标核心 | 100% | ✅ 完成 |
| Phase 3 | 资信标 + 标书改写 | 100% | ✅ 完成 |
| Phase 4 | 工作流 + 技能编排 + 模型管理 | 100% | ✅ 完成 |
| Phase 5 | 联调测试 + 性能优化 + 上线 | 0% | ⏳ 待开始 |

**总体进度：~65%**

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────────┐
│                    客户端层 (Vue3)                        │
├──────────────────────────────────────────────────────────┤
│                    应用层 (Spring Boot)                   │
│  ┌──────────┬──────────┬──────────┬──────────┬─────────┐ │
│  │ 项目管理 │ 技术标编 │ 资信标编 │ 素材库   │ 后台管理│ │
│  └──────────┴──────────┴──────────┴──────────┴─────────┘ │
├──────────────────────────────────────────────────────────┤
│                    支撑层 (PaaS)                          │
│  ┌──────────┬──────────┬──────────┬──────────┬─────────┐ │
│  │ 用户权限 │ 工作流   │ 技能编排 │ 知识库   │ API管理│ │
│  └──────────┴──────────┴──────────┴──────────┴─────────┘ │
├──────────────────────────────────────────────────────────┤
│                    AI能力中台 (LangChain)                  │
│  ┌──────────┬──────────┬──────────┬───────────────────┐ │
│  │ LLM网关   │ RAG引擎  │ 文档解析 │ Prompt管理        │ │
│  └──────────┴──────────┴──────────┴───────────────────┘ │
├──────────────────────────────────────────────────────────┤
│                    基础设施层                             │
│  PostgreSQL(+pgvector) │ Redis │ MinIO │ Docker           │
└──────────────────────────────────────────────────────────┘
```

## 📂 微服务模块

| 模块 | 类型 | 端口 | 说明 |
|------|------|------|------|
| `ai-bid-gateway` | Java | 8080 | API网关 + 模型管理 |
| `ai-bid-project` | Java | 8081 | 项目管理 + 工作流 + 技能编排 |
| `ai-bid-material` | Java | 8082 | 素材库 + 企业资料 |
| `ai-bid-user` | Java | 8083 | 用户管理 |
| `ai-bid-document` | Java | 8084 | 文档处理 |
| `ai-bid-ai` | Python | 8087 | AI能力（标书生成/RAG/改写）|
| `ai-bid-knowledge` | Python | 8086 | 知识库 + 向量检索 |
| `ai-bid-frontend` | Vue3 | 3000 | 前端界面 |

## ✨ 已实现功能

### Phase 1 - 基础设施 ✅
- [x] Spring Boot微服务架构
- [x] MyBatis-Plus数据访问层
- [x] PostgreSQL + pgvector向量数据库
- [x] Redis缓存层
- [x] Docker Compose容器化部署

### Phase 2 - AI能力层 ✅
- [x] 全文生成流水线（5阶段：解析→目录→正文→导出）
- [x] 图文并茂功能（图片插入 + 图表生成）
- [x] 表格自动生成（5种表格类型 + 甘特图）
- [x] 向量嵌入真实对接（MiniMax embo01 + ChromaDB）
- [x] 混合检索（向量 + 关键词）
- [x] RAG增强检索

### Phase 3 - 资信标 + 改写 ✅
- [x] 资信标智能编制（自动填充 + 资质匹配）
- [x] 企业信息管理
- [x] 业绩案例库
- [x] 标书改写（5种策略 + 6种风格）
- [x] 多版本改写
- [x] 模板管理系统（3个内置模板）
- [x] 版本管理与回滚

### Phase 4 - 工作流 + 技能编排 ✅
- [x] Camunda工作流引擎
- [x] 2个预设投标流程（BPMN）
- [x] 技能编排引擎（5个预置技能）
- [x] 模型注册与切换
- [x] 智能路由 + 熔断器 + 限流
- [x] 监控面板
- [x] Vue3完整业务界面

---

## 🕐 开发阶段

| Phase | 内容 | 工期 | 状态 |
|-------|------|------|------|
| Phase 1 | 架构设计 + 基础设施 + 核心CRUD | 6周 | ✅ 完成 |
| Phase 2 | AI能力层 + 技术标核心 | 8周 | ✅ 完成 |
| Phase 3 | 资信标 + 标书改写 | 6周 | ✅ 完成 |
| Phase 4 | 工作流 + 技能编排 + 模型管理 | 4周 | ✅ 完成 |
| Phase 5 | 联调测试 + 性能优化 + 上线 | 4周 | ⏳ 待开始 |

**总工期：约 24-28周**

---

## 🚀 快速开始

### 环境要求
- Docker & Docker Compose
- JDK 17+
- Node.js 18+
- Python 3.11+

### 1. 克隆仓库
```bash
git clone https://github.com/467718584/AI-Bid-System.git
cd AI-Bid-System
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入你的配置（尤其是 MINIMAX_API_KEY）
```

### 3. 启动基础设施
```bash
docker-compose up -d postgres redis minio chroma
```

### 4. 初始化数据库
```bash
mysql -h localhost -u bid_user -p bid_db < init-scripts/schema.sql
```

### 5. 启动后端服务
```bash
# Java微服务
./mvnw clean package -DskipTests
java -jar ai-bid-gateway/target/ai-bid-gateway.jar &

# Python AI服务
cd ai-bid-ai && pip install -r requirements.txt && uvicorn main:app --port 8087 &
cd ai-bid-knowledge && pip install -r requirements.txt && uvicorn main:app --port 8086 &
```

### 6. 启动前端
```bash
cd ai-bid-frontend
npm install
npm run dev
```

访问 `http://localhost:3000`

---

## 📐 API接口总览

### AI服务 (ai-bid-ai:8087)
| 方法 | 端点 | 说明 |
|-----|------|-----|
| POST | `/api/ai/generate/outline` | 技术标目录生成 |
| POST | `/api/ai/generate/content` | 技术标正文生成 |
| POST | `/api/ai/pipeline/generate` | 全文生成流水线 |
| POST | `/api/ai/rewrite` | 标书改写 |
| POST | `/api/ai/table/generate` | 表格生成 |
| GET | `/api/ai/skills` | 技能列表 |
| POST | `/api/ai/skills/pipeline` | 技能流水线执行 |

### 知识库服务 (ai-bid-knowledge:8086)
| 方法 | 端点 | 说明 |
|-----|------|-----|
| POST | `/api/knowledge/bases` | 创建知识库 |
| POST | `/api/knowledge/bases/{id}/vector-retrieve` | 向量检索 |
| POST | `/api/knowledge/bases/{id}/hybrid-search` | 混合检索 |
| POST | `/api/knowledge/bases/{id}/rag-generate` | RAG生成 |

### 工作流服务 (ai-bid-project:8081)
| 方法 | 端点 | 说明 |
|-----|------|-----|
| POST | `/api/project/workflow/deploy` | 部署流程 |
| POST | `/api/project/workflow/start/{processKey}` | 启动流程 |
| GET | `/api/project/workflow/tasks` | 待办任务 |

### 模型管理 (ai-bid-gateway:8080)
| 方法 | 端点 | 说明 |
|-----|------|-----|
| GET | `/api/gateway/models` | 模型列表 |
| POST | `/api/gateway/models` | 注册模型 |
| POST | `/api/gateway/models/switch` | 切换模型 |
| GET | `/api/gateway/models/dashboard` | 监控面板 |

---

## 📂 项目结构

```
ai-bid-system/
├── ai-bid-gateway/        # API网关 + 模型管理
├── ai-bid-project/        # 项目管理 + 工作流 + 技能
├── ai-bid-material/       # 素材库 + 企业资料
├── ai-bid-user/           # 用户管理
├── ai-bid-document/       # 文档处理
├── ai-bid-ai/             # AI能力服务（Python）
│   └── pipeline/          # 全文生成流水线
│   └── services/          # 图像/表格/改写服务
│   └── skill/             # 技能编排引擎
├── ai-bid-knowledge/      # 知识库服务（Python）
│   └── embedding_service.py
│   └── rag_service.py
│   └── chroma_client.py
├── ai-bid-frontend/       # Vue3前端
│   └── src/
│       ├── views/         # 业务页面
│       ├── components/     # 公共组件
│       ├── api/           # API封装
│       └── stores/        # Pinia状态
├── init-scripts/          # 数据库初始化脚本
├── docs/                  # 项目文档
└── docker-compose.yml     # 容器编排
```

---

## 📌 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Element Plus + Pinia + Vue Router |
| 后端Java | Spring Boot 3.2 + MyBatis-Plus |
| 后端Python | FastAPI + LangChain + ChromaDB |
| 数据库 | PostgreSQL 16 + pgvector |
| 缓存 | Redis 7 |
| 文件存储 | MinIO |
| LLM | 通义千问 / DeepSeek / Minimax |
| 向量模型 | MiniMax embo01 |
| 工作流 | Camunda BPM |
| 部署 | Docker + Docker Compose |

---

## 👥 团队信息

| 角色 | 名称 |
|------|------|
| 团队 | bid-team |
| 作者 | bid-admin |
| GitHub | https://github.com/467718584/AI-Bid-System |

---

## 📄 License

MIT License