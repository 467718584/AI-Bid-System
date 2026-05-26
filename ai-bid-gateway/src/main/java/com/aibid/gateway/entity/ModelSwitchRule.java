package com.aibid.gateway.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 模型切换规则
 */
@Data
public class ModelSwitchRule implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 主键ID */
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    /** 规则名称 */
    private String name;

    /** 规则类型: load_balance/cost_optimize/quality_priority/failover */
    private String ruleType;

    /** 触发条件-阈值 */
    private BigDecimal threshold;

    /** 触发条件-指标类型 */
    private String metricType;

    /** 源模型ID */
    private Long sourceModelId;

    /** 目标模型ID */
    private Long targetModelId;

    /** 是否启用 */
    private Integer enabled;

    /** 优先级 */
    private Integer priority;

    /** 冷却时间(秒) */
    private Integer cooldownSeconds;

    /** 上次触发时间 */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime lastTriggerTime;

    /** 触发次数 */
    private Integer triggerCount;

    /** 备注 */
    private String remark;

    /** 创建时间 */
    @TableField(fill = FieldFill.INSERT)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;

    /** 更新时间 */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;

    /** 创建人ID */
    @TableField(fill = FieldFill.INSERT)
    private Long createBy;

    /** 更新人ID */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Long updateBy;

    /** 乐观锁版本号 */
    @Version
    private Integer versionLock;

    /** 逻辑删除标记 */
    @TableLogic
    private Integer deleted;
}