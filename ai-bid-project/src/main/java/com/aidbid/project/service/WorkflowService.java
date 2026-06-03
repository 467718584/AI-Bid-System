package com.aidbid.project.service;

import com.aidbid.project.engine.DatabaseWorkflowEngine;
import com.aidbid.project.dto.WorkflowDeployRequest;
import com.aidbid.project.dto.WorkflowStartRequest;
import com.aidbid.project.dto.WorkflowTaskDTO;
import com.aidbid.project.entity.WorkflowDefinition;
import com.aidbid.project.entity.WorkflowInstance;
import com.aidbid.project.entity.WorkflowTask;
import com.aidbid.project.mapper.WorkflowDefinitionMapper;
import com.aidbid.project.mapper.WorkflowInstanceMapper;
import com.aidbid.project.mapper.WorkflowTaskMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 工作流服务 - 使用DatabaseWorkflowEngine
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class WorkflowService {

    private final DatabaseWorkflowEngine workflowEngine;
    private final WorkflowDefinitionMapper definitionMapper;
    private final WorkflowInstanceMapper instanceMapper;
    private final WorkflowTaskMapper taskMapper;
    private final ObjectMapper objectMapper;

    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /**
     * 部署工作流
     */
    @Transactional
    public WorkflowDefinition deployWorkflow(WorkflowDeployRequest request) {
        // 从name生成processKey
        String processKey = request.getName().toLowerCase().replaceAll("[^a-z0-9]", "_");
        return workflowEngine.deployWorkflow(
            request.getName(),
            processKey,
            request.getProcessType(),
            request.getBpmnXml(),
            request.getDescription()
        );
    }

    /**
     * 启动流程实例
     */
    @Transactional
    public WorkflowInstance startProcessInstance(String processKey, WorkflowStartRequest request) {
        WorkflowDefinition definition = workflowEngine.getWorkflowDefinition(processKey);
        if (definition == null) {
            throw new RuntimeException("流程定义不存在或未激活: " + processKey);
        }
        
        Map<String, Object> variables = request.getVariables() != null ? request.getVariables() : new HashMap<>();
        if (request.getProjectId() != null) {
            variables.put("projectId", request.getProjectId());
        }
        if (request.getEnterpriseId() != null) {
            variables.put("enterpriseId", request.getEnterpriseId());
        }
        
        return workflowEngine.startWorkflowInstance(
            definition.getId(),
            request.getBusinessKey(),
            variables
        );
    }

    /**
     * 完成任务
     */
    @Transactional
    public WorkflowTask completeTask(String taskId, Map<String, Object> variables) {
        workflowEngine.completeTask(taskId, variables);
        
        WorkflowTask task = taskMapper.selectOne(
            new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowTask>()
                .eq(WorkflowTask::getTaskId, taskId)
        );
        return task;
    }

    /**
     * 获取待办任务列表
     */
    public List<WorkflowTaskDTO> getPendingTasks(String assignee) {
        List<WorkflowTask> tasks;
        if (assignee != null && !assignee.isEmpty()) {
            tasks = taskMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowTask>()
                    .eq(WorkflowTask::getAssignee, assignee)
                    .eq(WorkflowTask::getStatus, "PENDING")
            );
        } else {
            tasks = taskMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowTask>()
                    .eq(WorkflowTask::getStatus, "PENDING")
                    .isNull(WorkflowTask::getAssignee)
            );
        }
        
        List<WorkflowTaskDTO> result = new ArrayList<>();
        for (WorkflowTask task : tasks) {
            result.add(convertToTaskDTO(task));
        }
        return result;
    }

    /**
     * 获取流程历史
     */
    public List<Map<String, Object>> getProcessHistory(String instanceId) {
        List<Map<String, Object>> history = new ArrayList<>();
        
        // 获取该实例的所有任务
        List<WorkflowTask> tasks = taskMapper.selectList(
            new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowTask>()
                .eq(WorkflowTask::getWorkflowInstanceId, 
                    instanceMapper.selectOne(
                        new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowInstance>()
                            .eq(WorkflowInstance::getProcessInstanceId, instanceId)
                    ).getId())
                .orderByAsc(WorkflowTask::getCreateTime)
        );
        
        for (WorkflowTask task : tasks) {
            Map<String, Object> item = new HashMap<>();
            item.put("taskId", task.getTaskId());
            item.put("taskName", task.getTaskName());
            item.put("taskKey", task.getTaskKey());
            item.put("assignee", task.getAssignee());
            item.put("status", task.getStatus());
            item.put("createTime", task.getCreateTime() != null ? task.getCreateTime().format(DATE_FORMAT) : null);
            item.put("completeTime", task.getCompleteTime() != null ? task.getCompleteTime().format(DATE_FORMAT) : null);
            item.put("type", "TASK");
            history.add(item);
        }
        
        return history;
    }

    /**
     * 获取流程定义列表
     */
    public List<WorkflowDefinition> listDefinitions() {
        return workflowEngine.listDefinitions();
    }

    /**
     * 获取流程实例列表
     */
    public List<WorkflowInstance> listInstances(Long projectId) {
        return workflowEngine.listInstances(projectId);
    }

    /**
     * 获取工作流定义详情
     */
    public WorkflowDefinition getDefinitionById(Long id) {
        return definitionMapper.selectById(id);
    }

    /**
     * 挂起流程定义
     */
    @Transactional
    public void suspendDefinition(String processKey) {
        definitionMapper.selectList(
            new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowDefinition>()
                .eq(WorkflowDefinition::getProcessKey, processKey)
        ).forEach(d -> {
            d.setIsActive(0);
            d.setStatus("SUSPENDED");
            definitionMapper.updateById(d);
        });
    }

    /**
     * 激活流程定义
     */
    @Transactional
    public void activateDefinition(String processKey) {
        definitionMapper.selectList(
            new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowDefinition>()
                .eq(WorkflowDefinition::getProcessKey, processKey)
        ).forEach(d -> {
            d.setIsActive(1);
            d.setStatus("PUBLISHED");
            definitionMapper.updateById(d);
        });
    }

    /**
     * 取消流程实例
     */
    @Transactional
    public void cancelProcessInstance(String instanceId, String cancelReason) {
        WorkflowInstance instance = instanceMapper.selectOne(
            new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowInstance>()
                .eq(WorkflowInstance::getProcessInstanceId, instanceId)
        );
        if (instance != null) {
            instance.setStatus("CANCELLED");
            instance.setEndTime(LocalDateTime.now());
            instanceMapper.updateById(instance);
        }
    }

    // ==================== 私有方法 ====================

    private WorkflowTaskDTO convertToTaskDTO(WorkflowTask task) {
        WorkflowTaskDTO dto = new WorkflowTaskDTO();
        dto.setTaskId(task.getTaskId());
        dto.setTaskName(task.getTaskName());
        dto.setTaskKey(task.getTaskKey());
        dto.setAssignee(task.getAssignee());
        dto.setPriority(task.getPriority());
        dto.setDescription(task.getDescription());
        dto.setCreateTime(task.getCreateTime() != null ? task.getCreateTime().format(DATE_FORMAT) : null);
        
        if (task.getWorkflowInstanceId() != null) {
            WorkflowInstance instance = instanceMapper.selectById(task.getWorkflowInstanceId());
            if (instance != null) {
                dto.setProcessInstanceId(instance.getProcessInstanceId());
                dto.setProjectId(instance.getProjectId());
            }
        }
        
        return dto;
    }
}
