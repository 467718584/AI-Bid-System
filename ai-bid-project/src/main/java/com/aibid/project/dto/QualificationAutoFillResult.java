package com.aibid.project.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 资信标自动填充结果DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class QualificationAutoFillResult {

    /** 企业信息 */
    private EnterpriseInfoDTO enterpriseInfo;

    /** 资质列表 */
    private QualificationListDTO qualifications;

    /** 业绩案例列表 */
    private ExperienceListDTO experiences;

    /** 财务数据 */
    private FinancialDataDTO financialData;

    /** 填充状态 */
    private FillStatusDTO fillStatus;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class EnterpriseInfoDTO {
        private Long enterpriseId;
        private String name;
        private String unifiedCreditCode;
        private String type;
        private String legalPerson;
        private String contactPhone;
        private String address;
        private Integer qualificationCount;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QualificationListDTO {
        private Integer total;
        private Integer active;
        private Integer expired;
        private Integer soonExpiring;
        private Integer nearExpirationCount;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ExperienceListDTO {
        private Integer total;
        private Integer totalBidAmount;
        private Integer largeProjects;
        private Integer mediumProjects;
        private Integer recentProjects;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FinancialDataDTO {
        private Integer latestYear;
        private BigDecimal totalAssets;
        private BigDecimal netAssets;
        private BigDecimal mainBusinessIncome;
        private BigDecimal netProfit;
        private BigDecimal roe;
        private BigDecimal assetLiabilityRatio;
        private String auditOpinion;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FillStatusDTO {
        /** 已填充模块 */
        private Integer filledModules;
        /** 总模块数 */
        private Integer totalModules;
        /** 缺失模块 */
        private java.util.List<String> missingModules;
    }
}