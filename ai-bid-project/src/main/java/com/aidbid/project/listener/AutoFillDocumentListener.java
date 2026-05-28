package com.aidbid.project.listener;

import lombok.extern.slf4j.Slf4j;
import com.aibid.common.camunda.stub.DelegateExecution;
import com.aibid.common.camunda.stub.ExecutionListener;
import org.springframework.stereotype.Component;

/**
 * 自动填充监听器
 */
@Slf4j
@Component
public class AutoFillDocumentListener implements ExecutionListener {

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        Long enterpriseId = (Long) execution.getVariable("enterpriseId");
        log.info("开始自动填充资信标: projectId={}, enterpriseId={}", projectId, enterpriseId);

        // TODO: 调用 QualificationService 进行自动填充
        // qualificationService.autoFillQualifications(projectId, enterpriseId);

        execution.setVariable("fillStatus", "COMPLETED");
        log.info("自动填充完成: projectId={}", projectId);
    }
}