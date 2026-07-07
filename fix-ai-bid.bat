@echo off
chcp 65001 >nul
echo ================================================
echo AI-BID 系统修复脚本
echo ================================================

echo [1/5] 创建业务表...
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS bid_project (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, code VARCHAR(50) UNIQUE, type VARCHAR(50), amount DECIMAL(15,2), tenderer VARCHAR(200), contact_person VARCHAR(100), contact_phone VARCHAR(20), deadline TIMESTAMP, status VARCHAR(20) DEFAULT 'DRAFT', description TEXT, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS bid_material (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, type VARCHAR(50), project_id BIGINT, file_path VARCHAR(500), file_size BIGINT, file_type VARCHAR(50), upload_user_id BIGINT, status VARCHAR(20) DEFAULT 'PENDING', remark VARCHAR(500), create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS bid_document (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, type VARCHAR(50), project_id BIGINT, material_id BIGINT, file_path VARCHAR(500), file_size BIGINT, content TEXT, parse_status VARCHAR(20) DEFAULT 'PENDING', analysis_result TEXT, status VARCHAR(20) DEFAULT 'ACTIVE', create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS bid_template (id BIGINT PRIMARY KEY, name VARCHAR(200) NOT NULL, code VARCHAR(50) UNIQUE, category VARCHAR(50), content TEXT, file_path VARCHAR(500), is_default INTEGER DEFAULT 0, status INTEGER DEFAULT 0, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS ai_task (id BIGINT PRIMARY KEY, task_type VARCHAR(50) NOT NULL, target_type VARCHAR(50), target_id BIGINT, input_data TEXT, output_data TEXT, status VARCHAR(20) DEFAULT 'PENDING', error_message VARCHAR(500), start_time TIMESTAMP, end_time TIMESTAMP, cost_time BIGINT, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, create_by BIGINT, update_by BIGINT, version INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0);
"
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "
CREATE TABLE IF NOT EXISTS sys_operation_log (id BIGINT PRIMARY KEY, module VARCHAR(50), business_type VARCHAR(20), method VARCHAR(200), request_method VARCHAR(10), request_url VARCHAR(500), request_params TEXT, response_data TEXT, user_id BIGINT, username VARCHAR(50), ip VARCHAR(50), user_agent VARCHAR(500), cost_time BIGINT, status INTEGER DEFAULT 0, error_message VARCHAR(500), create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
"
echo [1/5] 完成

echo [2/5] 插入种子数据...
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "INSERT INTO sys_user (id, username, password, nickname, email, status, create_time, update_time, deleted) VALUES (1, 'admin', 'admin', '管理员', 'admin@aibid.com', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0) ON CONFLICT (username) DO NOTHING;"
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "INSERT INTO bid_project (id, name, code, type, amount, tenderer, status, description, create_time, update_time, deleted) VALUES (1, '智慧城市数据治理平台建设项目', 'BID-2024-001', '智慧城市', 5000000.00, '某市政府信息中心', 'IN_PROGRESS', '建设智慧城市数据治理平台，实现数据统一管理', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0) ON CONFLICT (code) DO NOTHING;"
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "INSERT INTO bid_template (id, name, code, category, content, is_default, status, create_time, deleted) VALUES (1, '智慧城市技术标模板', 'TECH-STANDARD', '技术标', '# 智慧城市技术标\n\n## 第一章 项目概述\n\n本章描述项目背景和目标...', 1, 0, CURRENT_TIMESTAMP, 0), (2, '商务标标准模板', 'BIZ-STANDARD', '商务标', '# 商务标\n\n## 第一章 投标函\n\n投标单位：\n\n投标日期：', 0, 0, CURRENT_TIMESTAMP, 0) ON CONFLICT (code) DO NOTHING;"
echo [2/5] 完成

echo [3/5] 修复 knowledge healthcheck...
powershell -NoProfile -Command "(Get-Content C:\ai-bid\docker-compose.yml -Raw) -replace 'test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8086/health\"]', 'test: [\"CMD-SHELL\", \"python -c \""import urllib.request;urllib.request.urlopen('\'http://localhost:8086/health\'')"\""]' | Set-Content C:\ai-bid\docker-compose.yml -Encoding UTF8"
echo [3/5] 完成

echo [4/5] 重启 knowledge 服务...
cd C:\ai-bid && docker-compose up -d --no-deps ai-bid-knowledge
echo [4/5] 完成

echo [5/5] 验证数据库表...
docker exec ai-bid-postgres psql -U postgres -d ai_bid -c "\dt"
echo [5/5] 完成

echo ================================================
echo 修复完成！
echo ================================================
