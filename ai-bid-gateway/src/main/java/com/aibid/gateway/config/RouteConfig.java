package com.aibid.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * AI服务路由配置
 */
@Configuration
public class RouteConfig {

    private final ModelRoutingFilter modelRoutingFilter;

    public RouteConfig(ModelRoutingFilter modelRoutingFilter) {
        this.modelRoutingFilter = modelRoutingFilter;
    }

    @Bean
    public RouteLocator aiRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
                // AI服务路由
                .route("ai-bid-ai", r -> r
                        .path("/api/ai/**")
                        .filters(f -> f
                                .filter(modelRoutingFilter)
                                .stripPrefix(1)
                        )
                        .uri("lb://ai-bid-ai")
                )
                // 知识库服务路由
                .route("ai-bid-knowledge", r -> r
                        .path("/api/knowledge/**")
                        .filters(f -> f
                                .stripPrefix(1)
                        )
                        .uri("lb://ai-bid-knowledge")
                )
                .build();
    }
}