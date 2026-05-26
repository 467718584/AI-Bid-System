package com.aibid.gateway.config;

import com.aibid.gateway.dto.RouteContext;
import com.aibid.gateway.service.ModelRegistryService;
import com.aibid.gateway.service.RateLimiterService;
import com.aibid.gateway.service.SmartRouterService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.UUID;

/**
 * 模型路由过滤器 - 全局过滤器,负责智能路由和限流
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ModelRoutingFilter implements GlobalFilter, Ordered {

    private final SmartRouterService smartRouterService;
    private final RateLimiterService rateLimiterService;
    private final ModelRegistryService modelRegistryService;

    private static final int ORDER = -100;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        ServerHttpResponse response = exchange.getResponse();

        String path = request.getURI().getPath();

        // 只处理AI相关请求
        if (!path.startsWith("/ai/")) {
            return chain.filter(exchange);
        }

        // 生成请求ID
        String requestId = UUID.randomUUID().toString();
        request = request.mutate()
                .header("X-Request-Id", requestId)
                .build();

        // 构建路由上下文
        RouteContext context = buildRouteContext(request);
        exchange.getAttributes().put("routeContext", context);

        // 1. 检查限流
        if (!checkRateLimit(exchange, context)) {
            log.warn("请求被限流: path={}, requestId={}", path, requestId);
            response.setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
            response.getHeaders().add("X-Rate-Limit-Exceeded", "true");
            return response.setComplete();
        }

        // 2. 智能路由选择模型
        var model = smartRouterService.selectModel(context);
        if (model == null) {
            log.error("没有可用模型: path={}, requestId={}", path, requestId);
            response.setStatusCode(HttpStatus.SERVICE_UNAVAILABLE);
            return response.setComplete();
        }

        // 将选中的模型信息传递给下游服务
        request = request.mutate()
                .header("X-Model-Id", String.valueOf(model.getId()))
                .header("X-Model-Name", model.getName())
                .header("X-Model-Key", model.getModelKey())
                .header("X-Request-Type", context.getRequestType())
                .build();

        // 记录请求
        rateLimiterService.recordRequest(model.getId(), getUserId(request), context.getRequestType());

        final ServerHttpRequest finalRequest = request;
        long startTime = System.currentTimeMillis();

        return chain.filter(exchange.mutate().request(finalRequest).build())
                .then(Mono.fromRunnable(() -> {
                    // 记录调用结果
                    long duration = System.currentTimeMillis() - startTime;
                    boolean success = response.getStatusCode() == HttpStatus.OK;
                    smartRouterService.recordRouting(model.getId(), success, duration);
                    modelRegistryService.recordCall(
                            model.getId(),
                            model.getName(),
                            context.getRequestType(),
                            0, // 实际应从响应中获取
                            0,
                            duration,
                            success
                    );
                }));
    }

    @Override
    public int getOrder() {
        return ORDER;
    }

    // ========== 私有方法 ==========

    /**
     * 构建路由上下文
     */
    private RouteContext buildRouteContext(ServerHttpRequest request) {
        RouteContext context = new RouteContext();
        context.setRequestId(request.getHeaders().getFirst("X-Request-Id"));

        String path = request.getURI().getPath();
        String method = request.getMethod().name();

        // 根据路径判断请求类型
        if (path.contains("/analyze")) {
            context.setRequestType("analyze");
        } else if (path.contains("/embedding")) {
            context.setRequestType("embedding");
        } else if (path.contains("/summary")) {
            context.setRequestType("summary");
        } else if (path.contains("/chat")) {
            context.setRequestType("chat");
        } else {
            context.setRequestType("chat");
        }

        // 从请求头获取偏好设置
        String requireHighAccuracy = request.getHeaders().getFirst("X-Require-High-Accuracy");
        context.setRequireHighAccuracy("true".equalsIgnoreCase(requireHighAccuracy));

        String costSensitive = request.getHeaders().getFirst("X-Cost-Sensitive");
        context.setCostSensitive("true".equalsIgnoreCase(costSensitive));

        String preferredModelId = request.getHeaders().getFirst("X-Preferred-Model");
        if (preferredModelId != null && !preferredModelId.isEmpty()) {
            try {
                context.setPreferredModelId(Long.parseLong(preferredModelId));
            } catch (NumberFormatException ignored) {
            }
        }

        // 设置输入长度
        String contentLength = request.getHeaders().getFirst("Content-Length");
        if (contentLength != null) {
            try {
                context.setInputLength(Integer.parseInt(contentLength));
            } catch (NumberFormatException ignored) {
            }
        }

        return context;
    }

    /**
     * 检查限流
     */
    private boolean checkRateLimit(ServerWebExchange exchange, RouteContext context) {
        // 如果选择了模型,检查模型限流
        Long modelId = context.getSelectedModelId();
        if (modelId != null) {
            boolean allowed = rateLimiterService.allowRequest(modelId, null);
            if (!allowed) {
                exchange.getResponse().getHeaders().add("X-Rate-Limit-Type", "model");
                return false;
            }
        }

        // 检查用户限流
        Long userId = getUserId(exchange.getRequest());
        if (userId != null) {
            boolean allowed = rateLimiterService.allowUserRequest(userId, context.getRequestType());
            if (!allowed) {
                exchange.getResponse().getHeaders().add("X-Rate-Limit-Type", "user");
                return false;
            }
        }

        return true;
    }

    /**
     * 获取用户ID
     */
    private Long getUserId(ServerHttpRequest request) {
        String userId = request.getHeaders().getFirst("X-User-Id");
        if (userId != null && !userId.isEmpty()) {
            try {
                return Long.parseLong(userId);
            } catch (NumberFormatException ignored) {
            }
        }
        return null;
    }
}