package com.aidbid.project.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
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
import com.aibid.common.camunda.stub.FormService;
import com.aibid.common.camunda.stub.HistoryService;
import com.aibid.common.camunda.stub.HistoricActivityInstance;
import com.aibid.common.camunda.stub.HistoricTaskInstance;
import com.aibid.common.camunda.stub.ProcessEngine;
import com.aibid.common.camunda.stub.ProcessInstance;
import com.aibid.common.camunda.stub.RepositoryService;
import com.aibid.common.camunda.stub.RuntimeService;
import com.aibid.common.camunda.stub.Task;
import com.aibid.common.camunda.stub.TaskService;
import com.aibid.common.camunda.stub.Deployment;
import com.aibid.common.camunda.stub.ProcessDefinition;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 工作流服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class WorkflowService {

    private final ProcessEngine processEngine;
    private final RepositoryService repositoryService;
    private final RuntimeService runtimeService;
    private final TaskService taskService;
    private final HistoryService historyService;
    private final FormService formService;
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
        try {
            // 将BPMN XML转换为字节数组
            byte[] bpmnBytes = request.getBpmnXml().getBytes("UTF-8");

            // 使用Camunda部署流程
            Deployment deployment = repositoryService
                    .createDeployment()
                    .name(request.getName())
                    .addString(request.getName() + ".bpmn", request.getBpmnXml())
                    .deploy();

            // 获取流程定义
            ProcessDefinition processDefinition = repositoryService
                    .createProcessDefinitionQuery()
                    .deploymentId(deployment.getId())
                    .singleResult();

            // 保存到数据库
            WorkflowDefinition definition = new WorkflowDefinition();
            definition.setName(request.getName());
            definition.setProcessKey(processDefinition.getKey());
            definition.setProcessType(request.getProcessType());
            definition.setVersion(processDefinition.getVersion());
            definition.setDescription(request.getDescription());
            definition.setBpmnResourcePath(request.getName() + ".bpmn");
            definition.setIsActive(1);
            definition.setStatus("PUBLISHED");
            definitionMapper.insert(definition);

            log.info("工作流部署成功: processKey={}, version={}", processDefinition.getKey(), processDefinition.getVersion());
            return definition;

        } catch (Exception e) {
            log.error("工作流部署失败", e);
            throw new BusinessException(ResultCode.FAIL, "工作流部署失败: " + e.getMessage());
        }
    }

    /**
     * 启动流程实例
     */
    @Transactional
    public WorkflowInstance startProcessInstance(String processKey, WorkflowStartRequest request) {
        try {
            // 查询工作流定义
            WorkflowDefinition definition = definitionMapper.selectOne(
                    new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowDefinition>()
                            .eq(WorkflowDefinition::getProcessKey, processKey)
                            .eq(WorkflowDefinition::getIsActive, 1)
                            .orderByDesc(WorkflowDefinition::getVersion)
                            .last("LIMIT 1")
            );

            if (definition == null) {
                throw new BusinessException(ResultCode.PARAM_INVALID, "流程定义不存在或未激活: " + processKey);
            }

            // 准备流程变量
            Map<String, Object> variables = request.getVariables() != null ? request.getVariables() : new HashMap<>();
            if (request.getProjectId() != null) {
                variables.put("projectId", request.getProjectId());
            }
            if (request.getEnterpriseId() != null) {
                variables.put("enterpriseId", request.getEnterpriseId());
            }
            if (StringUtils.hasText(request.getBusinessKey())) {
                variables.put("businessKey", request.getBusinessKey());
            }

            // 启动Camunda流程
            ProcessInstance processInstance = runtimeService
                    .startProcessInstanceByKey(processKey, request.getBusinessKey(), variables);

            // 保存到数据库
            WorkflowInstance instance = new WorkflowInstance();
            instance.setProcessInstanceId(processInstance.getId());
            instance.setWorkflowDefinitionId(definition.getId());
            instance.setProcessKey(processKey);
            instance.setProjectId(request.getProjectId());
            instance.setEnterpriseId(request.getEnterpriseId());
            instance.setBusinessKey(request.getBusinessKey());
            instance.setStartUserId(request.getStartUserId());
            instance.setStatus("RUNNING");
            instance.setStartTime(LocalDateTime.now());
            instanceMapper.insert(instance);

            // 更新当前任务信息
            List<Task> tasks = taskService.createTaskQuery()
                    .processInstanceId(processInstance.getId())
                    .list();
            if (!tasks.isEmpty()) {
                Task task = tasks.get(0);
                instance.setCurrentTaskId(task.getId());
                instance.setCurrentTaskName(task.getName());
                instanceMapper.updateById(instance);
            }

            log.info("流程实例启动成功: processKey={}, instanceId={}", processKey, processInstance.getId());
            return instance;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("流程实例启动失败", e);
            throw new BusinessException(ResultCode.FAIL, "流程实例启动失败: " + e.getMessage());
        }
    }

    /**
     * 完成任务
     */
    @Transactional
    public WorkflowTask completeTask(String taskId, Map<String, Object> variables) {
        try {
            Task task = taskService.createTaskQuery().taskId(taskId).singleResult();
            if (task == null) {
                throw new BusinessException(ResultCode.PARAM_INVALID, "任务不存在: " + taskId);
            }

            // 更新任务记录状态
            WorkflowTask workflowTask = taskMapper.selectOne(
                    new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowTask>()
                            .eq(WorkflowTask::getTaskId, taskId)
                            .eq(WorkflowTask::getStatus, "PENDING")
                            .last("LIMIT 1")
            );

            // 完成任务
            if (variables != null && !variables.isEmpty()) {
                taskService.complete(taskId, variables);
            } else {
                taskService.complete(taskId);
            }

            // 更新本地任务记录
            if (workflowTask != null) {
                workflowTask.setStatus("COMPLETED");
                workflowTask.setCompleteTime(LocalDateTime.now());
                taskMapper.updateById(workflowTask);
            }

            // 更新流程实例的当前任务
            updateInstanceCurrentTask(task.getProcessInstanceId());

            log.info("任务完成成功: taskId={}", taskId);
            return workflowTask;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("任务完成失败", e);
            throw new BusinessException(ResultCode.FAIL, "任务完成失败: " + e.getMessage());
        }
    }

    /**
     * 获取待办任务列表
     */
    public List<WorkflowTaskDTO> getPendingTasks(String assignee) {
        List<Task> tasks;
        if (StringUtils.hasText(assignee)) {
            tasks = taskService.createTaskQuery().taskAssignee(assignee).list();
        } else {
            tasks = taskService.createTaskQuery().taskUnassigned().list();
        }

        List<WorkflowTaskDTO> result = new ArrayList<>();
        for (Task task : tasks) {
            result.add(convertToTaskDTO(task));
        }
        return result;
    }

    /**
     * 获取流程历史
     */
    public List<Map<String, Object>> getProcessHistory(String instanceId) {
        List<Map<String, Object>> history = new ArrayList<>();

        // 获取活动历史
        List<HistoricActivityInstance> activities = historyService
                .createHistoricActivityInstanceQuery()
                .processInstanceId(instanceId)
                .orderByHistoricActivityInstanceStartTime()
                .asc()
                .list();

        for (HistoricActivityInstance activity : activities) {
            Map<String, Object> item = new HashMap<>();
            item.put("activityId", activity.getActivityId());
            item.put("activityName", activity.getActivityName());
            item.put("activityType", activity.getActivityType());
            item.put("startTime", activity.getStartTime() != null ?
                    activity.getStartTime().format(DATE_FORMAT) : null);
            item.put("endTime", activity.getEndTime() != null ?
                    activity.getEndTime().format(DATE_FORMAT) : null);
            item.put("duration", activity.getDurationInMillis());
            item.put("assignee", activity.getAssignee());
            history.add(item);
        }

        // 获取任务历史
        List<HistoricTaskInstance> taskHistory = historyService
                .createHistoricTaskInstanceQuery()
                .processInstanceId(instanceId)
                .orderByHistoricTaskInstanceStartTime()
                .asc()
                .list();

        for (HistoricTaskInstance task : taskHistory) {
            Map<String, Object> item = new HashMap<>();
            item.put("taskId", task.getId());
            item.put("taskName", task.getName());
            item.put("taskKey", task.getTaskDefinitionKey());
            item.put("assignee", task.getAssignee());
            item.put("startTime", task.getStartTime() != null ?
                    task.getStartTime().format(DATE_FORMAT) : null);
            item.put("endTime", task.getEndTime() != null ?
                    task.getEndTime().format(DATE_FORMAT) : null);
            item.put("duration", task.getDurationInMillis());
            item.put("type", "TASK");
            history.add(item);
        }

        return history;
    }

    /**
     * 获取流程定义列表
     */
    public List<WorkflowDefinition> listDefinitions() {
        return definitionMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowDefinition>()
                        .eq(WorkflowDefinition::getIsActive, 1)
                        .orderByDesc(WorkflowDefinition::getCreateTime)
        );
    }

    /**
     * 获取流程实例列表
     */
    public List<WorkflowInstance> listInstances(Long projectId) {
        var queryWrapper = new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowInstance>();
        if (projectId != null) {
            queryWrapper.eq(WorkflowInstance::getProjectId, projectId);
        }
        return instanceMapper.selectList(queryWrapper.orderByDesc(WorkflowInstance::getCreateTime));
    }

    /**
     * 获取运行中的流程实例
     */
    public List<ProcessInstance> listRunningProcessInstances(String processKey) {
        return runtimeService.createProcessInstanceQuery()
                .processDefinitionKey(processKey)
                .list();
    }

    /**
     * 挂起流程定义
     */
    @Transactional
    public void suspendDefinition(String processKey) {
        repositoryService.suspendProcessDefinitionByKey(processKey);
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
        repositoryService.activateProcessDefinitionByKey(processKey);
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
        runtimeService.deleteProcessInstance(instanceId, cancelReason);

        WorkflowInstance instance = instanceMapper.selectOne(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowInstance>()
                        .eq(WorkflowInstance::getProcessInstanceId, instanceId)
                        .last("LIMIT 1")
        );
        if (instance != null) {
            instance.setStatus("CANCELLED");
            instance.setEndTime(LocalDateTime.now());
            instanceMapper.updateById(instance);
        }
    }

    // ==================== 私有方法 ====================

    private WorkflowTaskDTO convertToTaskDTO(Task task) {
        WorkflowTaskDTO dto = new WorkflowTaskDTO();
        dto.setTaskId(task.getId());
        dto.setTaskName(task.getName());
        dto.setTaskKey(task.getTaskDefinitionKey());
        dto.setAssignee(task.getAssignee());
        dto.setPriority(task.getPriority());
        dto.setDescription(task.getDescription());
        dto.setProcessInstanceId(task.getProcessInstanceId());
        dto.setProcessKey(task.getProcessDefinitionKey());
        dto.setBusinessKey(task.getBusinessKey());
        dto.setCreateTime(task.getCreateTime() != null ?
                task.getCreateTime().format(DATE_FORMAT) : null);

        // 获取流程变量
        Map<String, Object> variables = runtimeService.getVariables(task.getExecutionId());
        try {
            dto.setVariables(objectMapper.writeValueAsString(variables));
            if (variables.containsKey("projectId")) {
                dto.setProjectId(((Number) variables.get("projectId")).longValue());
            }
            if (variables.containsKey("enterpriseId")) {
                dto.setEnterpriseId(((Number) variables.get("enterpriseId")).longValue());
            }
        } catch (Exception e) {
            log.warn("转换流程变量失败", e);
        }

        return dto;
    }

    private void updateInstanceCurrentTask(String processInstanceId) {
        List<Task> tasks = taskService.createTaskQuery()
                .processInstanceId(processInstanceId)
                .list();

        WorkflowInstance instance = instanceMapper.selectOne(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<WorkflowInstance>()
                        .eq(WorkflowInstance::getProcessInstanceId, processInstanceId)
                        .last("LIMIT 1")
        );

        if (instance != null) {
            if (tasks.isEmpty()) {
                // 流程已结束
                instance.setStatus("COMPLETED");
                instance.setEndTime(LocalDateTime.now());
                if (instance.getStartTime() != null) {
                    instance.setDuration(java.time.Duration.between(
                            instance.getStartTime(), instance.getEndTime()).toMillis());
                }
            } else {
                Task task = tasks.get(0);
                instance.setCurrentTaskId(task.getId());
                instance.setCurrentTaskName(task.getName());
            }
            instanceMapper.updateById(instance);
        }
    }
}