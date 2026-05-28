package com.aibid.common.camunda.stub;

/**
 * Stub for Camunda BPM ExecutionListener
 */
public interface ExecutionListener {
    void notify(DelegateExecution execution) throws Exception;
}