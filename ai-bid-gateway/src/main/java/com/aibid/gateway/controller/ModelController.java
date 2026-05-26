package com.aibid.gateway.controller;

import com.aibid.common.core.Result;
import com.aibid.gateway.dto.ModelConfigDTO;
import com.aibid.gateway.dto.ModelStatsDTO;
import com.aibid.gateway.dto.ModelSwitchDTO;
import com.aibid.gateway.dto.MonitorDashboardDTO;
import com.aibid.gateway.entity.ModelConfig;
import com.aibid.gateway.service.ModelRegistryService;
import com.aibid.gateway.service.RateLimiterService;
import com.aibid.gateway.service.SmartRouterService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 模型管理控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/gateway/models")
@RequiredArgsConstructor
public class ModelController {

    private final ModelRegistryService modelRegistryService;
    private final SmartRouterService smartRouterService;
    private final RateLimiterService rateLimiterService;

    /**
     * 获取模型列表
     */
    @GetMapping
    public Result<List<ModelConfig>> listModels() {
        List<ModelConfig> models = modelRegistryService.listModels();
        return Result.ok(models);
    }

    /**
     * 获取启用的模型列表
     */
    @GetMapping("/enabled")
    public Result<List<ModelConfig>> listEnabledModels() {
        List<ModelConfig> models = modelRegistryService.listEnabledModels();
        return Result.ok(models);
    }

    /**
     * 获取模型详情
     */
    @GetMapping("/{id}")
    public Result<ModelConfig> getModel(@PathVariable Long id) {
        ModelConfig model = modelRegistryService.listModels().stream()
                .filter(m -> m.getId().equals(id))
                .findFirst()
                .orElse(null);
        if (model == null) {
            return Result.fail(404, "模型不存在");
        }
        return Result.ok(model);
    }

    /**
     * 注册新模型
     */
    @PostMapping
    public Result<ModelConfig> registerModel(@RequestBody ModelConfigDTO dto) {
        if (dto.getName() == null || dto.getName().isEmpty()) {
            return Result.fail("模型名称不能为空");
        }
        if (dto.getModelKey() == null || dto.getModelKey().isEmpty()) {
            return Result.fail("模型标识不能为空");
        }
        if (dto.getProvider() == null || dto.getProvider().isEmpty()) {
            return Result.fail("提供商不能为空");
        }

        ModelConfig model = modelRegistryService.registerModel(dto);
        return Result.ok(model);
    }

    /**
     * 更新模型配置
     */
    @PutMapping("/{id}")
    public Result<ModelConfig> updateModel(@PathVariable Long id, @RequestBody ModelConfigDTO dto) {
        ModelConfig model = modelRegistryService.updateModel(id, dto);
        return Result.ok(model);
    }

    /**
     * 删除模型
     */
    @DeleteMapping("/{id}")
    public Result<Void> deleteModel(@PathVariable Long id) {
        modelRegistryService.deleteModel(id);
        return Result.ok();
    }

    /**
     * 切换默认模型
     */
    @PostMapping("/switch")
    public Result<ModelConfig> switchModel(@RequestBody ModelSwitchDTO dto) {
        if (dto.getModelId() == null) {
            return Result.fail("目标模型ID不能为空");
        }
        String reason = dto.getReason() != null ? dto.getReason() : "手动切换";
        ModelConfig model = modelRegistryService.switchModel(dto.getModelId(), reason);
        return Result.ok(model);
    }

    /**
     * 获取模型使用统计
     */
    @GetMapping("/{id}/stats")
    public Result<ModelStatsDTO> getModelStats(@PathVariable Long id) {
        ModelStatsDTO stats = modelRegistryService.getModelStats(id);
        return Result.ok(stats);
    }

    /**
     * 获取监控面板数据
     */
    @GetMapping("/dashboard")
    public Result<MonitorDashboardDTO> getDashboard() {
        MonitorDashboardDTO dashboard = modelRegistryService.getDashboardData();
        return Result.ok(dashboard);
    }

    /**
     * 获取模型状态 (熔断器状态)
     */
    @GetMapping("/{id}/status")
    public Result<Map<String, Object>> getModelStatus(@PathVariable Long id) {
        Map<String, Object> status = smartRouterService.getModelStatus(id);
        return Result.ok(status);
    }

    /**
     * 获取限流状态
     */
    @GetMapping("/{id}/rate-limit")
    public Result<RateLimiterService.RateLimitStatus> getRateLimitStatus(
            @PathVariable Long id,
            @RequestParam(required = false) Long userId,
            @RequestParam(required = false, defaultValue = "chat") String requestType) {
        RateLimiterService.RateLimitStatus status = rateLimiterService.getRateLimitStatus(id, userId, requestType);
        return Result.ok(status);
    }

    /**
     * 重置限流计数
     */
    @PostMapping("/{id}/rate-limit/reset")
    public Result<Void> resetRateLimit(@PathVariable Long id) {
        rateLimiterService.resetRateLimit(id);
        return Result.ok();
    }

    /**
     * 获取默认模型
     */
    @GetMapping("/default")
    public Result<ModelConfig> getDefaultModel() {
        ModelConfig model = modelRegistryService.getDefaultModel();
        if (model == null) {
            return Result.fail(404, "没有默认模型");
        }
        return Result.ok(model);
    }

    /**
     * 测试模型连接
     */
    @PostMapping("/{id}/test")
    public Result<Map<String, Object>> testModel(@PathVariable Long id) {
        Map<String, Object> result = smartRouterService.getModelStatus(id);
        result.put("testPassed", (boolean) result.get("available"));
        result.put("modelId", id);
        return Result.ok(result);
    }
}