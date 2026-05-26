package com.aibid.gateway.config;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Configuration;

/**
 * MyBatis Plus配置
 */
@Configuration
@MapperScan("com.aibid.gateway.mapper")
public class MybatisPlusConfig {
}