package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import com.aibid.common.camunda.stub.DelegateExecution;
import com.aibid.common.camunda.stub.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 招标文件解析完成监听器
 */
@Slf4j
@Component
public class ParseDocumentCompleteListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        String documentId = (String) execution.getVariable("documentId");
        log.info("文档解析流程节点完成: documentId={}", documentId);

        // 解析完成后可以触发后续流程逻辑
    }
}