package com.aidbid.material.controller;

import com.aibid.common.core.Result;
import com.aidbid.material.entity.ProjectCase;
import com.aidbid.material.service.ProjectCaseService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/enterprise/project-case")
@RequiredArgsConstructor
public class ProjectCaseController {

    private final ProjectCaseService projectCaseService;

    @GetMapping("/{id}")
    public Result<ProjectCase> getById(@PathVariable Long id) {
        return Result.ok(projectCaseService.getById(id));
    }

    @GetMapping("/list/enterprise/{enterpriseId}")
    public Result<List<ProjectCase>> listByEnterprise(@PathVariable Long enterpriseId) {
        return Result.ok(projectCaseService.listByEnterpriseId(enterpriseId));
    }

    @GetMapping("/list/industry/{industry}")
    public Result<List<ProjectCase>> listByIndustry(@PathVariable String industry) {
        return Result.ok(projectCaseService.listByIndustry(industry));
    }

    @GetMapping("/list/featured")
    public Result<List<ProjectCase>> listFeatured() {
        return Result.ok(projectCaseService.listFeatured());
    }

    @PostMapping
    public Result<Void> save(@RequestBody ProjectCase projectCase) {
        projectCaseService.save(projectCase);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody ProjectCase projectCase) {
        projectCaseService.update(projectCase);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        projectCaseService.delete(id);
        return Result.ok();
    }
}