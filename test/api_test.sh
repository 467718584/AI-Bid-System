#!/bin/bash
#============================================
# AI智能投标系统 - API测试脚本
# AI Bid System - API Test Script
#============================================
# 用法: ./api_test.sh [选项]
#   -h, --help       显示帮助信息
#   -v, --verbose    详细输出模式
#   -s, --service    仅测试指定服务 (gateway|user|project|material|document|knowledge|ai)
#   --skip-auth      跳过需要认证的测试
#============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
GATEWAY_URL="http://localhost:8080"
USER_URL="http://localhost:8081"
PROJECT_URL="http://localhost:8082"
MATERIAL_URL="http://localhost:8083"
DOCUMENT_URL="http://localhost:8084"
KNOWLEDGE_URL="http://localhost:8086"
AI_URL="http://localhost:8087"

# 全局变量
TOKEN=""
VERBOSE=false
SKIP_AUTH=false
SERVICE_FILTER=""

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

# 发送请求并检查响应
# 参数: method url [data_file] [token]
request() {
    local method=$1
    local url=$2
    local data_file=$3
    local token=$4
    local extra_opts="${5:-}"

    local headers="-H 'Content-Type: application/json'"
    if [ -n "$token" ]; then
        headers="$headers -H 'Authorization: Bearer $token'"
    fi

    local cmd="curl -s -w '\nHTTP_STATUS:%{http_code}' -X $method '$url' $headers"

    if [ -n "$data_file" ] && [ -f "$data_file" ]; then
        cmd="$cmd -d @$data_file"
    elif [ -n "$data_file" ] && [ "$data_file" != "null" ]; then
        cmd="$cmd -d '$data_file'"
    fi

    if [ "$VERBOSE" = true ]; then
        echo "  CMD: $cmd"
    fi

    local response=$(eval $cmd 2>&1)
    local http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    local body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')

    if [ "$VERBOSE" = true ]; then
        echo "  Response: $body"
    fi

    echo "$http_code|$body"
}

# 检查服务是否运行
check_service() {
    local url=$1
    local name=$2

    if curl -s -f "$url" > /dev/null 2>&1; then
        log_success "$name is running"
        return 0
    else
        log_error "$name is NOT running at $url"
        return 1
    fi
}

# 解析响应
get_json_value() {
    local json=$1
    local key=$2
    echo "$json" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*[^,}]*" | sed 's/.*://' | tr -d '"' | tr -d ' '
}

#============================================
# 测试函数
#============================================

# 1. 健康检查测试
test_health_checks() {
    log_info "=== 健康检查测试 ==="

    local services=(
        "Gateway|$GATEWAY_URL/health"
        "User Service|$USER_URL/health"
        "Project Service|$PROJECT_URL/health"
        "Material Service|$MATERIAL_URL/health"
        "Document Service|$DOCUMENT_URL/health"
        "Knowledge Service|$KNOWLEDGE_URL/health"
        "AI Service|$AI_URL/health"
    )

    if [ -n "$SERVICE_FILTER" ]; then
        services=($(echo "${services[@]}" | tr ' ' '\n' | grep -i "$SERVICE_FILTER"))
    fi

    local all_passed=true
    for svc in "${services[@]}"; do
        local name="${svc%%|*}"
        local url="${svc##*|}"
        local result=$(request "GET" "$url" "" "")
        local http_code="${result%%|*}"
        if [ "$http_code" = "200" ]; then
            log_success "[$name] $url - OK"
        else
            log_error "[$name] $url - HTTP $http_code"
            all_passed=false
        fi
    done

    if [ "$all_passed" = true ]; then
        return 0
    else
        return 1
    fi
}

# 2. 认证接口测试
test_auth() {
    log_info "=== 认证接口测试 ==="

    # 登录测试
    log_info "测试用户登录..."
    local result=$(request "POST" "$GATEWAY_URL/api/auth/login" '{"username":"admin","password":"admin123"}' "")
    local http_code="${result%%|*}"
    local body="${result##*|}"

    if [ "$http_code" = "200" ]; then
        log_success "登录成功 (HTTP 200)"
        TOKEN=$(echo "$body" | grep -o '"token"[[:space:]]*:[[:space:]]*"[^"]*' | head -1 | sed 's/.*"://')
        [ "$VERBOSE" = true ] && log_info "Token: ${TOKEN:0:50}..."
    else
        log_error "登录失败 (HTTP $http_code)"
        [ "$VERBOSE" = true ] && log_info "Response: $body"
        return 1
    fi

    # Token刷新测试
    if [ -n "$TOKEN" ]; then
        log_info "测试Token刷新..."
        local refresh_result=$(request "POST" "$GATEWAY_URL/api/auth/refresh" "{\"refreshToken\":\"$TOKEN\"}" "")
        local refresh_code="${refresh_result%%|*}"
        if [ "$refresh_code" = "200" ]; then
            log_success "Token刷新成功"
        else
            log_warn "Token刷新失败 (HTTP $refresh_code) - 继续使用原Token"
        fi
    fi

    return 0
}

# 3. 用户管理接口测试
test_user_service() {
    if [ -n "$SERVICE_FILTER" ] && [ "$SERVICE_FILTER" != "user" ]; then
        return 0
    fi

    log_info "=== 用户管理接口测试 ==="

    # 获取用户列表
    log_info "获取用户列表..."
    local result=$(request "GET" "$USER_URL/api/users" "" "$TOKEN")
    local http_code="${result%%|*}"

    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        log_success "用户列表接口 (HTTP $http_code)"
    else
        log_error "用户列表接口失败 (HTTP $http_code)"
    fi

    # 获取角色列表
    log_info "获取角色列表..."
    local result=$(request "GET" "$USER_URL/api/roles" "" "$TOKEN")
    local http_code="${result%%|*}"

    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        log_success "角色列表接口 (HTTP $http_code)"
    else
        log_error "角色列表接口失败 (HTTP $http_code)"
    fi

    return 0
}

# 4. 项目管理接口测试
test_project_service() {
    if [ -n "$SERVICE_FILTER" ] && [ "$SERVICE_FILTER" != "project" ]; then
        return 0
    fi

    log_info "=== 项目管理接口测试 ==="

    # 获取项目列表
    log_info "获取项目列表..."
    local result=$(request "GET" "$PROJECT_URL/api/projects" "" "$TOKEN")
    local http_code="${result%%|*}"

    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        log_success "项目列表接口 (HTTP $http_code)"
    else
        log_error "项目列表接口失败 (HTTP $http_code)"
    fi

    # 创建项目测试
    log_info "测试创建项目..."
    local create_result=$(request "POST" "$PROJECT_URL/api/projects" \
        '{"projectName":"API测试项目","bidAmount":1000000,"projectType":"水利工程"}' "$TOKEN")
    local create_code="${create_result%%|*}"

    if [ "$create_code" = "200" ] || [ "$create_code" = "201" ] || [ "$create_code" = "401" ]; then
        log_success "创建项目接口 (HTTP $create_code)"
    else
        log_error "创建项目接口失败 (HTTP $create_code)"
    fi

    return 0
}

# 5. 素材库接口测试
test_material_service() {
    if [ -n "$SERVICE_FILTER" ] && [ "$SERVICE_FILTER" != "material" ]; then
        return 0
    fi

    log_info "=== 素材库接口测试 ==="

    # 获取素材分类树
    log_info "获取素材分类树..."
    local result=$(request "GET" "$MATERIAL_URL/api/materials/categories" "" "$TOKEN")
    local http_code="${result%%|*}"

    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        log_success "分类树接口 (HTTP $http_code)"
    else
        log_error "分类树接口失败 (HTTP $http_code)"
    fi

    # 获取素材列表
    log_info "获取素材列表..."
    local result=$(request "GET" "$MATERIAL_URL/api/materials" "" "$TOKEN")
    local http_code="${result%%|*}"

    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        log_success "素材列表接口 (HTTP $http_code)"
    else
        log_error "素材列表接口失败 (HTTP $http_code)"
    fi

    return 0
}

# 6. 文档管理接口测试
test_document_service() {
    if [ -n "$SERVICE_FILTER" ] && [ "$SERVICE_FILTER" != "document" ]; then
        return 0
    fi

    log_info "=== 文档管理接口测试 ==="

    # 获取文档列表
    log_info "获取文档列表..."
    local result=$(request "GET" "$DOCUMENT_URL/api/documents" "" "$TOKEN")
    local http_code="${result%%|*}"

    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        log_success "文档列表接口 (HTTP $http_code)"
    else
        log_error "文档列表接口失败 (HTTP $http_code)"
    fi

    return 0
}

# 7. 知识库接口测试
test_knowledge_service() {
    if [ -n "$SERVICE_FILTER" ] && [ "$SERVICE_FILTER" != "knowledge" ]; then
        return 0
    fi

    log_info "=== 知识库接口测试 ==="

    # 获取知识库列表
    log_info "获取知识库列表..."
    local result=$(request "GET" "$KNOWLEDGE_URL/api/knowledge/bases" "" "$TOKEN")
    local http_code="${result%%|*}"

    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        log_success "知识库列表接口 (HTTP $http_code)"
    else
        log_error "知识库列表接口失败 (HTTP $http_code)"
    fi

    # 检索测试
    log_info "测试向量检索..."
    local search_result=$(request "POST" "$KNOWLEDGE_URL/api/knowledge/bases/1/retrieve" \
        '{"query":"施工组织设计","topK":3}' "$TOKEN")
    local search_code="${search_result%%|*}"

    if [ "$search_code" = "200" ] || [ "$search_code" = "401" ]; then
        log_success "向量检索接口 (HTTP $search_code)"
    else
        log_error "向量检索接口失败 (HTTP $search_code)"
    fi

    return 0
}

# 8. AI服务接口测试
test_ai_service() {
    if [ -n "$SERVICE_FILTER" ] && [ "$SERVICE_FILTER" != "ai" ]; then
        return 0
    fi

    log_info "=== AI服务接口测试 ==="

    # 技术标目录生成测试
    log_info "测试技术标目录生成..."
    local outline_result=$(request "POST" "$AI_URL/api/ai/generate/outline" \
        '{"projectId":"test-id","expectedPages":50,"rule":"MIXED"}' "$TOKEN")
    local outline_code="${outline_result%%|*}"

    if [ "$outline_code" = "200" ] || [ "$outline_code" = "401" ]; then
        log_success "目录生成接口 (HTTP $outline_code)"
    else
        log_error "目录生成接口失败 (HTTP $outline_code)"
    fi

    # 标书改写测试
    log_info "测试标书改写..."
    local rewrite_result=$(request "POST" "$AI_URL/api/ai/rewrite" \
        '{"content":"原有标书内容","strategy":"EXPAND","multiplier":1.5}' "$TOKEN")
    local rewrite_code="${rewrite_result%%|*}"

    if [ "$rewrite_code" = "200" ] || [ "$rewrite_code" = "401" ]; then
        log_success "标书改写接口 (HTTP $rewrite_code)"
    else
        log_error "标书改写接口失败 (HTTP $rewrite_code)"
    fi

    # 合规检测测试
    log_info "测试合规检测..."
    local check_result=$(request "POST" "$AI_URL/api/ai/check/compliance" \
        '{"projectId":"test-id","documentContent":"标书内容","checkTypes":["DISQUALIFICATION"]}' "$TOKEN")
    local check_code="${check_result%%|*}"

    if [ "$check_code" = "200" ] || [ "$check_code" = "401" ]; then
        log_success "合规检测接口 (HTTP $check_code)"
    else
        log_error "合规检测接口失败 (HTTP $check_code)"
    fi

    return 0
}

#============================================
# 主函数
#============================================

show_help() {
    echo "AI智能投标系统 - API测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help       显示帮助信息"
    echo "  -v, --verbose    详细输出模式"
    echo "  -s, --service    仅测试指定服务 (gateway|user|project|material|document|knowledge|ai)"
    echo "  --skip-auth      跳过需要认证的测试"
    echo ""
    echo "示例:"
    echo "  $0                    # 运行所有测试"
    echo "  $0 -v                 # 详细模式运行"
    echo "  $0 -s knowledge       # 仅测试知识库"
    echo "  $0 --skip-auth        # 跳过认证测试"
}

main() {
    echo "=========================================="
    echo "  AI智能投标系统 - API自动化测试"
    echo "=========================================="
    echo ""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -s|--service)
                SERVICE_FILTER="$2"
                shift 2
                ;;
            --skip-auth)
                SKIP_AUTH=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    local failed=0

    # 1. 健康检查
    test_health_checks || ((failed++))

    # 2. 认证测试
    if [ "$SKIP_AUTH" = false ]; then
        test_auth || ((failed++))
    fi

    # 3. 业务服务测试
    test_user_service || ((failed++))
    test_project_service || ((failed++))
    test_material_service || ((failed++))
    test_document_service || ((failed++))
    test_knowledge_service || ((failed++))
    test_ai_service || ((failed++))

    echo ""
    echo "=========================================="
    if [ $failed -eq 0 ]; then
        log_success "所有测试完成!"
    else
        log_error "测试完成，$failed 项测试失败"
    fi
    echo "=========================================="

    return $failed
}

# 运行主函数
main "$@"