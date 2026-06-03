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

## 🔧 已知问题

1. SOUL.md过大(75KB)导致bootstrap截断48%
2. 飞书消息限制4096字符
3. Cron重复触发问题未修复

---

*最后更新: 2026-05-29*