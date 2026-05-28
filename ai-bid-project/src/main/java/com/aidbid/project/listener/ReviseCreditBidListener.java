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
 * 修改资信标监听器
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ReviseCreditBidListener implements ExecutionListener {

    private final AiGateway aiGateway;

    @Override
    public void notify(DelegateExecution execution) throws Exception {
        Long projectId = (Long) execution.getVariable("projectId");
        String confirmComment = (String) execution.getVariable("confirmComment");
        log.info("重新填充资信标: projectId={}, confirmComment={}", projectId, confirmComment);

        try {
            // 构建请求参数
            Map<String, Object> request = new HashMap<>();
            request.put("projectId", projectId);
            request.put("bidType", "credit");
            request.put("reviseRequirements", confirmComment);

            // 调用AI服务重新填充资信标
            Map<String, Object> response = aiGateway.reviseBid(request);

            // 检查响应结果
            if (response != null && "200".equals(String.valueOf(response.get("code")))) {
                execution.setVariable("fillStatus", "REVISED");
                log.info("资信标重新填充完成: projectId={}", projectId);
            } else {
                execution.setVariable("fillStatus", "REVISION_FAILED");
                log.error("资信标重新填充失败: projectId={}, response={}", projectId, response);
            }
        } catch (Exception e) {
            execution.setVariable("fillStatus", "REVISION_FAILED");
            log.error("资信标重新填充异常: projectId={}", projectId, e);
        }
    }
}