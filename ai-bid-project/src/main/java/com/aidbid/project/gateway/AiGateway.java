package com.aidbid.project.gateway;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * AI服务网关 - 调用Python AI服务
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AiGateway {

    private final RestTemplate restTemplate;

    @Value("${ai.service.url:http://ai:8087}")
    private String aiServiceUrl;

    /**
     * 生成技术标/资信标
     * POST /api/ai/pipeline/generate
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> generateBid(Map<String, Object> request) {
        String url = aiServiceUrl + "/api/ai/pipeline/generate";
        return doPost(url, request);
    }

    /**
     * 资质匹配 - 通过技能执行接口调用
     * POST /api/ai/skills/execute
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> matchQualifications(Map<String, Object> request) {
        // 构建技能执行请求
        Map<String, Object> skillRequest = new HashMap<>();
        skillRequest.put("skillId", "match-qualifications");
        skillRequest.put("inputs", request);
        skillRequest.put("projectId", request.get("projectId"));
        String url = aiServiceUrl + "/api/ai/skills/execute";
        return doPost(url, skillRequest);
    }

    /**
     * 标书改写 - 通过技能执行接口调用
     * POST /api/ai/skills/execute
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> reviseBid(Map<String, Object> request) {
        // 构建技能执行请求
        Map<String, Object> skillRequest = new HashMap<>();
        skillRequest.put("skillId", "revise-bid");
        skillRequest.put("inputs", request);
        skillRequest.put("projectId", request.get("projectId"));
        String url = aiServiceUrl + "/api/ai/skills/execute";
        return doPost(url, skillRequest);
    }

    /**
     * 通用POST请求
     */
    @SuppressWarnings("unchecked")
    private Map<String, Object> doPost(String url, Map<String, Object> body) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

            log.info("调用AI服务: {} - {}", url, body.keySet());
            var response = restTemplate.postForEntity(url, entity, Map.class);
            Map<String, Object> result = response.getBody();
            log.info("AI服务响应: {}", result);
            return result;
        } catch (Exception e) {
            log.error("AI服务调用失败: {} - {}", url, e.getMessage());
            return Map.of("code", 500, "message", e.getMessage());
        }
    }
}