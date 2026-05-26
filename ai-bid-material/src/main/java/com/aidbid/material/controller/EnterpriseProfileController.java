package com.aidbid.material.controller;

import com.aibid.common.core.Result;
import com.aibid.material.entity.EnterpriseProfile;
import com.aibid.material.service.EnterpriseProfileService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/enterprise/profile")
@RequiredArgsConstructor
public class EnterpriseProfileController {

    private final EnterpriseProfileService enterpriseProfileService;

    @GetMapping("/{id}")
    public Result<EnterpriseProfile> getById(@PathVariable Long id) {
        return Result.ok(enterpriseProfileService.getById(id));
    }

    @GetMapping("/list")
    public Result<List<EnterpriseProfile>> list() {
        return Result.ok(enterpriseProfileService.listActive());
    }

    @PostMapping
    public Result<Void> save(@RequestBody EnterpriseProfile profile) {
        enterpriseProfileService.save(profile);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody EnterpriseProfile profile) {
        enterpriseProfileService.update(profile);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        enterpriseProfileService.delete(id);
        return Result.ok();
    }

    @GetMapping("/count")
    public Result<Long> count() {
        return Result.ok(enterpriseProfileService.count());
    }
}