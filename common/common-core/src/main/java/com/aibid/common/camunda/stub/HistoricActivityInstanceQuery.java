package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.List;

public class HistoricActivityInstanceQuery implements Serializable {
    public HistoricActivityInstanceQuery processInstanceId(String instanceId) { return this; }
    public HistoricActivityInstanceQuery orderByHistoricActivityInstanceStartTime() { return this; }
    public HistoricActivityInstanceQuery asc() { return this; }
    public HistoricActivityInstanceQuery desc() { return this; }
    public List<HistoricActivityInstance> list() { return null; }
}
