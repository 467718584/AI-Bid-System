-- =============================================
-- AI Bid System - Seed Data
-- Optional test data for development
-- =============================================

-- =============================================
-- 1. 默认用户
-- =============================================

-- 插入默认超级管理员用户 (密码: admin123, BCrypt加密)
INSERT INTO sys_user (id, username, password, nickname, email, status, create_time, update_time, deleted)
VALUES (1, 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH',
        '超级管理员', 'admin@aibid.com', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
ON CONFLICT (username) DO NOTHING;

-- 插入测试用户 (密码: test123)
INSERT INTO sys_user (id, username, password, nickname, email, status, create_time, update_time, deleted)
VALUES (2, 'testuser', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH',
        '测试用户', 'test@aibid.com', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
ON CONFLICT (username) DO NOTHING;

-- =============================================
-- 2. 默认角色
-- =============================================
INSERT INTO sys_role (id, role_name, role_code, description, status, create_time, deleted)
VALUES
    (1, '超级管理员', 'SUPER_ADMIN', '系统超级管理员，拥有所有权限', 0, CURRENT_TIMESTAMP, 0),
    (2, '普通用户', 'USER', '普通用户角色', 0, CURRENT_TIMESTAMP, 0),
    (3, '投标经理', 'BID_MANAGER', '投标项目管理员', 0, CURRENT_TIMESTAMP, 0)
ON CONFLICT (role_code) DO NOTHING;

-- =============================================
-- 3. 角色绑定
-- =============================================

-- 绑定超管用户角色
INSERT INTO sys_user_role (id, user_id, role_id, create_time)
VALUES (1, 1, 1, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- 绑定测试用户角色
INSERT INTO sys_user_role (id, user_id, role_id, create_time)
VALUES (2, 2, 2, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- =============================================
-- 4. 默认权限
-- =============================================
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
-- 5. 测试项目数据
-- =============================================
INSERT INTO bid_project (id, name, code, type, amount, tenderer, contact_person, contact_phone, status, description, create_time, deleted)
VALUES
    (1, '智慧城市数据平台建设项目', 'PRJ202605001', '信息化建设', 5000000.00, '某市政府信息中心', '张三', '13800138000', 'IN_PROGRESS', '建设智慧城市数据平台，实现数据汇聚、治理、分析', CURRENT_TIMESTAMP, 0),
    (2, '企业ERP系统采购项目', 'PRJ202605002', '软件开发', 2800000.00, '某某集团', '李四', '13900139000', 'DRAFT', '采购并实施企业ERP系统', CURRENT_TIMESTAMP, 0)
ON CONFLICT (code) DO NOTHING;

-- =============================================
-- 6. 测试标书模板
-- =============================================
INSERT INTO bid_template (id, name, code, category, content, is_default, status, create_time, deleted)
VALUES
    (1, '技术标通用模板', 'TECH_STANDARD', '技术标', '# 技术标\n\n## 一、公司简介\n\n## 二、项目理解\n\n## 三、技术方案\n\n## 四、实施计划\n\n## 五、售后服务', 1, 0, CURRENT_TIMESTAMP, 0)
ON CONFLICT (code) DO NOTHING;

-- =============================================
-- 完成
-- =============================================