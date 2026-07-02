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

---

## EdgeHub 文件传输系统 (v3.2)

### 核心能力
| 模式 | 方向 | 说明 |
|------|------|------|
| Push | Agent → 设备 | Multipart上传，EdgeHub自动分块推送到设备 |
| Pull | 设备 → Agent | 从设备拉取文件到EdgeHub服务器 |

### 凭证
```bash
EDGEHUB_KEY="al_fWbIEQS4rySxY972aeIqVqCFsMloInrZ"
DEVICE_ID="82785476b5753520"
PROJECT_ID=10
```

### 📤 Push模式 - 上传文件到设备

**端点**: `POST /api/v1/upload` (Multipart推荐)

```bash
# 上传文件到WEIPC
curl -X POST http://1.13.247.173/api/v1/upload \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -F "file=@/path/to/file.bin" \
  -F "device_id=$DEVICE_ID" \
  -F "remote_path=C:\\Users\\Public\\file.bin" \
  -F "project_id=$PROJECT_ID"

# 响应: {"success":true,"data":{"transfer_id":"tf_xxx","status":"pending"}}
```

**端点**: `POST /api/v1/transfers` (服务端文件推送)
```bash
# 适用于文件已在EdgeHub服务器的场景
curl -X POST http://1.13.247.173/api/v1/transfers \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id":"$DEVICE_ID",
    "direction":"push",
    "local_path":"/app/data/uploads/file.bin",
    "remote_path":"C:\\Users\\Public\\file.bin",
    "project_id":$PROJECT_ID
  }'
```

### 📥 Pull模式 - 从设备拉取文件

**端点**: `POST /api/v1/transfers/pull`

```bash
curl -X POST http://1.13.247.173/api/v1/transfers/pull \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id":"$DEVICE_ID",
    "remote_path":"C:\\Users\\Public\\file_on_device.txt",
    "project_id":$PROJECT_ID
  }'
```

### 📊 查询传输状态

```bash
# 查询单个传输
curl http://1.13.247.173/api/v1/transfers/:transferId \
  -H "X-API-Key: $EDGEHUB_KEY"

# 查询项目所有传输
curl "http://1.13.247.173/api/v1/transfers?project_id=$PROJECT_ID" \
  -H "X-API-Key: $EDGEHUB_KEY"

# 下载Pull完成的文件
curl -O http://1.13.247.173/api/v1/transfers/:transferId/download \
  -H "X-API-Key: $EDGEHUB_KEY"
```

### 🔄 断点续传

```bash
curl http://1.13.247.173/api/v1/transfers/:transferId/resume \
  -H "X-API-Key: $EDGEHUB_KEY"
```

### ❌ 取消传输

```bash
curl -X DELETE http://1.13.247.173/api/v1/transfers/:transferId \
  -H "X-API-Key: $EDGEHUB_KEY"
```

### 📡 WebSocket 进度推送

连接: `ws://1.13.247.173/ws?device_id=xxx&api_key=$EDGEHUB_KEY&type=device`

事件: `transfer_start`, `transfer_progress`, `transfer_complete`, `transfer_error`

### ⚠️ 已知限制
1. **Nginx 413** - Multipart受 `client_max_body_size` 限制，大文件用 `/transfers` 推送
2. **Windows路径** - Pull模式中Windows路径会作为文件名一部分
3. **设备离线** - 传输进入pending，设备上线后自动重试

### ✅ 测试结果 (2026-07-02)
- Push模式: ✅ 成功，文件已到达WEIPC
- 状态查询: ✅ 可查询进度
- 传输记录: ⚠️ 列表API返回空（可能已清理）
