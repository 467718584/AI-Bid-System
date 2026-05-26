package com.aibid.gateway.dto;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * 模型配置请求DTO
 */
@Data
public class ModelConfigDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 主键ID (更新时必需) */
    private Long id;

    /** 模型名称 */
    private String name;

    /** 模型标识 */
    private String modelKey;

    /** 提供商 */
    private String provider;

    /** API端点 */
    private String endpoint;

    /** API密钥 */
    private String apiKey;

    /** 模型版本 */
    private String version;

    /** 最大Token数 */
    private Integer maxTokens;

    /** 温度参数 */
    private BigDecimal temperature;

    /** 调用费用/千Token */
    private BigDecimal costPerToken;

    /** 支持的任务类型 (逗号分隔) */
    private String taskTypes;

    /** 是否默认模型 */
    private Boolean isDefault;

    /** 状态: 0=禁用, 1=启用 */
    private Integer status;

    /** 优先级 */
    private Integer priority;

    /** 备注 */
    private String remark;
}