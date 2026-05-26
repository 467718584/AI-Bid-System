package com.aibid.gateway.dto;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 模型统计响应DTO
 */
@Data
public class ModelStatsDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 模型ID */
    private Long modelId;

    /** 模型名称 */
    private String modelName;

    /** 总调用次数 */
    private Long totalCallCount;

    /** 今日调用次数 */
    private Long todayCallCount;

    /** 成功次数 */
    private Long successCount;

    /** 失败次数 */
    private Long failureCount;

    /** 成功率 */
    private BigDecimal successRate;

    /** 平均响应时间(ms) */
    private Long avgResponseTime;

    /** 最大响应时间(ms) */
    private Long maxResponseTime;

    /** 总输入Token数 */
    private Long totalInputTokens;

    /** 总输出Token数 */
    private Long totalOutputTokens;

    /** 总Token数 */
    private Long totalTokens;

    /** 今日费用 */
    private BigDecimal todayCost;

    /** 总费用 */
    private BigDecimal totalCost;

    /** 最后调用时间 */
    private LocalDateTime lastCallTime;

    /** 连续失败次数 */
    private Integer failureCountStat;

    /** 状态 */
    private Integer status;
}