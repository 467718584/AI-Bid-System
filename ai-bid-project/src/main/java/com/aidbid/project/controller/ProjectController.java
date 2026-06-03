package com.aidbid.project.controller;

import com.aidbid.common.core.Result;
import com.aidbid.project.entity.BidProject;
import com.aidbid.project.service.ProjectService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/project")
@RequiredArgsConstructor
public class ProjectController {

    private final ProjectService projectService;

    @GetMapping("/{id}")
    public Result<BidProject> getById(@PathVariable Long id) {
        return Result.ok(projectService.getById(id));
    }

    @GetMapping("/list")
    public Result<List<BidProject>> list() {
        return Result.ok(projectService.list());
    }

    @GetMapping("/list/status/{status}")
    public Result<List<BidProject>> listByStatus(@PathVariable String status) {
        return Result.ok(projectService.listByStatus(status));
    }

    @PostMapping
    public Result<BidProject> save(@RequestBody BidProject project) {
        BidProject saved = projectService.save(project);
        return Result.ok(saved);
    }

    @PutMapping
    public Result<Void> update(@RequestBody BidProject project) {
        projectService.update(project);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        projectService.delete(id);
        return Result.ok();
    }

    @GetMapping("/count")
    public Result<Long> count() {
        return Result.ok(projectService.count());
    }
}
