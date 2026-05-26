-- =============================================
-- AI Bid System - 数据库修复脚本
-- 修复 P1 问题
-- =============================================

-- =============================================
-- 修复 1: 删除无效的GIN索引并创建正确的B-tree索引
-- material_library.tags 使用 VARCHAR 类型，GIN索引仅对JSONB有效
-- =============================================

-- 删除无效的GIN索引
DROP INDEX IF EXISTS idx_ml_tags_gin;

-- 检查当前索引类型并删除（如果存在其他命名方式）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'material_library'
        AND indexname = 'idx_ml_tags'
        AND indexdef LIKE '%gin%'
    ) THEN
        DROP INDEX IF EXISTS idx_ml_tags;
    END IF;
END $$;

-- 创建正确的B-tree索引（适用于VARCHAR类型）
-- B-tree索引支持 =, <, >, LIKE, ILIKE 等操作符
CREATE INDEX idx_ml_tags ON material_library USING btree (tags);

-- 如果需要支持JSON数组的包含查询（tags存储JSON数组如 '["标签1","标签2"]'）
-- 建议将tags列改为JSONB类型，然后可以使用GIN索引
-- ALTER TABLE material_library ALTER COLUMN tags TYPE JSONB USING tags::jsonb;
-- CREATE INDEX idx_ml_tags ON material_library USING gin (tags jsonb_path_ops);

-- =============================================
-- 说明
-- =============================================
-- GIN索引适用场景:
--   - JSONB类型列
--   - 数组类型列
--   - 全文搜索
--
-- B-tree索引适用场景:
--   - VARCHAR/TEXT类型列
--   - 等值查询
--   - 范围查询
--   - LIKE前缀匹配
--
-- 对于存储JSON字符串的VARCHAR列做标签查询，推荐:
-- 1. 改用JSONB类型 (推荐)
-- 2. 使用B-tree索引 + LIKE查询
-- =============================================