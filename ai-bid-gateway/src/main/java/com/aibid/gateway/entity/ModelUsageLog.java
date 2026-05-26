package com.aibid.gateway.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 模型使用日志
 */
@Data
public class ModelUsageLog implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 主键ID */
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    /** 模型ID */
    private Long modelId;

    /** 模型名称 */
    private String modelName;

    /** 请求类型 */
    private String requestType;

    /** 调用次数 */
    private Integer callCount;

    /** 输入Token数 */
    private Long inputTokens;

    /** 输出Token数 */
    private Long outputTokens;

    /** 总Token数 */
    private Long totalTokens;

    /** 成功次数 */
    private Integer successCount;

    /** 失败次数 */
    private Integer failureCount;

    /** 平均响应时间(毫秒) */
    private Long avgResponseTime;

    /** 最大响应时间(毫秒) */
    private Long maxResponseTime;

    /** 最小响应时间(毫秒) */
    private Long minResponseTime;

    /** 总费用 */
    private BigDecimal totalCost;

    /** 调用日期 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime callDate;

    /** 创建时间 */
    @TableField(fill = FieldFill.INSERT)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;

    /** 更新时间 */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;

    /** 逻辑删除标记 */
    @TableLogic
    private Integer deleted;
}