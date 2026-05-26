package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 重新生成技术标监听器
 */
@Slf4j
@Component
public class ReviseTechnicalBidListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        String reviewComment = (String) execution.getVariable("reviewComment");
        log.info("重新生成技术标: projectId={}, reviewComment={}", projectId, reviewComment);

        // TODO: 根据审核意见重新生成技术标
        execution.setVariable("bidStatus", "REVISED");
    }
}