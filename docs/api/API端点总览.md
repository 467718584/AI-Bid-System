# API端点总览

| 项目 | 说明 |
|------|------|
| 项目名称 | AI智能投标文件智能编制管理系统 |
| 版本 | v1.0.0 |
| 更新日期 | 2026-05-26 |

---

## 目录

1. [认证接口](#1-认证接口)
2. [用户管理接口](#2-用户管理接口)
3. [项目管理接口](#3-项目管理接口)
4. [文档管理接口](#4-文档管理接口)
5. [素材库接口](#5-素材库接口)
6. [企业资料接口](#6-企业资料接口)
7. [知识库接口](#7-知识库接口)
8. [AI服务接口](#8-ai服务接口)
9. [网关接口](#9-网关接口)

---

## 1. 认证接口

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/auth/login | 用户登录 | ✅ |
| POST | /api/auth/refresh | 刷新Token | ✅ |
| POST | /api/auth/logout | 用户登出 | ✅ |

**服务地址：** `http://localhost:8080` (Gateway)

---

## 2. 用户管理接口

### 2.1 用户CRUD

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/users | 创建用户 | ✅ |
| GET | /api/users | 查询用户列表 | ✅ |
| GET | /api/users/{id} | 查询用户详情 | ✅ |
| PUT | /api/users/{id} | 更新用户 | ✅ |
| DELETE | /api/users/{id} | 删除用户 | ✅ |
| PUT | /api/users/{id}/password | 修改密码 | ✅ |
| PUT | /api/users/{id}/status | 修改状态 | ✅ |
| POST | /api/users/{id}/roles | 分配角色 | ✅ |

### 2.2 角色管理

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/roles | 创建角色 | ✅ |
| GET | /api/roles | 查询角色列表 | ✅ |
| GET | /api/roles/{id} | 查询角色详情 | ✅ |
| PUT | /api/roles/{id} | 更新角色 | ✅ |
| DELETE | /api/roles/{id} | 删除角色 | ✅ |
| GET | /api/roles/{id}/permissions | 获取角色权限 | ✅ |
| PUT | /api/roles/{id}/permissions | 分配权限 | ✅ |

**服务地址：** `http://localhost:8081` (user-service)

---

## 3. 项目管理接口

### 3.1 项目CRUD

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/projects | 创建项目 | ✅ |
| GET | /api/projects | 查询项目列表 | ✅ |
| GET | /api/projects/{id} | 查询项目详情 | ✅ |
| PUT | /api/projects/{id} | 更新项目 | ✅ |
| DELETE | /api/projects/{id} | 删除项目 | ✅ |
| GET | /api/projects/{id}/documents | 项目文档列表 | ✅ |
| GET | /api/projects/{id}/materials | 项目素材列表 | ✅ |

### 3.2 项目状态流转

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| PUT | /api/projects/{id}/status | 更新项目状态 | ✅ |
| POST | /api/projects/{id}/submit | 提交项目 | ✅ |
| POST | /api/projects/{id}/archive | 归档项目 | ✅ |

**服务地址：** `http://localhost:8082` (project-service)

---

## 4. 文档管理接口

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/documents | 创建文档 | ✅ |
| GET | /api/documents/{id} | 获取文档详情 | ✅ |
| PUT | /api/documents/{id} | 更新文档 | ✅ |
| DELETE | /api/documents/{id} | 删除文档 | ✅ |
| GET | /api/documents/{id}/versions | 获取版本列表 | ✅ |
| GET | /api/documents/versions/{versionId} | 获取指定版本 | ✅ |
| PUT | /api/documents/{id}/content | 更新文档内容 | ✅ |
| GET | /api/documents/{id}/content | 获取文档内容 | ✅ |
| POST | /api/documents/{id}/export | 导出文档 | ✅ |
| POST | /api/documents/{id}/versions | 创建新版本 | ✅ |

**服务地址：** `http://localhost:8084` (document-service)

---

## 5. 素材库接口

### 5.1 素材分类

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/materials/categories | 创建分类 | ✅ |
| GET | /api/materials/categories | 获取分类树 | ✅ |
| PUT | /api/materials/categories/{id} | 更新分类 | ✅ |
| DELETE | /api/materials/categories/{id} | 删除分类 | ✅ |

### 5.2 素材管理

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/materials | 上传素材 | ✅ |
| GET | /api/materials | 查询素材列表 | ✅ |
| GET | /api/materials/{id} | 获取素材详情 | ✅ |
| PUT | /api/materials/{id} | 更新素材 | ✅ |
| DELETE | /api/materials/{id} | 删除素材 | ✅ |
| GET | /api/materials/search | 搜索素材 | ✅ |

### 5.3 文件上传

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/materials/upload | 上传文件 | ✅ |

**服务地址：** `http://localhost:8083` (material-service)

---

## 6. 企业资料接口

### 6.1 企业信息

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | /api/enterprise/info | 获取企业信息 | ✅ |
| PUT | /api/enterprise/info | 更新企业信息 | ✅ |

### 6.2 资质管理

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/enterprise/qualifications | 添加资质 | ✅ |
| GET | /api/enterprise/qualifications | 资质列表 | ✅ |
| PUT | /api/enterprise/qualifications/{id} | 更新资质 | ✅ |
| DELETE | /api/enterprise/qualifications/{id} | 删除资质 | ✅ |
| POST | /api/enterprise/qualifications/{id}/upload | 上传证书 | ✅ |

### 6.3 人员管理

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/enterprise/persons | 添加人员 | ✅ |
| GET | /api/enterprise/persons | 人员列表 | ✅ |
| PUT | /api/enterprise/persons/{id} | 更新人员 | ✅ |
| DELETE | /api/enterprise/persons/{id} | 删除人员 | ✅ |

### 6.4 业绩管理

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/enterprise/performances | 添加业绩 | ✅ |
| GET | /api/enterprise/performances | 业绩列表 | ✅ |
| PUT | /api/enterprise/performances/{id} | 更新业绩 | ✅ |
| DELETE | /api/enterprise/performances/{id} | 删除业绩 | ✅ |

### 6.5 有效期预警

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | /api/enterprise/expiring | 即将到期列表 | ✅ |

**服务地址：** `http://localhost:8083` (material-service)

---

## 7. 知识库接口

### 7.1 知识库CRUD

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/knowledge/bases | 创建知识库 | ✅ |
| GET | /api/knowledge/bases | 知识库列表 | ✅ |
| GET | /api/knowledge/bases/{id} | 知识库详情 | ✅ |
| PUT | /api/knowledge/bases/{id} | 更新知识库 | ✅ |
| DELETE | /api/knowledge/bases/{id} | 删除知识库 | ✅ |

### 7.2 文档管理

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/knowledge/bases/{id}/documents | 添加文档 | ✅ |
| GET | /api/knowledge/bases/{id}/documents | 文档列表 | ✅ |
| DELETE | /api/knowledge/bases/{id}/documents/{docId} | 删除文档 | ✅ |
| POST | /api/knowledge/bases/{id}/documents/{docId}/parse | 解析文档 | ✅ |

### 7.3 切片管理

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | /api/knowledge/bases/{id}/chunks | 切片列表 | ✅ |
| GET | /api/knowledge/bases/{id}/chunks/{chunkId} | 切片详情 | ✅ |
| PUT | /api/knowledge/bases/{id}/chunks/{chunkId} | 更新切片 | ✅ |

### 7.4 检索接口

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/knowledge/bases/{id}/retrieve | 向量检索 | ✅ |
| POST | /api/knowledge/bases/{id}/test | 命中测试 | ✅ |

### 7.5 健康检查

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | /health | 健康检查 | ✅ |

**服务地址：** `http://localhost:8086` (knowledge-service)

---

## 8. AI服务接口

### 8.1 招标文件解析

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/ai/parse/bid-document | 解析招标文件 | ✅ |

### 8.2 技术标生成

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/ai/generate/outline | 生成目录大纲 | ✅ |
| POST | /api/ai/generate/content | 生成正文内容 | ✅ |

### 8.3 标书改写

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/ai/rewrite | 标书改写 | ✅ |

### 8.4 资信标生成

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/ai/generate/credit-bid | 资信标生成 | ✅ |

### 8.5 合规检测

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | /api/ai/check/compliance | 合规性检测 | ✅ |

### 8.6 健康检查

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | /health | 健康检查 | ✅ |

**服务地址：** `http://localhost:8087` (ai-service)

---

## 9. 网关接口

### 9.1 健康检查

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | /health | 网关健康检查 | ✅ |
| GET | /api/health | API健康检查 | ✅ |

**服务地址：** `http://localhost:8080` (gateway)

---

## 附录：服务端口映射

| 服务 | 端口 | 容器名 |
|------|------|--------|
| Gateway | 8080 | aidbid-gateway |
| User Service | 8081 | aidbid-user |
| Project Service | 8082 | aidbid-project |
| Material Service | 8083 | aidbid-material |
| Document Service | 8084 | aidbid-document |
| Knowledge Service | 8086 | aidbid-knowledge |
| AI Service | 8087 | aidbid-ai |
| PostgreSQL | 5432 | aidbid-postgres |
| Redis | 6379 | aidbid-redis |
| ChromaDB | 8000 | aidbid-chroma |

---

*文档版本：v1.0.0*
*最后更新：2026-05-26*