package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 技术标生成监听器
 */
@Slf4j
@Component
public class GenerateTechnicalBidListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        Long enterpriseId = (Long) execution.getVariable("enterpriseId");
        log.info("开始生成技术标: projectId={}, enterpriseId={}", projectId, enterpriseId);

        // TODO: 调用 AI 服务生成技术标
        // aiGateway.generateTechnicalBid(projectId, enterpriseId);

        execution.setVariable("bidStatus", "GENERATED");
        log.info("技术标生成完成: projectId={}", projectId);
    }
}