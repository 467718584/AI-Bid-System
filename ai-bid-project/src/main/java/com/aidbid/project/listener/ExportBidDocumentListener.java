package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import com.aibid.common.camunda.stub.DelegateExecution;
import com.aibid.common.camunda.stub.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 标书导出监听器
 */
@Slf4j
@Component
public class ExportBidDocumentListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        String format = (String) execution.getVariable("format");
        log.info("开始导出标书: projectId={}, format={}", projectId, format);

        // TODO: 调用 DocumentExporter 导出标书
        // documentExporter.export(projectId, format);

        execution.setVariable("exportStatus", "COMPLETED");
        log.info("标书导出完成: projectId={}", projectId);
    }
}