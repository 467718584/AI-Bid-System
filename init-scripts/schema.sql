-- =============================================
-- AI Bid System - Database Schema (DDL)
-- PostgreSQL 16 + pgvector Extension
-- =============================================

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
-- 12. 知识库表 (kb_knowledge_base) - Phase 2
-- =============================================
CREATE TABLE IF NOT EXISTS kb_knowledge_base (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL COMMENT '知识库名称',
    description     VARCHAR(500) COMMENT '知识库描述',
    chunk_strategy  VARCHAR(20) DEFAULT 'recursive' COMMENT '分块策略',
    chunk_size      INTEGER DEFAULT 500 COMMENT '分块大小',
    embedding_model VARCHAR(50) DEFAULT 'embo01' COMMENT 'Embedding模型',
    status          INTEGER DEFAULT 1 COMMENT '状态: 0=禁用, 1=启用',
    document_count  INTEGER DEFAULT 0 COMMENT '文档数量',
    chunk_count     INTEGER DEFAULT 0 COMMENT '块数量',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_kb_name ON kb_knowledge_base(name);
CREATE INDEX idx_kb_status ON kb_knowledge_base(status);
CREATE INDEX idx_kb_deleted ON kb_knowledge_base(deleted);

-- =============================================
-- 13. 知识块表 (kb_chunk) - Phase 2
-- =============================================
CREATE TABLE IF NOT EXISTS kb_chunk (
    id              BIGINT PRIMARY KEY,
    kb_id           BIGINT NOT NULL COMMENT '所属知识库ID',
    doc_id          VARCHAR(100) COMMENT '文档ID',
    content         TEXT NOT NULL COMMENT '块内容',
    chunk_index     INTEGER DEFAULT 0 COMMENT '块索引',
    metadata        JSONB COMMENT '元数据',
    embedding       VECTOR(1536) COMMENT '向量embedding',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_kb_chunk_kb ON kb_chunk(kb_id);
CREATE INDEX idx_kb_chunk_doc ON kb_chunk(doc_id);
CREATE INDEX idx_kb_chunk_deleted ON kb_chunk(deleted);
-- 向量索引（用于相似度搜索）
CREATE INDEX idx_kb_chunk_embedding ON kb_chunk USING ivfflat (embedding vector_cosine_ops);

-- =============================================
-- 14. 企业资料库表 (enterprise_profile) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS enterprise_profile (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL COMMENT '企业名称',
    short_name      VARCHAR(100) COMMENT '企业简称',
    logo            VARCHAR(500) COMMENT '企业Logo路径',
    address         VARCHAR(300) COMMENT '企业地址',
    legal_person     VARCHAR(50) COMMENT '法定代表人',
    contact_person  VARCHAR(50) COMMENT '联系人',
    contact_phone   VARCHAR(20) COMMENT '联系电话',
    contact_email   VARCHAR(100) COMMENT '联系邮箱',
    website         VARCHAR(200) COMMENT '官网地址',
    business_scope  VARCHAR(500) COMMENT '经营范围',
    registered_capital VARCHAR(50) COMMENT '注册资本',
    established_date DATE COMMENT '成立日期',
    description     TEXT COMMENT '企业简介',
    main_products   VARCHAR(500) COMMENT '主要产品/服务',
    core_advantages TEXT COMMENT '核心优势',
    annual_revenue  VARCHAR(50) COMMENT '年营业额',
    employee_count  VARCHAR(20) COMMENT '员工规模',
    qualification_level VARCHAR(50) COMMENT '资质等级',
    status          INTEGER DEFAULT 1 COMMENT '状态: 0=禁用, 1=启用',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_ep_name ON enterprise_profile(name);
CREATE INDEX idx_ep_status ON enterprise_profile(status);
CREATE INDEX idx_ep_deleted ON enterprise_profile(deleted);

-- =============================================
-- 15. 企业证书资质表 (enterprise_certificate) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS enterprise_certificate (
    id              BIGINT PRIMARY KEY,
    enterprise_id  BIGINT NOT NULL COMMENT '企业ID',
    name            VARCHAR(200) NOT NULL COMMENT '证书名称',
    certificate_type VARCHAR(50) COMMENT '证书类型: QUALIFICATION/CREDIT/ISO/PATENT/AWARD',
    certificate_no  VARCHAR(100) COMMENT '证书编号',
    issuing_authority VARCHAR(200) COMMENT '发证机构',
    issue_date      DATE COMMENT '发证日期',
    expiry_date     DATE COMMENT '到期日期',
    certificate_level VARCHAR(50) COMMENT '证书等级',
    file_path       VARCHAR(500) COMMENT '证书文件路径',
    file_url        VARCHAR(500) COMMENT '证书文件URL',
    is_verified     INTEGER DEFAULT 0 COMMENT '是否已认证: 0=未认证, 1=已认证',
    status          INTEGER DEFAULT 1 COMMENT '状态: 0=禁用, 1=启用',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_ec_enterprise ON enterprise_certificate(enterprise_id);
CREATE INDEX idx_ec_type ON enterprise_certificate(certificate_type);
CREATE INDEX idx_ec_expiry ON enterprise_certificate(expiry_date);
CREATE INDEX idx_ec_deleted ON enterprise_certificate(deleted);

-- =============================================
-- 16. 业绩案例表 (enterprise_project_case) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS enterprise_project_case (
    id              BIGINT PRIMARY KEY,
    enterprise_id   BIGINT NOT NULL COMMENT '企业ID',
    project_name    VARCHAR(200) NOT NULL COMMENT '项目名称',
    project_type    VARCHAR(50) COMMENT '项目类型',
    industry        VARCHAR(50) COMMENT '所属行业',
    tenderer        VARCHAR(200) COMMENT '招标单位/甲方',
    tender_amount   DECIMAL(15,2) COMMENT '中标金额',
    bid_amount      DECIMAL(15,2) COMMENT '投标金额',
    win_date        DATE COMMENT '中标日期',
    start_date      DATE COMMENT '开始日期',
    end_date        DATE COMMENT '结束日期',
    project_status  VARCHAR(20) DEFAULT 'COMPLETED' COMMENT '项目状态: IN_PROGRESS/COMPLETED/SUSPENDED',
    description     TEXT COMMENT '项目描述',
    key_highlights  TEXT COMMENT '项目亮点',
    performance_amount DECIMAL(15,2) COMMENT '业绩金额',
    performance_scope VARCHAR(500) COMMENT '业绩范围',
    contract_no     VARCHAR(100) COMMENT '合同编号',
    contact_person  VARCHAR(50) COMMENT '甲方联系人',
    contact_phone   VARCHAR(20) COMMENT '甲方联系电话',
    evaluation_rating VARCHAR(10) COMMENT '甲方评价等级',
    evaluation_remark VARCHAR(500) COMMENT '甲方评价备注',
    show_on_homepage INTEGER DEFAULT 0 COMMENT '是否首页展示: 0=否, 1=是',
    status          INTEGER DEFAULT 1 COMMENT '状态: 0=禁用, 1=启用',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_epc_enterprise ON enterprise_project_case(enterprise_id);
CREATE INDEX idx_epc_type ON enterprise_project_case(project_type);
CREATE INDEX idx_epc_industry ON enterprise_project_case(industry);
CREATE INDEX idx_epc_status ON enterprise_project_case(project_status);
CREATE INDEX idx_epc_deleted ON enterprise_project_case(deleted);

-- =============================================
-- 17. 团队成员表 (enterprise_team_member) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS enterprise_team_member (
    id              BIGINT PRIMARY KEY,
    enterprise_id   BIGINT NOT NULL COMMENT '企业ID',
    name            VARCHAR(50) NOT NULL COMMENT '成员姓名',
    position        VARCHAR(100) COMMENT '职位/职称',
    department      VARCHAR(100) COMMENT '部门',
    education       VARCHAR(50) COMMENT '学历',
    experience_years INTEGER COMMENT '从业年限',
    major           VARCHAR(100) COMMENT '专业',
    certificate_no  VARCHAR(100) COMMENT '证书编号',
    is_leader       INTEGER DEFAULT 0 COMMENT '是否核心负责人: 0=否, 1=是',
    avatar_path     VARCHAR(500) COMMENT '头像路径',
    phone           VARCHAR(20) COMMENT '联系电话',
    email           VARCHAR(100) COMMENT '邮箱',
    bio             TEXT COMMENT '个人简介',
    achievements    TEXT COMMENT '主要业绩/成就',
    sort            INTEGER DEFAULT 0 COMMENT '排序',
    status          INTEGER DEFAULT 1 COMMENT '状态: 0=禁用, 1=启用',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_etm_enterprise ON enterprise_team_member(enterprise_id);
CREATE INDEX idx_etm_position ON enterprise_team_member(position);
CREATE INDEX idx_etm_deleted ON enterprise_team_member(deleted);

-- =============================================
-- 18. 素材库表 (material_library) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS material_library (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) NOT NULL COMMENT '素材名称',
    type            VARCHAR(50) NOT NULL COMMENT '素材类型: IMAGE/DOCUMENT/VIDEO/AUDIO/TEMPLATE',
    category        VARCHAR(100) COMMENT '素材分类',
    sub_category    VARCHAR(100) COMMENT '子分类',
    tags            VARCHAR(500) COMMENT '标签(JSON数组)',
    description     VARCHAR(500) COMMENT '素材描述',
    file_path       VARCHAR(500) COMMENT '文件存储路径',
    file_url        VARCHAR(500) COMMENT '文件访问URL',
    file_size       BIGINT COMMENT '文件大小(字节)',
    file_type       VARCHAR(50) COMMENT '文件MIME类型',
    file_hash       VARCHAR(64) COMMENT '文件哈希(SHA256)',
    width           INTEGER COMMENT '图片/视频宽度',
    height          INTEGER COMMENT '图片/视频高度',
    duration        INTEGER COMMENT '视频/音频时长(秒)',
    thumbnail_path  VARCHAR(500) COMMENT '缩略图路径',
    ai_generated    INTEGER DEFAULT 0 COMMENT '是否AI生成: 0=否, 1=是',
    ai_prompt       VARCHAR(500) COMMENT 'AI生成提示词',
    copyright_status VARCHAR(20) DEFAULT 'UNKNOWN' COMMENT '版权状态: UNKNOWN/OWNED/LICENSED/THIRD_PARTY/COPYRIGHTED',
    copyright_remark VARCHAR(500) COMMENT '版权备注',
    source          VARCHAR(100) COMMENT '素材来源',
    usage_count     INTEGER DEFAULT 0 COMMENT '使用次数',
    favorite_count  INTEGER DEFAULT 0 COMMENT '收藏次数',
    project_id      BIGINT COMMENT '关联项目ID(可选)',
    upload_user_id   BIGINT COMMENT '上传用户ID',
    status          VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE/ARCHIVED/HIDDEN',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_ml_type ON material_library(type);
CREATE INDEX idx_ml_category ON material_library(category);
CREATE INDEX idx_ml_status ON material_library(status);
CREATE INDEX idx_ml_deleted ON material_library(deleted);
CREATE INDEX idx_ml_project ON material_library(project_id);
CREATE INDEX idx_ml_tags ON material_library USING gin(tags jsonb_path_ops);

-- =============================================
-- 19. 素材使用记录表 (material_usage_log) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS material_usage_log (
    id              BIGINT PRIMARY KEY,
    material_id     BIGINT NOT NULL COMMENT '素材ID',
    user_id         BIGINT COMMENT '使用用户ID',
    usage_type      VARCHAR(50) COMMENT '使用类型: DOWNLOAD/VIEW/EMBED/CITE',
    usage_context   VARCHAR(200) COMMENT '使用场景/文档名',
    usage_project_id BIGINT COMMENT '使用项目ID',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mul_material ON material_usage_log(material_id);
CREATE INDEX idx_mul_user ON material_usage_log(user_id);
CREATE INDEX idx_mul_project ON material_usage_log(usage_project_id);
CREATE INDEX idx_mul_create_time ON material_usage_log(create_time);

-- =============================================
-- 20. 私人图库表 (private_image_library) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS private_image_library (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(200) COMMENT '图片名称',
    description     VARCHAR(500) COMMENT '图片描述',
    tags            VARCHAR(500) COMMENT '标签(JSON数组)',
    file_path       VARCHAR(500) COMMENT '文件存储路径',
    file_url        VARCHAR(500) COMMENT '文件访问URL',
    file_size       BIGINT COMMENT '文件大小(字节)',
    width           INTEGER COMMENT '图片宽度',
    height          INTEGER COMMENT '图片高度',
    thumbnail_path  VARCHAR(500) COMMENT '缩略图路径',
    ai_generated    INTEGER DEFAULT 0 COMMENT '是否AI生成',
    ai_model        VARCHAR(100) COMMENT 'AI模型名称',
    ai_prompt       TEXT COMMENT 'AI生成提示词',
    ai_negative_prompt TEXT COMMENT 'AI负面提示词',
    copyright_status VARCHAR(20) DEFAULT 'OWNED' COMMENT '版权状态',
    copyright_remark VARCHAR(500) COMMENT '版权备注',
    source_url      VARCHAR(500) COMMENT '图片来源URL',
    detected_sources TEXT COMMENT '检测到的相似图片来源(JSON)',
    detection_score DECIMAL(5,4) COMMENT '版权检测相似度分数',
    detection_result VARCHAR(20) COMMENT '检测结果: CLEAN/SUSPICIOUS/COPYRIGHTED',
    usage_count     INTEGER DEFAULT 0 COMMENT '使用次数',
    upload_user_id   BIGINT COMMENT '上传用户ID',
    album_id        BIGINT COMMENT '所属相册ID',
    status          VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_pil_user ON private_image_library(upload_user_id);
CREATE INDEX idx_pil_album ON private_image_library(album_id);
CREATE INDEX idx_pil_deleted ON private_image_library(deleted);

-- =============================================
-- 21. 私人图库相册表 (private_image_album) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS private_image_album (
    id              BIGINT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL COMMENT '相册名称',
    description     VARCHAR(500) COMMENT '相册描述',
    cover_image_id  BIGINT COMMENT '封面图片ID',
    image_count     INTEGER DEFAULT 0 COMMENT '图片数量',
    upload_user_id   BIGINT COMMENT '用户ID',
    sort            INTEGER DEFAULT 0 COMMENT '排序',
    status          INTEGER DEFAULT 1 COMMENT '状态',
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by       BIGINT,
    update_by       BIGINT,
    version         INTEGER DEFAULT 0,
    deleted         INTEGER DEFAULT 0
);

CREATE INDEX idx_pia_user ON private_image_album(upload_user_id);
CREATE INDEX idx_pia_deleted ON private_image_album(deleted);

-- =============================================
-- 19. 资信标资质表 (bid_qualification) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS bid_qualification (
    id                  BIGINT PRIMARY KEY,
    name                VARCHAR(200) NOT NULL COMMENT '资质名称',
    type                VARCHAR(50) COMMENT '资质类型: 施工/设计/监理/勘察等',
    level               VARCHAR(20) COMMENT '资质等级: 特级/一级/二级/三级',
    certificate_no      VARCHAR(100) COMMENT '资质编号',
    valid_from          DATE COMMENT '资质有效期起始',
    valid_until         DATE COMMENT '资质有效期截止',
    issuing_authority   VARCHAR(200) COMMENT '颁发机构',
    certificate_image  VARCHAR(500) COMMENT '证书图片路径',
    project_id         BIGINT COMMENT '关联项目ID',
    enterprise_id      BIGINT COMMENT '关联企业ID',
    status              VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '资质状态: ACTIVE/EXPIRED/REVOKED',
    remark              VARCHAR(500) COMMENT '备注',
    create_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by           BIGINT,
    update_by           BIGINT,
    version             INTEGER DEFAULT 0,
    deleted             INTEGER DEFAULT 0
);

CREATE INDEX idx_bq_type ON bid_qualification(type);
CREATE INDEX idx_bq_level ON bid_qualification(level);
CREATE INDEX idx_bq_enterprise ON bid_qualification(enterprise_id);
CREATE INDEX idx_bq_project ON bid_qualification(project_id);
CREATE INDEX idx_bq_status ON bid_qualification(status);
CREATE INDEX idx_bq_valid_until ON bid_qualification(valid_until);
CREATE INDEX idx_bq_deleted ON bid_qualification(deleted);

-- =============================================
-- 20. 资信标企业信息表 (bid_enterprise_info) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS bid_enterprise_info (
    id                      BIGINT PRIMARY KEY,
    name                    VARCHAR(200) NOT NULL COMMENT '企业名称',
    unified_credit_code     VARCHAR(50) COMMENT '统一社会信用代码',
    type                    VARCHAR(50) COMMENT '企业类型: 国有/民营/外资等',
    industry                VARCHAR(50) COMMENT '所属行业',
    registered_capital     DECIMAL(15,2) COMMENT '注册资本(万元)',
    paid_in_capital         DECIMAL(15,2) COMMENT '实缴资本(万元)',
    established_date        DATE COMMENT '成立日期',
    business_from          DATE COMMENT '营业期限起始',
    business_until         DATE COMMENT '营业期限截止',
    legal_person           VARCHAR(50) COMMENT '法定代表人',
    contact_phone          VARCHAR(20) COMMENT '联系电话',
    address                VARCHAR(300) COMMENT '联系地址',
    business_license_image  VARCHAR(500) COMMENT '营业执照图片路径',
    description            TEXT COMMENT '企业简介',
    qualification_count    INTEGER DEFAULT 0 COMMENT '资质总数',
    status                  VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '企业状态: ACTIVE/SUSPENDED/REVOKED',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by              BIGINT,
    update_by              BIGINT,
    version                INTEGER DEFAULT 0,
    deleted                INTEGER DEFAULT 0
);

CREATE INDEX idx_bei_credit_code ON bid_enterprise_info(unified_credit_code);
CREATE INDEX idx_bei_type ON bid_enterprise_info(type);
CREATE INDEX idx_bei_status ON bid_enterprise_info(status);
CREATE INDEX idx_bei_deleted ON bid_enterprise_info(deleted);

-- =============================================
-- 21. 资信标业绩案例表 (bid_project_experience) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS bid_project_experience (
    id                      BIGINT PRIMARY KEY,
    project_name            VARCHAR(200) NOT NULL COMMENT '项目名称',
    project_type            VARCHAR(50) COMMENT '项目类型',
    scale                   VARCHAR(20) COMMENT '项目规模: 大型/中型/小型',
    bid_amount              DECIMAL(15,2) COMMENT '中标金额(万元)',
    bid_date                DATE COMMENT '中标日期',
    contract_duration       INTEGER COMMENT '合同工期(天)',
    actual_completion_date  DATE COMMENT '实际完工日期',
    client                 VARCHAR(200) COMMENT '甲方单位',
    client_contact         VARCHAR(50) COMMENT '甲方联系人',
    client_phone           VARCHAR(20) COMMENT '甲方联系电话',
    location               VARCHAR(300) COMMENT '项目地址',
    description            TEXT COMMENT '项目描述',
    contract_file          VARCHAR(500) COMMENT '合同文件路径',
    acceptance_file        VARCHAR(500) COMMENT '验收文件路径',
    quality_rating         VARCHAR(20) COMMENT '项目质量评级: 优良/合格',
    is_archived            INTEGER DEFAULT 0 COMMENT '是否入库: 0=否, 1=是',
    enterprise_id          BIGINT COMMENT '关联企业ID',
    bid_project_id         BIGINT COMMENT '关联投标项目ID',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by              BIGINT,
    update_by              BIGINT,
    version                INTEGER DEFAULT 0,
    deleted                INTEGER DEFAULT 0
);

CREATE INDEX idx_bpe_enterprise ON bid_project_experience(enterprise_id);
CREATE INDEX idx_bpe_bid_project ON bid_project_experience(bid_project_id);
CREATE INDEX idx_bpe_scale ON bid_project_experience(scale);
CREATE INDEX idx_bpe_archived ON bid_project_experience(is_archived);
CREATE INDEX idx_bpe_deleted ON bid_project_experience(deleted);

-- =============================================
-- 22. 资信标财务数据表 (bid_financial_data) - Phase 3
-- =============================================
CREATE TABLE IF NOT EXISTS bid_financial_data (
    id                      BIGINT PRIMARY KEY,
    year                    INTEGER NOT NULL COMMENT '报表年份',
    report_type             VARCHAR(20) COMMENT '报表类型: 年报/季报/中期',
    total_assets            DECIMAL(15,2) COMMENT '总资产(万元)',
    net_assets             DECIMAL(15,2) COMMENT '净资产(万元)',
    fixed_assets            DECIMAL(15,2) COMMENT '固定资产(万元)',
    current_assets         DECIMAL(15,2) COMMENT '流动资产(万元)',
    total_liabilities      DECIMAL(15,2) COMMENT '总负债(万元)',
    current_liabilities    DECIMAL(15,2) COMMENT '流动负债(万元)',
    main_business_income   DECIMAL(15,2) COMMENT '主营业务收入(万元)',
    net_profit             DECIMAL(15,2) COMMENT '净利润(万元)',
    roe                    DECIMAL(5,2) COMMENT '净资产收益率(%)',
    asset_liability_ratio  DECIMAL(5,2) COMMENT '资产负债率(%)',
    current_ratio           DECIMAL(5,2) COMMENT '流动比率',
    quick_ratio            DECIMAL(5,2) COMMENT '速动比率',
    turnover               DECIMAL(15,2) COMMENT '营业额(万元)',
    auditor                VARCHAR(100) COMMENT '审计机构',
    audit_opinion          VARCHAR(20) COMMENT '审计意见: 无保留/保留/否定',
    financial_statements   VARCHAR(500) COMMENT '财务报表图片路径(JSON数组)',
    enterprise_id          BIGINT COMMENT '关联企业ID',
    remark                 VARCHAR(500) COMMENT '备注',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by              BIGINT,
    update_by              BIGINT,
    version                INTEGER DEFAULT 0,
    deleted                INTEGER DEFAULT 0
);

CREATE INDEX idx_bfd_enterprise ON bid_financial_data(enterprise_id);
CREATE INDEX idx_bfd_year ON bid_financial_data(year);
CREATE INDEX idx_bfd_deleted ON bid_financial_data(deleted);

-- =============================================
-- 23. 工作流定义表 (camunda_bpm_workflow_definition) - Phase 4
-- =============================================
CREATE TABLE IF NOT EXISTS camunda_bpm_workflow_definition (
    id                      BIGINT PRIMARY KEY,
    name                    VARCHAR(200) NOT NULL COMMENT '流程名称',
    process_key             VARCHAR(100) NOT NULL UNIQUE COMMENT '流程定义Key',
    process_type            VARCHAR(50) COMMENT '流程类型: TECHNICAL_BID/CREDIT_BID',
    version                 INTEGER DEFAULT 1 COMMENT '版本号',
    description             VARCHAR(500) COMMENT '流程描述',
    bpmn_resource_path      VARCHAR(255) COMMENT 'BPMN资源路径',
    is_active               INTEGER DEFAULT 1 COMMENT '是否激活: 0=停用, 1=激活',
    status                  VARCHAR(20) DEFAULT 'DRAFT' COMMENT '状态: DRAFT/PUBLISHED/SUSPENDED',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by               BIGINT,
    update_by               BIGINT,
    version_lock            INTEGER DEFAULT 0,
    deleted                 INTEGER DEFAULT 0
);

CREATE INDEX idx_wd_process_key ON camunda_bpm_workflow_definition(process_key);
CREATE INDEX idx_wd_type ON camunda_bpm_workflow_definition(process_type);
CREATE INDEX idx_wd_active ON camunda_bpm_workflow_definition(is_active);
CREATE INDEX idx_wd_deleted ON camunda_bpm_workflow_definition(deleted);

-- =============================================
-- 24. 工作流实例表 (camunda_bpm_workflow_instance) - Phase 4
-- =============================================
CREATE TABLE IF NOT EXISTS camunda_bpm_workflow_instance (
    id                      BIGINT PRIMARY KEY,
    process_instance_id     VARCHAR(100) COMMENT 'Camunda流程实例ID',
    workflow_definition_id  BIGINT COMMENT '工作流定义ID',
    process_key             VARCHAR(100) COMMENT '流程定义Key',
    project_id              BIGINT COMMENT '关联投标项目ID',
    enterprise_id           BIGINT COMMENT '关联企业ID',
    business_key            VARCHAR(200) COMMENT '业务Key(项目ID)',
    start_user_id           BIGINT COMMENT '发起人ID',
    current_task_id         VARCHAR(100) COMMENT '当前任务ID',
    current_task_name       VARCHAR(200) COMMENT '当前任务名称',
    status                  VARCHAR(20) DEFAULT 'RUNNING' COMMENT '状态: RUNNING/COMPLETED/ABORTED/CANCELLED',
    start_time              TIMESTAMP COMMENT '开始时间',
    end_time                TIMESTAMP COMMENT '结束时间',
    duration                BIGINT COMMENT '持续时长(毫秒)',
    result_data             TEXT COMMENT '结果数据(JSON)',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by               BIGINT,
    update_by               BIGINT,
    version_lock            INTEGER DEFAULT 0,
    deleted                 INTEGER DEFAULT 0
);

CREATE INDEX idx_wi_process_instance ON camunda_bpm_workflow_instance(process_instance_id);
CREATE INDEX idx_wi_definition ON camunda_bpm_workflow_instance(workflow_definition_id);
CREATE INDEX idx_wi_project ON camunda_bpm_workflow_instance(project_id);
CREATE INDEX idx_wi_business_key ON camunda_bpm_workflow_instance(business_key);
CREATE INDEX idx_wi_status ON camunda_bpm_workflow_instance(status);
CREATE INDEX idx_wi_deleted ON camunda_bpm_workflow_instance(deleted);

-- =============================================
-- 25. 工作流任务记录表 (camunda_bpm_workflow_task) - Phase 4
-- =============================================
CREATE TABLE IF NOT EXISTS camunda_bpm_workflow_task (
    id                      BIGINT PRIMARY KEY,
    workflow_instance_id    BIGINT COMMENT '工作流实例ID',
    task_id                 VARCHAR(100) NOT NULL COMMENT 'Camunda任务ID',
    task_name               VARCHAR(200) COMMENT '任务名称',
    task_key                VARCHAR(100) COMMENT '任务定义Key',
    assignee                VARCHAR(100) COMMENT '办理人',
    candidate_users         VARCHAR(500) COMMENT '候选用户(JSON数组)',
    candidate_groups       VARCHAR(500) COMMENT '候选组(JSON数组)',
    priority                INTEGER DEFAULT 50 COMMENT '优先级',
    due_date                TIMESTAMP COMMENT '到期时间',
    description             VARCHAR(500) COMMENT '任务描述',
    variables               TEXT COMMENT '流程变量(JSON)',
    status                  VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态: PENDING/COMPLETED/ABORTED',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    complete_time           TIMESTAMP COMMENT '完成时间',
    create_by               BIGINT,
    update_by               BIGINT,
    version_lock            INTEGER DEFAULT 0,
    deleted                 INTEGER DEFAULT 0
);

CREATE INDEX idx_wt_instance ON camunda_bpm_workflow_task(workflow_instance_id);
CREATE INDEX idx_wt_task_id ON camunda_bpm_workflow_task(task_id);
CREATE INDEX idx_wt_assignee ON camunda_bpm_workflow_task(assignee);
CREATE INDEX idx_wt_status ON camunda_bpm_workflow_task(status);
CREATE INDEX idx_wt_deleted ON camunda_bpm_workflow_task(deleted);

-- =============================================
-- 26. 模型配置表 (gateway_model_config) - Phase 4
-- =============================================
CREATE TABLE IF NOT EXISTS gateway_model_config (
    id                      BIGINT PRIMARY KEY,
    name                    VARCHAR(100) NOT NULL COMMENT '模型名称',
    model_key               VARCHAR(100) NOT NULL COMMENT '模型标识',
    provider                VARCHAR(50) NOT NULL COMMENT '提供商: openai/anthropic/local',
    endpoint                VARCHAR(500) COMMENT 'API端点',
    api_key                 VARCHAR(255) COMMENT 'API密钥',
    version                 VARCHAR(50) COMMENT '模型版本',
    max_tokens              INTEGER DEFAULT 4096 COMMENT '最大Token数',
    temperature             DECIMAL(3,2) DEFAULT 0.7 COMMENT '温度参数',
    cost_per_token          DECIMAL(10,6) DEFAULT 0 COMMENT '调用费用/千Token',
    task_types              VARCHAR(255) COMMENT '支持的任务类型(逗号分隔)',
    is_default              INTEGER DEFAULT 0 COMMENT '是否默认模型: 0=否, 1=是',
    status                  INTEGER DEFAULT 1 COMMENT '状态: 0=禁用, 1=启用',
    priority                INTEGER DEFAULT 0 COMMENT '优先级',
    failure_count           INTEGER DEFAULT 0 COMMENT '连续失败次数',
    last_call_time          TIMESTAMP COMMENT '最后调用时间',
    remark                  VARCHAR(500) COMMENT '备注',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by               BIGINT,
    update_by               BIGINT,
    version_lock            INTEGER DEFAULT 0,
    deleted                 INTEGER DEFAULT 0
);

CREATE INDEX idx_gmc_model_key ON gateway_model_config(model_key);
CREATE INDEX idx_gmc_provider ON gateway_model_config(provider);
CREATE INDEX idx_gmc_status ON gateway_model_config(status);
CREATE INDEX idx_gmc_is_default ON gateway_model_config(is_default);
CREATE INDEX idx_gmc_deleted ON gateway_model_config(deleted);

-- =============================================
-- 27. 模型使用日志表 (gateway_model_usage_log) - Phase 4
-- =============================================
CREATE TABLE IF NOT EXISTS gateway_model_usage_log (
    id                      BIGINT PRIMARY KEY,
    model_id                BIGINT NOT NULL COMMENT '模型ID',
    model_name              VARCHAR(100) COMMENT '模型名称',
    request_type            VARCHAR(50) COMMENT '请求类型',
    call_count              INTEGER DEFAULT 1 COMMENT '调用次数',
    input_tokens            BIGINT DEFAULT 0 COMMENT '输入Token数',
    output_tokens           BIGINT DEFAULT 0 COMMENT '输出Token数',
    total_tokens            BIGINT DEFAULT 0 COMMENT '总Token数',
    success_count           INTEGER DEFAULT 0 COMMENT '成功次数',
    failure_count           INTEGER DEFAULT 0 COMMENT '失败次数',
    avg_response_time       BIGINT DEFAULT 0 COMMENT '平均响应时间(毫秒)',
    max_response_time       BIGINT DEFAULT 0 COMMENT '最大响应时间(毫秒)',
    min_response_time       BIGINT DEFAULT 0 COMMENT '最小响应时间(毫秒)',
    total_cost              DECIMAL(15,6) DEFAULT 0 COMMENT '总费用',
    call_date               DATE COMMENT '调用日期',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted                 INTEGER DEFAULT 0
);

CREATE INDEX idx_gmul_model_id ON gateway_model_usage_log(model_id);
CREATE INDEX idx_gmul_call_date ON gateway_model_usage_log(call_date);
CREATE INDEX idx_gmul_request_type ON gateway_model_usage_log(request_type);
CREATE INDEX idx_gmul_deleted ON gateway_model_usage_log(deleted);

-- =============================================
-- 28. 模型切换规则表 (gateway_model_switch_rule) - Phase 4
-- =============================================
CREATE TABLE IF NOT EXISTS gateway_model_switch_rule (
    id                      BIGINT PRIMARY KEY,
    name                    VARCHAR(100) NOT NULL COMMENT '规则名称',
    rule_type               VARCHAR(50) NOT NULL COMMENT '规则类型: load_balance/cost_optimize/quality_priority/failover',
    threshold               DECIMAL(10,2) COMMENT '触发阈值',
    metric_type             VARCHAR(50) COMMENT '指标类型: latency/error_rate/cost',
    source_model_id         BIGINT COMMENT '源模型ID',
    target_model_id         BIGINT COMMENT '目标模型ID',
    enabled                 INTEGER DEFAULT 1 COMMENT '是否启用: 0=禁用, 1=启用',
    priority                INTEGER DEFAULT 0 COMMENT '优先级',
    cooldown_seconds        INTEGER DEFAULT 60 COMMENT '冷却时间(秒)',
    last_trigger_time       TIMESTAMP COMMENT '上次触发时间',
    trigger_count           INTEGER DEFAULT 0 COMMENT '触发次数',
    remark                  VARCHAR(500) COMMENT '备注',
    create_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by               BIGINT,
    update_by               BIGINT,
    version_lock            INTEGER DEFAULT 0,
    deleted                 INTEGER DEFAULT 0
);

CREATE INDEX idx_gmsr_rule_type ON gateway_model_switch_rule(rule_type);
CREATE INDEX idx_gmsr_enabled ON gateway_model_switch_rule(enabled);
CREATE INDEX idx_gmsr_source_model ON gateway_model_switch_rule(source_model_id);
CREATE INDEX idx_gmsr_target_model ON gateway_model_switch_rule(target_model_id);
CREATE INDEX idx_gmsr_deleted ON gateway_model_switch_rule(deleted);