package com.aidbid.gateway.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import lombok.Data;

@Data
@Configuration
@ConfigurationProperties(prefix = "jwt")
public class JwtProperties {
    
    private String secret = "ai-bid-system-secret-key-minimum-32-characters";
    private long expiration = 7200000; // 2小时
    private long refreshExpiration = 604800000; // 7天
}