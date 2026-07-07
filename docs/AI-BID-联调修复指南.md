# AI-BID 系统联调修复指南

## 当前状态

### 根因
1. **数据库完全为空** - ai_bid 库没有任何表，所有 API 都是 500 错误
2. **后端缺少登录接口** - 前端调用 `/user/login`、`/user/info`、`/user/logout`，但 UserController 没有这些方法
3. **knowledge 服务 unhealthy** - Dockerfile 用 curl 做 health check 但镜像没装 curl

### 修复步骤

#### Step 1: 初始化数据库（执行 SQL）

在 WEI-PC 上打开 PowerShell 运行：

```powershell
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS sys_user (id BIGINT PRIMARY KEY, username VARCHAR(50) NOT NULL UNIQUE, password VARCHAR(128) NOT NULL, nickname VARCHAR(50), email VARCHAR(100), phone VARCHAR(20), avatar VARCHAR(255), gender INTEGER DEFAULT 0, dept_id BIGINT, status INTEGER DEFAULT 0, last_login_ip VARCHAR(50), last_login_time TIMESTAMP, remark VARCHAR(500), create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"

docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS sys_role (id BIGINT PRIMARY KEY, role_name VARCHAR(50) NOT NULL, role_code VARCHAR(50) NOT NULL UNIQUE, description VARCHAR(255), status INTEGER DEFAULT 0, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS sys_user_role (id BIGINT PRIMARY KEY, user_id BIGINT NOT NULL, role_id BIGINT NOT NULL, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS bid_project (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, code VARCHAR(50) UNIQUE, type VARCHAR(50), amount DECIMAL(15,2), tenderer VARCHAR(200), contact_person VARCHAR(100), contact_phone VARCHAR(20), deadline TIMESTAMP, status VARCHAR(20) DEFAULT 'DRAFT', description TEXT, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS bid_material (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, type VARCHAR(50), project_id BIGINT, file_path VARCHAR(500), file_size BIGINT, file_type VARCHAR(50), upload_user_id BIGINT, status VARCHAR(20) DEFAULT 'PENDING', remark VARCHAR(500), create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"

docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS bid_document (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, type VARCHAR(50), project_id BIGINT, material_id BIGINT, file_path VARCHAR(500), file_size BIGINT, content TEXT, parse_status VARCHAR(20) DEFAULT 'PENDING', analysis_result TEXT, status VARCHAR(20) DEFAULT 'ACTIVE', create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS bid_template (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, code VARCHAR(50) UNIQUE, category VARCHAR(50), content TEXT, file_path VARCHAR(500), is_default INTEGER DEFAULT 0, status INTEGER DEFAULT 0, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS ai_task (id BIGINT PRIMARY KEY, task_type VARCHAR(50) NOT NULL, target_type VARCHAR(50), target_id BIGINT, input_data TEXT, output_data TEXT, status VARCHAR(20) DEFAULT 'PENDING', error_message VARCHAR(500), start_time TIMESTAMP, end_time TIMESTAMP, cost_time BIGINT, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"

# 插入种子数据
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
INSERT INTO sys_user (id, username, password, nickname, email, status, create_time, update_time, deleted) VALUES (1, 'admin', 'admin', '管理员', 'admin@aibid.com', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0) ON CONFLICT (username) DO NOTHING;
INSERT INTO bid_project (id, name, code, type, amount, tenderer, status, description, create_time, update_time, deleted) VALUES (1, '智慧城市数据治理平台建设项目', 'BID-2024-001', '智慧城市', 5000000.00, '某市政府信息中心', 'IN_PROGRESS', '建设智慧城市数据治理平台', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0) ON CONFLICT (code) DO NOTHING;
INSERT INTO bid_template (id, name, code, category, content, is_default, status, create_time, deleted) VALUES (1, '智慧城市技术标模板', 'TECH-STANDARD', '技术标', '智慧城市技术标内容...', 1, 0, CURRENT_TIMESTAMP, 0) ON CONFLICT (code) DO NOTHING;
"
```

#### Step 2: 修复 knowledge healthcheck（修改 docker-compose.yml）

编辑 `C:\ai-bid\docker-compose.yml`，找到 ai-bid-knowledge 的 healthcheck 部分：

```yaml
healthcheck:
  test: ["CMD-SHELL", "python -c \"import urllib.request;urllib.request.urlopen('http://localhost:8086/health')\""]
  interval: 30s
  timeout: 10s
  retries: 3
```

然后重启：
```powershell
cd C:\ai-bid
docker-compose up -d --no-deps ai-bid-knowledge
```

#### Step 3: 修复后端登录接口

在 `ai-bid-user/src/main/java/com/aidbid/user/controller/UserController.java` 中添加：

```java
@PostMapping("/login")
public Result<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
    String username = loginRequest.get("username");
    String password = loginRequest.get("password");
    SysUser user = userService.getByUsername(username);
    if (user == null || !user.getPassword().equals(password)) {
        throw new BusinessException(ResultCode.USERNAME_OR_PASSWORD_ERROR);
    }
    Map<String, Object> tokenData = new HashMap<>();
    tokenData.put("token", "mock-token-" + user.getId());
    tokenData.put("userId", user.getId());
    tokenData.put("username", user.getUsername());
    return Result.ok(tokenData);
}

@GetMapping("/info")
public Result<SysUser> getUserInfo() {
    SysUser user = userService.getById(1L); // mock
    return Result.ok(user);
}

@PostMapping("/logout")
public Result<Void> logout() {
    return Result.ok();
}
```

在 `UserService.java` 中添加：
```java
public SysUser getByUsername(String username) {
    return userMapper.selectByUsername(username);
}
```

在 `UserMapper.java` 中添加：
```java
SysUser selectByUsername(String username);
```

然后重新构建部署：
```bash
docker build -t ai-bid-user ./ai-bid-user
docker stop ai-bid-user && docker rm ai-bid-user
docker run -d --name ai-bid-user -p 8081:8081 --network ai-bid-network ai-bid-user
```

## 预期结果

修复完成后：
- ✅ 登录 → 返回 token
- ✅ 获取用户信息 → 返回用户数据
- ✅ 项目列表 → 返回示例项目
- ✅ 素材 CRUD → 正常
- ✅ AI 生成目录 → 正常（需要 knowledge 服务 healthy）
