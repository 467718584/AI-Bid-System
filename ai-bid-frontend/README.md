# AI智能投标系统 - 前端

基于 Vue 3 + Vite + Element Plus 的投标文件智能编制平台前端。

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4+ | 渐进式JavaScript框架 |
| Vite | 5.x | 下一代前端构建工具 |
| Element Plus | 2.x | Vue3 UI组件库 |
| Pinia | 2.x | Vue状态管理 |
| Vue Router | 4.x | Vue路由管理 |
| Axios | 1.x | HTTP请求库 |

## 项目结构

```
ai-bid-frontend/
├── src/
│   ├── api/                  # API封装层
│   │   ├── index.js          # Axios实例
│   │   ├── user.js           # 用户模块
│   │   ├── project.js        # 项目模块
│   │   ├── document.js       # 文档模块
│   │   ├── material.js       # 素材模块
│   │   └── ai.js             # AI模块
│   ├── components/           # 组件层
│   │   ├── common/           # 公共组件
│   │   └── bid/              # 标书业务组件
│   ├── composables/          # 组合式函数
│   ├── router/               # 路由配置
│   ├── stores/               # Pinia状态管理
│   ├── styles/               # 样式层
│   │   ├── constants/        # 样式常量
│   │   └── common/           # 公共样式
│   ├── utils/                # 工具函数
│   ├── views/                # 页面视图
│   ├── App.vue               # 根组件
│   └── main.js               # 应用入口
├── index.html
├── package.json
├── vite.config.js
└── .env.example
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发环境

```bash
npm run dev
```

### 生产构建

```bash
npm run build
```

### 预览构建

```bash
npm run preview
```

## 环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=AI智能投标系统
```

## 路由

| 路径 | 说明 |
|------|------|
| / | 首页 |
| /login | 登录页 |
| /bid | 标书列表 |
| /bid/create | 创建标书 |
| /bid/:id | 标书编辑 |
| /bid/:id/preview | 标书预览 |

## 样式系统

样式与业务解耦，通过CSS变量实现：

- `src/styles/constants/theme.css` - 主题变量
- `src/styles/constants/variables.css` - 全局变量
- `src/styles/constants/mixins.css` - 样式混入
- `src/styles/index.css` - 样式入口

## 相关文档

- [前端解耦架构设计文档](../../docs/3_系统设计/02_前端解耦架构设计.md)
- [API接口设计文档](../../docs/5_接口设计/01_API接口设计.md)