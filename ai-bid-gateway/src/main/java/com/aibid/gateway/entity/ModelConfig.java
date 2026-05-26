package com.aibid.gateway.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 模型配置实体
 */
@Data
public class ModelConfig implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 主键ID */
    @TableId(type = IdType.ASSIGN_ID)
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

    /** 支持的任务类型 */
    private String taskTypes;

    /** 是否默认模型 */
    private Integer isDefault;

    /** 状态: 0=禁用, 1=启用 */
    private Integer status;

    /** 优先级 (数字越大优先级越高) */
    private Integer priority;

    /** 失败次数计数 */
    private Integer failureCount;

    /** 最后调用时间 */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime lastCallTime;

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