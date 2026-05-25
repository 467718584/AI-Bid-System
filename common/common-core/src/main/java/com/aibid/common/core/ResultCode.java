package com.aibid.common.core;

/**
 * 响应状态码枚举
 */
public enum ResultCode {

    SUCCESS(200, "操作成功"),
    FAIL(500, "操作失败"),
    UNAUTHORIZED(401, "未授权"),
    FORBIDDEN(403, "禁止访问"),
    NOT_FOUND(404, "资源不存在"),
    INTERNAL_SERVER_ERROR(500, "服务器内部错误"),

    // 用户模块 1000-1999
    USER_NOT_FOUND(1001, "用户不存在"),
    USER_ALREADY_EXISTS(1002, "用户已存在"),
    USERNAME_PASSWORD_ERROR(1003, "用户名或密码错误"),
    TOKEN_EXPIRED(1004, "Token已过期"),
    TOKEN_INVALID(1005, "Token无效"),
    PERMISSION_DENIED(1006, "权限不足"),

    // 项目模块 2000-2999
    PROJECT_NOT_FOUND(2001, "项目不存在"),
    PROJECT_STATUS_ERROR(2002, "项目状态异常"),
    PROJECT_NOT_ALLOWED(2003, "不允许操作此项目"),

    // 材料模块 3000-3999
    MATERIAL_NOT_FOUND(3001, "材料不存在"),
    MATERIAL_UPLOAD_FAILED(3002, "材料上传失败"),
    MATERIAL_TYPE_NOT_SUPPORT(3003, "不支持的材料类型"),

    // 文档模块 4000-4999
    DOCUMENT_NOT_FOUND(4001, "文档不存在"),
    DOCUMENT_PARSE_ERROR(4002, "文档解析失败"),

    // 参数校验 9000-9999
    PARAM_INVALID(9001, "参数无效"),
    PARAM_MISSING(9002, "缺少必需参数");

    private final int code;
    private final String message;

    ResultCode(int code, String message) {
        this.code = code;
        this.message = message;
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}