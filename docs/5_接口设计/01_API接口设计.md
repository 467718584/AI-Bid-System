# API接口设计文档

| 项目 | 说明 |
|------|------|
| 项目名称 | AI智能投标文件智能编制管理系统 |
| 项目代号 | ai-bid-system |
| 版本 | v1.0.0 |
| 日期 | 2026-05-25 |
| 团队 | bid-team |
| 作者 | bid-admin |

---

## 目录

1. [接口规范](#1-接口规范)
2. [统一响应格式](#2-统一响应格式)
3. [认证授权](#3-认证授权)
4. [用户管理接口](#4-用户管理接口)
5. [项目管理接口](#5-项目管理接口)
6. [文档管理接口](#6-文档管理接口)
7. [素材库接口](#7-素材库接口)
8. [企业资料接口](#8-企业资料接口)
9. [知识库接口](#9-知识库接口)
10. [AI服务接口](#10-ai服务接口)
11. [错误码定义](#11-错误码定义)

---

## 1. 接口规范

### 1.1 基本规范

| 项目 | 规范 |
|------|------|
| 协议 | HTTP/HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 请求方法 | GET/POST/PUT/DELETE |
| 分页 | page（从1开始）+ pageSize |

### 1.2 URL规范

```
http(s)://{host}:{port}/api/{module}/{resource}
```

### 1.3 请求头规范

| Header | 说明 | 必填 |
|--------|------|------|
| Content-Type | application/json | 是 |
| Authorization | Bearer {token} | 是 |
| Accept | application/json | 否 |
| X-Request-Id | 请求唯一ID | 否 |

---

## 2. 统一响应格式

### 2.1 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": 1701234567890,
  "requestId": "uuid-string"
}
```

### 2.2 分页响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 100,
      "totalPages": 5
    }
  },
  "timestamp": 1701234567890,
  "requestId": "uuid-string"
}
```

### 2.3 错误响应

```json
{
  "code": 400,
  "message": "参数错误：username不能为空",
  "error": "VALIDATION_ERROR",
  "details": [
    {
      "field": "username",
      "message": "不能为空"
    }
  ],
  "timestamp": 1701234567890,
  "requestId": "uuid-string"
}
```

---

## 3. 认证授权

### 3.1 登录接口

**POST** `/api/auth/login`

**请求：**
```json
{
  "username": "admin",
  "password": "password123",
  "captcha": "abcd",
  "captchaKey": "uuid-key"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 7200,
    "user": {
      "id": "uuid",
      "username": "admin",
      "realName": "系统管理员",
      "roles": ["ADMIN"]
    }
  }
}
```

### 3.2 刷新Token

**POST** `/api/auth/refresh`

**请求：**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3.3 登出

**POST** `/api/auth/logout`

---

## 4. 用户管理接口

### 4.1 用户CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/users | 创建用户 |
| GET | /api/users | 查询用户列表 |
| GET | /api/users/{id} | 查询用户详情 |
| PUT | /api/users/{id} | 更新用户 |
| DELETE | /api/users/{id} | 删除用户 |
| PUT | /api/users/{id}/password | 修改密码 |
| PUT | /api/users/{id}/status | 修改状态 |
| POST | /api/users/{id}/roles | 分配角色 |

**创建用户 POST /api/users**

```json
{
  "username": "zhangsan",
  "password": "Password123!",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "realName": "张三",
  "roleIds": ["uuid1", "uuid2"]
}
```

### 4.2 角色管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/roles | 创建角色 |
| GET | /api/roles | 查询角色列表 |
| GET | /api/roles/{id} | 查询角色详情 |
| PUT | /api/roles/{id} | 更新角色 |
| DELETE | /api/roles/{id} | 删除角色 |
| GET | /api/roles/{id}/permissions | 获取角色权限 |
| PUT | /api/roles/{id}/permissions | 分配权限 |

---

## 5. 项目管理接口

### 5.1 项目CRUD

**POST** `/api/projects`

```json
{
  "projectName": "XX水库除险加固工程",
  "projectCode": "BID-2026-001",
  "bidAgency": "XX市水利局",
  "contactPerson": "李四",
  "contactPhone": "13900139000",
  "bidAmount": 5000000.00,
  "bidDeadline": "2026-06-30 18:00:00",
  "projectType": "水利工程",
  "province": "XX省",
  "city": "XX市"
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "projectName": "XX水库除险加固工程",
    "projectCode": "BID-2026-001",
    "projectStatus": "DRAFT",
    "createdAt": "2026-05-25 10:00:00"
  }
}
```

### 5.2 项目列表与查询

**GET** `/api/projects`

| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码 |
| pageSize | int | 每页数量 |
| projectStatus | string | 项目状态 |
| projectName | string | 项目名称（模糊） |
| startDate | date | 开始日期 |
| endDate | date | 结束日期 |

### 5.3 项目状态流转

| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | /api/projects/{id}/status | 更新项目状态 |
| POST | /api/projects/{id}/submit | 提交项目 |
| POST | /api/projects/{id}/archive | 归档项目 |

---

## 6. 文档管理接口

### 6.1 文档CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/documents | 创建文档 |
| GET | /api/documents/{id} | 获取文档详情 |
| PUT | /api/documents/{id} | 更新文档 |
| DELETE | /api/documents/{id} | 删除文档 |
| GET | /api/documents/{id}/versions | 获取版本列表 |
| GET | /api/documents/versions/{versionId} | 获取指定版本 |

### 6.2 文档内容操作

| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | /api/documents/{id}/content | 更新文档内容 |
| GET | /api/documents/{id}/content | 获取文档内容 |
| POST | /api/documents/{id}/export | 导出文档 |
| POST | /api/documents/{id}/versions | 创建新版本 |

**创建版本 POST /api/documents/{id}/versions**

```json
{
  "versionName": "V2.0 技术标初稿",
  "content": "# 第一章 项目概况...",
  "outline": {
    "title": "技术标",
    "children": [
      {"title": "第一章 项目概况", "pageCount": 2},
      {"title": "第二章 施工方案", "pageCount": 10}
    ]
  }
}
```

---

## 7. 素材库接口

### 7.1 素材分类

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/materials/categories | 创建分类 |
| GET | /api/materials/categories | 获取分类树 |
| PUT | /api/materials/categories/{id} | 更新分类 |
| DELETE | /api/materials/categories/{id} | 删除分类 |

**获取分类树 GET /api/materials/categories**

```json
{
  "code": 200,
  "data": [
    {
      "id": "uuid",
      "categoryName": "水利工程",
      "children": [
        {"id": "uuid2", "categoryName": "堤防工程"},
        {"id": "uuid3", "categoryName": "水库工程"}
      ]
    }
  ]
}
```

### 7.2 素材管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/materials | 上传素材 |
| GET | /api/materials | 查询素材列表 |
| GET | /api/materials/{id} | 获取素材详情 |
| PUT | /api/materials/{id} | 更新素材 |
| DELETE | /api/materials/{id} | 删除素材 |
| GET | /api/materials/search | 搜索素材 |

**搜索素材 GET /api/materials/search**

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 关键词 |
| categoryId | string | 分类ID |
| tags | string | 标签（逗号分隔） |
| fileType | string | 文件类型 |

### 7.3 文件上传

**POST** `/api/materials/upload`

Content-Type: multipart/form-data

| 字段 | 类型 | 说明 |
|------|------|------|
| file | file | 文件 |
| categoryId | string | 分类ID |
| title | string | 标题 |
| tags | string | 标签 |
| description | string | 描述 |

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "fileName": "施工方案模板.docx",
    "fileUrl": "https://minio.../materials/xxx.docx",
    "fileSize": 1024000,
    "fileType": "WORD"
  }
}
```

---

## 8. 企业资料接口

### 8.1 企业信息

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/enterprise/info | 获取企业信息 |
| PUT | /api/enterprise/info | 更新企业信息 |

### 8.2 资质管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/enterprise/qualifications | 添加资质 |
| GET | /api/enterprise/qualifications | 资质列表 |
| PUT | /api/enterprise/qualifications/{id} | 更新资质 |
| DELETE | /api/enterprise/qualifications/{id} | 删除资质 |
| POST | /api/enterprise/qualifications/{id}/upload | 上传证书 |

### 8.3 人员管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/enterprise/persons | 添加人员 |
| GET | /api/enterprise/persons | 人员列表 |
| PUT | /api/enterprise/persons/{id} | 更新人员 |
| DELETE | /api/enterprise/persons/{id} | 删除人员 |

### 8.4 业绩管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/enterprise/performances | 添加业绩 |
| GET | /api/enterprise/performances | 业绩列表 |
| PUT | /api/enterprise/performances/{id} | 更新业绩 |
| DELETE | /api/enterprise/performances/{id} | 删除业绩 |

### 8.5 有效期预警

**GET** `/api/enterprise/expiring`

获取即将到期（30天/60天）的资质、人员证书列表

---

## 9. 知识库接口

### 9.1 知识库CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/knowledge/bases | 创建知识库 |
| GET | /api/knowledge/bases | 知识库列表 |
| GET | /api/knowledge/bases/{id} | 知识库详情 |
| PUT | /api/knowledge/bases/{id} | 更新知识库 |
| DELETE | /api/knowledge/bases/{id} | 删除知识库 |

### 9.2 文档管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/knowledge/bases/{id}/documents | 添加文档 |
| GET | /api/knowledge/bases/{id}/documents | 文档列表 |
| DELETE | /api/knowledge/bases/{id}/documents/{docId} | 删除文档 |
| POST | /api/knowledge/bases/{id}/documents/{docId}/parse | 解析文档 |

### 9.3 切片管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/knowledge/bases/{id}/chunks | 切片列表 |
| GET | /api/knowledge/bases/{id}/chunks/{chunkId} | 切片详情 |
| PUT | /api/knowledge/bases/{id}/chunks/{chunkId} | 更新切片 |

### 9.4 检索接口

**POST** `/api/knowledge/bases/{id}/retrieve`

```json
{
  "query": "施工组织设计应该包含哪些内容",
  "topK": 5,
  "minSimilarity": 0.7,
  "filters": {
    "keywords": "水利"
  }
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "results": [
      {
        "chunkId": "uuid",
        "content": "施工组织设计主要包括以下内容...",
        "similarity": 0.85,
        "metadata": {
          "docName": "技术标编制指南",
          "docId": "uuid"
        }
      }
    ],
    "total": 5
  }
}
```

### 9.5 命中测试

**POST** `/api/knowledge/bases/{id}/test`

```json
{
  "query": "项目质量管理措施",
  "topK": 3
}
```

---

## 10. AI服务接口

### 10.1 招标文件解析

**POST** `/api/ai/parse/bid-document`

Content-Type: multipart/form-data

| 字段 | 类型 | 说明 |
|------|------|------|
| file | file | 招标文件 |
| fileType | string | PDF/WORD/ZF |

**响应：**
```json
{
  "code": 200,
  "data": {
    "basicInfo": {
      "projectName": "XX工程",
      "agencyName": "XX招标代理",
      "报名截止时间": "2026-06-01 18:00"
    },
    "scoringMethod": {
      "废标条款": ["条款1", "条款2"],
      "商务评审": ["打分点1"],
      "技术评审": ["打分点2"]
    },
    "complianceItems": [
      {"requirement": "资质要求", "status": "PASS"}
    ],
    "disqualificationItems": [
      {"item": "项目经理必须是一级建造师", "location": "P12"}
    ],
    "parsingTime": 8500
  }
}
```

### 10.2 技术标目录生成

**POST** `/api/ai/generate/outline`

```json
{
  "projectId": "uuid",
  "rule": "MIXED",
  "expectedPages": 50,
  "scoringPoints": ["施工方案", "质量保证", "安全措施"],
  "requirements": "响应招标文件的各项要求"
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "outline": {
      "title": "技术标",
      "totalPages": 50,
      "children": [
        {
          "title": "第一章 项目概况",
          "pageCount": 3,
          "children": []
        },
        {
          "title": "第二章 施工方案",
          "pageCount": 15,
          "children": [
            {"title": "2.1 总体施工思路", "pageCount": 5},
            {"title": "2.2 主要施工工艺", "pageCount": 10}
          ]
        }
      ]
    },
    "generatedAt": "2026-05-25 10:00:00"
  }
}
```

### 10.3 技术标正文生成

**POST** `/api/ai/generate/content`

```json
{
  "projectId": "uuid",
  "outlineId": "uuid",
  "chapterPath": "1.2",
  "mode": "SINGLE_CHAPTER",
  "pageCount": 5,
  "includeImages": true,
  "includeTables": true
}
```

### 10.4 标书改写

**POST** `/api/ai/rewrite`

```json
{
  "content": "原有标书内容...",
  "strategy": "EXPAND",
  "multiplier": 1.5,
  "preserveKeywords": ["水库", "除险加固"]
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "originalLength": 1000,
    "rewrittenLength": 1500,
    "rewrittenContent": "改写后的内容...",
    "changes": [
      {"type": "EXPAND", "location": "P1", "description": "详细描述了施工准备工作的具体内容"}
    ]
  }
}
```

### 10.5 资信标生成

**POST** `/api/ai/generate/credit-bid`

```json
{
  "projectId": "uuid",
  "enterpriseId": "uuid",
  "sections": ["BASIC_INFO", "QUALIFICATIONS", "PERSONS", "PERFORMANCES"]
}
```

### 10.6 合规检测

**POST** `/api/ai/check/compliance`

```json
{
  "projectId": "uuid",
  "documentContent": "标书内容...",
  "checkTypes": ["DISQUALIFICATION", "KEYWORD", "FORMAT"]
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "checkResults": [
      {
        "type": "DISQUALIFICATION",
        "severity": "HIGH",
        "location": "P5",
        "description": "缺少项目经理注册造价工程师证书",
        "suggestion": "请补充项目经理的注册造价工程师证书"
      }
    ],
    "summary": {
      "total": 5,
      "high": 1,
      "medium": 2,
      "low": 2
    }
  }
}
```

---

## 11. 错误码定义

### 11.1 错误码规范

| 区间 | 含义 |
|------|------|
| 200-299 | 成功 |
| 400-499 | 客户端错误 |
| 500-599 | 服务端错误 |

### 11.2 业务错误码

| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 200 | success | 成功 |
| 400 | BAD_REQUEST | 请求参数错误 |
| 401 | UNAUTHORIZED | 未登录或Token过期 |
| 403 | FORBIDDEN | 无权限访问 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 422 | VALIDATION_ERROR | 数据校验失败 |
| 500 | INTERNAL_ERROR | 内部服务错误 |
| 502 | GATEWAY_ERROR | 网关错误 |
| 503 | SERVICE_UNAVAILABLE | 服务不可用 |

### 11.3 业务子错误码

| 子错误码 | 说明 |
|----------|------|
| USER_NOT_FOUND | 用户不存在 |
| USER_DISABLED | 用户已被禁用 |
| PASSWORD_ERROR | 密码错误 |
| TOKEN_EXPIRED | Token已过期 |
| PROJECT_NOT_FOUND | 项目不存在 |
| PROJECT_CLOSED | 项目已关闭 |
| DOCUMENT_NOT_FOUND | 文档不存在 |
| FILE_TOO_LARGE | 文件过大 |
| FILE_TYPE_NOT_SUPPORTED | 文件类型不支持 |
| UPLOAD_FAILED | 上传失败 |
| PARSE_FAILED | 解析失败 |
| GENERATE_FAILED | 生成失败 |
| KNOWLEDGE_BASE_NOT_FOUND | 知识库不存在 |
| CHUNK_NOT_FOUND | 切片不存在 |

---

## 附录：接口测试示例

### A. cURL示例

```bash
# 登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 创建项目
curl -X POST http://localhost:8080/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"projectName":"测试项目","bidAmount":1000000}'

# 上传素材
curl -X POST http://localhost:8080/api/materials/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/file.docx" \
  -F "title=施工方案模板" \
  -F "categoryId=uuid"
```

### B. Postman Collection

提供完整的Postman测试集合，包含所有接口的预请求脚本和测试断言。

---

*文档版本：v1.0.0*
*最后更新：2026-05-25*
*作者：bid-admin*