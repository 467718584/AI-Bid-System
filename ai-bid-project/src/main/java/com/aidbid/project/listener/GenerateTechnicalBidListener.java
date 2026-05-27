package com.aidbid.project.listener;

import com.aidbid.project.gateway.AiGateway;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.ExecutionListener;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * 技术标生成监听器
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class GenerateTechnicalBidListener implements ExecutionListener {

    private final AiGateway aiGateway;

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        Long enterpriseId = (Long) execution.getVariable("enterpriseId");
        log.info("开始生成技术标: projectId={}, enterpriseId={}", projectId, enterpriseId);

        try {
            // 构建请求参数
            Map<String, Object> request = new HashMap<>();
            request.put("projectId", projectId);
            request.put("enterpriseId", enterpriseId);
            request.put("bidType", "technical");

            // 调用AI服务生成技术标
            Map<String, Object> response = aiGateway.generateBid(request);

            // 检查响应结果
            if (response != null && "200".equals(String.valueOf(response.get("code")))) {
                execution.setVariable("bidStatus", "GENERATED");
                execution.setVariable("jobId", response.get("data"));
                log.info("技术标生成完成: projectId={}, jobId={}", projectId, response.get("data"));
            } else {
                execution.setVariable("bidStatus", "FAILED");
                log.error("技术标生成失败: projectId={}, response={}", projectId, response);
            }
        } catch (Exception e) {
            execution.setVariable("bidStatus", "FAILED");
            log.error("技术标生成异常: projectId={}", projectId, e);
        }
    }
}