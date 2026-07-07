-- AI-BID 简版初始化脚本（无向量扩展）

CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT PRIMARY KEY, username VARCHAR(50) NOT NULL UNIQUE, password VARCHAR(128) NOT NULL,
    nickname VARCHAR(50), email VARCHAR(100), phone VARCHAR(20), avatar VARCHAR(255),
    gender INTEGER DEFAULT 0, dept_id BIGINT, status INTEGER DEFAULT 0,
    last_login_ip VARCHAR(50), last_login_time TIMESTAMP, remark VARCHAR(500),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sys_user_username ON sys_user(username);
CREATE INDEX IF NOT EXISTS idx_sys_user_status ON sys_user(status);
CREATE INDEX IF NOT EXISTS idx_sys_user_deleted ON sys_user(deleted);

CREATE TABLE IF NOT EXISTS sys_role (
    id BIGINT PRIMARY KEY, role_name VARCHAR(50) NOT NULL, role_code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255), status INTEGER DEFAULT 0,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sys_role_code ON sys_role(role_code);
CREATE INDEX IF NOT EXISTS idx_sys_role_deleted ON sys_role(deleted);

CREATE TABLE IF NOT EXISTS sys_user_role (
    id BIGINT PRIMARY KEY, user_id BIGINT NOT NULL, role_id BIGINT NOT NULL, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sys_user_role_user ON sys_user_role(user_id);
CREATE INDEX IF NOT EXISTS idx_sys_user_role_role ON sys_user_role(role_id);

CREATE TABLE IF NOT EXISTS sys_permission (
    id BIGINT PRIMARY KEY, name VARCHAR(100) NOT NULL, code VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20) DEFAULT 'menu', parent_id BIGINT DEFAULT 0, path VARCHAR(200),
    icon VARCHAR(100), sort INTEGER DEFAULT 0,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sys_permission_code ON sys_permission(code);
CREATE INDEX IF NOT EXISTS idx_sys_permission_parent ON sys_permission(parent_id);

CREATE TABLE IF NOT EXISTS sys_role_permission (
    id BIGINT PRIMARY KEY, role_id BIGINT NOT NULL, permission_id BIGINT NOT NULL, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sys_role_permission_role ON sys_role_permission(role_id);
CREATE INDEX IF NOT EXISTS idx_sys_role_permission_perm ON sys_role_permission(permission_id);

CREATE TABLE IF NOT EXISTS bid_project (
    id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, code VARCHAR(50) UNIQUE, type VARCHAR(50),
    amount DECIMAL(15,2), tenderer VARCHAR(200), contact_person VARCHAR(100), contact_phone VARCHAR(20),
    deadline TIMESTAMP, status VARCHAR(20) DEFAULT 'DRAFT', description TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_bid_project_code ON bid_project(code);
CREATE INDEX IF NOT EXISTS idx_bid_project_status ON bid_project(status);
CREATE INDEX IF NOT EXISTS idx_bid_project_deleted ON bid_project(deleted);

CREATE TABLE IF NOT EXISTS bid_material (
    id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, type VARCHAR(50), project_id BIGINT,
    file_path VARCHAR(500), file_size BIGINT, file_type VARCHAR(50), upload_user_id BIGINT,
    status VARCHAR(20) DEFAULT 'PENDING', remark VARCHAR(500),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_bid_material_project ON bid_material(project_id);
CREATE INDEX IF NOT EXISTS idx_bid_material_deleted ON bid_material(deleted);

CREATE TABLE IF NOT EXISTS bid_document (
    id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, type VARCHAR(50), project_id BIGINT, material_id BIGINT,
    file_path VARCHAR(500), file_size BIGINT, content TEXT, parse_status VARCHAR(20) DEFAULT 'PENDING',
    analysis_result TEXT, status VARCHAR(20) DEFAULT 'ACTIVE',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_bid_document_project ON bid_document(project_id);
CREATE INDEX IF NOT EXISTS idx_bid_document_deleted ON bid_document(deleted);

CREATE TABLE IF NOT EXISTS bid_template (
    id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, code VARCHAR(50) UNIQUE, category VARCHAR(50),
    content TEXT, file_path VARCHAR(500), is_default INTEGER DEFAULT 0, status INTEGER DEFAULT 0,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_bid_template_code ON bid_template(code);

CREATE TABLE IF NOT EXISTS ai_task (
    id BIGINT PRIMARY KEY, task_type VARCHAR(50) NOT NULL, target_type VARCHAR(50), target_id BIGINT,
    input_data TEXT, output_data TEXT, status VARCHAR(20) DEFAULT 'PENDING', error_message VARCHAR(500),
    start_time TIMESTAMP, end_time TIMESTAMP, cost_time BIGINT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_ai_task_status ON ai_task(status);

CREATE TABLE IF NOT EXISTS sys_operation_log (
    id BIGINT PRIMARY KEY, module VARCHAR(50), business_type VARCHAR(20), method VARCHAR(200),
    request_method VARCHAR(10), request_url VARCHAR(500), request_params TEXT, response_data TEXT,
    user_id BIGINT, username VARCHAR(50), ip VARCHAR(50), user_agent VARCHAR(500),
    cost_time BIGINT, status INTEGER DEFAULT 0, error_message VARCHAR(500), create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sys_log_user ON sys_operation_log(user_id);
CREATE INDEX IF NOT EXISTS idx_sys_log_create_time ON sys_operation_log(create_time);

-- 初始数据
INSERT INTO sys_user (id, username, password, nickname, email, status, create_time, update_time, deleted)
VALUES (1, 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH',
        '管理员', 'admin@aibid.com', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
ON CONFLICT (username) DO NOTHING;

INSERT INTO sys_role (id, role_name, role_code, description, status, create_time, deleted)
VALUES (1, '超级管理员', 'SUPER_ADMIN', '系统超级管理员', 0, CURRENT_TIMESTAMP, 0),
       (2, '普通用户', 'USER', '普通用户', 0, CURRENT_TIMESTAMP, 0)
ON CONFLICT (role_code) DO NOTHING;

INSERT INTO sys_user_role (id, user_id, role_id, create_time)
VALUES (1, 1, 1, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;
