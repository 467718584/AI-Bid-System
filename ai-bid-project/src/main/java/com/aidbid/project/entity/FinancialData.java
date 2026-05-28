package com.aidbid.project.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 财务数据实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_financial_data")
public class FinancialData extends BaseEntity {

    /** 报表年份 */
    private Integer year;

    /** 报表类型: 年报/季报/中期 */
    private String reportType;

    /** 总资产(万元) */
    private BigDecimal totalAssets;

    /** 净资产(万元) */
    private BigDecimal netAssets;

    /** 固定资产(万元) */
    private BigDecimal fixedAssets;

    /** 流动资产(万元) */
    private BigDecimal currentAssets;

    /** 总负债(万元) */
    private BigDecimal totalLiabilities;

    /** 流动负债(万元) */
    private BigDecimal currentLiabilities;

    /** 主营业务收入(万元) */
    private BigDecimal mainBusinessIncome;

    /** 净利润(万元) */
    private BigDecimal netProfit;

    /** 净资产收益率(%) */
    private BigDecimal roe;

    /** 资产负债率(%) */
    private BigDecimal assetLiabilityRatio;

    /** 流动比率 */
    private BigDecimal currentRatio;

    /** 速动比率 */
    private BigDecimal quickRatio;

    /** 营业额(万元) */
    private BigDecimal turnover;

    /** 审计机构 */
    private String auditor;

    /** 审计意见: 无保留/保留/否定 */
    private String auditOpinion;

    /** 财务报表图片路径(JSON数组) */
    private String financialStatements;

    /** 关联企业ID */
    private Long enterpriseId;

    /** 备注 */
    private String remark;
}