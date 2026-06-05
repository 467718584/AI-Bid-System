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

---

## 📊 开发进度

> ⚠️ 最后更新：2026-06-05

| Phase | 内容 | 进度 | 状态 |
|-------|------|------|------|
| Phase 1 | 架构设计 + 基础设施 + 核心CRUD | 100% | ✅ 完成 |
| Phase 2 | AI能力层 + 技术标核心 | 100% | ✅ 完成 |
| Phase 3 | 前后端联调 + 功能修复 | 100% | ✅ 完成 |
| Phase 4 | 完整功能验证 + 性能优化 | 80% | 🔄 进行中 |

**当前重点：Phase 4 测试验证接近完成 (用户旅程 11/11通过 ✅)**

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────────┐
│                    前端层 (Vue3:3000)                     │
├──────────────────────────────────────────────────────────┤
│                    网关层 (Gateway:8090)                  │
│         路由转发 + 负载均衡 + 安全过滤                    │
├────────────┬────────────┬────────────┬───────────────────┤
│ 用户服务    │ 项目服务    │ 物料服务    │ 文档服务          │
│ ai-bid-user│ ai-bid-   │ ai-bid-    │ ai-bid-document   │
│ :8081      │ project    │ material   │ :8084             │
│            │ :8082      │ :8083      │                   │
├────────────┴────────────┴────────────┴───────────────────┤
│                    标书服务 (ai-bid-bid:8085)             │
├──────────────────────────┬──────────────────────────────┤
│      AI服务 (ai-bid-ai)  │   知识库服务 (ai-bid-knowledge)│
│           :8087          │              :8086            │
│   - 标书生成/改写         │   - 向量检索                  │
│   - RAG增强              │   - 混合检索                   │
│   - 模板管理              │   - 文档解析                   │
├──────────────────────────┴──────────────────────────────┤
│                    数据层                                 │
│     PostgreSQL:5432  │  Redis:6379  │  ChromaDB         │
└─────────────────────────────────────────────────────────┘
```

## 📂 微服务模块

| 模块 | 类型 | 端口 | 健康状态 | 说明 |
|------|------|------|----------|------|
| `ai-bid-gateway` | Java | 8090 | ✅ | API网关，统一路由入口 |
| `ai-bid-user` | Java | 8081 | ✅ | 用户管理、权限控制 |
| `ai-bid-project` | Java | 8082 | ✅ | 项目管理、工作流 |
| `ai-bid-material` | Java | 8083 | ✅ | 素材库、企业资料 |
| `ai-bid-document` | Java | 8084 | ✅ | 文档处理、版本管理 |
| `ai-bid-bid` | Java | 8085 | ✅ | 标书管理、投标流程 |
| `ai-bid-ai` | Python | 8087 | ✅ | AI能力（生成/RAG/改写）|
| `ai-bid-knowledge` | Python | 8086 | ✅ | 知识库、向量检索 |
| `ai-bid-frontend` | Vue3 | 3000 | ✅ | 前端界面 |

---

## ✨ 已实现功能

### Phase 1 - 基础设施 ✅
- [x] Spring Boot微服务架构（8个服务）
- [x] MyBatis数据访问层
- [x] PostgreSQL + pgvector向量数据库
- [x] Redis缓存层
- [x] Gateway统一路由（10条路由规则）
- [x] CORS跨域支持

### Phase 2 - AI能力层 ✅
- [x] 技术标目录智能生成（8章结构）
- [x] 技术标正文分章节生成
- [x] 全文生成流水线（5阶段）
- [x] 图文并茂功能（图片插入 + 图表生成）
- [x] 表格自动生成（5种表格类型 + 甘特图）
- [x] 向量嵌入真实对接（MiniMax embo01）
- [x] 混合检索（向量 + 关键词）
- [x] RAG增强检索
- [x] 标书改写（5种策略 + 6种风格）

### Phase 3 - 前后端联调 ✅
- [x] Vue3完整业务界面
- [x] Tiptap富文本编辑器
- [x] Word模板导出（5种预设模板）
- [x] MD格式兼容性修复（表格、图表）
- [x] Gateway路由修复（AI/知识库服务）
- [x] 前端API路径统一（/api/knowledge/**）
- [x] 完整功能测试（91%通过率）

### Phase 4 - 待启动 ⏳
- [ ] 完整用户旅程测试
- [ ] 性能优化
- [ ] Docker容器化部署
- [ ] 生产环境适配

---

## 📐 API接口总览

### Gateway路由 (端口8090)

所有请求通过Gateway统一入口，路径规则：
- Java服务：`/api/{service}/**` → StripPrefix=1 → `http://localhost:{port}/{service}/**`
- Python服务：`/api/ai/**` → 保持路径 → `http://localhost:8087/api/ai/**`
- Python服务：`/api/knowledge/**` → 保持路径 → `http://localhost:8086/api/knowledge/**`

### AI服务 (ai-bid-ai:8087)

| 方法 | 端点 | 说明 |
|-----|------|-----|
| GET | `/api/ai/health` | 服务健康检查 |
| GET | `/api/ai/export/templates` | 获取模板列表 |
| POST | `/api/ai/generate/outline` | 技术标目录生成 |
| POST | `/api/ai/generate/content` | 技术标正文生成 |
| POST | `/api/ai/pipeline/generate` | 全文生成流水线 |
| POST | `/api/ai/rewrite` | 标书改写 |
| POST | `/api/ai/table/generate` | 表格生成 |
| POST | `/api/ai/table/generate-word` | Word表格生成 |
| POST | `/api/ai/export/html-to-word` | HTML转Word导出 |

### 知识库服务 (ai-bid-knowledge:8086)

| 方法 | 端点 | 说明 |
|-----|------|-----|
| GET | `/api/knowledge/health` | 服务健康检查 |
| POST | `/api/knowledge/bases` | 创建知识库 |
| GET | `/api/knowledge/bases/{kb_id}` | 获取知识库详情 |
| POST | `/api/knowledge/bases/{kb_id}/documents` | 上传文档 |
| POST | `/api/knowledge/bases/{kb_id}/vector-retrieve` | 向量检索 |
| POST | `/api/knowledge/bases/{kb_id}/hybrid-search` | 混合检索 |
| POST | `/api/knowledge/bases/{kb_id}/rag-retrieve` | RAG检索 |

### Java服务API (通过Gateway访问)

**用户服务** `GET /api/user/**`
- `GET /api/user/list` - 用户列表
- `GET /api/user/{id}` - 用户详情

**项目服务** `GET /api/project/**`
- `GET /api/project/list` - 项目列表
- `GET /api/project/{id}` - 项目详情

**物料服务** `GET /api/material/**`
- `GET /api/material/list` - 素材列表
- `GET /api/material/{id}` - 素材详情

**文档服务** `GET /api/document/**`
- `GET /api/document/list` - 文档列表
- `GET /api/document/{id}` - 文档详情

**标书服务** `GET /api/bid/**`
- `GET /api/bid/list` - 标书列表
- `GET /api/bid/{id}` - 标书详情

---

## 🚀 快速开始

### 环境要求
- JDK 17+
- Maven 3.8+
- Node.js 18+
- Python 3.11+
- PostgreSQL 16+
- Redis 7+

### 1. 克隆仓库
```bash
git clone https://github.com/467718584/AI-Bid-System.git
cd AI-Bid-System
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入配置（MINIMAX_API_KEY等）
```

### 3. 启动基础设施
```bash
docker-compose up -d postgres redis
```

### 4. 初始化数据库
```bash
# PostgreSQL中创建数据库
createdb -U postgres ai_bid

# 运行初始化脚本
psql -U postgres -d ai_bid -f init-scripts/schema.sql
```

### 5. 启动后端服务
```bash
# 编译所有Java服务
cd ai-bid-gateway && mvn clean compile -DskipTests
cd ai-bid-user && mvn clean compile -DskipTests
cd ai-bid-project && mvn clean compile -DskipTests
cd ai-bid-material && mvn clean compile -DskipTests
cd ai-bid-document && mvn clean compile -DskipTests
cd ai-bid-bid && mvn clean compile -DskipTests

# 启动Java服务（各自分开终端或后台）
cd ai-bid-gateway && mvn spring-boot:run &
cd ai-bid-user && mvn spring-boot:run &
cd ai-bid-project && mvn spring-boot:run &
cd ai-bid-material && mvn spring-boot:run &
cd ai-bid-document && mvn spring-boot:run &
cd ai-bid-bid && mvn spring-boot:run &

# 启动Python服务
cd ai-bid-ai && PYTHONPATH=./src/main/python python3 -m com.aidbid.ai.main &
cd ai-bid-knowledge && PYTHONPATH=./src/main/python python3 -m com.aidbid.knowledge.main &
```

### 6. 启动前端
```bash
cd ai-bid-frontend
npm install
npm run dev
```

访问 `http://localhost:3000`

---

## 🧪 系统测试

### 运行完整测试
```bash
python3 docs/system_test.py
```

### 预期输出
```
======================================================================
AI智能投标系统 - 完整功能测试报告
======================================================================
* 服务运行: 9/9
* API测试: 11/12 通过
* 内存占用: ~1600MB
======================================================================
```

---

## 📂 项目结构

```
AI-Bid-System/
├── ai-bid-gateway/           # API网关 (Java Spring Cloud Gateway)
│   └── src/main/resources/
│       └── application.yml    # 路由配置
├── ai-bid-user/              # 用户服务
├── ai-bid-project/          # 项目服务
├── ai-bid-material/          # 物料服务
├── ai-bid-document/          # 文档服务
├── ai-bid-bid/              # 标书服务
├── ai-bid-ai/               # AI能力服务 (Python FastAPI)
│   └── src/main/python/
│       └── com/aidbid/ai/
│           ├── main.py       # 服务入口
│           ├── services/     # AI服务
│           ├── pipeline/      # 生成流水线
│           └── skill/        # 技能编排
├── ai-bid-knowledge/         # 知识库服务 (Python FastAPI)
│   └── src/main/python/
│       └── com/aidbid/knowledge/
│           ├── main.py       # 服务入口
│           ├── embedding_service.py
│           └── rag_service.py
├── ai-bid-frontend/          # Vue3前端
│   └── src/
│       ├── views/            # 业务页面
│       ├── components/        # 公共组件
│       ├── api/              # API封装
│       └── stores/           # Pinia状态
├── templates/                # Word模板
│   ├── bid_templates.py      # 5种预设模板
│   └── styled_exporter.py    # 样式导出器
├── docs/                     # 项目文档
│   ├── system_test.py        # 系统测试脚本
│   ├── fix_all_md_tables.py  # MD表格修复
│   └── README.md              # 项目文档
├── init-scripts/             # 数据库初始化
├── scripts/                  # 运维脚本
├── knowledge/                # 知识库文件
├── patterns/                 # 模式库
└── docker-compose.yml        # 容器编排
```

---

## 🔧 最近修复记录 (2026-06-05)

| 日期 | 修复内容 |
|------|----------|
| 06-05 | Gateway路由配置修复：AI服务和知识库服务不再StripPrefix，保持/api/ai/**完整路径 |
| 06-05 | 前端API路径统一：知识库API从/knowledge/**改为/api/knowledge/** |
| 06-05 | MD表格解析修复：正则表达式优化，支持复杂表格格式 |
| 06-05 | Word模板导出API：/api/ai/export/templates 返回正确模板列表 |
| 06-04 | 图表显示优化：支持更多图片URL模式 |
| 06-04 | 内容排序算法优化：支持中文内容的正确排序 |

### Git提交历史 (最近5次)
```
3be7a99 fix: 修复Gateway路由配置和前端API路径
e7513a1 fix: 重写MD表格解析逻辑，使用简单直接的替换方式
0e2edaf feat: Word模板导出API，支持HTML表格转换
41ebcbb fix: MD表格分隔行正则漏了|字符
03bd0d7 fix: 优化MD表格正则，消除前瞻断言bug
```

---

## 📌 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Element Plus + Pinia + Vue Router + Tiptap |
| 后端Java | Spring Boot 3.2 + MyBatis |
| 后端Python | FastAPI + LangChain + ChromaDB |
| 数据库 | PostgreSQL 16 + pgvector |
| 缓存 | Redis 7 |
| LLM | Minimax API (MiniMax-M2) |
| 向量模型 | MiniMax embo01 |
| API网关 | Spring Cloud Gateway |
| 构建工具 | Maven + npm |

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

---

*最后更新：2026-06-05 by bid-admin*
