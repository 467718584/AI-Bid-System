package com.aidbid.project.engine;

import com.aidbid.project.entity.WorkflowDefinition;
import com.aidbid.project.entity.WorkflowInstance;
import com.aidbid.project.entity.WorkflowTask;
import com.aidbid.project.mapper.WorkflowDefinitionMapper;
import com.aidbid.project.mapper.WorkflowInstanceMapper;
import com.aidbid.project.mapper.WorkflowTaskMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 基于数据库的工作流引擎实现
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DatabaseWorkflowEngine implements Serializable {
    
    private final WorkflowDefinitionMapper definitionMapper;
    private final WorkflowInstanceMapper instanceMapper;
    private final WorkflowTaskMapper taskMapper;
    private final ObjectMapper objectMapper;
    
    private final AtomicLong idGenerator = new AtomicLong(System.currentTimeMillis());
    
    /** 流程实例级别的变量存储 */
    private final Map<String, Map<String, Object>> instanceVariables = new ConcurrentHashMap<>();
    /** 任务级别的变量存储 */
    private final Map<String, Map<String, Object>> taskVariables = new ConcurrentHashMap<>();
    
    @PostConstruct
    public void init() {
        log.info("DatabaseWorkflowEngine initialized");
    }
    
    public String generateId() {
        return UUID.randomUUID().toString().replace("-", "");
    }
    
    // ==================== 核心方法 ====================
    
    /**
     * 部署工作流
     */
    public WorkflowDefinition deployWorkflow(String name, String processKey, String processType, String bpmnXml, String description) {
        try {
            // 查询最大版本
            WorkflowDefinition existing = definitionMapper.selectOne(
                new LambdaQueryWrapper<WorkflowDefinition>()
                    .eq(WorkflowDefinition::getProcessKey, processKey)
                    .orderByDesc(WorkflowDefinition::getVersion)
                    .last("LIMIT 1")
            );
            
            int newVersion = (existing != null) ? existing.getVersion() + 1 : 1;
            
            WorkflowDefinition definition = new WorkflowDefinition();
            definition.setName(name);
            definition.setProcessKey(processKey);
            definition.setProcessType(processType);
            definition.setVersion(newVersion);
            definition.setDescription(description);
            definition.setBpmnResourcePath(name + ".bpmn");
            definition.setIsActive(1);
            definition.setStatus("PUBLISHED");
            definitionMapper.insert(definition);
            
            log.info("工作流部署成功: processKey={}, version={}", processKey, newVersion);
            return definition;
            
        } catch (Exception e) {
            log.error("工作流部署失败", e);
            throw new RuntimeException("工作流部署失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 启动流程实例
     */
    public WorkflowInstance startWorkflowInstance(Long definitionId, String businessKey, Map<String, Object> variables) {
        WorkflowDefinition definition = definitionMapper.selectById(definitionId);
        if (definition == null) {
            throw new RuntimeException("流程定义不存在: " + definitionId);
        }
        
        String instanceId = generateId();
        WorkflowInstance instance = new WorkflowInstance();
        instance.setProcessInstanceId(instanceId);
        instance.setWorkflowDefinitionId(definitionId);
        instance.setProcessKey(definition.getProcessKey());
        instance.setBusinessKey(businessKey);
        instance.setStatus("RUNNING");
        instance.setStartTime(LocalDateTime.now());
        instanceMapper.insert(instance);
        
        if (variables != null && !variables.isEmpty()) {
            instanceVariables.put(instanceId, new ConcurrentHashMap<>(variables));
        }
        
        return instance;
    }
    
    /**
     * 完成任务
     */
    public void completeTask(String taskId, Map<String, Object> variables) {
        WorkflowTask task = taskMapper.selectOne(
            new LambdaQueryWrapper<WorkflowTask>()
                .eq(WorkflowTask::getTaskId, taskId)
                .eq(WorkflowTask::getStatus, "PENDING")
        );
        if (task != null) {
            task.setStatus("COMPLETED");
            task.setCompleteTime(LocalDateTime.now());
            taskMapper.updateById(task);
        }
    }
    
    /**
     * 获取流程定义列表
     */
    public List<WorkflowDefinition> listDefinitions() {
        return definitionMapper.selectList(
            new LambdaQueryWrapper<WorkflowDefinition>()
                .eq(WorkflowDefinition::getIsActive, 1)
                .orderByDesc(WorkflowDefinition::getCreateTime)
        );
    }
    
    /**
     * 获取流程实例列表
     */
    public List<WorkflowInstance> listInstances(Long projectId) {
        if (projectId != null) {
            return instanceMapper.selectList(
                new LambdaQueryWrapper<WorkflowInstance>()
                    .eq(WorkflowInstance::getProjectId, projectId)
                    .orderByDesc(WorkflowInstance::getCreateTime)
            );
        }
        return instanceMapper.selectList(
            new LambdaQueryWrapper<WorkflowInstance>()
                .orderByDesc(WorkflowInstance::getCreateTime)
        );
    }
    
    // ==================== 工具方法 ====================
    
    public Map<String, Object> getInstanceVariables(String instanceId) {
        return instanceVariables.getOrDefault(instanceId, new HashMap<>());
    }
    
    @SuppressWarnings("unchecked")
    public Map<String, Object> getTaskVariables(String taskId) {
        return taskVariables.computeIfAbsent(taskId, k -> new ConcurrentHashMap<>());
    }
    
    public WorkflowDefinition getWorkflowDefinition(String processKey) {
        return definitionMapper.selectOne(
            new LambdaQueryWrapper<WorkflowDefinition>()
                .eq(WorkflowDefinition::getProcessKey, processKey)
                .eq(WorkflowDefinition::getIsActive, 1)
                .orderByDesc(WorkflowDefinition::getVersion)
                .last("LIMIT 1")
        );
    }
    
    public WorkflowInstance getWorkflowInstance(String processInstanceId) {
        return instanceMapper.selectOne(
            new LambdaQueryWrapper<WorkflowInstance>()
                .eq(WorkflowInstance::getProcessInstanceId, processInstanceId)
                .last("LIMIT 1")
        );
    }
}
