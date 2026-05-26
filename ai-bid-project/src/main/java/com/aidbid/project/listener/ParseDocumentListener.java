package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 招标文件解析监听器
 */
@Slf4j
@Component
public class ParseDocumentListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        String documentId = execution.getVariable("documentId");
        log.info("开始解析招标文件: documentId={}", documentId);

        // TODO: 调用 DocumentService 进行文档解析
        // documentService.parseDocument(documentId);

        execution.setVariable("parseStatus", "COMPLETED");
        log.info("招标文件解析完成: documentId={}", documentId);
    }
}