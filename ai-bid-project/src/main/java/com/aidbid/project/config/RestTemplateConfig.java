package com.aidbid.project.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

/**
 * RestTemplate配置
 */
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate() {
        var factory = new SimpleClientHttpRequestFactory();
        // 连接超时30秒，读取超时60秒
        factory.setConnectTimeout(30_000);
        factory.setReadTimeout(60_000);
        return new RestTemplate(factory);
    }
}