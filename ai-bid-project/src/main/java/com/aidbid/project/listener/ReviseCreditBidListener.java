package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 修改资信标监听器
 */
@Slf4j
@Component
public class ReviseCreditBidListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        String confirmComment = (String) execution.getVariable("confirmComment");
        log.info("重新填充资信标: projectId={}, confirmComment={}", projectId, confirmComment);

        // TODO: 根据确认意见重新填充
        execution.setVariable("fillStatus", "REVISED");
    }
}