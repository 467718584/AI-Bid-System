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
    username        VARCHAR(50) NOT NULL UNIQUE,
    password        VARCHAR(128) NOT NULL,
    nickname        VARCHAR(50),
    email           VARCHAR(100),
    phone           VARCHAR(20),
    avatar          VARCHAR(255),
    gender          INTEGER DEFAULT 0,
    dept_id         BIGINT,
    status          INTEGER DEFAULT 0,
    last_login_ip   VARCHAR(50),
    last_login_time TIMESTAMP,
    remark          VARCHAR(500),
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
    role_name   VARCHAR(50) NOT NULL,
    role_code   VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    status      INTEGER DEFAULT 0,
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
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(100) NOT NULL UNIQUE,
    type        VARCHAR(20) DEFAULT 'menu',
    parent_id   BIGINT DEFAULT 0,
    path        VARCHAR(200),
    icon        VARCHAR(100),
    sort        INTEGER DEFAULT 0,
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
    name            VARCHAR(200) NOT NULL,
    code            VARCHAR(50) UNIQUE,
    type            VARCHAR(50),
    amount          DECIMAL(15,2),
    tenderer        VARCHAR(200),
    contact_person  VARCHAR(100),
    contact_phone   VARCHAR(20),
    deadline        TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'DRAFT',
    description     TEXT,
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
    name            VARCHAR(200) NOT NULL,
    type            VARCHAR(50),
    project_id      BIGINT,
    file_path       VARCHAR(500),
    file_size       BIGINT,
    file_type       VARCHAR(50),
    upload_user_id   BIGINT,
    status          VARCHAR(20) DEFAULT 'PENDING',
    remark          VARCHAR(500),
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
    name            VARCHAR(200) NOT NULL,
    type            VARCHAR(50),
    project_id      BIGINT,
    material_id     BIGINT,
    file_path       VARCHAR(500),
    file_size       BIGINT,
    content         TEXT,
    parse_status    VARCHAR(20) DEFAULT 'PENDING',
    analysis_result TEXT,
    embedding       VECTOR(1536),
    status          VARCHAR(20) DEFAULT 'ACTIVE',
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
    name            VARCHAR(200) NOT NULL,
    code            VARCHAR(50) UNIQUE,
    category        VARCHAR(50),
    content         TEXT,
    file_path       VARCHAR(500),
    is_default      INTEGER DEFAULT 0,
    status          INTEGER DEFAULT 0,
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
    task_type       VARCHAR(50) NOT NULL,
    target_type     VARCHAR(50),
    target_id       BIGINT,
    input_data      TEXT,
    output_data     TEXT,
    status          VARCHAR(20) DEFAULT 'PENDING',
    error_message   VARCHAR(500),
    start_time      TIMESTAMP,
    end_time        TIMESTAMP,
    cost_time       BIGINT,
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
    module          VARCHAR(50),
    business_type   VARCHAR(20),
    method          VARCHAR(200),
    request_method  VARCHAR(10),
    request_url     VARCHAR(500),
    request_params  TEXT,
    response_data   TEXT,
    user_id         BIGINT,
    username        VARCHAR(50),
    ip             VARCHAR(50),
    user_agent      VARCHAR(500),
    cost_time       BIGINT,
    status          INTEGER DEFAULT 0,
    error_message   VARCHAR(500),
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

-- =============================================
-- 外键约束定义
-- =============================================

-- 用户角色关联表外键
ALTER TABLE sys_user_role ADD CONSTRAINT fk_user_role_user FOREIGN KEY (user_id) REFERENCES sys_user(id);
ALTER TABLE sys_user_role ADD CONSTRAINT fk_user_role_role FOREIGN KEY (role_id) REFERENCES sys_role(id);

-- 角色权限关联表外键
ALTER TABLE sys_role_permission ADD CONSTRAINT fk_role_perm_role FOREIGN KEY (role_id) REFERENCES sys_role(id);
ALTER TABLE sys_role_permission ADD CONSTRAINT fk_role_perm_perm FOREIGN KEY (permission_id) REFERENCES sys_permission(id);

-- 投标材料表外键
ALTER TABLE bid_material ADD CONSTRAINT fk_material_project FOREIGN KEY (project_id) REFERENCES bid_project(id);
ALTER TABLE bid_material ADD CONSTRAINT fk_material_upload_user FOREIGN KEY (upload_user_id) REFERENCES sys_user(id);

-- 投标文档表外键
ALTER TABLE bid_document ADD CONSTRAINT fk_document_project FOREIGN KEY (project_id) REFERENCES bid_project(id);
ALTER TABLE bid_document ADD CONSTRAINT fk_document_material FOREIGN KEY (material_id) REFERENCES bid_material(id);

-- 操作日志表外键
ALTER TABLE sys_operation_log ADD CONSTRAINT fk_oplog_user FOREIGN KEY (user_id) REFERENCES sys_user(id);
