package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * Stub for Camunda BPM RuntimeService
 */
public interface RuntimeService extends Serializable {
    default ProcessInstance startProcessInstanceByKey(String processKey, String businessKey, Map<String, Object> variables) { return null; }
    default ProcessInstanceQuery createProcessInstanceQuery() { return null; }
    default void deleteProcessInstance(String instanceId, String reason) {}
    default Map<String, Object> getVariables(String executionId) { return null; }
}