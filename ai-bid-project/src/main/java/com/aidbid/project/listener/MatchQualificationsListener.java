package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 资质匹配监听器
 */
@Slf4j
@Component
public class MatchQualificationsListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        Long enterpriseId = (Long) execution.getVariable("enterpriseId");
        log.info("开始资质匹配: projectId={}, enterpriseId={}", projectId, enterpriseId);

        // TODO: 调用 QualificationService 进行资质匹配
        // qualificationService.matchQualifications(projectId, enterpriseId);

        execution.setVariable("matchStatus", "COMPLETED");
        log.info("资质匹配完成: projectId={}", projectId);
    }
}