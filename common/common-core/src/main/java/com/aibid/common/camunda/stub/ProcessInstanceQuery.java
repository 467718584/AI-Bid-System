package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.util.List;

public class ProcessInstanceQuery implements Serializable {
    public ProcessInstanceQuery processDefinitionKey(String key) { return this; }
    public ProcessInstanceQuery businessKey(String key) { return this; }
    public List<ProcessInstance> list() { return null; }
}
