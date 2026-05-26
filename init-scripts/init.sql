-- =============================================
-- AI Bid System - Database Initialization
-- PostgreSQL 16 + pgvector Extension
-- =============================================

-- 启用pgvector扩展（用于AI向量存储）
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建数据库（如果不存在）
-- 注意：在docker-compose中通过POSTGRES_DB环境变量设置
-- CREATE DATABASE aidbid;