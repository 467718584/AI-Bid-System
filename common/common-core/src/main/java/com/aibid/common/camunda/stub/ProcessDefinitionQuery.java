package com.aibid.common.camunda.stub;

import java.io.Serializable;

public class ProcessDefinitionQuery implements Serializable {
    public ProcessDefinitionQuery deploymentId(String deploymentId) { return this; }
    public ProcessDefinitionQuery key(String key) { return this; }
    public ProcessDefinition singleResult() { return null; }
}
