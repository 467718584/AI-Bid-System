-- Init script without vector extension for systems without pgvector
-- This creates all tables except those requiring vector type

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. System tables
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

CREATE TABLE IF NOT EXISTS sys_user_role (
    id      BIGINT PRIMARY KEY,
    user_id  BIGINT NOT NULL,
    role_id  BIGINT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_user_role_user ON sys_user_role(user_id);
CREATE INDEX idx_sys_user_role_role ON sys_user_role(role_id);

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

CREATE TABLE IF NOT EXISTS sys_role_permission (
    id          BIGINT PRIMARY KEY,
    role_id     BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_role_permission_role ON sys_role_permission(role_id);
CREATE INDEX idx_sys_role_permission_perm ON sys_role_permission(permission_id);

-- 2. Project tables
CREATE TABLE IF NOT EXISTS bid_project (
    id              BIGINT PRIMARY KEY,
    project_name     VARCHAR(200) NOT NULL,
    project_code     VARCHAR(100),
    province         VARCHAR(50),
    city             VARCHAR(50),
    industry         VARCHAR(50),
    bidding_amount   DECIMAL(15,2),
    publishing_date  DATE,
    submission_deadline DATE,
    contact_person   VARCHAR(100),
    contact_phone    VARCHAR(20),
    contact_email    VARCHAR(100),
    procurement_category VARCHAR(100),
    procurement_mode VARCHAR(50),
    project_status   INTEGER DEFAULT 0,
    source_url       VARCHAR(500),
    description      TEXT,
    requirements     TEXT,
    evaluation_criteria TEXT,
    create_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by        BIGINT,
    update_by        BIGINT,
    version          INTEGER DEFAULT 0,
    deleted          INTEGER DEFAULT 0
);

CREATE INDEX idx_bid_project_name ON bid_project(project_name);
CREATE INDEX idx_bid_project_status ON bid_project(project_status);
CREATE INDEX idx_bid_project_del ON bid_project(deleted);

-- 3. Document tables (without vector)
CREATE TABLE IF NOT EXISTS bid_document (
    id              BIGINT PRIMARY KEY,
    project_id      BIGINT NOT NULL,
    doc_type        VARCHAR(50),
    title           VARCHAR(200),
    content         TEXT,
    file_path       VARCHAR(500),
    file_size       BIGINT,
    file_type       VARCHAR(50),
    version         INTEGER DEFAULT 1,
    status          VARCHAR(20) DEFAULT 'draft',
    generate_mode   VARCHAR(20),
    outline_json    TEXT,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version_col     INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_bid_document_project ON bid_document(project_id);
CREATE INDEX idx_bid_document_type ON bid_document(doc_type);

-- 4. Material tables
CREATE TABLE IF NOT EXISTS bid_material (
    id              BIGINT PRIMARY KEY,
    project_id      BIGINT NOT NULL,
    category        VARCHAR(50),
    title           VARCHAR(200),
    content         TEXT,
    file_path       VARCHAR(500),
    status          VARCHAR(20) DEFAULT 'active',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_bid_material_project ON bid_material(project_id);
CREATE INDEX idx_bid_material_category ON bid_material(category);

-- 5. AI Task table
CREATE TABLE IF NOT EXISTS ai_task (
    id              BIGINT PRIMARY KEY,
    task_type       VARCHAR(50),
    status          VARCHAR(20) DEFAULT 'pending',
    request_data    TEXT,
    result_data     TEXT,
    error_message   TEXT,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    complete_time   TIMESTAMP
);

CREATE INDEX idx_ai_task_type ON ai_task(task_type);
CREATE INDEX idx_ai_task_status ON ai_task(status);

-- 6. Template table
CREATE TABLE IF NOT EXISTS bid_template (
    id              BIGINT PRIMARY KEY,
    template_name   VARCHAR(100) NOT NULL,
    template_type   VARCHAR(50),
    category        VARCHAR(50),
    content         TEXT,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    deleted         INTEGER DEFAULT 0
);

-- 7. Knowledge base tables (without vector)
CREATE TABLE IF NOT EXISTS kb_knowledge_base (
    id              BIGINT PRIMARY KEY,
    kb_name         VARCHAR(100) NOT NULL,
    kb_description  VARCHAR(500),
    kb_type         VARCHAR(50),
    status          INTEGER DEFAULT 0,
    doc_count       INTEGER DEFAULT 0,
    chunk_count     INTEGER DEFAULT 0,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_kb_knowledge_base_name ON kb_knowledge_base(kb_name);

CREATE TABLE IF NOT EXISTS kb_chunk (
    id              BIGINT PRIMARY KEY,
    kb_id           BIGINT NOT NULL,
    doc_id          BIGINT,
    chunk_content   TEXT,
    chunk_order     INTEGER,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kb_chunk_kb ON kb_chunk(kb_id);

-- 8. Enterprise profile tables
CREATE TABLE IF NOT EXISTS enterprise_profile (
    id              BIGINT PRIMARY KEY,
    enterprise_name VARCHAR(200) NOT NULL,
    unified_credit_code VARCHAR(50),
    legal_person    VARCHAR(100),
    registered_capital DECIMAL(15,2),
    establish_date  DATE,
    province        VARCHAR(50),
    city            VARCHAR(50),
    address         VARCHAR(500),
    business_scope  TEXT,
    main_products   TEXT,
    certifications  TEXT,
    contact_person  VARCHAR(100),
    contact_phone   VARCHAR(20),
    contact_email   VARCHAR(100),
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_enterprise_profile_name ON enterprise_profile(enterprise_name);

CREATE TABLE IF NOT EXISTS enterprise_certificate (
    id              BIGINT PRIMARY KEY,
    enterprise_id   BIGINT NOT NULL,
    cert_name       VARCHAR(100) NOT NULL,
    cert_type       VARCHAR(50),
    cert_no         VARCHAR(100),
    issue_org       VARCHAR(200),
    issue_date      DATE,
    expire_date     DATE,
    status          VARCHAR(20) DEFAULT 'valid',
    attach_path     VARCHAR(500),
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enterprise_cert_ent ON enterprise_certificate(enterprise_id);

CREATE TABLE IF NOT EXISTS enterprise_project_case (
    id              BIGINT PRIMARY KEY,
    enterprise_id   BIGINT NOT NULL,
    project_name    VARCHAR(200) NOT NULL,
    project_type    VARCHAR(50),
    contract_amount DECIMAL(15,2),
    contract_date   DATE,
    customer_name   VARCHAR(200),
    project_status  VARCHAR(20),
    project_desc    TEXT,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enterprise_case_ent ON enterprise_project_case(enterprise_id);

CREATE TABLE IF NOT EXISTS enterprise_team_member (
    id              BIGINT PRIMARY KEY,
    enterprise_id   BIGINT NOT NULL,
    member_name     VARCHAR(100) NOT NULL,
    position        VARCHAR(100),
    education       VARCHAR(50),
    major           VARCHAR(100),
    certificates    TEXT,
    experience_years INTEGER,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enterprise_member_ent ON enterprise_team_member(enterprise_id);

-- 9. Material library tables
CREATE TABLE IF NOT EXISTS material_library (
    id              BIGINT PRIMARY KEY,
    category_id      BIGINT,
    material_name    VARCHAR(200) NOT NULL,
    material_type    VARCHAR(50),
    description      TEXT,
    tags             JSONB,
    file_path        VARCHAR(500),
    file_size        BIGINT,
    download_count   INTEGER DEFAULT 0,
    create_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by        BIGINT,
    deleted          INTEGER DEFAULT 0
);

CREATE INDEX idx_material_library_category ON material_library(category_id);
CREATE INDEX idx_material_library_name ON material_library(material_name);

CREATE TABLE IF NOT EXISTS material_category (
    id              BIGINT PRIMARY KEY,
    parent_id       BIGINT DEFAULT 0,
    category_name   VARCHAR(100) NOT NULL,
    sort            INTEGER DEFAULT 0,
    create_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_category_parent ON material_category(parent_id);

CREATE TABLE IF NOT EXISTS material_usage_log (
    id              BIGINT PRIMARY KEY,
    material_id     BIGINT NOT NULL,
    project_id      BIGINT,
    user_id         BIGINT,
    usage_type      VARCHAR(50),
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_usage_log_material ON material_usage_log(material_id);

-- 10. Operation log
CREATE TABLE IF NOT EXISTS sys_operation_log (
    id              BIGINT PRIMARY KEY,
    user_id         BIGINT,
    operation_type  VARCHAR(50),
    operation_desc  VARCHAR(500),
    request_method  VARCHAR(10),
    request_url     VARCHAR(200),
    request_params  TEXT,
    response_code   INTEGER,
    response_data   TEXT,
    ip_address      VARCHAR(50),
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sys_operation_log_user ON sys_operation_log(user_id);
CREATE INDEX idx_sys_operation_log_type ON sys_operation_log(operation_type);
