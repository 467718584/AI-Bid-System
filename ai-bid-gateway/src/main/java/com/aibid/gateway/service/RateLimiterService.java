package com.aibid.gateway.service;

import com.aibid.gateway.dto.RouteContext;
import com.aibid.gateway.entity.ModelConfig;
import com.aibid.gateway.mapper.ModelConfigMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * 限流服务 - 防止API超额调用
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class RateLimiterService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final ModelConfigMapper modelConfigMapper;

    private static final String RATE_LIMIT_KEY = "gateway:rate_limit:";
    private static final String USER_RATE_LIMIT_KEY = "gateway:user_rate_limit:";

    // 默认限流配置
    private static final int DEFAULT_REQUESTS_PER_MINUTE = 60;
    private static final int DEFAULT_REQUESTS_PER_HOUR = 1000;
    private static final int DEFAULT_REQUESTS_PER_DAY = 10000;

    /**
     * 检查是否允许请求
     */
    public boolean allowRequest(Long modelId, Long userId) {
        String key = RATE_LIMIT_KEY + modelId;
        return checkRateLimit(key, DEFAULT_REQUESTS_PER_MINUTE, 60);
    }

    /**
     * 检查用户级别的限流
     */
    public boolean allowUserRequest(Long userId, String requestType) {
        if (userId == null) {
            return true; // 无用户ID,不限制
        }

        // 按请求类型设置不同的限流阈值
        int limit = getLimitByRequestType(requestType);
        String key = USER_RATE_LIMIT_KEY + userId + ":" + requestType;

        return checkRateLimit(key, limit, 60);
    }

    /**
     * 获取当前请求剩余配额
     */
    public long getRemainingQuota(Long modelId) {
        String key = RATE_LIMIT_KEY + modelId;
        Object count = redisTemplate.opsForValue().get(key + ":count");
        if (count == null) {
            return DEFAULT_REQUESTS_PER_MINUTE;
        }
        return Math.max(0, DEFAULT_REQUESTS_PER_MINUTE - ((Long) count));
    }

    /**
     * 获取用户剩余配额
     */
    public long getUserRemainingQuota(Long userId, String requestType) {
        if (userId == null) {
            return -1; // 无限制
        }
        String key = USER_RATE_LIMIT_KEY + userId + ":" + requestType;
        Object count = redisTemplate.opsForValue().get(key + ":count");
        if (count == null) {
            return getLimitByRequestType(requestType);
        }
        return Math.max(0, getLimitByRequestType(requestType) - ((Long) count));
    }

    /**
     * 记录一次请求
     */
    public void recordRequest(Long modelId, Long userId, String requestType) {
        // 记录模型级别限流
        String modelKey = RATE_LIMIT_KEY + modelId;
        incrementRateLimit(modelKey, 60);

        // 记录用户级别限流
        if (userId != null) {
            String userKey = USER_RATE_LIMIT_KEY + userId + ":" + requestType;
            int limit = getLimitByRequestType(requestType);
            incrementRateLimit(userKey, 60);
        }
    }

    /**
     * 获取限流状态
     */
    public RateLimitStatus getRateLimitStatus(Long modelId, Long userId, String requestType) {
        RateLimitStatus status = new RateLimitStatus();

        // 模型限流状态
        String modelKey = RATE_LIMIT_KEY + modelId;
        Object modelCount = redisTemplate.opsForValue().get(modelKey + ":count");
        status.setModelLimit(DEFAULT_REQUESTS_PER_MINUTE);
        status.setModelUsed(modelCount != null ? ((Long) modelCount) : 0);
        status.setModelRemaining(Math.max(0, DEFAULT_REQUESTS_PER_MINUTE - status.getModelUsed()));

        // 用户限流状态
        if (userId != null) {
            int userLimit = getLimitByRequestType(requestType);
            String userKey = USER_RATE_LIMIT_KEY + userId + ":" + requestType;
            Object userCount = redisTemplate.opsForValue().get(userKey + ":count");
            status.setUserLimit(userLimit);
            status.setUserUsed(userCount != null ? ((Long) userCount) : 0);
            status.setUserRemaining(Math.max(0, userLimit - status.getUserUsed()));
        } else {
            status.setUserLimit(-1);
            status.setUserUsed(0);
            status.setUserRemaining(-1);
        }

        // 判断是否触发限流
        status.setLimited(status.getModelRemaining() <= 0 || status.getUserRemaining() <= 0);

        return status;
    }

    /**
     * 重置限流计数
     */
    public void resetRateLimit(Long modelId) {
        String key = RATE_LIMIT_KEY + modelId;
        redisTemplate.delete(key + ":count");
        redisTemplate.delete(key + ":window");
        log.info("重置模型限流: modelId={}", modelId);
    }

    /**
     * 设置自定义限流阈值
     */
    public void setCustomLimit(Long modelId, int requestsPerMinute) {
        String key = RATE_LIMIT_KEY + modelId + ":config";
        redisTemplate.opsForValue().set(key, requestsPerMinute);
        log.info("设置模型限流阈值: modelId={}, limit={}", modelId, requestsPerMinute);
    }

    // ========== 私有方法 ==========

    /**
     * 检查限流
     */
    private boolean checkRateLimit(String key, int limit, int windowSeconds) {
        Long current = redisTemplate.opsForValue().increment(key + ":count");
        if (current == 1) {
            redisTemplate.expire(key + ":count", windowSeconds, TimeUnit.SECONDS);
        }
        return current != null && current <= limit;
    }

    /**
     * 增加限流计数
     */
    private void incrementRateLimit(String key, int windowSeconds) {
        Long count = redisTemplate.opsForValue().increment(key + ":count");
        if (count != null && count == 1) {
            redisTemplate.expire(key + ":count", windowSeconds, TimeUnit.SECONDS);
        }
    }

    /**
     * 根据请求类型获取限流阈值
     */
    private int getLimitByRequestType(String requestType) {
        if (requestType == null) {
            return DEFAULT_REQUESTS_PER_MINUTE;
        }
        switch (requestType.toLowerCase()) {
            case "embedding":
                return 100; // Embedding任务可以更频繁
            case "analyze":
                return 30;  // 分析任务限流更严格
            case "summary":
                return 50;
            case "chat":
            default:
                return DEFAULT_REQUESTS_PER_MINUTE;
        }
    }

    /**
     * 限流状态
     */
    @lombok.Data
    public static class RateLimitStatus {
        private int modelLimit;
        private long modelUsed;
        private long modelRemaining;
        private int userLimit;
        private long userUsed;
        private long userRemaining;
        private boolean limited;
    }
}