package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.time.LocalDateTime;

public class HistoricActivityInstance implements Serializable {
    public String getActivityId() { return null; }
    public String getActivityName() { return null; }
    public String getActivityType() { return null; }
    public LocalDateTime getStartTime() { return null; }
    public LocalDateTime getEndTime() { return null; }
    public Long getDurationInMillis() { return null; }
    public String getAssignee() { return null; }
}
