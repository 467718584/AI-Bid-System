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

## EdgeHub 远控配置 (2026-06-23)

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

### 常用命令
```bash
# 登录EdgeHub
EDGEHUB_KEY="al_fWbIEQS4rySxY972aeIqVqCFsMloInrZ"

# 在项目10执行Shell命令
curl -X POST http://1.13.247.173/api/v1/agents/me/projects/10/commands \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la","timeout":30000}'

# 直接对WEI-PC下发命令
curl -X POST http://1.13.247.173/api/v1/devices/82785476b5753520/commands \
  -H "X-API-Key: $EDGEHUB_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command":"hostname","timeout_ms":5000}'
```

### 协议文档
- `docs/EDGEHUB_PROTOCOL.md` - EdgeHub v3.2 API完整说明
