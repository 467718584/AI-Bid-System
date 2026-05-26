package com.aidbid.material.controller;

import com.aibid.common.core.Result;
import com.aibid.material.entity.BidMaterial;
import com.aibid.material.service.MaterialService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/material")
@RequiredArgsConstructor
public class MaterialController {

    private final MaterialService materialService;

    @GetMapping("/{id}")
    public Result<BidMaterial> getById(@PathVariable Long id) {
        return Result.ok(materialService.getById(id));
    }

    @GetMapping("/list")
    public Result<List<BidMaterial>> list() {
        return Result.ok(materialService.list());
    }

    @GetMapping("/list/project/{projectId}")
    public Result<List<BidMaterial>> listByProjectId(@PathVariable Long projectId) {
        return Result.ok(materialService.listByProjectId(projectId));
    }

    @PostMapping
    public Result<Void> save(@RequestBody BidMaterial material) {
        materialService.save(material);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody BidMaterial material) {
        materialService.update(material);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        materialService.delete(id);
        return Result.ok();
    }
}
