# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## EdgeHub 远控配置 (2026-06-25 更新)

### 智能体凭证
| 项目 | 值 |
|------|-----|
| 平台 | http://1.13.247.173 |
| Agent ID | bid-agent |
| API Key | `al_fWbIEQS4rySxY972aeIqVqCFsMloInrZ` |

### 设备绑定
| 设备 | Device ID | 关联项目 |
|------|-----------|----------|
| WEI-PC | 82785476b5753520 | 智能投标平台 (ID:10) |

### ⚠️ 两种命令下发端点的区别

| 端点 | 路径 | 项目日志 | 推荐度 |
|------|------|---------|--------|
| ✅ 项目端点 | `/api/v1/agents/me/projects/:id/commands` | ✅ 自动记录 | **推荐** |
| ⚠️ 设备端点 | `/api/v1/devices/:id/commands` | ❌ 不记录 | 仅紧急运维 |

### 核心API

```bash
EDGEHUB_KEY="al_fWbIEQS4rySxY972aeIqVqCFsMloInrZ"
PROJECT_ID=10
DEVICE_ID=82785476b5753520

# 1. 投递命令到项目（推荐 - 自动记录到项目日志）
curl -X POST "http://1.13.247.173/api/v1/agents/me/projects/${PROJECT_ID}/commands" \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command":"echo test","timeout_ms":30000}'

# 2. 查询命令执行结果
curl "http://1.13.247.173/api/v1/commands/cmd_xxx" \
  -H "X-API-Key: $EDGEHUB_KEY"
# 响应: {status: "pending"|"completed", stdout, stderr, exit_code}

# 3. 设备端点（不记录到项目日志，仅紧急运维）
curl -X POST "http://1.13.247.173/api/v1/devices/${DEVICE_ID}/commands" \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command":"hostname","timeout_ms":5000}'
```

### 命令执行流程

1. **投递命令** → EdgeHub 返回 `command_id` + `status: pending`
2. **Agent接收** → WEI-PC 上需运行 EdgeHub Agent 客户端 polling 命令队列
3. **执行命令** → Agent 在设备上执行
4. **结果回调** → Agent 回调结果（需要 `edgehub_secret_key`，或通过 GET /commands/:id 查询）

### ⚠️ 当前限制
- WEI-PC 无 EdgeHub Agent 进程运行，命令 pending 无法执行
- 需要在 WEI-PC 上安装并启动 EdgeHub Agent 客户端

### 协议文档
- `docs/EDGEHUB_PROTOCOL.md` - EdgeHub v3.2 API完整说明
- http://1.13.247.173/edgehub-agent-manual.html - 官方接入手册
