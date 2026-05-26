package com.aibid.gateway.dto;

import lombok.Data;

import java.io.Serializable;

/**
 * API路由上下文 (用于智能路由)
 */
@Data
public class RouteContext implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 请求ID */
    private String requestId;

    /** 请求类型 (analyze/embedding/summary/chat) */
    private String requestType;

    /** 输入文本长度 */
    private Integer inputLength;

    /** 是否需要高准确性 */
    private Boolean requireHighAccuracy;

    /** 是否成本敏感 */
    private Boolean costSensitive;

    /** 优先模型ID (可选) */
    private Long preferredModelId;

    /** 选择的模型ID */
    private Long selectedModelId;

    /** 选择的模型名称 */
    private String selectedModelName;

    /** 是否限流 */
    private Boolean rateLimited;
}