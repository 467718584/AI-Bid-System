package com.aidbid.project.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 工作流定义实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("camunda_bpm_workflow_definition")
public class WorkflowDefinition extends BaseEntity {

    /** 流程名称 */
    private String name;

    /** 流程定义Key */
    private String processKey;

    /** 流程类型: TECHNICAL_BID / CREDIT_BID */
    private String processType;

    /** 版本号 */
    private Integer version;

    /** 流程描述 */
    private String description;

    /** BPMN资源路径 */
    private String bpmnResourcePath;

    /** 是否激活: 0=停用, 1=激活 */
    private Integer isActive;

    /** 状态: DRAFT / PUBLISHED / SUSPENDED */
    private String status;
}