package com.aibid.common.camunda.stub;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Stub for Camunda BPM HistoryService
 */
public interface HistoryService extends Serializable {
    default HistoricActivityInstanceQuery createHistoricActivityInstanceQuery() { return null; }
    default HistoricTaskInstanceQuery createHistoricTaskInstanceQuery() { return null; }
}