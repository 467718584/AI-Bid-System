package com.aibid.gateway.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.gateway.dto.ModelConfigDTO;
import com.aibid.gateway.dto.ModelStatsDTO;
import com.aibid.gateway.dto.MonitorDashboardDTO;
import com.aibid.gateway.entity.ModelConfig;
import com.aibid.gateway.entity.ModelUsageLog;
import com.aibid.gateway.mapper.ModelConfigMapper;
import com.aibid.gateway.mapper.ModelUsageLogMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

/**
 * 模型注册服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ModelRegistryService extends ServiceImpl<ModelConfigMapper, ModelConfig> {

    private final ModelConfigMapper modelConfigMapper;
    private final ModelUsageLogMapper modelUsageLogMapper;
    private final RedisTemplate<String, Object> redisTemplate;

    private static final String DEFAULT_MODEL_KEY = "gateway:default_model";
    private static final String MODEL_STATS_KEY = "gateway:model_stats:";

    /**
     * 注册新模型
     */
    @Transactional
    public ModelConfig registerModel(ModelConfigDTO dto) {
        // 检查模型标识是否已存在
        LambdaQueryWrapper<ModelConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ModelConfig::getModelKey, dto.getModelKey());
        if (modelConfigMapper.exists(wrapper)) {
            throw new BusinessException(ResultCode.PARAM_INVALID, "模型标识已存在");
        }

        ModelConfig config = new ModelConfig();
        config.setName(dto.getName());
        config.setModelKey(dto.getModelKey());
        config.setProvider(dto.getProvider());
        config.setEndpoint(dto.getEndpoint());
        config.setApiKey(dto.getApiKey());
        config.setVersion(dto.getVersion());
        config.setMaxTokens(dto.getMaxTokens() != null ? dto.getMaxTokens() : 4096);
        config.setTemperature(dto.getTemperature() != null ? dto.getTemperature() : new BigDecimal("0.7"));
        config.setCostPerToken(dto.getCostPerToken() != null ? dto.getCostPerToken() : BigDecimal.ZERO);
        config.setTaskTypes(dto.getTaskTypes());
        config.setIsDefault(dto.getIsDefault() != null && dto.getIsDefault() ? 1 : 0);
        config.setStatus(dto.getStatus() != null ? dto.getStatus() : 1);
        config.setPriority(dto.getPriority() != null ? dto.getPriority() : 0);
        config.setFailureCount(0);

        modelConfigMapper.insert(config);

        // 如果设置为默认模型,取消其他默认
        if (config.getIsDefault() == 1) {
            clearDefaultModel(config.getId());
        }

        log.info("模型注册成功: {}", config.getModelKey());
        return config;
    }

    /**
     * 更新模型配置
     */
    @Transactional
    public ModelConfig updateModel(Long id, ModelConfigDTO dto) {
        ModelConfig config = modelConfigMapper.selectById(id);
        if (config == null) {
            throw new BusinessException(ResultCode.PARAM_INVALID, "模型不存在");
        }

        if (dto.getName() != null) config.setName(dto.getName());
        if (dto.getProvider() != null) config.setProvider(dto.getProvider());
        if (dto.getEndpoint() != null) config.setEndpoint(dto.getEndpoint());
        if (dto.getApiKey() != null) config.setApiKey(dto.getApiKey());
        if (dto.getVersion() != null) config.setVersion(dto.getVersion());
        if (dto.getMaxTokens() != null) config.setMaxTokens(dto.getMaxTokens());
        if (dto.getTemperature() != null) config.setTemperature(dto.getTemperature());
        if (dto.getCostPerToken() != null) config.setCostPerToken(dto.getCostPerToken());
        if (dto.getTaskTypes() != null) config.setTaskTypes(dto.getTaskTypes());
        if (dto.getStatus() != null) config.setStatus(dto.getStatus());
        if (dto.getPriority() != null) config.setPriority(dto.getPriority());

        // 如果设置为默认模型,取消其他默认
        if (dto.getIsDefault() != null && dto.getIsDefault()) {
            clearDefaultModel(config.getId());
            config.setIsDefault(1);
        }

        modelConfigMapper.updateById(config);
        log.info("模型更新成功: {}", config.getModelKey());
        return config;
    }

    /**
     * 获取模型列表
     */
    public List<ModelConfig> listModels() {
        LambdaQueryWrapper<ModelConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(ModelConfig::getPriority)
               .orderByAsc(ModelConfig::getCreateTime);
        return modelConfigMapper.selectList(wrapper);
    }

    /**
     * 获取启用的模型列表
     */
    public List<ModelConfig> listEnabledModels() {
        LambdaQueryWrapper<ModelConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ModelConfig::getStatus, 1)
               .orderByDesc(ModelConfig::getIsDefault)
               .orderByDesc(ModelConfig::getPriority);
        return modelConfigMapper.selectList(wrapper);
    }

    /**
     * 获取默认模型
     */
    public ModelConfig getDefaultModel() {
        // 先从Redis缓存获取
        Object cached = redisTemplate.opsForValue().get(DEFAULT_MODEL_KEY);
        if (cached != null) {
            return (ModelConfig) cached;
        }

        LambdaQueryWrapper<ModelConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ModelConfig::getIsDefault, 1)
               .eq(ModelConfig::getStatus, 1);
        ModelConfig model = modelConfigMapper.selectOne(wrapper);

        if (model == null) {
            // 获取优先级最高的启用模型
            wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(ModelConfig::getStatus, 1)
                   .orderByDesc(ModelConfig::getPriority)
                   .last("LIMIT 1");
            model = modelConfigMapper.selectOne(wrapper);
        }

        if (model != null) {
            redisTemplate.opsForValue().set(DEFAULT_MODEL_KEY, model);
        }
        return model;
    }

    /**
     * 切换默认模型
     */
    @Transactional
    public ModelConfig switchModel(Long modelId, String reason) {
        ModelConfig model = modelConfigMapper.selectById(modelId);
        if (model == null) {
            throw new BusinessException(ResultCode.PARAM_INVALID, "模型不存在");
        }
        if (model.getStatus() != 1) {
            throw new BusinessException(ResultCode.PARAM_INVALID, "模型未启用");
        }

        clearDefaultModel(modelId);
        model.setIsDefault(1);
        modelConfigMapper.updateById(model);

        // 清除缓存
        redisTemplate.delete(DEFAULT_MODEL_KEY);

        log.info("默认模型切换成功: {} -> {} ({})", getDefaultModel().getModelKey(), model.getModelKey(), reason);
        return model;
    }

    /**
     * 删除模型
     */
    @Transactional
    public void deleteModel(Long modelId) {
        ModelConfig model = modelConfigMapper.selectById(modelId);
        if (model == null) {
            throw new BusinessException(ResultCode.PARAM_INVALID, "模型不存在");
        }
        if (model.getIsDefault() == 1) {
            throw new BusinessException(ResultCode.PARAM_INVALID, "不能删除默认模型");
        }
        modelConfigMapper.deleteById(modelId);
        log.info("模型删除成功: {}", model.getModelKey());
    }

    /**
     * 获取模型使用统计
     */
    public ModelStatsDTO getModelStats(Long modelId) {
        ModelConfig model = modelConfigMapper.selectById(modelId);
        if (model == null) {
            throw new BusinessException(ResultCode.PARAM_INVALID, "模型不存在");
        }

        ModelStatsDTO stats = new ModelStatsDTO();
        stats.setModelId(modelId);
        stats.setModelName(model.getName());
        stats.setStatus(model.getStatus());
        stats.setFailureCountStat(model.getFailureCount());

        // 从Redis获取实时统计
        String statsKey = MODEL_STATS_KEY + modelId;
        Map<Object, Object> cachedStats = redisTemplate.opsForHash().entries(statsKey);
        if (cachedStats != null && !cachedStats.isEmpty()) {
            stats.setTotalCallCount(getLongFromCache(cachedStats, "totalCallCount"));
            stats.setTodayCallCount(getLongFromCache(cachedStats, "todayCallCount"));
            stats.setSuccessCount(getLongFromCache(cachedStats, "successCount"));
            stats.setFailureCount(getLongFromCache(cachedStats, "failureCount"));
            stats.setAvgResponseTime(getLongFromCache(cachedStats, "avgResponseTime"));
            stats.setMaxResponseTime(getLongFromCache(cachedStats, "maxResponseTime"));
            stats.setTotalInputTokens(getLongFromCache(cachedStats, "totalInputTokens"));
            stats.setTotalOutputTokens(getLongFromCache(cachedStats, "totalOutputTokens"));
        } else {
            // 从数据库查询汇总数据
            List<ModelUsageLog> logs = queryUsageLogs(modelId, null, null);
            aggregateStats(stats, logs);
        }

        // 计算成功率
        if (stats.getTotalCallCount() != null && stats.getTotalCallCount() > 0) {
            long success = stats.getSuccessCount() != null ? stats.getSuccessCount() : 0;
            stats.setSuccessRate(new BigDecimal(success)
                    .divide(new BigDecimal(stats.getTotalCallCount()), 4, BigDecimal.ROUND_HALF_UP)
                    .multiply(new BigDecimal("100")));
        }

        stats.setLastCallTime(model.getLastCallTime());
        return stats;
    }

    /**
     * 获取监控面板数据
     */
    public MonitorDashboardDTO getDashboardData() {
        MonitorDashboardDTO dashboard = new MonitorDashboardDTO();

        // 获取所有模型统计
        List<ModelConfig> models = listModels();
        List<ModelStatsDTO> modelStatsList = new ArrayList<>();
        long totalCallCount = 0;
        long todayCallCount = 0;
        long totalSuccessCount = 0;
        long totalFailureCount = 0;
        BigDecimal totalCost = BigDecimal.ZERO;

        for (ModelConfig model : models) {
            ModelStatsDTO stats = getModelStats(model.getId());
            modelStatsList.add(stats);
            totalCallCount += stats.getTotalCallCount() != null ? stats.getTotalCallCount() : 0;
            todayCallCount += stats.getTodayCallCount() != null ? stats.getTodayCallCount() : 0;
            totalSuccessCount += stats.getSuccessCount() != null ? stats.getSuccessCount() : 0;
            totalFailureCount += stats.getFailureCount() != null ? stats.getFailureCount() : 0;
            if (stats.getTotalCost() != null) {
                totalCost = totalCost.add(stats.getTotalCost());
            }
        }
        dashboard.setModelStats(modelStatsList);
        dashboard.setTotalCallCount(totalCallCount);
        dashboard.setTodayCallCount(todayCallCount);
        dashboard.setTodayTotalCost(totalCost);

        // 获取每日调用趋势 (最近7天)
        dashboard.setDailyTrends(getDailyCallTrends());

        return dashboard;
    }

    /**
     * 记录模型调用
     */
    public void recordCall(Long modelId, String modelName, String requestType,
                          long inputTokens, long outputTokens, long responseTimeMs, boolean success) {
        String statsKey = MODEL_STATS_KEY + modelId;

        // 更新总调用次数
        redisTemplate.opsForHash().increment(statsKey, "totalCallCount", 1);
        if (success) {
            redisTemplate.opsForHash().increment(statsKey, "successCount", 1);
        } else {
            redisTemplate.opsForHash().increment(statsKey, "failureCount", 1);
        }

        // 更新Token统计
        redisTemplate.opsForHash().increment(statsKey, "totalInputTokens", inputTokens);
        redisTemplate.opsForHash().increment(statsKey, "totalOutputTokens", outputTokens);
        redisTemplate.opsForHash().increment(statsKey, "totalTokens", inputTokens + outputTokens);

        // 更新响应时间 (使用滑动平均)
        Long avgTime = getLongFromCache(redisTemplate.opsForHash().entries(statsKey), "avgResponseTime");
        if (avgTime == null) avgTime = 0L;
        long newAvg = (avgTime * 9 + responseTimeMs) / 10;
        redisTemplate.opsForHash().put(statsKey, "avgResponseTime", newAvg);

        // 更新最大响应时间
        Long maxTime = getLongFromCache(redisTemplate.opsForHash().entries(statsKey), "maxResponseTime");
        if (maxTime == null || responseTimeMs > maxTime) {
            redisTemplate.opsForHash().put(statsKey, "maxResponseTime", responseTimeMs);
        }

        // 更新今日调用
        String todayKey = statsKey + ":today:" + LocalDate.now();
        redisTemplate.opsForHash().increment(todayKey, "callCount", 1);
        redisTemplate.expire(todayKey, 2, TimeUnit.DAYS);

        // 更新费用统计
        ModelConfig model = modelConfigMapper.selectById(modelId);
        if (model != null && model.getCostPerToken() != null) {
            BigDecimal cost = model.getCostPerToken()
                    .multiply(new BigDecimal(inputTokens + outputTokens))
                    .divide(new BigDecimal("1000"), 6, BigDecimal.ROUND_HALF_UP);
            redisTemplate.opsForHash().increment(statsKey, "totalCost",
                    cost.multiply(new BigDecimal("1000000")).longValue());
            redisTemplate.opsForHash().increment(todayKey, "cost",
                    cost.multiply(new BigDecimal("1000000")).longValue());
        }

        // 更新模型最后调用时间
        LambdaUpdateWrapper<ModelConfig> updateWrapper = new LambdaUpdateWrapper<>();
        updateWrapper.eq(ModelConfig::getId, modelId)
                     .set(ModelConfig::getLastCallTime, LocalDateTime.now());
        modelConfigMapper.update(null, updateWrapper);

        log.debug("记录模型调用: modelId={}, inputTokens={}, outputTokens={}, responseTime={}ms, success={}",
                modelId, inputTokens, outputTokens, responseTimeMs, success);
    }

    /**
     * 记录模型失败
     */
    public void recordFailure(Long modelId) {
        ModelConfig model = modelConfigMapper.selectById(modelId);
        if (model != null) {
            model.setFailureCount(model.getFailureCount() == null ? 1 : model.getFailureCount() + 1);
            modelConfigMapper.updateById(model);
        }
    }

    /**
     * 重置失败计数
     */
    public void resetFailureCount(Long modelId) {
        LambdaUpdateWrapper<ModelConfig> wrapper = new LambdaUpdateWrapper<>();
        wrapper.eq(ModelConfig::getId, modelId)
               .set(ModelConfig::getFailureCount, 0);
        modelConfigMapper.update(null, wrapper);
    }

    /**
     * 获取每日调用趋势
     */
    private List<MonitorDashboardDTO.DailyCallTrend> getDailyCallTrends() {
        List<MonitorDashboardDTO.DailyCallTrend> trends = new ArrayList<>();
        LocalDate today = LocalDate.now();

        for (int i = 6; i >= 0; i--) {
            LocalDate date = today.minusDays(i);
            MonitorDashboardDTO.DailyCallTrend trend = new MonitorDashboardDTO.DailyCallTrend();
            trend.setDate(date.atStartOfDay());
            trend.setCallCount(0L);
            trend.setTotalCost(BigDecimal.ZERO);
            trend.setAvgResponseTime(0L);
            trends.add(trend);
        }

        return trends;
    }

    // ========== 私有方法 ==========

    private void clearDefaultModel(Long excludeId) {
        LambdaUpdateWrapper<ModelConfig> wrapper = new LambdaUpdateWrapper<>();
        wrapper.eq(ModelConfig::getIsDefault, 1)
               .ne(excludeId != null, ModelConfig::getId, excludeId)
               .set(ModelConfig::getIsDefault, 0);
        modelConfigMapper.update(null, wrapper);
        redisTemplate.delete(DEFAULT_MODEL_KEY);
    }

    private List<ModelUsageLog> queryUsageLogs(Long modelId, LocalDateTime startDate, LocalDateTime endDate) {
        LambdaQueryWrapper<ModelUsageLog> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(modelId != null, ModelUsageLog::getModelId, modelId);
        if (startDate != null) {
            wrapper.ge(ModelUsageLog::getCallDate, startDate);
        }
        if (endDate != null) {
            wrapper.le(ModelUsageLog::getCallDate, endDate);
        }
        return modelUsageLogMapper.selectList(wrapper);
    }

    private void aggregateStats(ModelStatsDTO stats, List<ModelUsageLog> logs) {
        long totalCalls = 0;
        long todayCalls = 0;
        long successCalls = 0;
        long failCalls = 0;
        long totalInputTokens = 0;
        long totalOutputTokens = 0;
        BigDecimal totalCost = BigDecimal.ZERO;
        LocalDate today = LocalDate.now();

        for (ModelUsageLog log : logs) {
            totalCalls += log.getCallCount() != null ? log.getCallCount() : 0;
            successCalls += log.getSuccessCount() != null ? log.getSuccessCount() : 0;
            failCalls += log.getFailureCount() != null ? log.getFailureCount() : 0;
            totalInputTokens += log.getInputTokens() != null ? log.getInputTokens() : 0;
            totalOutputTokens += log.getOutputTokens() != null ? log.getOutputTokens() : 0;
            if (log.getTotalCost() != null) {
                totalCost = totalCost.add(log.getTotalCost());
            }
            if (log.getCallDate() != null && log.getCallDate().toLocalDate().equals(today)) {
                todayCalls += log.getCallCount() != null ? log.getCallCount() : 0;
            }
        }

        stats.setTotalCallCount(totalCalls);
        stats.setTodayCallCount(todayCalls);
        stats.setSuccessCount(successCalls);
        stats.setFailureCount(failCalls);
        stats.setTotalInputTokens(totalInputTokens);
        stats.setTotalOutputTokens(totalOutputTokens);
        stats.setTotalTokens(totalInputTokens + totalOutputTokens);
        stats.setTotalCost(totalCost);
    }

    private Long getLongFromCache(Map<Object, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return null;
        if (value instanceof Long) return (Long) value;
        if (value instanceof Integer) return ((Integer) value).longValue();
        if (value instanceof String) {
            try {
                return Long.parseLong((String) value);
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }
}