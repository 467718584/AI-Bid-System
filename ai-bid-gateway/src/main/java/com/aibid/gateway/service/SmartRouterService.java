package com.aibid.gateway.service;

import com.aibid.gateway.dto.RouteContext;
import com.aibid.gateway.entity.ModelConfig;
import com.aibid.gateway.entity.ModelSwitchRule;
import com.aibid.gateway.mapper.ModelConfigMapper;
import com.aibid.gateway.mapper.ModelSwitchRuleMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * 智能路由服务 - 根据请求特征选择最佳模型
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SmartRouterService {

    private final ModelConfigMapper modelConfigMapper;
    private final ModelSwitchRuleMapper switchRuleMapper;
    private final ModelRegistryService modelRegistryService;
    private final RedisTemplate<String, Object> redisTemplate;

    private static final String CIRCUIT_BREAKER_KEY = "gateway:circuit_breaker:";
    private static final String LOAD_BALANCE_KEY = "gateway:load_balance:";

    // 熔断器配置
    private static final int FAILURE_THRESHOLD = 5;        // 失败5次触发熔断
    private static final int CIRCUIT_OPEN_TIME = 60000;     // 熔断持续60秒
    private static final int HALF_OPEN_REQUESTS = 3;        // 半开状态允许3个请求

    // 模型实例计数器 (用于负载均衡)
    private final Map<Long, AtomicCounter> modelCounters = new ConcurrentHashMap<>();

    /**
     * 根据请求上下文选择最佳模型
     */
    public ModelConfig selectModel(RouteContext context) {
        List<ModelConfig> candidates = getAvailableModels();

        if (candidates.isEmpty()) {
            log.warn("没有可用的模型");
            return null;
        }

        // 1. 如果指定了优先模型且可用
        if (context.getPreferredModelId() != null) {
            ModelConfig preferred = candidates.stream()
                    .filter(m -> m.getId().equals(context.getPreferredModelId()))
                    .filter(this::isModelAvailable)
                    .findFirst()
                    .orElse(null);
            if (preferred != null) {
                context.setSelectedModelId(preferred.getId());
                context.setSelectedModelName(preferred.getName());
                return preferred;
            }
        }

        // 2. 根据请求类型选择
        ModelConfig selected = selectByRequestType(candidates, context);

        // 3. 应用负载均衡
        selected = applyLoadBalance(selected, candidates);

        // 4. 检查熔断状态
        if (!isModelAvailable(selected)) {
            log.info("模型 {} 已熔断,尝试选择备用模型", selected.getModelKey());
            selected = selectFallbackModel(candidates, selected.getId());
        }

        context.setSelectedModelId(selected.getId());
        context.setSelectedModelName(selected.getName());
        return selected;
    }

    /**
     * 记录路由决策
     */
    public void recordRouting(Long modelId, boolean success, long responseTime) {
        // 更新负载均衡计数器
        AtomicCounter counter = modelCounters.get(modelId);
        if (counter == null) {
            counter = new AtomicCounter();
            modelCounters.put(modelId, counter);
        }

        if (success) {
            counter.incrementSuccess();
            counter.addResponseTime(responseTime);
            // 成功时重置失败计数
            modelRegistryService.resetFailureCount(modelId);
            // 关闭熔断器
            closeCircuitBreaker(modelId);
        } else {
            counter.incrementFailure();
            // 失败时记录失败计数
            modelRegistryService.recordFailure(modelId);
            // 检查是否需要打开熔断器
            checkCircuitBreaker(modelId);
        }
    }

    /**
     * 获取模型当前状态
     */
    public Map<String, Object> getModelStatus(Long modelId) {
        Map<String, Object> status = new HashMap<>();
        ModelConfig model = modelConfigMapper.selectById(modelId);

        status.put("modelId", modelId);
        status.put("modelName", model != null ? model.getName() : "unknown");
        status.put("available", model != null && isModelAvailable(model));
        status.put("circuitOpen", isCircuitOpen(modelId));
        status.put("failureCount", model != null ? model.getFailureCount() : 0);

        AtomicCounter counter = modelCounters.get(modelId);
        if (counter != null) {
            status.put("successRate", counter.getSuccessRate());
            status.put("avgResponseTime", counter.getAvgResponseTime());
            status.put("totalRequests", counter.getTotalRequests());
        }

        return status;
    }

    /**
     * 手动触发模型切换
     */
    public void manualSwitch(Long targetModelId, String reason) {
        modelRegistryService.switchModel(targetModelId, reason);
        log.info("手动触发模型切换: targetModelId={}, reason={}", targetModelId, reason);
    }

    // ========== 私有方法 ==========

    /**
     * 获取可用模型列表
     */
    private List<ModelConfig> getAvailableModels() {
        LambdaQueryWrapper<ModelConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ModelConfig::getStatus, 1)
               .orderByDesc(ModelConfig::getIsDefault)
               .orderByDesc(ModelConfig::getPriority);
        return modelConfigMapper.selectList(wrapper);
    }

    /**
     * 根据请求类型选择模型
     */
    private ModelConfig selectByRequestType(List<ModelConfig> candidates, RouteContext context) {
        String requestType = context.getRequestType();

        // 分析类任务 - 需要高质量模型
        if ("analyze".equals(requestType) || "quality_priority".equals(requestType)) {
            if (context.getRequireHighAccuracy() != null && context.getRequireHighAccuracy()) {
                return candidates.stream()
                        .filter(m -> supportsTaskType(m, "analyze"))
                        .filter(this::isModelAvailable)
                        .findFirst()
                        .orElse(candidates.get(0));
            }
        }

        // Embedding任务 - 需要快速模型
        if ("embedding".equals(requestType)) {
            return candidates.stream()
                    .filter(m -> supportsTaskType(m, "embedding"))
                    .filter(this::isModelAvailable)
                    .findFirst()
                    .orElse(candidates.get(0));
        }

        // 成本敏感场景 - 选择便宜的模型
        if (context.getCostSensitive() != null && context.getCostSensitive()) {
            return candidates.stream()
                    .filter(this::isModelAvailable)
                    .min(Comparator.comparing(ModelConfig::getCostPerToken,
                            Comparator.nullsFirst(Comparator.naturalOrder())))
                    .orElse(candidates.get(0));
        }

        // 默认返回默认模型
        return candidates.stream()
                .filter(m -> m.getIsDefault() == 1)
                .filter(this::isModelAvailable)
                .findFirst()
                .orElse(candidates.get(0));
    }

    /**
     * 应用负载均衡
     */
    private ModelConfig applyLoadBalance(ModelConfig selected, List<ModelConfig> candidates) {
        if (selected == null) return null;

        // 使用轮询 + 权重的方式进行负载均衡
        AtomicCounter counter = modelCounters.get(selected.getId());
        if (counter == null) {
            counter = new AtomicCounter();
            modelCounters.put(selected.getId(), counter);
        }

        // 如果当前模型请求过多,尝试转移到其他模型
        if (counter.getTotalRequests() > 100) {
            ModelConfig alternative = candidates.stream()
                    .filter(m -> !m.getId().equals(selected.getId()))
                    .filter(this::isModelAvailable)
                    .filter(m -> {
                        AtomicCounter altCounter = modelCounters.get(m.getId());
                        return altCounter == null || altCounter.getTotalRequests() < counter.getTotalRequests() / 2;
                    })
                    .findFirst()
                    .orElse(null);

            if (alternative != null) {
                log.debug("负载均衡: 从 {} 转移到 {}", selected.getModelKey(), alternative.getModelKey());
                return alternative;
            }
        }

        return selected;
    }

    /**
     * 选择备用模型
     */
    private ModelConfig selectFallbackModel(List<ModelConfig> candidates, Long excludeId) {
        return candidates.stream()
                .filter(m -> !m.getId().equals(excludeId))
                .filter(this::isModelAvailable)
                .findFirst()
                .orElse(null);
    }

    /**
     * 检查模型是否可用
     */
    private boolean isModelAvailable(ModelConfig model) {
        if (model == null || model.getStatus() != 1) {
            return false;
        }
        // 检查熔断状态
        return !isCircuitOpen(model.getId());
    }

    /**
     * 检查模型是否支持指定任务类型
     */
    private boolean supportsTaskType(ModelConfig model, String taskType) {
        if (model.getTaskTypes() == null || model.getTaskTypes().isEmpty()) {
            return true; // 没有配置则默认支持
        }
        String[] types = model.getTaskTypes().split(",");
        for (String type : types) {
            if (type.trim().equalsIgnoreCase(taskType)) {
                return true;
            }
        }
        return false;
    }

    // ========== 熔断器相关 ==========

    /**
     * 检查熔断器状态
     */
    private boolean isCircuitOpen(Long modelId) {
        String key = CIRCUIT_BREAKER_KEY + modelId;
        Object state = redisTemplate.opsForValue().get(key);
        if (state == null) {
            return false;
        }
        String[] parts = ((String) state).split(":");
        if (parts.length < 2) {
            return false;
        }
        String circuitState = parts[0];
        long openTime = Long.parseLong(parts[1]);

        if ("OPEN".equals(circuitState)) {
            if (System.currentTimeMillis() - openTime > CIRCUIT_OPEN_TIME) {
                // 转为半开状态
                redisTemplate.opsForValue().set(key, "HALF_OPEN:" + openTime);
                return false;
            }
            return true;
        }
        return false;
    }

    /**
     * 检查是否需要打开熔断器
     */
    private void checkCircuitBreaker(Long modelId) {
        ModelConfig model = modelConfigMapper.selectById(modelId);
        if (model == null) return;

        int failureCount = model.getFailureCount() != null ? model.getFailureCount() : 0;
        if (failureCount >= FAILURE_THRESHOLD) {
            openCircuitBreaker(modelId);
        }
    }

    /**
     * 打开熔断器
     */
    private void openCircuitBreaker(Long modelId) {
        String key = CIRCUIT_BREAKER_KEY + modelId;
        redisTemplate.opsForValue().set(key, "OPEN:" + System.currentTimeMillis());
        log.warn("熔断器打开: modelId={}", modelId);
    }

    /**
     * 关闭熔断器
     */
    private void closeCircuitBreaker(Long modelId) {
        String key = CIRCUIT_BREAKER_KEY + modelId;
        redisTemplate.delete(key);
    }

    /**
     * 原子计数器
     */
    private static class AtomicCounter {
        private volatile long totalRequests = 0;
        private volatile long successRequests = 0;
        private volatile long totalResponseTime = 0;

        public synchronized void incrementSuccess() {
            totalRequests++;
            successRequests++;
        }

        public synchronized void incrementFailure() {
            totalRequests++;
        }

        public synchronized void addResponseTime(long time) {
            totalResponseTime += time;
        }

        public long getTotalRequests() {
            return totalRequests;
        }

        public double getSuccessRate() {
            return totalRequests > 0 ? (double) successRequests / totalRequests * 100 : 100;
        }

        public long getAvgResponseTime() {
            return successRequests > 0 ? totalResponseTime / successRequests : 0;
        }
    }
}