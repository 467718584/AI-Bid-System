package com.aidbid.project.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 技能执行日志实体 - 记录技能执行历史
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_skill_execution_log")
public class SkillExecutionLog extends BaseEntity {

    /** 执行ID */
    private String executionId;

    /** 关联技能ID */
    private String skillId;

    /** 关联项目ID */
    private Long projectId;

    /** 流水线ID */
    private String pipelineId;

    /** 执行状态: PENDING/RUNNING/COMPLETED/FAILED/CANCELLED */
    private String status;

    /** 输入参数JSON */
    private String inputData;

    /** 输出结果JSON */
    private String outputData;

    /** 错误信息 */
    private String errorMessage;

    /** 执行耗时(毫秒) */
    private Long duration;

    /** 执行开始时间 */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime startTime;

    /** 执行结束时间 */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime endTime;

    /** 执行节点 */
    private String executorNode;

    /** 执行重试次数 */
    private Integer retryCount;
}