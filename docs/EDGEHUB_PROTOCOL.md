# EdgeHub 智能体完整接入说明书 v3.2

## 基本信息
- 更新时间：2026-06-16
- 提供方：极速科技 · EdgeHub 边缘设备管理系统
- 基础URL: http://1.13.247.173

## 认证方式

### 1. OpenClaw API Key 登录
```bash
curl -X POST http://1.13.247.173/api/v1/agents/me/login \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"test","api_key":"al_xxx..."}'
```

### 2. Agent Key（X-API-Key Header）
用于智能体操作已绑定的设备

### 3. 管理员 Key（edgehub_secret_key）
用于设备命令执行等高权限操作

## API 端点

### 1. 登录验证
```
POST /api/v1/agents/me/login
```

### 2. 创建项目
```
POST /api/v1/agents/me/projects
Headers: X-API-Key: al_xxx...
Body: {"project_name":"test","device_id":"82b2731d58533598"}
```

### 3. 获取任务列表
```
GET /api/v1/agents/me/projects/{project_id}/tasks
Headers: X-API-Key: al_xxx...
```

### 4. 添加任务
```
POST /api/v1/agents/me/projects/{project_id}/tasks
Headers: X-API-Key: al_xxx...
Body: {"title":"测试任务","priority":5}
```

### 5. 执行设备命令
```
POST /api/v1/devices/{device_id}/commands
Headers: X-API-Key: edgehub_secret_key
Body: {"command":"echo OK","timeout_ms":10000}
```

### 6. 添加日志
```
POST /api/v1/agents/me/projects/{project_id}/logs
Headers: X-API-Key: al_xxx...
Body: {"action_type":"command","command":"echo test","notes":"测试日志"}
```

## v3.2 新增功能

### Agent Key 权限测试
假设 ivp-agent-001 绑定了 WEI-PC (82785476b5753520)

下发命令：
```bash
curl -X POST http://1.13.247.173/api/v1/devices/82785476b5753520/commands \
  -H "X-API-Key: eh_key_ivp_agent_001_6747f7824d09c6d091128b360fa43831" \
  -H "Content-Type: application/json" \
  -d '{"command":"hostname","timeout_ms":5000}'
```

响应：
```json
{"success":true,"data":{"command_id":"cmd_xxx","status":"delivered_via_ws"}}
```

### 权限校验
访问未绑定设备会被拒绝：
```json
{"success":false,"error":{"code":"DEVICE_NOT_BINDED","message":"该设备未绑定到此智能体"}}
```

## 错误码
- DEVICE_NOT_BINDED: 该设备未绑定到此智能体
