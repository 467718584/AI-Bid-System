package com.aidbid.project.controller;

import com.aibid.common.core.Result;
import com.aidbid.project.dto.QualificationAutoFillResult;
import com.aidbid.project.dto.QualificationMatchRequest;
import com.aidbid.project.dto.QualificationMatchResult;
import com.aidbid.project.entity.EnterpriseInfo;
import com.aidbid.project.entity.FinancialData;
import com.aidbid.project.entity.ProjectExperience;
import com.aidbid.project.entity.Qualification;
import com.aidbid.project.service.QualificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 资信标资质控制器
 */
@RestController
@RequestMapping("/project/{projectId}/qualification")
@RequiredArgsConstructor
public class QualificationController {

    private final QualificationService qualificationService;

    /**
     * 自动填充资信标资质信息
     * POST /api/project/{project_id}/qualification/auto-fill
     */
    @PostMapping("/auto-fill")
    public Result<QualificationAutoFillResult> autoFill(@PathVariable Long projectId) {
        return Result.ok(qualificationService.autoFillQualifications(projectId));
    }

    /**
     * 获取资质匹配状态
     * GET /api/project/{project_id}/qualification/status
     */
    @PostMapping("/match")
    public Result<QualificationMatchResult> match(
        @PathVariable Long projectId,
        @RequestBody QualificationMatchRequest request
    ) {
        return Result.ok(qualificationService.matchQualifications(request));
    }

    /**
     * 验证企业资质有效性
     * POST /api/project/{project_id}/qualification/validate
     */
    @PostMapping("/validate")
    public Result<List<QualificationService.QualificationValidation>> validate(
        @PathVariable Long projectId,
        @RequestParam Long enterpriseId
    ) {
        return Result.ok(qualificationService.validateQualifications(enterpriseId));
    }

    /**
     * 获取企业资质列表
     * GET /api/project/{project_id}/qualification/list
     */
    @GetMapping("/list")
    public Result<List<Qualification>> list(
        @PathVariable Long projectId,
        @RequestParam Long enterpriseId
    ) {
        return Result.ok(qualificationService.listByEnterprise(enterpriseId));
    }

    /**
     * 获取企业信息
     * GET /api/project/{project_id}/qualification/enterprise
     */
    @GetMapping("/enterprise")
    public Result<EnterpriseInfo> getEnterprise(
        @PathVariable Long projectId,
        @RequestParam Long enterpriseId
    ) {
        return Result.ok(qualificationService.getEnterpriseInfo(enterpriseId));
    }

    /**
     * 获取企业业绩列表
     * GET /api/project/{project_id}/qualification/experiences
     */
    @GetMapping("/experiences")
    public Result<List<ProjectExperience>> listExperiences(
        @PathVariable Long projectId,
        @RequestParam Long enterpriseId
    ) {
        return Result.ok(qualificationService.listExperiences(enterpriseId));
    }

    /**
     * 获取企业财务数据列表
     * GET /api/project/{project_id}/qualification/financial
     */
    @GetMapping("/financial")
    public Result<List<FinancialData>> listFinancial(
        @PathVariable Long projectId,
        @RequestParam Long enterpriseId
    ) {
        return Result.ok(qualificationService.listFinancialData(enterpriseId));
    }
}