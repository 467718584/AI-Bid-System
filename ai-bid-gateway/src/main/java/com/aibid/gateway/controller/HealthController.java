package com.aibid.gateway.controller;

import com.aibid.common.core.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/")
public class HealthController {

    @GetMapping("/health")
    public Result<Map<String, Object>> health() {
        Map<String, Object> data = new HashMap<>();
        data.put("status", "UP");
        data.put("service", "ai-bid-gateway");
        data.put("timestamp", LocalDateTime.now());
        return Result.ok(data);
    }

    @GetMapping("/")
    public Result<Map<String, String>> index() {
        Map<String, String> data = new HashMap<>();
        data.put("name", "AI Bid System Gateway");
        data.put("version", "1.0.0");
        data.put("docs", "/swagger-ui.html");
        return Result.ok(data);
    }
}
