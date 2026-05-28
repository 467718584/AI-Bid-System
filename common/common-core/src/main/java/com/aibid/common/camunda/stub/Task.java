package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.time.LocalDateTime;

public class Task implements Serializable {
    public String getId() { return null; }
    public String getName() { return null; }
    public String getTaskDefinitionKey() { return null; }
    public String getAssignee() { return null; }
    public int getPriority() { return 0; }
    public String getDescription() { return null; }
    public String getProcessInstanceId() { return null; }
    public String getProcessDefinitionKey() { return null; }
    public String getBusinessKey() { return null; }
    public LocalDateTime getCreateTime() { return null; }
    public String getExecutionId() { return null; }
}
