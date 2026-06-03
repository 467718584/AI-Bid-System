package com.aidbid.project.controller;

import com.aibid.common.core.Result;
import com.aidbid.project.dto.WorkflowDeployRequest;
import com.aidbid.project.dto.WorkflowStartRequest;
import com.aidbid.project.dto.WorkflowTaskDTO;
import com.aidbid.project.entity.WorkflowDefinition;
import com.aidbid.project.entity.WorkflowInstance;
import com.aidbid.project.service.WorkflowService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import com.aibid.common.camunda.stub.ProcessInstance;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 工作流控制器
 */
@RestController
@RequestMapping("/api/project/workflow")
@RequiredArgsConstructor
public class WorkflowController {

    private final WorkflowService workflowService;

    /**
     * 创建工作流（简化版，用于前端新建工作流）
     * POST /api/project/workflow
     */
    @PostMapping
    public Result<WorkflowDefinition> createWorkflow(@RequestBody CreateWorkflowRequest request) {
        WorkflowDeployRequest deployRequest = new WorkflowDeployRequest();
        deployRequest.setName(request.getName());
        deployRequest.setDescription(request.getDescription());
        deployRequest.setProcessType(request.getCategory() != null ?
            request.getCategory().toUpperCase() : "BID");
        deployRequest.setBpmnXml(request.getBpmnXml());

        WorkflowDefinition definition = workflowService.deployWorkflow(deployRequest);
        return Result.ok(definition);
    }

    /**
     * 获取工作流列表
     * GET /api/project/workflow
     */
    @GetMapping
    public Result<List<WorkflowDefinition>> listWorkflows() {
        List<WorkflowDefinition> definitions = workflowService.listDefinitions();
        return Result.ok(definitions);
    }

    /**
     * 获取工作流详情
     * GET /api/project/workflow/{id}
     */
    @GetMapping("/{id}")
    public Result<WorkflowDefinition> getWorkflowById(@PathVariable Long id) {
        WorkflowDefinition definition = workflowService.getDefinitionById(id);
        return Result.ok(definition);
    }

    /**
     * 部署工作流
     * POST /api/project/workflow/deploy
     */
    @PostMapping("/deploy")
    public Result<WorkflowDefinition> deployWorkflow(@RequestBody WorkflowDeployRequest request) {
        WorkflowDefinition definition = workflowService.deployWorkflow(request);
        return Result.ok(definition);
    }

    /**
     * 启动流程实例
     * POST /api/project/workflow/start/{processKey}
     */
    @PostMapping("/start/{processKey}")
    public Result<WorkflowInstance> startProcessInstance(
            @PathVariable String processKey,
            @RequestBody(required = false) WorkflowStartRequest request) {
        if (request == null) {
            request = new WorkflowStartRequest();
        }
        WorkflowInstance instance = workflowService.startProcessInstance(processKey, request);
        return Result.ok(instance);
    }

    /**
     * 获取待办任务列表
     * GET /api/project/workflow/tasks
     */
    @GetMapping("/tasks")
    public Result<List<WorkflowTaskDTO>> getPendingTasks(
            @RequestParam(required = false) String assignee) {
        List<WorkflowTaskDTO> tasks = workflowService.getPendingTasks(assignee);
        return Result.ok(tasks);
    }

    /**
     * 完成任务
     * POST /api/project/workflow/task/{taskId}/complete
     */
    @PostMapping("/task/{taskId}/complete")
    public Result<Void> completeTask(
            @PathVariable String taskId,
            @RequestBody(required = false) Map<String, Object> variables) {
        workflowService.completeTask(taskId, variables);
        return Result.ok();
    }

    /**
     * 获取流程历史
     * GET /api/project/workflow/history/{instanceId}
     */
    @GetMapping("/history/{instanceId}")
    public Result<List<Map<String, Object>>> getProcessHistory(@PathVariable String instanceId) {
        List<Map<String, Object>> history = workflowService.getProcessHistory(instanceId);
        return Result.ok(history);
    }

    /**
     * 获取流程定义列表
     * GET /api/project/workflow/definitions
     */
    @GetMapping("/definitions")
    public Result<List<WorkflowDefinition>> listDefinitions() {
        List<WorkflowDefinition> definitions = workflowService.listDefinitions();
        return Result.ok(definitions);
    }

    /**
     * 获取流程实例列表
     * GET /api/project/workflow/instances
     */
    @GetMapping("/instances")
    public Result<List<WorkflowInstance>> listInstances(
            @RequestParam(required = false) Long projectId) {
        List<WorkflowInstance> instances = workflowService.listInstances(projectId);
        return Result.ok(instances);
    }

    /**
     * 挂起流程定义
     * PUT /api/project/workflow/suspend/{processKey}
     */
    @PutMapping("/suspend/{processKey}")
    public Result<Void> suspendDefinition(@PathVariable String processKey) {
        workflowService.suspendDefinition(processKey);
        return Result.ok();
    }

    /**
     * 激活流程定义
     * PUT /api/project/workflow/activate/{processKey}
     */
    @PutMapping("/activate/{processKey}")
    public Result<Void> activateDefinition(@PathVariable String processKey) {
        workflowService.activateDefinition(processKey);
        return Result.ok();
    }

    /**
     * 取消流程实例
     * DELETE /api/project/workflow/instance/{instanceId}
     */
    @DeleteMapping("/instance/{instanceId}")
    public Result<Void> cancelProcessInstance(
            @PathVariable String instanceId,
            @RequestParam(required = false, defaultValue = "用户取消") String cancelReason) {
        workflowService.cancelProcessInstance(instanceId, cancelReason);
        return Result.ok();
    }

    /**
     * 创建工作流请求
     */
    @Data
    public static class CreateWorkflowRequest {
        private String name;
        private String description;
        private String category;
        private String bpmnXml;
    }
}