package com.aibid.project.dto;

import lombok.Data;

import java.util.Map;

/**
 * 工作流启动请求DTO
 */
@Data
public class WorkflowStartRequest {

    /** 业务Key(关联项目ID) */
    private String businessKey;

    /** 关联项目ID */
    private Long projectId;

    /** 关联企业ID */
    private Long enterpriseId;

    /** 发起人ID */
    private Long startUserId;

    /** 初始流程变量 */
    private Map<String, Object> variables;
}