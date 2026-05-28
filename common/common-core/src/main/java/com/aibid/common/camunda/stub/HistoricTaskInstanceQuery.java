package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.util.List;

public class HistoricTaskInstanceQuery implements Serializable {
    public HistoricTaskInstanceQuery processInstanceId(String instanceId) { return this; }
    public HistoricTaskInstanceQuery orderByHistoricTaskInstanceStartTime() { return this; }
    public HistoricTaskInstanceQuery asc() { return this; }
    public HistoricTaskInstanceQuery desc() { return this; }
    public List<HistoricTaskInstance> list() { return null; }
}
