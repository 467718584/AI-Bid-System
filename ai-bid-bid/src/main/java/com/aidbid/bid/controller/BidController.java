package com.aidbid.bid.controller;

import com.aidbid.bid.entity.BidProject;
import com.aidbid.bid.service.BidProjectService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletResponse;
import org.apache.poi.xwpf.usermodel.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;

@RestController
@RequestMapping("/bid")
public class BidController {

    @Autowired
    private BidProjectService bidProjectService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @GetMapping("/list")
    public Map<String, Object> list(@RequestParam Map<String, String> params) {
        try {
            List<BidProject> projects = bidProjectService.list();
            List<Map<String, Object>> result = new ArrayList<>();
            for (BidProject p : projects) {
                result.add(convertToMap(p));
            }
            return Map.of(
                "code", 200,
                "message", "success",
                "data", Map.of(
                    "list", result,
                    "total", result.size(),
                    "page", 1,
                    "pageSize", 100
                )
            );
        } catch (Exception e) {
            return Map.of("code", 500, "message", "查询失败: " + e.getMessage());
        }
    }

    @GetMapping("/{id:[0-9]+}")
    public Map<String, Object> getById(@PathVariable("id") Long id) {
        try {
            BidProject project = bidProjectService.getById(id);
            if (project == null) {
                return Map.of("code", 404, "message", "Bid not found");
            }
            return Map.of("code", 200, "data", convertToMap(project));
        } catch (Exception e) {
            return Map.of("code", 500, "message", "查询失败: " + e.getMessage());
        }
    }

    @PostMapping
    public Map<String, Object> create(@RequestBody Map<String, Object> data) {
        try {
            BidProject project = new BidProject();
            project.setName((String) data.get("title"));
            project.setDescription((String) data.get("description"));
            project.setType((String) data.get("projectType"));
            
            // 处理大纲和内容
            if (data.get("outline") != null) {
                project.setOutline(objectMapper.writeValueAsString(data.get("outline")));
            }
            if (data.get("content") != null) {
                project.setContent((String) data.get("content"));
            }
            
            BidProject created = bidProjectService.create(project);
            return Map.of(
                "code", 200,
                "message", "success",
                "data", convertToMap(created)
            );
        } catch (JsonProcessingException e) {
            return Map.of("code", 500, "message", "创建失败: " + e.getMessage());
        }
    }

    @PutMapping("/{id:[0-9]+}")
    public Map<String, Object> update(@PathVariable("id") Long id, @RequestBody Map<String, Object> data) {
        try {
            BidProject existing = bidProjectService.getById(id);
            if (existing == null) {
                return Map.of("code", 404, "message", "Bid not found");
            }
            
            if (data.get("title") != null) {
                existing.setName((String) data.get("title"));
            }
            if (data.get("description") != null) {
                existing.setDescription((String) data.get("description"));
            }
            if (data.get("projectType") != null) {
                existing.setType((String) data.get("projectType"));
            }
            if (data.get("outline") != null) {
                existing.setOutline(objectMapper.writeValueAsString(data.get("outline")));
            }
            if (data.get("content") != null) {
                existing.setContent((String) data.get("content"));
            }
            if (data.get("status") != null) {
                existing.setStatus((String) data.get("status"));
            }
            
            BidProject updated = bidProjectService.update(id, existing);
            return Map.of("code", 200, "data", convertToMap(updated));
        } catch (JsonProcessingException e) {
            return Map.of("code", 500, "message", "更新失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id:[0-9]+}")
    public Map<String, Object> delete(@PathVariable("id") Long id) {
        boolean success = bidProjectService.delete(id);
        return Map.of("code", success ? 200 : 404, "message", success ? "deleted" : "Bid not found");
    }

    @PostMapping("/{id:[0-9]+}/submit")
    public Map<String, Object> submit(@PathVariable("id") Long id) {
        try {
            BidProject existing = bidProjectService.getById(id);
            if (existing == null) {
                return Map.of("code", 404, "message", "Bid not found");
            }
            existing.setStatus("SUBMITTED");
            BidProject updated = bidProjectService.update(id, existing);
            return Map.of("code", 200, "data", convertToMap(updated));
        } catch (Exception e) {
            return Map.of("code", 500, "message", "提交失败: " + e.getMessage());
        }
    }

    @GetMapping("/{id:[0-9]+}/export")
    public void export(@PathVariable("id") Long id, @RequestParam(defaultValue = "docx") String format, HttpServletResponse response) {
        try {
            BidProject project = bidProjectService.getById(id);
            if (project == null) {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                return;
            }

            if ("docx".equals(format)) {
                String title = project.getName() != null ? project.getName() : "标书导出";
                String content = project.getContent() != null ? project.getContent() : "";
                
                List<Map<String, Object>> outline = new ArrayList<>();
                if (project.getOutline() != null) {
                    try {
                        outline = objectMapper.readValue(project.getOutline(), new TypeReference<List<Map<String, Object>>>() {});
                    } catch (Exception e) {
                        outline = new ArrayList<>();
                    }
                }

                XWPFDocument doc = new XWPFDocument();

                // 标题
                XWPFParagraph titlePara = doc.createParagraph();
                titlePara.createRun().setText(title);
                titlePara.createRun().setFontSize(22);
                titlePara.createRun().setBold(true);
                titlePara.setAlignment(ParagraphAlignment.CENTER);

                // 目录
                if (!outline.isEmpty()) {
                    XWPFParagraph outlineTitle = doc.createParagraph();
                    outlineTitle.createRun().setText("目  录");
                    outlineTitle.createRun().setFontSize(16);
                    outlineTitle.createRun().setBold(true);
                    outlineTitle.setAlignment(ParagraphAlignment.CENTER);

                    renderOutline(doc, outline, 1);
                }

                // 正文内容
                if (content != null && !content.isEmpty()) {
                    XWPFParagraph contentTitle = doc.createParagraph();
                    contentTitle.createRun().setText("正  文");
                    contentTitle.createRun().setFontSize(16);
                    contentTitle.createRun().setBold(true);
                    contentTitle.setAlignment(ParagraphAlignment.CENTER);

                    String[] lines = content.split("\n");
                    for (String line : lines) {
                        XWPFParagraph para = doc.createParagraph();
                        if (line.startsWith("# ")) {
                            para.createRun().setText(line.substring(2));
                            para.createRun().setFontSize(16);
                            para.createRun().setBold(true);
                        } else if (line.startsWith("## ")) {
                            para.createRun().setText(line.substring(3));
                            para.createRun().setFontSize(14);
                            para.createRun().setBold(true);
                        } else if (line.startsWith("### ")) {
                            para.createRun().setText(line.substring(4));
                            para.createRun().setFontSize(12);
                            para.createRun().setBold(true);
                        } else if (!line.trim().isEmpty()) {
                            para.createRun().setText(line);
                            para.createRun().setFontSize(12);
                        }
                    }
                }

                String filename = title + ".docx";
                response.setContentType("application/vnd.openxmlformats-officedocument.wordprocessingml.document");
                response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + java.net.URLEncoder.encode(filename, StandardCharsets.UTF_8));
                doc.write(response.getOutputStream());
                doc.close();
            } else {
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            }
        } catch (IOException e) {
            throw new RuntimeException("Word export failed: " + e.getMessage(), e);
        }
    }

    private void renderOutline(XWPFDocument doc, List<Map<String, Object>> items, int level) {
        for (Map<String, Object> item : items) {
            String itemTitle = (String) item.get("title");
            if (itemTitle == null) continue;
            XWPFParagraph para = doc.createParagraph();
            String indent = "    ".repeat(Math.max(0, level - 1));
            para.createRun().setText(indent + itemTitle);
            para.createRun().setFontSize(level == 1 ? 14 : 12);
            para.createRun().setBold(level == 1);
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> children = (List<Map<String, Object>>) item.get("children");
            if (children != null && !children.isEmpty()) {
                renderOutline(doc, children, level + 1);
            }
        }
    }

    @GetMapping("/{id:[0-9]+}/versions")
    public Map<String, Object> versions(@PathVariable("id") Long id) {
        return Map.of("code", 200, "data", List.of());
    }

    @GetMapping("/{id:[0-9]+}/collaborators")
    public Map<String, Object> collaborators(@PathVariable("id") Long id) {
        return Map.of("code", 200, "data", List.of());
    }

    @GetMapping("/{id:[0-9]+}/activities")
    public Map<String, Object> activities(@PathVariable("id") Long id, @RequestParam Map<String, String> params) {
        return Map.of("code", 200, "data", List.of());
    }

    private Map<String, Object> convertToMap(BidProject p) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("id", String.valueOf(p.getId()));
        map.put("title", p.getName());
        map.put("name", p.getName());
        map.put("description", p.getDescription());
        map.put("projectType", p.getType());
        map.put("type", p.getType());
        map.put("status", p.getStatus() != null ? p.getStatus().toLowerCase() : "draft");
        map.put("content", p.getContent());
        map.put("outline", parseJson(p.getOutline()));
        map.put("createdAt", p.getCreateTime() != null ? p.getCreateTime().toString() : null);
        map.put("updatedAt", p.getUpdateTime() != null ? p.getUpdateTime().toString() : null);
        return map;
    }

    private Object parseJson(String json) {
        if (json == null || json.isEmpty()) return new ArrayList<>();
        try {
            return objectMapper.readValue(json, new TypeReference<Object>() {});
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }
}
