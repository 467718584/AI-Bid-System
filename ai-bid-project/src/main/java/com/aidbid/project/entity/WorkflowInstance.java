package com.aidbid.project.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 工作流实例实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("camunda_bpm_workflow_instance")
public class WorkflowInstance extends BaseEntity {

    /** Camunda流程实例ID */
    private String processInstanceId;

    /** 工作流定义ID */
    private Long workflowDefinitionId;

    /** 流程定义Key */
    private String processKey;

    /** 关联投标项目ID */
    private Long projectId;

    /** 关联企业ID */
    private Long enterpriseId;

    /** 业务Key(项目ID) */
    private String businessKey;

    /** 发起人ID */
    private Long startUserId;

    /** 当前任务ID */
    private String currentTaskId;

    /** 当前任务名称 */
    private String currentTaskName;

    /** 状态: RUNNING / COMPLETED / ABORTED / CANCELLED */
    private String status;

    /** 开始时间 */
    private LocalDateTime startTime;

    /** 结束时间 */
    private LocalDateTime endTime;

    /** 持续时长(毫秒) */
    private Long duration;

    /** 结果数据(JSON) */
    private String resultData;
}