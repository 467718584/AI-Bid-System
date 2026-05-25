package com.aibid.project.controller;

import com.aibid.common.core.Result;
import com.aibid.project.entity.BidProject;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/project")
@RequiredArgsConstructor
public class ProjectController {

    @GetMapping("/{id}")
    public Result<BidProject> getById(@PathVariable Long id) {
        BidProject project = new BidProject();
        project.setId(id);
        project.setName("测试项目");
        project.setCode("BID-2024-001");
        return Result.ok(project);
    }

    @GetMapping("/list")
    public Result<?> list() {
        return Result.ok();
    }
}
