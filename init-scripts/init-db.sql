-- =============================================
-- AI Bid System Database Initialization Script
-- PostgreSQL 16 + pgvector Extension
-- =============================================

-- 启用pgvector扩展（用于AI向量存储）
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建数据库（如果不存在）
-- CREATE DATABASE aidbid;

-- =============================================
-- 1. 系统用户表
-- =============================================
CREATE TABLE IF NOT EXISTS sys_user (
    id              BIGINT PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password        VARCHAR(128) NOT NULL COMMENT '密码',
    nickname        VARCHAR(50) COMMENT '昵称',
    email           VARCHAR(100) COMMENT '邮箱',
    phone           VARCHAR(20) COMMENT '手机号',
    avatar          VARCHAR(255) COMMENT '头像URL',
    gender          INTEGER DEFAULT 0 COMMENT '性别: 0=未知, 1=男, 2=女',
    dept_id         BIGINT COMMENT '部门ID',
    status          INTEGER DEFAULT 0 COMMENT '状态: 0=正常, 1=禁用',
    last_login_ip   VARCHAR(50) COMMENT '最后登录IP',
    last_login_time TIMESTAMP COMMENT '最后登录时间',
    remark          VARCHAR(500) COMMENT '备注',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_sys_user_username ON sys_user(username);
CREATE INDEX idx_sys_user_status ON sys_user(status);
CREATE INDEX idx_sys_user_deleted ON sys_user(deleted);

-- =============================================
-- 2. 系统角色表
-- =============================================
CREATE TABLE IF NOT EXISTS sys_role (
    id          BIGINT PRIMARY KEY,
    role_name   VARCHAR(50) NOT NULL COMMENT '角色名称',
    role_code   VARCHAR(50) NOT NULL UNIQUE COMMENT '角色标识',
    description VARCHAR(255) COMMENT '角色描述',
    status      INTEGER DEFAULT 0 COMMENT '状态: 0=正常, 1=禁用',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by   BIGINT,
    update_by   BIGINT,
    version     INTEGER DEFAULT 0,
    deleted     INTEGER DEFAULT 0
);

CREATE INDEX idx_sys_role_code ON sys_role(role_code);
CREATE INDEX idx_sys_role_deleted ON sys_role(deleted);

-- =============================================
-- 3. 用户角色关联表
-- =============================================
CREATE TABLE IF NOT EXISTS sys_user_role (
    id      BIGINT PRIMARY KEY,
    user_id  BIGINT NOT NULL,
    role_id  BIGINT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_user_role_user ON sys_user_role(user_id);
CREATE INDEX idx_sys_user_role_role ON sys_user_role(role_id);

-- =============================================
-- 4. 系统权限表
-- =============================================
CREATE TABLE IF NOT EXISTS sys_permission (
    id          BIGINT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL COMMENT '权限名称',
    code        VARCHAR(100) NOT NULL UNIQUE COMMENT '权限标识',
    type        VARCHAR(20) DEFAULT 'menu' COMMENT '类型: menu=菜单, button=按钮',
    parent_id   BIGINT DEFAULT 0 COMMENT '父权限ID',
    path        VARCHAR(200) COMMENT '路由路径',
    icon        VARCHAR(100) COMMENT '图标',
    sort        INTEGER DEFAULT 0 COMMENT '排序',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by   BIGINT,
    update_by   BIGINT,
    version     INTEGER DEFAULT 0,
    deleted     INTEGER DEFAULT 0
);

CREATE INDEX idx_sys_permission_code ON sys_permission(code);
CREATE INDEX idx_sys_permission_parent ON sys_permission(parent_id);

-- =============================================
-- 5. 角色权限关联表
-- =============================================
CREATE TABLE IF NOT EXISTS sys_role_permission (
    id              BIGINT PRIMARY KEY,
    role_id         BIGINT NOT NULL,
    permission_id   BIGINT NOT NULL,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_role_permission_role ON sys_role_permission(role_id);
CREATE INDEX idx_sys_role_permission_perm ON sys_role_permission(permission_id);

-- =============================================
-- 6. 投标项目表
-- =============================================
CREATE TABLE IF NOT EXISTS bid_project (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL COMMENT '项目名称',
    code            VARCHAR(50) UNIQUE COMMENT '项目编号',
    type            VARCHAR(50) COMMENT '项目类型',
    amount          DECIMAL(15,2) COMMENT '招标金额',
    tenderer        VARCHAR(200) COMMENT '招标单位',
    contact_person  VARCHAR(100) COMMENT '甲方联系人',
    contact_phone   VARCHAR(20) COMMENT '甲方联系电话',
    deadline        TIMESTAMP COMMENT '投标截止时间',
    status          VARCHAR(20) DEFAULT 'DRAFT' COMMENT '状态: DRAFT/IN_PROGRESS/COMPLETED/CANCELLED',
    description     TEXT COMMENT '项目描述',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_bid_project_code ON bid_project(code);
CREATE INDEX idx_bid_project_status ON bid_project(status);
CREATE INDEX idx_bid_project_deadline ON bid_project(deadline);
CREATE INDEX idx_bid_project_deleted ON bid_project(deleted);

-- =============================================
-- 7. 投标材料表
-- =============================================
CREATE TABLE IF NOT EXISTS bid_material (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL COMMENT '材料名称',
    type            VARCHAR(50) COMMENT '材料类型',
    project_id      BIGINT COMMENT '所属项目ID',
    file_path       VARCHAR(500) COMMENT '文件存储路径',
    file_size       BIGINT COMMENT '文件大小(字节)',
    file_type       VARCHAR(50) COMMENT '文件类型',
    upload_user_id   BIGINT COMMENT '上传用户ID',
    status          VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态: PENDING/APPROVED/REJECTED',
    remark          VARCHAR(500) COMMENT '备注',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_bid_material_project ON bid_material(project_id);
CREATE INDEX idx_bid_material_type ON bid_material(type);
CREATE INDEX idx_bid_material_deleted ON bid_material(deleted);

-- =============================================
-- 8. 投标文档表
-- =============================================
CREATE TABLE IF NOT EXISTS bid_document (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL COMMENT '文档名称',
    type            VARCHAR(50) COMMENT '文档类型',
    project_id      BIGINT COMMENT '所属项目ID',
    material_id     BIGINT COMMENT '关联材料ID',
    file_path       VARCHAR(500) COMMENT '文件存储路径',
    file_size       BIGINT COMMENT '文件大小(字节)',
    content         TEXT COMMENT '文档解析内容',
    parse_status    VARCHAR(20) DEFAULT 'PENDING' COMMENT '解析状态: PENDING/PARSING/COMPLETED/FAILED',
    analysis_result TEXT COMMENT 'AI分析结果(JSON)',
    embedding       VECTOR(1536) COMMENT '文档向量 embedding (pgvector)',
    status          VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE/ARCHIVED',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_bid_document_project ON bid_document(project_id);
CREATE INDEX idx_bid_document_material ON bid_document(material_id);
CREATE INDEX idx_bid_document_parse_status ON bid_document(parse_status);
CREATE INDEX idx_bid_document_deleted ON bid_document(deleted);
-- 向量索引（用于相似度搜索）
CREATE INDEX idx_bid_document_embedding ON bid_document USING ivfflat (embedding vector_cosine_ops);

-- =============================================
-- 9. 标书模板表
-- =============================================
CREATE TABLE IF NOT EXISTS bid_template (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL COMMENT '模板名称',
    code            VARCHAR(50) UNIQUE COMMENT '模板编码',
    category        VARCHAR(50) COMMENT '模板分类',
    content         TEXT COMMENT '模板内容',
    file_path       VARCHAR(500) COMMENT '模板文件路径',
    is_default      INTEGER DEFAULT 0 COMMENT '是否默认模板',
    status          INTEGER DEFAULT 0 COMMENT '状态: 0=正常, 1=禁用',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_bid_template_code ON bid_template(code);
CREATE INDEX idx_bid_template_category ON bid_template(category);

-- =============================================
-- 10. AI分析任务表
-- =============================================
CREATE TABLE IF NOT EXISTS ai_task (
    id              BIGINT PRIMARY KEY,
    task_type       VARCHAR(50) NOT NULL COMMENT '任务类型: analyze/embedding/summary',
    target_type     VARCHAR(50) COMMENT '目标类型: document/material',
    target_id       BIGINT COMMENT '目标ID',
    input_data      TEXT COMMENT '输入数据(JSON)',
    output_data     TEXT COMMENT '输出结果(JSON)',
    status          VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态: PENDING/RUNNING/COMPLETED/FAILED',
    error_message   VARCHAR(500) COMMENT '错误信息',
    start_time      TIMESTAMP COMMENT '开始时间',
    end_time        TIMESTAMP COMMENT '结束时间',
    cost_time       BIGINT COMMENT '耗时(毫秒)',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_ai_task_type ON ai_task(task_type);
CREATE INDEX idx_ai_task_status ON ai_task(status);
CREATE INDEX idx_ai_task_target ON ai_task(target_type, target_id);

-- =============================================
-- 11. 操作日志表
-- =============================================
CREATE TABLE IF NOT EXISTS sys_operation_log (
    id              BIGINT PRIMARY KEY,
    module          VARCHAR(50) COMMENT '模块',
    business_type   VARCHAR(20) COMMENT '业务类型: CREATE/UPDATE/DELETE/QUERY',
    method          VARCHAR(200) COMMENT '请求方法',
    request_method  VARCHAR(10) COMMENT '请求方式: GET/POST/PUT/DELETE',
    request_url     VARCHAR(500) COMMENT '请求URL',
    request_params  TEXT COMMENT '请求参数',
    response_data   TEXT COMMENT '响应数据',
    user_id         BIGINT COMMENT '操作用户ID',
    username        VARCHAR(50) COMMENT '用户名',
    ip             VARCHAR(50) COMMENT 'IP地址',
    user_agent      VARCHAR(500) COMMENT 'User-Agent',
    cost_time       BIGINT COMMENT '耗时(毫秒)',
    status          INTEGER DEFAULT 0 COMMENT '状态: 0=成功, 1=失败',
    error_message   VARCHAR(500) COMMENT '错误信息',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_log_user ON sys_operation_log(user_id);
CREATE INDEX idx_sys_log_module ON sys_operation_log(module);
CREATE INDEX idx_sys_log_create_time ON sys_operation_log(create_time);

-- =============================================
-- 初始数据
-- =============================================

-- 插入默认超级管理员用户 (密码: admin123)
INSERT INTO sys_user (id, username, password, nickname, email, status, create_time, update_time, deleted)
VALUES (1, 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH',
        '超级管理员', 'admin@aibid.com', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
ON CONFLICT (username) DO NOTHING;

-- 插入默认角色
INSERT INTO sys_role (id, role_name, role_code, description, status, create_time, deleted)
VALUES 
    (1, '超级管理员', 'SUPER_ADMIN', '系统超级管理员，拥有所有权限', 0, CURRENT_TIMESTAMP, 0),
    (2, '普通用户', 'USER', '普通用户角色', 0, CURRENT_TIMESTAMP, 0),
    (3, '投标经理', 'BID_MANAGER', '投标项目管理员', 0, CURRENT_TIMESTAMP, 0)
ON CONFLICT (role_code) DO NOTHING;

-- 绑定超管用户角色
INSERT INTO sys_user_role (id, user_id, role_id, create_time)
VALUES (1, 1, 1, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- 插入默认权限
INSERT INTO sys_permission (id, name, code, type, parent_id, path, sort, create_time, deleted)
VALUES 
    (1, '系统管理', 'system', 'menu', 0, '/system', 1, CURRENT_TIMESTAMP, 0),
    (2, '用户管理', 'system:user', 'menu', 1, '/system/user', 1, CURRENT_TIMESTAMP, 0),
    (3, '角色管理', 'system:role', 'menu', 1, '/system/role', 2, CURRENT_TIMESTAMP, 0),
    (4, '项目管理', 'project', 'menu', 0, '/project', 2, CURRENT_TIMESTAMP, 0),
    (5, '材料管理', 'material', 'menu', 0, '/material', 3, CURRENT_TIMESTAMP, 0),
    (6, '文档管理', 'document', 'menu', 0, '/document', 4, CURRENT_TIMESTAMP, 0)
ON CONFLICT (code) DO NOTHING;

-- 超管角色绑定所有权限
INSERT INTO sys_role_permission (id, role_id, permission_id, create_time)
SELECT 1, 1, id, CURRENT_TIMESTAMP FROM sys_permission
ON CONFLICT DO NOTHING;

-- =============================================
-- 完成
-- =============================================
