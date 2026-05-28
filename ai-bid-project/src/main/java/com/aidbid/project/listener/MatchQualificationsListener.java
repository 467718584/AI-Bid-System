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
 * 资质匹配监听器
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class MatchQualificationsListener implements ExecutionListener {

    private final AiGateway aiGateway;

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        Long enterpriseId = (Long) execution.getVariable("enterpriseId");
        log.info("开始资质匹配: projectId={}, enterpriseId={}", projectId, enterpriseId);

        try {
            // 构建请求参数
            Map<String, Object> request = new HashMap<>();
            request.put("projectId", projectId);
            request.put("enterpriseId", enterpriseId);

            // 调用AI服务进行资质匹配
            Map<String, Object> response = aiGateway.matchQualifications(request);

            // 检查响应结果
            if (response != null && "200".equals(String.valueOf(response.get("code")))) {
                execution.setVariable("matchStatus", "COMPLETED");
                execution.setVariable("matchResult", response.get("data"));
                log.info("资质匹配完成: projectId={}", projectId);
            } else {
                execution.setVariable("matchStatus", "FAILED");
                log.error("资质匹配失败: projectId={}, response={}", projectId, response);
            }
        } catch (Exception e) {
            execution.setVariable("matchStatus", "FAILED");
            log.error("资质匹配异常: projectId={}", projectId, e);
        }
    }
}