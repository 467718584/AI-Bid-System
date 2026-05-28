package com.aibid.common.camunda.stub;

import java.io.Serializable;

/**
 * Stub for Camunda BPM RepositoryService
 */
public interface RepositoryService extends Serializable {
    default Deployment createDeployment() { return null; }
    default ProcessDefinitionQuery createProcessDefinitionQuery() { return null; }
    default void suspendProcessDefinitionByKey(String key) {}
    default void activateProcessDefinitionByKey(String key) {}
}