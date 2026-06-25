# SOUL.md - bid-admin

_EO-Enhanced Agent - Auto-configured by EO Plugin_

---

## 🚀 EO-Enhanced 能力

| 工具 | 功能 |
|------|------|
| `eo_collab` | 多专家协作 |
| `eo_plan` | 项目规划 |
| `eo_architect` | 架构设计 |
| `eo_verify` | 检查点验证 |
| `eo_list_experts` | 专家列表(141位) |

---

## 📚 历史学习积累

### ✅ 成功模式

- 晨会/日报模式：cron每日触发Dream Module自检
- 主动记忆模式：每次会话后记录memory/YYYY-MM-DD.md

### ⚠️ 经验教训

- **飞书文件下载**：App不是资源发送者，无法下载用户上传的文件
  - 解决：让用户提供飞书云文档链接，而非直接文件

---

## 📊 项目进度

### AI智能投标系统

| Phase | 状态 | 说明 |
|-------|------|------|
| Phase 1 | ✅ 完成 | 架构设计 + 8服务 + 数据库 |
| Phase 2 | ✅ 完成 | AI生成 + RAG + Pipeline |
| Phase 3 | 🔄 进行中 | 前后端联调 |

**核心成果**: 知识库(`knowledge/PROJECT_KNOWLEDGE.md`) + 模式库(`patterns/SOLUTION_PATTERNS.md`)

---

## 🏗️ 系统架构

```
Gateway(8090) 
├── ai-bid-user(8081)
├── ai-bid-project(8082)
├── ai-bid-material(8083)
├── ai-bid-document(8084)
├── ai-bid-bid(8085)
├── ai-bid-knowledge(8086)
├── ai-bid-ai(8087)
└── ai-bid-enterprise(8088)
```

---

## 🌐 EdgeHub 远控集成 (v3.2)

### 智能体注册信息
| 项目 | 值 |
|------|-----|
| Agent ID | bid-agent |
| Agent Name | BID智能投标助手 |
| Agent Type | openclaw |
| API Key | `al_fWbIEQS4rySxY972aeIqVqCFsMloInrZ` |
| 注册时间 | 2026-06-23 |

### 项目信息
| 项目 | 值 |
|------|-----|
| Project ID | 10 |
| Project Name | 智能投标平台 |
| 关联设备 | WEI-PC (82785476b5753520) |
| Status | active |

### EdgeHub API
| 端点 | 说明 |
|------|------|
| POST /api/v1/agents/register | 智能体注册 |
| POST /api/v1/agents/me/login | 登录验证 |
| POST /api/v1/agents/me/projects | 创建项目 |
| GET /api/v1/agents/me/projects/{id}/tasks | 获取任务 |
| POST /api/v1/agents/me/projects/{id}/commands | ✅ 执行命令（推荐-记项目日志） |
| GET /api/v1/commands/{command_id} | ✅ 查询命令结果（Agent Key可用） |
| POST /api/v1/devices/{device_id}/commands | ⚠️ 设备命令（不记项目日志） |

### ⚠️ 两种命令端点的区别
- **项目端点** `/agents/me/projects/:id/commands` → 自动记录到项目日志 ✅
- **设备端点** `/devices/:id/commands` → 不记录，仅紧急运维 ⚠️

### 快速命令
```bash
EDGEHUB_KEY="al_fWbIEQS4rySxY972aeIqVqCFsMloInrZ"
PROJECT_ID=10

# 1. 在项目10中执行命令（推荐）
curl -X POST "http://1.13.247.173/api/v1/agents/me/projects/${PROJECT_ID}/commands" \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command":"hostname","timeout_ms":30000}'

# 2. 查询命令执行结果
curl "http://1.13.247.173/api/v1/commands/cmd_xxx" \
  -H "X-API-Key: $EDGEHUB_KEY"
# 响应: {status, stdout, stderr, exit_code}

# 3. 设备端点（不记录到项目日志）
curl -X POST "http://1.13.247.173/api/v1/devices/82785476b5753520/commands" \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command":"hostname","timeout_ms":5000}'
```

### 命令执行流程
1. 投递命令 → 返回 `command_id` + `status: pending`
2. Agent接收 → 目标设备需运行 EdgeHub Agent polling
3. 执行并回调 → Agent 执行后回调结果

### ⚠️ 当前限制
- WEI-PC 无 EdgeHub Agent 进程，命令 pending 无法执行

---

## 🔧 已知问题

1. SOUL.md过大(75KB)导致bootstrap截断48%
2. 飞书消息限制4096字符
3. Cron重复触发问题未修复

---

*最后更新: 2026-06-25*
*更新内容: EdgeHub API用法纠错 - 增加GET /commands/:id查询、明确项目端点vs设备端点区别*