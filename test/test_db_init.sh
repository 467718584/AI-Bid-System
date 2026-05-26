#!/bin/bash
#============================================
# AI智能投标系统 - 数据库初始化验证脚本
# AI Bid System - Database Initialization Verification
#============================================
# 用法: ./test_db_init.sh [选项]
#   -h, --help       显示帮助
#   -H, --host       数据库主机 (默认: localhost)
#   -p, --port       数据库端口 (默认: 5432)
#   -u, --user       数据库用户 (默认: postgres)
#   -d, --database   数据库名 (默认: aidbid)
#   --skip-tables    跳过表结构检查
#   --skip-seed      跳过种子数据检查
#============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 默认配置
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-aidbid}"
DB_PASSWORD="${DB_PASSWORD:-}"

# 选项
SKIP_TABLES=false
SKIP_SEED=false

#============================================
# 工具函数
#============================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 构建psql命令
get_psql_cmd() {
    local cmd="psql"
    if [ -n "$DB_HOST" ]; then
        cmd="$cmd -h $DB_HOST"
    fi
    if [ -n "$DB_PORT" ]; then
        cmd="$cmd -p $DB_PORT"
    fi
    if [ -n "$DB_USER" ]; then
        cmd="$cmd -U $DB_USER"
    fi
    if [ -n "$DB_PASSWORD" ]; then
        cmd="PGPASSWORD=$DB_PASSWORD $cmd"
    fi
    if [ -n "$DB_NAME" ]; then
        cmd="$cmd -d $DB_NAME"
    fi
    echo "$cmd"
}

# 检查数据库连接
check_connection() {
    log_info "检查数据库连接..."
    local psql_cmd=$(get_psql_cmd)

    if $psql_cmd -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "数据库连接成功 ($DB_HOST:$DB_PORT/$DB_NAME)"
        return 0
    else
        log_error "数据库连接失败"
        log_error "请检查数据库是否运行，或使用 -H/-p/-u/-d 参数指定正确的连接信息"
        return 1
    fi
}

# 检查表是否存在
check_table() {
    local table_name=$1
    local psql_cmd=$(get_psql_cmd)

    if $psql_cmd -t -c "SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name='$table_name');" 2>/dev/null | grep -q "t"; then
        return 0
    else
        return 1
    fi
}

# 获取表行数
get_table_count() {
    local table_name=$1
    local psql_cmd=$(get_psql_cmd)
    $psql_cmd -t -c "SELECT COUNT(*) FROM $table_name;" 2>/dev/null | tr -d ' '
}

#============================================
# 核心表检查
#============================================

test_core_tables() {
    log_info "=== 核心表结构检查 ==="

    local core_tables=(
        "sys_user"
        "sys_role"
        "sys_user_role"
        "sys_permission"
        "sys_role_permission"
        "bid_project"
        "bid_material"
        "bid_document"
        "bid_template"
        "ai_task"
        "sys_operation_log"
    )

    local all_exists=true
    for table in "${core_tables[@]}"; do
        if check_table "$table"; then
            local count=$(get_table_count "$table")
            log_success "[$table] 存在, 行数: $count"
        else
            log_error "[$table] 不存在"
            all_exists=false
        fi
    done

    if [ "$all_exists" = true ]; then
        return 0
    else
        return 1
    fi
}

#============================================
# 知识库表检查 (Phase 2)
#============================================

test_knowledge_tables() {
    log_info "=== 知识库表检查 (Phase 2) ==="

    local kb_tables=(
        "kb_knowledge_base"
        "kb_chunk"
    )

    local all_exists=true
    for table in "${kb_tables[@]}"; do
        if check_table "$table"; then
            local count=$(get_table_count "$table")
            log_success "[$table] 存在, 行数: $count"
        else
            log_error "[$table] 不存在"
            all_exists=false
        fi
    done

    # 检查向量扩展
    local psql_cmd=$(get_psql_cmd)
    if $psql_cmd -t -c "SELECT 1 FROM pg_extension WHERE extname='vector';" 2>/dev/null | grep -q "1"; then
        log_success "[pgvector] 扩展已安装"
    else
        log_warn "[pgvector] 扩展未安装 (可选，用于向量检索)"
    fi

    if [ "$all_exists" = true ]; then
        return 0
    else
        return 1
    fi
}

#============================================
# 企业资料表检查 (Phase 3)
#============================================

test_enterprise_tables() {
    log_info "=== 企业资料表检查 (Phase 3) ==="

    local enterprise_tables=(
        "enterprise_profile"
        "enterprise_certificate"
        "enterprise_project_case"
        "enterprise_team_member"
        "material_library"
        "material_usage_log"
        "private_image_library"
        "private_image_album"
        "bid_qualification"
        "bid_enterprise_info"
        "bid_project_experience"
        "bid_financial_data"
    )

    local all_exists=true
    for table in "${enterprise_tables[@]}"; do
        if check_table "$table"; then
            local count=$(get_table_count "$table")
            log_success "[$table] 存在, 行数: $count"
        else
            log_error "[$table] 不存在"
            all_exists=false
        fi
    done

    if [ "$all_exists" = true ]; then
        return 0
    else
        return 1
    fi
}

#============================================
# 工作流表检查 (Phase 4)
#============================================

test_workflow_tables() {
    log_info "=== 工作流表检查 (Phase 4) ==="

    local workflow_tables=(
        "camunda_bpm_workflow_definition"
        "camunda_bpm_workflow_instance"
        "camunda_bpm_workflow_task"
        "gateway_model_config"
        "gateway_model_usage_log"
        "gateway_model_switch_rule"
    )

    local all_exists=true
    for table in "${workflow_tables[@]}"; do
        if check_table "$table"; then
            local count=$(get_table_count "$table")
            log_success "[$table] 存在, 行数: $count"
        else
            log_error "[$table] 不存在"
            all_exists=false
        fi
    done

    if [ "$all_exists" = true ]; then
        return 0
    else
        return 1
    fi
}

#============================================
# 种子数据检查
#============================================

test_seed_data() {
    log_info "=== 种子数据检查 ==="

    local psql_cmd=$(get_psql_cmd)

    # 检查管理员用户
    local admin_exists=$($psql_cmd -t -c "SELECT COUNT(*) FROM sys_user WHERE username='admin';" 2>/dev/null | tr -d ' ')
    if [ "$admin_exists" -gt 0 ]; then
        log_success "[sys_user] admin用户存在"
    else
        log_warn "[sys_user] admin用户不存在"
    fi

    # 检查默认角色
    local role_count=$($psql_cmd -t -c "SELECT COUNT(*) FROM sys_role;" 2>/dev/null | tr -d ' ')
    if [ "$role_count" -gt 0 ]; then
        log_success "[sys_role] 角色数据存在, 共 $role_count 条"
    else
        log_warn "[sys_role] 无角色数据"
    fi

    # 检查权限数据
    local perm_count=$($psql_cmd -t -c "SELECT COUNT(*) FROM sys_permission;" 2>/dev/null | tr -d ' ')
    if [ "$perm_count" -gt 0 ]; then
        log_success "[sys_permission] 权限数据存在, 共 $perm_count 条"
    else
        log_warn "[sys_permission] 无权限数据"
    fi

    # 检查模板数据
    local template_count=$($psql_cmd -t -c "SELECT COUNT(*) FROM bid_template;" 2>/dev/null | tr -d ' ')
    if [ "$template_count" -gt 0 ]; then
        log_success "[bid_template] 模板数据存在, 共 $template_count 条"
    else
        log_warn "[bid_template] 无模板数据"
    fi

    return 0
}

#============================================
# 数据库统计信息
#============================================

show_db_stats() {
    log_info "=== 数据库统计 ==="

    local psql_cmd=$(get_psql_cmd)

    # 表数量
    local table_count=$($psql_cmd -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" 2>/dev/null | tr -d ' ')
    log_info "数据库表数量: $table_count"

    # 序列数量
    local sequence_count=$($psql_cmd -t -c "SELECT COUNT(*) FROM information_schema.sequences WHERE sequence_schema='public';" 2>/dev/null | tr -d ' ')
    log_info "序列数量: $sequence_count"

    # 索引数量
    local index_count=$($psql_cmd -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public';" 2>/dev/null | tr -d ' ')
    log_info "索引数量: $index_count"

    # 总行数估算
    log_info "各表行数统计:"
    $psql_cmd -c "SELECT table_name, pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS total_size, pg_total_relation_size(quote_ident(table_name)) AS size_bytes FROM information_schema.tables WHERE table_schema = 'public' AND table_type='BASE TABLE' ORDER BY size_bytes DESC LIMIT 10;" 2>/dev/null || true
}

#============================================
# 帮助信息
#============================================

show_help() {
    echo "AI智能投标系统 - 数据库初始化验证脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "连接选项:"
    echo "  -H, --host       数据库主机 (默认: localhost)"
    echo "  -p, --port       数据库端口 (默认: 5432)"
    echo "  -u, --user       数据库用户 (默认: postgres)"
    echo "  -d, --database   数据库名 (默认: aidbid)"
    echo ""
    echo "检查选项:"
    echo "  --skip-tables    跳过表结构检查"
    echo "  --skip-seed      跳过种子数据检查"
    echo "  -h, --help       显示帮助"
    echo ""
    echo "环境变量:"
    echo "  DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASSWORD"
    echo ""
    echo "示例:"
    echo "  $0                          # 使用默认配置检查"
    echo "  $0 -H localhost -u postgres # 指定主机和用户"
    echo "  DB_HOST=remote DB_NAME=test $0  # 使用环境变量"
}

#============================================
# 主函数
#============================================

main() {
    echo "=========================================="
    echo "  AI智能投标系统 - 数据库初始化验证"
    echo "=========================================="
    echo ""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -H|--host)
                DB_HOST="$2"
                shift 2
                ;;
            -p|--port)
                DB_PORT="$2"
                shift 2
                ;;
            -u|--user)
                DB_USER="$2"
                shift 2
                ;;
            -d|--database)
                DB_NAME="$2"
                shift 2
                ;;
            --skip-tables)
                SKIP_TABLES=true
                shift
                ;;
            --skip-seed)
                SKIP_SEED=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    log_info "连接信息: $DB_HOST:$DB_PORT/$DB_NAME (user: $DB_USER)"
    echo ""

    local failed=0

    # 1. 检查数据库连接
    check_connection || exit 1

    echo ""

    # 2. 核心表检查
    test_core_tables || ((failed++))

    echo ""

    # 3. 知识库表检查
    test_knowledge_tables || ((failed++))

    echo ""

    # 4. 企业资料表检查
    test_enterprise_tables || ((failed++))

    echo ""

    # 5. 工作流表检查
    test_workflow_tables || ((failed++))

    echo ""

    # 6. 种子数据检查
    if [ "$SKIP_SEED" = false ]; then
        test_seed_data || ((failed++))
        echo ""
    fi

    # 7. 统计信息
    show_db_stats

    echo ""
    echo "=========================================="
    if [ $failed -eq 0 ]; then
        log_success "数据库验证完成!"
    else
        log_error "数据库验证完成，$failed 项检查失败"
    fi
    echo "=========================================="

    return $failed
}

# 运行主函数
main "$@"