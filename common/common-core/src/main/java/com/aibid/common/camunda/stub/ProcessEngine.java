package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.util.Map;

/**
 * Stub for Camunda BPM ProcessEngine
 */
public interface ProcessEngine extends Serializable {
    default RepositoryService getRepositoryService() { return null; }
    default RuntimeService getRuntimeService() { return null; }
    default TaskService getTaskService() { return null; }
    default HistoryService getHistoryService() { return null; }
    default FormService getFormService() { return null; }
}