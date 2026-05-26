package com.aidbid.material.controller;

import com.aibid.common.core.Result;
import com.aibid.material.entity.Certificate;
import com.aibid.material.service.CertificateService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/enterprise/certificate")
@RequiredArgsConstructor
public class CertificateController {

    private final CertificateService certificateService;

    @GetMapping("/{id}")
    public Result<Certificate> getById(@PathVariable Long id) {
        return Result.ok(certificateService.getById(id));
    }

    @GetMapping("/list/enterprise/{enterpriseId}")
    public Result<List<Certificate>> listByEnterprise(@PathVariable Long enterpriseId) {
        return Result.ok(certificateService.listByEnterpriseId(enterpriseId));
    }

    @GetMapping("/list/type/{type}")
    public Result<List<Certificate>> listByType(@PathVariable String type) {
        return Result.ok(certificateService.listByType(type));
    }

    @GetMapping("/list/expiring")
    public Result<List<Certificate>> listExpiring(int days) {
        return Result.ok(certificateService.listExpiring(days));
    }

    @PostMapping
    public Result<Void> save(@RequestBody Certificate certificate) {
        certificateService.save(certificate);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody Certificate certificate) {
        certificateService.update(certificate);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        certificateService.delete(id);
        return Result.ok();
    }
}