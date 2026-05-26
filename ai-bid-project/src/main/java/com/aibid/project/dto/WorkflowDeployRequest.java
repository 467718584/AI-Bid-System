package com.aibid.project.dto;

import lombok.Data;

import java.util.Map;

/**
 * 工作流部署请求DTO
 */
@Data
public class WorkflowDeployRequest {

    /** BPMN XML内容 */
    private String bpmnXml;

    /** 流程名称 */
    private String name;

    /** 流程类型: TECHNICAL_BID / CREDIT_BID */
    private String processType;

    /** 流程描述 */
    private String description;
}