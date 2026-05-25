-- AI智能投标文件智能编制管理系统
-- 数据库初始化脚本
-- PostgreSQL 16 + pgvector

-- 创建数据库（需要手动执行: CREATE DATABASE ai_bid）

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 系统管理模块表
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    real_name VARCHAR(50),
    avatar_url VARCHAR(500),
    status INT DEFAULT 1 COMMENT '1-正常 0-禁用',
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by VARCHAR(36)
);

-- 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(50) NOT NULL,
    role_code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    status INT DEFAULT 1,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 权限表
CREATE TABLE IF NOT EXISTS sys_permission (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    permission_name VARCHAR(100) NOT NULL,
    permission_code VARCHAR(100) NOT NULL UNIQUE,
    parent_id VARCHAR(36),
    menu_type VARCHAR(20) COMMENT 'MENU-菜单 BUTTON-按钮',
    path VARCHAR(255),
    icon VARCHAR(100),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS sys_user_role (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36) NOT NULL,
    role_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_user_role UNIQUE (user_id, role_id)
);

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS sys_role_permission (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id VARCHAR(36) NOT NULL,
    permission_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_role_permission UNIQUE (role_id, permission_id)
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS sys_operation_log (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36),
    username VARCHAR(50),
    operation VARCHAR(100),
    method VARCHAR(20),
    path VARCHAR(255),
    params TEXT,
    result TEXT,
    ip VARCHAR(50),
    user_agent TEXT,
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time INT,
    status INT COMMENT '1-成功 0-失败'
);

-- ============================================
-- 投标业务模块表
-- ============================================

-- 投标项目表
CREATE TABLE IF NOT EXISTS bid_project (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(255) NOT NULL,
    project_code VARCHAR(50),
    bid_agency VARCHAR(255),
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    bid_amount DECIMAL(15,2),
    bid_deadline TIMESTAMP,
    submit_deadline TIMESTAMP,
    project_type VARCHAR(50),
    province VARCHAR(50),
    city VARCHAR(50),
    project_status VARCHAR(20) DEFAULT 'DRAFT',
    project_stage VARCHAR(20) DEFAULT 'BIDDING',
    is_qualified BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 标书文档表
CREATE TABLE IF NOT EXISTS bid_document (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(36) NOT NULL,
    doc_type VARCHAR(20) NOT NULL COMMENT 'TECHNICAL-技术标 CREDIT-资信标',
    doc_name VARCHAR(255),
    doc_status VARCHAR(20) DEFAULT 'DRAFT',
    current_version INT DEFAULT 1,
    total_pages INT,
    outline JSONB,
    keywords VARCHAR(500),
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 文档版本表
CREATE TABLE IF NOT EXISTS bid_document_version (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(36) NOT NULL,
    version_no INT NOT NULL,
    version_name VARCHAR(100),
    version_status VARCHAR(20) DEFAULT 'DRAFT',
    content LONGTEXT,
    outline JSONB,
    page_count INT,
    word_count INT,
    file_url VARCHAR(500),
    generated_by VARCHAR(20) DEFAULT 'MANUAL',
    generation_prompt TEXT,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE
);

-- ============================================
-- 素材资料模块表
-- ============================================

-- 素材分类表
CREATE TABLE IF NOT EXISTS material_category (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id VARCHAR(36),
    category_name VARCHAR(100) NOT NULL,
    category_code VARCHAR(50),
    description VARCHAR(255),
    icon VARCHAR(100),
    sort_order INT DEFAULT 0,
    is_public BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 素材表
CREATE TABLE IF NOT EXISTS material_item (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id VARCHAR(36),
    title VARCHAR(255) NOT NULL,
    file_type VARCHAR(20),
    file_url VARCHAR(500),
    file_size BIGINT,
    file_hash VARCHAR(64),
    description TEXT,
    content TEXT,
    chunk_count INT DEFAULT 0,
    tags VARCHAR(500),
    source VARCHAR(100),
    author VARCHAR(100),
    status INT DEFAULT 1,
    view_count INT DEFAULT 0,
    use_count INT DEFAULT 0,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 企业信息表
CREATE TABLE IF NOT EXISTS enterprise_info (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    enterprise_name VARCHAR(255) NOT NULL,
    credit_code VARCHAR(18),
    legal_person VARCHAR(50),
    registered_capital DECIMAL(15,2),
    registered_address VARCHAR(255),
    actual_address VARCHAR(255),
    phone VARCHAR(20),
    business_scope TEXT,
    establishment_date DATE,
    logo_url VARCHAR(500),
    intro TEXT,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- ============================================
-- 知识库模块表
-- ============================================

-- 知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    kb_name VARCHAR(100) NOT NULL,
    kb_description TEXT,
    kb_type VARCHAR(20) DEFAULT 'DOCUMENT',
    chunk_strategy VARCHAR(50) DEFAULT 'recursive',
    chunk_size INT DEFAULT 500,
    chunk_overlap INT DEFAULT 50,
    embedding_model VARCHAR(50) DEFAULT 'm3e',
    vector_dimension INT DEFAULT 1536,
    retrieval_type VARCHAR(20) DEFAULT 'similarity',
    top_k INT DEFAULT 5,
    min_similarity DECIMAL(5,4) DEFAULT 0.7,
    status INT DEFAULT 1,
    document_count INT DEFAULT 0,
    chunk_count INT DEFAULT 0,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识切片表（带向量）
CREATE TABLE IF NOT EXISTS knowledge_chunk (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    kb_id VARCHAR(36) NOT NULL,
    doc_id VARCHAR(36),
    content TEXT NOT NULL,
    vector VECTOR(1536),
    chunk_index INT,
    parent_chunk_id VARCHAR(36),
    metadata JSONB,
    keywords VARCHAR(255),
    summary TEXT,
    access_count INT DEFAULT 0,
    hit_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 索引创建
-- ============================================

-- 用户索引
CREATE INDEX IF NOT EXISTS idx_sys_user_status ON sys_user(status);
CREATE INDEX IF NOT EXISTS idx_sys_user_phone ON sys_user(phone);

-- 角色索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_sys_role_code ON sys_role(role_code);

-- 权限索引
CREATE INDEX IF NOT EXISTS idx_sys_permission_parent ON sys_permission(parent_id);
CREATE INDEX IF NOT EXISTS idx_sys_permission_code ON sys_permission(permission_code);

-- 项目索引
CREATE INDEX IF NOT EXISTS idx_bid_project_status ON bid_project(project_status);
CREATE INDEX IF NOT EXISTS idx_bid_project_deadline ON bid_project(bid_deadline);
CREATE INDEX IF NOT EXISTS idx_bid_project_created_at ON bid_project(created_at);

-- 文档索引
CREATE INDEX IF NOT EXISTS idx_bid_document_project ON bid_document(project_id);
CREATE INDEX IF NOT EXISTS idx_bid_document_type ON bid_document(doc_type);

-- 素材索引
CREATE INDEX IF NOT EXISTS idx_material_item_category ON material_item(category_id);
CREATE INDEX IF NOT EXISTS idx_material_item_title ON material_item(title);

-- 知识库索引
CREATE INDEX IF NOT EXISTS idx_knowledge_base_status ON knowledge_base(status);

-- 向量索引（HNSW）
CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_vector ON knowledge_chunk USING hnsw (vector vector_cosine_ops);

-- ============================================
-- 初始化数据
-- ============================================

-- 初始化管理员账号 (密码: Admin123!)
INSERT INTO sys_user (id, username, password, real_name, email, status, created_by)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'admin',
    '$2a$10$rBN0r8Z8vNZ8LZVZ1NqZ5eRkLqLQZqLQZqLQZqLQZqLQZqLQZqLQ',
    '系统管理员',
    'admin@ai-bid.com',
    1,
    '00000000-0000-0000-0000-000000000001'
) ON CONFLICT (username) DO NOTHING;

-- 初始化角色
INSERT INTO sys_role (id, role_name, role_code, description, sort_order) VALUES
('00000000-0000-0000-0000-000000000001', '系统管理员', 'ADMIN', '系统管理员，拥有全部权限', 1),
('00000000-0000-0000-0000-000000000002', '投标负责人', 'PM', '投标项目负责人', 2),
('00000000-0000-0000-0000-000000000003', '编标人员', 'WRITER', '标书编制人员', 3),
('00000000-0000-0000-0000-000000000004', '审核人员', 'REVIEWER', '标书审核人员', 4)
ON CONFLICT (role_code) DO NOTHING;

-- 分配管理员角色
INSERT INTO sys_user_role (user_id, role_id)
VALUES ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001')
ON CONFLICT DO NOTHING;

-- ============================================
-- 触发器函数
-- ============================================

-- 自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为主要表创建触发器
DROP TRIGGER IF EXISTS update_sys_user_updated_at ON sys_user;
CREATE TRIGGER update_sys_user_updated_at BEFORE UPDATE ON sys_user
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sys_role_updated_at ON sys_role;
CREATE TRIGGER update_sys_role_updated_at BEFORE UPDATE ON sys_role
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bid_project_updated_at ON bid_project;
CREATE TRIGGER update_bid_project_updated_at BEFORE UPDATE ON bid_project
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bid_document_updated_at ON bid_document;
CREATE TRIGGER update_bid_document_updated_at BEFORE UPDATE ON bid_document
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE sys_user IS '用户表';
COMMENT ON TABLE sys_role IS '角色表';
COMMENT ON TABLE sys_permission IS '权限表';
COMMENT ON TABLE bid_project IS '投标项目表';
COMMENT ON TABLE bid_document IS '标书文档表';
COMMENT ON TABLE bid_document_version IS '文档版本表';
COMMENT ON TABLE material_category IS '素材分类表';
COMMENT ON TABLE material_item IS '素材表';
COMMENT ON TABLE enterprise_info IS '企业信息表';
COMMENT ON TABLE knowledge_base IS '知识库表';
COMMENT ON TABLE knowledge_chunk IS '知识切片表';