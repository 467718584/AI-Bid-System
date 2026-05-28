package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * Stub for Camunda BPM TaskService
 */
public interface TaskService extends Serializable {
    default TaskQuery createTaskQuery() { return null; }
    default void complete(String taskId) {}
    default void complete(String taskId, Map<String, Object> variables) {}
    default void complete(String taskId, Map<String, Object> variables, boolean withVariablesInReturn) {}
}