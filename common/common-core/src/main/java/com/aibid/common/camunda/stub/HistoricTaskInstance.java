package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.time.LocalDateTime;

public class HistoricTaskInstance implements Serializable {
    public String getId() { return null; }
    public String getName() { return null; }
    public String getTaskDefinitionKey() { return null; }
    public String getAssignee() { return null; }
    public LocalDateTime getStartTime() { return null; }
    public LocalDateTime getEndTime() { return null; }
    public Long getDurationInMillis() { return null; }
}
