package com.aibid.common.camunda.stub;

import java.io.Serializable;

/**
 * Stub for Camunda BPM DelegateExecution
 */
public class DelegateExecution implements Serializable {
    public String getProcessInstanceId() { return null; }
    public String getBusinessKey() { return null; }
    public void setVariable(String name, Object value) {}
    public Object getVariable(String name) { return null; }
}