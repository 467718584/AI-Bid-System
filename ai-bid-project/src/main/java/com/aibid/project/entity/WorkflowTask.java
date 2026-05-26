package com.aibid.project.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 工作流任务记录实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("camunda_bpm_workflow_task")
public class WorkflowTask extends BaseEntity {

    /** 工作流实例ID */
    private Long workflowInstanceId;

    /** Camunda任务ID */
    private String taskId;

    /** 任务名称 */
    private String taskName;

    /** 任务定义Key */
    private String taskKey;

    /** 办理人 */
    private String assignee;

    /** 候选用户(JSON数组) */
    private String candidateUsers;

    /** 候选组(JSON数组) */
    private String candidateGroups;

    /** 优先级 */
    private Integer priority;

    /** 到期时间 */
    private LocalDateTime dueDate;

    /** 任务描述 */
    private String description;

    /** 流程变量(JSON) */
    private String variables;

    /** 状态: PENDING / COMPLETED / ABORTED */
    private String status;

    /** 完成时间 */
    private LocalDateTime completeTime;
}