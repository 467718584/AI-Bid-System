package com.aidbid.project.listener;

import com.aidbid.project.gateway.AiGateway;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import com.aibid.common.camunda.stub.DelegateExecution;
import com.aibid.common.camunda.stub.ExecutionListener;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * 重新生成技术标监听器
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ReviseTechnicalBidListener implements ExecutionListener {

    private final AiGateway aiGateway;

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        String reviewComment = (String) execution.getVariable("reviewComment");
        log.info("重新生成技术标: projectId={}, reviewComment={}", projectId, reviewComment);

        try {
            // 构建请求参数
            Map<String, Object> request = new HashMap<>();
            request.put("projectId", projectId);
            request.put("bidType", "technical");
            request.put("reviseRequirements", reviewComment);

            // 调用AI服务重新生成技术标
            Map<String, Object> response = aiGateway.reviseBid(request);

            // 检查响应结果
            if (response != null && "200".equals(String.valueOf(response.get("code")))) {
                execution.setVariable("bidStatus", "REVISED");
                log.info("技术标重新生成完成: projectId={}", projectId);
            } else {
                execution.setVariable("bidStatus", "REVISION_FAILED");
                log.error("技术标重新生成失败: projectId={}, response={}", projectId, response);
            }
        } catch (Exception e) {
            execution.setVariable("bidStatus", "REVISION_FAILED");
            log.error("技术标重新生成异常: projectId={}", projectId, e);
        }
    }
}