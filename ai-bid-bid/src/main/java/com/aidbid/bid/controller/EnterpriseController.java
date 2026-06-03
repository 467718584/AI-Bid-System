package com.aidbid.bid.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.*;

@RestController
@RequestMapping("/enterprise")
public class EnterpriseController {

    private final Map<String, Object> enterpriseInfo = new HashMap<>();
    private final List<Map<String, Object>> qualifications = new ArrayList<>();
    private final List<Map<String, Object>> experiences = new ArrayList<>();
    private final Map<String, Object> financialData = new HashMap<>();
    
    {
        enterpriseInfo.put("name", "示例科技有限公司");
        enterpriseInfo.put("creditCode", "91110000000000000X");
        enterpriseInfo.put("address", "北京市朝阳区科技园区");
        enterpriseInfo.put("contactPerson", "张三");
        enterpriseInfo.put("contactPhone", "010-12345678");
        enterpriseInfo.put("registeredCapital", 50000000);
        enterpriseInfo.put("成立时间", "2010-01-01");
    }

    @GetMapping("/info")
    public Map<String, Object> info() {
        return Map.of("code", 200, "data", enterpriseInfo);
    }

    @PutMapping("/info")
    public Map<String, Object> updateInfo(@RequestBody Map<String, Object> data) {
        enterpriseInfo.putAll(data);
        return Map.of("code", 200, "data", enterpriseInfo);
    }

    @GetMapping("/qualifications")
    public Map<String, Object> qualifications(@RequestParam Map<String, String> params) {
        return Map.of("code", 200, "data", qualifications, "total", qualifications.size());
    }

    @PostMapping("/qualifications")
    public Map<String, Object> uploadQualification(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "type", required = false) String type) {
        Map<String, Object> qual = new HashMap<>();
        qual.put("id", System.currentTimeMillis());
        qual.put("name", file.getOriginalFilename());
        qual.put("type", type != null ? type : "other");
        qual.put("size", file.getSize());
        qual.put("uploadTime", new Date().toString());
        qualifications.add(qual);
        return Map.of("code", 200, "data", qual);
    }

    @DeleteMapping("/qualifications/{id:[0-9]+}")
    public Map<String, Object> deleteQualification(@PathVariable("id") Long id) {
        qualifications.removeIf(q -> ((Number) q.get("id")).longValue() == id);
        return Map.of("code", 200, "message", "deleted");
    }

    @GetMapping("/qualification-types")
    public Map<String, Object> qualificationTypes() {
        return Map.of("code", 200, "data", List.of(
            Map.of("type", "iso", "name", "ISO认证"),
            Map.of("type", "certificate", "name", "资质证书"),
            Map.of("type", "patent", "name", "专利"),
            Map.of("type", "other", "name", "其他")
        ));
    }

    @GetMapping("/experiences")
    public Map<String, Object> experiences(@RequestParam Map<String, String> params) {
        return Map.of("code", 200, "data", experiences, "total", experiences.size());
    }

    @PostMapping("/experiences")
    public Map<String, Object> addExperience(@RequestBody Map<String, Object> data) {
        data.put("id", System.currentTimeMillis());
        experiences.add(data);
        return Map.of("code", 200, "data", data);
    }

    @PutMapping("/experiences/{id:[0-9]+}")
    public Map<String, Object> updateExperience(@PathVariable("id") Long id, @RequestBody Map<String, Object> data) {
        for (int i = 0; i < experiences.size(); i++) {
            if (((Number) experiences.get(i).get("id")).longValue() == id) {
                data.put("id", id);
                experiences.set(i, data);
                return Map.of("code", 200, "data", data);
            }
        }
        return Map.of("code", 404, "message", "Experience not found");
    }

    @DeleteMapping("/experiences/{id:[0-9]+}")
    public Map<String, Object> deleteExperience(@PathVariable("id") Long id) {
        experiences.removeIf(e -> ((Number) e.get("id")).longValue() == id);
        return Map.of("code", 200, "message", "deleted");
    }

    @GetMapping("/financial")
    public Map<String, Object> financial() {
        return Map.of("code", 200, "data", financialData.isEmpty() ? Map.of(
            "year", 2024,
            "revenue", 100000000,
            "profit", 10000000,
            "assets", 50000000
        ) : financialData);
    }

    @PutMapping("/financial")
    public Map<String, Object> updateFinancial(@RequestBody Map<String, Object> data) {
        financialData.putAll(data);
        return Map.of("code", 200, "data", financialData);
    }

    @GetMapping("/completeness")
    public Map<String, Object> completeness() {
        int total = 5;
        int completed = enterpriseInfo.isEmpty() ? 0 : 3;
        return Map.of("code", 200, "data", Map.of(
            "total", total,
            "completed", completed,
            "percentage", (completed * 100) / total
        ));
    }

    @GetMapping("/suggestions")
    public Map<String, Object> suggestions() {
        return Map.of("code", 200, "data", List.of(
            "请完善企业资质证书",
            "请添加近期项目业绩",
            "请更新财务数据"
        ));
    }
}
