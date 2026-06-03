package com.aidbid.bid.controller;

import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/workflow")
public class WorkflowController {

    private final List<Map<String, Object>> workflows = new ArrayList<>();
    private final List<Map<String, Object>> instances = new ArrayList<>();
    
    {
        Map<String, Object> wf = new HashMap<>();
        wf.put("id", 1L);
        wf.put("name", "投标文件编制流程");
        wf.put("status", "active");
        wf.put("nodes", List.of(
            Map.of("id", 1, "name", "创建标书", "type", "start"),
            Map.of("id", 2, "name", "技术标编制", "type", "task"),
            Map.of("id", 3, "name", "商务标编制", "type", "task"),
            Map.of("id", 4, "name", "审核", "type", "review"),
            Map.of("id", 5, "name", "提交", "type", "end")
        ));
        workflows.add(wf);
    }

    @GetMapping("/list")
    public Map<String, Object> list(@RequestParam Map<String, String> params) {
        return Map.of(
            "code", 200,
            "message", "success",
            "data", Map.of(
                "list", new ArrayList<>(workflows),
                "total", workflows.size(),
                "page", 1,
                "pageSize", 100
            )
        );
    }

    @GetMapping("/{id:[0-9]+}")
    public Map<String, Object> getById(@PathVariable("id") Long id) {
        for (Map<String, Object> wf : workflows) {
            Long wfId = ((Number) wf.get("id")).longValue();
            if (wfId.equals(id)) {
                return Map.of("code", 200, "data", wf);
            }
        }
        return Map.of("code", 404, "message", "Workflow not found");
    }

    @PostMapping
    public Map<String, Object> create(@RequestBody Map<String, Object> data) {
        data.put("id", System.currentTimeMillis());
        data.put("status", "active");
        data.put("nodes", new ArrayList<>());
        workflows.add(data);
        return Map.of(
            "code", 200,
            "message", "success",
            "data", Map.of(
                "list", new ArrayList<>(workflows),
                "total", workflows.size(),
                "page", 1,
                "pageSize", 100
            )
        );
    }

    @PutMapping("/{id:[0-9]+}")
    public Map<String, Object> update(@PathVariable("id") Long id, @RequestBody Map<String, Object> data) {
        for (int i = 0; i < workflows.size(); i++) {
            Long wfId = ((Number) workflows.get(i).get("id")).longValue();
            if (wfId.equals(id)) {
                data.put("id", id);
                workflows.set(i, data);
                return Map.of("code", 200, "data", data);
            }
        }
        return Map.of("code", 404, "message", "Workflow not found");
    }

    @DeleteMapping("/{id:[0-9]+}")
    public Map<String, Object> delete(@PathVariable("id") Long id) {
        workflows.removeIf(wf -> ((Number) wf.get("id")).longValue() == id);
        return Map.of("code", 200, "message", "deleted");
    }

    @PostMapping("/{id:[0-9]+}/duplicate")
    public Map<String, Object> duplicate(@PathVariable("id") Long id) {
        for (Map<String, Object> wf : workflows) {
            if (((Number) wf.get("id")).longValue() == id) {
                Map<String, Object> newWf = new HashMap<>(wf);
                newWf.put("id", System.currentTimeMillis());
                newWf.put("name", wf.get("name") + " (副本)");
                workflows.add(newWf);
                return Map.of("code", 200, "data", newWf);
            }
        }
        return Map.of("code", 404, "message", "Workflow not found");
    }

    @PostMapping("/{id:[0-9]+}/toggle")
    public Map<String, Object> toggle(@PathVariable("id") Long id, @RequestBody Map<String, Object> data) {
        for (Map<String, Object> wf : workflows) {
            if (((Number) wf.get("id")).longValue() == id) {
                boolean enabled = Boolean.TRUE.equals(data.get("enabled"));
                wf.put("status", enabled ? "active" : "inactive");
                return Map.of("code", 200, "data", wf);
            }
        }
        return Map.of("code", 404, "message", "Workflow not found");
    }

    @GetMapping("/{workflowId:[0-9]+}/nodes")
    public Map<String, Object> getNodes(@PathVariable("workflowId") Long workflowId) {
        for (Map<String, Object> wf : workflows) {
            if (((Number) wf.get("id")).longValue() == workflowId) {
                Object nodes = wf.getOrDefault("nodes", List.of());
                return Map.of("code", 200, "data", nodes);
            }
        }
        return Map.of("code", 200, "data", List.of());
    }

    @PostMapping("/{workflowId:[0-9]+}/nodes")
    public Map<String, Object> createNode(@PathVariable("workflowId") Long workflowId, @RequestBody Map<String, Object> data) {
        // 找到工作流并添加节点
        for (Map<String, Object> wf : workflows) {
            if (((Number) wf.get("id")).longValue() == workflowId) {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> nodes = (List<Map<String, Object>>) wf.computeIfAbsent("nodes", k -> new ArrayList<>());
                data.put("id", System.currentTimeMillis());
                nodes.add(data);
                return Map.of("code", 200, "data", data);
            }
        }
        return Map.of("code", 404, "message", "Workflow not found");
    }

    @GetMapping("/instances")
    public Map<String, Object> getInstances(@RequestParam Map<String, String> params) {
        return Map.of(
            "code", 200,
            "message", "success",
            "data", Map.of(
                "list", new ArrayList<>(instances),
                "total", instances.size(),
                "page", 1,
                "pageSize", 100
            )
        );
    }

    @PostMapping("/{workflowId:[0-9]+}/instances")
    public Map<String, Object> startInstance(@PathVariable("workflowId") Long workflowId, @RequestBody Map<String, Object> data) {
        Map<String, Object> instance = new HashMap<>();
        instance.put("id", System.currentTimeMillis());
        instance.put("workflowId", workflowId);
        instance.put("status", "running");
        instance.put("startTime", new Date().toString());
        instances.add(instance);
        return Map.of("code", 200, "data", instance);
    }

    @GetMapping("/instances/{instanceId:[0-9]+}")
    public Map<String, Object> getInstance(@PathVariable("instanceId") Long instanceId) {
        for (Map<String, Object> inst : instances) {
            if (((Number) inst.get("id")).longValue() == instanceId) {
                return Map.of("code", 200, "data", inst);
            }
        }
        return Map.of("code", 404, "message", "Instance not found");
    }

    @GetMapping("/instances/{instanceId:[0-9]+}/status")
    public Map<String, Object> getInstanceStatus(@PathVariable("instanceId") Long instanceId) {
        for (Map<String, Object> inst : instances) {
            if (((Number) inst.get("id")).longValue() == instanceId) {
                return Map.of("code", 200, "data", Map.of("status", inst.get("status")));
            }
        }
        return Map.of("code", 404, "message", "Instance not found");
    }

    @PostMapping("/instances/{instanceId:[0-9]+}/cancel")
    public Map<String, Object> cancelInstance(@PathVariable("instanceId") Long instanceId) {
        for (Map<String, Object> inst : instances) {
            if (((Number) inst.get("id")).longValue() == instanceId) {
                inst.put("status", "cancelled");
                return Map.of("code", 200, "data", inst);
            }
        }
        return Map.of("code", 404, "message", "Instance not found");
    }

    @GetMapping("/stats")
    public Map<String, Object> stats() {
        long activeCount = workflows.stream()
            .filter(w -> "active".equals(w.get("status")))
            .count();
        return Map.of("code", 200, "data", Map.of(
            "total", workflows.size(),
            "active", activeCount,
            "instances", instances.size()
        ));
    }

    @GetMapping("/templates")
    public Map<String, Object> templates() {
        return Map.of("code", 200, "data", List.of(
            Map.of("id", 1, "name", "标准投标流程"),
            Map.of("id", 2, "name", "紧急投标流程")
        ));
    }

    @GetMapping("/node-types")
    public Map<String, Object> nodeTypes() {
        return Map.of("code", 200, "data", List.of(
            Map.of("type", "start", "name", "开始"),
            Map.of("type", "task", "name", "任务"),
            Map.of("type", "review", "name", "审核"),
            Map.of("type", "end", "name", "结束")
        ));
    }
}
