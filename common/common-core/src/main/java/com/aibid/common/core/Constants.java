package com.aibid.common.core;

/**
 * 系统常量定义
 */
public final class Constants {

    private Constants() {
    }

    // ========== 业务常量 ==========

    /** 超级管理员ID */
    public static final Long SUPER_ADMIN_ID = 1L;

    /** 超级管理员角色标识 */
    public static final String SUPER_ADMIN_ROLE = "SUPER_ADMIN";

    /** 默认分页大小 */
    public static final Integer DEFAULT_PAGE_SIZE = 20;

    /** 最大分页大小 */
    public static final Integer MAX_PAGE_SIZE = 100;

    // ========== JWT相关 ==========

    /** JWT密钥（生产环境从环境变量读取） */
    public static final String JWT_SECRET_KEY = "ai-bid-system-jwt-secret-key-2024";

    /** JWT签名算法 */
    public static final String JWT_ALGORITHM = "HS256";

    /** Token过期时间（毫秒），默认7天 */
    public static final Long JWT_EXPIRE_TIME = 7 * 24 * 60 * 60 * 1000L;

    /** Token前缀 */
    public static final String TOKEN_PREFIX = "Bearer ";

    // ========== 文件上传 ==========

    /** 上传文件最大大小（字节），默认10MB */
    public static final Long MAX_FILE_SIZE = 10 * 1024 * 1024L;

    /** 允许上传的文件类型 */
    public static final String[] ALLOWED_FILE_TYPES = {
            "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
            "txt", "jpg", "jpeg", "png", "gif", "bmp"
    };

    // ========== Redis缓存Key前缀 ==========

    /** 用户信息缓存前缀 */
    public static final String CACHE_USER_PREFIX = "user:";

    /** 权限信息缓存前缀 */
    public static final String CACHE_PERMISSION_PREFIX = "permission:";

    /** 角色信息缓存前缀 */
    public static final String CACHE_ROLE_PREFIX = "role:";

    /** Token缓存前缀 */
    public static final String CACHE_TOKEN_PREFIX = "token:";

    /** 验证码缓存前缀 */
    public static final String CACHE_CAPTCHA_PREFIX = "captcha:";

    // ========== 缓存过期时间（秒） ==========

    /** 短缓存过期时间：5分钟 */
    public static final Long CACHE_SHORT_EXPIRE = 5 * 60L;

    /** 中缓存过期时间：30分钟 */
    public static final Long CACHE_MEDIUM_EXPIRE = 30 * 60L;

    /** 长缓存过期时间：1小时 */
    public static final Long CACHE_LONG_EXPIRE = 60 * 60L;

    /** 永久缓存 */
    public static final Long CACHE_FOREVER_EXPIRE = -1L;

    // ========== 项目状态 ==========

    /** 项目状态 - 草稿 */
    public static final String PROJECT_STATUS_DRAFT = "DRAFT";

    /** 项目状态 - 进行中 */
    public static final String PROJECT_STATUS_IN_PROGRESS = "IN_PROGRESS";

    /** 项目状态 - 已完成 */
    public static final String PROJECT_STATUS_COMPLETED = "COMPLETED";

    /** 项目状态 - 已取消 */
    public static final String PROJECT_STATUS_CANCELLED = "CANCELLED";

    // ========== 用户状态 ==========

    /** 用户状态 - 启用 */
    public static final Integer USER_STATUS_ENABLED = 0;

    /** 用户状态 - 禁用 */
    public static final Integer USER_STATUS_DISABLED = 1;

    // ========== 文档类型 ==========

    /** 文档类型 - PDF */
    public static final String DOC_TYPE_PDF = "pdf";

    /** 文档类型 - Word */
    public static final String DOC_TYPE_WORD = "word";

    /** 文档类型 - Excel */
    public static final String DOC_TYPE_EXCEL = "excel";

    /** 文档类型 - 图片 */
    public static final String DOC_TYPE_IMAGE = "image";

    // ========== 消息队列 ==========

    /** 文档解析队列 */
    public static final String MQ_QUEUE_DOC_PARSE = "doc-parse-queue";

    /** AI分析队列 */
    public static final String MQ_QUEUE_AI_ANALYZE = "ai-analyze-queue";

    /** 消息通知队列 */
    public static final String MQ_QUEUE_NOTIFY = "notify-queue";
}