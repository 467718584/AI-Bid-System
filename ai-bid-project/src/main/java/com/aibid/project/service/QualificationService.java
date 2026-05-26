package com.aibid.project.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.project.dto.QualificationAutoFillResult;
import com.aibid.project.dto.QualificationMatchRequest;
import com.aibid.project.dto.QualificationMatchResult;
import com.aibid.project.entity.EnterpriseInfo;
import com.aibid.project.entity.FinancialData;
import com.aibid.project.entity.ProjectExperience;
import com.aibid.project.entity.Qualification;
import com.aibid.project.mapper.EnterpriseInfoMapper;
import com.aibid.project.mapper.FinancialDataMapper;
import com.aibid.project.mapper.ProjectExperienceMapper;
import com.aibid.project.mapper.QualificationMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 资质服务 - 资信标智能编制核心服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class QualificationService {

    private final QualificationMapper qualificationMapper;
    private final EnterpriseInfoMapper enterpriseInfoMapper;
    private final ProjectExperienceMapper projectExperienceMapper;
    private final FinancialDataMapper financialDataMapper;

    /** 资质过期预警阈值（天） */
    private static final int EXPIRATION_WARNING_DAYS = 30;
    /** 资质严重过期阈值（天） */
    private static final int CRITICAL_EXPIRATION_DAYS = 7;

    /**
     * 匹配招标文件要求的资质
     *
     * @param requirement 资质要求
     * @return 匹配结果
     */
    public QualificationMatchResult matchQualifications(QualificationMatchRequest requirement) {
        if (requirement == null || requirement.getRequirements() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING, "资质要求不能为空");
        }

        List<Qualification> allQualifications = qualificationMapper.selectList(
            new LambdaQueryWrapper<Qualification>()
                .eq(Qualification::getStatus, "ACTIVE")
                .or()
                .isNull(Qualification::getStatus)
        );

        List<QualificationMatchResult.MatchedQualification> matchedList = new ArrayList<>();
        List<QualificationMatchResult.UnmatchedRequirement> unmatchedList = new ArrayList<>();
        List<QualificationMatchResult.ExpirationWarning> warnings = new ArrayList<>();

        for (QualificationMatchRequest.QualificationRequirement req : requirement.getRequirements()) {
            List<Qualification> matched = findMatchingQualifications(allQualifications, req);

            if (!matched.isEmpty()) {
                for (Qualification q : matched) {
                    matchedList.add(toMatched(q));
                    addExpirationWarning(warnings, q);
                }
            } else {
                unmatchedList.add(new QualificationMatchResult.UnmatchedRequirement(
                    req.getType(), req.getLevel(),
                    "企业资质库中未找到匹配的" + req.getType() + " " + req.getLevel() + "资质"
                ));
            }
        }

        String status = unmatchedList.isEmpty() ? "FULL_MATCH"
            : matchedList.isEmpty() ? "NO_MATCH" : "PARTIAL_MATCH";

        return new QualificationMatchResult(status, matchedList, unmatchedList, warnings);
    }

    /**
     * 验证企业资质有效性
     *
     * @param enterpriseId 企业ID
     * @return 验证结果列表
     */
    public List<QualificationValidation> validateQualifications(Long enterpriseId) {
        List<Qualification> qualifications = qualificationMapper.selectList(
            new LambdaQueryWrapper<Qualification>()
                .eq(Qualification::getEnterpriseId, enterpriseId)
                .eq(Qualification::getDeleted, 0)
        );

        List<QualificationValidation> validations = new ArrayList<>();
        LocalDate today = LocalDate.now();

        for (Qualification q : qualifications) {
            QualificationValidation validation = new QualificationValidation();
            validation.setQualificationId(q.getId());
            validation.setName(q.getName());
            validation.setCertificateNo(q.getCertificateNo());
            validation.setValidUntil(q.getValidUntil());

            if (q.getValidUntil() == null) {
                validation.setValid(true);
                validation.setMessage("有效期未设置");
            } else if (q.getValidUntil().toLocalDate().isBefore(today)) {
                validation.setValid(false);
                validation.setMessage("资质已过期");
                validation.setExpired(true);
            } else {
                long daysLeft = ChronoUnit.DAYS.between(today, q.getValidUntil().toLocalDate());
                validation.setDaysUntilExpiration((int) daysLeft);
                if (daysLeft <= EXPIRATION_WARNING_DAYS) {
                    validation.setValid(true);
                    validation.setMessage("资质即将过期，剩余" + daysLeft + "天");
                    validation.setExpiringSoon(true);
                } else {
                    validation.setValid(true);
                    validation.setMessage("资质有效");
                }
            }
            validations.add(validation);
        }
        return validations;
    }

    /**
     * 自动填充资信标
     *
     * @param projectId 投标项目ID
     * @return 填充结果
     */
    public QualificationAutoFillResult autoFillQualifications(Long projectId) {
        QualificationAutoFillResult result = new QualificationAutoFillResult();

        // 1. 获取企业信息
        EnterpriseInfo enterprise = enterpriseInfoMapper.selectOne(
            new LambdaQueryWrapper<EnterpriseInfo>()
                .eq(EnterpriseInfo::getStatus, "ACTIVE")
                .last("LIMIT 1")
        );

        QualificationAutoFillResult.EnterpriseInfoDTO enterpriseInfoDTO = null;
        if (enterprise != null) {
            Integer qualCount = qualificationMapper.selectCount(
                new LambdaQueryWrapper<Qualification>()
                    .eq(Qualification::getEnterpriseId, enterprise.getId())
                    .eq(Qualification::getStatus, "ACTIVE")
            );
            enterpriseInfoDTO = new QualificationAutoFillResult.EnterpriseInfoDTO(
                enterprise.getId(),
                enterprise.getName(),
                enterprise.getUnifiedCreditCode(),
                enterprise.getType(),
                enterprise.getLegalPerson(),
                enterprise.getContactPhone(),
                enterprise.getAddress(),
                qualCount
            );
        }
        result.setEnterpriseInfo(enterpriseInfoDTO);

        // 2. 资质统计
        List<Qualification> allQualifications = qualificationMapper.selectList(
            new LambdaQueryWrapper<Qualification>()
                .eq(enterprise != null ? Qualification::getEnterpriseId : null, enterprise == null ? null : enterprise.getId())
                .or()
                .isNull(Qualification::getEnterpriseId)
        );
        QualificationAutoFillResult.QualificationListDTO qualDTO = buildQualificationStats(allQualifications);
        result.setQualifications(qualDTO);

        // 3. 业绩案例统计
        List<ProjectExperience> experiences = projectExperienceMapper.selectList(
            new LambdaQueryWrapper<ProjectExperience>()
                .eq(enterprise != null ? ProjectExperience::getEnterpriseId : null, enterprise == null ? null : enterprise.getId())
                .eq(ProjectExperience::getIsArchived, 1)
        );
        QualificationAutoFillResult.ExperienceListDTO expDTO = buildExperienceStats(experiences);
        result.setExperiences(expDTO);

        // 4. 财务数据
        FinancialData financial = null;
        if (enterprise != null) {
            financial = financialDataMapper.selectOne(
                new LambdaQueryWrapper<FinancialData>()
                    .eq(FinancialData::getEnterpriseId, enterprise.getId())
                    .orderByDesc(FinancialData::getYear)
                    .last("LIMIT 1")
            );
        }
        QualificationAutoFillResult.FinancialDataDTO finDTO = null;
        if (financial != null) {
            finDTO = new QualificationAutoFillResult.FinancialDataDTO(
                financial.getYear(),
                financial.getTotalAssets(),
                financial.getNetAssets(),
                financial.getMainBusinessIncome(),
                financial.getNetProfit(),
                financial.getRoe(),
                financial.getAssetLiabilityRatio(),
                financial.getAuditOpinion()
            );
        }
        result.setFinancialData(finDTO);

        // 5. 填充状态
        QualificationAutoFillResult.FillStatusDTO statusDTO = buildFillStatus(
            enterpriseInfoDTO, qualDTO, expDTO, finDTO
        );
        result.setFillStatus(statusDTO);

        return result;
    }

    /**
     * 获取企业资质列表
     */
    public List<Qualification> listByEnterprise(Long enterpriseId) {
        return qualificationMapper.selectList(
            new LambdaQueryWrapper<Qualification>()
                .eq(Qualification::getEnterpriseId, enterpriseId)
                .orderByDesc(Qualification::getValidUntil)
        );
    }

    /**
     * 获取企业信息
     */
    public EnterpriseInfo getEnterpriseInfo(Long enterpriseId) {
        EnterpriseInfo info = enterpriseInfoMapper.selectById(enterpriseId);
        if (info == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "企业信息不存在");
        }
        return info;
    }

    /**
     * 获取企业业绩列表
     */
    public List<ProjectExperience> listExperiences(Long enterpriseId) {
        return projectExperienceMapper.selectList(
            new LambdaQueryWrapper<ProjectExperience>()
                .eq(ProjectExperience::getEnterpriseId, enterpriseId)
                .eq(ProjectExperience::getIsArchived, 1)
                .orderByDesc(ProjectExperience::getBidDate)
        );
    }

    /**
     * 获取企业财务数据列表
     */
    public List<FinancialData> listFinancialData(Long enterpriseId) {
        return financialDataMapper.selectList(
            new LambdaQueryWrapper<FinancialData>()
                .eq(FinancialData::getEnterpriseId, enterpriseId)
                .orderByDesc(FinancialData::getYear)
        );
    }

    // ========== 私有辅助方法 ==========

    private List<Qualification> findMatchingQualifications(
        List<Qualification> all, QualificationMatchRequest.QualificationRequirement req
    ) {
        return all.stream()
            .filter(q -> {
                boolean typeMatch = req.getType() == null || req.getType().isEmpty()
                    || q.getName() != null && q.getName().contains(req.getType());
                boolean levelMatch = req.getLevel() == null || req.getLevel().isEmpty()
                    || req.getLevel().equals(q.getLevel());
                return typeMatch && levelMatch && isValidNow(q);
            })
            .collect(Collectors.toList());
    }

    private boolean isValidNow(Qualification q) {
        if (q.getValidUntil() == null) return true;
        return !q.getValidUntil().toLocalDate().isBefore(LocalDate.now());
    }

    private QualificationMatchResult.MatchedQualification toMatched(Qualification q) {
        return new QualificationMatchResult.MatchedQualification(
            q.getId(), q.getName(), q.getType(), q.getLevel(),
            q.getCertificateNo(), q.getValidUntil(), q.getStatus()
        );
    }

    private void addExpirationWarning(
        List<QualificationMatchResult.ExpirationWarning> warnings, Qualification q
    ) {
        if (q.getValidUntil() == null) return;
        long daysLeft = ChronoUnit.DAYS.between(LocalDate.now(), q.getValidUntil().toLocalDate());
        if (daysLeft <= EXPIRATION_WARNING_DAYS && daysLeft >= 0) {
            String level = daysLeft <= CRITICAL_EXPIRATION_DAYS ? "CRITICAL" : "WARNING";
            warnings.add(new QualificationMatchResult.ExpirationWarning(
                q.getId(), q.getName(), q.getValidUntil(), (int) daysLeft, level
            ));
        }
    }

    private QualificationAutoFillResult.QualificationListDTO buildQualificationStats(List<Qualification> list) {
        LocalDate today = LocalDate.now();
        int expired = 0, nearExp = 0, active = 0;
        for (Qualification q : list) {
            if (q.getValidUntil() == null) {
                active++;
            } else if (q.getValidUntil().toLocalDate().isBefore(today)) {
                expired++;
            } else {
                long daysLeft = ChronoUnit.DAYS.between(today, q.getValidUntil().toLocalDate());
                if (daysLeft <= EXPIRATION_WARNING_DAYS) nearExp++;
                active++;
            }
        }
        return new QualificationAutoFillResult.QualificationListDTO(
            list.size(), active, expired, nearExp, nearExp
        );
    }

    private QualificationAutoFillResult.ExperienceListDTO buildExperienceStats(List<ProjectExperience> list) {
        int large = 0, medium = 0, recent = 0;
        java.math.BigDecimal totalAmt = java.math.BigDecimal.ZERO;
        LocalDate oneYearAgo = LocalDate.now().minusYears(1);
        for (ProjectExperience e : list) {
            if (e.getBidAmount() != null) totalAmt = totalAmt.add(e.getBidAmount());
            if ("大型".equals(e.getScale())) large++;
            else if ("中型".equals(e.getScale())) medium++;
            if (e.getBidDate() != null && !e.getBidDate().toLocalDate().isBefore(oneYearAgo)) recent++;
        }
        return new QualificationAutoFillResult.ExperienceListDTO(
            list.size(), totalAmt.intValue(), large, medium, recent
        );
    }

    private QualificationAutoFillResult.FillStatusDTO buildFillStatus(
        QualificationAutoFillResult.EnterpriseInfoDTO ei,
        QualificationAutoFillResult.QualificationListDTO ql,
        QualificationAutoFillResult.ExperienceListDTO el,
        QualificationAutoFillResult.FinancialDataDTO fd
    ) {
        List<String> missing = new ArrayList<>();
        int filled = 0, total = 4;
        if (ei != null) { filled++; } else { missing.add("enterprise_info"); }
        if (ql != null && ql.getTotal() > 0) { filled++; } else { missing.add("qualifications"); }
        if (el != null && el.getTotal() > 0) { filled++; } else { missing.add("experiences"); }
        if (fd != null) { filled++; } else { missing.add("financial_data"); }
        return new QualificationAutoFillResult.FillStatusDTO(filled, total, missing);
    }

    // ========== 内部类 ==========

    @lombok.Data
    public static class QualificationValidation {
        private Long qualificationId;
        private String name;
        private String certificateNo;
        private LocalDateTime validUntil;
        private boolean valid;
        private boolean expired;
        private boolean expiringSoon;
        private Integer daysUntilExpiration;
        private String message;
    }
}