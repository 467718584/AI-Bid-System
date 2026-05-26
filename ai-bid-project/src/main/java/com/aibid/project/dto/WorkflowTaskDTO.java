package com.aibid.project.dto;

import lombok.Data;

/**
 * 工作流任务DTO
 */
@Data
public class WorkflowTaskDTO {

    /** 任务ID */
    private String taskId;

    /** 任务名称 */
    private String taskName;

    /** 任务定义Key */
    private String taskKey;

    /** 办理人 */
    private String assignee;

    /** 候选用户 */
    private String candidateUsers;

    /** 候选组 */
    private String candidateGroups;

    /** 优先级 */
    private Integer priority;

    /** 到期时间 */
    private String dueDate;

    /** 任务描述 */
    private String description;

    /** 流程实例ID */
    private String processInstanceId;

    /** 流程定义Key */
    private String processKey;

    /** 业务Key */
    private String businessKey;

    /** 关联项目ID */
    private Long projectId;

    /** 关联企业ID */
    private Long enterpriseId;

    /** 流程变量(JSON) */
    private String variables;

    /** 创建时间 */
    private String createTime;
}